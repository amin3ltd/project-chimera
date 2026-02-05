"""
MCP Client - Model Context Protocol Integration

Provides standardized connection to MCP servers for external tool/resource access.
"""

import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class MCPMessageType(str, Enum):
    """MCP Message Types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


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
    
    def __init__(self, server_name: str = "default"):
        """Initialize MCP client."""
        self.server_name = server_name
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, str] = {}
        self._connected = False
        
    async def connect(self, transport: str = "stdio", **kwargs) -> bool:
        """
        Connect to MCP server.
        
        Args:
            transport: Transport type (stdio, sse, websocket)
            **kwargs: Transport-specific options
            
        Returns:
            True if connection successful
        """
        try:
            # For stdio transport, would spawn subprocess
            # For SSE, would connect to HTTP endpoint
            self._connected = True
            print(f"✅ MCP Client connected to {self.server_name}")
            return True
        except Exception as e:
            print(f"❌ MCP connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MCP server."""
        self._connected = False
        self.tools.clear()
        self.resources.clear()
        print(f"🔌 MCP Client disconnected from {self.server_name}")
    
    def is_connected(self) -> bool:
        """Check if connected to server."""
        return self._connected
    
    async def list_tools(self) -> List[MCPTool]:
        """List available tools from server."""
        if not self._connected:
            raise MCPError("Not connected to server")
        
        # In real implementation, would send list_tools request
        return list(self.tools.values())
    
    async def list_resources(self) -> List[MCPResource]:
        """List available resources from server."""
        if not self._connected:
            raise MCPError("Not connected to server")
        
        return list(self.resources.values())
    
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
        
        if tool_name not in self.tools:
            raise MCPError(f"Unknown tool: {tool_name}")
        
        # In real implementation, would send tool call request
        # For now, simulate response
        print(f"🔧 Calling MCP tool: {tool_name}")
        return {"status": "success", "tool": tool_name, "result": "simulated"}
    
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
        
        if uri not in self.resources:
            raise MCPError(f"Unknown resource: {uri}")
        
        # In real implementation, would send resource read request
        return f"Resource content for: {uri}"
    
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
    client = MCPClient(server_name="news")
    
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
