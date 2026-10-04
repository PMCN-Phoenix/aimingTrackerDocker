"""
查找 Flower Easier 50cm 和 SmoothBot Perfected Easier 的感悟和技巧
1. InfluxDB 中已有的感悟
2. 本地 B站调研数据
"""
import sys
import os
import json
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
from app.repositories.influx_client import InfluxDBClient

db = InfluxDBClient()

scenarios = ["Flower Easier 50cm", "SmoothBot Perfected Easier"]

print("=" * 80)
print("一、InfluxDB 中已有的感悟")
print("=" * 80)

for scn in scenarios:
    print(f"\n【{scn}】")
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "aim_reflection")
  |> filter(fn: (r) => r.scenario == "{scn}")
  |> keep(columns: ["_time", "_value", "scenario", "note"])
  |> sort(columns: ["_time"])
'''
    try:
        rows = db.query(flux)
        if rows:
            for r in rows:
                time_str = r.get("_time", "")[:10]
                note = r.get("note", "")
                print(f"  [{time_str}] {note}")
        else:
            print("  （暂无感悟记录）")
    except Exception as e:
        print(f"  查询出错: {e}")

print("\n" + "=" * 80)
print("二、本地 B站调研数据搜索")
print("=" * 80)

# 搜索本地 B站调研数据
search_dirs = [
    r"D:\11.project\iwen-codex\codex-list",
    r"D:\11.project\iwen-codex\bilibili-transcripts",
]

keywords = {
    "Flower Easier 50cm": ["flower", "Flower", "弧线", "描线", "精细跟枪", "小幅度", "fingertip", "指尖"],
    "SmoothBot Perfected Easier": ["smoothbot", "SmoothBot", "平滑跟枪", "手臂跟枪", "arm", "大幅度", "平滑移动"],
}

for scn, kws in keywords.items():
    print(f"\n【{scn}】关键词: {kws[:5]}...")
    
    found_content = []
    
    for search_dir in search_dirs:
        # 搜索 JSON 文件（评论、字幕）
        for json_file in glob.glob(os.path.join(search_dir, "**", "*.json"), recursive=True):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含关键词
                content_lower = content.lower()
                for kw in kws:
                    if kw.lower() in content_lower:
                        # 找到相关内容，提取上下文
                        idx = content_lower.find(kw.lower())
                        if idx > 0:
                            start = max(0, idx - 100)
                            end = min(len(content), idx + 200)
                            snippet = content[start:end].replace('\n', ' ')[:300]
                            found_content.append({
                                'file': os.path.basename(json_file),
                                'keyword': kw,
                                'snippet': snippet
                            })
                        break  # 一个文件只记一次
            except Exception:
                pass
        
        # 搜索 MD 文件
        for md_file in glob.glob(os.path.join(search_dir, "**", "*.md"), recursive=True):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content_lower = content.lower()
                for kw in kws:
                    if kw.lower() in content_lower:
                        idx = content_lower.find(kw.lower())
                        if idx > 0:
                            start = max(0, idx - 100)
                            end = min(len(content), idx + 200)
                            snippet = content[start:end].replace('\n', ' ')[:300]
                            found_content.append({
                                'file': os.path.basename(md_file),
                                'keyword': kw,
                                'snippet': snippet
                            })
                        break
            except Exception:
                pass
    
    if found_content:
        print(f"  找到 {len(found_content)} 条相关内容:")
        for i, item in enumerate(found_content[:10]):
            print(f"\n  [{i+1}] 文件: {item['file']} (关键词: {item['keyword']})")
            print(f"      内容: {item['snippet']}")
    else:
        print("  （未找到相关内容）")
