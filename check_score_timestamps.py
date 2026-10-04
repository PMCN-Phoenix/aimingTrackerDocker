import requests

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 查询最近 7 天的成绩数据，看看时间戳
query = f'''
from(bucket: "{bucket}")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r._field == "score")
  |> keep(columns: ["_time", "scenario", "_value"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 10)
'''

body = {'query': query}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, json=body)

print("=== 最近 10 条成绩数据的时间 ===")
print(response.text)

# 再看看 Day4 的时间范围对应的时间
print("\n=== Day4 时间范围 ===")
print("start_ts: 1790841600")
print("end_ts: 1790927999")

from datetime import datetime
print("start 对应时间:", datetime.utcfromtimestamp(1790841600))
print("end 对应时间:", datetime.utcfromtimestamp(1790927999))
