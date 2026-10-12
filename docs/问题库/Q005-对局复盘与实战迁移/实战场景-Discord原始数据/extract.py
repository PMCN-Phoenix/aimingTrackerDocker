"""
提取Woohoojin Discord #vod-review中与残局1v1/peeking/对枪相关的精华评论
"""
import os
import re
import json
from pathlib import Path

SRC_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q005-对局复盘与实战迁移\实战场景-Discord原始数据")
OUT_FILE = SRC_DIR / "精华提取-残局1v1-peeking.md"

# 关键词分组
KEYWORDS = {
    "残局1v1": ["clutch", "1v1", "1 v 1", "post plant", "retake", "last man", "solo", "1v2", "1v3"],
    "peeking技巧": ["peek", "swing", "wide", "jiggle", "jump peek", "crouch peek", "angle", "holding angle", "pre-aim", "preaim", "crosshair placement"],
    "对枪技巧": ["gunfight", "gun fight", "aim duel", "duel", "tapping", "burst", "spray", "counter strafe", "counter-strafe", "movement", "strafing"],
    "残局决策": ["pacing", "positioning", "utility", "smoke", "flash", "info", "timing", "trade", "space", "retake pacing"],
}

def clean_text(text):
    """清理base64图片数据和多余空白"""
    # 移除base64图片
    text = re.sub(r'!\[img\]\(data:image/[^)]+\)', '', text)
    # 移除图片链接
    text = re.sub(r'!\[图片\]\([^)]+\)', '', text)
    # 移除多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_messages(filepath):
    """从文件中提取消息块"""
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    # 按消息分隔符分割
    # 消息格式: - ## 用户名 *—* 日期
    messages = re.split(r'\n- ## ', content)
    result = []
    for msg in messages:
        if not msg.strip():
            continue
        # 提取用户名和日期
        header_match = re.match(r'(.+?)\s*\*—\*\s*(\d{4}/\d+/\d+[^\n]*)', msg)
        if header_match:
            username = header_match.group(1).strip()
            date = header_match.group(2).strip()
            body = msg[header_match.end():].strip()
        else:
            username = "unknown"
            date = "unknown"
            body = msg.strip()
        
        body = clean_text(body)
        if len(body) < 20:  # 跳过太短的消息
            continue
        
        result.append({
            'username': username,
            'date': date,
            'body': body,
            'source': filepath.name,
            'length': len(body)
        })
    return result

def match_keywords(body, keywords):
    """检查消息是否匹配关键词组"""
    body_lower = body.lower()
    matched = []
    for category, words in keywords.items():
        for word in words:
            if word.lower() in body_lower:
                matched.append(category)
                break
    return matched

def main():
    all_messages = []
    for f in sorted(SRC_DIR.glob("Woohoojin*.md")):
        msgs = extract_messages(f)
        all_messages.extend(msgs)
        print(f"  {f.name}: {len(msgs)} 条消息")
    
    print(f"\n总消息数: {len(all_messages)}")
    
    # 按关键词分类
    categorized = {k: [] for k in KEYWORDS.keys()}
    for msg in all_messages:
        matched = match_keywords(msg['body'], KEYWORDS)
        for cat in matched:
            categorized[cat].append(msg)
    
    # 输出精华
    output = ["# Woohoojin Discord #vod-review 精华提取\n",
              "> 来源：Woohoojin Discord #vod-review频道，搜索关键词 clutch / 1v1\n",
              f"> 提取时间：2026-10-12\n",
              f"> 原始数据：{len(all_messages)} 条消息，11个文件，1.57MB\n",
              "---\n"]
    
    for category, msgs in categorized.items():
        # 按长度排序（长的通常更有价值）
        msgs_sorted = sorted(msgs, key=lambda x: x['length'], reverse=True)
        # 取前20条
        top_msgs = msgs_sorted[:20]
        
        output.append(f"\n## {category}（{len(msgs)}条相关，展示Top {len(top_msgs)}）\n")
        output.append("---\n")
        
        for i, msg in enumerate(top_msgs, 1):
            output.append(f"\n### [{i}] {msg['username']} ({msg['date']})\n")
            output.append(f"*来源：{msg['source']}*\n\n")
            output.append(f"{msg['body']}\n")
    
    OUT_FILE.write_text('\n'.join(output), encoding='utf-8')
    print(f"\n精华已写入: {OUT_FILE}")
    print(f"文件大小: {OUT_FILE.stat().st_size / 1024:.1f}KB")
    
    # 输出统计
    print("\n=== 分类统计 ===")
    for cat, msgs in categorized.items():
        print(f"  {cat}: {len(msgs)} 条")

if __name__ == "__main__":
    main()
