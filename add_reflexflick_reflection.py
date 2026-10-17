"""
记录用户自己的感悟到 Reflex Flick - Easy
（本机沙箱无 Docker/InfluxDB，此脚本需在宿主机运行；Docker 起来后执行：
  python add_reflexflick_reflection.py）
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
scenario = "Reflex Flick - Easy"
note = "在手腕放松时候更快"
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
    print("✓ 感悟已写入 InfluxDB（Web 版场景详情页可见）")
else:
    print("✗ 写入失败:", response.text[:300])
