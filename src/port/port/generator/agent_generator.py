"""Agent file generator — produces ``.claude/agents/<name>.md`` from Copilot agent prompts.

Pipeline:
1. Read the original agent markdown file from the source repo.
2. Parse / extract YAML frontmatter (or synthesise if absent).
3. Adjust the tools list (Copilot → Claude Code equivalents).
4. Rewrite path references in the body.
5. Write the result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from port.writer import write_file


# ── frontmatter template (f-string) ─────────────────────────────────────

AGENT_FRONTMATTER_TEMPLATE = """\
---
name: {name}
description: >
  {description}
tools:
{tools}
---
"""

# ── tool translation table (Copilot → Claude Code) ─────────────────────

TOOL_TRANSLATION: dict[str, str | None] = {
    "bash": "bash",
    "view": "read",
    "read": "read",
    "grep": "grep",
    "glob": "glob",
    "find": "find",
    "edit": None,       # removed — agents delegate to CLI
    "create": None,     # removed
    "search": None,     # removed
}

DEFAULT_TOOLS = ["bash", "read", "grep", "glob"]


def _adjust_tools(original: list[str]) -> list[str]:
    """Translate a Copilot tools list into Claude Code equivalents."""
    result: list[str] = []
    for t in original:
        mapped = TOOL_TRANSLATION.get(t)
        if mapped:
            if mapped not in result:
                result.append(mapped)
        # None → skip (tool has no Claude Code equivalent)
    # Ensure read is present
    if "read" not in result and "bash" in result:
        result.insert(result.index("bash") + 1, "read")
    return result


def _extract_agent_name(source_path: Path, source_content: str) -> str:
    """Derive the agent name from frontmatter or filename."""
    fm = _parse_frontmatter(source_content)
    if fm and "name" in fm:
        name = str(fm["name"]).strip()
        if name:
            return name
    # Fall back to filename stem
    return source_path.stem


def _extract_description(source_path: Path, source_content: str,
                         fallback: str = "") -> str:
    """Extract a one-line description from frontmatter or first paragraph."""
    fm = _parse_frontmatter(source_content)
    if fm and "description" in fm:
        desc = str(fm["description"]).strip()
        if desc:
            return desc
    # Fall back to first non-empty content line
    body = _strip_frontmatter(source_content).strip()
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:120]
    return fallback or "Claude Code agent ported from Copilot format"


def _extract_tools(source_content: str) -> list[str]:
    """Extract tools from frontmatter, or return default list."""
    fm = _parse_frontmatter(source_content)
    if fm and "tools" in fm:
        raw = fm["tools"]
        if isinstance(raw, list):
            return [str(t) for t in raw]
    return list(DEFAULT_TOOLS)


def _parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Try to parse YAML frontmatter from the start of *content*."""
    stripped = content.lstrip("﻿")
    if not stripped.startswith("---"):
        return None
    # Find closing ---
    end = stripped.find("---", 3)
    if end == -1:
        return None
    try:
        return dict(yaml.safe_load(stripped[3:end]) or {})
    except yaml.YAMLError:
        return None


def _strip_frontmatter(content: str) -> str:
    """Return the body after frontmatter, or the full content if no frontmatter."""
    stripped = content.lstrip("﻿")
    if not stripped.startswith("---"):
        return content
    end = stripped.find("---", 3)
    if end == -1:
        return content
    return stripped[end + 3:]


def _adjust_paths(body: str) -> str:
    """Rewrite common Copilot path references to Claude Code equivalents."""
    replacements = [
        (".github/agents/", ".claude/agents/"),
        (".github/workflows/", ".claude/workflows/"),  # if ported
    ]
    for old, new in replacements:
        body = body.replace(old, new)
    return body


def _render_tools_yaml(tools: list[str]) -> str:
    """Render the tools list as indented YAML list items."""
    return "\n".join(f"  - {t}" for t in tools)


def generate_agent_file(
    component_name: str,
    source_root: Path,
    output_root: Path,
    dry_run: bool = False,
) -> Path:
    """Generate a ``.claude/agents/<name>.md`` from a Copilot agent prompt.

    Parameters
    ----------
    component_name:
        Short name used to locate the component in the source (e.g. ``dirk``).
    source_root:
        Absolute path to the source repository root.
    output_root:
        Directory where ``.claude/agents/`` will be created.
    dry_run:
        If True, only compute the output path without writing.

    Returns
    -------
    The output ``Path`` that was (or would be) written.
    """
    # Locate the source file
    candidates = [
        source_root / ".github" / "agents" / f"{component_name}.md",
        source_root / ".github" / "agents" / component_name,
    ]
    source_path: Path | None = None
    for c in candidates:
        if c.is_file():
            source_path = c
            break
    if source_path is None:
        raise FileNotFoundError(
            f"Could not find agent file for '{component_name}' in {source_root}"
        )

    source_content = source_path.read_text(encoding="utf-8")

    # Extract / derive frontmatter fields
    agent_name = _extract_agent_name(source_path, source_content)
    original_tools = _extract_tools(source_content)
    description = _extract_description(source_path, source_content,
                                       fallback=f"Claude Code agent ported from {source_path.name}")

    # Adjust tools
    adjusted_tools = _adjust_tools(original_tools)

    # Build body
    body = _strip_frontmatter(source_content)
    body = _adjust_paths(body)

    # Render new frontmatter
    frontmatter = AGENT_FRONTMATTER_TEMPLATE.format(
        name=agent_name,
        description=description,
        tools=_render_tools_yaml(adjusted_tools),
    )

    full_content = frontmatter + body

    # Output path
    out_path = output_root / ".claude" / "agents" / f"{agent_name}.md"

    if not dry_run:
        write_file(full_content, out_path)

    return out_path
