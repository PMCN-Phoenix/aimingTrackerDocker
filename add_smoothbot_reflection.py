"""
记录用户自己的感悟到 SmoothBot Perfected Easier
"""
import requests
import json
from datetime import datetime

# InfluxDB 配置
INFLUX_URL = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"

# 感悟内容
scenario = "SmoothBot Perfected Easier"
note = "专注于物体和手部动作做速度匹配"
timestamp = int(datetime.now().timestamp())

# 构造 Line Protocol（纳秒级时间戳）
# tag 值中的空格需要用反斜杠转义，不需要引号
# field 值（字符串）需要双引号，note 在双引号内不需要转义逗号和空格
scenario_escaped = scenario.replace(" ", "\\ ")
line = f'aim_reflection,scenario={scenario_escaped} note="{note}" {timestamp * 1000000000}'

print(f"写入感悟:")
print(f"  场景: {scenario}")
print(f"  感悟: {note}")
print(f"  时间: {datetime.fromtimestamp(timestamp)}")
print(f"  Line Protocol: {line}")

# 写入 InfluxDB
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "text/plain; charset=utf-8"
}
params = {
    "org": ORG,
    "bucket": BUCKET
}

response = requests.post(
    f"{INFLUX_URL}/api/v2/write",
    headers=headers,
    params=params,
    data=line.encode("utf-8"),
    timeout=30
)

print(f"\n写入结果: HTTP {response.status_code}")
if response.status_code == 204:
    print("✅ 感悟写入成功！")
else:
    print(f"❌ 写入失败: {response.text}")

# 验证写入
print("\n=== 验证写入 ===")
flux = f'''
from(bucket: "{BUCKET}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "aim_reflection")
  |> filter(fn: (r) => r.scenario == "{scenario}")
  |> keep(columns: ["_time", "note"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 5)
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
    lines = query_response.text.strip().split("\n")
    print(f"返回 {len(lines)} 行")
    for line in lines[:10]:
        print(f"  {line}")
