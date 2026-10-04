import sys
sys.path.insert(0, r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\web\backend')

from app.repositories import queries

# 测试 get_daylist_extras
extras = queries.get_daylist_extras("Day4")
print(f"get_daylist_extras('Day4') 返回 {len(extras)} 个:")
for extra in extras:
    print(f"  - {extra}")

print()

# 测试 get_daylist_meta
meta = queries.get_daylist_meta("Day4-extra-1")
print(f"get_daylist_meta('Day4-extra-1'):")
print(f"  {meta}")
