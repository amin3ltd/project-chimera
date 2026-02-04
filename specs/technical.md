# Technical Specifications

## API Contracts

### Task Schema (Planner → Worker)

```json
{
  "task_id": "uuid-v4-string",
  "task_type": "generate_content | reply_comment | execute_transaction",
  "priority": "high | medium | low",
  "context": {
    "goal_description": "string",
    "persona_constraints": ["string"],
    "required_resources": ["mcp://twitter/mentions/123"]
  },
  "assigned_worker_id": "string",
  "created_at": "timestamp",
  "status": "pending | in_progress | review | complete"
}
```

### MCP Tool: Post Content

```json
{
  "name": "post_content",
  "description": "Publishes text and media to a connected social platform.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "platform": {
        "type": "string",
        "enum": ["twitter", "instagram", "threads"]
      },
      "text_content": {
        "type": "string"
      },
      "media_urls": {
        "type": "array",
        "items": {"type": "string"}
      },
      "disclosure_level": {
        "type": "string",
        "enum": ["automated", "assisted", "none"]
      }
    },
    "required": ["platform", "text_content"]
  }
}
```

## Database Schema

### Agent Memory (Weaviate Collection)
- `agent_id`: UUID
- `content_type`: enum(text, image, video, interaction)
- `embedding`: vector(1536)
- `metadata`: JSON
- `created_at`: timestamp
- `importance_score`: float(0.0-1.0)

### Campaign Goals (Redis)
- `campaign_id`: string
- `goals`: array of objects
- `budget_limit`: float
- `status`: enum(active, paused, completed)
- `updated_at`: timestamp

### Task Queue (Redis)
- Queue: `task_queue` - Planner → Worker
- Queue: `review_queue` - Worker → Judge
- Queue: `hitl_queue` - Judge → Human

## MCP Resources

| Resource | Purpose |
|----------|---------|
| `twitter://mentions/recent` | Monitor agent mentions |
| `news://{topic}/trends` | Trend detection |
| `market://crypto/{asset}/price` | Financial data |
| `memory://agent/{id}/recent` | Retrieve recent memories |

## Service Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         Central Orchestrator            │
                    │  (Planner → Worker → Judge Pattern)     │
                    └─────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   MCP Host   │  │    Redis     │  │   Weaviate   │
            │  (Runtime)   │  │  (Queues)    │  │  (Memory)    │
            └──────────────┘  └──────────────┘  └──────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Twitter │ │  News   │ │Coinbase │
   │   MCP   │ │   MCP   │ │   MCP   │
   └─────────┘ └─────────┘ └─────────┘
