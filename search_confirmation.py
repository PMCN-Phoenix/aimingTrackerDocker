"""
搜索"确认感"相关内容，从本地 B站调研数据中提取
"""
import json
import glob
import os
import re

# 搜索目录
DIRS = [
    r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\Popcorn专项",
    r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据",
]

# 关键词
KEYWORDS = ['确认', '确认感', '点击确认', '射击确认', '开火确认', 'trigger', 'click', 'confirmation']

results = []

def search_in_file(filepath):
    """在单个文件中搜索关键词"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # JSON 文件
        if filepath.endswith('.json'):
            try:
                data = json.loads(content)
                # 递归搜索
                def search_obj(obj, path=""):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, str):
                                for kw in KEYWORDS:
                                    if kw in v:
                                        results.append({
                                            'file': os.path.basename(filepath),
                                            'path': f"{path}.{k}",
                                            'content': v[:300],
                                            'keyword': kw
                                        })
                                        break
                            elif isinstance(v, (dict, list)):
                                search_obj(v, f"{path}.{k}")
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            if isinstance(item, str):
                                for kw in KEYWORDS:
                                    if kw in item:
                                        results.append({
                                            'file': os.path.basename(filepath),
                                            'path': f"{path}[{i}]",
                                            'content': item[:300],
                                            'keyword': kw
                                        })
                                        break
                            elif isinstance(item, (dict, list)):
                                search_obj(item, f"{path}[{i}]")
                search_obj(data)
            except:
                pass

        # 文本文件
        elif filepath.endswith('.md') or filepath.endswith('.txt'):
            lines = content.split('\n')
            for i, line in enumerate(lines):
                for kw in KEYWORDS:
                    if kw in line:
                        # 取上下文
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        context = '\n'.join(lines[start:end])
                        results.append({
                            'file': os.path.basename(filepath),
                            'line': i+1,
                            'content': context[:500],
                            'keyword': kw
                        })
                        break
    except Exception as e:
        pass

# 搜索所有文件
print("搜索'确认感'相关内容...")
for dir_path in DIRS:
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(('.json', '.md', '.txt')):
                    search_in_file(os.path.join(root, file))

print(f"找到 {len(results)} 条相关内容")
print()

# 按关键词分组
by_keyword = {}
for r in results:
    kw = r['keyword']
    if kw not in by_keyword:
        by_keyword[kw] = []
    by_keyword[kw].append(r)

print("按关键词分组:")
for kw, items in by_keyword.items():
    print(f"  {kw}: {len(items)} 条")

# 输出最相关的内容
print()
print("=" * 70)
print("最相关的内容（前 30 条）")
print("=" * 70)

# 按文件和关键词排序，优先字幕和评论
sorted_results = sorted(results, key=lambda x: (
    0 if '字幕' in x['file'] else 1 if '评论' in x['file'] else 2,
    x['keyword']
))

for i, r in enumerate(sorted_results[:30], 1):
    print(f"\n{i}. [{r['file']}] (关键词: {r['keyword']})")
    if 'line' in r:
        print(f"   行号: {r['line']}")
    print(f"   内容: {r['content'][:300]}")

# 保存结果
output_file = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\确认感-搜索结果.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n完整结果已保存到: {output_file}")
