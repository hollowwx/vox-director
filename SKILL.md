---
name: vox-director
description: >
  Turn ONE topic into a finished Vox-style paper-collage explainer / ad video with a
  Codex-native workflow: Codex ImageGen keyframes, SuperGrok/Grok Imagine motion handoff,
  local audio assets, and ffmpeg assembly. Atlas Cloud remains an optional automated
  fallback. Use this whenever the user wants a "Vox style" video,
  a paper/torn-paper collage animation, a "motion collage", a narrated explainer or short
  ad built from AI-generated collage posters, a scrapbook-style tribute, or wants to turn
  a topic / product / person into a punchy narrated collage video — even if they don't say
  the word "Vox". Also use when reproducing Stav Zilber / rom1trs / Higgsfield-style collage
  ad workflows, or when the user asks for a motion collage or a scrapbook-style tribute.
  Triggers: "vox video", "collage video", "motion collage", "paper collage
  explainer", "make a collage ad", "turn this topic into a collage video".
---

# Vox Director

Turn a one-line topic into a finished **Vox-style paper-collage video**: a bold, punchy,
narrated explainer/ad where each beat is a torn-paper collage poster that comes alive, with
voice-over, music and captions. The default Codex route needs local **ffmpeg** and no Atlas
key. Atlas remains available for optional provider-generated media.

The look is the modern editorial paper-collage popularized by Vox explainers and creators
like Stav Zilber / rom1trs: hand-cut paper cut-outs, torn edges, tape, halftone dots,
newspaper clippings, bold flat color per beat, big cut-out headlines.

## The core idea (read this first)

The Vox collage look and the collage motion are **two different steps**:

1. **The look is born in the IMAGE step.** Each beat is a finished collage *poster* made by a
   text-to-image model. All the collage DNA (torn paper, cut-outs, halftone, bold color,
   headline text) lives in that image. If the image isn't a rich collage, nothing downstream
   will save it.
2. **The motion is added after.** By default an AI video model animates the whole poster (the
   "living poster" path — simple, automated). For dramatic *piece-by-piece* assembly you cut
   the poster into parts and drive them with the local keyframe engine (advanced path).

Everything hinges on the prompts. **Before writing any image or video prompt, read
`references/prompt-guide.md`** — it has the exact prompt structures that make the difference
between "a real Vox collage" and "a moving PowerPoint".

## Codex runtime contract

Run every command from the skill root. Use `python` on Windows PowerShell and usually `python3`
on macOS/Linux. In the commands below, `<python>` means the interpreter available in the current
environment.

Before drafting or generating anything, run `<python> scripts/doctor.py --json`. This checks
Python, Pillow, ffmpeg, ffprobe, and curl without network access or billable calls. Fix every
missing required dependency before continuing. An absent Atlas key is allowed during planning
and offline validation.

Only when using the optional Atlas provider, run `<python> scripts/doctor.py --require-api-key`
immediately before its first call. Codex ImageGen and SuperGrok do not require an Atlas key. Read
`references/codex-supergrok.md` before running either stage.

## Standard workflow (topic → film)

This is the default, most-automated path. Every stage is one script, all driven by a single
`beats.json` per project under `out/<project>/`.

1. **Topic → beat map.** First **read `references/beat-layer.md`** (the story layer) and pick a
   narrative `arc` that fits the topic (`timeline` for history, `pas`/`bab` for ads,
   `how_it_works` for explainers, `man_in_hole` for transformations, …). Then write
   `out/<project>/beats.json` following that arc: **beat-1 headline must be a ≤3s hook**; beat
   count per duration (30s→6–8, 60s→10–12); split each beat into **2 shots** (wide+detail) with
   **per-shot `camera_move` VARIED across adjacent beats** (never repeat; `static` on the payoff)
   and **rich `element_motion`** (see step 4). Each beat: `narration`, `title_cn`/`title_en`,
   `scene`, `bg`, `feel`, `hook`. This draft is the **one mandatory approval gate** — show the
   user the beat map before generating. Examples in `examples/`.

2. **Pick the visual style (hybrid — do this BEFORE keyframes).** Do not reuse one house style
   for every topic. Read `references/prompt-guide.md` (§5 theme presets); pick 3–4 **theme presets**
   (`styles.THEME_PRESETS`: `american-retro`, `swiss-modern`, `punk-zine`,
   `soviet-constructivist`, `wpa-propaganda`, `70s-groovy`, `chinese-ink`, `atomic-age`) that fit
   the topic's era/culture/tone — **or compose a custom theme** by mixing the prompt-guide dimensions
   (medium/era/palette/type/finish) when none fit. Match the topic, **not** the language (an
   English film on Chinese history should look Chinese). A theme bundles the whole LOOK layer
   (idiom+palette+type+finish+mood+motion). Run a bake-off and let the user pick by eye — AI
   proposes, the library is the quality floor, the human decides. Prepare Codex ImageGen tasks:
   `<python> scripts/codex_media.py prepare out/<project> --stage bakeoff --styles
   american-retro,swiss-modern,punk-zine,atomic-age`. Generate and record the candidates, show
   them to the user, then persist the approved theme with `<python> scripts/codex_media.py
   select-style out/<project> --theme <pick>`.

