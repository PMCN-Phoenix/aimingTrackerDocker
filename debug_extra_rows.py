import requests
import json

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询 Day4-extra-1 的清单项
query = '''
from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist" and r.daylist == "Day4-extra-1")
  |> keep(columns: ["_value", "scenario", "role"])
'''

body = {'query': query}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/vnd.flux'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, data=query.encode('utf-8'))
print("=== Day4-extra-1 清单项 ===")
print(response.text)
print()

# 通过 API 查询
print("=== 通过 API 查询 Day4-extra-1 进度 ===")
try:
    r = requests.get("http://127.0.0.1:8000/api/daylists/Day4-extra-1/progress", timeout=10)
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text}")
except Exception as e:
    print(f"错误: {e}")
