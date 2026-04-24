"""Command-line interface for the Port CLI.

Usage::

    port init --source <repo-path>     # analyze + inventory + plan
    port scan [--source <path>]        # re-scan and diff
    port generate --plan <path>        # generate artifacts from plan
    port validate --generated <path>   # verify generated artifacts
    port run --all --source <path>     # full pipeline
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from port import __version__
from port.config import PortConfig, load_config
from port.scanner import scan_directory
from port.inventory import build_inventory, InventoryFile
from port.planner import generate_plan
from port.mapper import get_mapping
from port.writer import write_file, write_yaml, ensure_dir


# ── helpers shared by commands ──────────────────────────────────────────


def _load_plan_file(path: Path):
    """Load a porting plan YAML and return the dict."""
    import yaml
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _echo_summary(entries, gaps, inventory_path, plan_path):
    click.echo(f"\n  Found {len(entries)} components across "
               f"{len({e.component_type for e in entries})} types.")
    if gaps:
        click.echo(f"  ⚠ {len(gaps)} component(s) could not be classified "
                   f"(logged in gap log).")
    click.echo(f"  Inventory: {inventory_path}")
    click.echo(f"  Plan:      {plan_path}")


# ── CLI group ───────────────────────────────────────────────────────────


@click.group()
@click.version_option(__version__, prog_name="port")
@click.option(
    "--config", "config_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Path to port.config.yml.",
)
@click.option(
    "--root",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Project root directory (default: cwd).",
)
@click.pass_context
def main(ctx: click.Context, config_path: Path | None, root: Path | None) -> None:
    """Port — automate porting Copilot components to Claude Code format."""
    ctx.ensure_object(dict)


# ── init ────────────────────────────────────────────────────────────────


@main.command()
@click.option(
    "--source", "-s", "source",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Path to the source Copilot repository.",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory for inventory + plan (default: cwd).",
)
@click.option("--force", is_flag=True, help="Overwrite existing inventory/plan files.")
@click.option("--verbose", "-v", is_flag=True, help="Print progress details.")
@click.pass_context
def init(ctx: click.Context, source: Path, output: Path | None,
         force: bool, verbose: bool) -> None:
    """Analyze a source repo and produce component inventory + porting plan."""
    source = source.resolve()
    root = output.resolve() if output else Path.cwd()

    click.echo(f"Port init v{__version__} — analysing {source}")

    # Phase B: scan
    if verbose:
        click.echo("  Scanning directory structure...")
    components = scan_directory(source)
    if verbose:
        click.echo(f"  Found {len(components)} files/dirs to classify.")

    # Phase C: build inventory (which internally calls mapper)
    inventory = build_inventory(components, source)

    # Check for unknowns
    unknowns = [e for e in inventory.entries if e.component_type == "unknown"]
    if unknowns and not force:
        click.echo(f"\n  ⚠ {len(unknowns)} unknown component(s) found. "
                   f"Run with --force to accept defaults, or edit the inventory "
                   f"after generation.")
        if verbose:
            for u in unknowns:
                click.echo(f"     - {u.path}")

    # Phase D: generate plan
    plan = generate_plan(inventory)

    # Write outputs
    ensure_dir(root)

    inv_path = root / "component-inventory.yml"
    plan_path = root / "porting-plan.yml"

    if inv_path.exists() and not force:
        click.echo(f"  ✗ {inv_path} exists. Use --force to overwrite.", err=True)
        sys.exit(1)
    if plan_path.exists() and not force:
        click.echo(f"  ✗ {plan_path} exists. Use --force to overwrite.", err=True)
        sys.exit(1)

    inv_file = InventoryFile.from_inventory(inventory)
    inv_file.write_yaml(inv_path)
    plan_dict = plan.to_dict()
    write_yaml(plan_dict, plan_path)

    _echo_summary(inventory.entries, inventory.gaps, inv_path, plan_path)


# ── scan ────────────────────────────────────────────────────────────────


@main.command()
@click.option(
    "--source", "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Re-scan this path (default: from existing inventory).",
)
@click.option(
    "--inventory", "-i",
    type=click.Path(dir_okay=False, exists=True, path_type=Path),
    default=None,
    help="Path to existing inventory (default: component-inventory.yml).",
)
@click.option("--no-diff", is_flag=True, help="Skip diff output.")
@click.pass_context
def scan(ctx: click.Context, source: Path | None, inventory: Path | None,
         no_diff: bool) -> None:
    """Re-scan a source repo and diff against the existing inventory."""
    import yaml

    inv_path = inventory or Path.cwd() / "component-inventory.yml"
    if not inv_path.exists():
        click.echo(f"No inventory found at {inv_path}. Run `port init` first.", err=True)
        sys.exit(1)

    # Load existing inventory
    with inv_path.open("r", encoding="utf-8") as f:
        existing_data = yaml.safe_load(f) or {}
    existing_entries = {
        e["path"]: e for e in existing_data.get("entries", [])
    }

    # Determine source
    if source is None:
        source = Path(existing_data.get("source_path", "."))
    source = source.resolve()

    click.echo(f"Re-scanning {source} ...")
    components = scan_directory(source)
    inventory_new = build_inventory(components, source)
    new_entries = {e.path: e for e in inventory_new.entries}

    # Diff
    added = [p for p in new_entries if p not in existing_entries]
    removed = [p for p in existing_entries if p not in new_entries]
    changed = [
        p for p in new_entries
        if p in existing_entries
        and (new_entries[p].component_type != existing_entries[p].get("component_type")
             or new_entries[p].purpose != existing_entries[p].get("purpose", ""))
    ]

    if not no_diff:
        if added:
            click.echo(f"\n  + {len(added)} new component(s):")
            for p in sorted(added):
                click.echo(f"      + {p}  ({new_entries[p].component_type})")
        if removed:
            click.echo(f"\n  - {len(removed)} removed component(s):")
            for p in sorted(removed):
                click.echo(f"      - {p}")
        if changed:
            click.echo(f"\n  ~ {len(changed)} changed component(s):")
            for p in sorted(changed):
                click.echo(f"      ~ {p}")
        if not added and not removed and not changed:
            click.echo("  No changes detected.")

    # Write updated inventory
    inv_file = InventoryFile.from_inventory(inventory_new)
    inv_file.write_yaml(inv_path)
    click.echo(f"\n  Updated inventory: {inv_path}")


# ── generate ────────────────────────────────────────────────────────────


@main.command()
@click.option(
    "--plan", "-p", "plan_path",
    type=click.Path(dir_okay=False, exists=True, path_type=Path),
    required=True,
    help="Path to porting-plan.yml.",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory (default: cwd).",
)
@click.option(
    "--only-phase",
    type=int,
    default=None,
    help="Only generate artifacts for this phase number (1-5).",
)
@click.option("--dry-run", is_flag=True, help="Show what would be generated without writing.")
@click.pass_context
def generate(ctx: click.Context, plan_path: Path, output: Path | None,
             only_phase: int | None, dry_run: bool) -> None:
    """Generate Claude Code artifacts from a porting plan."""
    import yaml

    root = output.resolve() if output else Path.cwd()
    with plan_path.open("r", encoding="utf-8") as f:
        plan_data = yaml.safe_load(f) or {}

    phases = plan_data.get("phases", [])
    source_root = Path(plan_data.get("source_path", "."))
    generate_root = root / "generated"

    click.echo(f"Generating artifacts from {plan_path}")
    if dry_run:
        click.echo("  (dry-run mode — no files written)")

    generated_files = []

    for phase in phases:
        pnum = phase.get("phase_number", 0)
        if only_phase is not None and pnum != only_phase:
            continue

        tasks = phase.get("tasks", [])
        for task in tasks:
            action = (task.get("requirement_ids") or [None])[0]
            if not action:
                continue

            # Phase 2: agent generation
            if pnum == 2 and "DIRK-FR-01" in str(action):
                for comp_name in task.get("components", []):
                    _gen_agent(comp_name, source_root, generate_root,
                               root, dry_run, generated_files)

            # Phase 3: CLAUDE.md + bootstrap
            if pnum == 3 and "SETUP-FR-02" in str(action):
                _gen_claude_md(inventory=None, plan=plan_data,
                               generate_root=generate_root,
                               dry_run=dry_run, generated_files=generated_files)

            # Phase 4: workflow docs
            if pnum == 4 and "WF-FR-01" in str(action):
                for comp_name in task.get("components", []):
                    _gen_workflow(comp_name, source_root, generate_root,
                                  root, dry_run, generated_files)

    if not generated_files:
        click.echo("  No files were generated (no matching phases/tasks).")
        return

    click.echo(f"\n  Generated {len(generated_files)} file(s):")
    for f in generated_files:
        click.echo(f"    {f}")
    click.echo(f"\n  Output directory: {generate_root}")


# ── generate helpers ────────────────────────────────────────────────────


def _gen_agent(comp_name, source_root, generate_root, root, dry_run, generated_files):
    """Generate a .claude/agents/<name>.md file from an agent_prompt component."""
    from port.generator.agent_generator import generate_agent_file
    try:
        out = generate_agent_file(comp_name, source_root, generate_root, dry_run)
        generated_files.append(str(out.relative_to(root) if out.is_absolute() else out))
    except Exception as e:
        click.echo(f"  ⚠ Could not generate agent for '{comp_name}': {e}", err=True)


def _gen_claude_md(inventory, plan, generate_root, dry_run, generated_files):
    """Generate CLAUDE.md with setup and workflow instructions."""
    from port.generator.claude_md_generator import generate_claude_md
    content = generate_claude_md(plan)
    out_path = generate_root / "CLAUDE.md"
    if dry_run:
        generated_files.append(str(out_path))
    else:
        write_file(content, out_path)
        generated_files.append(str(out_path))


def _gen_workflow(comp_name, source_root, generate_root, root, dry_run, generated_files):
    """Generate workflow documentation."""
    from port.generator.workflow_generator import generate_workflow_doc
    try:
        content = generate_workflow_doc(comp_name, source_root)
        out_path = generate_root / "workflow.md"
        if dry_run:
            generated_files.append(str(out_path))
        else:
            write_file(content, out_path)
        generated_files.append(str(out_path.relative_to(root)))
    except Exception as e:
        click.echo(f"  ⚠ Could not generate workflow doc for '{comp_name}': {e}", err=True)


# ── validate ────────────────────────────────────────────────────────────


@main.command()
@click.option(
    "--generated", "-g", "generated_path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Path to generated directory (default: ./generated).",
)
@click.option("--tests", "run_tests", is_flag=True, help="Also run the original test suite.")
@click.option(
    "--test-path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to test suite (default: auto-discover from inventory).",
)
@click.pass_context
def validate(ctx: click.Context, generated_path: Path | None,
             run_tests: bool, test_path: Path | None) -> None:
    """Validate generated Claude Code artifacts."""
    from port.validator import run_validation, ValidationReport

    gpath = generated_path.resolve() if generated_path else Path.cwd() / "generated"
    if not gpath.exists():
        click.echo(f"Generated directory not found: {gpath}", err=True)
        sys.exit(1)

    click.echo(f"Validating generated artifacts in {gpath}")

    # Find inventory for test discovery
    inv_path = Path.cwd() / "component-inventory.yml"
    inventory_data = None
    if inv_path.exists():
        import yaml
        with inv_path.open("r", encoding="utf-8") as f:
            inventory_data = yaml.safe_load(f)

    report = run_validation(gpath, inventory_data=inventory_data,
                            run_tests=run_tests, test_path=test_path)

    # Print report
    click.echo(f"\n  {report.summary_str()}")

    if report.failed > 0:
        click.echo("  Some checks failed.", err=True)
        for r in report.results:
            if r.status == "fail":
                click.echo(f"    FAIL  {r.check}: {r.detail}", err=True)
        sys.exit(1)

    click.echo("  All checks passed.")


# ── run ─────────────────────────────────────────────────────────────────


@main.command()
@click.option("--all", "all_flag", is_flag=True, help="Run the full pipeline.")
@click.option(
    "--source", "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Source repo path (passed to init).",
)
@click.option(
    "--output", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory.",
)
@click.option("--force", is_flag=True, help="Overwrite existing files.")
@click.option("--tests", is_flag=True, help="Include test suite execution in validation.")
@click.pass_context
def run(ctx: click.Context, all_flag: bool, source: Path | None,
        output: Path | None, force: bool, tests: bool) -> None:
    """Run the full porting pipeline: init → generate → validate."""
    if not all_flag:
        click.echo("Pass --all to run the full pipeline.", err=True)
        sys.exit(2)

    root = output.resolve() if output else Path.cwd()

    if source is None:
        click.echo("--source is required when running --all", err=True)
        sys.exit(1)

    # 1. init
    click.echo("── Phase 1: Init ──────────────────────────────")
    ctx.invoke(init, source=source, output=root, force=force, verbose=True)

    # 2. generate
    plan_path = root / "porting-plan.yml"
    click.echo("\n── Phase 2: Generate ───────────────────────────")
    ctx.invoke(generate, plan_path=plan_path, output=root, only_phase=None, dry_run=False)

    # 3. validate
    click.echo("\n── Phase 3: Validate ──────────────────────────")
    generated_path = root / "generated"
    ctx.invoke(validate, generated_path=generated_path, run_tests=tests, test_path=None)

    click.echo("\n── Complete ───────────────────────────────────")
    click.echo(f"All phases finished. Output in {root}")


if __name__ == "__main__":  # pragma: no cover
    main()
