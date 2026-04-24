"""Skill stub generator — produces minimal ``.claude/skills/<name>/SKILL.md`` files."""

from __future__ import annotations

from pathlib import Path

from port.writer import write_file, ensure_dir


SKILL_TEMPLATE = """\
---
name: {name}
description: >
  {description}
---

# Skill: {name}

{{One-sentence context about what this skill produces.}}

---

## Process

### Step 1: {{title}}

{{Instructions}}

---

## Reference

See the porting plan for the full specification.
"""


def generate_skill_stub(
    name: str,
    purpose: str,
    output_root: Path,
    dry_run: bool = False,
) -> Path:
    """Create a minimal ``.claude/skills/<name>/SKILL.md`` stub.

    Parameters
    ----------
    name:
        Skill name (e.g. ``repo_inventory``).
    purpose:
        One-line description of what the skill does.
    output_root:
        Directory where ``.claude/skills/`` will be created.
    dry_run:
        If True, only compute the path without writing.

    Returns
    -------
    Output ``Path`` that was (or would be) written.
    """
    out_path = output_root / ".claude" / "skills" / name / "SKILL.md"

    if not dry_run:
        content = SKILL_TEMPLATE.format(name=name, description=purpose)
        write_file(content, out_path)

    return out_path
