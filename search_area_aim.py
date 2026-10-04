"""
搜索"区域中心/预瞄/覆盖跟枪"相关的感悟和技巧
"""
import json
import glob
import os

search_dirs = [
    r"D:\11.project\iwen-codex\codex-list",
    r"D:\11.project\iwen-codex\bilibili-transcripts",
]

# 区域中心/预瞄/覆盖相关关键词
keywords = [
    "预瞄", "提前量", "预判", "站位", "覆盖",
    "区域", "中心", "准星放置", "准星位置",
    "守门员", "球门", "活动范围", "移动范围",
    "轨迹预判", "目标区域", "可能出现",
    "跟枪", "平滑跟枪", "持续跟枪",
    "眼睛", "视线", "注意力", "焦点",
    "拉枪不足", "拉枪过头", "定位",
    "低敏", "高敏", "灵敏度",
    "手腕", "手臂", "手指", "发力",
    "变向", "变向跟枪", "频繁变向",
    "确认", "开枪时机", "重合"
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
                        matched_kws = [kw for kw in keywords if kw.lower() in msg.lower()]
                        if len(matched_kws) >= 2:  # 至少匹配2个关键词，更精准
                            results.append({
                                'file': os.path.basename(filepath),
                                'message': msg,
                                'like': obj.get('like', 0),
                                'matched_kws': matched_kws
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
                        matched_kws = [kw for kw in keywords if kw.lower() in content.lower()]
                        if len(matched_kws) >= 2:
                            results.append({
                                'file': os.path.basename(filepath),
                                'from': item.get('from', 0),
                                'to': item.get('to', 0),
                                'content': content,
                                'matched_kws': matched_kws
                            })
    except Exception:
        pass
    return results

print("=" * 90)
print("🔍 区域中心/预瞄/覆盖跟枪 感悟搜索")
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

# 按点赞数排序
all_comments.sort(key=lambda x: x.get('like', 0), reverse=True)

print("\n" + "=" * 90)
print("一、高赞评论（最有价值的感悟）")
print("=" * 90)

for i, r in enumerate(all_comments[:20]):
    like = r.get('like', 0)
    kws = ', '.join(r['matched_kws'][:5])
    print(f"\n[{i+1}] 👍{like} | {r['file']}")
    print(f"    匹配关键词: {kws}")
    print(f"    {r['message'][:350]}")

# 按主题分类
print("\n" + "=" * 90)
print("二、按主题分类整理")
print("=" * 90)

themes = {
    "预瞄/提前量": ["预瞄", "提前量", "预判", "可能出现"],
    "区域/覆盖/站位": ["区域", "覆盖", "站位", "中心", "活动范围", "移动范围", "守门员", "球门"],
    "眼睛/视线/注意力": ["眼睛", "视线", "注意力", "焦点", "盯着目标"],
    "拉枪控制/灵敏度": ["拉枪不足", "拉枪过头", "低敏", "高敏", "灵敏度"],
    "变向跟枪": ["变向", "频繁变向", "变向跟枪"],
    "确认/开枪时机": ["确认", "开枪时机", "重合"],
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
        print(f"  👍{like}: {r['message'][:180]}")

# 字幕中的技巧
print("\n" + "=" * 90)
print("三、字幕中的技巧讲解")
print("=" * 90)

for i, r in enumerate(all_subs[:8]):
    print(f"\n[{i+1}] {r['file']} ({r['from']:.0f}s-{r['to']:.0f}s)")
    print(f"    匹配: {', '.join(r['matched_kws'][:5])}")
    print(f"    {r['content'][:250]}")
