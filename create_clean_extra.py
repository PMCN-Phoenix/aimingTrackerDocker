import requests
import json

# 1. 用英文名称创建新的加练清单
print("=" * 60)
print("1. 创建新的加练清单（英文名称）")
print("=" * 60)

payload = {
    "parent_daylist": "Day4",
    "name": "Popcorn Extra - Relax and Apex",
    "exec_dates": "2026-10-03",
    "items": [
        {
            "scenario": "Popcorn MV Easier",
            "role": "Main",
            "rounds": 4,
            "order": 1
        },
        {
            "scenario": "SmoothBot Perfected Easier",
            "role": "Warmup",
            "rounds": 2,
            "order": 2
        }
    ]
}

r = requests.post('http://127.0.0.1:8000/api/daylists/extras', json=payload)
result = r.json()
print(f"创建结果: code={result['code']}")
if result['code'] == 0:
    data = result['data']
    print(f"  daylist: {data['daylist']}")
    print(f"  name: {data['name']}")
    print(f"  type: {data['type']}")
    print(f"  parent_daylist: {data['parent_daylist']}")
    new_daylist = data['daylist']
else:
    print(f"  错误: {result.get('message')}")
    new_daylist = None

# 2. 导出到 Kovaak's
if new_daylist:
    print("\n" + "=" * 60)
    print("2. 导出到 Kovaak's")
    print("=" * 60)

    r2 = requests.post(f'http://127.0.0.1:8000/api/daylists/{new_daylist}/export-playlist')
    result2 = r2.json()
    print(f"导出结果: code={result2['code']}")
    if result2['code'] == 0:
        data2 = result2['data']
        print(f"  文件名: {data2['filename']}")
        print(f"  已复制到 Kovaak's: {data2['copied_to_kovaaks']}")
        print(f"  路径: {data2['kovaaks_path']}")
    else:
        print(f"  错误: {result2.get('message')}")

    # 3. 查询进度
    print("\n" + "=" * 60)
    print("3. 查询加练清单进度")
    print("=" * 60)

    r3 = requests.get(f'http://127.0.0.1:8000/api/daylists/{new_daylist}/progress')
    result3 = r3.json()
    if result3['code'] == 0:
        data3 = result3['data']
        print(f"  清单: {data3['daylist']}")
        print(f"  类型: {data3['type']}")
        print(f"  场景数: {len(data3['rows'])}")
        for row in data3['rows']:
            print(f"    - {row['scenario']}: {row['role']}, 要求{row['required_rounds']}轮, 已打{row['done_rounds']}轮, {row['status']}")
    else:
        print(f"  错误: {result3.get('message')}")

# 4. 列出当前所有加练清单
print("\n" + "=" * 60)
print("4. 当前所有加练清单")
print("=" * 60)

r4 = requests.get('http://127.0.0.1:8000/api/daylists/Day4/extras')
extras = r4.json()['data']
for e in extras:
    print(f"  {e['daylist']}: {e.get('name', '无名称')}, type={e.get('type', '无')}")
