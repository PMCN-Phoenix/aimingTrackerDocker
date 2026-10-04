"""
1. 录入 Air CELESTIAL 感悟
2. 更新 Day6 加练数据（扫描新的 stats 文件）
"""
import os
import csv
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# 配置
STATS_DIR = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
INFLUX_URL = "http://127.0.0.1:8087"
TOKEN = "aim-super-secret-token-2026"
ORG = "aim-org"
BUCKET = "aim"

# 加练清单配置
EXTRA_ID = "Day6-extra-1"
EXTRA_NAME = "VT摸底+冲卡口"
PARENT_DAYLIST = "Day6"

# 目标场景
TARGET_SCENARIOS = [
    "VT Controlsphere Viscose Easier",
    "Air CELESTIAL No UFO Easier",
]

# Air CELESTIAL 感悟
REFLECTION_SCENARIO = "Air CELESTIAL No UFO Easier"
REFLECTION_TEXT = "要用手指发力，变换方向时候最小位移距离避免错位，并且需要时时刻刻判断左右"
REFLECTION_DATE = "2026-10-05"

print("=" * 80)
print("📝 任务 1：录入 Air CELESTIAL 感悟")
print("=" * 80)

# 构造感悟的 Line Protocol
# 参考之前的写法：note 字段在双引号内，不需要转义逗号
scenario_tag = REFLECTION_SCENARIO.replace(' ', '\\ ').replace(',', '\\,')
now_ts = int(datetime.now().timestamp())
now_ns = now_ts * 1000000000

# 感悟文本需要转义双引号（如果有的话），这里没有
reflection_escaped = REFLECTION_TEXT.replace('"', '\\"')

reflection_line = (
    f'kovaaks_reflection,scenario={scenario_tag} '
    f'note="{reflection_escaped}",date="{REFLECTION_DATE}" {now_ns}'
)

print(f"   场景: {REFLECTION_SCENARIO}")
print(f"   感悟: {REFLECTION_TEXT}")
print(f"   日期: {REFLECTION_DATE}")
print(f"   Line Protocol: {reflection_line[:100]}...")

# 写入感悟
write_url = f"{INFLUX_URL}/api/v2/write?org={ORG}&bucket={BUCKET}"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "text/plain; charset=utf-8"
}

response = requests.post(write_url, headers=headers, data=reflection_line.encode("utf-8"))
print(f"   写入结果: HTTP {response.status_code}")
if response.status_code == 204:
    print("   ✅ 感悟写入成功！")
else:
    print(f"   ❌ 写入失败: {response.text}")

# 验证感悟
print("\n   验证感悟写入...")
flux_verify = f'''
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "kovaaks_reflection")
  |> filter(fn: (r) => r.scenario == "{REFLECTION_SCENARIO}")
  |> keep(columns: ["_time", "scenario", "note", "date"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 3)
'''

query_response = requests.post(
    f"{INFLUX_URL}/api/v2/query",
    headers={"Authorization": f"Token {TOKEN}", "Content-Type": "application/vnd.flux"},
    params={"org": ORG},
    data=flux_verify,
    timeout=30
)

if query_response.status_code == 200:
    lines_out = query_response.text.strip().split("\n")
    print(f"   查询到 {len(lines_out)-1} 条感悟记录")
    for line in lines_out[:5]:
        print(f"   {line[:150]}")
else:
    print(f"   查询失败: {query_response.text}")

print("\n" + "=" * 80)
print("📥 任务 2：更新 Day6 加练数据")
print("=" * 80)

# 扫描最近的 stats 文件
print("\n1. 扫描 Kovaak's stats 目录...")

now = datetime.now()
cutoff = now - timedelta(days=2)

stats_files = []
for f in os.listdir(STATS_DIR):
    if f.endswith('.csv'):
        fpath = os.path.join(STATS_DIR, f)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        if mtime >= cutoff:
            stats_files.append((fpath, mtime, f))

stats_files.sort(key=lambda x: x[1], reverse=True)
print(f"   找到 {len(stats_files)} 个最近 2 天的 stats 文件")

# 解析每个文件
print("\n2. 解析 stats 文件，提取目标场景数据...")

all_records = []

for fpath, mtime, fname in stats_files:
    try:
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        scenario = None
        score = None
        hit_count = None
        miss_count = None
        
        for row in rows:
            if len(row) >= 2:
                key = row[0].strip()
                val = row[1].strip() if len(row) > 1 else ''
                if key == 'Scenario:':
                    scenario = val
                elif key == 'Score:':
                    try:
                        score = float(val)
                    except:
                        pass
                elif key == 'Hit Count:':
                    try:
                        hit_count = int(val)
                    except:
                        pass
                elif key == 'Miss Count:':
                    try:
                        miss_count = int(val)
                    except:
                        pass
        
        if scenario and any(ts.lower() in scenario.lower() for ts in TARGET_SCENARIOS):
            accuracy = None
            if hit_count is not None and miss_count is not None:
                total = hit_count + miss_count
                if total > 0:
                    accuracy = hit_count / total
            
            record = {
                'scenario': scenario,
                'score': score,
                'hit_count': hit_count,
                'miss_count': miss_count,
                'accuracy': accuracy,
                'file_mtime': mtime,
                'filename': fname,
            }
            all_records.append(record)
    
    except Exception as e:
        pass

