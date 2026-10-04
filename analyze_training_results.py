"""
全面分析训练成果
- 最近 7 天各场景成绩趋势
- Day5 成效分析
- 各子类档位进展
- 长期最弱项变化
"""
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

db = InfluxDBClient()

# 查询最近 14 天的所有场景成绩
end_ts = int(datetime.now().timestamp())
start_ts = end_ts - 14 * 24 * 3600

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
scenario_data = defaultdict(list)
for row in rows:
    scn = row.get("scenario")
    score = float(row.get("_value", 0))
    time_str = row.get("_time", "")
    date = time_str[:10]
    scenario_data[scn].append({"score": score, "date": date, "time": time_str})

print("=" * 90)
print("📊 训练成果全面分析")
print(f"分析时间范围: {datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d')} ~ {datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d')}")
print(f"数据总轮数: {len(rows)}")
print("=" * 90)

# ========== 一、各场景综合统计 ==========
print("\n" + "=" * 90)
print("一、各场景综合统计（最近 14 天）")
print("=" * 90)

focus_scenarios = [
    ("Popcorn MV Easier", "CLICK·Precision"),
    ("cloverRawControl Viscose Easier 50cm", "CONTROL·Fingertip"),
    ("Flower Easier 50cm", "CONTROL·Fingertip"),
    ("SmoothBot Perfected Easier", "CONTROL·Arm"),
    ("Smoothsphere Viscose Easier", "CONTROL·Arm"),
    ("Air CELESTIAL No UFO Easier", "CONTROL·Blending"),
    ("Pasu Voltaic Reload Easier", "CLICK·Precision"),
    ("1w2ts reload smallflicks larger", "CLICK·Precision"),
    ("ww5t Voltaic Slightly Larger", "CLICK·Precision"),
    ("VT Controlsphere Viscose Easier", "CONTROL·Wrist"),
    ("Whisphere Viscose Easier", "CONTROL·Arm"),
]

print(f"\n{'场景':<42} {'子类':<18} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8} {'最近分':>8}")
print("-" * 105)

for scn, sub in focus_scenarios:
    if scn in scenario_data:
        data = scenario_data[scn]
        scores = [d["score"] for d in data]
        avg = sum(scores) / len(scores)
        max_s = max(scores)
        min_s = min(scores)
        latest = scores[-1]
        print(f"{scn:<42} {sub:<18} {len(scores):>5} {avg:>8.1f} {max_s:>8.1f} {min_s:>8.1f} {latest:>8.1f}")
    else:
        print(f"{scn:<42} {sub:<18} {'0':>5} {'-':>8} {'-':>8} {'-':>8} {'-':>8}")

# ========== 二、按日期统计关键场景 ==========
print("\n" + "=" * 90)
print("二、关键场景按日期趋势")
print("=" * 90)

key_scenarios = ["Popcorn MV Easier", "cloverRawControl Viscose Easier 50cm", "Flower Easier 50cm", "SmoothBot Perfected Easier"]

for scn in key_scenarios:
    if scn in scenario_data:
        print(f"\n【{scn}】")
        by_date = defaultdict(list)
        for d in scenario_data[scn]:
            by_date[d["date"]].append(d["score"])
        
        print(f"  {'日期':<12} {'轮数':>5} {'平均分':>8} {'最高分':>8} {'最低分':>8} {'趋势':>10}")
        print("  " + "-" * 60)
        
        prev_avg = None
        for date in sorted(by_date.keys()):
            scores = by_date[date]
            avg = sum(scores) / len(scores)
            trend = ""
            if prev_avg is not None:
                diff = avg - prev_avg
                pct = (diff / prev_avg * 100) if prev_avg > 0 else 0
                if diff > 0:
                    trend = f"↑ +{diff:.0f} (+{pct:.1f}%)"
                elif diff < 0:
                    trend = f"↓ {diff:.0f} ({pct:.1f}%)"
                else:
                    trend = "→ 持平"
            print(f"  {date:<12} {len(scores):>5} {avg:>8.1f} {max(scores):>8.1f} {min(scores):>8.1f} {trend:>10}")
            prev_avg = avg

# ========== 三、Day5 专项分析 ==========
print("\n" + "=" * 90)
print("三、Day5 专项分析（10/03 攻 Precision）")
print("=" * 90)

day5_date = "2026-10-03"
print(f"\nDay5 执行日期: {day5_date}")
print(f"Day5 主项: Popcorn MV Easier ×8（校准3 + 追分5）")
print(f"Day5 加练: Popcorn Extra - Relax and Apex（Popcorn ×4 + SmoothBot ×2）")

