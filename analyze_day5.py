"""
查询最近几天的成绩数据，分析各场景进展，为 Day6 清单做准备
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

db = InfluxDBClient()

# 查询最近 7 天的所有场景成绩
end_ts = int(datetime.now().timestamp())
start_ts = end_ts - 7 * 24 * 3600

flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_ts}, stop: {end_ts})
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario"])
  |> sort(columns: ["_time"])
'''

rows = db.query(flux)

# 按场景分组
scenario_data = {}
for row in rows:
    scn = row.get("scenario")
    score = float(row.get("_value", 0))
    time_str = row.get("_time", "")
    if scn not in scenario_data:
        scenario_data[scn] = []
    scenario_data[scn].append({"score": score, "time": time_str})

# 统计每个场景的最近成绩
print("=" * 80)
print("最近 7 天各场景成绩统计")
print("=" * 80)

# 重点关注的场景
focus_scenarios = [
    "Popcorn MV Easier",
    "cloverRawControl Viscose Easier 50cm",
    "Flower Easier 50cm",
    "SmoothBot Perfected Easier",
    "Smoothsphere Viscose Easier",
    "Air CELESTIAL No UFO Easier",
    "Pasu Voltaic Reload Easier",
    "1w2ts reload smallflicks larger",
    "ww5t Voltaic Slightly Larger",
    "VT Controlsphere Viscose Easier",
    "Whisphere Viscose Easier",
]

print()
print(f"{'场景':<45} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8} {'最近分':>8}")
print("-" * 95)

for scn in focus_scenarios:
    if scn in scenario_data:
        data = scenario_data[scn]
        scores = [d["score"] for d in data]
        avg = sum(scores) / len(scores)
        max_s = max(scores)
        min_s = min(scores)
        latest = scores[-1]
        print(f"{scn:<45} {len(scores):>5} {avg:>8.1f} {max_s:>8.1f} {min_s:>8.1f} {latest:>8.1f}")
    else:
        print(f"{scn:<45} {'0':>5} {'-':>8} {'-':>8} {'-':>8} {'-':>8}")

# 按日期统计 Popcorn 的进展
print()
print("=" * 80)
print("Popcorn MV Easier 按日期统计")
print("=" * 80)

if "Popcorn MV Easier" in scenario_data:
    by_date = {}
    for d in scenario_data["Popcorn MV Easier"]:
        date = d["time"][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(d["score"])
    
    print(f"{'日期':<15} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8}")
    print("-" * 50)
    for date in sorted(by_date.keys()):
        scores = by_date[date]
        avg = sum(scores) / len(scores)
        print(f"{date:<15} {len(scores):>5} {avg:>8.1f} {max(scores):>8.1f} {min(scores):>8.1f}")

# 按日期统计 cloverRawControl 的进展
print()
print("=" * 80)
print("cloverRawControl Viscose Easier 50cm 按日期统计")
print("=" * 80)

if "cloverRawControl Viscose Easier 50cm" in scenario_data:
    by_date = {}
    for d in scenario_data["cloverRawControl Viscose Easier 50cm"]:
        date = d["time"][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(d["score"])
    
    print(f"{'日期':<15} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8}")
    print("-" * 50)
    for date in sorted(by_date.keys()):
        scores = by_date[date]
        avg = sum(scores) / len(scores)
        print(f"{date:<15} {len(scores):>5} {avg:>8.1f} {max(scores):>8.1f} {min(scores):>8.1f}")

# 按日期统计 Flower 的进展
print()
print("=" * 80)
print("Flower Easier 50cm 按日期统计")
print("=" * 80)

if "Flower Easier 50cm" in scenario_data:
    by_date = {}
    for d in scenario_data["Flower Easier 50cm"]:
        date = d["time"][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(d["score"])
    
    print(f"{'日期':<15} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8}")
    print("-" * 50)
    for date in sorted(by_date.keys()):
        scores = by_date[date]
        avg = sum(scores) / len(scores)
        print(f"{date:<15} {len(scores):>5} {avg:>8.1f} {max(scores):>8.1f} {min(scores):>8.1f}")
