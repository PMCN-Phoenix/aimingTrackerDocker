import requests
import json

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询 Day5 元数据
query1 = f'''
from(bucket: "{bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "Day5")
  |> keep(columns: ["_field", "_value", "daylist"])
'''

body = {'query': query1}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body)
print("=== Day5 元数据 ===")
print(response.text)

# 查询 Day5 行数据
query2 = f'''
from(bucket: "{bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist" and r.daylist == "Day5")
  |> keep(columns: ["_value", "scenario", "role"])
'''

body2 = {'query': query2}
response2 = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body2)
print("\n=== Day5 行数据 ===")
print(response2.text)
