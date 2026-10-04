"""
整理"确认感"的原理级别拆解
"""
import json

# 读取搜索结果
with open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\确认感-搜索结果.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 筛选最有价值的内容
valuable = []
for r in results:
    content = r.get('content', '')
    # 筛选包含关键概念的内容
    key_concepts = ['确认感', '准星确认', '微调确认', '确认目标', '确认速度', '确认准确度', '先确认', '确认再开枪', '重合的那种确认感']
    if any(kc in content for kc in key_concepts):
        valuable.append(r)

print(f"筛选出 {len(valuable)} 条高价值内容")
print()

# 输出
for i, r in enumerate(valuable[:50], 1):
    print(f"{i}. [{r['file']}]")
    print(f"   {r['content'][:400]}")
    print()
