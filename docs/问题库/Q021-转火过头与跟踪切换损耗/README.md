# Q021 转火过头与跟踪切换损耗

## 问题概述

- **场景背景**：针对 Speed Target Switching（Speed TS，如 VDIM Friday 场景、tamTargetSwitch 等）中转火时的过冲（overshoot）以及目标间切换停顿损耗。
- **核心关注**：从 Kovaak's stats CSV 与多渠道社区/学术数据量化切换损耗（Shots - Hits 额外开火、TTK 击杀耗时），探索如何减少过头并提升有效命中率。

## 当前状态

- ✅ B站搜索与原始视频清单已采集（`B站原始数据/`）
- ✅ YouTube 检索及字幕抓取脚本就绪（`YouTube原始数据/`）
- ✅ PubMed 学术检索题录就绪（`学术原始数据/pubmed检索结果.json`）
- ✅ 本地 Kovaak's stats 切换损耗统计已生成（`学术原始数据/本地数据-切换损耗.json`）
- ⏳ 主调研报告与训练方案整理中

## 产物索引

| 文件 / 目录 | 说明 |
|---|---|
| `B站原始数据/` | B站搜索清单（`搜索清单.json`）及相关字幕 |
| `YouTube原始数据/` | YouTube 检索及字幕 |
| `学术原始数据/` | PubMed 检索结果与本地 stats 切换损耗度量数据 |
| `_bilibili_search.py` | B站检索脚本 |
| `_bilibili_subtitles.py` | B站字幕获取脚本 |
| `_local_stats.py` | 本地 stats 切换损耗量化分析脚本 |
| `_pubmed.py` | PubMed 检索脚本 |
| `_youtube.py` | YouTube 检索脚本 |
