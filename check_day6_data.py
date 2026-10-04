"""
检查最近 24 小时的数据导入情况
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

db = InfluxDBClient()

# 查询最近 48 小时的所有数据
end_ts = int(datetime.now().timestamp())
start_ts = end_ts - 2 * 24 * 3600

print(f"查询时间范围: {datetime.fromtimestamp(start_ts)} ~ {datetime.fromtimestamp(end_ts)}")

# 查询所有 aim_scenario 数据
flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_ts}, stop: {end_ts})
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario"])
  |> sort(columns: ["_time"])
'''

rows = db.query(flux)
print(f"\n最近 48 小时 aim_scenario 数据: {len(rows)} 条")

# 按日期分组
from collections import defaultdict
by_date = defaultdict(list)
for row in rows:
    time_str = row.get("_time", "")
    date = time_str[:10]
    by_date[date].append(row)

print("\n按日期统计:")
for date in sorted(by_date.keys()):
    data = by_date[date]
    scenarios = set(r.get("scenario") for r in data)
    print(f"  {date}: {len(data)} 条, {len(scenarios)} 个场景")
    for scn in sorted(scenarios):
        scn_data = [r for r in data if r.get("scenario") == scn]
        scores = [float(r.get("_value", 0)) for r in scn_data]
        print(f"    - {scn}: {len(scn_data)}轮, 平均 {sum(scores)/len(scores):.1f}, 最高 {max(scores):.0f}")

# 检查 Kovaak's stats 目录中今天的文件
print("\n" + "=" * 80)
print("检查 Kovaak's stats 目录中最近的文件")
print("=" * 80)

stats_dir = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
if os.path.exists(stats_dir):
    files = []
    for f in os.listdir(stats_dir):
        if f.endswith('.csv'):
            fpath = os.path.join(stats_dir, f)
            mtime = os.path.getmtime(fpath)
            files.append((f, mtime))
    
    files.sort(key=lambda x: x[1], reverse=True)
    print(f"\n最近 20 个 stats 文件:")
    for f, mtime in files[:20]:
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {mtime_str} - {f}")
else:
    print(f"stats 目录不存在: {stats_dir}")
