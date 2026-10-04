"""
Day6 训练成果分析
- 查询今天（10/04）的训练数据
- 分析各场景完成情况
- 与 Day5 对比
- 下一步建议
"""
import sys
import os
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

db = InfluxDBClient()

# 查询最近 3 天的所有场景成绩（用于对比）
end_ts = int(datetime.now().timestamp())
start_ts = end_ts - 3 * 24 * 3600

flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_ts}, stop: {end_ts})
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario"])
  |> sort(columns: ["_time"])
'''

rows = db.query(flux)

# 按场景和日期分组
scenario_data = defaultdict(lambda: defaultdict(list))
for row in rows:
    scn = row.get("scenario")
    score = float(row.get("_value", 0))
    time_str = row.get("_time", "")
    date = time_str[:10]
    scenario_data[scn][date].append(score)

day6_date = "2026-10-04"
day5_date = "2026-10-03"

print("=" * 90)
print("📊 Day6 训练成果分析")
print(f"分析日期: {day6_date}")
print(f"Day6 清单: 攻Fingertip(cloverRawControl) — 29轮")
print("=" * 90)

# ========== 一、Day6 各场景完成情况 ==========
print("\n" + "=" * 90)
print("一、Day6 各场景完成情况")
print("=" * 90)

day6_scenarios = [
    ("1w2ts reload smallflicks larger", "热身", 2, "命中率95%+"),
    ("ww5t Voltaic Slightly Larger", "热身", 2, "命中率90%+"),
    ("cloverRawControl Viscose Easier 50cm", "主项", 8, "目标5000"),
    ("Flower Easier 50cm", "巩固", 4, "练动作，不追分"),
    ("SmoothBot Perfected Easier", "巩固", 4, "目标3000"),
    ("Pasu Voltaic Reload Easier", "巩固", 4, "目标45"),
    ("Popcorn MV Easier", "巩固", 4, "目标180"),
    ("Air CELESTIAL No UFO Easier", "卡口", 1, "目标842"),
]

print(f"\n{'场景':<42} {'角色':<6} {'要求':>4} {'实际':>4} {'平均分':>8} {'最高分':>8} {'最低分':>8} {'状态'}")
print("-" * 100)

total_required = 0
total_actual = 0

for scn, role, required, target in day6_scenarios:
    total_required += required
    if day6_date in scenario_data[scn]:
        scores = scenario_data[scn][day6_date]
        actual = len(scores)
        total_actual += actual
        avg = sum(scores) / len(scores)
        max_s = max(scores)
        min_s = min(scores)
        
        if actual >= required:
            status = "✅ 完成"
        elif actual > 0:
            status = f"⚠️ 部分({actual}/{required})"
        else:
            status = "❌ 未打"
        
        print(f"{scn:<42} {role:<6} {required:>4} {actual:>4} {avg:>8.1f} {max_s:>8.1f} {min_s:>8.1f} {status}")
    else:
        print(f"{scn:<42} {role:<6} {required:>4} {'0':>4} {'-':>8} {'-':>8} {'-':>8} ❌ 未打")

print(f"\n总轮数: 要求 {total_required} 轮 / 实际 {total_actual} 轮")
if total_actual >= total_required:
    print("✅ 清单全部完成！")
elif total_actual > 0:
    print(f"⚠️ 完成度: {total_actual/total_required*100:.1f}%")
else:
    print("❌ 尚未开始训练")

# ========== 二、主项 cloverRawControl 详细分析 ==========
print("\n" + "=" * 90)
print("二、主项详细分析：cloverRawControl Viscose Easier 50cm")
print("=" * 90)

scn = "cloverRawControl Viscose Easier 50cm"
if day6_date in scenario_data[scn]:
    scores = scenario_data[scn][day6_date]
    print(f"\nDay6 成绩: {len(scores)} 轮")
    print(f"  平均分: {sum(scores)/len(scores):.1f}")
    print(f"  最高分: {max(scores):.1f}")
    print(f"  最低分: {min(scores):.1f}")
    
    # 分段分析
    if len(scores) >= 3:
        calibration = scores[:3]
        chase = scores[3:8] if len(scores) >= 8 else scores[3:]
        print(f"\n  分段分析:")
        print(f"    校准段（前3轮）: 平均分 {sum(calibration)/len(calibration):.1f}, 最高 {max(calibration):.0f}")
        if chase:
            print(f"    追分段（4-8轮）: 平均分 {sum(chase)/len(chase):.1f}, 最高 {max(chase):.0f}")
    
    # 与 Day5 对比
    if day5_date in scenario_data[scn]:
        day5_scores = scenario_data[scn][day5_date]
        day5_avg = sum(day5_scores)/len(day5_scores)
        day6_avg = sum(scores)/len(scores)
        diff = day6_avg - day5_avg
        pct = diff / day5_avg * 100 if day5_avg > 0 else 0
        print(f"\n  与 Day5 对比:")
        print(f"    Day5 ({len(day5_scores)}轮): 平均分 {day5_avg:.1f}, 最高 {max(day5_scores):.0f}")
        print(f"    Day6 ({len(scores)}轮): 平均分 {day6_avg:.1f}, 最高 {max(scores):.0f}")
        if diff > 0:
            print(f"    变化: ✅ 平均分提升 +{diff:.1f} (+{pct:.1f}%)")
        elif diff < 0:
            print(f"    变化: ⚠️ 平均分下降 {diff:.1f} ({pct:.1f}%)")
        else:
            print(f"    变化: ➡️ 持平")
    
    # 目标达成情况
    target = 5000
    max_score = max(scores)
    avg_score = sum(scores)/len(scores)
    print(f"\n  目标达成情况:")
    print(f"    目标分: {target}")
    print(f"    最高分: {max_score:.1f} (达成率 {max_score/target*100:.1f}%)")
    print(f"    平均分: {avg_score:.1f} (达成率 {avg_score/target*100:.1f}%)")
    if max_score >= target:
        print(f"    ✅ 最高分已达到目标！")
    elif avg_score >= target:
        print(f"    ✅ 平均分已达到目标！")
    else:
        print(f"    ⚠️ 尚未达到目标，差距 {target - max_score:.0f} 分")

# ========== 三、Flower 动作纠正效果 ==========
print("\n" + "=" * 90)
print("三、Flower Easier 50cm 动作纠正效果")
print("=" * 90)

scn = "Flower Easier 50cm"
if day6_date in scenario_data[scn]:
    scores = scenario_data[scn][day6_date]
    print(f"\nDay6 成绩: {len(scores)} 轮")
    print(f"  平均分: {sum(scores)/len(scores):.1f}")
    print(f"  最高分: {max(scores):.1f}")
    print(f"  最低分: {min(scores):.1f}")
    
    # 与前两天对比
    print(f"\n  近三天趋势:")
    for date in ["2026-10-02", "2026-10-03", "2026-10-04"]:
        if date in scenario_data[scn]:
            s = scenario_data[scn][date]
            print(f"    {date}: {len(s)}轮, 平均分 {sum(s)/len(s):.1f}, 最高 {max(s):.0f}")
    
    # 判断是否有进步
    if day5_date in scenario_data[scn] and day6_date in scenario_data[scn]:
        day5_avg = sum(scenario_data[scn][day5_date])/len(scenario_data[scn][day5_date])
        day6_avg = sum(scores)/len(scores)
        diff = day6_avg - day5_avg
        if diff > 10:
            print(f"\n  ✅ 动作纠正有效！平均分提升 +{diff:.1f}")
        elif diff > -10:
            print(f"\n  ➡️ 基本持平（{diff:+.1f}），动作纠正需要更多时间")
        else:
            print(f"\n  ⚠️ 平均分下降 {diff:.1f}，可能还在调整动作阶段")

# ========== 四、其他场景保持情况 ==========
print("\n" + "=" * 90)
print("四、其他场景保持情况")
print("=" * 90)

other_scenarios = [
    ("SmoothBot Perfected Easier", 3000),
    ("Pasu Voltaic Reload Easier", 45),
    ("Popcorn MV Easier", 180),
    ("Air CELESTIAL No UFO Easier", 842),
]

for scn, target in other_scenarios:
    if day6_date in scenario_data[scn]:
        scores = scenario_data[scn][day6_date]
        avg = sum(scores)/len(scores)
        max_s = max(scores)
        print(f"\n【{scn}】")
        print(f"  Day6: {len(scores)}轮, 平均分 {avg:.1f}, 最高 {max_s:.1f}")
        print(f"  目标: {target}, 最高达成率: {max_s/target*100:.1f}%")
        
        if day5_date in scenario_data[scn]:
            day5_scores = scenario_data[scn][day5_date]
            day5_avg = sum(day5_scores)/len(day5_scores)
            diff = avg - day5_avg
            print(f"  与 Day5 对比: Day5平均分 {day5_avg:.1f} → Day6平均分 {avg:.1f} ({diff:+.1f})")

# ========== 五、总结与下一步建议 ==========
print("\n" + "=" * 90)
print("五、总结与下一步建议")
print("=" * 90)

print("""
📊 Day6 核心指标：
- 主项 cloverRawControl：待分析
- Flower 动作纠正：待分析
- 其他场景保持：待分析

🎯 下一步建议（Day7）：
根据 Day6 成效，明天可以考虑：
1. 如果 cloverRawControl 达到 5000：继续巩固，或换下一个最弱项（VT Controlsphere）
2. 如果 cloverRawControl 未达到 5000：继续作为主项，再练一天
3. Flower 如果仍无进步：考虑换训练方式，或增加感悟记录
4. 加练建议：VT Controlsphere 摸底（最近14天0轮，完全空白）
""")
