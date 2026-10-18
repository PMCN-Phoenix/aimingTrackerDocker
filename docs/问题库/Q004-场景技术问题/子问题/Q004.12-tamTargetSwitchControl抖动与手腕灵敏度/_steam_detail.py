# -*- coding: utf-8 -*-
"""按 id 拉官方描述"""
import sys, json
sys.path.insert(0, ".")
from _steam_search import details

IDS = sys.argv[1:] or [
    "2183788318", "2193101371", "2522496909", "2855599533",
    "3412764985", "3412765199", "2193872594", "2392789238",
    "3564757731", "3567511123", "2183788413", "3422247586",
]
rows = []
for i in range(0, len(IDS), 10):
    for d in details(IDS[i:i + 10]):
        rows.append(d)
for d in rows:
    print(f"\n[{d.get('publishedfileid')}] {d.get('title')}  订阅={d.get('subscriptions')}")
    print("  " + (d.get("description") or "").replace("\n", "\n  "))
with open("steam_detail.json", "w", encoding="utf-8") as f:
    json.dump([{"id": d.get("publishedfileid"), "title": d.get("title"),
                "subs": d.get("subscriptions"), "desc": d.get("description")}
               for d in rows], f, ensure_ascii=False, indent=2)
