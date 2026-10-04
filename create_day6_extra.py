"""
在 InfluxDB 中创建 Day6 加练清单元数据
"""
import requests
from datetime import datetime

INFLUX_URL = "http://127.0.0.1:8087"
TOKEN = "aim-super-secret-token-2026"
ORG = "aim-org"
BUCKET = "aim"

now_ts = int(datetime.now().timestamp())
now_ns = now_ts * 1000000000

# 加练清单元数据
extra_id = "Day6-extra-1"
name = "VT摸底+冲卡口"
parent_daylist = "Day6"
created_at = now_ts

print(f"创建加练清单: {extra_id}")
print(f"  名称: {name}")
print(f"  父级: {parent_daylist}")
print(f"  时间戳: {now_ts} ({datetime.fromtimestamp(now_ts)})")

# 构造 Line Protocol
lines = []

# meta 记录 - tag 值中的空格和特殊字符需要转义
# label 中有中文和加号，InfluxDB tag 值可以包含中文，但空格需要转义
label_tag = name.replace(" ", "\\ ")
lines.append(
    f'aim_daylist_meta,daylist={extra_id},label={label_tag},type=extra,parent_daylist={parent_daylist} '
    f'created_at={created_at}i {now_ns}'
)

# 清单项
items = [
    ("VT Controlsphere Viscose Easier", "extra", 4, 1),
    ("Air CELESTIAL No UFO Easier", "extra", 2, 2),
]

for scenario, role, rounds, order in items:
    scenario_tag = scenario.replace(" ", "\\ ").replace(",", "\\,")
    lines.append(
        f'aim_daylist_item,daylist={extra_id},scenario={scenario_tag},role={role},order={order}i '
        f'rounds={rounds}i {now_ns}'
    )

print(f"\n构造 {len(lines)} 行 Line Protocol:")
for line in lines:
    print(f"  {line}")

# 写入 InfluxDB
write_url = f"{INFLUX_URL}/api/v2/write?org={ORG}&bucket={BUCKET}"
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "text/plain; charset=utf-8"
}
body = "\n".join(lines)

response = requests.post(write_url, headers=headers, data=body.encode("utf-8"))

print(f"\n写入结果: HTTP {response.status_code}")
if response.status_code == 204:
    print("✅ 加练清单元数据写入成功！")
else:
    print(f"❌ 写入失败: {response.text}")

# 验证写入
print("\n=== 验证写入 ===")
flux = f'''
from(bucket: "{BUCKET}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r.daylist == "{extra_id}")
  |> keep(columns: ["_time", "daylist", "label", "type", "parent_daylist", "created_at"])
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

print(f"查询结果: HTTP {query_response.status_code}")
if query_response.status_code == 200:
    lines_out = query_response.text.strip().split("\n")
    print(f"返回 {len(lines_out)} 行")
    for line in lines_out[:5]:
        print(f"  {line}")