3. **Keyframes with Codex ImageGen (default).** Run
   `<python> scripts/codex_media.py prepare out/<project> --stage keyframes`. For every `pending`
   task in `codex-media.json`, call built-in ImageGen with its prompt, copy the selected PNG to
   `output_path`, inspect it, and record it with `<python> scripts/codex_media.py record
   out/<project> --stage keyframes --key <key> --output <path>`. Do not use the Image API CLI or
   ask for `OPENAI_API_KEY` unless the user explicitly requests that fallback.

4. **SuperGrok handoff pack (default).** Run
   `<python> scripts/codex_media.py prepare out/<project> --stage supergrok`. Do not open Grok or
   upload anything. Give the user each task's local `input_path` image together with its exact
   prompt and duration, grouped by shot key. Render the reference images inline when possible and
   keep the files in the project. The user performs image-to-video generation in SuperGrok.
   Because Grok Imagine I2V has a 6-second minimum, two short A/B shots may be delivered as one
   Multi-Image storyboard: upload A as `@image1`, B as `@image2`, then allocate the six seconds
   explicitly (default 3s A + 1s transition + 2s B). Use this only when the images have a coherent
   visual progression; retain separate single-image fallbacks for disruptive scene changes.
   Motion prompts use two independent axes:
   • **`camera_move`** — ONE move per shot. Safe/default: `{static, push_in, pull_out, pan, tilt,
     parallax}`. **Bold/experimental** `{orbit, dolly_zoom, roll, whip}` are **available, not
     banned** — they can warp the flat art, so pair with `constraints: loose` and **re-roll**.
     Any custom phrase also passes through.
   • **`element_motion`** — where the energy lives; **AI writes it per beat to fit that scene** (not a
     template). Make it RICH (several elements moving) — be bold. A **hero element flying across
     the frame** (paper bird/plane/coins) is a great **occasional** punch on a key beat, **not
     every shot** (a flyer in every frame reads as a formula).
   `motion_style` = amplitude `calm | punchy | max` (the theme sets a default). **`constraints`**
   = `strict` (default: defect guards on — flat-2D, one-way, no-morph; best for clean text-heavy
   explainers) or `loose` (let the model explore 3D/bold moves; re-roll the misses). **Headline
   text is hard-protected only on shots that have a title** (detail shots without a headline are
   free to go wild).

   **Atlas fallback:** run `<python> scripts/keyframes.py out/<project>` and
   `<python> scripts/clips.py out/<project>` only when the user explicitly selects Atlas and has
   configured `ATLASCLOUD_API_KEY`.

5. **Voice + music.** The Codex-native route accepts local assets: one narration file per beat
   recorded as `narration_audio`, plus project-level `bgm_path`. Help the user prepare or import
   them, but do not invent a cloud provider or request a key. If the user explicitly selects
   Atlas, run `<python> scripts/audio.py out/<project>` for provider-generated narration and BGM.

6. **Assemble.** `<python> scripts/assemble.py out/<project>`
   ffmpeg: normalize + concat all shots, lay the single narration ducked under the music,
   burn captions timed per beat, add the watermark. Output `out/<project>/final.mp4`.

7. **Verify.** You can't read an mp4 directly — extract frames to jpg and look:
   `ffmpeg -ss <t> -i final.mp4 -vf "scale=640:-1,format=yuvj420p" -frames:v 1 f.jpg`

### Cadence — how long shots should be

A common mistake is one long shot per beat. On a 9:16 / social piece especially, a static
10s shot reads as dead air. Aim for a **cut every ~4–6 seconds**:

- **Shots run 3–6s; never let a single shot exceed ~7s** — beyond that the AI motion has
  nowhere to go and it feels static.
- **A beat's narration is ~8–10s, so give each beat 2 shots** (a *wide* establishing shot with
  the headline + a *detail* cut-in without it). The narration plays continuously across both;
  the visual cuts mid-sentence. This is the single biggest rhythm win.
- So a ~60s film is typically **~6 beats × 2 shots × ~5s = 12 shots**, not 6 × 10s.
- Reuse the wide keyframe as shot `a`; generate a tighter detail scene for shot `b`.
  `keyframes.py` skips any shot that already has a `keyframe_url`, so adding `b` shots and
  re-running only generates the new ones.

Add a `shots` array to each beat (see schema). Give each shot its own short `scene` and
`motion`; set `"title": true` only on the wide shot so the headline shows once per beat.

