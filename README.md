# Copilot-to-Claude Code Porting Framework

A reusable framework and automated CLI tool for porting frameworks, plugins, skills, and workflows built for GitHub Copilot into Claude Code compatible format.

## What it does

Given a GitHub Copilot repository as input, this project:

1. **Analyzes** the source structure and classifies components (agent prompts, workflows, configs, CLI tools, test suites, docs, etc.)
2. **Maps** each Copilot component to its Claude Code equivalent using a defined mapping reference
3. **Generates** Claude Code-native artifacts (`.claude/agents/`, skills, `CLAUDE.md`, workflow docs)
4. **Validates** the ported artifacts by checking frontmatter syntax, file references, and running the original test suite

## Quick start

### Install the Port CLI

```bash
pip install -e src/port
```

### Port a repository

```bash
port init --source /path/to/copilot-repo --output ./output
port generate --plan ./output/porting-plan.yml --output ./output
port validate --generated ./output/generated
```

Or run the full pipeline in one command:

```bash
port run --all --source /path/to/copilot-repo --output ./output
```

### Port CLI commands

| Command | Description |
|---------|-------------|
| `port init --source REPO` | Scan source repo, classify components, generate inventory + porting plan |
| `port scan` | Re-scan source and diff against existing inventory |
| `port generate --plan PLAN` | Generate Claude Code artifacts (agent files, CLAUDE.md, workflow docs) |
| `port validate --generated DIR` | Validate generated frontmatter, paths, and optionally run tests |
| `port run --all --source REPO` | Full pipeline: init → generate → validate |

## The porting framework

Beyond the CLI, this repository defines a **repeatable process** for porting any Copilot repository. The framework includes:

- **Component inventory template** — categorize source components into 10 types (agent_prompt, workflow, config, cli_tool, test_suite, documentation, bootstrap, source_library, skill_module, unknown)
- **Copilot-to-Claude Code mapping reference** — maps each Copilot concept to its Claude Code equivalent
- **Porting plan template** — 5-phase execution plan with dependency tracking
- **Agent team** — specialist Claude Code agents for each phase (porting-architect, dirk-agent-engineer, setup-engineer, workflow-engineer, qa-engineer)

## Case study: Dirk / ai-etcetera

The first application of the framework was porting **Dirk** — a holistic research agent that scans GitHub repositories and produces a knowledge graph of connections between them.

What was ported:
- Agent prompt → `.claude/agents/dirk.md` with YAML frontmatter and Claude Code-compatible tools
- GitHub Actions workflow → documented manual run pattern in CLAUDE.md
- Python CLI, config, and test suite kept as-is (invoked via Claude Code bash tool)

## Project structure

```
.
├── .claude/
│   ├── agents/                     # Ported Dirk + forge agents
│   └── plugins/agent-forge/agents/ # Specialist porting agents
├── docs/
│   ├── product-vision.md           # Cross-cutting architecture & mapping
│   ├── features/                   # Feature documents
│   ├── templates/                  # Reusable inventory & plan templates
│   └── porting-plan-dirk.md        # Filled-in Dirk case study plan
├── src/port/
│   ├── pyproject.toml              # Port CLI build config
│   └── port/
│       ├── cli.py                  # 5 CLI commands
│       ├── scanner.py              # Component classifier
│       ├── mapper.py               # Copilot→Claude Code mapping
│       ├── inventory.py            # Inventory model
│       ├── planner.py              # Plan generator
│       ├── generator/              # Artifact generators
│       ├── validator.py            # Validation checks
│       └── writer.py               # File output helpers
└── repos/ai-etcetera/              # Dirk source repository
```

## Development

### Set up

```bash
pip install -e "src/port[dev]"
```

### Run tests

```bash
cd src/port && pytest
```

## License

See [LICENSE](LICENSE).
