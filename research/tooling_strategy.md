# Tooling Strategy for Project Chimera

## Overview
This document outlines the Developer MCPs (Model Context Protocol servers) and tools used during development, distinct from the Runtime MCPs that the Chimera Agent uses.

## Developer Tools (MCPs)

### MCP Selection Criteria
- Must enhance developer productivity
- Must integrate with Cursor IDE
- Must support spec-driven development workflow

### Selected Developer MCPs

| MCP Server | Purpose | Configuration |
|------------|---------|---------------|
| git-mcp | Version control operations | `GIT_TOKEN` in environment |
| filesystem-mcp | File read/write/edit | Read/write permissions configured |
| fetch-mcp | HTTP requests for APIs | No auth required |

### MCP Configuration

#### git-mcp
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-git"]
}
```
**Capabilities:**
- Commit creation
- Branch management
- Push/Pull operations
- Diff viewing

#### filesystem-mcp
```json
{
  "command": "npx", 
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
}
```
**Capabilities:**
- Read files
- Write files
- List directories
- Glob pattern matching

#### fetch-mcp
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-fetch"]
}
```
**Capabilities:**
- HTTP GET requests
- JSON response parsing
- API testing

## Runtime Tools (MCPs for Chimera Agent)

### Agent Runtime MCPs

| MCP Server | Purpose | Status |
|------------|---------|--------|
| twitter-mcp | Post tweets, read mentions | Planned |
| instagram-mcp | Publish media, engage | Planned |
| news-mcp | Fetch trending topics | Implemented |
| weaviate-mcp | Memory retrieval/storage | Planned |
| coinbase-mcp | Wallet operations | Planned |
| ideogram-mcp | Image generation | Implemented |

## Distinction: Developer vs. Runtime Tools

| Aspect | Developer MCPs | Runtime MCPs |
|--------|----------------|--------------|
| **User** | Developer (human) | Chimera Agent (AI) |
| **Purpose** | Code editing, git ops, testing | Social posting, trend analysis |
| **Environment** | IDE/Development | Production/Runtime |
| **Security** | Local credentials | Agent-managed wallets |

## MCP Setup Instructions

### Step 1: Install MCP Servers
```bash
# Install git-mcp
npm install -g @modelcontextprotocol/server-git

# Install filesystem-mcp
npm install -g @modelcontextprotocol/server-filesystem

# Install fetch-mcp
npm install -g @modelcontextprotocol/server-fetch
```

### Step 2: Configure Cursor
Add to `.cursor/mcp.json`:
```json
{
  "servers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

### Step 3: Verify Connection
Check Cursor status bar for MCP server connectivity indicators.

## Security Considerations

### Developer Tools
- Store API tokens in `.env` file (not committed)
- Use read-only filesystem access where possible
- Rotate tokens regularly

### Runtime Tools
- Agent manages its own credentials via Coinbase AgentKit
- Non-custodial wallet architecture
- Budget governance on all transactions
