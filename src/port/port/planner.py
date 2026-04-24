"""Porting plan generator.

Distributes inventory entries across 5 canonical phases and generates
tasks with dependency tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from port.inventory import ComponentInventory, InventoryEntry


@dataclass
class PlanTask:
    task_id: str
    task: str
    agent: str
    components: list[str]
    requirement_ids: list[str]
    depends_on: list[str]
    est_effort: str = "Small"


@dataclass
class PlanPhase:
    phase_number: int
    phase_name: str
    description: str
    tasks: list[PlanTask] = field(default_factory=list)


@dataclass
class PortingPlan:
    source_path: str
    derived_from_inventory: str
    date: str
    phases: list[PlanPhase] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "derived_from_inventory": self.derived_from_inventory,
            "date": self.date,
            "dependency_summary": self._dependency_summary(),
            "phases": [
                {
                    "phase_number": p.phase_number,
                    "phase_name": p.phase_name,
                    "description": p.description,
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "task": t.task,
                            "agent": t.agent,
                            "components": t.components,
                            "requirement_ids": t.requirement_ids,
                            "depends_on": t.depends_on,
                            "est_effort": t.est_effort,
                        }
                        for t in p.tasks
                    ],
                }
                for p in self.phases
            ],
        }

    def _dependency_summary(self) -> str:
        return """\
