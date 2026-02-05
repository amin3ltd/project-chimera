"""
MCP Client - Model Context Protocol Integration.

This module provides a small wrapper around the official `mcp` Python SDK
so the repository can actually connect to MCP servers (via stdio) and execute
tools/read resources end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPError(Exception):
    """MCP-related error."""
    pass


@dataclass
class MCPTool:
    """MCP Tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResource:
    """MCP Resource definition."""
    uri: str
    description: str
    mime_type: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "uri": self.uri,
            "description": self.description,
            "mimeType": self.mime_type
        }


class MCPClient:
    """
    Model Context Protocol Client.
    
    Connects to MCP servers and provides unified access to:
    - Tools: Executable functions
    - Resources: Data sources
    - Prompts: Reusable templates
    """
    
    def __init__(
        self,
        server_name: str = "default",
        *,
        stdio_command: str | None = None,
        stdio_args: list[str] | None = None,
        stdio_env: dict[str, str] | None = None,
        cwd: str | None = None,
    ):
        """Initialize MCP client.

        If `stdio_command` is provided, `connect()` will spawn that MCP server
        and connect via stdio.
        """
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}  # optional local registry (for tests)
        self.resources: Dict[str, MCPResource] = {}  # optional local registry (for tests)
        self.prompts: Dict[str, str] = {}  # optional local registry (for tests)

        self._connected = False
        self._session: ClientSession | None = None
        self._stdio_ctx = None
        self._read_stream = None
        self._write_stream = None

        self._stdio_command = stdio_command
        self._stdio_args = stdio_args or []
        self._stdio_env = stdio_env
        self._cwd = cwd
        
    async def connect(self, transport: str = "stdio", **kwargs) -> bool:
        """
        Connect to MCP server.
        
        Args:
            transport: Transport type (stdio, sse, websocket)
            **kwargs: Transport-specific options
            
        Returns:
            True if connection successful
        """
        if transport != "stdio":
            raise MCPError("Only stdio transport is implemented in this repository.")

        # Back-compat: if no stdio server is configured, behave like a "local registry" client.
        if not self._stdio_command:
            self._connected = True
            return True

        try:
            params = StdioServerParameters(
                command=self._stdio_command,
                args=self._stdio_args,
                env=self._stdio_env,
                cwd=self._cwd,
            )
            # stdio_client is an async context manager that yields (read_stream, write_stream)
            self._stdio_ctx = stdio_client(params)
            self._read_stream, self._write_stream = await self._stdio_ctx.__aenter__()

            self._session = ClientSession(self._read_stream, self._write_stream)
            # Enter session context so the internal receiver loop is running.
            await self._session.__aenter__()
            await self._session.initialize()
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise MCPError(f"MCP connection failed: {e}") from e
    
    def disconnect(self):
        """Disconnect from MCP server."""
        # Prefer `await aclose()` for stdio-backed sessions. This sync method is
        # retained for backwards compatibility in places that never spawn a server.
        try:
            import asyncio

            asyncio.get_running_loop()
            # We're inside an event loop; cannot synchronously close safely.
            self._connected = False
            self.tools.clear()
            self.resources.clear()
            return
        except RuntimeError:
            # No running loop: safe to run an async close.
            anyio.run(self.aclose)

    async def aclose(self) -> None:
        """Async close (recommended)."""
        self._connected = False
        self.tools.clear()
        self.resources.clear()

        if self._session is not None:
            try:
                await self._session.__aexit__(None, None, None)
            except Exception:
                pass

        if self._stdio_ctx is not None:
            try:
                await self._stdio_ctx.__aexit__(None, None, None)
            except Exception:
                pass

        self._session = None
        self._stdio_ctx = None
        self._read_stream = None
        self._write_stream = None
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self._connected
    
    async def list_tools(self) -> List[MCPTool]:
        """List available tools from server."""
        if not self._connected:
            raise MCPError("Not connected to server")
        if self._session is None:
            return list(self.tools.values())

        resp = await self._session.list_tools()
        tools: list[MCPTool] = []
        for t in resp.tools:
            tools.append(
                MCPTool(
                    name=t.name,
                    description=t.description or "",
                    input_schema=t.inputSchema or {"type": "object"},
                )
            )
        return tools
    
    async def list_resources(self) -> List[MCPResource]:
        """List available resources from server."""
        if not self._connected:
            raise MCPError("Not connected to server")
        if self._session is None:
            return list(self.resources.values())

        resp = await self._session.list_resources()
        resources: list[MCPResource] = []
        for r in resp.resources:
            resources.append(
                MCPResource(
                    uri=r.uri,
                    description=r.description or "",
                    mime_type=r.mimeType,
                )
            )
        return resources
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool-specific arguments
            
        Returns:
            Tool result
        """
        if not self._connected:
            raise MCPError("Not connected to server")

        if self._session is None:
            # Local registry mode (legacy/demo)
            if tool_name not in self.tools:
                raise MCPError(f"Unknown tool: {tool_name}")
            return {"status": "success", "tool": tool_name, "result": "local-registry"}

        result = await self._session.call_tool(tool_name, arguments)
        # Most servers return JSON-serializable dicts. MCP SDK wraps content; keep it simple here.
        # If server returns structured output, it will be in `result.content`.
        if hasattr(result, "content"):
            # content is a list of content blocks; for our local servers we return JSON text blocks
            # or structured output. Prefer structured output if present.
            try:
                # If it's a single JSON text block, parse it.
                if len(result.content) == 1 and getattr(result.content[0], "type", "") == "text":
                    import json as _json

                    return _json.loads(result.content[0].text)
            except Exception:
                pass
        # Fallback: return the raw object as dict-like
        return getattr(result, "model_dump", lambda: result)()
    
    async def read_resource(self, uri: str) -> str:
        """
        Read a resource from the MCP server.
        
        Args:
            uri: Resource URI (e.g., news://latest)
            
        Returns:
            Resource content
        """
        if not self._connected:
            raise MCPError("Not connected to server")
        if self._session is None:
            if uri not in self.resources:
                raise MCPError(f"Unknown resource: {uri}")
            return f"Resource content for: {uri}"

        resp = await self._session.read_resource(uri)
        # read_resource returns content blocks; prefer text.
        if resp.contents:
            first = resp.contents[0]
            if hasattr(first, "text"):
                return first.text
            if hasattr(first, "blob"):
                return str(first.blob)
            return str(first)
        return ""
    
    def add_tool(self, tool: MCPTool):
        """Manually add a tool (for testing)."""
        self.tools[tool.name] = tool
    
    def add_resource(self, resource: MCPResource):
        """Manually add a resource (for testing)."""
        self.resources[resource.uri] = resource
    
    def add_prompt(self, name: str, template: str):
        """Add a prompt template."""
        self.prompts[name] = template
    
    async def get_prompt(self, name: str, variables: Dict[str, str] | None = None) -> str:
        """Get a rendered prompt template."""
        if name not in self.prompts:
            raise MCPError(f"Unknown prompt: {name}")
        
        template = self.prompts[name]
        
        if variables:
            for key, value in variables.items():
                template = template.replace(f"{{{key}}}", value)
        
        return template


class MCPServerManager:
    """
    Manager for multiple MCP server connections.
    
    Handles discovery, load balancing, and failover.
    """
    
    def __init__(self):
        """Initialize server manager."""
        self.servers: Dict[str, MCPClient] = {}
        
    def register_server(self, name: str, client: MCPClient):
        """Register an MCP server."""
        self.servers[name] = client
        
    def get_server(self, name: str) -> Optional[MCPClient]:
        """Get a registered server."""
        return self.servers.get(name)
    
    async def connect_all(self) -> int:
        """Connect to all registered servers."""
        connected = 0
        for name, client in self.servers.items():
            if await client.connect():
                connected += 1
        return connected
    
    def disconnect_all(self):
        """Disconnect from all servers."""
        for client in self.servers.values():
            client.disconnect()
    
    async def call_tool(self, server_name: str, tool_name: str,
                       arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific server."""
        client = self.get_server(server_name)
        if not client:
            raise MCPError(f"Unknown server: {server_name}")
        return await client.call_tool(tool_name, arguments)
    
    async def read_resource(self, server_name: str, uri: str) -> str:
        """Read a resource from a specific server."""
        client = self.get_server(server_name)
        if not client:
            raise MCPError(f"Unknown server: {server_name}")
        return await client.read_resource(uri)


# Factory functions for common MCP servers
def create_twitter_mcp_client() -> MCPClient:
    """Create Twitter MCP client."""
    client = MCPClient(server_name="twitter")
    
    # Add Twitter tools
    client.add_tool(MCPTool(
        name="post_tweet",
        description="Post a tweet to Twitter",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Tweet content"},
                "media_ids": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["text"]
        }
    ))
    
    client.add_tool(MCPTool(
        name="get_mentions",
        description="Get recent mentions of the agent",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20}
            }
        }
    ))
    
    # Add Twitter resources
    client.add_resource(MCPResource(
        uri="twitter://mentions/recent",
        description="Recent mentions of the agent"
    ))
    
    return client


