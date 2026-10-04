import requests
import json

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 先删除 Day4 的所有行数据
delete_url = f'{influx_url}/api/v2/delete?org={org}&bucket={bucket}'
delete_body = {
    "start": "1970-01-01T00:00:00Z",
    "stop": "2099-12-31T23:59:59Z",
    "predicate": '_measurement="aim_daylist" AND daylist="Day4"'
}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(delete_url, headers=headers, json=delete_body)
print(f"删除 Day4 旧行数据状态: {response.status_code}")

# 重新导入 Day4 行数据
ts = 1790841600  # Day4 的 start_ts

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
        'scenario': 'SmoothBot Perfected Easier',
        'role': '主项',
        'rounds': 8
    },
    {
        'order': 4,
        'scenario': 'Smoothsphere Viscose Easier',
        'role': '主项',
        'rounds': 4
    },
    {
        'order': 5,
        'scenario': 'Popcorn MV Easier',
        'role': '巩固',
        'rounds': 4
    },
    {
        'order': 6,
        'scenario': 'Flower Easier 50cm',
        'role': '巩固',
        'rounds': 4
    },
    {
        'order': 7,
        'scenario': 'Pasu Voltaic Reload Easier',
        'role': '巩固',
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
    line = f'aim_daylist,daylist=Day4,scenario={scenario_tag},role={role_tag} rowJson="{row_json}" {ts}'
    lines.append(line)

# 写入
write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
body = '\n'.join(lines)
response = requests.post(write_url, headers=write_headers, data=body.encode('utf-8'))
print(f"写入 Day4 新行数据状态: {response.status_code}")

print("\n完成！Day4 行数据已修复")
