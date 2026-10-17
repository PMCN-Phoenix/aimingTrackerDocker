# -*- coding: utf-8 -*-
"""
录入用户感悟（打瓦实战）：闪光之后不要直接瞄，先涣散→重载视角→算位移→再微调

双通道写入：
1) InfluxDB game_reflection（Web 版数据源）
2) web/docs/记录/游戏感悟/2026-10-17.md（人类可读镜像，增量追加，保留已有内容与关联批注）

运行（宿主机/沙箱均可，需 InfluxDB 可达 8087）：
  python add_flashreset_reflection.py
"""
import sys
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "web", "backend"))

from app.repositories.game_reflection_repo import create_game_reflection  # noqa: E402

DATE = "2026-10-17"
TITLE = "闪光后先涣散重载视角，算完位移再微调"
CONTENT = "打完闪之后，先涣散一下，重新载入视角，计算一下位移距离之后再进行瞄准微调"
THEME = "aim"          # 对枪/瞄准
GAME = "valorant"
TAGS = ["闪光后重置", "视角重载", "soft focus", "位移补偿", "微调"]

MD_PATH = os.path.join(BASE, "web", "docs", "记录", "游戏感悟", f"{DATE}.md")

NOTE = (
    "> **关联问题库**：这条把 **Q015-周边视觉与注意力分配** 的 soft focus 与 "
    "**Q004.6-Multiclick远距离目标连续击打与贴近反应** 的「眼先行/位移规划」串成了实战时序——"
    "闪光后不是立刻找敌人，而是先放弃旧的视觉锚点、重建画面坐标、补偿位移，再启动微调。"
    "下一步可对照 **Q014.1-卸力减速训练** 的「落地前停顿」验证同一条律："
    "先读信息、后动手，比直接甩更快。"
)


def main():
    print("写入感悟（InfluxDB game_reflection）:")
    print(f"  title  : {TITLE}")
    print(f"  content: {CONTENT}")
    print(f"  theme  : {THEME} | game: {GAME}")
    print(f"  tags   : {' '.join(TAGS)}")

    ref = create_game_reflection(
        title=TITLE,
        content=CONTENT,
        theme=THEME,
        date=DATE,
        game=GAME,
        tags=TAGS,
    )
    ref_id = ref["id"]
    print(f"  ✅ InfluxDB 写入成功: {ref_id}")

    # ---- Markdown 镜像：增量追加，不清空既有内容 ----
    block = []

    # 若文件不存在，先建骨架
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
        block.append(f"**主题**: 对枪/瞄准 | **游戏**: {GAME}")
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
            # 确保与既有内容之间有分隔，避免标题直接贴在上一段末尾
            lead = ""
            if existing and not existing.rstrip().endswith("---"):
                lead = "\n---\n\n"
            elif existing and not existing.endswith("\n\n"):
                lead = "\n"
            f.write(lead + "\n".join(block))
        print(f"  ✅ Markdown 追加成功: {MD_PATH}")

    print("\n完成。Web 版「游戏感悟」页刷新即可见。")


if __name__ == "__main__":
    main()
