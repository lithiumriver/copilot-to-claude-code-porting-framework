# Product Vision: Copilot-to-Claude Code Porting Framework

## 1. Overview

**Product Name:** Copilot-to-Claude Code Porting Framework

**Summary:** A reusable process and toolchain for porting frameworks, plugins, skills, and workflows built for GitHub Copilot into Claude Code compatible format. The framework defines a systematic approach for analyzing a source repository and reshaping each component into its Claude Code equivalent — agent markdown files, skills, workflow hooks, and project configuration.

**Target Platform:** Claude Code CLI (Linux, macOS, Windows via VS Code / JetBrains / standalone terminal)

**Key Constraints:**
- The source directory is provided interactively at the start of each project (no hardcoded paths)
- Ported components must follow existing Claude Code conventions (`.claude/agents/`, `.claude/skills/`, `CLAUDE.md`)
- The porting process is generative — it builds Claude Code-native artifacts rather than wrapping or shimming the original
- Original source repositories are treated as read-only inputs; no modifications are made upstream
- All porting work is executed by Claude Code agents using the Agent Forge system

**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](copilot-to-claude-code-porting-framework.md)

---

## 2. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-24 | — | Initial product vision (decomposed from PRD v1.0) |

---

## 3. Goals and Non-Goals

### 3.1 Goals
- Define a **repeatable, documented process** for analyzing a GitHub Copilot repository and mapping its components to Claude Code equivalents
- Produce a **mapping specification** that translates each Copilot concept to its Claude Code counterpart
- Deliver a **set of Claude Code agent definitions** (`.claude/agents/`) that encapsulate the ported functionality
- Create **bootstrap scripts and configuration** that allow the ported components to be installed and run within a Claude Code session
- Provide **documentation** at both the framework level and the project level
- Run the **original test suite** to validate that the ported components function correctly
- Use the **Dirk** repository (`ai-etcetera`) as the first case study

### 3.2 Non-Goals
- Maintaining a bidirectional sync with the original Copilot repository after porting
- Building a generic "convert any Copilot extension" CLI tool — the framework is process-oriented, not a standalone converter binary
- Modifying or contributing back to the original Copilot repositories
- Supporting every Copilot extension type (focuses on the patterns found in the target repository)
- Reimplementing the Python runtime of Dirk in another language — the ported agents call the existing Python CLI through the bash tool

---

## 4. Personas

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| Framework User | A developer who wants to port a Copilot repo to Claude Code format | Clear steps, mapping reference, validated templates, working example |
| End User | A Claude Code user who installs and runs the ported components | Smooth setup, familiar interaction patterns, clear instructions |
| Framework Maintainer | The developer evolving the porting framework across multiple source repos | Abstracted patterns, reusable templates, feedback loop from each project |

---

## 5. Research Findings

### 5.1 Source Repository Analysis: Dirk / ai-etcetera

The Dirk repository implements a holistic research agent that scans GitHub repositories and produces a knowledge graph of connections between them. Key architectural observations:

**Component Inventory:**

| Component | Location | Purpose | Porting Target |
|-----------|----------|---------|----------------|
| Agent prompt | `.github/agents/dirk.md` | System prompt with operating loop, output contract, serendipity guidance | `.claude/agents/dirk.md` |
| Python CLI | `src/dirk/` | Deterministic pipeline: inventory, dependency mapping, interface extraction, graph storage, report writing | Keep as-is; agents call via bash tool |
| Skills dir | `src/dirk/skills/` | Individual skill modules that the CLI orchestrates | `.claude/skills/` or keep as Python modules |
| Config schema | `dirk.config.yml` | YAML config for scope, depth, thresholds, output paths | Keep as-is |
| Repo scope | `repos.yml` | List of repos to analyze | Keep as-is |
| CI workflow | `.github/workflows/dirk-scan.yml` | Scheduled weekly scan + PR creation | Port to Claude Code hooks/cron or manual pattern |
| Tests | `tests/` | pytest suite | Run as-is for validation |
| Docs | `README.md`, `docs/PHASES.md` | Project and phase documentation | Reference in CLAUDE.md |
| Python project config | `pyproject.toml` | Build system, dependencies, entry point | Keep as-is |

