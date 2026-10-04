"""
深度提取 Flower 和 SmoothBot 的技巧和感悟
专门搜索评论和字幕中的有价值内容
"""
import json
import glob
import os
import re

# 搜索目录
search_dirs = [
    r"D:\11.project\iwen-codex\codex-list",
    r"D:\11.project\iwen-codex\bilibili-transcripts",
]

def extract_comments_from_json(filepath, keywords, min_length=20):
    """从 JSON 文件中提取包含关键词的评论"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def search_obj(obj, path=""):
            if isinstance(obj, dict):
                # 检查是否是评论结构
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
                # 递归搜索
                for k, v in obj.items():
                    search_obj(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    search_obj(item, f"{path}[{i}]")
        
        search_obj(data)
    except Exception as e:
        pass
    return results

def extract_subs_from_json(filepath, keywords, min_length=15):
    """从字幕 JSON 文件中提取包含关键词的字幕段"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 字幕结构通常是 {"body": [{"from":, "to":, "content":}, ...]}
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
    except Exception as e:
        pass
    return results

# ========== Flower Easier 50cm ==========
print("=" * 80)
print("【Flower Easier 50cm】技巧与感悟")
print("=" * 80)
print("\n关键词：描线、弧线、手腕放松、精细控制、Fingertip、小幅度、跟枪")

flower_keywords = ["描线", "弧线", "手腕放松", "精细控制", "fingertip", "小幅度", "跟枪", "平滑", "轨迹"]
flower_results = []

for search_dir in search_dirs:
    for json_file in glob.glob(os.path.join(search_dir, "**", "*.json"), recursive=True):
        basename = os.path.basename(json_file).lower()
        # 优先搜索评论和字幕文件
        if '评论' in basename or 'comment' in basename or '字幕' in basename or 'sub' in basename:
            flower_results.extend(extract_comments_from_json(json_file, flower_keywords))
            flower_results.extend(extract_subs_from_json(json_file, flower_keywords))

# 按点赞数排序
flower_results.sort(key=lambda x: x.get('like', 0), reverse=True)

print(f"\n找到 {len(flower_results)} 条相关评论/字幕")
print("\n--- 高赞评论 ---")
for i, r in enumerate(flower_results[:10]):
    like = r.get('like', 0)
    print(f"\n[{i+1}] 👍{like} | {r['file']}")
    print(f"    {r['message'][:200]}")

# ========== SmoothBot Perfected Easier ==========
print("\n\n" + "=" * 80)
print("【SmoothBot Perfected Easier】技巧与感悟")
print("=" * 80)
print("\n关键词：手臂跟枪、平滑移动、固定支点、大幅度、Arm、肩膀、手肘")

smoothbot_keywords = ["手臂跟枪", "平滑移动", "固定支点", "大幅度", "arm", "肩膀", "手肘", "手臂", "smoothbot", "平滑跟枪"]
smoothbot_results = []

for search_dir in search_dirs:
    for json_file in glob.glob(os.path.join(search_dir, "**", "*.json"), recursive=True):
        basename = os.path.basename(json_file).lower()
        if '评论' in basename or 'comment' in basename or '字幕' in basename or 'sub' in basename:
            smoothbot_results.extend(extract_comments_from_json(json_file, smoothbot_keywords))
            smoothbot_results.extend(extract_subs_from_json(json_file, smoothbot_keywords))

smoothbot_results.sort(key=lambda x: x.get('like', 0), reverse=True)

print(f"\n找到 {len(smoothbot_results)} 条相关评论/字幕")
print("\n--- 高赞评论 ---")
for i, r in enumerate(smoothbot_results[:15]):
    like = r.get('like', 0)
    print(f"\n[{i+1}] 👍{like} | {r['file']}")
    print(f"    {r['message'][:250]}")
