"""Validator — checks generated Claude Code artifacts for correctness."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ValidationResult:
    check: str
    status: str       # "pass", "fail", "skip"
    detail: str = ""

    @classmethod
    def ok(cls, check: str, detail: str = "") -> ValidationResult:
        return cls(check=check, status="pass", detail=detail)

    @classmethod
    def fail(cls, check: str, detail: str = "") -> ValidationResult:
        return cls(check=check, status="fail", detail=detail)

    @classmethod
    def skip(cls, check: str, detail: str = "") -> ValidationResult:
        return cls(check=check, status="skip", detail=detail)


@dataclass
class ValidationReport:
    source_path: str
    generated_dir: str
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == "skip")

    def summary_str(self) -> str:
        parts = []
        for r in self.results:
            icon = {"pass": "✅", "fail": "❌", "skip": "⏭"}[r.status]
            msg = f"  {icon} [{r.status.upper()}] {r.check}"
            if r.detail:
                msg += f" — {r.detail}"
            parts.append(msg)
        parts.append(
            f"\n  Summary: {self.passed} passed, {self.failed} failed, "
            f"{self.skipped} skipped"
        )
        return "\n".join(parts)


# ── individual checks ───────────────────────────────────────────────────


def _validate_agent_frontmatter(path: Path, results: list[ValidationResult]) -> None:
    """Check that an agent file has valid YAML frontmatter with required fields."""
    check_name = f"agent frontmatter: {path.name}"

    if not path.exists():
        results.append(ValidationResult.fail(check_name, "File not found"))
        return

    content = path.read_text(encoding="utf-8")
    stripped = content.lstrip("﻿")

    if not stripped.startswith("---"):
        results.append(ValidationResult.fail(check_name, "Missing YAML frontmatter (---)"))
        return

    end = stripped.find("---", 3)
    if end == -1:
        results.append(ValidationResult.fail(check_name, "Unclosed YAML frontmatter"))
        return

    try:
        fm = dict(yaml.safe_load(stripped[3:end]) or {})
    except yaml.YAMLError as e:
        results.append(ValidationResult.fail(check_name, f"YAML parse error: {e}"))
        return

    # Required fields
    if "name" not in fm or not str(fm.get("name", "")).strip():
        results.append(ValidationResult.fail(check_name, "Missing or empty 'name' field"))
        return
    if "description" not in fm or not str(fm.get("description", "")).strip():
        results.append(ValidationResult.fail(check_name, "Missing or empty 'description' field"))
        return
    tools = fm.get("tools", [])
    if not isinstance(tools, list) or not tools:
        results.append(ValidationResult.fail(check_name,
                                              "Missing or empty 'tools' list"))
        return
    for t in tools:
        if not isinstance(t, str) or not t.strip():
            results.append(ValidationResult.fail(check_name,
                                                  f"Invalid tool entry: {t!r}"))
            return

    results.append(ValidationResult.ok(check_name,
                                        f"name={fm['name']}, tools={tools}"))


def _validate_claude_md(path: Path, results: list[ValidationResult]) -> None:
    """Check that CLAUDE.md exists and has basic structure."""
    check_name = "CLAUDE.md structure"

    if not path.exists():
        results.append(ValidationResult.fail(check_name, "File not found"))
        return

    content = path.read_text(encoding="utf-8")
    if not content.strip():
        results.append(ValidationResult.fail(check_name, "Empty file"))
        return

    issues = []
    if not any(line.startswith("# ") for line in content.splitlines()):
        issues.append("No H1 heading found")

    if issues:
        results.append(ValidationResult.fail(check_name, "; ".join(issues)))
    else:
        results.append(ValidationResult.ok(check_name))


def _validate_path_exists(path: Path, desc: str, results: list[ValidationResult]) -> None:
    """Check that a referenced path exists."""
    exists = path.exists()
    status = ValidationResult.ok if exists else ValidationResult.fail
    label = "path exists" if exists else "path not found"
    results.append(
        status(f"path: {desc}", f"{path} ({label})")
    )


def _run_test_suite(test_path: Path, results: list[ValidationResult]) -> None:
    """Optionally run pytest and report results."""
    check_name = f"test suite: {test_path}"

    if not test_path.exists():
        results.append(ValidationResult.skip(check_name, "Test path not found"))
        return

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-x", "-q", "--tb=short"],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        results.append(ValidationResult.fail(check_name, "Timed out after 120s"))
        return
    except FileNotFoundError:
        results.append(ValidationResult.skip(check_name, "pytest not available"))
        return

    passed = "passed" in proc.stdout.lower() and "failed" not in proc.stdout.lower()
    if passed or proc.returncode == 0:
        results.append(ValidationResult.ok(check_name, proc.stdout.strip()))
    else:
        results.append(ValidationResult.fail(check_name, proc.stdout.strip()))


# ── main validation entry point ─────────────────────────────────────────


def run_validation(
    generated_dir: Path,
    inventory_data: dict[str, Any] | None = None,
    run_tests: bool = False,
    test_path: Path | None = None,
) -> ValidationReport:
    """Run all validation checks on a generated directory.

    Parameters
    ----------
    generated_dir:
        The ``generated/`` directory produced by ``port generate``.
    inventory_data:
        The parsed inventory YAML (used for test discovery).
    run_tests:
        Whether to attempt running the test suite.
    test_path:
        Explicit path to the test suite. If None and *inventory_data* is
        provided, auto-discover from inventory entries with
        ``component_type: test_suite``.

    Returns
    -------
    ``ValidationReport`` with all check results.
    """
    results: list[ValidationResult] = []

    # -- Agent files --
    agents_dir = generated_dir / ".claude" / "agents"
    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*.md")):
            _validate_agent_frontmatter(agent_file, results)
    else:
        results.append(ValidationResult.skip("agent files", "No .claude/agents/ directory"))

    # -- CLAUDE.md --
    claude_md = generated_dir / "CLAUDE.md"
    if claude_md.exists():
        _validate_claude_md(claude_md, results)
    else:
        results.append(ValidationResult.skip("CLAUDE.md", "Not generated"))

    # -- Path existence for keep_as_is components --
    if inventory_data:
        source_path = Path(inventory_data.get("source_path", ""))
        if source_path.exists():
            for entry in inventory_data.get("entries", []):
                if entry.get("porting_target", "").lower() == "keep as-is":
                    full = source_path / entry.get("path", "")
                    _validate_path_exists(full, entry["component"], results)

    # -- Test suite --
    if run_tests or test_path:
        if test_path:
            _run_test_suite(test_path, results)
        elif inventory_data:
            # Auto-discover test paths from inventory
            for entry in inventory_data.get("entries", []):
                if entry.get("component_type") == "test_suite":
                    src = Path(inventory_data.get("source_path", "."))
                    tp = src / entry.get("path", "")
                    _run_test_suite(tp, results)
        else:
            results.append(ValidationResult.skip("test suite",
                                                  "No inventory for test discovery"))
    else:
        results.append(ValidationResult.skip("test suite",
                                              "Use --tests to enable"))

    return ValidationReport(
        source_path=str(generated_dir),
        generated_dir=str(generated_dir),
        results=results,
    )
