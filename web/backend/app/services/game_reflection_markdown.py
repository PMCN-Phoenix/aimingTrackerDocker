# -*- coding: utf-8 -*-
"""
游戏感悟功能 - Markdown 文件同步服务
对应技术方案文档第四章
将感悟同步到 Markdown 文件（人类可读），按日期组织
"""
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.game_reflection import (
    THEME_NAMES, THEME_ICONS, THEME_COLORS
)


# Markdown 文件存储目录
MARKDOWN_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "docs", "记录", "游戏感悟"
)

# 手写批注块标记（如「关联问题库」）。放在 reflection_id 之后、用注释包裹，
# 这样重新生成 Markdown 时既不会污染 content，也不会被整文件重写吞掉。
ANNOTATION_START = "<!-- annotation:start -->"
ANNOTATION_END = "<!-- annotation:end -->"


def ensure_markdown_dir():
    """确保 Markdown 目录存在"""
    if not os.path.exists(MARKDOWN_DIR):
        os.makedirs(MARKDOWN_DIR, exist_ok=True)


def get_markdown_path(date: str) -> str:
    """获取指定日期的 Markdown 文件路径"""
    return os.path.join(MARKDOWN_DIR, f"{date}.md")


def reflection_to_markdown(reflection: Dict[str, Any]) -> str:
    """将单条感悟转换为 Markdown 格式"""
    theme = reflection.get("theme", "")
    theme_name = THEME_NAMES.get(theme, theme)
    theme_icon = THEME_ICONS.get(theme, "📝")

    lines = []
    lines.append(f"### {theme_icon} {reflection.get('title', '无标题')}")
    lines.append("")

    # 元信息
    meta_parts = [f"**主题**: {theme_name}"]
    if reflection.get("game"):
        meta_parts.append(f"**游戏**: {reflection['game']}")
    if reflection.get("mode"):
        meta_parts.append(f"**模式**: {reflection['mode']}")
    if reflection.get("map_name"):
        meta_parts.append(f"**地图**: {reflection['map_name']}")
    if reflection.get("agent_name"):
        meta_parts.append(f"**英雄**: {reflection['agent_name']}")
    if reflection.get("scenario"):
        meta_parts.append(f"**场景**: {reflection['scenario']}")
    if reflection.get("warmup_item"):
        meta_parts.append(f"**热身项目**: {reflection['warmup_item']}")

    lines.append(" | ".join(meta_parts))
    lines.append("")

    # 标签
    tags = reflection.get("tags") or []
    if tags:
        lines.append(f"**标签**: {' '.join(tags)}")
        lines.append("")

    # 内容
    content = reflection.get("content", "")
    lines.append(content)
    lines.append("")

    # ID（隐藏标记，用于同步）
    lines.append(f"<!-- reflection_id: {reflection.get('id', '')} -->")
    lines.append("")

    # 手写批注（关联问题库等），单独标记以便重写时保留
    annotation = (reflection.get("annotation") or "").strip()
    if annotation:
        lines.append(ANNOTATION_START)
        lines.append("")
        lines.append(annotation)
        lines.append("")
        lines.append(ANNOTATION_END)
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def parse_markdown_reflections(content: str) -> List[Dict[str, Any]]:
    """从 Markdown 内容中解析感悟列表"""
    reflections = []

    # 按 ### 分割感悟块
    blocks = re.split(r'^### ', content, flags=re.MULTILINE)

    for block in blocks[1:]:  # 跳过第一个空块
        reflection = {}

        # 提取 ID（隐藏标记）
        id_match = re.search(r'<!-- reflection_id: (.+?) -->', block)
        if id_match:
            reflection["id"] = id_match.group(1).strip()

        # 提取手写批注（关联问题库等）
        annotation_match = re.search(
            re.escape(ANNOTATION_START) + r'(.*?)' + re.escape(ANNOTATION_END),
            block,
            re.DOTALL
        )
        if annotation_match:
            annotation = annotation_match.group(1).strip()
            if annotation:
                reflection["annotation"] = annotation

        # 提取标题（第一行）
        first_line = block.split("\n")[0].strip()
        # 移除开头的 emoji 图标和空格（只移除图标，不移除标题中的特殊字符如 []）
        # emoji 范围: \U0001F300-\U0001F9FF, \U00002600-\U000027BF, \U0001F000-\U0001F02F, \U0001FA00-\U0001FA6F
        title = re.sub(r'^[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F000-\U0001F02F\U0001FA00-\U0001FA6F\s]+', '', first_line).strip()
        reflection["title"] = title

        # 提取元信息
        theme_match = re.search(r'\*\*主题\*\*: (.+?)(?:\s*\||\n|$)', block)
        if theme_match:
            theme_name = theme_match.group(1).strip()
            # 反向查找主题 key
            for key, name in THEME_NAMES.items():
                if name == theme_name:
                    reflection["theme"] = key
                    break

        game_match = re.search(r'\*\*游戏\*\*: (.+?)(?:\s*\||\n|$)', block)
        if game_match:
            reflection["game"] = game_match.group(1).strip()

        mode_match = re.search(r'\*\*模式\*\*: (.+?)(?:\s*\||\n|$)', block)
        if mode_match:
            reflection["mode"] = mode_match.group(1).strip()

        map_match = re.search(r'\*\*地图\*\*: (.+?)(?:\s*\||\n|$)', block)
        if map_match:
            reflection["map_name"] = map_match.group(1).strip()

        agent_match = re.search(r'\*\*英雄\*\*: (.+?)(?:\s*\||\n|$)', block)
        if agent_match:
            reflection["agent_name"] = agent_match.group(1).strip()

        scenario_match = re.search(r'\*\*场景\*\*: (.+?)(?:\s*\||\n|$)', block)
        if scenario_match:
            reflection["scenario"] = scenario_match.group(1).strip()

        warmup_match = re.search(r'\*\*热身项目\*\*: (.+?)(?:\s*\||\n|$)', block)
        if warmup_match:
            reflection["warmup_item"] = warmup_match.group(1).strip()

        # 提取标签
        tags_match = re.search(r'\*\*标签\*\*: (.+?)(?:\n|$)', block)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            reflection["tags"] = [t.strip() for t in tags_str.split() if t.strip()]

        # 提取内容（标签之后，ID 标记之前）
        content_match = re.search(
            r'\*\*标签\*\*:.*?\n\n(.*?)(?:\n<!-- reflection_id)',
            block,
            re.DOTALL
        )
        if not content_match:
            # 如果没有标签，内容在元信息之后
            content_match = re.search(
                r'\*\*主题\*\*:.*?\n\n(.*?)(?:\n<!-- reflection_id)',
                block,
                re.DOTALL
            )
        if content_match:
            reflection["content"] = content_match.group(1).strip()

        if reflection.get("title"):
            reflections.append(reflection)

    return reflections


