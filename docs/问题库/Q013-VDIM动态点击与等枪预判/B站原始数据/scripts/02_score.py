# -*- coding: utf-8 -*-
"""
Q013 - 第2步：去重打分精选
打分 = 播放量权重 + 收藏 + 弹幕 + 标题相关度
优先复用 Q003/Q007 已有字幕
输出：selected_videos.json
"""
import json, re
from pathlib import Path

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")

# 已有字幕目录（可复用）
REUSE_DIRS = {
    "Q003": Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q003-VDIM进步方法论\VDIM调研-B站原始数据\字幕"),
    "Q007": Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据\字幕"),
}

# 收集可复用bvid
REUSE_MAP = {}
for tag, d in REUSE_DIRS.items():
    if d.exists():
        for f in d.glob("*.txt"):
            bvid = f.stem
            REUSE_MAP[bvid] = (tag, str(f))
print(f"可复用字幕bvid数: {len(REUSE_MAP)}")

# 标题相关度词
RELEVANT_WORDS = [
    "VDIM", "动态点击", "dynamic clicking", "跟枪", "tracking", "tracking",
    "甩枪", "flick", "flicking", "等枪", "预判", "提前量", "预瞄",
    "kovaak", "kovaaks", "瞄准训练", "aim", "aiming", "练枪",
    "目标速度", "移动目标", "追踪", "微操", "微调",
    "瓦", "valorant", "CS", "csgo", "apex", "fps",
]
# 排除词（明显跑题）
EXCLUDE_WORDS = [
    "抽卡", "直播回放", "直播间", "切片", "集锦", "高能",
    "王者荣耀", "lol", "英雄联盟", "原神", "崩坏", "星穹",
    "鬼畜", "鬼畜", "搞笑", "沙雕", "vlog", "日常",
    "开箱", "抽奖", "福利", "优惠券", "带货",
]


def score_video(v):
    title = (v.get("title") or "").lower()
    desc = (v.get("description") or "").lower()
    text = title + " " + desc

    # 排除
    for w in EXCLUDE_WORDS:
        if w in text:
            return -1, "excluded"

    # 相关度命中数
    rel_hits = sum(1 for w in RELEVANT_WORDS if w.lower() in text)

    # 多关键词命中加分
    kw_bonus = len(v.get("hit_keywords", [v.get("source_keyword", "")])) * 2

    # 播放量对数（避免头部视频垄断）
    play = v.get("play", 0) or 0
    fav = v.get("favorites", 0) or 0
    danmaku = v.get("danmaku", 0) or 0
    reply = v.get("reply", 0) or 0

    # 加权分
    import math
    s = (
        math.log10(play + 1) * 3
        + math.log10(fav + 1) * 2
        + math.log10(danmaku + 1) * 1.5
        + math.log10(reply + 1) * 1
        + rel_hits * 3
        + kw_bonus
    )

    # 可复用字幕的大幅加分（已经验证过内容）
    if v["bvid"] in REUSE_MAP:
        s += 10

    # 时长过滤：<30秒或>30分钟都不要
    dur = v.get("duration", "")
    m = re.match(r"(?:(\d+):)?(\d+):(\d+)", dur)
    if m:
        h = int(m.group(1) or 0)
        mm = int(m.group(2))
        ss = int(m.group(3))
        total = h * 3600 + mm * 60 + ss
        if total < 30:
            return -1, "too_short"
        if total > 30 * 60:
            s -= 5  # 太长的技术视频反而不聚焦

    return s, {"rel_hits": rel_hits, "kw_bonus": kw_bonus}


def main():
    data = json.load(open(OUT_DIR / "search_results.json", encoding="utf-8"))
    videos = data["videos"]
    print(f"待打分: {len(videos)} 条")

    scored = []
    for v in videos:
        s, info = score_video(v)
        if s < 0:
            continue
        v2 = dict(v)
        v2["score"] = round(s, 2)
        v2["score_info"] = info if isinstance(info, dict) else {"reason": info}
        if v["bvid"] in REUSE_MAP:
            tag, path = REUSE_MAP[v["bvid"]]
            v2["reuse_subtitle"] = f"{tag}: {path}"
        scored.append(v2)

    scored.sort(key=lambda x: -x["score"])

    # 分组选取：保证3个方向都有覆盖
    by_theme = {"D1": [], "D2": [], "D3": []}
    picked = []
    picked_bvids = set()

    # 第一轮：每个方向取前5
    for v in scored:
        for t in v.get("hit_themes", [v.get("keyword_hit")]):
            if t in by_theme and len(by_theme[t]) < 5:
                if v["bvid"] not in picked_bvids:
                    by_theme[t].append(v)
                    picked.append(v)
                    picked_bvids.add(v["bvid"])
                break

    # 第二轮：按分数继续补到15
    for v in scored:
        if len(picked) >= 15:
            break
        if v["bvid"] not in picked_bvids:
            picked.append(v)
            picked_bvids.add(v["bvid"])

    print(f"\n精选 {len(picked)} 个：")
    for i, v in enumerate(picked):
        reuse = " [复用字幕]" if v.get("reuse_subtitle") else ""
        print(f"  {i+1:2d}. {v['bvid']} | play={v.get('play',0):>7} | score={v['score']:6.2f} | {v['title'][:50]}{reuse}")

    out = {
        "selected_time": data.get("search_time"),
        "total_searched": len(videos),
        "selected_count": len(picked),
        "selected": picked,
    }
    (OUT_DIR / "selected_videos.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已保存: {OUT_DIR / 'selected_videos.json'}")


if __name__ == "__main__":
    main()
