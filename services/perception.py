"""
Perception System (SRS FR 2.0 / FR 2.1)

Implements:
- Active resource monitoring (polling MCP Resources)
- Semantic filtering & relevance scoring
- Task emission to the Planner (or any task sink)

This module is designed to work without external credentials by default by
connecting to the in-repo MCP news server (`mcp_servers.news_server`) via stdio.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Callable, Iterable

from services.mcp_client import MCPClient, create_news_mcp_client
from services.planner import GlobalState, Planner, Task


def _tokenize(text: str) -> set[str]:
    return {
        t
        for t in re.sub(r"[^a-zA-Z0-9]+", " ", text.lower()).split()
        if t and len(t) > 2
    }


@dataclass
class SemanticFilter:
    """
    Lightweight semantic filter.

    The SRS suggests a small/cheap model. In this repository we implement a
    deterministic relevance score (token overlap) to keep the system runnable
    offline while still enforcing a threshold gate.
    """

    relevance_threshold: float = 0.75

    def score(self, content: str, goal: str) -> float:
        goal_toks = _tokenize(goal)
        if not goal_toks:
            return 0.0
        content_toks = _tokenize(content)
        if not content_toks:
            return 0.0
        overlap = len(goal_toks & content_toks)
        return overlap / max(1, len(goal_toks))

    def is_relevant(self, content: str, goals: Iterable[str]) -> tuple[bool, float, str | None]:
        best_score = 0.0
        best_goal: str | None = None
        for g in goals:
            s = self.score(content, g)
            if s > best_score:
                best_score = s
                best_goal = g
        return best_score >= self.relevance_threshold, best_score, best_goal


TaskSink = Callable[[Task], None]


class PerceptionPoller:
    """
    Polls MCP resources for updates and emits tasks when relevant.
    """

    def __init__(
        self,
        *,
        mcp_client: MCPClient | None = None,
        resource_uri: str = "news://latest",
        semantic_filter: SemanticFilter | None = None,
        task_sink: TaskSink | None = None,
        campaign_id: str = "default",
    ):
        self.mcp = mcp_client or create_news_mcp_client()
        self.resource_uri = resource_uri
        self.filter = semantic_filter or SemanticFilter()
        self.task_sink = task_sink or (lambda _task: None)
        self.campaign_id = campaign_id

        self._last_fingerprint: str | None = None

    async def start(self) -> None:
        await self.mcp.connect()

    async def stop(self) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        try:
            await self.mcp.aclose()
        except Exception:
            # Backwards-compat with local-registry mode.
            try:
                self.mcp.disconnect()
            except Exception:
                pass

    async def poll_once(self, goals: list[str]) -> list[Task]:
        """
        Poll one resource read and return emitted tasks.
        """
        raw = await self.mcp.read_resource(self.resource_uri)
        fingerprint = str(hash(raw))
        if self._last_fingerprint == fingerprint:
            return []
        self._last_fingerprint = fingerprint

        # Extract candidate lines/headlines
        lines = [ln.strip(" -\t") for ln in raw.splitlines() if ln.strip()]
        emitted: list[Task] = []

        for ln in lines:
            relevant, score, best_goal = self.filter.is_relevant(ln, goals)
            if not relevant:
                continue

            t = Task(
                task_type="analyze_trends",
                priority="high" if score >= 0.9 else "medium",
                goal_description=f"Trend alert ({score:.2f}) from {self.resource_uri}: {ln}",
                persona_constraints=["professional", "engaging"],
                required_resources=[self.resource_uri],
                campaign_id=self.campaign_id,
            )
            emitted.append(t)
            self.task_sink(t)

        return emitted

    async def run(self, goals: list[str], poll_interval_s: float = 5.0) -> None:
        """
        Continuous polling loop (service mode).
        """
        await self.start()
        try:
            while True:
                await self.poll_once(goals)
                await asyncio.sleep(poll_interval_s)
        finally:
            await self.aclose()


class RedisTaskQueueSink:
    """
    Task sink that enqueues tasks into the Planner Redis priority queue.

    This makes the Perception system a runnable subsystem that feeds the swarm.
    """

    def __init__(self, *, redis_url: str | None = None):
        self.planner = Planner(redis_url=redis_url) if redis_url else Planner()

    def is_connected(self) -> bool:
        return self.planner.is_connected()

    def __call__(self, task: Task) -> None:
        # Best-effort enqueue; do not crash the perception loop.
        try:
            self.planner.push_task(task)
        except Exception as e:
            print(f"Perception sink enqueue error: {e}")


class GlobalStateGoals:
    """
    Goal source that reads the campaign GlobalState from Redis.
    """

    def __init__(self, campaign_id: str, *, redis_url: str | None = None):
        self.campaign_id = campaign_id
        self.planner = Planner(redis_url=redis_url) if redis_url else Planner()

    def get(self) -> list[str]:
        state: GlobalState | None = self.planner.read_global_state(self.campaign_id)
        if not state:
            return []
        if state.status != "active":
            return []
        return list(state.goals)


class PerceptionSubsystem:
    """
    Continuous resource monitoring + semantic filtering (SRS FR 2.0 / FR 2.1).

    - Polls one or more MCP resources on an interval
    - Applies semantic filtering against current campaign goals
    - Emits tasks into Redis via the Planner task queue (optional)
    """

    def __init__(
        self,
        *,
        campaign_id: str,
        resource_uris: list[str] | None = None,
        poll_interval_s: float = 10.0,
        relevance_threshold: float = 0.75,
        redis_url: str | None = None,
        goals: list[str] | None = None,
        use_global_state: bool = True,
        task_sink: TaskSink | None = None,
    ):
        self.campaign_id = campaign_id
        self.resource_uris = resource_uris or ["news://latest"]
        self.poll_interval_s = poll_interval_s

        self.filter = SemanticFilter(relevance_threshold=relevance_threshold)

        self._explicit_goals = goals or []
        self._goal_source = GlobalStateGoals(campaign_id, redis_url=redis_url) if use_global_state else None

        self.sink = task_sink or (RedisTaskQueueSink(redis_url=redis_url) if redis_url or use_global_state else (lambda _t: None))

        # One poller per resource. For now, default to the in-repo news client.
        self.pollers: list[PerceptionPoller] = [
            PerceptionPoller(
                mcp_client=create_news_mcp_client(),
                resource_uri=uri,
                semantic_filter=self.filter,
                task_sink=self.sink,
                campaign_id=campaign_id,
            )
            for uri in self.resource_uris
        ]

    def _current_goals(self) -> list[str]:
        if self._goal_source is not None:
            goals = self._goal_source.get()
            if goals:
                return goals
        return self._explicit_goals

    async def start(self) -> None:
        # Connect all MCP clients.
        for p in self.pollers:
            await p.start()

    async def aclose(self) -> None:
        for p in self.pollers:
            await p.aclose()

    async def run(self) -> None:
        await self.start()
        try:
            while True:
                goals = self._current_goals()
                if not goals:
                    # No goals available; avoid spamming tasks.
                    await asyncio.sleep(self.poll_interval_s)
                    continue

                for p in self.pollers:
                    await p.poll_once(goals)

                await asyncio.sleep(self.poll_interval_s)
        finally:
            await self.aclose()


if __name__ == "__main__":
    # Demo: print emitted tasks (no Redis required)
    async def _demo() -> None:
        tasks: list[Task] = []

        def sink(t: Task) -> None:
            tasks.append(t)
            print("EMIT:", t.goal_description)

        poller = PerceptionPoller(
            campaign_id="demo",
            semantic_filter=SemanticFilter(relevance_threshold=0.3),
            task_sink=sink,
        )
        await poller.start()
        await poller.poll_once(goals=["AI agents", "Ethiopia tech", "AI disclosure"])
        await poller.aclose()

    asyncio.run(_demo())