def read_date_reflections(date: str) -> List[Dict[str, Any]]:
    """读取指定日期的所有感悟（从 Markdown 文件）"""
    filepath = get_markdown_path(date)
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return parse_markdown_reflections(content)


def read_existing_annotations(date: str) -> Dict[str, str]:
    """读取已有文件里的手写批注，返回 {reflection_id: annotation}

    整文件重写（如 InfluxDB → Markdown 导出）时用它将批注回填，
    避免手写的「关联问题库」等批注被生成逻辑覆盖丢失。
    """
    filepath = get_markdown_path(date)
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    annotations: Dict[str, str] = {}
    for item in parse_markdown_reflections(content):
        if item.get("id") and item.get("annotation"):
            annotations[item["id"]] = item["annotation"]
    return annotations


def write_date_reflections(date: str, reflections: List[Dict[str, Any]]) -> bool:
    """写入指定日期的所有感悟到 Markdown 文件"""
    ensure_markdown_dir()
    filepath = get_markdown_path(date)

    # 回填已有手写批注（调用方通常不带 annotation 字段）
    existing_annotations = read_existing_annotations(date)
    if existing_annotations:
        for reflection in reflections:
            ref_id = reflection.get("id", "")
            if not reflection.get("annotation") and ref_id in existing_annotations:
                reflection["annotation"] = existing_annotations[ref_id]

    lines = []
    lines.append(f"# 游戏感悟 - {date}")
    lines.append("")
    lines.append(f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for reflection in reflections:
        lines.append(reflection_to_markdown(reflection))

    content = "\n".join(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def sync_reflection_to_markdown(reflection: Dict[str, Any]) -> bool:
    """同步单条感悟到 Markdown 文件（增量更新）"""
    date = reflection.get("date", "")
    if not date:
        return False

    # 读取现有感悟
    existing = read_date_reflections(date)

    # 查找是否已存在（按 ID）
    ref_id = reflection.get("id", "")
    found = False
    for i, item in enumerate(existing):
        if item.get("id") == ref_id:
            existing[i] = reflection
            found = True
            break

    if not found:
        existing.append(reflection)

    # 按创建时间排序
    existing.sort(key=lambda x: x.get("id", ""))

    # 写入文件
    return write_date_reflections(date, existing)


def delete_reflection_from_markdown(date: str, ref_id: str) -> bool:
    """从 Markdown 文件中删除单条感悟"""
    existing = read_date_reflections(date)
    remaining = [item for item in existing if item.get("id") != ref_id]

    if len(remaining) == len(existing):
        # 没有找到要删除的
        return True

    if remaining:
        return write_date_reflections(date, remaining)
    else:
        # 如果没有感悟了，删除文件
        filepath = get_markdown_path(date)
        if os.path.exists(filepath):
            os.remove(filepath)
        return True


def list_all_markdown_dates() -> List[str]:
    """列出所有有感悟的日期"""
    ensure_markdown_dir()
    dates = []
    for filename in os.listdir(MARKDOWN_DIR):
        if filename.endswith(".md") and re.match(r'\d{4}-\d{2}-\d{2}\.md$', filename):
            dates.append(filename.replace(".md", ""))
    dates.sort(reverse=True)
    return dates


def import_all_from_markdown() -> List[Dict[str, Any]]:
    """从所有 Markdown 文件导入感悟"""
    all_reflections = []
    dates = list_all_markdown_dates()
    for date in dates:
        reflections = read_date_reflections(date)
        for reflection in reflections:
            reflection["date"] = date
        all_reflections.extend(reflections)
    return all_reflections
