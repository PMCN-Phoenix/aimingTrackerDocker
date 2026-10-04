"""
调试创建感悟的 Line Protocol 格式
"""
import requests
import time

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

# Popcorn 感悟
scenario = 'Popcorn MV Easier'
note = '先盯着目标做粗跟枪，差不多把控轨迹之后看准星做定位'
daylist = 'Day5'

ts = int(time.time())

# 方法1：使用项目中的转义方式
scenario_escaped = scenario.replace(' ', '\\ ').replace(',', '\\,')
daylist_escaped = daylist.replace(' ', '\\ ').replace(',', '\\,')
note_escaped = note.replace(',', '\\,').replace(' ', '\\ ')

line1 = f'aim_reflection,scenario={scenario_escaped},daylist={daylist_escaped} note="{note_escaped}" {ts * 1000000000}'

print("方法1（项目中的转义）:")
print(f"  {line1}")
print()

# 方法2：不转义 note 中的逗号和空格（因为在双引号内）
line2 = f'aim_reflection,scenario={scenario_escaped},daylist={daylist_escaped} note="{note}" {ts * 1000000000}'

print("方法2（不转义 note）:")
print(f"  {line2}")
print()

# 尝试方法2
write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}

print("尝试方法2...")
response = requests.post(write_url, headers=write_headers, data=line2.encode('utf-8'))
print(f"  状态码: {response.status_code}")
print(f"  响应: {response.text}")

if response.status_code == 204:
    print("  ✅ 写入成功！")
else:
    print("  ❌ 写入失败")
    # 尝试方法1
    print()
    print("尝试方法1...")
    response = requests.post(write_url, headers=write_headers, data=line1.encode('utf-8'))
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.text}")
