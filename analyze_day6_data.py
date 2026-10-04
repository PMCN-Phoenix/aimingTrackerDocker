"""
查询最近训练数据，分析 Day5/Day6 成效
"""
import urllib.request
import json
from datetime import datetime, timedelta

# InfluxDB 配置
INFLUX_URL = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"

def query_flux(flux_query):
    """执行 Flux 查询"""
    url = f"{INFLUX_URL}/api/v2/query?org={ORG}"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/vnd.flux",
        "Accept": "application/csv"
    }
    data = flux_query.encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def parse_csv(csv_text):
    """解析 InfluxDB CSV 输出"""
    lines = csv_text.strip().split("\n")
    if len(lines) < 2:
        return []
    headers = lines[0].split(",")
    results = []
    for line in lines[1:]:
        if line.startswith("#") or not line.strip():
            continue
        values = line.split(",")
        row = {}
        for i, h in enumerate(headers):
            if i < len(values):
                row[h.strip()] = values[i].strip()
        results.append(row)
    return results

# 查询最近 7 天的练枪成绩
print("=" * 80)
print("查询最近 7 天的练枪成绩（按场景分组统计）")
print("=" * 80)

flux_query = f'''
from(bucket: "{BUCKET}")
  |> range(start: -7d)
  |> filter(fn: (r) => r["_measurement"] == "aim_scenario")
  |> filter(fn: (r) => r["list"] == "viscose-s2-easier")
  |> filter(fn: (r) => r["_field"] == "score")
  |> group(columns: ["scenario"])
  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
  |> yield(name: "daily_mean")
'''

try:
    csv_result = query_flux(flux_query)
    results = parse_csv(csv_result)
    
    # 按场景整理
    scenario_data = {}
    for row in results:
        scenario = row.get("scenario", "unknown")
        time_str = row.get("_time", "")
        value = row.get("_value", "")
        if scenario and value:
            if scenario not in scenario_data:
                scenario_data[scenario] = []
            try:
                scenario_data[scenario].append({
                    "date": time_str[:10],
                    "score": float(value)
                })
            except:
                pass
    
    # 打印每个场景的最近数据
    print(f"\n共找到 {len(scenario_data)} 个场景的数据\n")
    
    # 重点关注的场景
    key_scenarios = [
        "cloverRawControl Viscose Easier 50cm",
        "Flower Easier 50cm",
        "Popcorn MV Easier",
        "SmoothBot Perfected Easier",
        "Pasu Voltaic Reload Easier",
        "Air CELESTIAL No UFO Easier",
        "VT Controlsphere Viscose Easier",
        "Smoothsphere Viscose Easier",
        "Whisphere Viscose Easier",
        "Controlsphere SuperbAim Viscose Easier",
        "1w2ts reload smallflicks larger",
        "ww5t Voltaic Slightly Larger",
    ]
    
    print("【重点场景数据】")
    print("-" * 80)
    for scenario in key_scenarios:
        if scenario in scenario_data:
            data = sorted(scenario_data[scenario], key=lambda x: x["date"])
            print(f"\n📊 {scenario}")
            for d in data[-5:]:  # 最近 5 天
                print(f"   {d['date']}: 平均分 {d['score']:.1f}")
            if len(data) >= 2:
                first = data[0]["score"]
                last = data[-1]["score"]
                change = ((last - first) / first * 100) if first > 0 else 0
                print(f"   → 变化: {first:.1f} → {last:.1f} ({change:+.1f}%)")
        else:
            print(f"\n⚠️  {scenario} - 无数据")
    
    # 查询最高分
    print("\n" + "=" * 80)
    print("查询各场景最高分（最近 7 天）")
    print("=" * 80)
    
    flux_query_max = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -7d)
      |> filter(fn: (r) => r["_measurement"] == "aim_scenario")
      |> filter(fn: (r) => r["list"] == "viscose-s2-easier")
      |> filter(fn: (r) => r["_field"] == "score")
      |> group(columns: ["scenario"])
      |> max()
      |> yield(name: "max_score")
    '''
    
    csv_max = query_flux(flux_query_max)
    max_results = parse_csv(csv_max)
    
    print("\n【各场景最高分】")
    print("-" * 80)
    for row in max_results:
        scenario = row.get("scenario", "")
        value = row.get("_value", "")
        if scenario in key_scenarios and value:
            try:
                print(f"  {scenario}: 最高分 {float(value):.1f}")
            except:
                pass
    
    # 查询 Day6 当天的详细数据
    print("\n" + "=" * 80)
    print("查询 Day6（2026-10-04）详细数据")
    print("=" * 80)
    
    flux_query_day6 = f'''
    from(bucket: "{BUCKET}")
      |> range(start: 2026-10-04T00:00:00Z, stop: 2026-10-05T00:00:00Z)
      |> filter(fn: (r) => r["_measurement"] == "aim_scenario")
      |> filter(fn: (r) => r["list"] == "viscose-s2-easier")
      |> filter(fn: (r) => r["_field"] == "score")
      |> group(columns: ["scenario"])
      |> count()
      |> yield(name: "round_count")
    '''
    
    csv_day6 = query_flux(flux_query_day6)
    day6_results = parse_csv(csv_day6)
    
    print("\n【Day6 各场景轮数】")
    print("-" * 80)
    total_rounds = 0
    for row in day6_results:
        scenario = row.get("scenario", "")
        count = row.get("_value", "0")
        if scenario:
            try:
                c = int(float(count))
                total_rounds += c
                print(f"  {scenario}: {c} 轮")
            except:
                pass
    print(f"\n  总计: {total_rounds} 轮")
    
except Exception as e:
    print(f"❌ 查询出错: {e}")
    import traceback
    traceback.print_exc()