Phase 1 (Foundation) — no dependencies
  |
  ├── Phase 2 (Agent Porting) — depends on Phase 1
  |     |
  |     ├── Phase 3 (Bootstrap & Setup) — depends on Phase 2
  |     |
  |     └── Phase 2 + Phase 3 → Phase 5 (Validation)
  |
  └── Phase 4 (Workflow Porting) — depends on Phase 1 (parallel with 2, 3)"""


def generate_plan(inventory: ComponentInventory) -> PortingPlan:
    """Distribute inventory entries across 5 phases and produce a ``PortingPlan``.

    Phase distribution logic:

    1. **Foundation** — Always created. Records the inventory and plan metadata.
    2. **Agent Porting** — One task per ``agent_prompt`` component.
    3. **Bootstrap & Setup** — For ``bootstrap``, ``config``, ``documentation``,
       ``source_library``, ``cli_tool`` components that need documentation/setup.
    4. **Workflow Porting** — One task per ``workflow`` component.
    5. **Validation & Testing** — For ``test_suite`` components + agent validation.
    """
    phases: list[PlanPhase] = []
    task_counter = [0]  # mutable counter for task IDs

    def _next_id() -> str:
        task_counter[0] += 1
        return str(task_counter[0])

    def _by_type(ctype: str) -> list[InventoryEntry]:
        return [e for e in inventory.entries if e.component_type == ctype]

    # ── Phase 1: Foundation ──────────────────────────────────────────
    p1 = PlanPhase(
        phase_number=1,
        phase_name="Foundation",
        description="Process artifacts and mapping reference for the porting project.",
    )
    task_counter[0] = 0
    p1.tasks.append(PlanTask(
        task_id=_next_id(),
        task=f"Analyse source repo and produce component inventory ({len(inventory.entries)} entries)",
        agent="porting-architect",
        components=[e.component for e in inventory.entries],
        requirement_ids=["FOUND-FR-02", "FOUND-FR-03"],
        depends_on=[],
        est_effort="Small",
    ))
    p1.tasks.append(PlanTask(
        task_id=_next_id(),
        task="Apply Copilot-to-Claude Code mapping reference to all components",
        agent="porting-architect",
        components=[e.component for e in inventory.entries],
        requirement_ids=["FOUND-FR-04"],
        depends_on=[p1.tasks[0].task_id],
        est_effort="Small",
    ))
    phases.append(p1)

    # ── Phase 2: Agent Porting ───────────────────────────────────────
    agent_entries = _by_type("agent_prompt")
    p2 = PlanPhase(
        phase_number=2,
        phase_name="Agent Porting",
        description="Port Copilot agent prompts to Claude Code agent files.",
    )
    p2_dep = p1.tasks[-1].task_id
    for entry in agent_entries:
        p2.tasks.append(PlanTask(
            task_id=_next_id(),
            task=f"Port agent prompt '{entry.component}' to Claude Code format",
            agent="dirk-agent-engineer",
            components=[entry.component],
            requirement_ids=["DIRK-FR-01", "DIRK-FR-02", "DIRK-FR-03"],
            depends_on=[p2_dep],
            est_effort="Medium",
        ))
        p2_dep = p2.tasks[-1].task_id
    phases.append(p2)

    # ── Phase 3: Bootstrap & Setup ───────────────────────────────────
    setup_types = {"bootstrap", "config", "cli_tool", "documentation", "source_library"}
    setup_entries = [e for e in inventory.entries if e.component_type in setup_types]
    p3 = PlanPhase(
        phase_number=3,
        phase_name="Bootstrap & Setup",
        description="Install dependencies, configure environment, document usage.",
    )
    p3_dep = agent_entries[0].component if agent_entries else p1.tasks[-1].task_id
    # Install task
    p3.tasks.append(PlanTask(
        task_id=_next_id(),
        task="Install Python dependencies and verify CLI entry point",
        agent="setup-engineer",
        components=[e.component for e in _by_type("config")],
        requirement_ids=["SETUP-FR-01"],
        depends_on=[str(task_counter[0])],  # placeholder — will be fixed below
        est_effort="Small",
    ))
    # CLAUDE.md task
    p3.tasks.append(PlanTask(
        task_id=_next_id(),
        task="Create/update CLAUDE.md with setup, configuration, usage, and testing instructions",
        agent="setup-engineer",
        components=[e.component for e in setup_entries],
        requirement_ids=["SETUP-FR-02", "SETUP-FR-03"],
        depends_on=[p3.tasks[0].task_id],
        est_effort="Medium",
    ))
    phases.append(p3)

    # ── Phase 4: Workflow Porting ────────────────────────────────────
    workflow_entries = _by_type("workflow")
    p4 = PlanPhase(
        phase_number=4,
        phase_name="Workflow Porting",
        description="Port CI/CD workflows to Claude Code equivalents.",
    )
    for entry in workflow_entries:
        p4.tasks.append(PlanTask(
            task_id=_next_id(),
            task=f"Port workflow '{entry.component}' to Claude Code manual run pattern",
            agent="workflow-engineer",
            components=[entry.component],
            requirement_ids=["WF-FR-01"],
            depends_on=[p1.tasks[-1].task_id],
            est_effort="Small",
        ))
    phases.append(p4)

    # ── Phase 5: Validation & Testing ────────────────────────────────
    test_entries = _by_type("test_suite")
    p5 = PlanPhase(
        phase_number=5,
        phase_name="Validation & Testing",
        description="Verify all ported components work correctly.",
    )
    p5_deps = [p1.tasks[-1].task_id]
    if p2.tasks:
        p5_deps.append(p2.tasks[-1].task_id)
    if p3.tasks:
        p5_deps.append(p3.tasks[-1].task_id)

    p5.tasks.append(PlanTask(
        task_id=_next_id(),
        task="Run pytest suite to validate original components still work",
        agent="qa-engineer",
        components=[e.component for e in test_entries],
        requirement_ids=["VAL-FR-01", "VAL-FR-03"],
        depends_on=p5_deps,
        est_effort="Medium",
    ))
    p5.tasks.append(PlanTask(
        task_id=_next_id(),
        task="Validate generated agent YAML frontmatter and file references",
        agent="qa-engineer",
        components=[e.component for e in agent_entries],
        requirement_ids=["VAL-FR-03"],
        depends_on=p5_deps,
        est_effort="Small",
    ))
    phases.append(p5)

    return PortingPlan(
        source_path=inventory.source_path,
        derived_from_inventory="component-inventory.yml",
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        phases=phases,
    )
