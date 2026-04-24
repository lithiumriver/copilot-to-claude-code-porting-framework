# testing — Claude Code Configuration

## Agent Team

This project uses a custom Claude Code agent team managed by Agent Forge.

| Agent | Role |
|---|---|
| `project-orchestrator` | Coordinates specialist agents through PRD implementation phases |

> Agent files live in `.claude/plugins/agent-forge/agents/`. Run `/forge-build-agent-team` to generate specialist agents from your PRD.

## Workflow

1. **Build a PRD** — `/forge-build-prd` (if not done yet)
2. **Generate agents** — `/forge-build-agent-team`
3. **Execute the build** — invoke `project-orchestrator` to coordinate phases

For decomposed projects:
1. `/forge-build-prd` → `/forge-decompose-prd` → `/forge-build-agent-team` → build feature by feature

## Conventions

- Agent names are lowercase-hyphenated (e.g., `backend-engineer`, `qa-tester`)
- Each agent owns one domain — no overlapping responsibilities
- Agents reference the PRD by section number, not by copying content
- Commit after each phase completes

## Dirk — Holistic Research Agent

The Dirk source lives in `repos/ai-etcetera/`. A virtual environment is at `/opt/testing/.venv/` with all dependencies installed (`dirk` CLI, PyYAML, Click, pytest, requests).

### Setup

```bash
source /opt/testing/.venv/bin/activate
pip install -e "repos/ai-etcetera[github,dev]"
```

### Configuration

Edit `repos/ai-etcetera/dirk.config.yml` (scope, depth, serendipity) and `repos/ai-etcetera/repos.yml` (repos to scan).

### Usage

Invoke the `dirk` agent, or run directly:

```bash
source /opt/testing/.venv/bin/activate
cd repos/ai-etcetera && dirk run --all
```

### Testing

```bash
source /opt/testing/.venv/bin/activate
cd repos/ai-etcetera && pytest
```

## Manual Dirk Scan (Ported from GitHub Actions)

Run the full Dirk pipeline on demand — the equivalent of the original weekly scheduled scan:

1. **Run the pipeline** — `dirk run --all` (from `repos/ai-etcetera/`)
2. **Review changes** — check `git status graph/ findings/` for new/modified files
3. **Interpret output**:
   - `graph/` — knowledge graph database (`graph.db`) and JSON export (`graph.json`)
   - `findings/` — markdown reports (`latest.md`, `delta-*.md`)

PR creation is GitHub-specific and not ported. Changes are reviewed locally via `git diff`.

## EJS Recording Contract (optional)

If using the Engineering Journey System:
- Record decisions and sub-agent work to the session journey file
- Query `.ejs.db` before reading raw markdown for past context
- Attribute every entry by agent name