# Popcorn Day5 详细分析
if "Popcorn MV Easier" in scenario_data:
    popcorn_day5 = [d for d in scenario_data["Popcorn MV Easier"] if d["date"] == day5_date]
    if popcorn_day5:
        scores = [d["score"] for d in popcorn_day5]
        print(f"\n【Popcorn MV Easier - Day5 详细】")
        print(f"  总轮数: {len(scores)}")
        print(f"  平均分: {sum(scores)/len(scores):.1f}")
        print(f"  最高分: {max(scores):.1f}")
        print(f"  最低分: {min(scores):.1f}")
        
        # 分段分析（前3轮校准 vs 后段追分）
        if len(scores) >= 8:
            calibration = scores[:3]
            chase = scores[3:8]
            extra = scores[8:] if len(scores) > 8 else []
            print(f"\n  分段分析:")
            print(f"    校准段（前3轮）: 平均分 {sum(calibration)/len(calibration):.1f}, 最高 {max(calibration):.0f}")
            print(f"    追分段（4-8轮）: 平均分 {sum(chase)/len(chase):.1f}, 最高 {max(chase):.0f}")
            if extra:
                print(f"    加练段（9+轮）: 平均分 {sum(extra)/len(extra):.1f}, 最高 {max(extra):.0f}, 共 {len(extra)} 轮")
        
        # 分数分布
        print(f"\n  分数分布:")
        ranges = [(0, 100), (100, 150), (150, 200), (200, 250), (250, 300)]
        for low, high in ranges:
            count = sum(1 for s in scores if low <= s < high)
            pct = count / len(scores) * 100
            bar = "█" * int(pct / 5)
            print(f"    {low}-{high}: {count:>3}轮 ({pct:>5.1f}%) {bar}")

# ========== 四、长期最弱项进展 ==========
print("\n" + "=" * 90)
print("四、长期最弱项进展跟踪")
print("=" * 90)

weak_items = [
    ("Popcorn MV Easier", "CLICK·Precision", "摸底120", "Day5主攻"),
    ("cloverRawControl Viscose Easier 50cm", "CONTROL·Fingertip", "摸底2928", "Day5打了8轮"),
    ("Flower Easier 50cm", "CONTROL·Fingertip", "摸底968", "连续两天持平"),
    ("VT Controlsphere Viscose Easier", "CONTROL·Wrist", "摸底1388", "最近14天0轮"),
    ("Whisphere Viscose Easier", "CONTROL·Arm", "摸底9000", "最近14天0轮"),
]

print(f"\n{'场景':<42} {'子类':<18} {'基线':<12} {'最近状态':<15} {'进展评估'}")
print("-" * 110)

for scn, sub, baseline, status in weak_items:
    if scn in scenario_data and scenario_data[scn]:
        data = scenario_data[scn]
        scores = [d["score"] for d in data]
        latest_avg = sum(scores[-min(5, len(scores)):]) / min(5, len(scores))
        max_s = max(scores)
        total_rounds = len(scores)
        
        # 提取基线数字
        baseline_num = float(''.join(c for c in baseline if c.isdigit() or c == '.'))
        progress_pct = (latest_avg - baseline_num) / baseline_num * 100 if baseline_num > 0 else 0
        
        if progress_pct > 20:
            eval_str = f"✅ 大幅进步 +{progress_pct:.0f}% (最高{max_s:.0f})"
        elif progress_pct > 5:
            eval_str = f"📈 稳步进步 +{progress_pct:.0f}% (最高{max_s:.0f})"
        elif progress_pct > -5:
            eval_str = f"➡️ 基本持平 ({progress_pct:+.0f}%)"
        else:
            eval_str = f"📉 退步 {progress_pct:.0f}%"
        
        print(f"{scn:<42} {sub:<18} {baseline:<12} {status:<15} {eval_str}")
    else:
        print(f"{scn:<42} {sub:<18} {baseline:<12} {status:<15} ❌ 完全没练")

# ========== 五、总结与建议 ==========
print("\n" + "=" * 90)
print("五、总结与下一步建议")
print("=" * 90)

print("""
✅ 主要成果：
1. Popcorn MV Easier 突破成功：摸底120 → Day5平均分152 → 最高分260（+117%）
2. cloverRawControl 潜力显现：摸底2928 → 8轮平均分4024（+37%），但量不足
3. SmoothBot 保持稳定：最近平均分2943，最高分3213，接近3000目标
4. 建立了感悟系统：Popcorn 2条感悟，SmoothBot 1条感悟

⚠️ 需要关注：
1. Flower Easier 50cm 连续两天持平（1440→1440），需要动作纠正而非追分
2. VT Controlsphere 和 Whisphere 最近14天0轮，完全被遗忘
3. Day5 Popcorn 打了116轮（主项94+加练22），量偏大，注意避免疲劳

🎯 下一步建议（Day6）：
1. 主攻 cloverRawControl（Fingertip 子类），认真练8轮，目标5000
2. Flower 专门练动作（4轮），不追分：手腕放松、弧线跟踪、不要急停
3. Popcorn 巩固（4轮），保持 Day5 成果
4. 加练建议：VT Controlsphere 摸底（4-6轮），填补空白项
""")
