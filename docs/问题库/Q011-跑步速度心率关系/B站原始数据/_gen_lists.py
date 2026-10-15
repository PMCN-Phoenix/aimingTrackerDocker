# -*- coding: utf-8 -*-
"""生成 B站精选视频列表.md 和 B站搜索结果-全部.md"""
import json, os

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"

sl = json.load(open(os.path.join(OUT, "shortlist.json"), encoding="utf-8"))
status = json.load(open(os.path.join(OUT, "subtitle_status.json"), encoding="utf-8"))
by_bv = {r["bvid"]: r for r in status}

# ===== 1. 精选视频列表 =====
lines = ["# B站精选视频列表（18个）\n",
         "> 从 274 个去重视频中按播放量/弹幕/标题匹配度/UP 主专业度打分精选\n",
         "| # | 主题 | BV号 | 标题 | UP主 | 播放 | 时长 | 字幕 | 选择理由 |",
         "|---|---|---|---|---|---|---|---|---|"]
for i, v in enumerate(sl):
    bv = v["bvid"]
    st = by_bv.get(bv, {})
    has_sub = "✅" if st.get("status") == "ok" else "❌"
    play = v.get("play") or 0
    play_str = f"{play/10000:.1f}万" if play >= 10000 else str(play)
    title = v["title"].replace("|", "\\|")[:45]
    lines.append(f"| {i+1} | {v.get('_theme','')} | {bv} | {title} | {v.get('author','')} | {play_str} | {v.get('duration','')} | {has_sub} | {v.get('_reason','')} |")

lines.append("\n## 字幕抓取情况\n")
ok = [r for r in status if r["status"] == "ok"]
no = [r for r in status if r["status"] != "ok"]
lines.append(f"- **有字幕**：{len(ok)} 个")
for r in ok:
    lines.append(f"  - {r['bvid']}：{r.get('seg_count')} 段，覆盖 {r.get('cover_sec',0)}s / {r.get('duration','?')}s")
lines.append(f"- **无 AI 字幕**：{len(no)} 个（硬字幕视频，需 ASR 兜底）")
for r in no:
    lines.append(f"  - {r['bvid']}：{r['title'][:40]}")

with open(os.path.join(OUT, "B站精选视频列表.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("[ok] B站精选视频列表.md")

# ===== 2. 全部搜索结果 =====
raw = json.load(open(os.path.join(OUT, "search_raw.json"), encoding="utf-8"))
lines = ["# B站搜索结果-全部\n", "> 6 组关键词 × 2 页，共 360 条原始结果，去重后 274 个唯一视频\n"]
for kw, items in raw.items():
    lines.append(f"\n## 关键词：{kw}（{len(items)} 条）\n")
    lines.append("| # | BV号 | 标题 | UP主 | 播放 | 时长 | 简介 |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, it in enumerate(items):
        play = it.get("play") or 0
        play_str = f"{play/10000:.1f}万" if play >= 10000 else str(play)
        title = (it.get("title") or "").replace("|", "\\|")[:50]
        desc = (it.get("description") or "").replace("|", " ").replace("\n", " ")[:60]
        lines.append(f"| {i+1} | {it.get('bvid','')} | {title} | {it.get('author','')} | {play_str} | {it.get('duration','')} | {desc} |")

with open(os.path.join(OUT, "B站搜索结果-全部.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("[ok] B站搜索结果-全部.md")
