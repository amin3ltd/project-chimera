# Project Chimera - Agent Skills

This directory contains the Skills that the Chimera Agent will use at runtime.

## Skill Definition

A **Skill** is a specific capability package that the agent can invoke. Unlike MCP servers (which are external bridges), Skills are reusable functions/scripts bundled with the agent.

## Skill Contracts

### skill_download_youtube
**Purpose**: Download and process YouTube video content

**Input**:
```json
{
  "url": "string",
  "format": "audio | video",
  "output_path": "string"
}
```

**Output**:
```json
{
  "status": "success | error",
  "file_path": "string",
  "duration_seconds": "number"
}
```

### skill_transcribe_audio
**Purpose**: Transcribe audio content to text

**Input**:
```json
{
  "audio_path": "string",
  "language": "string (optional, default: en)"
}
```

**Output**:
```json
{
  "status": "success | error",
  "transcript": "string",
  "confidence_score": "number"
}
```

### skill_analyze_trends
**Purpose**: Analyze content for trending topics

**Input**:
```json
{
  "content": "string",
  "platform": "twitter | instagram | tiktok",
  "max_results": "number (default: 10)",
  "min_relevance_score": "number (default: 0.75)"
}
```

**Output**:
```json
{
  "status": "success | error",
  "trends": [
    {
      "topic": "string",
      "score": "number",
      "velocity": "rising | stable | declining"
    }
  ],
  "analysis_metadata": {}
}
```

**Location**: [`skill_analyze_trends/`](skill_analyze_trends/)
- [`main.py`](skill_analyze_trends/main.py) - Implementation
- [`contract.json`](skill_analyze_trends/contract.json) - Contract definition

### skill_generate_image
**Purpose**: Generate images using MCP image tools with character consistency

**Input**:
```json
{
  "prompt": "string",
  "style": "string (realistic | anime | abstract)",
  "character_ref": "string (optional)",
  "size": "string (default: 1024x1024)",
  "agent_id": "string"
}
```

**Output**:
```json
{
  "status": "success | error",
  "image_url": "string",
  "generation_id": "string",
  "generation_metadata": {}
}
```

**Location**: [`skill_generate_image/`](skill_generate_image/)
- [`main.py`](skill_generate_image/main.py) - Implementation
- [`contract.json`](skill_generate_image/contract.json) - Contract definition

### skill_post_content
**Purpose**: Publish content to social platforms

**Input**:
```json
{
  "platform": "twitter | instagram | threads",
  "text_content": "string",
  "media_urls": ["string"],
  "disclosure_level": "automated | assisted"
}
```

**Output**:
```json
{
  "status": "success | error",
  "post_id": "string",
  "url": "string"
}
```

## Skill Registry

| Skill | Version | Status | MCP Dependencies |
|-------|---------|--------|------------------|
| skill_download_youtube | 1.0.0 | Planned | youtube-mcp |
| skill_transcribe_audio | 1.0.0 | Planned | whisper-mcp |
| skill_analyze_trends | 1.0.0 | Implemented | news-mcp |
| skill_generate_image | 1.0.0 | Implemented | ideogram-mcp, midjourney-mcp |
| skill_post_content | 1.0.0 | Planned | twitter-mcp, instagram-mcp |

## Adding New Skills

1. Create a new directory: `skills/skill_{name}/`
2. Add `__init__.py`, `main.py`, and `contract.json`
3. Define Input/Output schemas using Pydantic
4. Register in the table above
5. Write corresponding tests in `tests/`

## Skill Execution Flow

```
Planner → Worker → Judge
              ↓
        Skill Invocation
              ↓
    ┌────────┴────────┐
    ↓                 ↓
 MCP Tools        Skills/
    ↓                 ↓
 External APIs    Internal Logic
```
