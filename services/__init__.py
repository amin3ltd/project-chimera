"""
Services for Project Chimera

FastRender Swarm Services: Planner, Worker, Judge
MCP Client for external integrations
"""

from .planner import Planner, Task, GlobalState
from .worker import Worker, TaskResult
from .judge import Judge, JudgeDecision, CommitResult
from .mcp_client import (
    MCPClient,
    MCPServerManager,
    MCPTool,
    MCPResource,
    create_twitter_mcp_client,
    create_news_mcp_client,
    create_coinbase_mcp_client,
)

__all__ = [
    # Planner
    "Planner",
    "Task",
    "GlobalState",
    # Worker
    "Worker",
    "TaskResult",
    # Judge
    "Judge",
    "JudgeDecision",
    "CommitResult",
    # MCP
    "MCPClient",
    "MCPServerManager",
    "MCPTool",
    "MCPResource",
    "create_twitter_mcp_client",
    "create_news_mcp_client",
    "create_coinbase_mcp_client",
]
