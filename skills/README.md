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
  "max_results": "number (default: 10)"
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
  ]
}
```

### skill_generate_image
**Purpose**: Generate images using MCP image tools

**Input**:
```json
{
  "prompt": "string",
  "style": "string (realistic | anime | abstract)",
  "character_ref": "string (optional)"
}
```

**Output**:
```json
{
  "status": "success | error",
  "image_url": "string",
  "generation_id": "string"
}
```

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

## Adding New Skills

1. Create a new directory: `skills/skill_{name}/`
2. Add `__init__.py`, `main.py`, and `contract.json`
3. Register in `skills/registry.json`
4. Write corresponding tests in `tests/`
