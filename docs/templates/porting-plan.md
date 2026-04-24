# Porting Plan Template

## Overview

Use this template to produce an ordered, dependency-aware checklist of all artifacts to create or modify when porting a GitHub Copilot repository to Claude Code format. The plan is derived from the component inventory (see `docs/templates/component-inventory.md`) and the Copilot-to-Claude Code mapping reference (product-vision.md 5.4).

**Fulfills:** FOUND-FR-05 (produce a porting plan listing all artifacts to create or modify)

---

## Instructions

1. **Start from the filled-in component inventory** — Every component from the inventory should have a corresponding plan item.
2. **Order by dependencies** — Components that create the foundation for others come first. For example:
   - Templates and mapping definitions first
   - Agent prompts next (these are the primary ported artifacts)
   - Installation/setup follows (needs the agent to reference)
   - Workflow porting next (standalone, depends only on foundation)
   - Validation last (needs everything installed and ported)
3. **Assign execution** — Each task should be assigned to the appropriate agent (porting-architect, dirk-agent-engineer, setup-engineer, workflow-engineer, qa-engineer).
4. **Plan in phases** — Group tasks into logical phases that can be completed, validated, and committed independently.

---

## Plan Structure Template

```markdown
# Porting Plan: [Repository Name]

**Source path:** `/path/to/source-repo`
**Derived from inventory:** [Link to filled-in inventory]
**Date:** [YYYY-MM-DD]

---

## Phase 1: Foundation
*Creates the process artifacts and mapping reference needed by subsequent phases.*

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 1.1 | [task] | [agent] | [component names] | [FOUND-FR-xx] | None | [Small/Med/Large] |
| 1.2 | [task] | [agent] | [component names] | [FOUND-FR-xx] | 1.1 | [Small/Med/Large] |

---

## Phase 2: Agent Porting
*Ports the primary agent prompt(s) to Claude Code format.*

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 2.1 | [task] | [agent] | [component names] | [DIRK-FR-xx] | 1.x | [Small/Med/Large] |
| 2.2 | [task] | [agent] | [component names] | [DIRK-FR-xx] | 2.1 | [Small/Med/Large] |

---

## Phase 3: Bootstrap & Setup
*Configures the project environment and documentation.*

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 3.1 | [task] | [agent] | [component names] | [SETUP-FR-xx] | 2.x | [Small/Med/Large] |
| 3.2 | [task] | [agent] | [component names] | [SETUP-FR-xx] | 3.1 | [Small/Med/Large] |

---

## Phase 4: Workflow Porting (Optional)
*Ports CI/CD workflows to Claude Code equivalents.*

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 4.1 | [task] | [agent] | [component names] | [WF-FR-xx] | 1.x | [Small/Med/Large] |
| 4.2 | [task] | [agent] | [component names] | [WF-FR-xx] | 4.1 | [Small/Med/Large] |

---

## Phase 5: Validation & Testing
*Verifies all ported components work correctly.*

| # | Task | Agent | Component(s) | Requirement IDs | Depends On | Est. Effort |
|---|------|-------|--------------|-----------------|------------|-------------|
| 5.1 | [task] | [agent] | [component names] | [VAL-FR-xx] | 2.x, 3.x | [Small/Med/Large] |
| 5.2 | [task] | [agent] | [component names] | [VAL-FR-xx] | 5.1 | [Small/Med/Large] |

---

## Dependency Summary

```
Phase 1 (Foundation) — no dependencies
  │
  ├── Phase 2 (Agent Porting) — depends on Phase 1
  │     │
  │     ├── Phase 3 (Bootstrap & Setup) — depends on Phase 2
  │     │
  │     └── Phase 2 + Phase 3 → Phase 5 (Validation)
  │
  └── Phase 4 (Workflow Porting) — depends on Phase 1 (parallel with 2, 3)
```

## Legend

| Field | Description |
|-------|-------------|
| `#` | Sequential task number within its phase |
| `Task` | Description of what to build or modify |
| `Agent` | The specialist agent responsible for execution |
| `Component(s)` | Which components from the inventory are affected |
| `Requirement IDs` | The feature requirements this task fulfills |
| `Depends On` | Task numbers that must be completed first |
| `Est. Effort` | Small (minutes), Medium (hours), Large (half-day+) |

## Notes

- Add any assumptions, decisions, or context here
- Items marked `(Optional)` can be deferred to a later iteration
- If a task cannot be completed, document the blocking issue and move on
