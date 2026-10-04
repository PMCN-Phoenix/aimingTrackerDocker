import requests

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询 Day4-extra-1 的所有元数据
query = '''
from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "Day4-extra-1")
  |> keep(columns: ["_value", "_field", "daylist"])
'''

body = {'query': query}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body)
print("=== Day4-extra-1 元数据 ===")
print(response.text)
print()

# 查询所有 parent_daylist 字段
query2 = '''
from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "parent_daylist")
  |> keep(columns: ["_value", "_field", "daylist"])
'''

body2 = {'query': query2}
response2 = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body2)
print("=== 所有 parent_daylist 字段 ===")
print(response2.text)
