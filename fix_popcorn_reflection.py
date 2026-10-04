import requests
import time

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# 先删除旧的 Popcorn 感悟
delete_url = f'{influx_url}/api/v2/delete?org={org}&bucket={bucket}'
delete_body = {
    "start": "1970-01-01T00:00:00Z",
    "stop": "2099-12-31T23:59:59Z",
    "predicate": '_measurement="aim_reflection" AND scenario="Popcorn MV Easier"'
}
headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
response = requests.post(delete_url, headers=headers, json=delete_body)
print(f"删除旧感悟状态: {response.status_code}")

# 重新写入正确格式的感悟
scenario = 'Popcorn MV Easier'
note = '肩部绷紧肩袖发力，上下移动，卡手需要调整手腕到舒适状态'
ts = int(time.time())

# tag 值转义（场景名里的空格）
scenario_tag = scenario.replace(' ', '\\ ').replace(',', '\\,')

# note 里的逗号和空格要转义（按照后端代码的逻辑）
note_escaped = note.replace(',', '\\,').replace(' ', '\\ ')

# 构建 Line Protocol（纳秒级时间戳）
line = f'aim_reflection,scenario={scenario_tag} note="{note_escaped}" {ts * 1000000000}'

print(f"写入感悟: {line}")

# 写入
write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=ns'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
response = requests.post(write_url, headers=write_headers, data=line.encode('utf-8'))
print(f"写入状态: {response.status_code}")

if response.status_code == 204:
    print("感悟写入成功！")
else:
    print(f"写入失败: {response.text}")
