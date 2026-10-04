import requests
import json

# 1. 直接查询 InfluxDB，看看 Day5-extra-1 的元数据是否存在
print("=" * 60)
print("1. 查询 Day5-extra-1 元数据")
print("=" * 60)

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'

query = '''
from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r.daylist == "Day5-extra-1")
  |> keep(columns: ["_value", "_field", "daylist"])
'''

headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/vnd.flux'}
response = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, data=query.encode('utf-8'))
print("元数据查询结果:")
print(response.text[:500])

# 2. 查询 parent_daylist = Day5 的所有元数据
print("\n" + "=" * 60)
print("2. 查询 parent_daylist = Day5 的所有元数据")
print("=" * 60)

query2 = '''
from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "parent_daylist")
  |> keep(columns: ["_value", "daylist"])
'''

response2 = requests.post(f'{influx_url}/api/v2/query?org={org}', headers=headers, data=query2.encode('utf-8'))
print("所有 parent_daylist:")
print(response2.text[:1000])

# 3. 测试 API
print("\n" + "=" * 60)
print("3. 测试 API")
print("=" * 60)

# 测试 Day5 加练列表
r = requests.get('http://127.0.0.1:8000/api/daylists/Day5/extras')
print(f"Day5 加练列表: code={r.json()['code']}, count={len(r.json()['data'])}")

# 测试 Day4 加练列表
r2 = requests.get('http://127.0.0.1:8000/api/daylists/Day4/extras')
print(f"Day4 加练列表: code={r2.json()['code']}, count={len(r2.json()['data'])}")

# 测试 Day5-extra-1 进度
r3 = requests.get('http://127.0.0.1:8000/api/daylists/Day5-extra-1/progress')
print(f"Day5-extra-1 进度: code={r3.json()['code']}")
if r3.json()['code'] == 0:
    data = r3.json()['data']
    print(f"  场景数: {len(data.get('rows', []))}")
else:
    print(f"  错误: {r3.json().get('message')}")
