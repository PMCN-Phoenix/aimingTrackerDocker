import requests
import json

# 先查询加练列表，确认创建成功
r = requests.get('http://127.0.0.1:8000/api/daylists/Day4/extras')
extras = r.json()['data']
print('当前加练清单:')
for e in extras:
    name = e.get('name', '无名称')
    daylist = e.get('daylist', '')
    etype = e.get('type', '')
    print(f'  {daylist}: {name}, type={etype}')

# 找到最新创建的加练清单（Day4-extra-11）
latest = None
for e in extras:
    if e.get('daylist') == 'Day4-extra-11':
        latest = e
        break

if not latest:
    latest = extras[-1]

print(f'\n最新加练清单: {latest["daylist"]} - {latest.get("name")}')

# 导出到 Kovaak's
print('\n导出到 Kovaak\'s...')
r2 = requests.post(f'http://127.0.0.1:8000/api/daylists/{latest["daylist"]}/export-playlist')
result = r2.json()['data']
print(f'  文件名: {result.get("filename")}')
print(f'  已复制到 Kovaak\'s: {result.get("copied_to_kovaaks")}')
print(f'  路径: {result.get("kovaaks_path")}')

# 查询进度
print('\n查询加练清单进度...')
r3 = requests.get(f'http://127.0.0.1:8000/api/daylists/{latest["daylist"]}/progress')
progress = r3.json()['data']
print(f'  清单: {progress["daylist"]}')
print(f'  类型: {progress["type"]}')
print(f'  场景数: {len(progress["rows"])}')
for row in progress['rows']:
    print(f'    - {row["scenario"]}: {row["role"]}, 要求{row["required_rounds"]}轮, 已打{row["done_rounds"]}轮, {row["status"]}')
