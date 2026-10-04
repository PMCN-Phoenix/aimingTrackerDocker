import requests
import time

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

ts = int(time.time())
ts_ns = ts * 1000000000

# 测试写入一条简单的数据
line = f'aim_daylist_meta,daylist=Day4-extra-test type="extra" {ts_ns}'
print(f"写入: {line}")

write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain'}
response = requests.post(write_url, headers=write_headers, data=line.encode('utf-8'))
print(f"写入状态: {response.status_code}")
print(f"写入响应: {response.text}")

# 等待一下
time.sleep(1)

# 查询
query = '''
from(bucket: "aim")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "Day4-extra-test")
  |> keep(columns: ["_value", "_field", "daylist"])
'''

query_url = f'{influx_url}/api/v2/query?org={org}'
query_headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/vnd.flux'}
response2 = requests.post(query_url, headers=query_headers, data=query.encode('utf-8'))
print(f"\n查询结果:")
print(response2.text)
