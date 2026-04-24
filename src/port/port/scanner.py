"""Directory walker and component classifier for the Port CLI.

Groups related files into logical components (rather than one-per-file) using
path-pattern heuristics.  Ten component types are supported.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


# ── paths/patterns to skip ──────────────────────────────────────────────

EXCLUDED_DIRS = frozenset({
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".eggs", "eggs", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".claude", ".egg-info",
})

EXCLUDED_PATTERNS = (".pyc", ".pyo", ".egg-info", ".DS_Store",
                     ".tmp", ".swp", ".coverage")

# Runtime-output directories — not source components.
OUTPUT_DIRS = frozenset({"graph", "findings", "dist", "build", "htmlcov"})


COMPONENT_TYPES = [
    "agent_prompt",
    "workflow",
    "config",
    "cli_tool",
    "test_suite",
    "documentation",
    "bootstrap",
    "source_library",
    "skill_module",
    "unknown",
]


# ── data model ──────────────────────────────────────────────────────────


@dataclass
class DiscoveredComponent:
    name: str
    path: Path                     # relative to source root
    component_type: str = "unknown"
    sub_type: str | None = None
    purpose: str = ""
    size_bytes: int = 0
    priority: str = "Must"
    file_count: int = 1            # how many files this component groups


# ── helpers ─────────────────────────────────────────────────────────────


def _is_excluded(rel_path: Path) -> bool:
    for part in rel_path.parts:
        if part in EXCLUDED_DIRS or part in OUTPUT_DIRS:
            return True
        if part.endswith(".egg-info"):
            return True
    return False


def _classify(rel_path: Path) -> tuple[str, str | None]:
    """Return ``(component_type, sub_type)``.  First-match wins."""
    parts = rel_path.parts
    name = rel_path.name

    # agent_prompt
    if len(parts) >= 3 and parts[0] == ".github" and parts[1] == "agents" and name.endswith(".md"):
        return ("agent_prompt", "copilot")

    # workflow
    if len(parts) >= 3 and parts[0] == ".github" and parts[1] == "workflows" and name.endswith((".yml", ".yaml")):
        return ("workflow", "github_actions")

    # config (specific file names)
    if name.endswith(".config.yml") or name == "repos.yml":
        return ("config", "yaml")
    if name in ("pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "poetry.lock",
                "Cargo.toml", "go.mod", "Gemfile", "Package.swift"):
        return ("config", "build")

    # test suite directory
    if parts[0] == "tests":
        return ("test_suite", "pytest")

    # CLI tool entry point
    if name in ("cli.py", "main.py") and "src" in parts:
        return ("cli_tool", None)

    # documentation
    if name == "README.md":
        return ("documentation", None)
    if len(parts) >= 2 and parts[0] == "docs" and name.endswith(".md"):
        return ("documentation", None)

    # bootstrap
    if name in ("Makefile", "requirements.txt", ".gitignore", ".env.example", "Dockerfile", "docker-compose.yml"):
        return ("bootstrap", name.lower())
    if len(parts) >= 2 and parts[0] == "script" and parts[1] in ("setup", "bootstrap", "install"):
        return ("bootstrap", "script")

    # skill_module (Python files inside a "skills" directory)
    if "skills" in parts and name.endswith(".py"):
        return ("skill_module", None)

    # source_library: .py files in src/ that are NOT cli.py/main.py
    if parts[0] == "src" and name.endswith(".py") and name not in ("cli.py", "main.py"):
        return ("source_library", None)

    # config: anything else in .github/ or at root that looks like config
    if name.endswith((".yml", ".yaml", ".json", ".toml")):
        return ("config", None)

    # schema / templates (part of source library)
    if name.endswith(".sql"):
        return ("source_library", "schema")
    if name.endswith((".html", ".j2", ".jinja")):
        return ("source_library", "template")

    # license
    if name == "LICENSE":
        return ("documentation", "license")

    return ("unknown", None)


def _generate_purpose(rel_path: Path, ctype: str, sub: str | None, count: int = 1) -> str:
    if ctype == "agent_prompt":
        return f"System prompt defining agent behaviour ({rel_path.name})"
    if ctype == "workflow":
        return f"CI/CD workflow definition ({rel_path.name})"
    if ctype == "config":
        return f"Configuration file ({rel_path.name})"
    if ctype == "cli_tool":
        return "CLI entry point for the tool"
    if ctype == "test_suite":
        return f"Test suite ({count} files) for validating the project"
    if ctype == "documentation":
        return f"Project documentation ({rel_path.name})"
    if ctype == "bootstrap":
        return f"Setup/dev configuration ({rel_path.name})"
    if ctype == "skill_module":
        return f"Skill module for the agent pipeline"
    if ctype == "source_library":
        return f"Core library module ({rel_path.name})"
    return f"Unknown component ({rel_path})"


# ── scanning ────────────────────────────────────────────────────────────


def _walk(source_root: Path) -> Iterator[Path]:
    """Yield relative paths of non-excluded files."""
    for dirpath_str, dirnames, filenames in os.walk(source_root):
        dirpath = Path(dirpath_str)
        rel = dirpath.relative_to(source_root)

        # Prune in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        for fn in filenames:
            if fn in EXCLUDED_PATTERNS or fn.endswith((".pyc", ".pyo")):
                continue
            yield rel / fn


def scan_directory(source_root: Path) -> list[DiscoveredComponent]:
    """Walk *source_root* and group files into logical components.

    The result is a list of ``DiscoveredComponent`` objects — one per
    logical component (not one per file).  Related files (e.g. all ``tests/``
    files) are grouped into a single component entry.
    """
    source_root = source_root.resolve()

    # Collect every file with its classification
    raw: list[tuple[Path, str, str | None]] = []
    for rel_path in _walk(source_root):
        if _is_excluded(rel_path):
            continue
        ctype, sub = _classify(rel_path)
        raw.append((rel_path, ctype, sub))

    # Group by (component_type, sub_type, top-level-group-key)
    # For directories (tests/, docs/, src/...), group everything under that dir.
    groups: dict[str, list[tuple[Path, str, str | None]]] = {}
    for rel_path, ctype, sub in raw:
        # Determine group key
        parts = rel_path.parts
        if ctype == "test_suite" and parts[0] == "tests":
            key = "tests"
        elif ctype == "skill_module" and "skills" in parts:
            # Group all skills together with parent prefix
            idx = parts.index("skills")
            key = str(Path(*parts[:idx+1])) if idx > 0 else "skills"
        elif ctype == "documentation" and len(parts) >= 2 and parts[0] == "docs":
            key = "docs"
        elif ctype == "agent_prompt":
            key = rel_path.as_posix()
        elif ctype in ("source_library", "cli_tool") and parts[0] == "src":
            # CLI tool files get their own key; source_library grouped by subdir
            if ctype == "cli_tool":
                key = rel_path.as_posix()
            else:
                key = str(Path(parts[0]) / parts[1]) if len(parts) > 1 else "src"
        else:
            key = rel_path.as_posix()  # each file is its own group

        groups.setdefault(key, []).append((rel_path, ctype, sub))

    # Build discovered components
    components: list[DiscoveredComponent] = []
    seen_paths: set[str] = set()

    for key, items in groups.items():
        # Pick a representative path
        rep_path = items[0][0]
        ctype = items[0][1]
        sub_type = items[0][2]
        count = len(items)

        # Use the group key as the "path" if it's a directory grouping
        if key in ("tests", "docs", "skills") or key.startswith("src/"):
            display_path = Path(key)
        else:
            display_path = rep_path

        # Skip duplicates (e.g., if an individual file was also matched)
        path_str = display_path.as_posix()
        if path_str in seen_paths:
            continue
        seen_paths.add(path_str)

        total_size = sum((source_root / p[0]).stat().st_size for p in items)

        purpose = _generate_purpose(display_path, ctype, sub_type, count)

        components.append(DiscoveredComponent(
            name=display_path.name if count == 1 else display_path.as_posix(),
            path=display_path,
            component_type=ctype,
            sub_type=sub_type,
            purpose=purpose,
            size_bytes=total_size,
            file_count=count,
        ))

    # Sort for deterministic output
    components.sort(key=lambda c: c.path.as_posix())
    return components
