---
name: vox-director
description: >
  Create a finished Vox-inspired paper-collage explainer or ad video from one
  topic with Codex ImageGen, a SuperGrok/Grok Imagine handoff, local media
  assets, and ffmpeg assembly; keep Atlas Cloud as an optional automation
  fallback. Use for Vox-style explainers, motion collages, paper collage ads,
  narrated scrapbook videos, and topic-to-video requests.
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

Follow the root workflow's Codex-native route by default. Translate shell
examples to the current platform:

- On Windows PowerShell, use `python` (or the configured workspace Python).
- On macOS/Linux, keep the documented Bash and `python3` commands.
- Run `scripts/doctor.py --json` before generating media.
- Do not request an Atlas key unless the user explicitly selects Atlas.
- Do not open Grok, control a browser, or upload media during handoff unless the
  user separately asks for browser automation.

Keep both human approval gates from the authoritative workflow. Do not call paid
media-generation APIs before the beat-map and visual-style approvals are given.
