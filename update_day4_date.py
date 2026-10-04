import requests
from datetime import datetime, timedelta

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 计算北京时间 10/02 的时间戳
beijing_offset = 8 * 3600
first_date = datetime.strptime('2026-10-02', '%Y-%m-%d')
start_ts = int(first_date.timestamp()) - beijing_offset
last_dt = first_date + timedelta(days=1) - timedelta(seconds=1)
end_ts = int(last_dt.timestamp()) - beijing_offset

print(f"Day4 新日期: 2026-10-02")
print(f"start_ts: {start_ts}")
print(f"end_ts: {end_ts}")

# 先删除旧的 Day4 元数据
delete_query = f'''
from(bucket: "{bucket}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "Day4")
'''

# 用 delete API 删除
delete_url = f'{influx_url}/api/v2/delete?org={org}&bucket={bucket}'
delete_body = {
    "start": "1970-01-01T00:00:00Z",
    "stop": "2099-12-31T23:59:59Z",
    "predicate": '_measurement="aim_daylist_meta" AND daylist="Day4"'
}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(delete_url, headers=headers, json=delete_body)
print(f"删除旧元数据状态: {response.status_code}")

# 写入新的 Day4 元数据
ts = start_ts
meta_lines = f'''aim_daylist_meta,daylist=Day4 start_ts={start_ts} {ts}
aim_daylist_meta,daylist=Day4 end_ts={end_ts} {ts}
aim_daylist_meta,daylist=Day4 run_date="2026-10-02" {ts}
aim_daylist_meta,daylist=Day4 exec_dates="2026-10-02" {ts}
aim_daylist_meta,daylist=Day4 items=8 {ts}
aim_daylist_meta,daylist=Day4 rounds_total=29 {ts}
aim_daylist_meta,daylist=Day4 label="Day4 攻Arm" {ts}'''

write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
response = requests.post(write_url, headers=write_headers, data=meta_lines.encode('utf-8'))
print(f"写入新元数据状态: {response.status_code}")
print("完成！")
