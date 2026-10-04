import requests
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
print(f"start_ts: {start_ts}")
print(f"end_ts: {end_ts}")

# 用 start_ts + 100 作为写入时间戳，避免和 Day4 的时间戳冲突
ts = start_ts + 100

# 写入元数据，每一行单独写入，确保都能成功
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
    if response.status_code != 204:
        print(f"  失败: {response.text}")

print("\nDay5 元数据写入完成！")
