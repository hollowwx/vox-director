#!/usr/bin/env python3
"""Validate the repository's native Codex skill layout without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_SKILL = ROOT / ".agents" / "skills" / "vox-director" / "SKILL.md"
REQUIRED_ROOT_PATHS = (
    ROOT / "SKILL.md",
    ROOT / "AGENTS.md",
    ROOT / "scripts",
    ROOT / "references",
    ROOT / "assets",
)


def validate() -> list[str]:
    """Return human-readable validation failures for the Codex packaging."""
    errors = [f"missing required path: {path.relative_to(ROOT)}" for path in REQUIRED_ROOT_PATHS if not path.exists()]

    if not CODEX_SKILL.is_file():
        errors.append("missing native Codex entry: .agents/skills/vox-director/SKILL.md")
        return errors

    text = CODEX_SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("Codex SKILL.md must start with YAML frontmatter")
    if not re.search(r"(?m)^name:\s*vox-director\s*$", text):
        errors.append("Codex SKILL.md must declare name: vox-director")
    if not re.search(r"(?m)^description:\s*(?:>?\s*$|\S)", text):
        errors.append("Codex SKILL.md must declare a description")
    if "../../../SKILL.md" not in text:
        errors.append("Codex entry must route to the root SKILL.md single source of truth")

    return errors


def main() -> int:
    """Print validation results and return a shell-friendly status code."""
    errors = validate()
    if errors:
        print("Codex skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Codex skill layout is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