**Key Architecture Patterns to Preserve:**
- Agent-as-runtime principle: smart skills run inside the agent session; the Python CLI handles deterministic storage/scanning/reporting
- Phase-based pipeline: Phases 1–5 with clear data dependencies
- CLI verbs as surface area: the agent orchestrates by calling small CLI verbs

### 5.2 Claude Code Conventions

The target environment uses these conventions:
- Agent files: `.claude/agents/<name>.md` with YAML frontmatter (name, description, tools)
- Skills: `.claude/skills/<name>/SKILL.md` with process documentation
- Agent Forge plugins: `.claude/plugins/agent-forge/agents/` for multi-agent teams
- Project config: `CLAUDE.md` at repo root for project-level instructions
- Workflow hooks: Via `settings.json` hooks configuration
- Scheduled tasks: Via the `schedule` skill for recurring operations

### 5.3 Technology Currency Check

| Technology | Version in Repo | Latest Stable | Notes |
|-----------|-----------------|---------------|-------|
| Python | >=3.10 | 3.13 (Apr 2026) | Compatible |
| PyYAML | >=6.0 | 6.0.2 | Current |
| Click | >=8.1 | 8.1.8 | Current |
| SQLite | stdlib | N/A | No action needed |
| setuptools | >=68 | 75.x | Still compatible |
| pytest | >=7.4 | 8.x | Compatible |

No deprecation or EOL concerns.

### 5.4 Copilot-to-Claude Code Mapping Reference

| Copilot Concept | Claude Code Equivalent | Translation Notes |
|----------------|------------------------|-------------------|
| `.github/agents/<name>.md` | `.claude/agents/<name>.md` | Add YAML frontmatter; adjust tool permissions |
| GitHub Actions workflow | `settings.json` hooks + cron/schedule skill | Map triggers to Claude Code equivalents |
| Copilot skills/extensions | `.claude/skills/<name>/SKILL.md` | Document as skill files with process steps |
| `pyproject.toml` / Python package | Keep as-is | No translation needed; agents call via bash |
| CLI entry points | Keep as-is | Agents invoke via bash tool |
| YAML config files | Keep as-is | Compatible format |
| `README.md` project docs | `CLAUDE.md` + reference original README | CLAUDE.md gets project instructions |
| Bootstrap scripts | `script/setup` or documented in CLAUDE.md | Adapt to Claude Code setup conventions |
| Test suite (`pytest`) | Keep as-is | Run via bash for validation |

---

## 6. Technical Architecture

### 6.1 Technology Stack

| Component | Technology | Version Notes |
|-----------|-----------|---------------|
| Target runtime | Claude Code CLI | Uses Claude Opus 4.7 / Sonnet 4.6 agents |
| Agent format | Markdown + YAML frontmatter | `.claude/agents/*.md` |
| Skill format | Markdown | `.claude/skills/*/SKILL.md` |
| Agent Forge | Plugin system | `.claude/plugins/agent-forge/` |
| Source language | Python 3.10+ | Keep as-is |
| Build system | setuptools / pyproject.toml | Keep as-is |
| Testing | pytest 7+ | Keep as-is |
| Sourcing | Interactive prompt | User provides source dir at start |

### 6.2 Project Structure (After Porting)

```
/opt/testing/
├── .claude/
│   ├── agents/
│   │   ├── dirk.md                        # Ported from .github/agents/dirk.md
│   │   └── project-orchestrator.md        # Existing
│   ├── skills/
│   │   └── forge-build-prd/              # Existing
│   ├── plugins/
│   │   └── agent-forge/                  # Existing
│   └── settings.json                     # Hooks / permissions
├── repos/
│   └── ai-etcetera/                      # Source repo (read-only input)
│       ├── .github/agents/dirk.md        # Original agent prompt
│       ├── src/dirk/                     # Python CLI (kept as-is)
│       ├── tests/                        # Test suite (kept as-is)
│       ├── dirk.config.yml               # Config (kept as-is)
│       ├── repos.yml                     # Repo scope (kept as-is)
│       ├── pyproject.toml                # Build config (kept as-is)
│       └── README.md                     # Project docs (kept as-is)
├── docs/
│   ├── copilot-to-claude-code-porting-framework.md  # Original PRD
│   ├── product-vision.md                             # This document
│   └── features/
│       ├── foundation.md                # Feature: Foundation
│       ├── dirk-agent-port.md           # Feature: Dirk Agent Port
│       ├── bootstrap-setup.md           # Feature: Bootstrap & Setup
│       ├── workflow-porting.md          # Feature: Workflow Porting
│       └── validation-testing.md        # Feature: Validation & Testing
├── config.yaml                          # LiteLLM config (existing)
├── CLAUDE.md                            # Project instructions
└── .env                                 # Environment variables
```

