# Copilot-to-Claude Code Porting Framework

## 1. Overview

**Product Name:** Copilot-to-Claude Code Porting Framework

**Summary:** A reusable process and toolchain for porting frameworks, plugins, skills, and workflows built for GitHub Copilot into Claude Code compatible format. The framework defines a systematic approach for analyzing a source repository (prompts, Python/TypeScript tooling, CI workflows, configuration, bootstrap scripts) and reshaping each component into its Claude Code equivalent — agent markdown files, skills, workflow hooks, and project configuration. The first application of the framework is the **Dirk** holistic research agent (`ai-etcetera`).

**Target Platform:** Claude Code CLI (Linux, macOS, Windows via VS Code / JetBrains / standalone terminal)

**Key Constraints:**
- The source directory is provided interactively at the start of each project (no hardcoded paths)
- Ported components must follow existing Claude Code conventions (`.claude/agents/`, `.claude/skills/`, `CLAUDE.md`)
- The porting process is generative — it builds Claude Code-native artifacts rather than wrapping or shimming the original
- Original source repositories are treated as read-only inputs; no modifications are made upstream
- All porting work is executed by Claude Code agents using the Agent Forge system

---

## 2. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-24 | — | Initial PRD — approved by stakeholder |

---

## 3. Goals and Non-Goals

### 3.1 Goals

- Define a **repeatable, documented process** for analyzing a GitHub Copilot repository and mapping its components to Claude Code equivalents
- Produce a **mapping specification** that translates each Copilot concept (agent prompt, skill, workflow, config, bootstrap) to its Claude Code counterpart
- Deliver a **set of Claude Code agent definitions** (`.claude/agents/`) that encapsulate the ported functionality
- Create **bootstrap scripts and configuration** that allow the ported components to be installed, configured, and run within a Claude Code session
- Provide **documentation** at both the framework level (how to port any repo) and the project level (how to use the ported components)
- Run the **original test suite** to validate that the ported components function correctly
- Use the **Dirk** repository (`ai-etcetera`) as the first case study to validate and refine the framework

### 3.2 Non-Goals

- Maintaining a bidirectional sync with the original Copilot repository after porting (no live-upstream coupling)
- Building a generic "convert any Copilot extension" CLI tool — the framework is process-oriented, not a standalone converter binary
- Modifying or contributing back to the original Copilot repositories
- Supporting every Copilot extension type (focuses on the patterns found in the target repository: agent prompts, CLI tools, workflows, configs, bootstrap scripts)
- Reimplementing the Python runtime of Dirk in TypeScript or another language — the ported agents call the existing Python CLI through the bash tool

---

## 4. User Stories / Personas

### 4.1 Personas

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| Framework User | A developer who wants to port a Copilot repo to Claude Code format. Knows the source repo's structure and wants a guided process. | Clear steps, mapping reference, validated templates, working example to follow |
| End User | A Claude Code user who installs and runs the ported components. Wants a smooth setup and familiar interaction patterns. | `pip install -e .`, `dirk run --all` just works, clear CLAUDE.md instructions |
| Framework Maintainer | The developer evolving the porting framework itself across multiple source repos. | Abstracted patterns, reusable templates, feedback loop from each porting project |

### 4.2 User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| US-01 | Framework User | To provide a source repo path and have the framework analyze its structure | I understand what components exist and what needs porting | Must |
| US-02 | Framework User | To have a mapping of each Copilot component to its Claude Code equivalent | I know exactly what to create for each source artifact | Must |
| US-03 | Framework User | To generate Claude Code agent files from Copilot agent prompts | The ported agents work natively in Claude Code | Must |
| US-04 | End User | To run `dirk run --all` and get the same results as in Copilot | The ported functionality is correct | Must |
| US-05 | End User | To have clear bootstrap/installation instructions in CLAUDE.md | I can get started without reading external docs | Should |
| US-06 | Framework Maintainer | To reuse the porting process across multiple repos | I don't reinvent the mapping each time | Must |
| US-07 | Framework User | To validate ported components against the original test suite | I know the port is correct | Should |
| US-08 | End User | To configure Dirk via `dirk.config.yml` the same way as before | My existing config works unchanged | Must |
| US-09 | Framework User | To port CI/CD workflows (GitHub Actions) to Claude Code equivalents | Scheduled/responsive behaviors work in the Claude Code environment | Should |

