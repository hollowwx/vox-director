---
name: vox-director
description: >
  Create a finished Vox-inspired paper-collage explainer or ad video from one
  topic using the repository workflow, Atlas Cloud media generation, and local
  ffmpeg assembly. Use for Vox-style explainers, motion collages, paper collage
  ads, narrated scrapbook videos, and topic-to-video requests.
---

# Vox Director for Codex

This is the Codex discovery entry for the repository's complete Vox Director
skill. The root workflow remains the single source of truth.

Before taking any production action:

1. Resolve the repository root from this file as `../../..`.
2. Read [`../../../SKILL.md`](../../../SKILL.md) completely and follow it as the
   authoritative workflow.
3. Read only the root `references/` files required by that workflow.
4. Run the root `scripts/` commands from the repository root so relative paths
   and `out/<project>/` remain consistent.

Translate the authoritative workflow's shell examples to the current platform:

- On Windows PowerShell, use `$env:ATLASCLOUD_API_KEY`, `Get-Command`, and
  `python` (or the configured workspace Python) instead of Bash `export`,
  `command -v`, and `python3`.
- On macOS/Linux, keep the documented Bash and `python3` commands.
- Resolve `ffmpeg`, `ffprobe`, Python, and Pillow before generating media.

Keep both human approval gates from the authoritative workflow. Do not call paid
media-generation APIs before the beat-map and visual-style approvals are given.
