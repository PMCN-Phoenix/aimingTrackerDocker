"""
搜索 Air CELESTIAL No UFO Easier 相关的感悟和技巧
重点关键词：Blending、变向、持续发力、视线聚焦、平滑跟枪、混合
"""
import json
import glob
import os
from collections import defaultdict

# 搜索目录
search_dirs = [
    r"D:\11.project\iwen-codex\codex-list",
    r"D:\11.project\iwen-codex\bilibili-transcripts",
]

# Air CELESTIAL 相关关键词
keywords = [
    "blending", "Blending", "混合", "变向", "持续发力", "视线聚焦",
    "平滑跟枪", "持续跟枪", "目标阅读", "预判变向", "发力不停",
    "air celestial", "Air CELESTIAL", "celestial", "UFO",
    "跟踪变向", "平滑移动", "手臂放松", "持续瞄准",
    "读目标", "目标轨迹", "变向预判", "跟枪变向"
]

def extract_comments(filepath, min_length=15):
    """从 JSON 文件中提取评论"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def search_obj(obj, path=""):
            if isinstance(obj, dict):
                if 'message' in obj and isinstance(obj['message'], str):
                    msg = obj['message']
                    if len(msg) >= min_length:
                        for kw in keywords:
                            if kw.lower() in msg.lower():
                                results.append({
                                    'file': os.path.basename(filepath),
                                    'path': path,
                                    'message': msg,
                                    'like': obj.get('like', 0),
                                    'keyword': kw
                                })
                                break
                for k, v in obj.items():
                    search_obj(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_obj(item, f"{path}[{i}]")
        
        search_obj(data)
    except Exception:
        pass
    return results

def extract_subs(filepath, min_length=10):
    """从字幕 JSON 文件中提取字幕段"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'body' in data:
            for item in data['body']:
                if isinstance(item, dict) and 'content' in item:
                    content = item['content']
                    if len(content) >= min_length:
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                results.append({
                                    'file': os.path.basename(filepath),
                                    'from': item.get('from', 0),
                                    'to': item.get('to', 0),
                                    'content': content,
                                    'keyword': kw
                                })
                                break
    except Exception:
        pass
    return results

print("=" * 90)
print("🔍 Air CELESTIAL No UFO Easier 感悟技巧搜索")
print("=" * 90)
print(f"\n关键词: {', '.join(keywords[:10])}...")

# 搜索所有 JSON 文件
all_comments = []
all_subs = []

for search_dir in search_dirs:
    for json_file in glob.glob(os.path.join(search_dir, "**", "*.json"), recursive=True):
        basename = os.path.basename(json_file).lower()
        if '评论' in basename or 'comment' in basename:
            all_comments.extend(extract_comments(json_file))
        elif '字幕' in basename or 'sub' in basename:
            all_subs.extend(extract_subs(json_file))

print(f"\n找到 {len(all_comments)} 条相关评论, {len(all_subs)} 条相关字幕")

# 按点赞数排序评论
all_comments.sort(key=lambda x: x.get('like', 0), reverse=True)

print("\n" + "=" * 90)
print("一、高赞评论（最有价值的感悟）")
print("=" * 90)

for i, r in enumerate(all_comments[:15]):
    like = r.get('like', 0)
    print(f"\n[{i+1}] 👍{like} | {r['file']} (关键词: {r['keyword']})")
    print(f"    {r['message'][:300]}")

# 按关键词分组统计
print("\n" + "=" * 90)
print("二、按主题分类整理")
print("=" * 90)

themes = {
    "变向预判": ["变向", "预判", "读目标", "目标阅读", "目标轨迹"],
    "持续发力": ["持续发力", "发力不停", "持续跟枪", "持续瞄准"],
    "视线聚焦": ["视线聚焦", "眼睛", "盯着目标", "目光"],
    "平滑跟枪": ["平滑", "平滑跟枪", "平滑移动", "不停顿"],
    "Blending混合": ["blending", "Blending", "混合"],
}

for theme, theme_kws in themes.items():
    print(f"\n【{theme}】")
    found = []
    for r in all_comments:
        for kw in theme_kws:
            if kw.lower() in r['message'].lower():
                found.append(r)
                break
    
    found.sort(key=lambda x: x.get('like', 0), reverse=True)
    for i, r in enumerate(found[:3]):
        like = r.get('like', 0)
        print(f"  👍{like}: {r['message'][:150]}")

# 字幕中的技巧
print("\n" + "=" * 90)
print("三、字幕中的技巧讲解")
print("=" * 90)

for i, r in enumerate(all_subs[:10]):
    print(f"\n[{i+1}] {r['file']} ({r['from']:.0f}s-{r['to']:.0f}s)")
    print(f"    {r['content'][:200]}")
