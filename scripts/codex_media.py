#!/usr/bin/env python3
"""Prepare and track Codex ImageGen and SuperGrok media tasks."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

from clips import collage_prompt, painterly_prompt
from keyframes import shots_of
from styles import compose_collage_prompt, compose_keyframe_prompt, resolve_theme


MANIFEST_NAME = "codex-media.json"
DEFAULT_BAKEOFF_STYLES = ("american-retro", "swiss-modern", "punk-zine", "atomic-age")
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def _safe_identifier(value: object) -> str:
    """Return a filename-safe manifest identifier or reject unsafe project input."""
    identifier = str(value)
    if not SAFE_IDENTIFIER.fullmatch(identifier):
        raise ValueError(f"Unsafe media identifier: {identifier!r}")
    return identifier


def _stage_output(project: Path, folder: str, filename: str) -> Path:
    """Resolve an output path and enforce containment in its project stage directory."""
    project_root = project.resolve()
    stage_dir = (project_root / folder).resolve()
    try:
        stage_dir.relative_to(project_root)
    except ValueError as error:
        raise ValueError(f"Project stage directory escapes project root: {stage_dir}") from error
    output = (stage_dir / filename).resolve()
    try:
        output.relative_to(stage_dir)
    except ValueError as error:  # pragma: no cover - filename validation should catch this first
        raise ValueError(f"Output escapes project stage directory: {output}") from error
    return output


def _read_document(project_dir: Path) -> dict[str, Any]:
    beats_path = project_dir / "beats.json"
    if not beats_path.is_file():
        raise FileNotFoundError(f"Missing project file: {beats_path}")
    return json.loads(beats_path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _keyframe_prompt(document: dict[str, Any], beat: dict[str, Any], shot: dict[str, Any]) -> str:
    aspect = document.get("aspect", "16:9")
    style = document.get("style", "painterly")
    if style != "collage":
        return compose_keyframe_prompt(
            document.get("era"), shot["scene"], beat["title_cn"], beat["title_en"], aspect
        )

    theme = resolve_theme(document.get("theme")) or {}
    return compose_collage_prompt(
        shot["scene"],
        beat["title_cn"],
        beat["title_en"],
        beat.get("bg", "warm ochre"),
        aspect,
        with_title=shot.get("title", True),
        style=theme.get("idiom") or document.get("collage_style", "american-retro"),
        palette=theme.get("palette") or document.get("palette"),
        type_style=theme.get("type_style") or document.get("type_style"),
        finish=theme.get("finish") or document.get("finish"),
    )


def _supergrok_prompt(document: dict[str, Any], beat: dict[str, Any], shot: dict[str, Any]) -> str:
    camera = shot.get("camera_move") or shot.get("motion", "push_in")
    if document.get("style", "painterly") != "collage":
        return painterly_prompt(shot.get("motion", camera))

    theme = resolve_theme(document.get("theme")) or {}
    return collage_prompt(
        camera,
        element_motion=shot.get("element_motion"),
        feel=beat.get("feel"),
        palette=beat.get("bg"),
        amplitude=document.get("motion_style") or theme.get("motion_style", "punchy"),
        has_title=shot.get("title", True),
        constraints=document.get("constraints", "strict"),
    )


def _previous_statuses(manifest_path: Path, stage: str) -> dict[str, str]:
    if not manifest_path.is_file():
        return {}
    previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    if previous.get("stage") != stage:
        return {}
    return {task["key"]: task.get("status", "pending") for task in previous.get("tasks", [])}


def prepare_manifest(
    project_dir: str | Path,
    *,
    stage: str,
    styles: list[str] | tuple[str, ...] | None = None,
    beat_index: int = 0,
) -> dict[str, Any]:
    """Create a resumable task manifest for a Codex-native media stage."""
    if stage not in {"bakeoff", "keyframes", "supergrok"}:
        raise ValueError("stage must be 'bakeoff', 'keyframes', or 'supergrok'")

    project = Path(project_dir).resolve()
    document = _read_document(project)
    manifest_path = project / MANIFEST_NAME
    previous_statuses = _previous_statuses(manifest_path, stage)
    tasks: list[dict[str, Any]] = []

    if stage == "bakeoff":
        beat = document["beats"][beat_index]
        shot = next(shots_of(beat))[0]
        for raw_name in styles or DEFAULT_BAKEOFF_STYLES:
            name = _safe_identifier(raw_name)
            candidate_document = {**document, "theme": name}
            output = _stage_output(project, "style-bakeoff", f"{name}.png")
            tasks.append(
                {
                    "key": name,
                    "provider": "codex-imagegen",
                    "aspect": document.get("aspect", "16:9"),
                    "prompt": _keyframe_prompt(candidate_document, beat, shot),
                    "output_path": str(output),
                    "status": "complete" if output.is_file() else previous_statuses.get(name, "pending"),
                }
            )

    for beat in document["beats"] if stage != "bakeoff" else []:
        for shot, key in shots_of(beat):
            key = _safe_identifier(key)
            if stage == "keyframes":
                output = _stage_output(project, "keyframes", f"kf_{key}.png")
                task = {
                    "key": key,
                    "provider": "codex-imagegen",
                    "aspect": document.get("aspect", "16:9"),
                    "prompt": _keyframe_prompt(document, beat, shot),
                    "output_path": str(output),
                    "status": "complete" if output.is_file() else previous_statuses.get(key, "pending"),
                }
            else:
                keyframe_value = shot.get("keyframe_path")
                keyframe = Path(keyframe_value).resolve() if keyframe_value else None
                output = _stage_output(project, "clips", f"clip_{key}.mp4")
                trim_to = int(shot.get("dur", 6))
                generation_duration = max(6, trim_to)
                motion_prompt = _supergrok_prompt(document, beat, shot)
                motion_prompt += (
                    f"\nTIMING: Create one {generation_duration}-second continuous shot. Start the motion "
                    f"immediately, complete the main action by second {generation_duration - 2}, then hold "
                    "the final composition perfectly stable for the last 2 seconds so the editor can trim it."
                )
                task = {
                    "key": key,
                    "provider": "supergrok",
                    "input_path": str(keyframe) if keyframe else None,
                    "prompt": motion_prompt,
                    "duration": generation_duration,
                    "trim_to": trim_to,
                    "output_path": str(output),
                    "status": (
                        "complete"
                        if output.is_file()
                        else previous_statuses.get(key, "pending")
                        if keyframe and keyframe.is_file()
                        else "blocked"
                    ),
                }
            tasks.append(task)

    manifest = {
        "project": document.get("project", project.name),
        "stage": stage,
        "tasks": tasks,
    }
    _write_json(manifest_path, manifest)
    return manifest


def select_style(project_dir: str | Path, theme: str) -> None:
    """Persist the human-approved theme in beats.json."""
    project = Path(project_dir).resolve()
    document = _read_document(project)
    selected = _safe_identifier(theme)
    document["theme"] = selected
    document["collage_style"] = selected
    _write_json(project / "beats.json", document)


def record_output(project_dir: str | Path, *, stage: str, key: str, output_path: str | Path) -> None:
    """Record one generated artifact in beats.json and the active manifest."""
    project = Path(project_dir).resolve()
    output = Path(output_path).resolve()
    if not output.is_file():
        raise FileNotFoundError(f"Generated output does not exist: {output}")
    if output.is_symlink():
        raise ValueError(f"Generated output must not be a symlink: {output}")

    safe_key = _safe_identifier(key)
    manifest_path = project / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("stage") != stage:
        raise ValueError(f"Active manifest stage is {manifest.get('stage')!r}, not {stage!r}")
    manifest_task = next((task for task in manifest["tasks"] if task["key"] == safe_key), None)
    if manifest_task is None:
        raise KeyError(f"Unknown manifest task: {safe_key}")

    document = _read_document(project)
    matched_shot: dict[str, Any] | None = None
    if stage != "bakeoff":
        for beat in document["beats"]:
            for shot, shot_key in shots_of(beat):
                if _safe_identifier(shot_key) == safe_key:
                    matched_shot = shot
                    break
        if matched_shot is None:
            raise KeyError(f"Unknown shot key: {safe_key}")

    destinations = {
        "bakeoff": _stage_output(project, "style-bakeoff", f"{safe_key}.png"),
        "keyframes": _stage_output(project, "keyframes", f"kf_{safe_key}.png"),
        "supergrok": _stage_output(project, "clips", f"clip_{safe_key}.mp4"),
    }
    if stage not in destinations:
        raise ValueError(f"Unknown stage: {stage}")
    destination = destinations[stage]
    if output != destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, destination)
    output = destination

    if matched_shot is not None:
        matched_shot["keyframe_path" if stage == "keyframes" else "clip_path"] = str(output)
        _write_json(project / "beats.json", document)
    manifest_task["status"] = "complete"
    manifest_task["output_path"] = str(output)
    _write_json(manifest_path, manifest)


def build_parser() -> argparse.ArgumentParser:  # pragma: no cover - CLI wiring
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="write codex-media.json")
    prepare.add_argument("project_dir")
    prepare.add_argument("--stage", choices=("bakeoff", "keyframes", "supergrok"), required=True)
    prepare.add_argument("--styles", help="comma-separated bake-off themes")
    prepare.add_argument("--beat-index", type=int, default=0)

    record = subparsers.add_parser("record", help="record one completed artifact")
    record.add_argument("project_dir")
    record.add_argument("--stage", choices=("bakeoff", "keyframes", "supergrok"), required=True)
    record.add_argument("--key", required=True)
    record.add_argument("--output", required=True)

    select = subparsers.add_parser("select-style", help="write the approved theme to beats.json")
    select.add_argument("project_dir")
    select.add_argument("--theme", required=True)
    return parser


def main() -> int:  # pragma: no cover - exercised by CLI smoke tests
    args = build_parser().parse_args()
    if args.command == "prepare":
        manifest = prepare_manifest(
            args.project_dir,
            stage=args.stage,
            styles=args.styles.split(",") if args.styles else None,
            beat_index=args.beat_index,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    elif args.command == "record":
        record_output(args.project_dir, stage=args.stage, key=args.key, output_path=args.output)
        print(f"recorded {args.stage} {args.key}: {Path(args.output).resolve()}")
    else:
        select_style(args.project_dir, args.theme)
        print(f"selected theme: {args.theme}")
    return 0


if __name__ == "__main__":  # pragma: no cover - covered by subprocess smoke tests
    raise SystemExit(main())
