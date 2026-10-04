"""
创建 Popcorn MV Easier 感悟（使用项目中的 create_reflection 函数）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.queries import create_reflection, get_scenario_reflections

# 创建感悟
scenario = "Popcorn MV Easier"
note = "先盯着目标做粗跟枪，差不多把控轨迹之后看准星做定位"
daylist = "Day5"

print(f"创建感悟:")
print(f"  场景: {scenario}")
print(f"  感悟: {note}")
print(f"  清单: {daylist}")
print()

try:
    result = create_reflection(scenario, note, daylist)
    print(f"✅ 感悟创建成功！")
    print(f"  结果: {result}")
except Exception as e:
    print(f"❌ 创建失败: {e}")
    import traceback
    traceback.print_exc()

# 验证
print()
print("验证感悟列表:")
reflections = get_scenario_reflections(scenario, 7)
for r in reflections:
    print(f"  - [{r['date']}] {r['note']}")
