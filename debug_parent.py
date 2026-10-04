import requests
import time

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

ts = int(time.time())
ts_ns = ts * 1000000000

# 测试写入 parent_daylist 字段
line = f'aim_daylist_meta,daylist=Day4-extra-test2 parent_daylist="Day4" {ts_ns}'
print(f"写入: {line}")

write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain'}
response = requests.post(write_url, headers=write_headers, data=line.encode('utf-8'))
print(f"写入状态: {response.status_code}")

time.sleep(1)

# 查询：用 r._value == "Day4"
query = '''
from(bucket: "aim")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "parent_daylist" and r._value == "Day4")
  |> keep(columns: ["_value", "_field", "daylist"])
'''

query_url = f'{influx_url}/api/v2/query?org={org}'
query_headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/vnd.flux'}
response2 = requests.post(query_url, headers=query_headers, data=query.encode('utf-8'))
print(f"\n查询结果（_value == 'Day4'）:")
print(response2.text)

# 查询：所有 parent_daylist
query2 = '''
from(bucket: "aim")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "parent_daylist")
  |> keep(columns: ["_value", "_field", "daylist"])
'''
response3 = requests.post(query_url, headers=query_headers, data=query2.encode('utf-8'))
print(f"\n所有 parent_daylist:")
print(response3.text)
