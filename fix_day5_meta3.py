import requests
import time
from datetime import datetime, timedelta

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# Day5 日期：2026-10-03
date_str = '2026-10-03'
first_date = datetime.strptime(date_str, '%Y-%m-%d')
start_ts = int(first_date.timestamp())
last_dt = first_date + timedelta(days=1) - timedelta(seconds=1)
end_ts = int(last_dt.timestamp())

print(f"Day5 日期: {date_str}")
print(f"start_ts (字段值): {start_ts}")
print(f"end_ts (字段值): {end_ts}")

# 关键：写入时间戳用现在的时间，不能用未来的时间！
# 否则后端查询过去 30 天的数据时查不到
ts = int(time.time())
print(f"写入时间戳: {ts} (现在)")

# 先删除旧的 Day5 元数据（如果有的话）
delete_url = f'{influx_url}/api/v2/delete?org={org}&bucket={bucket}'
delete_body = {
    "start": "1970-01-01T00:00:00Z",
    "stop": "2099-12-31T23:59:59Z",
    "predicate": '_measurement="aim_daylist_meta" AND daylist="Day5"'
}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(delete_url, headers=headers, json=delete_body)
print(f"删除旧元数据状态: {response.status_code}")

# 写入元数据
lines = [
    f'aim_daylist_meta,daylist=Day5 start_ts={start_ts} {ts}',
    f'aim_daylist_meta,daylist=Day5 end_ts={end_ts} {ts}',
    f'aim_daylist_meta,daylist=Day5 run_date="{date_str}" {ts}',
    f'aim_daylist_meta,daylist=Day5 exec_dates="{date_str}" {ts}',
    f'aim_daylist_meta,daylist=Day5 items=8 {ts}',
    f'aim_daylist_meta,daylist=Day5 rounds_total=29 {ts}',
    f'aim_daylist_meta,daylist=Day5 label="Day5 攻Precision" {ts}',
]

write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}

for i, line in enumerate(lines):
    response = requests.post(write_url, headers=write_headers, data=line.encode('utf-8'))
    print(f"写入第 {i+1} 行: 状态 {response.status_code}")

print("\nDay5 元数据写入完成！")
