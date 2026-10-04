"""
搜索"鼠标控制不住、打久了失瞄、拖不动"相关的感悟和技巧
关键词：鼠标控制、失瞄、拖不动、疲劳、握力、手臂酸、手腕僵硬、发力、紧张
"""
import json
import glob
import os

# 搜索目录
search_dirs = [
    r"D:\11.project\iwen-codex\codex-list",
    r"D:\11.project\iwen-codex\bilibili-transcripts",
]

# 相关关键词
keywords = [
    # 核心问题
    "失瞄", "拖不动", "控制不住", "拉不动", "瞄不准",
    # 疲劳相关
    "疲劳", "累", "酸", "无力", "没力气", "手酸", "手臂酸",
    # 握力/紧张
    "握力", "握紧", "紧张", "僵硬", "锁死", "捏鼠标",
    # 发力/姿势
    "发力", "姿势", "手臂支撑", "悬空", "手腕", "手臂",
    # 鼠标/设备
    "鼠标", "鼠标垫", "摩擦力", "灵敏度", "DPI",
    # 相关技巧
    "放松", "握姿", "手臂放松", "手腕放松",
]

def extract_comments(filepath, min_length=15):
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
print("🔍 鼠标控制不住/打久了失瞄 - 感悟技巧搜索")
print("=" * 90)

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

# 去重
seen_messages = set()
unique_comments = []
for r in all_comments:
    msg_key = r['message'][:100]
    if msg_key not in seen_messages:
        seen_messages.add(msg_key)
        unique_comments.append(r)

unique_comments.sort(key=lambda x: x.get('like', 0), reverse=True)

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
    "疲劳/无力": ["疲劳", "累", "酸", "无力", "没力气", "手酸", "手臂酸"],
    "握力/紧张/僵硬": ["握力", "握紧", "紧张", "僵硬", "锁死", "捏鼠标"],
    "放松/姿势": ["放松", "握姿", "手臂放松", "手腕放松", "姿势", "手臂支撑", "悬空"],
    "发力/肌肉群": ["发力", "手腕", "手臂", "手指", "肌肉"],
    "设备/灵敏度": ["鼠标", "鼠标垫", "摩擦力", "灵敏度", "DPI"],
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

# 字幕
print("\n" + "=" * 90)
print("三、字幕中的技巧讲解")
print("=" * 90)

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
