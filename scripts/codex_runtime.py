#!/usr/bin/env python3
"""Cross-platform runtime checks shared by Codex and the media scripts."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class RuntimeDependencyError(RuntimeError):
    """Raised when a required local executable cannot be resolved."""


def resolve_executable(name: str) -> str:
    """Return an executable path from PATH or raise an actionable error."""
    override = os.environ.get(f"VOX_{name.upper()}")
    if override:
        override_path = Path(override)
        if not override_path.is_absolute():
            raise RuntimeDependencyError(f"VOX_{name.upper()} must be an absolute executable path.")
        if not override_path.is_file():
            raise RuntimeDependencyError(f"VOX_{name.upper()} does not point to a file: {override_path}")
        return str(override_path.resolve())

    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeDependencyError(
            f"Required executable '{name}' was not found on PATH. Install it and rerun scripts/doctor.py."
        )
    resolved_path = Path(resolved).resolve()
    repository_root = Path(__file__).resolve().parents[1]
    try:
        resolved_path.relative_to(repository_root)
    except ValueError:
        return str(resolved_path)
    raise RuntimeDependencyError(
        f"Refusing repository-local executable for '{name}': {resolved_path}. "
        f"Set VOX_{name.upper()} to an explicit trusted absolute path if this is intentional."
    )


def inspect_environment(
    *, env: Mapping[str, str] | None = None, require_api_key: bool = False
) -> dict[str, Any]:
    """Inspect local dependencies without making network or billable API calls."""
    environment = os.environ if env is None else env
    checks: dict[str, dict[str, str]] = {}
    missing_required = False

    python_ok = sys.version_info >= (3, 10)
    checks["python"] = {
        "status": "ok" if python_ok else "missing",
        "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    missing_required |= not python_ok

    pillow_ok = importlib.util.find_spec("PIL") is not None
    checks["pillow"] = {
        "status": "ok" if pillow_ok else "missing",
        "detail": "Python package PIL/Pillow",
    }
    missing_required |= not pillow_ok

    for executable in ("ffmpeg", "ffprobe", "curl"):
        resolved = shutil.which(executable)
        required = executable != "curl" or require_api_key
        checks[executable] = {
            "status": "ok" if resolved else ("missing" if required else "optional"),
            "detail": resolved or "not found on PATH",
        }
        missing_required |= required and resolved is None

    offline_ready = not missing_required
    has_key = bool(environment.get("ATLASCLOUD_API_KEY"))
    key_status = "ok" if has_key else ("missing" if require_api_key else "optional")
    checks["atlas_api_key"] = {
        "status": key_status,
        "detail": "set" if has_key else "not set",
    }
    missing_required |= require_api_key and not has_key

    atlas_ready = offline_ready and has_key and checks["curl"]["status"] == "ok"
    return {
        "ok": offline_ready and (has_key or not require_api_key),
        "offline_ready": offline_ready,
        "production_ready": atlas_ready,
        "checks": checks,
    }