---

## 5. Research Findings

### 5.1 Source Repository Analysis: Dirk / ai-etcetera

The Dirk repository implements a **holistic research agent** that scans GitHub repositories and produces a knowledge graph of connections between them. Key architectural observations:

**Component Inventory:**

| Component | Location | Purpose | Porting Target |
|-----------|----------|---------|----------------|
| Agent prompt | `.github/agents/dirk.md` | System prompt with operating loop, output contract, serendipity guidance | `.claude/agents/dirk.md` |
| Python CLI | `src/dirk/` (cli.py, agent.py, storage.py, config.py, writers.py) | Deterministic pipeline: inventory, dependency mapping, interface extraction, graph storage, report writing | Keep as-is; agents call via bash tool |
| Skills dir | `src/dirk/skills/` | Individual skill modules that the CLI orchestrates | `.claude/skills/` or keep as Python modules |
| Config schema | `dirk.config.yml` | YAML config for scope, depth, thresholds, output paths | Keep as-is (Compatible YAML) |
| Repo scope | `repos.yml` | List of repos to analyze | Keep as-is |
| CI workflow | `.github/workflows/dirk-scan.yml` | Scheduled weekly scan + PR creation | Port to Claude Code cron/hooks or manual run pattern |
| Tests | `tests/` | pytest suite | Run as-is for validation |
| Docs | `README.md`, `docs/PHASES.md` | Project and phase documentation | Reference in CLAUDE.md |
| Python project config | `pyproject.toml` | Build system, dependencies, entry point | Keep as-is |

**Key Architecture Patterns to Preserve:**
- **Agent-as-runtime principle**: Smart skills run inside the agent session; the Python CLI handles deterministic storage/scanning/reporting
- **Phase-based pipeline**: Phases 1–5 with clear data dependencies between them
- **CLI verbs as surface area**: The agent orchestrates by calling small CLI verbs (`dirk concept add`, `dirk link add`, etc.)

### 5.2 Claude Code Conventions

The target environment uses these conventions (from the existing `/opt/testing` project):

- **Agent files**: `.claude/agents/<name>.md` with YAML frontmatter (name, description, tools)
- **Skills**: `.claude/skills/<name>/SKILL.md` with process documentation
- **Agent Forge plugins**: `.claude/plugins/agent-forge/agents/` for multi-agent teams
- **Project config**: `CLAUDE.md` at repo root for project-level instructions
- **Workflow hooks**: Via `settings.json` hooks configuration (onRespond, onFileUpdate, etc.)
- **Scheduled tasks**: Via the `schedule` skill for recurring operations

### 5.3 Technology Currency Check

| Technology | Version in Repo | Latest Stable | Notes |
|-----------|-----------------|---------------|-------|
| Python | >=3.10 | 3.13 (Apr 2026) | Compatible; 3.10+ is fine |
| PyYAML | >=6.0 | 6.0.2 | Current |
| Click | >=8.1 | 8.1.8 | Current |
| SQLite | stdlib | N/A | No action needed |
| setuptools | >=68 | 75.x | Still compatible |
| pytest | >=7.4 | 8.x | Compatible |

No deprecation or EOL concerns. The Python stack is healthy.

### 5.4 Copilot-to-Claude Code Mapping Reference

| Copilot Concept | Claude Code Equivalent | Translation Notes |
|----------------|------------------------|-------------------|
| `.github/agents/<name>.md` | `.claude/agents/<name>.md` | Add YAML frontmatter; adjust tool permissions; same Markdown body structure |
| GitHub Actions workflow | `settings.json` hooks + cron/schedule skill | Map triggers (schedule, push) to Claude Code equivalents; manual triggers remain manual |
| Copilot skills/extensions | `.claude/skills/<name>/SKILL.md` | Document as skill files with process steps; agent invokes via Skill tool |
| `pyproject.toml` / Python package | Keep as-is | No translation needed; agents call via bash |
| CLI entry points (`dirk <verb>`) | Keep as-is | Agents invoke via bash tool in agent definitions |
| YAML config files | Keep as-is | Compatible format |
| `README.md` project docs | `CLAUDE.md` + reference original README | CLAUDE.md gets project instructions; README.md kept for human readers |
| Bootstrap scripts | `script/setup` or documented in CLAUDE.md | Adapt to Claude Code setup conventions |
| Test suite (`pytest`) | Keep as-is | Run via bash for validation; no translation needed |

