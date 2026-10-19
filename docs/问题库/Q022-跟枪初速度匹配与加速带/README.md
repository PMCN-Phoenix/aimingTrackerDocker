# Q022 跟枪初速度匹配与加速带

## 问题概述

- **场景背景**：针对跟枪（Tracking）启动阶段的初速度匹配，以及鼠标加速/加速带在平滑跟踪与快速变向中的损耗与代价。
- **核心关注**：从 Kovaak's stats 与多渠道检索分析跟丢惯性、回血代价及速度匹配机制。

## 当前状态

- ✅ B站搜索与精选字幕已抓取（`B站原始数据/`）
- ✅ YouTube 检索及多语言字幕就绪（`YouTube原始数据/`）
- ✅ PubMed 学术题录与摘要就绪（`学术原始数据/`）
- ✅ 本地 stats 跟丢惯性与回血代价统计已生成（`学术原始数据/`）
- ⏳ 主调研报告与训练方案整理中

## 产物索引

| 文件 / 目录 | 说明 |
|---|---|
| `B站原始数据/` | B站搜索清单（`搜索清单.json`）及精选视频字幕 |
| `YouTube原始数据/` | YouTube 检索清单及 VTT 字幕 |
| `学术原始数据/` | PubMed 检索摘要与本地 stats 分析数据 |
| `_bilibili_search.py` / `_bilibili_subtitles.py` | B站检索与字幕抓取脚本 |
| `_youtube.py` | YouTube 检索脚本 |
| `_pubmed.py` / `_pubmed2.py` | PubMed 检索脚本 |
| `_local_stats.py` / `_local_stats2.py` | 本地数据统计脚本 |
