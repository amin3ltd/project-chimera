# Project Chimera - Fleet Governance Configuration

This file defines the governance rules for the entire agent fleet.

## Fleet-Wide Policies

### Content Safety
- **AI Disclosure**: All published content MUST include AI disclosure
- **Sensitive Topics**: Politics, health, finance require human review
- **Confidence Threshold**: < 0.70 requires HITL escalation

### Financial Governance
- **Max Daily Spend**: 50 USDC per agent
- **Max Transaction**: 10 USDC per transaction
- **Token Deployment**: Always requires CFO approval

### Behavioral Constraints
- **Never claim to be human**
- **Never share personal info about real people**
- **Never engage in harmful activities**
- **Always verify information before sharing**

## Persona Templates

### SOUL.md Locations
- `/SOUL.md` - Default agent persona
- `skills/skill_*/SOUL.md` - Skill-specific personas (if needed)

## Task Routing

### Planner Rules
- Break goals into atomic tasks
- Prioritize based on campaign goals
- Escalate unclear goals to human

### Worker Rules
- Execute only assigned tasks
- Use MCP tools for all external interactions
- Report failures to Judge

### Judge Rules
- Validate output against persona constraints
- Escalate low confidence (< 0.70) to HITL
- Approve high confidence (> 0.90) automatically

## Fleet Status States

| State | Meaning | Actions Allowed |
|-------|---------|-----------------|
| online | Active and processing | All actions |
| busy | Processing tasks | Read-only operations |
| paused | Paused by operator | No actions |
| offline | Not running | No actions |

## MCP Tool Allowlist

### Required Tools
- `twitter.post_tweet`
- `instagram.publish_media`
- `news.fetch_trends`
- `weaviate.query_memory`

### Restricted Tools (Require Approval)
- `coinbase.transfer`
- `coinbase.deploy_token`
- `mcp-server-deploy.*`

## Emergency Procedures

### Human Escalation
1. Judge detects confidence < 0.70
2. Task added to HITL queue
3. Human reviewer notified
4. Reviewer approves, rejects, or edits
5. Decision propagated to agent

### System Failure
1. Planner detects worker failure
2. Task re-queued with retry count
3. After 3 failures, escalate to human
4. Human can modify task or cancel

## Compliance

### AI Transparency Laws
- All posts include platform-native AI labels
- Identity questions trigger honesty directive
- EU AI Act compliance enabled

### Platform Terms
- Rate limits enforced per platform
- No automated spam behavior
- Respect platform API terms
