---
name: vox-director
description: >
  把一个主题变成成品 Vox 纸片拼贴讲解/广告视频。默认走 Codex 原生流程：Codex ImageGen
  生成关键帧、SuperGrok/Grok Imagine 交付动效、本地音频素材与 ffmpeg 合成；Atlas Cloud
  保留为可选自动化备用路径。当用户想做「Vox 风格」视频、纸片/撕纸拼贴
  动画、「motion collage」、用 AI 生成的拼贴海报做旁白讲解或短广告、剪贴簿式致敬片,或想把一个
  主题/产品/人物变成有冲击力的旁白拼贴视频时使用——即使没说「Vox」也用。也用于复刻 Stav Zilber
  / rom1trs / Higgsfield 式拼贴广告工作流,或用户提到 拼贴动效视频 / 剪贴簿视频 / 拼贴广告 /
  motion collage。触发词:「vox video」「collage video」「拼贴视频」「拼贴动效」「剪贴簿」
  「paper collage explainer」「做个拼贴广告」「把这个主题做成拼贴视频」。
---

# Vox Director(中文版)

把一句话主题变成一条成品 **Vox 纸片拼贴视频**:大胆、有冲击力、带旁白的讲解/广告片,每一段都是
一张会动的撕纸拼贴海报,配旁白、配乐、字幕。默认 Codex 路径只需本地 **ffmpeg**，不要求
Atlas key；需要 provider 自动生成媒体时再选择 Atlas Cloud。

风格 = Vox 讲解片和 Stav Zilber / rom1trs 带火的现代编辑感纸片拼贴:手撕纸边、胶带、半调网点、
报纸剪报、每段一块大胆平涂色底、大号剪贴标题。

## 核心思路(先读这段)

Vox 拼贴的**样子**和**动效**是两件事、两步:

1. **样子诞生在「生图」这一步。** 每段是一张文生图模型做的成品拼贴*海报*,所有拼贴 DNA(撕纸、剪贴、
   半调、大胆色、标题字)都在这张图里。图不到位,后面全白搭。
2. **动效是之后加的。** 默认让 AI 视频模型动整张海报(「会动的海报」,简单自动)。要那种零件逐个飞入
   组装的更炸效果,才把海报拆件、用本地关键帧引擎驱动(高阶路线)。

一切成败在提示词。**写任何生图/生视频 prompt 前,先读 `references/prompt-guide.md`**——它有把
「真·Vox 拼贴」和「会动的 PPT」区分开的精确 prompt 结构。两个"库"文件:`prompt-guide.md`(画面/LOOK
层:生图5段 + 生视频轴 + 词库 + 8 套主题预置)、`beat-layer.md`(故事/STORY 层:叙事弧库 + 运镜/素材运动)。

## Codex 运行约定

所有命令都从技能根目录执行。Windows PowerShell 使用 `python`，macOS/Linux 通常使用
`python3`。下文的 `<python>` 指当前环境实际可用的解释器。

开始写脚本或生成素材前，先运行 `<python> scripts/doctor.py --json`。它只检查 Python、Pillow、
ffmpeg、ffprobe 和 curl，不访问网络，也不会产生付费调用。先修复所有缺失的必需依赖。策划和
离线验证阶段可以没有 Atlas key。

只有使用备用 Atlas provider 时，才在第一次调用前运行
`<python> scripts/doctor.py --require-api-key`。Codex ImageGen 和 SuperGrok 不需要 Atlas key。
执行这两个阶段前先读 `references/codex-supergrok.md`。

## 标准流程(主题 → 成片)

默认最自动化路线。每阶段一个脚本,全由每个项目 `out/<project>/` 下的 `beats.json` 驱动。

1. **主题 → 分镜表。** 先**读 `references/beat-layer.md`**(故事层),按主题选一条叙事弧 `arc`
   (历史→`timeline`,广告→`pas`/`bab`,讲解→`how_it_works`,转变→`man_in_hole`…)。再按这条弧写
   `out/<project>/beats.json`:**第1段标题必须是 ≤3 秒的钩子**;beat 数量按时长(30s→6–8,60s→10–12);
   每段拆 **2 镜**(广角+特写),**每镜 `camera_move` 相邻段要不同**(不重复;`static` 留给点题段),
   **`element_motion` 写丰富**(见第4步)。每段:`narration`、`title_cn`/`title_en`、`scene`、`bg`、
   `feel`、`hook`。这份草稿是**唯一强制确认关口**——生成前先给用户过。示例见 `examples/`。