def create_news_mcp_client() -> MCPClient:
    """Create News MCP client."""
    # Default to the in-repo news server so the integration is runnable.
    import sys

    client = MCPClient(
        server_name="news",
        stdio_command=sys.executable,
        stdio_args=["-m", "mcp_servers.news_server"],
    )
    
    # Add News tools
    client.add_tool(MCPTool(
        name="fetch_trends",
        description="Fetch trending topics",
        input_schema={
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "country": {"type": "string", "default": "US"},
                "limit": {"type": "integer", "default": 10}
            }
        }
    ))
    
    # Add News resources
    client.add_resource(MCPResource(
        uri="news://trending",
        description="Current trending topics"
    ))
    
    return client


def create_coinbase_mcp_client() -> MCPClient:
    """Create Coinbase MCP client."""
    client = MCPClient(server_name="coinbase")
    
    # Add Commerce tools
    client.add_tool(MCPTool(
        name="get_balance",
        description="Get wallet balance",
        input_schema={
            "type": "object",
            "properties": {
                "asset": {"type": "string", "default": "USDC"}
            }
        }
    ))
    
    client.add_tool(MCPTool(
        name="transfer",
        description="Transfer assets",
        input_schema={
            "type": "object",
            "properties": {
                "to_address": {"type": "string"},
                "amount": {"type": "number"},
                "asset": {"type": "string", "default": "USDC"}
            },
            "required": ["to_address", "amount"]
        }
    ))
    
    return client


if __name__ == "__main__":
    # Demo
    import asyncio

    async def demo():
        print("=== MCP Client Demo ===\n")
        
        # Create server manager
        manager = MCPServerManager()
        
        # Register Twitter server
        twitter = create_twitter_mcp_client()
        manager.register_server("twitter", twitter)
        
        # Connect
        await manager.connect_all()
        print()
        
        # List tools
        tools = await twitter.list_tools()
        print(f"Twitter tools: {[t.name for t in tools]}")
        print()
        
        # Call tool
        result = await manager.call_tool("twitter", "get_mentions", {"limit": 5})
        print(f"Tool result: {result}")
        print()
        
        # Disconnect
        manager.disconnect_all()
    
    asyncio.run(demo())
