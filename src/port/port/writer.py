"""Writer helpers: atomic file / YAML output."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml


def ensure_dir(path: Path) -> Path:
    """Create parent directories for *path* if they don't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_file(content: str, path: Path, atomic: bool = True) -> None:
    """Write *content* to *path*, optionally atomically."""
    ensure_dir(path)
    if atomic:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
    else:
        path.write_text(content, encoding="utf-8")


def write_yaml(data: Any, path: Path, atomic: bool = True) -> None:
    """Serialize *data* as YAML and write to *path*."""
    content = yaml.safe_dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    write_file(content, path, atomic=atomic)
