# Porting Plan: Dirk / ai-etcetera

**Source path:** `repos/ai-etcetera/`
**Derived from inventory:** `docs/templates/component-inventory.md` (completed example)
**Date:** 2026-04-24

---

## Phase 1: Foundation (COMPLETE)

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 1.1 | Draft and finalize the PRD | project-orchestrator | — | — | None | Large |
| 1.2 | Decompose into Product Vision + Features | project-orchestrator | — | — | 1.1 | Large |
| 1.3 | Define component inventory template | porting-architect | — | FOUND-FR-02, FOUND-FR-03 | 1.2 | Small |
| 1.4 | Define porting plan template | porting-architect | — | FOUND-FR-05 | 1.3 | Small |
| 1.5 | Document Copilot-to-Claude Code mapping | porting-architect | — | FOUND-FR-04 | 1.2 | Medium |
| 1.6 | Generate framework agents | forge-team-builder | — | Foundation AC #4 | 1.2 | Medium |

**Status:** Tasks 1.1, 1.2, 1.5, 1.6 complete. Tasks 1.3, 1.4 complete now.

---

## Phase 2: Dirk Agent Port

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 2.1 | Read original agent prompt | dirk-agent-engineer | `.github/agents/dirk.md` | DIRK-FR-01 | 1.x | Small |
| 2.2 | Create `.claude/agents/dirk.md` with YAML frontmatter | dirk-agent-engineer | `.github/agents/dirk.md` → `.claude/agents/dirk.md` | DIRK-FR-01 | 2.1 | Medium |
| 2.3 | Validate agent frontmatter & paths | dirk-agent-engineer | `.claude/agents/dirk.md` | DIRK-FR-01, DIRK-FR-02, DIRK-FR-03 | 2.2 | Small |

---

## Phase 3: Bootstrap & Setup

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 3.1 | Install Python dependencies | setup-engineer | `pyproject.toml`, `src/dirk/` | SETUP-FR-01 | 2.x | Small |
| 3.2 | Verify CLI & test discovery | setup-engineer | `dirk` CLI, `tests/` | SETUP-FR-01 | 3.1 | Small |
| 3.3 | Create/update CLAUDE.md with setup instructions | setup-engineer | `CLAUDE.md` | SETUP-FR-02 | 3.2 | Medium |

---

## Phase 4: Workflow Porting

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 4.1 | Analyze original workflow | workflow-engineer | `.github/workflows/dirk-scan.yml` | WF-FR-01 | 1.x | Small |
| 4.2 | Document manual run pattern in CLAUDE.md | workflow-engineer | `CLAUDE.md` | WF-FR-01 | 4.1 | Small |

---

## Phase 5: Validation & Testing

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 5.1 | Run pytest suite | qa-engineer | `tests/` | VAL-FR-01, VAL-FR-03 | 2.x, 3.x | Medium |
| 5.2 | Validate agent YAML frontmatter | qa-engineer | `.claude/agents/dirk.md` | VAL-FR-03 | 2.x | Small |
| 5.3 | Execute dry-run (`dirk scan`) | qa-engineer | `src/dirk/` | VAL-FR-02 | 3.x | Medium |
| 5.4 | Produce validation summary | qa-engineer | — | VAL-FR-03 | 5.1, 5.2, 5.3 | Small |

---

## Dependency Summary

```
Phase 1 (Foundation) — Complete
  │
  ├──→ Phase 2 (Dirk Agent Port) — Ready to start
  │     │
  │     ├──→ Phase 3 (Bootstrap & Setup) — Awaiting Phase 2
  │     │
  │     └──→ Phase 5 (Validation & Testing) — Awaiting Phase 2 + 3
  │
  └──→ Phase 4 (Workflow Porting) — Can start alongside Phase 2 (parallel)
```

## Current State

- **Phase 1:** Complete (all 6 tasks done)
- **Phase 2:** Pending — ready to execute
- **Phase 3:** Pending — needs Phase 2 first
- **Phase 4:** Pending — can run in parallel with Phase 2
- **Phase 5:** Pending — needs Phase 2 and Phase 3
