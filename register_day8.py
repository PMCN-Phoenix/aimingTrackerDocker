# -*- coding: utf-8 -*-
"""注册 Day8 清单到 InfluxDB"""
import urllib.request
import json
import time
from datetime import datetime

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"

def write(lines):
    if not lines:
        return
    data = "\n".join(lines).encode("utf-8")
    req = urllib.request.Request(
        f"{INFLUX}/api/v2/write?org={ORG}&bucket={BUCKET}&precision=ns",
        data=data, method="POST")
    req.add_header("Authorization", f"Token {TOKEN}")
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status

# Day8 配置
DAYLIST = "Day8"
LABEL = "攻Blending"
RUN_DATE = "2026-10-06"

# 计算时间戳
start_dt = datetime(2026, 10, 6, 0, 0, 0)
end_dt = datetime(2026, 10, 6, 23, 59, 59)
start_ts = int(start_dt.timestamp())
end_ts = int(end_dt.timestamp())
timestamp_ns = int(start_dt.timestamp() * 1e9)

# 场景列表
scenarios = [
    {"scenario": "1w2ts reload smallflicks larger", "rounds": 2, "role": "热身", "order": 1},
    {"scenario": "ww5t Voltaic Slightly Larger", "rounds": 2, "role": "热身", "order": 2},
    {"scenario": "Air Voltaic Easy", "rounds": 2, "role": "主项", "order": 3},
    {"scenario": "Air CELESTIAL No UFO Easier", "rounds": 4, "role": "主项", "order": 4},
    {"scenario": "Popcorn MV Easier", "rounds": 4, "role": "长期最弱项", "order": 5},
    {"scenario": "cloverRawControl Viscose Easier 50cm", "rounds": 4, "role": "Fingertip巩固", "order": 6},
    {"scenario": "SmoothBot Perfected Easier", "rounds": 4, "role": "Arm保持", "order": 7},
    {"scenario": "Controlsphere SuperbAim Viscose Easier", "rounds": 1, "role": "收尾验收", "order": 8},
]

items = len(scenarios)
rounds_total = sum(s["rounds"] for s in scenarios)

print(f"=== 注册 Day8 清单 ===")
print(f"  label: {LABEL}")
print(f"  run_date: {RUN_DATE}")
print(f"  items: {items}")
print(f"  rounds_total: {rounds_total}")
print(f"  start_ts: {start_ts}")
print(f"  end_ts: {end_ts}")
print()

# 1. 写入元数据
meta_lines = []
tags = f'daylist={DAYLIST},label={LABEL}'

# run_date (string)
meta_lines.append(f'aim_daylist_meta,{tags} run_date="{RUN_DATE}" {timestamp_ns}')
# exec_dates (string)
meta_lines.append(f'aim_daylist_meta,{tags} exec_dates="{RUN_DATE}" {timestamp_ns}')
# start_ts (integer)
meta_lines.append(f'aim_daylist_meta,{tags} start_ts={start_ts}i {timestamp_ns}')
# end_ts (integer)
meta_lines.append(f'aim_daylist_meta,{tags} end_ts={end_ts}i {timestamp_ns}')
# items (integer)
meta_lines.append(f'aim_daylist_meta,{tags} items={items}i {timestamp_ns}')
# rounds_total (integer)
meta_lines.append(f'aim_daylist_meta,{tags} rounds_total={rounds_total}i {timestamp_ns}')

print("写入元数据...")
status = write(meta_lines)
print(f"  状态码: {status}")
print()

# 2. 写入场景列表
row_lines = []
for s in scenarios:
    row_json = json.dumps(s, ensure_ascii=False)
    # 转义 rowJson 中的双引号
    row_json_escaped = row_json.replace('\\', '\\\\').replace('"', '\\"')
    scenario_escaped = s["scenario"].replace(" ", "\\ ")
    role_escaped = s["role"].replace(" ", "\\ ")
    tags = f'daylist={DAYLIST},scenario={scenario_escaped},role={role_escaped}'
    row_lines.append(f'aim_daylist,{tags} rowJson="{row_json_escaped}" {timestamp_ns}')

print("写入场景列表...")
status = write(row_lines)
print(f"  状态码: {status}")
print()

print("✅ Day8 清单注册完成！")
print(f"  访问: http://localhost:5173/daylist/Day8")
