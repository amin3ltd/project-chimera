from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from mcp.server import FastMCP


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str | None = None
    source: str | None = None
    published_at: str | None = None


def _load_items() -> list[NewsItem]:
    """
    Load items from a JSON fixture if provided.

    Env:
      - CHIMERA_NEWS_FIXTURE: path to a JSON file with {"items":[{title,url,source,published_at},...]}
    """
    fixture = os.environ.get("CHIMERA_NEWS_FIXTURE")
    if fixture:
        data = json.loads(Path(fixture).read_text(encoding="utf-8"))
        items = data.get("items", [])
        return [NewsItem(**i) for i in items]

    # Default seed items (deterministic, offline-friendly)
    return [
        NewsItem(
            title="AI agents accelerate product teams with safer automation patterns",
            url="https://example.com/ai-agents-automation",
            source="demo-wire",
            published_at="2026-02-05T08:00:00Z",
        ),
        NewsItem(
            title="Ethiopia tech ecosystem: startups adopt LLM copilots for customer support",
            url="https://example.com/ethiopia-llm-copilots",
            source="demo-wire",
            published_at="2026-02-05T07:30:00Z",
        ),
        NewsItem(
            title="Creator economy tools add platform-native AI disclosure controls",
            url="https://example.com/ai-disclosure-controls",
            source="demo-wire",
            published_at="2026-02-05T06:45:00Z",
        ),
    ]


def _tokenize(text: str) -> set[str]:
    return {t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if t}


def _score_topic(item: NewsItem, topic: str) -> float:
    topic_tokens = _tokenize(topic)
    if not topic_tokens:
        return 0.0
    item_tokens = _tokenize(item.title)
    overlap = len(topic_tokens & item_tokens)
    return overlap / max(1, len(topic_tokens))


class TrendItem(TypedDict):
    topic: str
    score: float
    source: str | None
    url: str | None


mcp = FastMCP("chimera-news")

_ITEMS: list[NewsItem] = _load_items()


@mcp.resource(
    "news://latest",
    title="Latest news headlines",
    description="Offline-friendly latest headlines used for perception polling.",
    mime_type="text/plain",
)
def latest() -> str:
    # Add a tiny amount of variation so polling can observe change if desired.
    epoch_bucket = int(time.time()) // 60
    items = _ITEMS[:] if epoch_bucket % 2 == 0 else list(reversed(_ITEMS))
    lines: list[str] = []
    for it in items:
        meta = " | ".join([p for p in [it.source, it.published_at, it.url] if p])
        lines.append(f"- {it.title}" + (f" ({meta})" if meta else ""))
    return "\n".join(lines).strip() + "\n"


@mcp.tool(
    name="fetch_trends",
    title="Fetch trending topics",
    description="Derive simple 'trend' topics from headlines for a given topic query.",
)
def fetch_trends(topic: str = "technology", limit: int = 10, country: str = "US") -> dict[str, Any]:
    # This tool is intentionally simple but real: it derives scored trends from headlines.
    scored: list[TrendItem] = [
        {
            "topic": it.title,
            "score": float(_score_topic(it, topic)),
            "source": it.source,
            "url": it.url,
        }
        for it in _ITEMS
    ]
    scored.sort(key=lambda d: d["score"], reverse=True)
    # Return only items with some overlap, but always provide something for demo
    filtered = [s for s in scored if s["score"] > 0] or scored
    return {"topic": topic, "country": country, "trends": filtered[: max(1, int(limit))]}


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

