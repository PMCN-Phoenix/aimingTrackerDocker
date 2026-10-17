# -*- coding: utf-8 -*-
"""把 Reflex Flick - Easy 的感悟写入 aim_reflection（场景详情页的项目级感悟）

内容来自 2026-10-17 15:34 的游戏感悟：手腕放松时更快
"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "web", "backend"))

from app.repositories.queries import create_reflection, get_scenario_reflections  # noqa: E402

SCENARIO = "Reflex Flick - Easy"
NOTE = "在手腕放松时候更快"

res = create_reflection(SCENARIO, NOTE)
print("写入:", res)

print("\n回查该场景的感悟列表：")
for r in get_scenario_reflections(SCENARIO, days=30):
    print(" -", r["date"], "|", r["note"])
