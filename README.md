<p align="right"><b>English</b> · <a href="README.zh.md">简体中文</a></p>

# 🎬 Vox Director

**Turn one topic into a finished Vox-style paper-collage explainer / ad video — script, collage keyframes, motion, voice-over, music and captions, all automated.**

This fork is **Codex-native**: Codex ImageGen creates the collage keyframes, a resumable handoff pack sends motion prompts and local reference images to SuperGrok/Grok Imagine, and local `ffmpeg` assembles the film. Atlas Cloud remains available as an optional automated provider route.

![License: MIT](https://img.shields.io/badge/License-MIT-black.svg) ![Codex Native](https://img.shields.io/badge/Codex-native-111827.svg) ![Atlas Optional](https://img.shields.io/badge/Atlas-optional-ff5a1f.svg) ![Agent Skill](https://img.shields.io/badge/Agent-Skill-d97757.svg)

https://github.com/user-attachments/assets/561788b1-5615-4828-b3f8-b24ae5ad7bcd

<p align="center">
  <em>▶ "Mexican street food" · 60s · landscape</em>
</p>

https://github.com/user-attachments/assets/ed08d230-7bcb-4b48-a17d-23c079208f9f

<p align="center">
  <em>▶ "The evolution of Chinese civilization" · 30s · landscape</em>
</p>

https://github.com/user-attachments/assets/f69f072f-f50a-41ba-9e66-7ed0aae4ddc0

<p align="center">
  <em>▶ "A brief history of money" · 60s · vertical</em>
</p>

---

## What it is

The look is the modern editorial **paper-collage** popularized by Vox explainers: hand-cut paper cut-outs, torn edges, tape, halftone dots, newspaper clippings, bold flat color per beat, big cut-out headlines — brought to life with motion, a narrator, music and captions.

## How it works

One topic flows through one script per stage, all driven by a single `beats.json` per project:

```
topic
  │
  ├─ 1. beat map        pick a narrative arc → write beats.json      ◀── GATE 1: you approve the beat map
  ├─ 2. style bake-off  Codex ImageGen renders 3–4 themes            ◀── GATE 2: you pick the look by eye
  ├─ 3. keyframes       Codex ImageGen creates each collage poster
  ├─ 4. motion          SuperGrok/Grok Imagine handoff per shot
  ├─ 5. voice + music   import local assets (or use Atlas optionally)
  ├─ 6. assemble        ffmpeg: concat, duck music under VO, burn captions + watermark
  └─ final.mp4
```

Two ideas make or break the result, and the skill is built around both:

1. **The look is born in the image step.** Each beat is a finished collage *poster*. All the collage DNA (torn paper, cut-outs, halftone, headline text) lives in that image — if the poster isn't a rich collage, nothing downstream saves it.
2. **The motion is added after.** By default an AI video model animates the whole poster (the "living poster" path). For dramatic *piece-by-piece* assembly, an optional local keyframe engine cuts the poster into parts and drives them frame-by-frame (no content filters, pixel-exact — great for real people).

Two human decision gates keep you in control (approve the beat map; pick the style); everything else is automated.

## Media routes

| Stage | Codex-native default | Optional Atlas automation |
|---|---|---|
| Style bake-off | Codex ImageGen | Nano Banana 2 |
| Keyframes | Codex ImageGen | Nano Banana 2 |
| Motion | SuperGrok/Grok Imagine handoff | Gemini Omni Flash or Kling |
| Voice + music | Local user-supplied assets | xAI TTS + MiniMax Music |
| Assembly | Local ffmpeg | Local ffmpeg |

The Codex route never asks for `OPENAI_API_KEY`; Codex calls its built-in ImageGen tool. The SuperGrok stage creates a handoff pack and never opens a browser or uploads files without a separate user request.

### Atlas models

| Job | Model |
|---|---|
| Keyframe / collage poster | `google/nano-banana-2/text-to-image` |
| Animate (non-real content) | `google/gemini-omni-flash/image-to-video` |
| Animate (**real people / brands**) | `kwaivgi/kling-video-o3-pro/image-to-video` |
| Narration | `xai/tts-v1` |
| Music | `minimax/music-2.6` |
| Cut out an element (advanced path) | `youchuan/v8.1/remove-background` |

Model IDs drift — the skill fetches the live list from `GET https://api.atlascloud.ai/api/v1/models` before running.

## Install

This is an **agent skill** — it works with coding agents that can read a workflow and run scripts. Claude Code and Codex use different discovery directories, so install it for the agent you use.

**Codex — global install (recommended):**
```bash
git clone https://github.com/hollowwx/vox-director.git ~/.codex/skills/vox-director
```

On Windows PowerShell:
```powershell
git clone https://github.com/hollowwx/vox-director.git "$HOME/.codex/skills/vox-director"
```

Restart Codex or open a new task after installation, then ask for a Vox-style
video. When working inside this repository, Codex also discovers the project
entry at [`.agents/skills/vox-director/SKILL.md`](.agents/skills/vox-director/SKILL.md).

**Claude Code:**
```bash
git clone https://github.com/hollowwx/vox-director.git ~/.claude/skills/vox-director
```

The cross-agent `~/.agents/skills/vox-director` path also works in environments that scan it. The packaged [`vox-director.skill`](vox-director.skill) remains a Claude skill package. Codex should clone the repository so `scripts/`, `references/`, and `assets/` stay beside `SKILL.md`.

No API key is required for the Codex-native keyframe and SuperGrok handoff route. Only when you explicitly choose Atlas automation, set an Atlas Cloud API key:
```bash
export ATLASCLOUD_API_KEY="sk-..."
```

On Windows PowerShell:
```powershell
$env:ATLASCLOUD_API_KEY = "sk-..."
```

## Quick start

Just ask your coding agent, with the skill installed:

> *"Make me a Vox-style collage video introducing Mexican street food — English, 16:9, 15 seconds."*

Codex runs `scripts/doctor.py`, drafts the beat map for approval, prepares an ImageGen style bake-off, generates keyframes, builds the SuperGrok handoff pack, and assembles returned clips plus local audio into `out/<project>/final.mp4`.

## Requirements

- **Codex** (recommended) or another coding agent that reads `SKILL.md`
- **ffmpeg** + **ffprobe** (`brew install ffmpeg`)
- **Python 3** with **Pillow** (`pip install pillow`) — for caption/watermark overlays
- **Atlas Cloud API key + curl** only for the optional Atlas route

For pinned toolchains, set trusted absolute paths with `VOX_FFMPEG`, `VOX_FFPROBE`, or `VOX_CURL`.

## What's in the box

```
SKILL.md              the skill (English) — the workflow the agent follows
SKILL.zh.md           the same skill in Chinese
AGENTS.md             entry point for non-Claude agents (Codex, …)
agents/openai.yaml     Codex UI metadata
.agents/skills/        project-scoped Codex discovery entry
references/           the creative engine
  codex-supergrok.md    Codex ImageGen + SuperGrok handoff contract
  prompt-guide.md       the LOOK layer — prompt structures, vocab & 8 theme presets
  beat-layer.md         14 narrative arcs + hook/pacing + shot patterns
  models-and-gotchas.md every API / ffmpeg gotcha, already solved
  local-engine.md       the advanced element-level motion engine
scripts/              one script per pipeline stage
examples/             ready-to-run beats.json examples
assets/               the showcase film
```

## Credits

Inspired by the collage-ad workflows of **[Stav Zilber](https://x.com/StavZilber)**, **[rom1trs](https://x.com/rom1trs)** and **[Higgsfield](https://x.com/higgsfield_ai)**, and by **[Vox](https://www.vox.com)**'s explainer visual language.

The original automated provider route was built on **[Atlas Cloud](https://www.atlascloud.ai/?utm_source=github&utm_campaign=vox_director)**. This fork adds the Codex-native route while preserving that fallback.

## License

[MIT](LICENSE) © 2026 Atlas Cloud
