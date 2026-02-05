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
from typing import Callable, Iterable, Optional

from services.mcp_client import MCPClient, create_news_mcp_client
from services.planner import Task


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