## beats.json schema

```json
{
  "project": "my-film", "topic": "...", "language": "en",
  "aspect": "9:16",                       // 16:9 | 9:16 | 1:1 | 3:4
  "style": "collage",
  "provider": "codex",                    // codex | atlas_cloud
  "theme": "american-retro",              // THEME_PRESET (styles.THEME_PRESETS) — the LOOK layer
  "arc": "timeline",                      // narrative arc (beat-layer.md) — the STORY skeleton
  "video_model": "google/gemini-omni-flash/image-to-video",  // Kling for real people
  "motion_style": "punchy",               // amplitude: calm | punchy | max (theme sets a default)
  "constraints": "strict",                // strict = defect guards on | loose = let AI explore + re-roll
  "voice": {"voice_id": "leo", "language": "en", "speed": 1.0},
  "music": "epic cinematic orchestral, instrumental, no vocals",
  "mix": {"music": 0.6, "voice": 1.25},   // audio balance — optional; these are the defaults (BGM ducks under the VO)
  "watermark": "vox-director",
  "beats": [
    {
      "id": 1, "title_cn": "", "title_en": "BEFORE MONEY",
      "bg": "earthy clay tan", "feel": "ancient, humble", "hook": "surprising_stat",
      "narration": "For most of history, there was no money...",
      "shots": [
        // shot_size: EST_WIDE|WIDE|MEDIUM|CLOSE|DETAIL ; camera_move: static|push_in|
        // pull_out|pan|tilt|parallax (flat-safe only) — VARY per adjacent beat, static for payoff
        {"id": "a", "dur": 5, "title": true,  "shot_size": "WIDE", "camera_move": "push_in",
         "scene": "...wide establishing collage...",
         "element_motion": "traders gesture, goat bobs, a paper bird flaps across the frame, coins scatter"},
        {"id": "b", "dur": 5, "title": false, "shot_size": "CLOSE", "camera_move": "parallax",
         "scene": "...close cut-in detail...",
         "element_motion": "the exchanged goods slide together, halftone pulses"}
      ]
    }
  ]
}
```
`theme`+`arc` set the two big layers; `element_motion` per shot is the energy (make it rich — see
below). `motion`/`collage_style`/`era` are still read for back-compat.

## Model selection (always verify IDs live)

Model IDs change — fetch the live list first: `GET https://api.atlascloud.ai/api/v1/models`
(no auth; keep only `display_console: true`). Defaults that work today:

| Job | Model | Note |
|---|---|---|
| Keyframe / collage poster | `google/nano-banana-2/text-to-image` | renders CN+EN text well |
| Cut out an element | `youchuan/v8.1/remove-background` | advanced path only |
| Animate (non-real content) | `google/gemini-omni-flash/image-to-video` | keeps text stable, layered motion |
| Animate (**real people / brands**) | `kwaivgi/kling-video-o3-pro/image-to-video` | Omni & Seedance BLOCK celebrities |
| Narration | `xai/tts-v1` | clean, multilingual, `voice_id` |
| Music | `minimax/music-2.6` | `is_instrumental: true` |

See `references/models-and-gotchas.md` for the full model-choice reasoning and every
API / ffmpeg gotcha (auth header, curl downloads, no-libass captions, content blocks, etc.).
Read it before debugging any failure — most failures are already documented there.

**Media routes are explicit.** `"provider": "codex"` uses `scripts/codex_media.py` to build
resumable manifests for built-in ImageGen and the manual SuperGrok handoff. `"provider":
"atlas_cloud"` uses the legacy provider scripts for automated submit/poll/download and requires
`ATLASCLOUD_API_KEY`. Never silently switch routes or incur provider cost.

## Advanced: element-level motion collage

The standard path animates the *whole* poster (great, automated, "living poster"). For the
dramatic **pieces-fly-in-and-assemble** motion collage (à la cr7v2), or to animate **real
people with full control and zero content filters**, cut each poster into independent
elements and drive them with the local keyframe engine (no video model needed).

Read `references/local-engine.md`. In short: `extract_elements.py` (crop + background-removal
+ residue/erase cleanup) → `motion.py` (Layer + keyframes, `fly_in`/`slap`/`drop`/`pop_settle`
easings, procedural confetti/starburst, camera zoom+shake+whip, frame render). Pieces fly
back to their **original positions** on a blurred-placeholder backdrop, so the assembled
frame reconstructs the original poster.

## Editions

- **Codex-native (default):** ImageGen keyframes, SuperGrok handoff, local audio, and ffmpeg
  assembly. This resumable route requires no Atlas key.
- **Atlas automation (optional):** provider-generated keyframes, clips, voice, and music when the
  user explicitly selects Atlas and supplies `ATLASCLOUD_API_KEY`.
- **Prompt pack:** beat map plus image, motion, and narration prompts for any external generator.
