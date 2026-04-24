# Feature: Validation & Testing

## Traceability

| Feature ID | Original PRD ID | Description |
|-----------|----------------|-------------|
| VAL-US-01 | US-07 | Validate ported components against the original test suite |
| VAL-FR-01 | DK-06 | Original pytest suite passes when run from Claude Code environment |
| VAL-FR-02 | DK-07 | Dry-run produces same knowledge graph as direct CLI invocation |
| VAL-FR-03 | PF-10 | Framework shall validate ported components by running the original test suite |

**Product Vision:** [docs/product-vision.md](../product-vision.md)
**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](../copilot-to-claude-code-porting-framework.md)

---

## 1. Feature Overview

**Feature Name:** Validation & Testing
**ID Prefix:** VAL
**Summary:** End-to-end validation that the ported components work correctly. This includes running the original test suite, verifying agent loads, and executing a dry-run of the complete pipeline to confirm the output matches expectations.
**Dependencies:** Dirk Agent Port (agent must exist), Bootstrap & Setup (dependencies must be installed)
**Priority:** Should

---

## 2. User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| VAL-US-01 | Framework User | To validate ported components against the original test suite | I know the port is correct | Should |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| VAL-FR-01 | The original pytest suite shall pass when run from the Claude Code environment | Should |
| VAL-FR-02 | A dry-run of the ported Dirk agent shall produce the same knowledge graph and findings as running `dirk run --all` directly | Should |
| VAL-FR-03 | Framework shall validate ported components by running the original test suite | Must |

---

## 4. UI / Interaction Design

Validation is executed by the porting agent as a verification step:

1. **Test suite**: Agent runs `cd repos/ai-etcetera && pytest` and reports results
2. **Agent load**: Agent attempts to load itself (or validates via tool) and confirms no syntax errors
3. **Dry-run**: Agent runs `dirk run --all` (or a subset like `dirk scan`), checks exit code, and verifies output files exist
4. **Report**: Agent presents a validation summary to the user

Validation output format:

```
## Validation Results

### Test Suite: PASS
  - 12 passed, 0 failed, 0 skipped
  - Completed in 2.3s

### Agent Load: PASS
  - dirk.md: valid YAML frontmatter, all tools recognized

### Dry Run: PASS
  - dirk scan: exit 0
  - Output: graph/graph.db, graph/graph.json created
  - Findings: findings/*.md created
```

---

## 5. Implementation Tasks

### Phase 1: Run Test Suite
- [ ] Install dev dependencies: `pip install -e "repos/ai-etcetera[dev]"`
- [ ] Run `cd repos/ai-etcetera && pytest -v` and capture results
- [ ] Investigate and fix any test failures

### Phase 2: Verify Agent
- [ ] Verify `.claude/agents/dirk.md` has valid YAML frontmatter
- [ ] Verify agent file references exist (config files, scripts)
- [ ] Attempt to load agent (validation via Claude Code mechanisms)

### Phase 3: Dry-Run
- [ ] Run `dirk scan` (Phase 1 skills — deterministic, no agent reasoning needed)
- [ ] Or run `dirk run --all` if full pipeline is desired
- [ ] Verify exit code is 0
- [ ] Verify output files exist in `graph/` and `findings/` directories

---

## 6. Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Unit Tests | Dirk Python CLI | pytest — run as-is from source |
| Integration | Agent invocation → CLI calls | Manual verify: agent loads, executes `dirk scan`, produces output |
| Validation | Porting process | Run full process on Dirk; verify idempotent output |
| Dry-run | End-to-end | Execute `dirk run --all` from within Claude Code session |
| Agent load | Agent file syntax | Validate YAML frontmatter; check for parse errors |

Key test scenarios:
1. `pytest` passes (all tests green)
2. `dirk scan --help` prints CLI help
3. `dirk scan` produces graph output files
4. Agent file loads without syntax errors when invoked
5. YAML frontmatter has all required fields (name, description, tools)

---

## 7. Acceptance Criteria

1. Original pytest suite passes with no failures
2. `.claude/agents/dirk.md` has valid YAML frontmatter
3. `dirk scan` (or `dirk run --all`) completes with exit code 0
4. Knowledge graph output files are created (`graph/graph.db`, `graph/graph.json`)
5. Findings output files are created (`findings/*.md`)
6. Validation summary can be produced and reviewed

---

## 8. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Should dry-run execute the full pipeline (`dirk run --all`) or just Phase 1 (`dirk scan`)? | Start with `dirk scan` (Phase 1 — deterministic). Full pipeline requires configured repos |
| 2 | What if the test suite requires network access (e.g., `[github]` extras)? | Install with `[github,dev]` extras; document network dependency |
