import requests
import json
from datetime import datetime, timedelta

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 计算北京时间 10/03 的时间戳
beijing_offset = 8 * 3600
first_date = datetime.strptime('2026-10-03', '%Y-%m-%d')
start_ts = int(first_date.timestamp()) - beijing_offset
last_dt = first_date + timedelta(days=1) - timedelta(seconds=1)
end_ts = int(last_dt.timestamp()) - beijing_offset

print(f"Day5 日期: 2026-10-03")
print(f"start_ts: {start_ts}")
print(f"end_ts: {end_ts}")

ts = start_ts

# 写入元数据
meta_lines = f'''aim_daylist_meta,daylist=Day5 start_ts={start_ts} {ts}
aim_daylist_meta,daylist=Day5 end_ts={end_ts} {ts}
aim_daylist_meta,daylist=Day5 run_date="2026-10-03" {ts}
aim_daylist_meta,daylist=Day5 exec_dates="2026-10-03" {ts}
aim_daylist_meta,daylist=Day5 items=8 {ts}
aim_daylist_meta,daylist=Day5 rounds_total=29 {ts}
aim_daylist_meta,daylist=Day5 label="Day5 攻Precision" {ts}'''

write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
response = requests.post(write_url, headers=write_headers, data=meta_lines.encode('utf-8'))
print(f"写入元数据状态: {response.status_code}")

# 行数据
rows = [
    {
        'order': 1,
        'scenario': '1w2ts reload smallflicks larger',
        'role': '热身',
        'rounds': 2
    },
    {
        'order': 2,
        'scenario': 'ww5t Voltaic Slightly Larger',
        'role': '热身',
        'rounds': 2
    },
    {
        'order': 3,
        'scenario': 'Popcorn MV Easier',
        'role': '主项',
        'rounds': 8
    },
    {
        'order': 4,
        'scenario': 'cloverRawControl Viscose Easier 50cm',
        'role': '第二主项',
        'rounds': 4
    },
    {
        'order': 5,
        'scenario': 'SmoothBot Perfected Easier',
        'role': '保持',
        'rounds': 4
    },
    {
        'order': 6,
        'scenario': 'Flower Easier 50cm',
        'role': '保持',
        'rounds': 4
    },
    {
        'order': 7,
        'scenario': 'Pasu Voltaic Reload Easier',
        'role': '维护',
        'rounds': 4
    },
    {
        'order': 8,
        'scenario': 'Air CELESTIAL No UFO Easier',
        'role': '卡口',
        'rounds': 1
    }
]

# 构建 Line Protocol
lines = []
for row in rows:
    scenario_tag = row['scenario'].replace(' ', '\\ ').replace(',', '\\,')
    role_tag = row['role']
    row_json = json.dumps(row, ensure_ascii=False).replace('"', '\\"')
    line = f'aim_daylist,daylist=Day5,scenario={scenario_tag},role={role_tag} rowJson="{row_json}" {ts}'
    lines.append(line)

# 写入行数据
body = '\n'.join(lines)
response = requests.post(write_url, headers=write_headers, data=body.encode('utf-8'))
print(f"写入行数据状态: {response.status_code}")

print("\n完成！Day5 清单已导入 InfluxDB")
