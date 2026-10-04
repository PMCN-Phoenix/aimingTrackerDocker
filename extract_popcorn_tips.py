"""
从 Popcorn 专项调研数据中提取技巧和感悟
"""
import json
import glob
import os
import re

BASE_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\Popcorn专项"

# 关键词（按相关度排序）
KEYWORDS = [
    # Popcorn 专属
    'popcorn', '爆米花', '垂直', '上下', 'y轴', '纵向',
    # 点击/定位
    '点击', '定位', '微调', '瞄准', '准星', '跟枪', '追踪',
    # 技巧
    '节奏', '放松', '手腕', '手臂', '手指', '肩部', '发力',
    '预判', '预测', '轨迹', '弧线', '最高点', '顶点',
    # 错误/纠正
    '错误', '问题', '瓶颈', '提升', '练习', '训练',
]

def extract_from_subtitle(filepath):
    """从字幕文件提取相关段落"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bvid = os.path.basename(filepath).replace('字幕-', '').replace('.json', '')

        # 字幕可能在 body 字段
        body = data.get('body', [])
        if not body and isinstance(data, list):
            body = data

        for item in body:
            content = item.get('content', '')
            if not content:
                continue

            # 检查是否包含关键词
            content_lower = content.lower()
            matched = [kw for kw in KEYWORDS if kw in content_lower]

            if matched:
                results.append({
                    'bvid': bvid,
                    'from': item.get('from', 0),
                    'to': item.get('to', 0),
                    'content': content,
                    'matched': matched[:3],
                    'source': '字幕'
                })
    except Exception as e:
        print(f"  读取字幕失败 {filepath}: {e}")

    return results


def extract_from_comments(filepath):
    """从评论文件提取相关评论"""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bvid = os.path.basename(filepath).replace('comments_', '').replace('.json', '')

        # 递归收集评论
        def collect_comments(obj, depth=0):
            if isinstance(obj, dict):
                # 主评论格式
                if 'message' in obj and 'like' in obj:
                    content = obj.get('message', '')
                    if content:
                        content_lower = content.lower()
                        matched = [kw for kw in KEYWORDS if kw in content_lower]
                        if matched:
                            results.append({
                                'bvid': bvid,
                                'content': content,
                                'like': obj.get('like', 0),
                                'matched': matched[:3],
                                'source': '评论',
                                'depth': depth
                            })

                    # 楼中楼
                    subs = obj.get('subs') or obj.get('replies') or []
                    if isinstance(subs, list):
                        for sub in subs:
                            collect_comments(sub, depth + 1)

                # 递归其他字段
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        collect_comments(v, depth)

            elif isinstance(obj, list):
                for item in obj:
                    collect_comments(item, depth)

        collect_comments(data)

    except Exception as e:
        print(f"  读取评论失败 {filepath}: {e}")

    return results


def main():
    print("=" * 70)
    print("Popcorn 场景技巧与感悟提取")
    print("=" * 70)

    all_results = []

    # 1. 提取字幕
    print("\n【1】扫描字幕文件...")
    subtitle_dir = os.path.join(BASE_DIR, '字幕')
    subtitle_files = glob.glob(os.path.join(subtitle_dir, '*.json'))
    print(f"  找到 {len(subtitle_files)} 个字幕文件")

    for f in subtitle_files:
        results = extract_from_subtitle(f)
        all_results.extend(results)
        print(f"  {os.path.basename(f)}: {len(results)} 段相关")

    # 2. 提取评论
    print("\n【2】扫描评论文件...")
    comment_files = glob.glob(os.path.join(BASE_DIR, 'comments*.json'))
    print(f"  找到 {len(comment_files)} 个评论文件")

    for f in comment_files:
        results = extract_from_comments(f)
        all_results.extend(results)
        print(f"  {os.path.basename(f)}: {len(results)} 条相关")

    # 3. 按点赞数排序（评论），按时间排序（字幕）
    subtitle_results = [r for r in all_results if r['source'] == '字幕']
    comment_results = [r for r in all_results if r['source'] == '评论']

    # 评论按点赞数排序
    comment_results.sort(key=lambda x: x.get('like', 0), reverse=True)

    print(f"\n【3】统计结果")
    print(f"  字幕相关段落: {len(subtitle_results)}")
    print(f"  评论相关条数: {len(comment_results)}")
    print(f"  总计: {len(all_results)}")

    # 4. 输出 Top 30 评论（高赞）
    print("\n" + "=" * 70)
    print("【4】高赞评论 Top 30")
    print("=" * 70)

    for i, r in enumerate(comment_results[:30], 1):
        print(f"\n{i}. [{r['source']}] 👍{r.get('like', 0)} | BV: {r['bvid']}")
        print(f"   关键词: {', '.join(r['matched'])}")
        print(f"   内容: {r['content'][:200]}")

    # 5. 输出字幕精华（按关键词匹配度）
    print("\n" + "=" * 70)
    print("【5】字幕精华（Popcorn/点击/定位 相关）")
    print("=" * 70)

    # 筛选高相关度的字幕
    high_relevance = [r for r in subtitle_results if
                       any(kw in r['content'].lower() for kw in ['popcorn', '点击', '定位', '微调', '垂直', '上下'])]

    for i, r in enumerate(high_relevance[:40], 1):
        minutes = int(r['from'] // 60)
        seconds = int(r['from'] % 60)
        print(f"\n{i}. [{r['source']}] {r['bvid']} @ {minutes}:{seconds:02d}")
        print(f"   关键词: {', '.join(r['matched'])}")
        print(f"   内容: {r['content'][:200]}")

    # 6. 保存完整结果
    output_file = os.path.join(BASE_DIR, 'Popcorn技巧与感悟-提取结果.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'subtitle_results': subtitle_results,
            'comment_results': comment_results,
            'stats': {
                'total': len(all_results),
                'subtitle': len(subtitle_results),
                'comment': len(comment_results)
            }
        }, f, ensure_ascii=False, indent=2)

    print(f"\n【6】完整结果已保存到: {output_file}")


if __name__ == '__main__':
    main()
