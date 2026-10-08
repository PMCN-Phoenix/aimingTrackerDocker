# -*- coding: utf-8 -*-
"""更新 Day8 清单的执行日期为 2026-10-08"""
import urllib.request
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

# Day8 新日期
NEW_DATE = "2026-10-08"
start_dt = datetime(2026, 10, 8, 0, 0, 0)
end_dt = datetime(2026, 10, 8, 23, 59, 59)
start_ts = int(start_dt.timestamp())
end_ts = int(end_dt.timestamp())
timestamp_ns = int(start_dt.timestamp() * 1e9)

DAYLIST = "Day8"
LABEL = "攻Blending"

print(f"=== 更新 Day8 清单执行日期 ===")
print(f"  旧日期: 2026-10-06")
print(f"  新日期: {NEW_DATE}")
print(f"  start_ts: {start_ts}")
print(f"  end_ts: {end_ts}")
print()

# 写入新的元数据（会覆盖旧的，因为时间戳相同但值不同）
tags = f'daylist={DAYLIST},label={LABEL}'
lines = [
    f'aim_daylist_meta,{tags} run_date="{NEW_DATE}" {timestamp_ns}',
    f'aim_daylist_meta,{tags} exec_dates="{NEW_DATE}" {timestamp_ns}',
    f'aim_daylist_meta,{tags} start_ts={start_ts}i {timestamp_ns}',
    f'aim_daylist_meta,{tags} end_ts={end_ts}i {timestamp_ns}',
]

status = write(lines)
print(f"写入状态码: {status}")
print()
print("✅ Day8 清单执行日期已更新为 2026-10-08")
