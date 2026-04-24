# Feature: Bootstrap & Setup

## Traceability

| Feature ID | Original PRD ID | Description |
|-----------|----------------|-------------|
| SETUP-US-01 | US-05 | Have clear bootstrap/installation instructions in CLAUDE.md |
| SETUP-FR-01 | DK-05 | Python dependencies installable via pip install |
| SETUP-FR-02 | PF-07 | Create/update CLAUDE.md with project instructions |
| SETUP-FR-03 | PF-09 | Create bootstrap/setup scripts following Claude Code conventions |

**Product Vision:** [docs/product-vision.md](../product-vision.md)
**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](../copilot-to-claude-code-porting-framework.md)

---

## 1. Feature Overview

**Feature Name:** Bootstrap & Setup
**ID Prefix:** SETUP
**Summary:** The installation experience and project documentation that allows an End User to set up and run the ported Dirk components. This includes CLAUDE.md instructions, dependency installation, and bootstrap scripts.
**Dependencies:** Dirk Agent Port (needs the agent to reference in setup instructions)
**Priority:** Should

---

## 2. User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| SETUP-US-01 | End User | To have clear bootstrap/installation instructions in CLAUDE.md | I can get started without reading external docs | Should |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| SETUP-FR-01 | Python dependencies shall be installable via `pip install -e "repos/ai-etcetera[dev]"` | Must |
| SETUP-FR-02 | Framework shall create/update `CLAUDE.md` with project instructions including setup, configuration, and usage | Should |
| SETUP-FR-03 | Framework shall create bootstrap/setup scripts following Claude Code conventions | Should |

---

## 4. UI / Interaction Design

The setup experience is:

1. User reads `CLAUDE.md` for project instructions
2. User runs `pip install -e "repos/ai-etcetera[dev]"` to install dependencies
3. User configures via `dirk.config.yml` and `repos.yml`
4. User invokes the Dirk agent or runs `dirk run --all` directly

CLAUDE.md structure:

```markdown
# testing

## Dirk — Holistic Research Agent

The Dirk source lives in `repos/ai-etcetera/`. To use it:

### Setup
pip install -e "repos/ai-etcetera[github,dev]"

### Configuration
Edit repos/ai-etcetera/dirk.config.yml and repos/ai-etcetera/repos.yml

### Run
Invoke the Dirk agent, or run directly: dirk run --all

### Test
cd repos/ai-etcetera && pytest
```

---

## 5. Implementation Tasks

### Phase 1: Installation
- [ ] Install Python dependencies: `pip install -e "repos/ai-etcetera[github,dev]"`
- [ ] Verify `dirk` CLI is available: `dirk --help`
- [ ] Verify pytest can discover tests: `cd repos/ai-etcetera && pytest --collect-only`

### Phase 2: Documentation
- [ ] Create/update `CLAUDE.md` with Dirk setup instructions
- [ ] Document how to configure (config.yml, repos.yml)
- [ ] Document how to invoke the Dirk agent
- [ ] Document how to run tests
- [ ] Create any bootstrap scripts needed (`script/setup` or similar)

---

## 6. Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Installation | Python environment | `pip install` completes without error |
| CLI | Entry point | `dirk --help` prints help and exits 0 |
| Test discovery | Test suite | `pytest --collect-only` discovers all tests |
| Documentation | CLAUDE.md | Instructions are accurate and actionable |

Key test scenarios:
1. `pip install -e "repos/ai-etcetera[dev]"` completes without error
2. `dirk --help` prints CLI help and exits with code 0
3. `dirk scan --help` prints scan-specific help
4. CLAUDE.md instructions can be followed without external references

---

## 7. Acceptance Criteria

1. Python dependencies install successfully via `pip install`
2. `dirk` CLI is available as a shell command
3. CLAUDE.md contains clear instructions for setup, configuration, usage, and testing
4. Bootstrap scripts exist (if needed) and are documented
5. A user new to the project can set up and run Dirk by following CLAUDE.md alone

---

## 8. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should bootstrap scripts be shell scripts or documented steps in CLAUDE.md? | Documented steps in CLAUDE.md initially; add shell scripts if setup becomes multi-step |
