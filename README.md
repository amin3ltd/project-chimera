# Project Chimera - Autonomous AI Influencer Network

<div align="center">

![Project Chimera](https://img.shields.io/badge/Project-Chimera-blue)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-blue)

</div>

## Overview

Project Chimera is an autonomous AI influencer system built on **Spec-Driven Development (SDD)**, **FastRender Swarm Architecture**, and **Model Context Protocol (MCP)**. It enables AI agents to:

- 🔍 Research and identify trends
- 🎨 Generate multimodal content (text, images, video)
- 📱 Manage social media engagement autonomously
- 💰 Execute financial transactions via Agentic Commerce

## Architecture

```
                    ┌─────────────────┐
                    │    PLANNER      │  ← Goal decomposition
                    │  (Strategist)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │ WORKER  │   │ WORKER  │   │ WORKER  │  ← Task execution
         │ #1      │   │ #2      │   │ #n      │
         └────┬────┘   └────┬────┘   └────┬────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │     JUDGE       │  ← Quality control & HITL
                    │   (Gatekeeper)  │
                    └─────────────────┘
```

## Features

### FastRender Swarm Pattern
- **Planner**: Decomposes goals into atomic tasks
- **Worker**: Stateless execution with skill routing
- **Judge**: Quality control with confidence scoring

### MCP Integration
- Twitter, Instagram, News MCP servers
- Weaviate vector memory
- Coinbase AgentKit for commerce

### Human-in-the-Loop (HITL)
- Confidence-based routing (>0.90 auto-approve)
- Mandatory review for sensitive topics
- Dashboard for human operators

## Installation

### Prerequisites
- Python 3.11+
- Redis 7.0+
- uv (fast Python package manager)

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/amin3ltd/project-chimera.git
cd project-chimera

# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make setup

# Or manually
uv pip install -r pyproject.toml
uv pip install -r pyproject.toml[dev]
```

### Option 2: Docker

```bash
# Build the image
docker build -t project-chimera .

# Run tests in Docker
docker run --rm project-chimera make test

# Run interactively
docker run -it --rm -v $(pwd):/app project-chimera bash
```

### Option 3: Docker Compose (Recommended)

```bash
# Start all services including Redis
docker-compose up -d

# Run tests
docker-compose exec chimera make test
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Redis
REDIS_URL=redis://localhost:6379

# Weaviate
WEAVIATE_URL=http://localhost:8080

# Coinbase AgentKit
CDP_API_KEY_NAME=your_api_key_name
CDP_API_KEY_PRIVATE_KEY=your_private_key

# MCP Servers (optional)
MCP_TWITTER_URL=http://localhost:3000
MCP_NEWS_URL=http://localhost:3001
MCP_COINBASE_URL=http://localhost:3002
```

### MCP Server Setup

```bash
# Install MCP servers
npm install -g @anthropic-ai/mcp-server-twitter
npm install -g @anthropic-ai/mcp-server-news
npm install -g @anthropic-ai/mcp-server-coinbase

# Start MCP servers
mcp-server-twitter --port 3000
mcp-server-news --port 3001
mcp-server-coinbase --port 3002
```

## Usage

### Running Services

```bash
# Start the Planner
python -m services.planner

# Start a Worker (in another terminal)
python -m services.worker --worker-id worker-001

# Start the Judge
python -m services.judge
```

### Using Skills

```python
from skills.skill_analyze_trends import AnalyzeTrendsSkill
from skills.skill_memory import MemorySkill
from skills.skill_commerce import CommerceSkill

# Analyze trends
skill = AnalyzeTrendsSkill()
result = skill.execute(
    content="AI agents transforming technology",
    platform="twitter",
    max_results=10
)

# Store memory
memory = MemorySkill(agent_id="chimera-001")
memory.execute(
    action="store",
    content="User interaction about AI",
    memory_type="episodic"
)

# Check wallet balance
commerce = CommerceSkill(agent_id="chimera-001")
result = commerce.execute(action="get_balance")
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_trend_fetcher.py -v
```

## Project Structure

```
project-chimera/
├── components/           # React components (Dashboard, ReviewCard)
├── schemas/              # Pydantic models & SQL schemas
│   ├── trend.py         # Trend data models
│   └── postgres_schema.sql
├── services/             # FastRender swarm services
│   ├── planner.py      # Task decomposition
│   ├── worker.py       # Task execution
│   ├── judge.py        # Quality control
│   └── mcp_client.py   # MCP integration
├── skills/              # Agent skills
│   ├── skill_analyze_trends/
│   ├── skill_generate_image/
│   ├── skill_download_youtube/
│   ├── skill_transcribe_audio/
│   ├── skill_post_content/
│   ├── skill_commerce/
│   └── skill_memory/
├── specs/               # Specification documents
│   ├── _meta.md       # Vision & constraints
│   ├── functional.md   # User stories
│   ├── technical.md    # API contracts
│   └── openclaw_integration.md
├── research/           # Research & strategy
├── tests/              # TDD tests
├── .github/workflows/   # CI/CD
├── .cursor/            # IDE rules
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

## API Reference

### Task Schema

```json
{
  "task_id": "uuid-v4-string",
  "task_type": "generate_content | analyze_trends | execute_transaction",
  "priority": "high | medium | low",
  "goal_description": "string",
  "confidence_score": 0.0-1.0
}
```

### Skill Input/Output

Each skill follows the contract pattern:

```python
# Input
class SkillNameInput(BaseModel):
    param1: str
    param2: int = 10

# Output  
class SkillNameOutput(BaseModel):
    status: str  # "success" | "error"
    result: dict
```

## Documentation

| Document | Description |
|----------|-------------|
| [SRS](srs.txt) | Full Software Requirements Specification |
| [Challenge Guide](projectchimera.txt) | 3-day challenge roadmap |
| [AGENTS.md](AGENTS.md) | Fleet governance rules |
| [SOUL.md](SOUL.md) | Agent persona template |
| [specs/functional.md](specs/functional.md) | User stories |
| [specs/technical.md](specs/technical.md) | API contracts |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following spec-driven development
4. Run tests: `make test`
5. Run linters: `make lint`
6. Commit and push
7. Create Pull Request

## Governance

- **Max Daily Spend**: 50 USDC per agent
- **Max Transaction**: 10 USDC
- **Token Deployment**: Requires CFO approval
- **AI Disclosure**: Mandatory on published content
- **HITL**: Escalation for confidence < 0.70

## License

MIT License - See LICENSE file for details.

## Support

- 📧 Email: support@aiqem.tech
- 📖 Docs: [docs.project-chimera.dev](https://docs.project-chimera.dev)
- 💬 Discord: [discord.gg/project-chimera](https://discord.gg/project-chimera)
