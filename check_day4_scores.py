import requests

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询 Day4 时间范围内的成绩数据
# Day4: start_ts=1790841600, end_ts=1790927999
query = f'''
from(bucket: "{bucket}")
  |> range(start: 1790841600, stop: 1790927999)
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> keep(columns: ["_time", "_value", "_field", "scenario", "list"])
  |> limit(n: 20)
'''

body = {'query': query}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body)

print("=== Day4 时间范围内的成绩数据（前20条）===")
print(response.text)

# 再查询一下所有 aim_scenario 数据，看看 list tag 是什么
query2 = f'''
from(bucket: "{bucket}")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "aim_scenario")
  |> keep(columns: ["scenario", "list"])
  |> distinct(column: "list")
'''

body2 = {'query': query2}
response2 = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body2)
print("\n=== 所有 list tag 值 ===")
print(response2.text)