---

## 6. Concept

### 6.1 Core Workflow

The porting framework operates as a multi-phase process executed by a Claude Code session:

```
┌───────────────────────────────────────────────────┐
│              Porting Framework                     │
├───────────────────────────────────────────────────┤
│                                                    │
│  Phase 1: Analyze Source Repository                │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Read source directory structure          │   │
│  │ 2. Catalog components by type               │   │
│  │    (agents, workflows, configs, tests, CLI) │   │
│  │ 3. Generate Component Inventory             │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│                         ▼                           │
│  Phase 2: Map to Claude Code Format                │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Apply mapping reference per component    │   │
│  │ 2. Identify keep-as-is vs. translate        │   │
│  │ 3. Produce porting plan (ordered tasks)     │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│                         ▼                           │
│  Phase 3: Generate Claude Code Artifacts            │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Create .claude/agents/<name>.md          │   │
│  │ 2. Create .claude/skills/ as needed         │   │
│  │ 3. Create / update CLAUDE.md                │   │
│  │ 4. Create bootstrap / setup scripts         │   │
│  │ 5. Port workflow triggers to hooks / cron   │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│                         ▼                           │
│  Phase 4: Validate                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Install dependencies (pip install -e .)  │   │
│  │ 2. Run original test suite (pytest)         │   │
│  │ 3. Verify agents are invokeable             │   │
│  │ 4. Dry-run: agent loads, calls CLI, checks  │   │
│  └─────────────────────────────────────────────┘   │
│                         │                           │
│                         ▼                           │
│  Phase 5: Document                                  │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. Write/update CLAUDE.md instructions      │   │
│  │ 2. Document porting decisions               │   │
│  │ 3. Note any gaps or limitations             │   │
│  └─────────────────────────────────────────────┘   │
│                                                    │
└───────────────────────────────────────────────────┘
```

### 6.2 Success / Completion Criteria

- All components from the source inventory have been ported, kept-as-is, or explicitly noted as out of scope
- Claude Code agent files exist and load without errors
- The original test suite passes in the Claude Code environment
- CLAUDE.md contains clear instructions for using the ported components
- A dry-run execution confirms the ported workflow produces the expected output
- The process is documented well enough that a second developer (or the same developer a month later) could port a different Copilot repo using the same framework

---

## 7. Technical Architecture

### 7.1 Technology Stack

| Component | Technology | Version Notes |
|-----------|-----------|---------------|
| Target runtime | Claude Code CLI | Uses Claude Opus 4.7 / Sonnet 4.6 agents |
| Agent format | Markdown + YAML frontmatter | `.claude/agents/*.md` |
| Skill format | Markdown | `.claude/skills/*/SKILL.md` |
| Agent Forge | Plugin system | `.claude/plugins/agent-forge/` |
| Source language | Python 3.10+ | Keep as-is |
| Build system | setuptools / pyproject.toml | Keep as-is |
| Testing | pytest 7+ | Keep as-is |
| Sourcing | Interactive prompt | User provides source dir at start of each project |

