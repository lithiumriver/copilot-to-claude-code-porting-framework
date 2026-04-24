"""Mapping reference — translates Copilot component types to Claude Code equivalents.

Encodes the mapping reference from ``product-vision.md §5.4`` as code.
Each component type maps to a ``MappingEntry`` with a target path template,
translation notes, and a ``porting_action`` that drives the generator logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from port.scanner import DiscoveredComponent


@dataclass(frozen=True)
class MappingEntry:
    """One row from the Copilot-to-Claude Code mapping reference."""

    copilot_concept: str
    claude_code_target: str
    translation_notes: str
    porting_action: str  # rewrite_with_frontmatter | keep_as_is | create_claude_md | reference_in_claude_md | map_to_hooks | generate_stub | unknown


# ── the canonical mapping table ─────────────────────────────────────────

MAPPING_REFERENCE: dict[str, MappingEntry] = {
    "agent_prompt": MappingEntry(
        copilot_concept=".github/agents/<name>.md",
        claude_code_target=".claude/agents/<name>.md",
        translation_notes="Add YAML frontmatter; adjust tool permissions",
        porting_action="rewrite_with_frontmatter",
    ),
    "workflow": MappingEntry(
        copilot_concept="GitHub Actions workflow",
        claude_code_target="settings.json hooks + cron/schedule skill",
        translation_notes="Map triggers to Claude Code equivalents",
        porting_action="map_to_hooks",
    ),
    "config": MappingEntry(
        copilot_concept="YAML / TOML config files",
        claude_code_target="Keep as-is",
        translation_notes="Compatible format; consumed by original tooling",
        porting_action="keep_as_is",
    ),
    "cli_tool": MappingEntry(
        copilot_concept="CLI entry points",
        claude_code_target="Keep as-is",
        translation_notes="Invoke via Claude Code bash tool",
        porting_action="keep_as_is",
    ),
    "test_suite": MappingEntry(
        copilot_concept="Test suite (pytest)",
        claude_code_target="Keep as-is",
        translation_notes="Run via bash for validation; no translation needed",
        porting_action="keep_as_is",
    ),
    "documentation": MappingEntry(
        copilot_concept="README / docs",
        claude_code_target="CLAUDE.md + reference original README",
        translation_notes="Condense key instructions into CLAUDE.md",
        porting_action="create_claude_md",
    ),
    "bootstrap": MappingEntry(
        copilot_concept="Bootstrap scripts / dev config",
        claude_code_target="script/setup or CLAUDE.md sections",
        translation_notes="Adapt to Claude Code setup conventions",
        porting_action="reference_in_claude_md",
    ),
    "source_library": MappingEntry(
        copilot_concept="Python / library code",
        claude_code_target="Keep as-is",
        translation_notes="No translation; agents call via bash tool",
        porting_action="keep_as_is",
    ),
    "skill_module": MappingEntry(
        copilot_concept="Copilot skills / extensions",
        claude_code_target=".claude/skills/<name>/SKILL.md",
        translation_notes="Document as Claude Code skill files",
        porting_action="generate_stub",
    ),
    "unknown": MappingEntry(
        copilot_concept="Unknown",
        claude_code_target="TBD — requires manual review",
        translation_notes="Component could not be auto-classified",
        porting_action="unknown",
    ),
}


def get_mapping(component_type: str) -> MappingEntry:
    """Return the ``MappingEntry`` for a component type string.

    Falls back to ``unknown`` if the type isn't in the table.
    """
    return MAPPING_REFERENCE.get(component_type, MAPPING_REFERENCE["unknown"])


def compute_porting_target(component: DiscoveredComponent) -> str:
    """Produce the human-readable 'Porting Target' string for an inventory entry."""
    mapping = get_mapping(component.component_type)
    target = mapping.claude_code_target

    if mapping.porting_action == "rewrite_with_frontmatter":
        # Derive agent name from the filename
        name = component.path.stem  # e.g. "dirk" from ".github/agents/dirk.md"
        target = f".claude/agents/{name}.md"
    elif mapping.porting_action == "generate_stub":
        name = component.path.stem
        target = f".claude/skills/{name}/SKILL.md"

    return target


def resolve_action(component: DiscoveredComponent) -> str:
    """Return the porting action string for *component*."""
    return get_mapping(component.component_type).porting_action
