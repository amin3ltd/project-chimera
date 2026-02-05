# IDE Chat History 

---

## Phase 0 — Repo setup & guardrails
- “Initialize the repo structure for Project Chimera with `services/`, `skills/`, `schemas/`, `tests/`, `specs/`, and `research/`.”
- “Create a `pyproject.toml` suitable for Python 3.11+ and include dev deps for ruff/mypy/pytest.”
- “Add a `Makefile` with `setup`, `test`, `lint`, and `docker-test` targets.”
- “Add a `Dockerfile` that installs deps with `uv` and can run tests.”
- “Add GitHub Actions CI to run ruff + mypy + pytest, then build Docker.”
- “Add `.coderabbit.yaml` policy to check spec alignment + security.”
- “Create `.cursor/rules` that enforces ‘read `specs/` before coding’.”
- “Add `AGENTS.md` governance rules and a default `SOUL.md` persona.”

## Phase 1 — Specs-first (SDD)
- “Create `specs/_meta.md` with the system vision and non-negotiable constraints.”
- “Write `specs/functional.md` user stories for trend research, content generation, posting, memory, commerce, and HITL.”
- “Write `specs/technical.md` including JSON contracts + DB schema expectations.”
- “Draft `specs/openclaw_integration.md` describing how the system would advertise agent status/capabilities.”
- “Create `research/reading_notes.md` summarizing a16z/OpenClaw/MoltBook and how they map to Chimera.”
- “Write `research/architecture_strategy.md` to justify hierarchical swarm selection.”
- “Write `research/tooling_strategy.md` to separate Dev MCP vs Runtime Skills.”

## Phase 2 — Core swarm services (Planner / Worker / Judge)
- “Implement the Planner service with a Task schema and a GlobalState schema.”
- “Use Redis sorted sets for priority queuing and make the Planner push tasks with a score.”
- “Implement Worker that pops tasks, routes by `task_type`, and produces a TaskResult with confidence.”
- “Implement Judge that reviews outputs, applies confidence thresholds, and escalates sensitive topics to HITL.”
- “Add OCC state version checks before committing outputs.”
- “Add a demo mode for each service when Redis is not available.”
- “Fix any Redis API misuse (e.g., make sure the zset pop method exists in redis-py).”

## Phase 3 — Skills (runtime capabilities)
- “Create skill packages for: analyze trends, generate image, post content, download youtube, transcribe audio, commerce, memory.”
- “Ensure each skill has clear Pydantic-ish input/output contracts and an `execute(...)` entrypoint.”
- “Write unit tests that assert skill interface parameters match the expected contract.”
- “Make all skills importable via the `skills/` package.”

## Phase 4 — MCP integration (real, runnable)
- “Implement an MCP client wrapper so tools/resources can be called end-to-end.”
- “Use stdio transport to spawn an MCP server process and communicate via the official `mcp` SDK.”
- “Add in-repo MCP servers for development: a `news` server with `news://latest` + `fetch_trends`.”
- “Add an in-repo memory MCP server with `store_memory` + `search_memory` and a `memory://recent` resource.”
- “Add tests that connect to the MCP stdio server and successfully call a tool + read a resource.”

## Phase 5 — Perception subsystem (continuous monitoring + semantic filtering)
- “Implement continuous polling of MCP resources on an interval.”
- “Implement a lightweight semantic filter with a relevance threshold and ensure it blocks irrelevant items.”
- “When relevant, emit `Task` objects into Redis so the swarm can process them.”
- “Make Perception configurable: interval, threshold, resources, goals.”
- “Add a CLI entrypoint (`chimera perception`) that runs as a long-lived subsystem.”

## Phase 6 — HITL + Orchestrator UI components
- “Implement a `ReviewCard` component that displays generated content, confidence, reasoning, and actions.”
- “Make the dashboard responsive and attractive (mobile-first, clean spacing/typography).”
- “Create an HITL dashboard page component that lays out review cards in a responsive grid.”
- “Add an Orchestrator Dashboard component with tabs: Fleet, Campaigns, HITL.”
- “Implement a Fleet Status View component (agent state, wallet health, queue depth).”
- “Implement a Campaign Composer component that shows a goal input and a task tree preview.”

## Phase 7 — Multi-tenancy (tenant isolation)
- “Add a tenant context model and enforce tenant-prefixed Redis keyspaces.”
- “Ensure task queues, review queues, HITL queues, outputs, campaign state, and budgets are isolated per tenant.”
- “Add `tenant_id` fields to Task and TaskResult and propagate them through Worker → Judge.”
- “Update Perception to accept `--tenant-id` and enqueue tasks into the correct tenant queue.”
- “Add tests that prove Redis keyspace names differ across tenants.”

## Phase 8 — Secrets manager injection
- “Implement a secrets facade with an env provider by default.”
- “Add optional AWS Secrets Manager provider (only if boto3 is present).”
- “Update commerce wallet initialization to read Coinbase keys via the secrets facade.”
- “Add tests that `get_required` fails safely when missing and succeeds when present.”

## Phase 9 — Packaging, docs, and submission artifacts
- “Fix packaging so `pip install .` works with Hatch (set wheel packages).”
- “Add `project_chimera/__main__.py` so `python -m project_chimera` works.”
- “Add a `chimera` console script entrypoint.”
- “Update README with clear install + quickstart steps (Redis + chimera commands).”
- “Update `research/SUBMISSION_REPORT.md` to reflect current features + tests + commit count.”
- “Generate a Feb 5 submission report in both `.md` and `.pdf` and keep it updated.”
- “Add an offline script to generate a PDF from markdown (no external dependencies).”

## Phase 10 — Maintenance queries (ongoing)
- “Run the full suite: ruff, mypy, pytest — fix all failures and keep changes minimal.”
- “Stage, commit, and push each logical change separately with clear commit messages.”
- “Confirm that `origin/master` is up-to-date and no local commits are missing.”

