# Component Inventory Template

## Overview

Use this template to catalog every component in a source GitHub Copilot repository before porting. Fill in one row per component identified during analysis. This inventory drives the porting plan (see `docs/templates/porting-plan.md`).

**Fulfills:** FOUND-FR-02 (analyze source directory), FOUND-FR-03 (classify by type)

---

## Instructions

1. **Walk the source directory tree** — Start from the repo root and recursively list files and directories.
2. **Classify each component** — Assign a type from the Component Types table below.
3. **Record metadata** — For each component, fill in: path, type, sub-type (if applicable), purpose, porting target, and notes.
4. **Flag unknowns** — If you encounter a component that doesn't fit any type, mark it as `Unknown` and add a note. These become gaps to document (FOUND-FR-11).

---

## Component Types

| Type | Description | Examples |
|------|-------------|----------|
| `agent_prompt` | System prompt files for AI coding assistants | `.github/agents/dirk.md`, `.github/agents/*.md` |
| `workflow` | CI/CD pipeline definitions | `.github/workflows/*.yml` |
| `config` | Configuration files consumed by the tool | `*.config.yml`, `repos.yml`, `pyproject.toml` |
| `cli_tool` | CLI entry points and command implementations | `src/*/cli.py`, `src/*/main.py`, `bin/*` |
| `test_suite` | Test files and test configuration | `tests/`, `pytest.ini`, `conftest.py` |
| `documentation` | Project documentation | `README.md`, `docs/*.md`, `CONTRIBUTING.md` |
| `bootstrap` | Setup scripts and dev environment config | `script/setup`, `Makefile`, `requirements.txt`, `.gitignore` |
| `source_library` | Core library code (non-CLI, non-agent) | `src/*/` (utility modules, models, helpers) |
| `skill_module` | Individual Copilot skill or extension module | `src/*/skills/*.py`, Copilot skills directories |
| `unknown` | Cannot be classified with current types | — |

---

## Inventory Table Template

```markdown
## Component Inventory: [Repository Name]

**Source path:** `/path/to/source-repo`
**Analyzed by:** [Agent name]
**Date:** [YYYY-MM-DD]

| # | Component | Path (relative to source root) | Type | Sub-Type | Purpose | Porting Target | Priority | Notes |
|---|-----------|--------------------------------|------|----------|---------|----------------|----------|-------|
| 1 | [name] | [path] | [type] | [sub-type] | [1-2 sentences] | [.claude/agents/... or keep as-is or N/A] | Must/Should/Nice | [notes] |
| 2 | [name] | [path] | [type] | [sub-type] | [1-2 sentences] | [.claude/agents/... or keep as-is or N/A] | Must/Should/Nice | [notes] |
```

---

## Metadata Field Definitions

| Field | Description | Required |
|-------|-------------|----------|
| `#` | Sequential row number | Yes |
| `Component` | Short name for the component | Yes |
| `Path` | Path relative to the source repository root | Yes |
| `Type` | One of the types from the Component Types table | Yes |
| `Sub-Type` | Optional refinement (e.g., "agent prompt — orchestrator") | No |
| `Purpose` | 1–2 sentence description of what it does | Yes |
| `Porting Target` | Where this maps in Claude Code format (or "Keep as-is" if no porting needed) | Yes |
| `Priority` | Must, Should, or Nice based on the PRD/feature priorities | Yes |
| `Notes` | Observations, dependencies, or gaps | No |

---

## Gap Log Template

Use this section to document any components that don't cleanly map to Claude Code equivalents (FOUND-FR-11):

| # | Component | Gap Description | Proposed Resolution |
|---|-----------|-----------------|---------------------|
| 1 | [name] | [what doesn't map and why] | [workaround or defer] |

---

## Completed Example (Dirk / ai-etcetera)

**Source path:** `repos/ai-etcetera/`
**Analyzed by:** porting-architect
**Date:** 2026-04-24

| # | Component | Path | Type | Sub-Type | Purpose | Porting Target | Priority | Notes |
|---|-----------|------|------|----------|---------|----------------|----------|-------|
| 1 | Dirk agent prompt | `.github/agents/dirk.md` | agent_prompt | — | System prompt that defines Dirk's operating loop, output contract, and serendipity guidance | `.claude/agents/dirk.md` | Must | Core porting artifact |
| 2 | Weekly scan workflow | `.github/workflows/dirk-scan.yml` | workflow | CI/CD | Scheduled weekly scan, checkout + Python setup + `dirk run --all` + PR creation | Manual pattern in CLAUDE.md | Should | PR creation is GitHub-specific; not ported |
| 3 | Dirk config | `dirk.config.yml` | config | — | YAML config for scope, depth, thresholds, output paths | Keep as-is | Must | Consumed by Python CLI |
| 4 | Repo scope | `repos.yml` | config | — | List of repos to analyze | Keep as-is | Must | Consumed by Python CLI |
| 5 | Python project config | `pyproject.toml` | config | build | Build system, dependencies, entry point config | Keep as-is | Must | Consumed by pip/setuptools |
| 6 | Python CLI | `src/dirk/cli.py` | cli_tool | — | Deterministic pipeline: inventory, deps, interfaces, concepts, links, curation, graph, reports | Keep as-is | Must | Invoked by agents via bash tool |
| 7 | CLI support modules | `src/dirk/config.py`, `src/dirk/storage.py`, `src/dirk/writers.py`, `src/dirk/agent.py` | source_library | — | Config loading, SQLite storage, report writing, agent orchestration | Keep as-is | Must | Part of the Python CLI |
| 8 | Skills directory | `src/dirk/skills/` | skill_module | — | Individual skill modules (repo_inventory, dependency_mapper, etc.) | Keep as-is | Must | Invoked by `dirk run --all` |
| 9 | Test suite | `tests/` | test_suite | pytest | pytest suite for validating Dirk CLI | Keep as-is (run via bash) | Must | Run for validation |
| 10 | README | `README.md` | documentation | — | Project documentation | Reference in CLAUDE.md | Should | |
| 11 | Docs | `docs/PHASES.md` | documentation | — | Phase documentation | Reference as needed | Nice | |
| 12 | Git ignore | `.gitignore` | bootstrap | — | Git ignore rules | Keep as-is | Nice | |
| 13 | License | `LICENSE` | documentation | — | MIT license | Keep as-is | Nice | |

**Gaps:** None identified. All components fit the existing type categories and Porting Targets.
