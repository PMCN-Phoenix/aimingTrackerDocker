import sys
sys.path.insert(0, r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\web\backend')

from app.repositories import queries

# 测试 get_daylist_progress
print("测试 get_daylist_progress('Day5-extra-1')...")
try:
    result = queries.get_daylist_progress('Day5-extra-1')
    print(f"  成功! 类型: {type(result)}")
    if result:
        print(f"  daylist: {result.get('daylist')}")
        print(f"  场景数: {len(result.get('rows', []))}")
        for row in result.get('rows', []):
            print(f"    - {row['scenario']}: {row['role']}, 要求{row['required_rounds']}轮, 已打{row['done_rounds']}轮")
except Exception as e:
    print(f"  失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 get_daylist_extras
print("\n测试 get_daylist_extras('Day5')...")
try:
    result = queries.get_daylist_extras('Day5')
    print(f"  成功! 数量: {len(result)}")
    for extra in result:
        print(f"    - {extra.get('daylist')}: {extra.get('name')}, 场景数: {len(extra.get('rows', []))}")
except Exception as e:
    print(f"  失败: {e}")
    import traceback
    traceback.print_exc()