2. **选视觉风格(混合式——在生关键帧前做)。** 别所有主题都用一个风格。读 `references/prompt-guide.md`(§5 主题预置);
   从 **主题预置**(`styles.THEME_PRESETS`:`american-retro`、`swiss-modern`、`punk-zine`、
   `soviet-constructivist`、`wpa-propaganda`、`70s-groovy`、`chinese-ink`、`atomic-age`)里挑 3–4 个
   贴主题(年代/文化/调性)的,**库里没有就现调一个**(混 prompt-guide 的 媒介/年代/配色/字体/质感)。
   **匹配主题、不匹配语言**(英文讲中国史照样该中式)。一个主题打包整个"看的层"
   (idiom+配色+字体+质感+情绪+运动)。跑 bake-off 让用户看图 pick——AI 出主意、库保底、人拍板。
   先准备 Codex ImageGen 试片任务：`<python> scripts/codex_media.py prepare out/<project>
   --stage bakeoff --styles american-retro,swiss-modern,punk-zine,atomic-age`。逐张生成、记录并展示，
   用户选定后运行 `<python> scripts/codex_media.py select-style out/<project> --theme <pick>`。

3. **Codex ImageGen 关键帧（默认）。** 运行
   `<python> scripts/codex_media.py prepare out/<project> --stage keyframes`。对
   `codex-media.json` 中每个 `pending` 任务调用内置 ImageGen，把选中的 PNG 复制到
   `output_path`，检查后运行 `<python> scripts/codex_media.py record out/<project>
   --stage keyframes --key <key> --output <path>`。除非用户明确要求 API fallback，否则不要调用
   Image API CLI，也不要索取 `OPENAI_API_KEY`。

4. **SuperGrok 交付包（默认）。** 运行
   `<python> scripts/codex_media.py prepare out/<project> --stage supergrok`。不要打开 Grok，也不要
   上传任何文件。按镜头 key 把每个任务的本地 `input_path` 参考图、完整 prompt 和时长交给用户；
   可以显示图片时直接内嵌预览，并保留项目内原文件。图生视频由用户在 SuperGrok 中完成。
   动效仍使用两根独立轴：
   • **`camera_move`** —— 每镜一个运镜。安全/默认:`{static, push_in, pull_out, pan, tilt, parallax}`。
     **大胆/实验**:`{orbit, dolly_zoom, roll, whip}` 是**可选、不是禁用**——它们可能掰弯平面,所以配
     `constraints: loose` 用、并**抽卡**重滚,留给值得的那一拍。自定义短语也能穿透。
   • **`element_motion`** —— **张力就在这**;**AI 每 beat 按场景自己写**(不是模板)。写**丰富**(多元素同动),
     大胆点。**"英雄"飞行元素**(纸鸟/纸飞机/硬币飞过全屏)是**偶尔在关键拍点睛**的好料,**不是每镜必有**
     (每帧都飞就俗套)。
   `motion_style` = 幅度 `calm | punchy | max`(主题给默认)。**`constraints`** = `strict`(默认:开防缺陷
   护栏——平面2D/单向/不 morph,适合重文字讲解片)或 `loose`(放开让模型探索 3D/大胆运镜,抽卡重滚)。
   **只有带标题的镜头才硬锁文字**(无标题的特写镜随便浪)。

   **Atlas 备用路径：** 只有用户明确选择 Atlas 并配置 `ATLASCLOUD_API_KEY` 时，才运行
   `<python> scripts/keyframes.py out/<project>` 和 `<python> scripts/clips.py out/<project>`。

5. **旁白 + 配乐。** Codex 原生路径接收本地素材：每个 beat 用 `narration_audio` 指向旁白文件，
   项目用 `bgm_path` 指向背景音乐。可以协助用户准备或导入素材，但不能擅自选择云服务或索取 API key。
   只有用户明确选择 Atlas 时，才运行 `<python> scripts/audio.py out/<project>` 生成旁白和配乐。

6. **合成。** `<python> scripts/assemble.py out/<project>`
   ffmpeg:归一化 + 拼接所有镜头,单一旁白压在配乐下(ducking),按段烧字幕,加水印。
   产物 `out/<project>/final.mp4`。

7. **验证。** mp4 内容读不了——抽帧成 jpg 看:
   `ffmpeg -ss <t> -i final.mp4 -vf "scale=640:-1,format=yuvj420p" -frames:v 1 f.jpg`

### 节奏——一镜多长

常见错误是一段一个长镜头。9:16/社媒尤其:静态 10 秒 = 死画面。目标**每 ~4–6 秒切一刀**:
- **单镜 3–6 秒;别超 ~7 秒**,再长 AI 运动没处使、发闷。
- **一段旁白 ~8–10 秒,所以每段给 2 镜**(带标题的广角 + 不带标题的特写切入);旁白连续跨两镜、画面
  中途切。这是节奏最大的赢法。
- 所以 ~60s 通常是 **~6 段 × 2 镜 × ~5s = 12 镜**,不是 6×10s。
- 广角当 shot `a` 复用;特写 shot `b` 另写更紧的场景。`keyframes.py` 会**跳过已有 `keyframe_url` 的镜**,
  所以加 `b` 镜重跑只生成新的。

## beats.json schema

