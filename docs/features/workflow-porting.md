# Feature: Workflow Porting

## Traceability

| Feature ID | Original PRD ID | Description |
|-----------|----------------|-------------|
| WF-US-01 | US-09 | Port CI/CD workflows to Claude Code equivalents |
| WF-FR-01 | PF-08 | Port CI workflows to Claude Code equivalents |

**Product Vision:** [docs/product-vision.md](../product-vision.md)
**Original PRD:** [docs/copilot-to-claude-code-porting-framework.md](../copilot-to-claude-code-porting-framework.md)

---

## 1. Feature Overview

**Feature Name:** Workflow Porting
**ID Prefix:** WF
**Summary:** Port the GitHub Actions CI/CD workflow (`.github/workflows/dirk-scan.yml`) to a Claude Code equivalent. The original workflow runs a weekly scheduled scan of the Dirk pipeline and opens a PR with updated findings. The ported version should provide equivalent functionality within the Claude Code environment.
**Dependencies:** Foundation (needs workflow mapping from the mapping reference)
**Priority:** Should

---

## 2. User Stories

| ID | As a... | I want to... | So that... | Priority |
|----|---------|-------------|-----------|----------|
| WF-US-01 | Framework User | To port CI/CD workflows (GitHub Actions) to Claude Code equivalents | Scheduled/responsive behaviors work in the Claude Code environment | Should |

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| WF-FR-01 | Framework shall port CI workflows (GitHub Actions) to Claude Code equivalents (hooks, cron, or manual patterns) | Should |

---

## 4. UI / Interaction Design

The ported workflow takes one of three forms:

**Option A: Manual trigger pattern (default)**
The workflow is documented in CLAUDE.md as a set of commands the user runs on demand. The equivalent of the weekly scan is a documented manual invocation.

**Option B: Claude Code cron/schedule skill**
The Claude Code `schedule` skill can run recurring tasks. The weekly scan becomes a scheduled prompt that invokes the Dirk agent.

**Option C: settings.json hooks**
Workflow triggers (on push, on schedule) can be mapped to Claude Code hooks (onRespond, onFileUpdate) in `settings.json`.

Original workflow structure (`.github/workflows/dirk-scan.yml`):

| Trigger | Action |
|---------|--------|
| `schedule: cron "0 6 * * 1"` | Checkout + Python setup + pip install + `dirk run --all` + detect changes + open PR |
| `workflow_dispatch` | Same, with optional depth override |

Claude Code equivalents:

| Trigger | Claude Code Mechanism |
|---------|----------------------|
| Scheduled (weekly) | Manual invocation via documented command; optionally `schedule` skill |
| On-demand | Manual invocation |
| Change detection | Run `dirk run --all`, check `git status` on graph/findings |
| PR creation | Documented as manual step; not automated in Claude Code terminal |

---

## 5. Implementation Tasks

### Phase 1: Analyze the Workflow
- [ ] Read `.github/workflows/dirk-scan.yml` from the source repo
- [ ] Catalog all triggers, steps, and actions
- [ ] Identify which have Claude Code equivalents

### Phase 2: Port
- [ ] Document the manual run pattern in CLAUDE.md
- [ ] If using `schedule` skill: set up scheduled Dirk agent invocations
- [ ] If using hooks: configure `settings.json` with appropriate hooks
- [ ] Document how to detect and review changes (equivalent of the PR workflow)

---

## 6. Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Manual run | Full pipeline | Execute `dirk run --all` and verify output is generated |
| Change detection | Graph/findings | Verify new output files are produced in the expected directories |

Key test scenarios:
1. `dirk run --all` completes successfully and produces graph output
2. Graph output files (`graph/graph.db`, `graph/graph.json`) are created
3. Findings files (`findings/*.md`) are created
4. If using schedule skill: scheduled invocation runs the Dirk agent on the configured cadence

---

## 7. Acceptance Criteria

1. Workflow is documented as a manual run pattern in CLAUDE.md
2. `dirk run --all` can be invoked from the Claude Code session
3. Output (graph + findings) is generated and reviewable
4. If schedule skill is configured: scheduled runs execute automatically

---

## 8. Open Questions

| # | Question | Default Assumption |
|---|----------|--------------------|
| 1 | Which mechanism to use for scheduled execution? | Default to manual pattern (documented in CLAUDE.md); explore `schedule` skill as a stretch goal |
| 2 | Should we port the PR creation step? | No — PR creation is GitHub-specific. The ported workflow generates output; the user reviews it manually or via `git diff` in the Claude Code session |
