# -*- coding: utf-8 -*-
"""
录入感悟（Kovaak：lgc3 Reborn Easy）：
打的时候心里要想着同向匹配和反向匹配，二者区分好就会追得比较好。

三通道写入：
1) InfluxDB game_reflection（Web 游戏感悟页，带 scenario 标记来源场景）
2) InfluxDB aim_reflection（场景详情页，scenario=lgc3 Reborn Easy）
3) web/docs/记录/游戏感悟/2026-10-21.md（人类可读镜像，增量追加）

运行：  python add_lgc3reborn_reflection.py
"""
import sys
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "web", "backend"))

from app.repositories.game_reflection_repo import create_game_reflection  # noqa: E402
from app.repositories.queries import create_reflection  # noqa: E402

DATE = "2026-10-21"
SCENARIO = "lgc3 Reborn Easy"
TITLE = "同向匹配与反向匹配要分开想：分清这两件事，跟枪才追得住"
CONTENT = (
    "打的时候心里要想着同向匹配和反向匹配，二者区分好就会追的比较好"
)
THEME = "aim"          # 对枪/瞄准（tracking 类）
GAME = "valorant"
TAGS = ["同向匹配", "反向匹配", "变向识别", "准星同向运动", "跟枪速度匹配"]

MD_PATH = os.path.join(BASE, "web", "docs", "记录", "游戏感悟", f"{DATE}.md")

NOTE = (
    "> **关联问题库**：这条是把「同向」和「反向」拆成两个独立任务的第一次明确表述，\n"
    "> 问题库里对应的原文锚点有三处——\n"
    "> ① **Q004.10 / Q004.11 的「准星和目标同向运动」**：B站 UP 主原话「如果目标变向了，你往反方向修正，\n"
    "> 那么目标相对于你速度是变得更快了……我准星一直和它同向运动，所以轨迹很清晰」。\n"
    "> 反面就是**反向修正 = 相对速度翻倍 = 更看不清 = 更修不准**，这正是「反向匹配」为什么难；\n"
    "> ② **Q004.11「有手眼两个门槛」**：眼睛的门槛是意识到目标变向、目标与准星脱轨；\n"
    "> 手的门槛是之后再用平滑技巧做下一段**同向**运动。你说的「区分好」，拆开就是这个判断——\n"
    "> 先分清此刻是「跟着同一方向继续」还是「目标已经掉头」，两种情况的发力方向完全不同；\n"
    "> ③ **Q004.7 欠甩偏置的成本不对称**：修正欠甩 = 同向继续，1 个事件；\n"
    "> 修正过冲 = 停 + 反向 + 再瞄，3 个事件。同向段几乎裸打，反向段才是真正花时间的部分。\n"
    ">\n"
    "> 与 Q022 的接续：反向匹配不是「停下再加速」，而是「减速→加速」（张力有下限、不归零），\n"
    "> 和 10-20 日记里「连续=用减速代替停止」是同一件事在变向点上的版本。\n"
    ">\n"
    "> **当日数据**（2026-10-21 05:58–06:05，四轮）：12939 → 12592 → 16364 → **19537**，\n"
    "> 末轮同时是历史最佳（超 10-14 Day9 首轮 18504 约 5.6%），命中率 27.0% → 30.6%，越打越顺而非衰减。"
)


def main():
    print("写入感悟（InfluxDB game_reflection）:")
    print(f"  title   : {TITLE}")
    print(f"  content : {CONTENT}")
    print(f"  theme   : {THEME} | game: {GAME} | scenario: {SCENARIO}")
    print(f"  tags    : {' '.join(TAGS)}")

    ref = create_game_reflection(
        title=TITLE,
        content=CONTENT,
        theme=THEME,
        date=DATE,
        game=GAME,
        scenario=SCENARIO,
        tags=TAGS,
    )
    ref_id = ref["id"]
    print(f"  ✅ game_reflection 写入成功: {ref_id}")

    # ---- 场景详情页（aim_reflection） ----
    try:
        create_reflection(scenario=SCENARIO, note=CONTENT)
        print(f"  ✅ aim_reflection 写入成功: scenario={SCENARIO}")
    except Exception as e:
        print(f"  ⚠️ aim_reflection 写入失败（场景页暂不可见，game_reflection 不受影响）: {e}")

    # ---- Markdown 镜像：增量追加，不清空既有内容 ----
    block = []

    if not os.path.exists(MD_PATH):
        os.makedirs(os.path.dirname(MD_PATH), exist_ok=True)
        with open(MD_PATH, "w", encoding="utf-8") as f:
            f.write(f"# 游戏感悟 - {DATE}\n\n")
            f.write(f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        existing = ""
    else:
        with open(MD_PATH, "r", encoding="utf-8") as f:
            existing = f.read()

    if ref_id in existing:
        print("  ℹ️ Markdown 已存在该条目，跳过追加")
    else:
        block.append(f"### 🎯 {TITLE}")
        block.append("")
        block.append(f"**主题**: 对枪/瞄准 | **游戏**: {GAME} | **场景**: {SCENARIO}")
        block.append("")
        block.append(f"**标签**: {' '.join(TAGS)}")
        block.append("")
        block.append(CONTENT)
        block.append("")
        block.append(f"<!-- reflection_id: {ref_id} -->")
        block.append("")
        block.append("---")
        block.append("")
        block.append(NOTE)
        block.append("")

        with open(MD_PATH, "a", encoding="utf-8") as f:
            lead = ""
            if existing and not existing.rstrip().endswith("---"):
                lead = "\n---\n\n"
            elif existing and not existing.endswith("\n\n"):
                lead = "\n"
            f.write(lead + "\n".join(block))
        print(f"  ✅ Markdown 追加成功: {MD_PATH}")

    print("\n完成。Web 版「游戏感悟」页与场景详情页刷新即可见。")


if __name__ == "__main__":
    main()
