"""
录入 Day6 加练数据（VT摸底+冲卡口）
- VT Controlsphere Viscose Easier ×4
- Air CELESTIAL No UFO Easier ×2
标记为 type=extra, daylist=Day6-extra-1
"""
import os
import csv
import json
import requests
from datetime import datetime, timedelta

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

print("=" * 80)
print("📥 Day6 加练数据录入")
print("=" * 80)

# 1. 扫描最近的 stats 文件
print("\n1. 扫描 Kovaak's stats 目录...")

# 获取最近 2 天的文件
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

# 2. 解析每个文件，提取目标场景数据
print("\n2. 解析 stats 文件，提取目标场景数据...")

all_records = []

for fpath, mtime, fname in stats_files:
    try:
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        # 查找汇总行（通常在文件末尾）
        scenario = None
        score = None
        hit_count = None
        miss_count = None
        challenge_start = None
        
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
                elif key == 'Challenge Start:':
                    challenge_start = val
        
        # 检查是否是目标场景
        if scenario and any(ts.lower() in scenario.lower() for ts in TARGET_SCENARIOS):
            # 计算命中率
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
                'challenge_start': challenge_start,
                'file_mtime': mtime,
                'filename': fname,
            }
            all_records.append(record)
            print(f"   ✅ {scenario}: score={score}, hits={hit_count}, misses={miss_count}, acc={accuracy:.2%}" if accuracy else f"   ✅ {scenario}: score={score}")
    
    except Exception as e:
        print(f"   ⚠️ 解析失败 {fname}: {e}")

print(f"\n   共找到 {len(all_records)} 条目标场景记录")

# 3. 按场景分组统计
print("\n3. 按场景分组统计...")

from collections import defaultdict
scenario_groups = defaultdict(list)
for r in all_records:
    scenario_groups[r['scenario']].append(r)

for scenario, records in scenario_groups.items():
    records.sort(key=lambda x: x['file_mtime'])
    scores = [r['score'] for r in records if r['score'] is not None]
    accs = [r['accuracy'] for r in records if r['accuracy'] is not None]
    
    print(f"\n   【{scenario}】{len(records)} 轮")
    if scores:
        print(f"      分数: {scores}")
        print(f"      平均: {sum(scores)/len(scores):.1f}, 最高: {max(scores):.1f}, 最低: {min(scores):.1f}")
    if accs:
        print(f"      命中率: {[f'{a:.1%}' for a in accs]}")
        print(f"      平均命中率: {sum(accs)/len(accs):.2%}")

# 4. 写入 InfluxDB
print("\n4. 写入 InfluxDB...")

lines = []
for r in all_records:
    scenario = r['scenario']
    # tag 值中的空格需要转义
    scenario_tag = scenario.replace(' ', '\\ ').replace(',', '\\,')
    
    # 时间戳：用文件修改时间（纳秒）
    ts_ns = int(r['file_mtime'].timestamp() * 1000000000)
    
    # 构造 fields
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
        # 加练数据标记：type=extra, daylist=Day6-extra-1, parent_daylist=Day6
        line = f"kovaaks_score,scenario={scenario_tag},type=extra,daylist={EXTRA_ID},parent_daylist={PARENT_DAYLIST} {fields_str} {ts_ns}"
        lines.append(line)

print(f"   构造 {len(lines)} 行 Line Protocol")

# 写入
write_url = f"{INFLUX_URL}/api/v2/write?org={ORG}&bucket={BUCKET}"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "text/plain; charset=utf-8"
}
body = "\n".join(lines)

response = requests.post(write_url, headers=headers, data=body.encode("utf-8"))

print(f"   写入结果: HTTP {response.status_code}")
if response.status_code == 204:
    print("   ✅ 加练数据写入成功！")
else:
    print(f"   ❌ 写入失败: {response.text}")

# 5. 验证写入
print("\n5. 验证写入...")

flux = f'''
from(bucket: "{BUCKET}")
  |> range(start: -2d)
  |> filter(fn: (r) => r._measurement == "kovaaks_score")
  |> filter(fn: (r) => r.type == "extra")
  |> filter(fn: (r) => r.daylist == "{EXTRA_ID}")
  |> keep(columns: ["_time", "scenario", "score", "accuracy", "daylist", "type"])
  |> sort(columns: ["_time"])
'''

query_response = requests.post(
    f"{INFLUX_URL}/api/v2/query",
    headers={
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/vnd.flux"
    },
    params={"org": ORG},
    data=flux,
    timeout=30
)

print(f"   查询结果: HTTP {query_response.status_code}")
if query_response.status_code == 200:
    lines_out = query_response.text.strip().split("\n")
    print(f"   返回 {len(lines_out)} 行（含表头）")
    for line in lines_out[:10]:
        print(f"   {line}")
else:
    print(f"   查询失败: {query_response.text}")

print("\n" + "=" * 80)
print("✅ 加练数据录入完成")
print("=" * 80)
