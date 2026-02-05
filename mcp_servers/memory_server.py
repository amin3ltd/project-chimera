from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from mcp.server import FastMCP


@dataclass
class MemoryItem:
    memory_id: str
    agent_id: str
    memory_type: str
    content: str
    created_at: str
    importance_score: float = 0.5


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _tokenize(text: str) -> set[str]:
    return {t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t}


def _score(query: str, content: str) -> float:
    q = _tokenize(query)
    if not q:
        return 0.0
    c = _tokenize(content)
    return len(q & c) / max(1, len(q))


def _db_path() -> Path:
    # Persist to a file so the server is stateful across calls.
    p = os.environ.get("CHIMERA_MEMORY_DB", "/tmp/chimera_memory.json")
    return Path(p)


def _load() -> list[MemoryItem]:
    path = _db_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8") or "{}")
    items = data.get("items", [])
    return [MemoryItem(**i) for i in items]


def _save(items: list[MemoryItem]) -> None:
    path = _db_path()
    path.write_text(json.dumps({"items": [i.__dict__ for i in items]}, indent=2), encoding="utf-8")


mcp = FastMCP("chimera-memory")


@mcp.tool(
    name="store_memory",
    title="Store memory",
    description="Persist a memory item for an agent.",
)
def store_memory(
    agent_id: str,
    content: str,
    memory_type: str = "episodic",
    importance_score: float = 0.5,
) -> dict[str, Any]:
    items = _load()
    mid = f"mem_{uuid.uuid4().hex[:10]}"
    item = MemoryItem(
        memory_id=mid,
        agent_id=agent_id,
        memory_type=memory_type,
        content=content,
        created_at=_now_iso(),
        importance_score=float(importance_score),
    )
    items.append(item)
    _save(items)
    return {"status": "success", "memory_id": mid}


@mcp.tool(
    name="search_memory",
    title="Search memory",
    description="Search memories for an agent by query string.",
)
def search_memory(agent_id: str, query: str, limit: int = 5) -> dict[str, Any]:
    items = [i for i in _load() if i.agent_id == agent_id]

    class SearchResult(TypedDict):
        memory_id: str
        memory_type: str
        content: str
        created_at: str
        score: float

    scored: list[SearchResult] = [
        {
            "memory_id": i.memory_id,
            "memory_type": i.memory_type,
            "content": i.content,
            "created_at": i.created_at,
            "score": float(_score(query, i.content) * (0.7 + 0.3 * i.importance_score)),
        }
        for i in items
    ]
    scored.sort(key=lambda d: d["score"], reverse=True)
    return {"status": "success", "results": scored[: max(1, int(limit))]}


@mcp.resource(
    "memory://recent",
    title="Recent memories",
    description="Returns the most recent stored memories (for demos).",
    mime_type="application/json",
)
def recent() -> str:
    items = _load()
    last = items[-10:]
    return json.dumps({"items": [i.__dict__ for i in last]}, indent=2)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

