"""Component inventory — model and serialization for scan results."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from port.mapper import compute_porting_target, get_mapping
from port.scanner import DiscoveredComponent


@dataclass
class GapEntry:
    """A component that couldn't be mapped to a Claude Code equivalent."""
    number: int
    component: str
    gap_description: str
    proposed_resolution: str = "Requires manual review"


@dataclass
class InventoryEntry:
    """One row in the component inventory."""
    number: int
    component: str
    path: str
    component_type: str
    sub_type: str | None
    purpose: str
    porting_target: str
    priority: str
    notes: str = ""


@dataclass
class ComponentInventory:
    """The full inventory produced by scanning + mapping a source repo."""
    source_path: str
    analyzed_by: str = "port CLI v0.2.0"
    date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    entries: list[InventoryEntry] = field(default_factory=list)
    gaps: list[GapEntry] = field(default_factory=list)


def build_inventory(
    components: list[DiscoveredComponent],
    source_root: Path,
) -> ComponentInventory:
    """Take raw scan results, apply the mapper, produce a full inventory.

    Parameters
    ----------
    components:
        Flat list of discovered components from ``scanner.scan_directory``.
    source_root:
        Absolute path to the source repo (used for the serialised path).

    Returns
    -------
    ``ComponentInventory`` with mapped entries and any gap log items.
    """
    entries: list[InventoryEntry] = []
    gaps: list[GapEntry] = []
    gap_counter = 0

    for i, comp in enumerate(components, start=1):
        porting_target = compute_porting_target(comp)
        mapping = get_mapping(comp.component_type)
        notes = ""

        if comp.component_type == "unknown":
            gap_counter += 1
            gaps.append(GapEntry(
                number=gap_counter,
                component=comp.name,
                gap_description=f"Cannot classify: {comp.path}",
            ))
            notes = "UNCLASSIFIED — see gap log"

        entry = InventoryEntry(
            number=i,
            component=comp.name,
            path=str(comp.path.as_posix()),
            component_type=comp.component_type,
            sub_type=comp.sub_type,
            purpose=comp.purpose,
            porting_target=porting_target,
            priority=comp.priority,
            notes=notes,
        )
        entries.append(entry)

    return ComponentInventory(
        source_path=str(source_root),
        entries=entries,
        gaps=gaps,
    )


# ── serializable wrapper for YAML output ────────────────────────────────


@dataclass
class InventoryFile:
    """Flat, YAML-friendly structure for writing the inventory to disk."""

    source_path: str
    analyzed_by: str
    date: str
    entries: list[dict[str, Any]]
    gaps: list[dict[str, Any]]

    @classmethod
    def from_inventory(cls, inv: ComponentInventory) -> InventoryFile:
        return cls(
            source_path=inv.source_path,
            analyzed_by=inv.analyzed_by,
            date=inv.date,
            entries=[asdict(e) for e in inv.entries],
            gaps=[asdict(g) for g in inv.gaps],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "analyzed_by": self.analyzed_by,
            "date": self.date,
            "entries": self.entries,
            "gaps": self.gaps,
        }

    def write_yaml(self, path: Path) -> None:
        from port.writer import write_yaml
        write_yaml(self.to_dict(), path)