```json
{
  "project": "my-film", "topic": "...", "language": "en",
  "aspect": "9:16",                       // 16:9 | 9:16 | 1:1 | 3:4
  "style": "collage",
  "provider": "codex",                    // codex | atlas_cloud
  "theme": "american-retro",              // 主题预置(styles.THEME_PRESETS)——"看的层"
  "arc": "timeline",                      // 叙事弧(beat-layer.md)——"故事骨架"
  "video_model": "google/gemini-omni-flash/image-to-video",  // 真人用 Kling
  "motion_style": "punchy",               // 幅度:calm | punchy | max(主题给默认)
  "constraints": "strict",                // strict = 开防缺陷护栏 | loose = 放开探索 + 抽卡
  "voice": {"voice_id": "leo", "language": "en", "speed": 1.0},
  "music": "epic cinematic orchestral, instrumental, no vocals",
  "mix": {"music": 0.6, "voice": 1.25},   // 音量平衡(可选;这是默认值,音乐在人声下自动让路)
  "watermark": "vox-director",
  "beats": [
    {
      "id": 1, "title_cn": "", "title_en": "BEFORE MONEY",
      "bg": "earthy clay tan", "feel": "ancient, humble", "hook": "surprising_stat",
      "narration": "For most of history, there was no money...",
      "shots": [
        // shot_size: EST_WIDE|WIDE|MEDIUM|CLOSE|DETAIL ; camera_move: static|push_in|
        // pull_out|pan|tilt|parallax(仅平面安全)—— 相邻段要变,点题段用 static
        {"id": "a", "dur": 5, "title": true,  "shot_size": "WIDE", "camera_move": "push_in",
         "scene": "...广角建立镜拼贴...",
         "element_motion": "商贩比手势、羊点头、一只纸鸟拍翅飞过画面、硬币散落"},
        {"id": "b", "dur": 5, "title": false, "shot_size": "CLOSE", "camera_move": "parallax",
         "scene": "...特写切入...",
         "element_motion": "交换的货物滑到一起,半调脉动"}
      ]
    }
  ]
}
```
`theme`+`arc` 定两个大层;每镜 `element_motion` 是张力(写丰富,见上)。`motion`/`collage_style`/`era`
仍读,向后兼容。

## 模型选型(务必先校验 ID)

模型 ID 会变——先拉实时表:`GET https://api.atlascloud.ai/api/v1/models`(无 auth;只留 `display_console:true`)。当前默认:

| 环节 | 模型 | 说明 |
|---|---|---|
| 关键帧 / 拼贴海报 | `google/nano-banana-2/text-to-image` | 中英文字都好 |
| 抠单个零件 | `youchuan/v8.1/remove-background` | 仅高阶路线 |
| 动效(非真人) | `google/gemini-omni-flash/image-to-video` | 文字稳、分层运动 |
| 动效(**真人 / 品牌**) | `kwaivgi/kling-video-o3-pro/image-to-video` | Omni 和 Seedance 拦名人 |
| 旁白 | `xai/tts-v1` | 干净、多语言、`voice_id` |
| 配乐 | `minimax/music-2.6` | `is_instrumental: true` |

完整选型理由 + 每个 API/ffmpeg 坑(auth 头、curl 下载、无 libass 烧字幕、内容审核等)见
`references/models-and-gotchas.md`。**排查任何失败前先读它**——大多数坑已记录。

**媒体路径必须显式选择。** `"provider": "codex"` 使用 `scripts/codex_media.py` 生成可恢复的
ImageGen 与 SuperGrok 任务清单；`"provider": "atlas_cloud"` 使用原有 provider 脚本自动提交、
轮询和下载，并要求 `ATLASCLOUD_API_KEY`。不能静默切换路径或产生费用。

## 高阶:元素级 motion collage

标准路线动的是*整张*海报(好、自动、"会动的海报")。要那种**碎片飞入组装**的 motion collage(cr7v2 那种),
或要**完全可控、零内容审核地动真人**,就把每张海报拆成独立零件、用本地关键帧引擎驱动(不经视频模型)。

读 `references/local-engine.md`。简述:`extract_elements.py`(裁切 + 抠图 + 残渣/erase 清理)→
`motion.py`(Layer + 关键帧,`fly_in`/`slap`/`drop`/`pop_settle` 缓动,程序化 confetti/starburst,相机
zoom+shake+whip,逐帧渲染)。零件飞回它们在海报里的**原位**、落在模糊占位底上,组装完还原原海报。

## 两个版本

- **Codex 原生版（默认）：** ImageGen 关键帧、SuperGrok 交付、本地音频和 ffmpeg 合成，不需要 Atlas key。
- **Atlas 自动版（可选）：** 用户明确选择并提供 key 后，自动生成关键帧、视频、旁白和配乐。
- **Prompt 包：** 输出分镜、生图、运动和旁白提示词，交给任意外部生成器。