### 7.2 Project Structure (After Porting)

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
│   └── copilot-to-claude-code-porting-framework.md  # This PRD
├── config.yaml                          # LiteLLM config (existing)
├── CLAUDE.md                            # Project instructions
└── .env                                 # Environment variables
```

### 7.3 Key APIs / Interfaces

| Interface | Location | Purpose |
|-----------|----------|---------|
| Dirk CLI | `repos/ai-etcetera/src/dirk/cli.py` | CLI entry point: `dirk init`, `dirk scan`, `dirk run --all`, etc. |
| Config loader | `repos/ai-etcetera/src/dirk/config.py` | Reads `dirk.config.yml` |
| Graph storage | `repos/ai-etcetera/src/dirk/storage.py` | SQLite read/write for knowledge graph |
| Agent definition | `.claude/agents/dirk.md` | Claude Code agent that orchestrates Dirk |
| Agent invocation | `claude` CLI | `claude` with agent flag to invoke the Dirk agent |

---

## 8. Functional Requirements

### 8.1 Porting Framework

| ID | Requirement | Priority |
|----|-------------|----------|
| PF-01 | Framework shall accept a source directory path via interactive prompt at project start | Must |
| PF-02 | Framework shall analyze the source directory structure and produce a component inventory | Must |
| PF-03 | Framework shall classify each component by type (agent prompt, workflow, config, CLI tool, test, docs, bootstrap) | Must |
| PF-04 | Framework shall apply the Copilot-to-Claude Code mapping reference to each component | Must |
| PF-05 | Framework shall produce a porting plan listing all artifacts to create or modify | Must |
| PF-06 | Framework shall generate Claude Code agent files (`.claude/agents/*.md`) from Copilot agent prompts | Must |
| PF-07 | Framework shall create/update `CLAUDE.md` with project instructions | Should |
| PF-08 | Framework shall port CI workflows (GitHub Actions) to Claude Code equivalents (hooks, cron, or manual patterns) | Should |
| PF-09 | Framework shall create bootstrap/setup scripts following Claude Code conventions | Should |
| PF-10 | Framework shall validate ported components by running the original test suite | Must |
| PF-11 | Framework shall document all porting decisions and any gaps/limitations | Should |

### 8.2 Dirk Case Study

| ID | Requirement | Priority |
|----|-------------|----------|
| DK-01 | Dirk agent prompt from `.github/agents/dirk.md` shall be ported to `.claude/agents/dirk.md` with YAML frontmatter | Must |
| DK-02 | Ported Dirk agent shall include `bash` and `read` tools in its frontmatter to invoke the Python CLI and read files | Must |
| DK-03 | Ported Dirk agent shall reference the original `dirk.config.yml` and `repos.yml` for configuration | Must |
| DK-04 | Ported Dirk agent shall invoke `dirk run --all` via bash tool to execute the pipeline | Must |
| DK-05 | Python dependencies shall be installable via `pip install -e "repos/ai-etcetera[dev]"` | Must |
| DK-06 | The original pytest suite shall pass when run from the Claude Code environment | Should |
| DK-07 | A dry-run of the ported Dirk agent shall produce the same knowledge graph and findings as running `dirk run --all` directly | Should |
| DK-08 | CLI verb examples from the original agent prompt (`dirk concept add`, `dirk link add`) shall remain accessible | Should |

---

## 9. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NF-01 | Porting process for a new repo shall complete within a single Claude Code session (no multi-session handoffs) | Must |
| NF-02 | Ported agents shall load without YAML frontmatter or Markdown parsing errors | Must |
| NF-03 | Ported components shall not modify the original source repository (read-only access) | Must |
| NF-04 | CLAUDE.md shall be kept concise (under 50 lines of instructions) | Should |
| NF-05 | Agent definitions shall use a single `tools:` list with only the minimum tools needed | Should |
| NF-06 | Porting process shall be repeatable — running the framework on the same source repo twice produces the same output | Should |

---

## 10. Security and Privacy

| ID | Requirement | Priority |
|----|-------------|----------|
| SP-01 | Source repository is treated as read-only; no writes, no modifications | Must |
| SP-02 | All porting work occurs within the local Claude Code session; no external data transmission | Must |
| SP-03 | If the source repo contains `.env` files or secrets, they must be excluded from porting and explicitly noted | Must |
| SP-04 | Ported agent definitions must not embed API keys, tokens, or credentials | Must |
| SP-05 | Agent tool permissions (bash, read, edit, etc.) should be scoped to the minimum required | Should |

---

## 11. Accessibility

| ID | Requirement | Priority |
|----|-------------|----------|
| ACC-01 | Documentation shall use clear Markdown formatting compatible with terminal rendering | Should |
| ACC-02 | CLAUDE.md shall use plain language and avoid ambiguous jargon | Should |
| ACC-03 | Agent descriptions in YAML frontmatter shall be self-explanatory (one-line summary of what the agent does) | Should |

---

## 12. User Interface / Interaction Design

The primary interface is the **Claude Code CLI session**. The porting workflow is agent-driven:

1. **User invocation**: User runs a Claude Code agent or series of agents that execute the porting phases
2. **Interactive source prompt**: Agent asks the user for the source directory path
3. **Progress feedback**: Agent reports each phase as it completes (analysis, mapping, generation, validation, documentation)
4. **Validation results**: Agent presents test results and any issues found
5. **Completion summary**: Agent outputs a summary of what was ported, what was kept, and any open items

No GUI or web interface is required. All interaction is through the Claude Code chat interface.

---

## 13. System States / Lifecycle

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
| ANALYZING | Scanning source directory, building component inventory | → MAPPING (inventory complete) or → FAILED (unreadable source) |
| MAPPING | Classifying components, applying mapping reference | → GENERATING (mapping complete) |
| GENERATING | Writing Claude Code artifacts (agents, skills, CLAUDE.md) | → VALIDATING (artifacts written) |
| VALIDATING | Running tests, verifying agent loads | → DOCUMENTING (validated) or → FAILED (tests fail) |
| DOCUMENTING | Writing final docs, porting decisions, open items | → COMPLETE (documentation done) |
| COMPLETE | All phases finished successfully | (terminal) |
| FAILED | Error at any phase | Requires re-entry or manual fix |

---

## 14. Implementation Phases

### Phase 1: Framework Definition
- [ ] Draft and finalize this PRD
- [ ] Define the component inventory template (what to capture for each source repo)
- [ ] Define the porting plan template (ordered checklist of artifacts to create)
- [ ] Document the Copilot-to-Claude Code mapping reference
- [ ] Generate the framework agents (Analyzer, Mapper, Generator, Validator) via Agent Forge

### Phase 2: Dirk Case Study — Analysis & Mapping
- [ ] Analyze the Dirk repository structure (already done in this PRD)
- [ ] Run component inventory against Dirk
- [ ] Produce Dirk-specific porting plan
- [ ] Confirm plan with user

### Phase 3: Dirk Case Study — Generation
- [ ] Create `.claude/agents/dirk.md` with YAML frontmatter (tools: bash, read, grep, glob)
- [ ] Create/update `CLAUDE.md` with Dirk project instructions (setup, configuration, usage)
- [ ] Port CI workflow (`.github/workflows/dirk-scan.yml`) to Claude Code schedule/cron or manual pattern
- [ ] Create any needed bootstrap/setup scripts
- [ ] Verify Python dependencies install correctly (`pip install -e "repos/ai-etcetera[github,dev]"`)

### Phase 4: Dirk Case Study — Validation
- [ ] Run `pytest` from the Dirk test suite
- [ ] Verify Dirk agent loads in Claude Code (`claude` with agent flag)
- [ ] Dry-run `dirk run --all` (or `dirk scan`) to confirm CLI works
- [ ] Fix any issues found during validation

### Phase 5: Framework Generalization
- [ ] Document learnings from Dirk case study
- [ ] Refine mapping reference with any edge cases encountered
- [ ] Update framework documentation
- [ ] Identify next candidate repository for porting

---

## 15. Testing Strategy

| Level | Scope | Tools / Approach |
|-------|-------|------------------|
| Unit Tests | Dirk Python CLI (source repo) | pytest — run as-is from source |
| Integration | Agent invocation → CLI calls | Manual verify: agent loads, executes `dirk scan`, produces graph output |
| Validation | Porting process | Run full framework on Dirk twice; verify idempotent output |
| Dry-run | End-to-end | Execute `dirk run --all` from within Claude Code session |
| Agent load | Agent file syntax | Attempt to load agent; catch YAML/Markdown errors |

**Key Test Scenarios:**

1. Source directory is readable and contains the expected structure
2. Component inventory accurately identifies all component types
3. Dirk agent YAML frontmatter is valid (name, description, tools)
4. `pip install -e "repos/ai-etcetera[dev]"` completes without error
5. `pytest` passes (all tests green)
6. `dirk scan --help` prints CLI help
7. Agent file loads without syntax errors when invoked

---

## 16. Analytics / Success Metrics

No telemetry is planned. Success will be evaluated by:

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Components ported | 100% of identified items | Component inventory checklist |
| Test suite pass rate | 100% | pytest exit code |
| Agent load success | All agents load without errors | Claude Code agent invocation |
| Dry-run output | Graph/findings generated same as direct CLI | Compare output files |
| Time to port a repo | Under 2 Claude Code sessions | Session tracking |

---

## 17. Acceptance Criteria

1. Porting framework document exists and describes a repeatable process
2. Component inventory template is defined and usable
3. Copilot-to-Claude Code mapping reference is documented
4. Dirk agent is ported to `.claude/agents/dirk.md` with valid YAML frontmatter
5. CLAUDE.md contains clear instructions for setting up and using Dirk
6. Python dependencies install successfully
7. Original pytest suite passes
8. A dry-run execution of Dirk produces the expected knowledge graph output
9. The porting process can be repeated for a different Copilot repository without modifying the framework

---

## 18. Dependencies and Risks

### 18.1 Dependencies

| Dependency | Type | Risk if Unavailable | Mitigation |
|------------|------|---------------------|------------|
| Source repository (ai-etcetera) | Local filesystem | Cannot analyze or port | Must have source checked out before starting |
| Python 3.10+ | Runtime | Dirk CLI won't run | Verify Python version early in process |
| Claude Code CLI | Runtime | Cannot create or use agents | Framework is documentation-only without it |
| pip / setuptools | Build | Cannot install Dirk deps | Include in system requirements check |
| Network (for GitHub Actions workflow) | Service | Cannot validate CI porting | CI porting is "Should" priority; manual pattern is fallback |

### 18.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Source repo has complex or unsupported component types not covered by the mapping reference | Medium | Medium | Framework is extensible; add new mapping entries as encountered |
| Python version conflicts between source repo and Claude Code environment | Low | Medium | Use `pyproject.toml` requires-python to validate compatibility early |
| Agent prompt references Copilot-specific features not available in Claude Code (e.g., Copilot CLI verbs, Copilot-specific MCP tools) | Medium | High | Identify during analysis phase; replace with Claude Code equivalents or note as gaps |
| Source repo contains large binary files or generated artifacts that slow down analysis | Low | Low | Exclude common binary/generated dirs from analysis scope |
| Ported components drift from upstream improvements | Medium | Low | Not a bidirectional sync; port is a point-in-time capture |

---

## 19. Future Considerations

| Item | Description | Potential Version |
|------|-------------|-------------------|
| Automated porting CLI | Build a standalone Python CLI tool that automates the analysis, mapping, and generation phases | v2 |
| Multi-repo batch porting | Port multiple Copilot repos in a single session using the same framework | v2 |
| Bidirectional sync hooks | Optional mechanism to detect upstream changes in the source repo and flag them | v3 |
| Community template library | Share porting templates for common Copilot patterns (agents, skills, MCP servers) | v3 |
| Copilot MCP server support | Handle repos that define MCP (Model Context Protocol) servers and translate them | v2 |

---

## 20. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should the ported agents include Claude Code-specific tool permissions beyond `bash` and `read`? | Start with `bash`, `read`, `grep`, `glob`; expand as needed per agent role |
| 2 | How should the weekly scheduled GitHub Actions workflow be ported? | Document as a manual trigger pattern initially; explore Claude Code cron/schedule skill as stretch goal |
| 3 | Should the Dirk case study include porting the Phase 3/4 stub implementations? | No — the stubs are Python CLI work, not agent prompt work. Port the existing agent prompt and CLI surface; Phase 3/4 will be implemented when ready |
| 4 | Should we keep `dirk.config.yml` settings unchanged or adapt them to Claude Code conventions? | Keep unchanged — the config is consumed by the Python CLI, not by Claude Code |

---

## 21. Glossary

| Term | Definition |
|------|------------|
| Agent Forge | Claude Code plugin system for building multi-agent teams using agent definition files |
| CLAUDE.md | Project-level configuration file that provides instructions to Claude Code |
| Dirk | The holistic research agent from the `ai-etcetera` repository; the first case study for this framework |
| Knowledge graph | A graph database (SQLite in Dirk) storing nodes (repos, concepts, technologies) and edges (relationships) |
| Porting | The process of reshaping a GitHub Copilot component into Claude Code compatible format |
| Skill | A Claude Code capability, typically documented in `.claude/skills/<name>/SKILL.md` |
| YAML frontmatter | YAML metadata block at the top of agent Markdown files specifying name, description, and tools |
