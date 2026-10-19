# -*- coding: utf-8 -*-
"""新增感悟：vertical smoothness training popcorn —— 上行欠瞄 / 确定感加速 / 下落回准星"""
import sys, os, json
sys.path.insert(0, os.getcwd())
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None); os.environ.pop("HTTPS_PROXY", None)

from app.repositories import influx_client
from app.repositories import game_reflection_repo as gr
from app.services import game_reflection_markdown as md

influx_client.db.url = "http://127.0.0.1:8087"

DATE = "2026-10-18"
TITLE = "vertical smoothness training popcorn - 上行欠瞄，下落回准星，用确定感做切换"
CONTENT = """在目标上行时候进行欠瞄，等确定感到了就锁着目标进行加速匹配，下落时候感觉差不多就把注意力放准星上等下一次上升的确定感

——
三步拆开：
1. 上行：**欠瞄**（不追满，留余量）
2. 确定感到了：**锁住目标 + 加速匹配**
3. 下落：差不多就把注意力**收回准星**，等下一次上行再给确定感
"""

entry = dict(
    title=TITLE,
    content=CONTENT,
    theme="aim",
    date=DATE,
    game="valorant",
    scenario="vertical smoothness training popcorn",
    tags=["vertical smoothness training popcorn", "欠瞄", "确定感", "上行", "下落",
          "准星", "平滑跟枪", "Popcorn"],
)

res = gr.create_game_reflection(**entry)
print("InfluxDB 写入:", res)

row = gr.get_game_reflection_by_id(res["id"])
print("回读:", json.dumps(row, ensure_ascii=False)[:300] if row else None)

old = md.read_date_reflections(DATE)
print("当日已有:", len(old))

merged = old + [{
    "id": res["id"], "title": entry["title"], "content": entry["content"],
    "theme": entry["theme"], "game": entry["game"], "date": DATE,
    "scenario": entry["scenario"], "tags": entry["tags"],
}]
md.write_date_reflections(DATE, merged)
print("markdown:", md.get_markdown_path(DATE))
print("解析回读:", len(md.read_date_reflections(DATE)), "条")
