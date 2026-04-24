"""Workflow generator — documents how to run CI/CD equivalents in Claude Code."""

from __future__ import annotations

from pathlib import Path


def generate_workflow_doc(component_name: str, source_root: Path) -> str:
    """Generate a Markdown document describing the Claude Code equivalent of a
    GitHub Actions workflow.

    Parameters
    ----------
    component_name:
        Name of the workflow component (e.g. ``dirk-scan.yml``).
    source_root:
        Absolute path to the source repository.

    Returns
    -------
    Markdown content describing the manual run pattern.
    """
    # Try to read the original workflow to extract triggers
    candidates = [
        source_root / ".github" / "workflows" / component_name,
        source_root / ".github" / "workflows" / f"{component_name}.yml",
        source_root / ".github" / "workflows" / f"{component_name}.yaml",
    ]
    workflow_path: Path | None = None
    for c in candidates:
        if c.is_file():
            workflow_path = c
            break

    schedule_info = "unknown"
    manual_only = "manual invocation"
    run_command = "implement the run steps documented in the plan"

    if workflow_path:
        content = workflow_path.read_text(encoding="utf-8")
        # Basic YAML parsing to extract schedule and steps
        import yaml
        try:
            data = yaml.safe_load(content) or {}
            on_section = data.get("on", {})
            if isinstance(on_section, dict):
                if "schedule" in on_section:
                    cron_entries = on_section["schedule"]
                    if cron_entries:
                        schedule_info = str(cron_entries)
                if "workflow_dispatch" in on_section:
                    manual_only = "on-demand (workflow_dispatch)"

            # Extract run steps
            jobs = data.get("jobs", {})
            run_lines = []
            for job_name, job in jobs.items():
                steps = job.get("steps", []) if isinstance(job, dict) else []
                for step in steps:
                    if isinstance(step, dict) and "run" in step:
                        run_lines.append(step["run"])
            if run_lines:
                run_command = "\n".join(run_lines)
        except yaml.YAMLError:
            pass

    lines = [
        f"# Workflow: {component_name}",
        "",
        "## Source",
        "",
        f"Original workflow: `{workflow_path.relative_to(source_root) if workflow_path else 'not found'}`",
        "",
        "## Claude Code Equivalent",
        "",
        "This workflow has been ported to a manual run pattern.",
        "",
        "### Triggers",
        "",
        f"- Schedule: `{schedule_info}` (ported to manual invocation)",
        f"- Manual: {manual_only}",
        "",
        "### How to Run",
        "",
        "1. Ensure dependencies are installed.",
        "2. Run the pipeline:",
        "",
        "```bash",
        run_command,
        "```",
        "",
        "3. Review output changes.",
        "",
        "### Notes",
        "",
        "- PR creation is GitHub-specific and not ported.",
        "- Review changes locally via `git diff` or `git status`.",
        "- To schedule recurring runs, use the Claude Code `schedule` skill.",
        "",
    ]
    return "\n".join(lines)
