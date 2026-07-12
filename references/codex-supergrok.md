# Codex ImageGen + SuperGrok workflow

## Trusted local tools

`scripts/doctor.py` resolves `ffmpeg`, `ffprobe`, and optional `curl` from `PATH`. Provider mode
refuses executables placed inside the repository. To pin trusted binaries explicitly, set absolute
paths with `VOX_FFMPEG`, `VOX_FFPROBE`, or `VOX_CURL` before running the relevant script.

## Style bake-off

1. Run `python scripts/codex_media.py prepare out/<project> --stage bakeoff --styles
   american-retro,swiss-modern,punk-zine,atomic-age`.
2. Generate only the `pending` ImageGen tasks, record each output with `--stage bakeoff`, and
   show every candidate to the user in one comparison.
3. After the user chooses, run `python scripts/codex_media.py select-style out/<project>
   --theme <pick>`. Do not infer approval from silence.

## Keyframes

1. Run `python scripts/codex_media.py prepare out/<project> --stage keyframes`.
2. Read `out/<project>/codex-media.json` and process only `pending` tasks.
3. Call built-in ImageGen once per task with the exact prompt. Do not use the Image API CLI and
   do not request `OPENAI_API_KEY` for this path.
4. Copy the selected generated image into the exact `output_path`.
5. Inspect composition, collage layering, text, aspect ratio, and artifacts. Re-generate only the
   failed task.
6. Run `python scripts/codex_media.py record out/<project> --stage keyframes --key <key>
   --output <output_path>`.

## SuperGrok handoff

1. Run `python scripts/codex_media.py prepare out/<project> --stage supergrok`.
2. Stop on `blocked` tasks because their local keyframe is missing. Process only `pending` tasks.
3. Do not open Grok, control a browser, upload files, or submit generations unless the user later
   explicitly asks for browser automation.
4. Present each task as one handoff unit: shot key, duration, local reference-image path, inline
   image preview when supported, and the exact motion prompt in a copyable code block.
5. Keep the ordering from `codex-media.json` so reference images and prompts cannot be mismatched.
6. The user uploads the reference image and prompt to SuperGrok manually.

### Six-second Multi-Image storyboard mode

When SuperGrok's minimum I2V duration is 6 seconds and a beat has two short shots, prefer one
Multi-Image generation using the A and B keyframes as `@image1` and `@image2`. Treat the spare
second explicitly as transition time: 3 seconds on A, 1 second transitioning, and 2 seconds on B.
Do not claim that 3 + 2 equals 6. Preserve both source compositions and forbid texture morphing.

Use paired generation when the two shots form a clear visual progression. For large semantic or
compositional jumps, provide a paired experimental prompt plus the original single-image fallback.
Always state upload order because swapping the images reverses the storyboard.

## Recovery

- Treat `codex-media.json` as the active checkpoint. `complete` tasks are immutable by default.
- Re-run `prepare` after editing `beats.json`; existing output files remain complete.
- Do not mark a SuperGrok task complete until the user later returns a corresponding clip.
- When the user supplies clips, record each one with `python scripts/codex_media.py record
  out/<project> --stage supergrok --key <key> --output <clip_path>`.

## Local audio contract

The Codex-native route does not assume an audio-generation API. Put each narration file on its
beat as `narration_audio` and set project-level `bgm_path` before assembly. Use WAV, MP3, M4A, or
another ffmpeg-readable format. Run `scripts/audio.py` only after the user explicitly selects the
Atlas provider and supplies its key.
