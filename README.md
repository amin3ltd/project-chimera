# Project Chimera - Autonomous Influencer Network

## Overview
Project Chimera is an autonomous AI influencer system that researches trends, generates content, and manages social media engagement without human intervention.

## Architecture
- **FastRender Swarm Pattern**: Planner → Worker → Judge coordination
- **MCP (Model Context Protocol)**: Universal connectivity layer
- **Agentic Commerce**: Financial autonomy via Coinbase AgentKit

## Project Structure
```
project-chimera/
├── specs/              # Specification documents
│   ├── _meta.md       # Vision and constraints
│   ├── functional.md  # User stories and requirements
│   └── technical.md   # API contracts and database schema
├── skills/             # Agent runtime skills
│   └── README.md      # Skill contracts
├── tests/             # Failing tests (TDD approach)
├── research/          # Research notes and strategy
├── .github/workflows/ # CI/CD pipeline
├── .cursor/rules      # IDE context rules
├── Dockerfile
├── Makefile
└── pyproject.toml
```

## Quick Start
```bash
# Install dependencies
make setup

# Run tests
make test

# Build Docker
docker build -t project-chimera .
```

## Documentation
- [SRS Document](srs.txt) - Full requirements specification
- [Challenge Guide](projectchimera.txt) - 3-day challenge roadmap
