"""CLAUDE.md generator — produces project-level Claude Code instructions."""

from __future__ import annotations

from typing import Any


def generate_claude_md(plan_data: dict[str, Any]) -> str:
    """Generate CLAUDE.md content from the porting plan data."""
    source_path = plan_data.get("source_path", ".")

    lines = [
        f"# Ported Project",
        "",
        f"Source repository: `{source_path}`",
        "",
        "## Setup",
        "",
        "```bash",
        "pip install -e .",
        "```",
        "",
        "## Configuration",
        "",
        f"Edit configuration files in `{source_path}` as needed.",
        "",
        "## Usage",
        "",
        "Invoke the ported agent, or run tools directly via the CLI.",
        "",
        "## Testing",
        "",
        "```bash",
        "pytest",
        "```",
        "",
        "## Porting Reference",
        "",
        "This project was ported from Copilot to Claude Code using the `port` CLI.",
        f"See `component-inventory.yml` for the full component map.",
        "",
    ]
    return "\n".join(lines)