print(f"   共找到 {len(all_records)} 条目标场景记录")

# 按场景分组统计
print("\n3. 按场景分组统计（全部数据）...")

scenario_groups = defaultdict(list)
for r in all_records:
    scenario_groups[r['scenario']].append(r)

for scenario, records in scenario_groups.items():
    records.sort(key=lambda x: x['file_mtime'])
    scores = [r['score'] for r in records if r['score'] is not None]
    accs = [r['accuracy'] for r in records if r['accuracy'] is not None]
    
    print(f"\n   【{scenario}】{len(records)} 轮（全部）")
    if scores:
        print(f"      分数: {[f'{s:.1f}' for s in scores]}")
        print(f"      平均: {sum(scores)/len(scores):.1f}, 最高: {max(scores):.1f}, 最低: {min(scores):.1f}")
    if accs:
        print(f"      平均命中率: {sum(accs)/len(accs):.2%}")

# 查询 InfluxDB 中已有的加练数据，避免重复
print("\n4. 查询 InfluxDB 中已有的加练数据...")

flux_existing = f'''
from(bucket: "{BUCKET}")
  |> range(start: -2d)
  |> filter(fn: (r) => r._measurement == "kovaaks_score")
  |> filter(fn: (r) => r.type == "extra")
  |> filter(fn: (r) => r.daylist == "{EXTRA_ID}")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "scenario", "_value"])
  |> sort(columns: ["_time"])
'''

query_response = requests.post(
    f"{INFLUX_URL}/api/v2/query",
    headers={"Authorization": f"Token {TOKEN}", "Content-Type": "application/vnd.flux"},
    params={"org": ORG},
    data=flux_existing,
    timeout=30
)

existing_timestamps = set()
if query_response.status_code == 200:
    lines_out = query_response.text.strip().split("\n")
    # 跳过表头
    for line in lines_out[1:]:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 4:
                try:
                    ts = parts[3].strip()
                    existing_timestamps.add(ts)
                except:
                    pass

print(f"   InfluxDB 中已有 {len(existing_timestamps)} 条加练数据")

# 找出新的数据（时间戳不在已有集合中的）
print("\n5. 筛选新增数据...")

new_records = []
for r in all_records:
    ts_ns = int(r['file_mtime'].timestamp() * 1000000000)
    # InfluxDB 返回的时间戳格式可能是 RFC3339，需要转换比较
    # 改用分数+场景+时间的组合来判断是否重复
    ts_str = r['file_mtime'].strftime('%Y-%m-%dT%H:%M:%S')
    # 简单判断：如果文件修改时间在最近 1 小时内，认为是新数据
    if (now - r['file_mtime']).total_seconds() < 3600:
        new_records.append(r)
        print(f"   🆕 {r['scenario']}: score={r['score']}, time={r['file_mtime']}")

if not new_records:
    print("   没有找到最近 1 小时内的新数据")
    # 列出所有数据的时间，让用户确认
    print("\n   所有数据的时间:")
    for r in all_records:
        print(f"      {r['file_mtime']} - {r['scenario']} - {r['score']}")

# 写入新增数据
if new_records:
    print(f"\n6. 写入 {len(new_records)} 条新增数据...")
    
    lines = []
    for r in new_records:
        scenario = r['scenario']
        scenario_tag = scenario.replace(' ', '\\ ').replace(',', '\\,')
        ts_ns = int(r['file_mtime'].timestamp() * 1000000000)
        
        fields = []
        if r['score'] is not None:
            fields.append(f"score={r['score']}")
        if r['hit_count'] is not None:
            fields.append(f"hit_count={r['hit_count']}i")
        if r['miss_count'] is not None:
            fields.append(f"miss_count={r['miss_count']}i")
        if r['accuracy'] is not None:
            fields.append(f"accuracy={r['accuracy']:.6f}")
        
        if fields:
            fields_str = ','.join(fields)
            line = f"kovaaks_score,scenario={scenario_tag},type=extra,daylist={EXTRA_ID},parent_daylist={PARENT_DAYLIST} {fields_str} {ts_ns}"
            lines.append(line)
    
    body = "\n".join(lines)
    response = requests.post(write_url, headers=headers, data=body.encode("utf-8"))
    print(f"   写入结果: HTTP {response.status_code}")
    if response.status_code == 204:
        print("   ✅ 新增数据写入成功！")
    else:
        print(f"   ❌ 写入失败: {response.text}")

print("\n" + "=" * 80)
print("✅ 全部任务完成")
print("=" * 80)
