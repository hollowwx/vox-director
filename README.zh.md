<p align="right"><a href="README.md">English</a> · <b>简体中文</b></p>

# 🎬 Vox Director(拼贴动效导演）

**一个选题进,一条成片出——脚本、拼贴关键帧、动效、旁白、配乐、字幕,全流程自动化的 Vox 风格拼贴讲解/广告视频。**

这个 fork 已改成 **Codex 原生工作流**：Codex ImageGen 生成拼贴关键帧，SuperGrok/Grok Imagine 交付包负责图生视频，本地 `ffmpeg` 完成合成。Atlas Cloud 保留为可选的自动化 provider。

![License: MIT](https://img.shields.io/badge/License-MIT-black.svg) ![Codex Native](https://img.shields.io/badge/Codex-native-111827.svg) ![Atlas Optional](https://img.shields.io/badge/Atlas-optional-ff5a1f.svg) ![Agent Skill](https://img.shields.io/badge/Agent-Skill-d97757.svg)

https://github.com/user-attachments/assets/561788b1-5615-4828-b3f8-b24ae5ad7bcd

<p align="center">
  <em>▶《墨西哥街头美食》· 60 秒 · 横屏</em>
</p>

https://github.com/user-attachments/assets/ed08d230-7bcb-4b48-a17d-23c079208f9f

<p align="center">
  <em>▶《中华文明的变迁》· 30 秒 · 横屏</em>
</p>

https://github.com/user-attachments/assets/f69f072f-f50a-41ba-9e66-7ed0aae4ddc0

<p align="center">
  <em>▶《货币简史》· 60 秒 · 竖屏</em>
</p>

---

## 这是什么

风格是 Vox 讲解片带火的现代编辑感**纸质拼贴**:手撕纸片、毛边、胶带、半调网点、报纸剪贴、每一拍一块大胆平涂色、大号剪纸标题——再配上动效、旁白、配乐和字幕,让整张海报活过来。

## 工作原理

一个选题依次流过每个阶段一个脚本,全程由每个项目一份 `beats.json` 驱动:

```
选题
  │
  ├─ 1. 分镜脚本   选叙事弧线 → 写 beats.json          ◀── 决策点 1:你确认分镜脚本
  ├─ 2. 风格试片   Codex ImageGen 渲染 3–4 种主题      ◀── 决策点 2:你看图挑风格
  ├─ 3. 关键帧     Codex ImageGen 生成每张拼贴海报
  ├─ 4. 动效       为 SuperGrok/Grok Imagine 生成交付包
  ├─ 5. 旁白+配乐  导入本地素材（或明确选择 Atlas）
  ├─ 6. 合成       ffmpeg:拼接、配乐在旁白下自动闪避、烧字幕+水印
  └─ final.mp4
```

两个关键理念决定成败,技能就是围绕它们搭的:

1. **风格诞生在生图这一步。** 每一拍是一张成品拼贴*海报*,所有拼贴基因(撕纸、剪纸、网点、标题文字)都长在这张图里——图不够拼贴,后面再怎么救也救不回来。
2. **动效是后加的。** 默认由 AI 视频模型把整张海报动起来(「活海报」路径);要那种戏剧化的**零件逐个飞入拼合**,可选的本地关键帧引擎会把海报拆成零件逐帧驱动(无内容审核、像素级精确,尤其适合真人)。

两个人工决策点让你始终掌控(确认分镜脚本、挑风格),其余全自动。

## 媒体路径

| 阶段 | Codex 原生默认 | Atlas 自动化（可选） |
|---|---|---|
| 风格试片 | Codex ImageGen | Nano Banana 2 |
| 关键帧 | Codex ImageGen | Nano Banana 2 |
| 动效 | SuperGrok/Grok Imagine 交付 | Gemini Omni Flash 或 Kling |
| 旁白与配乐 | 用户本地素材 | xAI TTS + MiniMax Music |
| 合成 | 本地 ffmpeg | 本地 ffmpeg |

Codex 路径不会索取 `OPENAI_API_KEY`，而是直接调用内置 ImageGen。SuperGrok 阶段只生成交付包；除非用户另行要求浏览器自动化，否则不会打开网页或上传文件。

### Atlas 模型

| 用途 | 模型 |
|---|---|
| 关键帧 / 拼贴海报 | `google/nano-banana-2/text-to-image` |
| 动效(非真人内容) | `google/gemini-omni-flash/image-to-video` |
| 动效(**真人 / 品牌**) | `kwaivgi/kling-video-o3-pro/image-to-video` |
| 旁白 | `xai/tts-v1` |
| 配乐 | `minimax/music-2.6` |
| 抠素材(高级路径) | `youchuan/v8.1/remove-background` |

模型 ID 会变——技能运行前会先从 `GET https://api.atlascloud.ai/api/v1/models` 拉取最新列表。

## 安装

这是一个**通用 agent 技能**——任何能读工作流、跑脚本的编码 agent 都能用。Claude Code 和 Codex 的技能发现目录不同，请按你实际使用的 agent 安装。

**Codex——全局安装（推荐）：**
```bash
git clone https://github.com/hollowwx/vox-director.git ~/.codex/skills/vox-director
```

Windows PowerShell：
```powershell
git clone https://github.com/hollowwx/vox-director.git "$HOME/.codex/skills/vox-director"
```

安装后重启 Codex 或新建一个任务，再直接提出 Vox 风格视频需求。在本仓库内工作时，Codex 也会自动发现 [`.agents/skills/vox-director/SKILL.md`](.agents/skills/vox-director/SKILL.md) 项目入口。

**Claude Code：**
```bash
git clone https://github.com/hollowwx/vox-director.git ~/.claude/skills/vox-director
```

需要跨 Agent 共用时也可以安装到 `~/.agents/skills/vox-director`。打包文件 [`vox-director.skill`](vox-director.skill) 仍是 Claude Skill 安装包；Codex 应克隆完整仓库，确保 `SKILL.md` 与资源目录保持在一起。

Codex 原生关键帧与 SuperGrok 交付路径不需要 API key。只有明确选择 Atlas 自动化时才设置：
```bash
export ATLASCLOUD_API_KEY="sk-..."
```

Windows PowerShell：
```powershell
$env:ATLASCLOUD_API_KEY = "sk-..."
```

## 快速开始

装好技能后,直接跟你的编码 agent 说:

> *「做一条 Vox 风格的拼贴视频,介绍墨西哥街头美食——全英文,16:9,15 秒。」*

Codex 会先运行 `scripts/doctor.py`，再起草分镜、准备 ImageGen 风格试片、生成关键帧、制作 SuperGrok 交付包，并把返回的视频与本地音频合成为 `out/<项目>/final.mp4`。

## 环境要求

- **Codex**（推荐）或其他能读取 `SKILL.md` 的编码 agent
- **ffmpeg** + **ffprobe**(`brew install ffmpeg`)
- **Python 3** + **Pillow**(`pip install pillow`)——用于字幕/水印叠加
- 只有可选 Atlas 路径需要 **Atlas Cloud API key + curl**

需要固定本地工具版本时，可用 `VOX_FFMPEG`、`VOX_FFPROBE`、`VOX_CURL` 设置可信绝对路径。

## 目录结构

```
SKILL.md              技能本体(英文)——agent 遵循的工作流
SKILL.zh.md           同一技能的中文版
AGENTS.md             非 Claude agent(Codex 等)的入口
agents/openai.yaml     Codex 界面元数据
.agents/skills/        项目级 Codex 技能入口
references/           创意引擎
  codex-supergrok.md    Codex ImageGen + SuperGrok 交付约定
  prompt-guide.md       画面/LOOK 层:提示词结构 + 词库 + 8 套主题预设
  beat-layer.md         14 种叙事弧线 + 钩子/节奏 + 镜头模式
  models-and-gotchas.md 每一个 API / ffmpeg 坑,都已填平
  local-engine.md       高级的元素级动效引擎
scripts/              每个管线阶段一个脚本
examples/             可直接跑的 beats.json 示例
assets/               样片
```

## 致谢

灵感来自 **[Stav Zilber](https://x.com/StavZilber)**、**[rom1trs](https://x.com/rom1trs)**、**[Higgsfield](https://x.com/higgsfield_ai)** 的拼贴广告工作流,以及 **[Vox](https://www.vox.com)** 的讲解片视觉语言。

原始自动化 provider 基于 **[Atlas Cloud](https://www.atlascloud.ai/?utm_source=github&utm_campaign=vox_director)**。这个 fork 在保留该路径的同时增加了 Codex 原生流程。

## 许可

[MIT](LICENSE) © 2026 Atlas Cloud
