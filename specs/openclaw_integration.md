# OpenClaw Integration Specification

## Overview
Project Chimera integrates with the OpenClaw Agent Social Network to enable agent-to-agent communication, discovery, and collaboration.

## OpenClaw Connection Points

### 1. Agent Discovery Protocol
Chimera agents publish their capabilities and availability to the OpenClaw network.

**Schema**:
```json
{
  "agent_id": "uuid-v4-string",
  "agent_type": "influencer_marketing",
  "capabilities": [
    "trend_analysis",
    "content_generation", 
    "social_engagement",
    "agentic_commerce"
  ],
  "version": "1.0.0",
  "status": "available | busy | offline",
  "availability_window": {
    "start": "ISO8601 timestamp",
    "end": "ISO8601 timestamp"
  },
  "endpoint": "mcp://project-chimera/agent/{id}"
}
```

### 2. Task Offloading Protocol
Chimera can delegate tasks to specialized agents on the OpenClaw network.

**Protocol**: `agent://delegate`
```json
{
  "task_id": "uuid-v4",
  "delegating_agent": "chimera-{id}",
  "task_type": "image_generation | video_editing | translation | audio_transcription",
  "priority": "high | medium | low",
  "input_artifacts": [
    {
      "type": "url",
      "value": "https://...",
      "mime_type": "image/jpeg"
    }
  ],
  "requirements": {
    "max_cost_usdc": 5.0,
    "deadline": "ISO8601 timestamp",
    "quality_level": "high"
  },
  "reward_offer": 0.5
}
```

### 3. Knowledge Sharing Protocol
Chimera agents share insights with other agents on the network.

**Protocol**: `agent://share`
```json
{
  "sharing_agent": "chimera-{id}",
  "topic": "trending_topic_analysis",
  "insight_type": "trend_data | engagement_metrics | audience_insights",
  "payload": {
    "topic": "AI Agents",
    "trending_score": 0.92,
    "engagement_velocity": "rising",
    "recommended_action": "create_content_about_ai_trends"
  },
  "ttl_seconds": 3600,
  "reputation_stake": "positive"
}
```

## Integration Points

### A. Availability Status (agent://discover)
Chimera agents broadcast their status to enable discovery:
- **Online**: Ready to receive and process tasks
- **Busy**: Processing existing tasks, may delay new ones
- **Offline**: Not accepting new tasks

### B. Task Delegation (agent://delegate)
When Chimera encounters tasks outside its core capabilities:
1. Query OpenClaw for available specialized agents
2. Negotiate terms (cost, deadline, quality)
3. Delegate task with reward offer
4. Monitor progress and receive results

### C. Collaborative Campaigns
Multiple Chimera instances can coordinate:
- Cross-platform content distribution
- Audience sharing between agents
- Joint promotional campaigns

## Security Considerations

### Agent Authentication
- All OpenClaw communications use agent credentials
- Credentials stored in secure vault (HashiCorp/AWS Secrets Manager)
- Rotated regularly

### Reputation System
- Chimera agents maintain reputation scores
- Based on task completion rate, quality, timeliness
- Affects ability to delegate tasks

### Cost Management
- Budget limits on task delegation
- Auto-rejection of tasks exceeding cost threshold
- Audit trail of all inter-agent transactions

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Discovery Protocol | Planned | MCP resource implementation |
| Task Delegation | Planned | AgentKit integration |
| Knowledge Sharing | Planned | Pub/sub pattern |
| Reputation System | Future | v2.0 |
