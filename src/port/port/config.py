"""Configuration for the Port CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PortConfig:
    """Configuration for a port CLI run.

    ``source_path`` is the only required field — the Copilot repository to port.
    Everything else has a sensible default.
    """

    source_path: Path
    inventory_file: str = "component-inventory.yml"
    plan_file: str = "porting-plan.yml"
    generate_dir: str = "generated"
    version: str = "0.2.0"
    root: Path = field(default_factory=Path.cwd)

    @property
    def inventory_path(self) -> Path:
        return self.root / self.inventory_file

    @property
    def plan_path(self) -> Path:
        return self.root / self.plan_file

    @property
    def generate_path(self) -> Path:
        return self.root / self.generate_dir

    @classmethod
    def from_dict(cls, data: dict[str, Any], root: Path) -> PortConfig:
        source_raw = data.get("source_path")
        if not source_raw:
            raise ValueError("source_path is required in port.config.yml")
        return cls(
            source_path=Path(source_raw).resolve(),
            inventory_file=str(data.get("inventory_file", cls.inventory_file)),
            plan_file=str(data.get("plan_file", cls.plan_file)),
            generate_dir=str(data.get("generate_dir", cls.generate_dir)),
            version=str(data.get("version", cls.version)),
            root=root,
        )


def load_config(path: str | Path | None = None) -> PortConfig:
    """Load Port CLI configuration.

    If *path* is given it is loaded as YAML.  Otherwise we look for
    ``port.config.yml`` in the current directory.  Missing file → error
    (source_path is required).
    """
    root = Path.cwd()
    if path is None:
        path = root / "port.config.yml"
    else:
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            f"Create a port.config.yml or pass --config explicitly."
        )

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return PortConfig.from_dict(data, root)


def make_default_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
