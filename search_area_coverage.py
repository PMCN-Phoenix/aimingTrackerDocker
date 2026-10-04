"""
搜索"区域覆盖跟枪法"相关的感悟和技巧
核心概念：把准星放在目标可能出现的区域中心，用小范围微调覆盖
关键词：区域覆盖、预判、预瞄、准星位置、不追目标、站位、预测轨迹、中心
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

# "区域覆盖跟枪法"相关关键词
keywords = [
    # 核心概念
    "区域", "覆盖", "中心", "中间", "范围",
    # 预判相关
    "预判", "预瞄", "提前", "预测", "预想",
    # 准星位置
    "准星位置", "准星放", "放准星", "瞄准位置",
    # 不追目标
    "不追", "不跟", "不要追", "不要跟", "不盯着",
    # 站位/位置感
    "站位", "位置感", "身位", "预瞄位",
    # 轨迹/路径
    "轨迹", "路径", "路线", "运动规律",
    # 相关技巧
    "拉枪不足", "拉过头", "微调", "小范围",
    # 类比
    "守门", "防守", "覆盖范围", "控制范围",
    # 英文
    "tracking", "predict", "anticipate", "positioning",
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
                        matched_kws = []
                        for kw in keywords:
                            if kw.lower() in msg.lower():
                                matched_kws.append(kw)
                        if matched_kws:
                            results.append({
                                'file': os.path.basename(filepath),
                                'path': path,
                                'message': msg,
                                'like': obj.get('like', 0),
                                'keywords': matched_kws
                            })
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
                        matched_kws = []
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                matched_kws.append(kw)
                        if matched_kws:
                            results.append({
                                'file': os.path.basename(filepath),
                                'from': item.get('from', 0),
                                'to': item.get('to', 0),
                                'content': content,
                                'keywords': matched_kws
                            })
    except Exception:
        pass
    return results

print("=" * 90)
print("🔍 区域覆盖跟枪法 - 感悟技巧搜索")
print("=" * 90)
print(f"\n关键词数: {len(keywords)}")

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

# 去重（相同消息只保留点赞最高的）
seen_messages = set()
unique_comments = []
for r in all_comments:
    msg_key = r['message'][:100]
    if msg_key not in seen_messages:
        seen_messages.add(msg_key)
        unique_comments.append(r)

print(f"去重后: {len(unique_comments)} 条评论")

print("\n" + "=" * 90)
print("一、高赞评论（最有价值的感悟）")
print("=" * 90)

for i, r in enumerate(unique_comments[:20]):
    like = r.get('like', 0)
    kws = ', '.join(r['keywords'][:3])
    print(f"\n[{i+1}] 👍{like} | {r['file']} (关键词: {kws})")
    print(f"    {r['message'][:400]}")

# 按主题分类
print("\n" + "=" * 90)
print("二、按主题分类整理")
print("=" * 90)

themes = {
    "预判/预瞄": ["预判", "预瞄", "提前", "预测", "预想"],
    "不追目标/看区域": ["不追", "不跟", "不要追", "不要跟", "区域", "覆盖", "范围"],
    "准星位置/站位": ["准星位置", "准星放", "放准星", "站位", "位置感", "身位", "预瞄位"],
    "拉枪不足/微调": ["拉枪不足", "拉过头", "微调", "小范围"],
    "轨迹/运动规律": ["轨迹", "路径", "路线", "运动规律"],
}

for theme, theme_kws in themes.items():
    print(f"\n【{theme}】")
    found = []
    for r in unique_comments:
        for kw in theme_kws:
            if kw.lower() in r['message'].lower():
                found.append(r)
                break
    
    found.sort(key=lambda x: x.get('like', 0), reverse=True)
    for i, r in enumerate(found[:3]):
        like = r.get('like', 0)
        print(f"  👍{like}: {r['message'][:200]}")

# 字幕中的技巧
print("\n" + "=" * 90)
print("三、字幕中的技巧讲解")
print("=" * 90)

# 去重字幕
seen_subs = set()
unique_subs = []
for r in all_subs:
    content_key = r['content'][:80]
    if content_key not in seen_subs:
        seen_subs.add(content_key)
        unique_subs.append(r)

for i, r in enumerate(unique_subs[:15]):
    kws = ', '.join(r['keywords'][:3])
    print(f"\n[{i+1}] {r['file']} ({r['from']:.0f}s-{r['to']:.0f}s) (关键词: {kws})")
    print(f"    {r['content'][:300]}")
