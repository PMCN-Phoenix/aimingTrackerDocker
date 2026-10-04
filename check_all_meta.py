import requests

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询所有 daylist_meta，不限制时间
query = '''
from(bucket: "aim")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> keep(columns: ["_field", "_value", "daylist"])
  |> limit(n: 50)
'''

body = {'query': query}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body)
print("=== 所有 daylist_meta 数据 ===")
print(response.text)
