import requests
import json

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'
ts = 1789977600

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
    # tag 值里的空格和逗号要转义
    scenario_tag = row['scenario'].replace(' ', '\\ ').replace(',', '\\,')
    role_tag = row['role']
    
    # field 值是 JSON 字符串，用双引号括起来，里面的双引号要转义
    row_json = json.dumps(row, ensure_ascii=False).replace('"', '\\"')
    
    line = f'aim_daylist,daylist=Day4,scenario={scenario_tag},role={role_tag} rowJson="{row_json}" {ts}'
    lines.append(line)

# 写入
body = '\n'.join(lines)
headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
response = requests.post(f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s', headers=headers, data=body.encode('utf-8'))
print(f'状态码: {response.status_code}')
print(f'响应: {response.text}')