### 6.3 Key APIs / Interfaces

| Interface | Location | Purpose |
|-----------|----------|---------|
| Dirk CLI | `repos/ai-etcetera/src/dirk/cli.py` | CLI entry point: `dirk init`, `dirk scan`, `dirk run --all` |
| Config loader | `repos/ai-etcetera/src/dirk/config.py` | Reads `dirk.config.yml` |
| Graph storage | `repos/ai-etcetera/src/dirk/storage.py` | SQLite read/write for knowledge graph |
| Agent definition | `.claude/agents/dirk.md` | Claude Code agent that orchestrates Dirk |
| Agent invocation | `claude` CLI | `claude` with agent flag to invoke the Dirk agent |

---

## 7. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NF-01 | Porting process for a new repo shall complete within a single Claude Code session | Must |
| NF-02 | Ported agents shall load without YAML frontmatter or Markdown parsing errors | Must |
| NF-03 | Ported components shall not modify the original source repository (read-only access) | Must |
| NF-04 | CLAUDE.md shall be kept concise (under 50 lines of instructions) | Should |
| NF-05 | Agent definitions shall use a single `tools:` list with only the minimum tools needed | Should |
| NF-06 | Porting process shall be repeatable — running the framework on the same source repo twice produces the same output | Should |

---

## 8. Security and Privacy

| ID | Requirement | Priority |
|----|-------------|----------|
| SP-01 | Source repository is treated as read-only; no writes, no modifications | Must |
| SP-02 | All porting work occurs within the local Claude Code session; no external data transmission | Must |
| SP-03 | If the source repo contains `.env` files or secrets, they must be excluded from porting and explicitly noted | Must |
| SP-04 | Ported agent definitions must not embed API keys, tokens, or credentials | Must |
| SP-05 | Agent tool permissions should be scoped to the minimum required | Should |

---

## 9. Accessibility

| ID | Requirement | Priority |
|----|-------------|----------|
| ACC-01 | Documentation shall use clear Markdown formatting compatible with terminal rendering | Should |
| ACC-02 | CLAUDE.md shall use plain language and avoid ambiguous jargon | Should |
| ACC-03 | Agent descriptions in YAML frontmatter shall be self-explanatory | Should |

---

## 10. System States / Lifecycle

The porting framework follows a linear progression through defined states:

```
IDLE → ANALYZING → MAPPING → GENERATING → VALIDATING → DOCUMENTING → COMPLETE
                                                                       │
                                                                       ▼
                                                                    FAILED
```

| State | Description | Transitions |
|-------|-------------|-------------|
| IDLE | Awaiting user input (source directory) | → ANALYZING (when provided) |
| ANALYZING | Scanning source directory, building component inventory | → MAPPING or → FAILED |
| MAPPING | Classifying components, applying mapping reference | → GENERATING |
| GENERATING | Writing Claude Code artifacts | → VALIDATING |
| VALIDATING | Running tests, verifying agent loads | → DOCUMENTING or → FAILED |
| DOCUMENTING | Writing final docs, porting decisions, open items | → COMPLETE |
| COMPLETE | All phases finished successfully | (terminal) |
| FAILED | Error at any phase | Requires re-entry or manual fix |

---

## 11. Analytics / Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Components ported | 100% of identified items | Component inventory checklist |
| Test suite pass rate | 100% | pytest exit code |
| Agent load success | All agents load without errors | Claude Code agent invocation |
| Dry-run output | Graph/findings generated same as direct CLI | Compare output files |
| Time to port a repo | Under 2 Claude Code sessions | Session tracking |

