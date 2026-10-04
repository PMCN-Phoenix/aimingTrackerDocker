import requests
import json

# 1. 先确认 Day5 主清单存在
print("=" * 60)
print("1. 确认 Day5 主清单")
print("=" * 60)

r = requests.get('http://127.0.0.1:8000/api/daylists/Day5/progress')
result = r.json()
if result['code'] == 0:
    data = result['data']
    print(f"  Day5 主清单存在，场景数: {len(data['rows'])}")
    for row in data['rows']:
        print(f"    - {row['scenario']}: {row['role']}, 要求{row['required_rounds']}轮, 已打{row['done_rounds']}轮, {row['status']}")
else:
    print(f"  Day5 主清单不存在或出错: {result.get('message')}")

# 2. 创建属于 Day5 的加练清单
print("\n" + "=" * 60)
print("2. 创建 Day5 加练清单")
print("=" * 60)

payload = {
    "parent_daylist": "Day5",
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

r2 = requests.post('http://127.0.0.1:8000/api/daylists/extras', json=payload)
result2 = r2.json()
print(f"创建结果: code={result2['code']}")
if result2['code'] == 0:
    data2 = result2['data']
    print(f"  daylist: {data2['daylist']}")
    print(f"  name: {data2['name']}")
    print(f"  type: {data2['type']}")
    print(f"  parent_daylist: {data2['parent_daylist']}")
    new_daylist = data2['daylist']
else:
    print(f"  错误: {result2.get('message')}")
    new_daylist = None

# 3. 导出到 Kovaak's
if new_daylist:
    print("\n" + "=" * 60)
    print("3. 导出到 Kovaak's")
    print("=" * 60)

    r3 = requests.post(f'http://127.0.0.1:8000/api/daylists/{new_daylist}/export-playlist')
    result3 = r3.json()
    print(f"导出结果: code={result3['code']}")
    if result3['code'] == 0:
        data3 = result3['data']
        print(f"  文件名: {data3['filename']}")
        print(f"  已复制到 Kovaak's: {data3['copied_to_kovaaks']}")
        print(f"  路径: {data3['kovaaks_path']}")
    else:
        print(f"  错误: {result3.get('message')}")

    # 4. 查询进度
    print("\n" + "=" * 60)
    print("4. 查询加练清单进度")
    print("=" * 60)

    r4 = requests.get(f'http://127.0.0.1:8000/api/daylists/{new_daylist}/progress')
    result4 = r4.json()
    if result4['code'] == 0:
        data4 = result4['data']
        print(f"  清单: {data4['daylist']}")
        print(f"  类型: {data4['type']}")
        print(f"  父级: {data4.get('parent_daylist')}")
        print(f"  场景数: {len(data4['rows'])}")
        for row in data4['rows']:
            print(f"    - {row['scenario']}: {row['role']}, 要求{row['required_rounds']}轮, 已打{row['done_rounds']}轮, {row['status']}")
    else:
        print(f"  错误: {result4.get('message')}")

    # 5. 查询 Day5 的加练列表
    print("\n" + "=" * 60)
    print("5. Day5 的加练列表")
    print("=" * 60)

    r5 = requests.get('http://127.0.0.1:8000/api/daylists/Day5/extras')
    extras = r5.json()['data']
    print(f"  Day5 共有 {len(extras)} 个加练清单:")
    for e in extras:
        print(f"    - {e['daylist']}: {e.get('name', '无名称')}, type={e.get('type', '无')}")
