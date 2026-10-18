# -*- coding: utf-8 -*-
"""
录入感悟（Kovaak：Vertical Smoothness Training Popcorn）：
目标上行时欠瞄→确定感到→锁住目标加速匹配；下落差不多就把注意力放回准星，等下一次上升的确定感。

三通道写入：
1) InfluxDB game_reflection（Web 游戏感悟页，带 scenario 标记来源场景）
2) web/docs/记录/游戏感悟/2026-10-19.md（人类可读镜像，增量追加）
3) InfluxDB aim_reflection（场景详情页，scenario=Vertical Smoothness Training Popcorn）

运行：  python add_vstpopcorn_reflection.py
"""
import sys
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "web", "backend"))

from app.repositories.game_reflection_repo import create_game_reflection  # noqa: E402
from app.repositories.queries import create_reflection  # noqa: E402

DATE = "2026-10-19"
SCENARIO = "Vertical Smoothness Training Popcorn"
TITLE = "上行欠瞄，确定感到了锁住目标加速匹配；下落把注意力放回准星等下一次上升"
CONTENT = (
    "在目标上行时候进行欠瞄，等确定感到了就锁着目标进行加速匹配，"
    "下落时候感觉差不多就把注意力放准星上等下一次上升的确定感"
)
THEME = "aim"          # 对枪/瞄准（tracking 类）
GAME = "valorant"
TAGS = ["欠瞄", "速度匹配", "确定感", "锁定跟踪", "上下行节律", "外焦点"]

MD_PATH = os.path.join(BASE, "web", "docs", "记录", "游戏感悟", f"{DATE}.md")

NOTE = (
    "> **关联问题库**：这条是 tracking 类的「确定感时序」，把四条线串成一个循环——\n"
    "> ① 上行段**欠瞄** = Q004.7 的「欠甩偏置」（修正欠甩=1 个事件，过冲=3 个事件）；\n"
    "> ② **确定感到了再锁** = Q013 的「等确定感/等枪预判」窗口，而非无脑预压；\n"
    "> ③ **锁住加速匹配** = speed match（ww3t 问答：先贴住再提速），也是 Q007「平滑后微调僵住」的反面解法；\n"
    "> ④ 下落段**注意力放回准星等下一次上升** = Q017 的「外焦点」（注意力在准星/任务上防再投入），\n"
    "> 也是 Q014.1「先降张力再动手」的节律版：跟着目标的呼吸节奏分配注意力，而不是全程死盯目标。"
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
