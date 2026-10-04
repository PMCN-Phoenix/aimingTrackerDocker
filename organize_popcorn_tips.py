"""
整理 Popcorn 技巧与感悟，按主题分类
"""
import json
import os

BASE_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\Popcorn专项"

# 主题分类
CATEGORIES = {
    '垂直/Y轴控制': ['垂直', '上下', 'y轴', '纵向', 'y轴瞄准', '上下移动'],
    '点击节奏与时机': ['点击', '节奏', '时机', '最高点', '顶点', '确认', '开枪'],
    '眼睛与视线': ['眼睛', '视线', '看目标', '余光', '注意力', '聚焦'],
    '手部发力与放松': ['手腕', '手臂', '手指', '肩部', '发力', '放松', '紧绷', '肌肉'],
    '定位与微调': ['定位', '微调', '准星', '瞄准', '修正', '拉枪'],
    '轨迹预判': ['预判', '预测', '轨迹', '弧线', '移动方向', '变向'],
    '常见错误与纠正': ['错误', '问题', '瓶颈', '不稳定', '波动', '马枪'],
    '训练方法': ['练习', '训练', '方法', '技巧', '提升', '突破'],
}

def categorize(content):
    """对内容进行分类"""
    content_lower = content.lower()
    categories = []
    for cat, keywords in CATEGORIES.items():
        if any(kw in content_lower for kw in keywords):
            categories.append(cat)
    return categories if categories else ['其他']

def main():
    # 读取提取结果
    with open(os.path.join(BASE_DIR, 'Popcorn技巧与感悟-提取结果.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    subtitle_results = data['subtitle_results']
    comment_results = data['comment_results']

    print(f"字幕: {len(subtitle_results)} 段")
    print(f"评论: {len(comment_results)} 条")

    # 按主题分类
    categorized = {cat: {'subtitles': [], 'comments': []} for cat in CATEGORIES}
    categorized['其他'] = {'subtitles': [], 'comments': []}

    # 分类字幕
    for item in subtitle_results:
        content = item['content']
        cats = categorize(content)
        for cat in cats:
            if cat in categorized:
                categorized[cat]['subtitles'].append(item)

    # 分类评论（按点赞数排序）
    comment_results.sort(key=lambda x: x.get('like', 0), reverse=True)
    for item in comment_results:
        content = item['content']
        cats = categorize(content)
        for cat in cats:
            if cat in categorized:
                categorized[cat]['comments'].append(item)

    # 输出整理结果
    output = []
    output.append("# Popcorn 场景技巧与感悟整理")
    output.append("")
    output.append("> 来源：B站 Popcorn 专项调研（16 个视频、13 个有字幕、1000+ 条评论）")
    output.append(f"> 提取时间：2026-10-03")
    output.append("")

    for cat in CATEGORIES:
        subs = categorized[cat]['subtitles']
        comments = categorized[cat]['comments']

        if not subs and not comments:
            continue

        output.append(f"## {cat}")
        output.append("")
        output.append(f"*相关字幕 {len(subs)} 段，评论 {len(comments)} 条*")
        output.append("")

        # 输出高赞评论（Top 5）
        if comments:
            output.append("### 🔥 高赞评论")
            output.append("")
            for i, c in enumerate(comments[:5], 1):
                like = c.get('like', 0)
                content = c['content'][:300].replace('\n', ' ')
                output.append(f"{i}. **👍 {like}**：{content}")
                output.append("")

        # 输出字幕精华（Top 10，按相关度）
        if subs:
            output.append("### 📝 字幕精华")
            output.append("")
            # 按匹配关键词数量排序
            subs_sorted = sorted(subs, key=lambda x: len(x.get('matched', [])), reverse=True)
            for i, s in enumerate(subs_sorted[:10], 1):
                bvid = s['bvid']
                minutes = int(s['from'] // 60)
                seconds = int(s['from'] % 60)
                content = s['content'][:200]
                output.append(f"{i}. **{bvid} @ {minutes}:{seconds:02d}**：{content}")
                output.append("")

        output.append("---")
        output.append("")

    # 保存整理结果
    output_file = os.path.join(BASE_DIR, 'Popcorn技巧与感悟-整理报告.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    print(f"\n整理完成！已保存到: {output_file}")

    # 打印统计
    print("\n各主题统计:")
    for cat in CATEGORIES:
        subs = len(categorized[cat]['subtitles'])
        comments = len(categorized[cat]['comments'])
        if subs or comments:
            print(f"  {cat}: 字幕 {subs}, 评论 {comments}")


if __name__ == '__main__':
    main()
