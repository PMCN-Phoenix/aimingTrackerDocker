import requests
import json

try:
    response = requests.get("http://127.0.0.1:8000/api/daylists/Day5/progress", timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"内容长度: {len(response.content)}")
    print()

    data = response.json()
    print("=== Day5 数据 ===")
    print(f"exec_dates: {data['data']['exec_dates']}")
    print(f"场景数量: {len(data['data']['rows'])}")
    print()

    for row in data['data']['rows']:
        print(f"  - {row['scenario']}: {row['done_rounds']}/{row['required_rounds']} - {row['status']}")

except Exception as e:
    print(f"请求失败: {e}")
