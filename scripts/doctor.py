#!/usr/bin/env python3
"""Diagnose Vox Director's local Codex runtime without calling Atlas Cloud."""

from __future__ import annotations

import argparse
import json

from codex_runtime import inspect_environment


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument(
        "--require-api-key",
        action="store_true",
        help="fail when ATLASCLOUD_API_KEY is not set",
    )
    return parser


def main() -> int:
    """Print the runtime report and return nonzero only for required failures."""
    args = build_parser().parse_args()
    report = inspect_environment(require_api_key=args.require_api_key)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Vox Director Codex runtime")
        for name, check in report["checks"].items():
            print(f"- {name}: {check['status']} ({check['detail']})")
        print(f"offline_ready: {str(report['offline_ready']).lower()}")
        print(f"production_ready: {str(report['production_ready']).lower()}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke tests
    raise SystemExit(main())
