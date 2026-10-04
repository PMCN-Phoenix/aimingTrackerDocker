"""
统计 Day5 加练清单 "Popcorn Extra - Relax and Apex" 的成效
使用项目中的 InfluxDB 客户端
"""
import sys
import os
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

# 初始化客户端
db = InfluxDBClient()

# 加练清单信息
extra_id = "Day5-extra-1"
extra_name = "Popcorn Extra - Relax and Apex"
created_at = 1790998434  # 2026-10-03 11:33:54

# 加练场景
scenarios = [
    {"name": "Popcorn MV Easier", "required": 4},
    {"name": "SmoothBot Perfected Easier", "required": 2}
]

# 时间范围：从创建时间到现在
start_ts = created_at
end_ts = int(datetime.now().timestamp())

print(f"加练清单: {extra_name} ({extra_id})")
print(f"创建时间: {datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S')}")
print(f"统计时间: {datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S')} ~ {datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 查询每个场景的成绩
total_score = 0
total_rounds = 0
scenario_results = []

for scn in scenarios:
    name = scn["name"]
    required = scn["required"]

    # Flux 查询：获取该场景在时间范围内的所有轮次
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_ts}, stop: {end_ts})
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> filter(fn: (r) => r.scenario == "{name}")
  |> filter(fn: (r) => r._field == "score")
  |> sort(columns: ["_time"])
'''

    rows = db.query(flux)

    rounds = []
    for row in rows:
        score = row.get("_value")
        time_str = row.get("_time")
        if score is not None:
            rounds.append({
                "score": float(score),
                "time": time_str
            })

    # 统计
    done = len(rounds)
    if done > 0:
        avg_score = sum(r["score"] for r in rounds) / done
        max_score = max(r["score"] for r in rounds)
        min_score = min(r["score"] for r in rounds)
    else:
        avg_score = 0
        max_score = 0
        min_score = 0

    status = "已完成" if done >= required else ("进行中" if done > 0 else "未开始")

    scenario_results.append({
        "name": name,
        "required": required,
        "done": done,
        "avg_score": avg_score,
        "max_score": max_score,
        "min_score": min_score,
        "rounds": rounds,
        "status": status
    })

    total_score += avg_score * done
    total_rounds += done

    print(f"【{name}】")
    print(f"  要求轮数: {required}, 已打轮数: {done}, 状态: {status}")
    if done > 0:
        print(f"  平均分: {avg_score:.1f}, 最高分: {max_score:.1f}, 最低分: {min_score:.1f}")
        print(f"  各轮成绩:")
        for i, r in enumerate(rounds, 1):
            print(f"    第{i}轮: {r['score']:.1f} ({r['time']})")
    print()

# 总体统计
print("=" * 60)
print("【总体统计】")
print(f"  总轮数: {total_rounds} / {sum(s['required'] for s in scenarios)}")
if total_rounds > 0:
    overall_avg = total_score / total_rounds
    print(f"  总体平均分: {overall_avg:.1f}")
print(f"  完成状态: {'已完成' if total_rounds >= sum(s['required'] for s in scenarios) else '进行中'}")

# 保存结果
result = {
    "extra_id": extra_id,
    "extra_name": extra_name,
    "created_at": created_at,
    "created_at_str": datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M:%S'),
    "date": datetime.fromtimestamp(created_at).strftime('%Y-%m-%d'),
    "scenarios": scenario_results,
    "total_rounds": total_rounds,
    "total_required": sum(s['required'] for s in scenarios),
    "overall_avg": total_score / total_rounds if total_rounds > 0 else 0
}

output_file = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\记录\Day5-加练-Popcorn Extra-成效统计.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存到: {output_file}")