---

## 12. Dependencies and Risks

### 12.1 Dependencies

| Dependency | Type | Risk if Unavailable | Mitigation |
|------------|------|---------------------|------------|
| Source repository (ai-etcetera) | Local filesystem | Cannot analyze or port | Must have source checked out before starting |
| Python 3.10+ | Runtime | Dirk CLI won't run | Verify Python version early |
| Claude Code CLI | Runtime | Cannot create or use agents | Framework is documentation-only without it |
| pip / setuptools | Build | Cannot install Dirk deps | Include in system requirements check |
| Network (for GitHub Actions) | Service | Cannot validate CI porting | CI porting is "Should" priority; manual fallback |

### 12.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Source repo has unsupported component types | Medium | Medium | Framework is extensible; add new mapping entries |
| Python version conflicts | Low | Medium | Validate compatibility early |
| Agent prompt references Copilot-specific features | Medium | High | Identify during analysis; replace or note as gaps |
| Source repo contains large binaries | Low | Low | Exclude binary/generated dirs from analysis scope |

---

## 13. Future Considerations

| Item | Description | Potential Version |
|------|-------------|-------------------|
| Automated porting CLI | Standalone Python CLI tool for analysis, mapping, and generation | v2 |
| Multi-repo batch porting | Port multiple Copilot repos in a single session | v2 |
| Bidirectional sync hooks | Detect upstream changes in the source repo and flag them | v3 |
| Community template library | Share porting templates for common Copilot patterns | v3 |
| Copilot MCP server support | Handle repos that define MCP servers | v2 |

---

## 14. Features

Summary of all features decomposed from this product vision:

| # | Feature | File | Dependencies | Priority |
|---|---------|------|-------------|----------|
| 1 | Foundation | [docs/features/foundation.md](features/foundation.md) | None | Must |
| 2 | Dirk Agent Port | [docs/features/dirk-agent-port.md](features/dirk-agent-port.md) | Feature 1 | Must |
| 3 | Bootstrap & Setup | [docs/features/bootstrap-setup.md](features/bootstrap-setup.md) | Feature 2 | Should |
| 4 | Workflow Porting | [docs/features/workflow-porting.md](features/workflow-porting.md) | Feature 1 | Should |
| 5 | Validation & Testing | [docs/features/validation-testing.md](features/validation-testing.md) | Features 2, 3 | Should |

### Feature Dependency Graph

```
Feature 1 (Foundation)
├── Feature 2 (Dirk Agent Port) — can start after Feature 1
│   ├── Feature 3 (Bootstrap & Setup) — can start after Feature 2
│   └── Feature 4 (Workflow Porting) — can start after Feature 1
│
Feature 2 + Feature 3 → Feature 5 (Validation & Testing) — requires both
```

---

## 15. Glossary

| Term | Definition |
|------|------------|
| Agent Forge | Claude Code plugin system for building multi-agent teams using agent definition files |
| CLAUDE.md | Project-level configuration file that provides instructions to Claude Code |
| Dirk | The holistic research agent from the `ai-etcetera` repository; the first case study |
| Knowledge graph | A graph database (SQLite in Dirk) storing nodes and edges representing relationships |
| Porting | The process of reshaping a GitHub Copilot component into Claude Code compatible format |
| Skill | A Claude Code capability, typically documented in `.claude/skills/<name>/SKILL.md` |
| YAML frontmatter | YAML metadata block at the top of agent Markdown files specifying name, description, and tools |

---

## 16. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should the ported agents include Claude Code-specific tool permissions beyond `bash` and `read`? | Start with `bash`, `read`, `grep`, `glob`; expand as needed |
| 2 | How should the weekly scheduled GitHub Actions workflow be ported? | Document as a manual trigger pattern initially; explore cron/schedule skill as stretch goal |
| 3 | Should the Dirk case study include porting the Phase 3/4 stub implementations? | No — the stubs are Python CLI work, not agent prompt work |
| 4 | Should we keep `dirk.config.yml` settings unchanged or adapt them? | Keep unchanged — the config is consumed by the Python CLI |
