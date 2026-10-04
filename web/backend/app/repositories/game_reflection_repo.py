# -*- coding: utf-8 -*-
"""
游戏感悟功能 - 数据访问层（InfluxDB）
对应技术方案文档第三章
Measurement: game_reflection
"""
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .influx_client import db


# ==================== 工具函数 ====================

def _escape_tag_value(value: str) -> str:
    """转义 InfluxDB tag 值中的空格、逗号、等号"""
    return value.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def _escape_field_string(value: str) -> str:
    """转义 InfluxDB field 字符串值中的双引号"""
    return value.replace('"', '\\"')


def _generate_reflection_id(date: str) -> str:
    """生成感悟唯一 ID: ref_{YYYYMMDD}_{短UUID}"""
    date_compact = date.replace("-", "")
    short_uuid = uuid.uuid4().hex[:8]
    return f"ref_{date_compact}_{short_uuid}"


def _generate_warmup_item_id() -> str:
    """生成热身项目唯一 ID: warmup_{短UUID}"""
    short_uuid = uuid.uuid4().hex[:8]
    return f"warmup_{short_uuid}"


def _date_to_timestamp(date_str: str) -> int:
    """日期字符串转时间戳（北京时间 00:00:00）"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


# ==================== 感悟 CRUD ====================

def create_game_reflection(
    title: str,
    content: str,
    theme: str,
    date: str,
    game: str = "valorant",
    mode: Optional[str] = None,
    map_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    scenario: Optional[str] = None,
    tags: Optional[List[str]] = None,
    warmup_item: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建一条游戏感悟
    返回: {"id": "...", "created_at": "..."}
    """
    ref_id = _generate_reflection_id(date)
    now_ns = int(time.time() * 1e9)
    tags_str = ",".join(tags) if tags else ""

    # 构造 Line Protocol
    # Tags: id, theme, game, date, mode(可选), map_name(可选), agent_name(可选), warmup_item(可选)
    # Fields: title, content, scenario(可选), tags
    tag_parts = [
        f"id={_escape_tag_value(ref_id)}",
        f"theme={_escape_tag_value(theme)}",
        f"game={_escape_tag_value(game)}",
        f"date={_escape_tag_value(date)}",
    ]
    if mode:
        tag_parts.append(f"mode={_escape_tag_value(mode)}")
    if map_name:
        tag_parts.append(f"map_name={_escape_tag_value(map_name)}")
    if agent_name:
        tag_parts.append(f"agent_name={_escape_tag_value(agent_name)}")
    if warmup_item:
        tag_parts.append(f"warmup_item={_escape_tag_value(warmup_item)}")

    field_parts = [
        f'title="{_escape_field_string(title)}"',
        f'content="{_escape_field_string(content)}"',
        f'tags="{_escape_field_string(tags_str)}"',
    ]
    if scenario:
        field_parts.append(f'scenario="{_escape_field_string(scenario)}"')

    line = f"game_reflection,{','.join(tag_parts)} {','.join(field_parts)} {now_ns}"

    success = db.write(line)
    if not success:
        raise Exception("写入 InfluxDB 失败")

    return {
        "id": ref_id,
        "created_at": datetime.fromtimestamp(now_ns / 1e9).isoformat(),
    }


def get_game_reflection_by_id(ref_id: str) -> Optional[Dict[str, Any]]:
    """根据 ID 获取单条感悟"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "game_reflection")
  |> filter(fn: (r) => r.id == "{ref_id}")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> keep(columns: ["_time", "id", "theme", "game", "date", "mode", "map_name", "agent_name", "warmup_item", "title", "content", "scenario", "tags"])
  |> limit(n: 1)
'''
    rows = db.query(flux)
    if not rows:
        return None
    return _parse_reflection_row(rows[0])


def list_game_reflections(
    theme: Optional[str] = None,
    game: Optional[str] = None,
    mode: Optional[str] = None,
    date: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    tag: Optional[str] = None,
    warmup_item: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    获取感悟列表（支持筛选）
    返回: {"total": N, "items": [...]}
    """
    # 构造时间范围
    if date_start:
        start_ts = _date_to_timestamp(date_start)
    else:
        start_ts = int((datetime.now() - timedelta(days=365)).timestamp())

    if date_end:
        end_ts = _date_to_timestamp(date_end) + 86400
    else:
        end_ts = int(time.time()) + 86400

    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')

    # 构造 filter 条件
    filters = [f'r._measurement == "game_reflection"']
    if theme:
        filters.append(f'r.theme == "{theme}"')
    if game:
        filters.append(f'r.game == "{game}"')
    if mode:
        filters.append(f'r.mode == "{mode}"')
    if date:
        filters.append(f'r.date == "{date}"')
    if warmup_item:
        filters.append(f'r.warmup_item == "{warmup_item}"')

    filter_str = " and ".join(filters)

    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => {filter_str})
  |> filter(fn: (r) => r._field == "title")
  |> group(columns: ["id"])
  |> count()
  |> keep(columns: ["id", "_value"])
'''
    count_rows = db.query(flux)
    total = len(count_rows)

    # 查询详情
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => {filter_str})
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> keep(columns: ["_time", "id", "theme", "game", "date", "mode", "map_name", "agent_name", "warmup_item", "title", "content", "scenario", "tags"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {limit}, offset: {offset})
'''
    rows = db.query(flux)
    items = [_parse_reflection_row(row) for row in rows]

    # tag 过滤（在内存中过滤，因为 tag 是 field 不是 tag）
    if tag:
        items = [item for item in items if tag in (item.get("tags") or [])]

    return {"total": total, "items": items}


def update_game_reflection(ref_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新感悟
    InfluxDB 不支持原地更新，采用"删除旧数据 + 写入新数据"的方式
    """
    # 1. 获取旧数据
    old = get_game_reflection_by_id(ref_id)
    if not old:
        raise Exception(f"感悟不存在: {ref_id}")

    # 2. 合并更新
    merged = {**old, **updates}
    # 移除不需要的字段
    for key in ["id", "created_at", "updated_at", "theme_name", "theme_icon", "theme_color"]:
        merged.pop(key, None)

    # 3. 删除旧数据（InfluxDB 2.x delete API）
    _delete_game_reflection(ref_id)

    # 4. 写入新数据（保留原 ID 和创建时间）
    now_ns = int(time.time() * 1e9)
    tags_str = ",".join(merged.get("tags") or [])

    tag_parts = [
        f"id={_escape_tag_value(ref_id)}",
        f"theme={_escape_tag_value(merged['theme'])}",
        f"game={_escape_tag_value(merged['game'])}",
        f"date={_escape_tag_value(merged['date'])}",
    ]
    if merged.get("mode"):
        tag_parts.append(f"mode={_escape_tag_value(merged['mode'])}")
    if merged.get("map_name"):
        tag_parts.append(f"map_name={_escape_tag_value(merged['map_name'])}")
    if merged.get("agent_name"):
        tag_parts.append(f"agent_name={_escape_tag_value(merged['agent_name'])}")
    if merged.get("warmup_item"):
        tag_parts.append(f"warmup_item={_escape_tag_value(merged['warmup_item'])}")

    field_parts = [
        f'title="{_escape_field_string(merged["title"])}"',
        f'content="{_escape_field_string(merged["content"])}"',
        f'tags="{_escape_field_string(tags_str)}"',
    ]
    if merged.get("scenario"):
        field_parts.append(f'scenario="{_escape_field_string(merged["scenario"])}"')

    line = f"game_reflection,{','.join(tag_parts)} {','.join(field_parts)} {now_ns}"
    success = db.write(line)
    if not success:
        raise Exception("写入 InfluxDB 失败")

    return {"id": ref_id, "updated_at": datetime.fromtimestamp(now_ns / 1e9).isoformat()}


def delete_game_reflection(ref_id: str) -> Dict[str, Any]:
    """删除感悟"""
    _delete_game_reflection(ref_id)
    return {"id": ref_id, "deleted": True}


def _delete_game_reflection(ref_id: str):
    """内部方法：通过 InfluxDB 2.x delete API 删除数据"""
    import urllib.request

    # InfluxDB 2.x delete API 需要指定时间范围和 predicate
    # 时间范围设为过去 10 年，确保覆盖所有数据
    start_time = "2016-01-01T00:00:00Z"
    end_time = "2036-01-01T00:00:00Z"

    url = f"{db.url}/api/v2/delete?org={db.org}&bucket={db.bucket}"
    payload = {
        "start": start_time,
        "stop": end_time,
        "predicate": f'_measurement="game_reflection" AND id="{ref_id}"'
    }
    import json
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Token {db.token}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=30) as response:
        return response.status == 204


# ==================== 统计 ====================

def get_game_reflection_stats() -> Dict[str, Any]:
    """获取感悟统计数据"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 总数
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "game_reflection")
  |> filter(fn: (r) => r._field == "title")
  |> group(columns: ["id"])
  |> count()
'''
    rows = db.query(flux)
    total_count = len(rows)

    # 今日数
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1d)
  |> filter(fn: (r) => r._measurement == "game_reflection")
  |> filter(fn: (r) => r.date == "{today}")
  |> filter(fn: (r) => r._field == "title")
  |> group(columns: ["id"])
  |> count()
'''
    rows = db.query(flux)
    today_count = len(rows)

    # 主题分布
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "game_reflection")
  |> filter(fn: (r) => r._field == "title")
  |> group(columns: ["theme", "id"])
  |> count()
  |> group(columns: ["theme"])
  |> count()
'''
    rows = db.query(flux)
    theme_distribution = {}
    theme_count = 0
    for row in rows:
        theme = row.get("theme", "")
        count = int(float(row.get("_value", 0)))
        if theme:
            theme_distribution[theme] = count
            theme_count += 1

    # 连续记录天数（简化计算：最近 30 天内有记录的天数）
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "game_reflection")
  |> filter(fn: (r) => r._field == "title")
  |> keep(columns: ["date"])
  |> distinct(column: "date")
'''
    rows = db.query(flux)
    recorded_dates = set()
    for row in rows:
        d = row.get("_value", "")
        if d:
            recorded_dates.add(d)

    # 计算连续天数（从今天往前数）
    consecutive_days = 0
    check_date = datetime.now()
    while check_date.strftime("%Y-%m-%d") in recorded_dates:
        consecutive_days += 1
        check_date -= timedelta(days=1)

    return {
        "total_count": total_count,
        "today_count": today_count,
        "consecutive_days": consecutive_days,
        "theme_count": theme_count,
        "theme_distribution": theme_distribution,
    }


# ==================== 热身项目 ====================

def create_warmup_item(name: str, type: str = "other", description: Optional[str] = None) -> Dict[str, Any]:
    """创建热身项目"""
    item_id = _generate_warmup_item_id()
    now_ns = int(time.time() * 1e9)

    tag_parts = [
        f"id={_escape_tag_value(item_id)}",
        f"name={_escape_tag_value(name)}",
        f"type={_escape_tag_value(type)}",
    ]

    field_parts = [
        f'name="{_escape_field_string(name)}"',
        f'type="{_escape_field_string(type)}"',
    ]
    if description:
        field_parts.append(f'description="{_escape_field_string(description)}"')

    line = f"warmup_item,{','.join(tag_parts)} {','.join(field_parts)} {now_ns}"
    success = db.write(line)
    if not success:
        raise Exception("写入 InfluxDB 失败")

    return {
        "id": item_id,
        "name": name,
        "type": type,
        "description": description,
        "created_at": datetime.fromtimestamp(now_ns / 1e9).isoformat(),
    }


def list_warmup_items() -> List[Dict[str, Any]]:
    """获取所有热身项目（含每个项目的感悟）"""
    # 简化查询：不用 pivot，直接查所有 field，在内存中组装
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "warmup_item")
  |> keep(columns: ["_time", "id", "name", "type", "_field", "_value"])
  |> sort(columns: ["_time"])
'''
    rows = db.query(flux)

    # 按 id 分组组装
    items_map = {}
    for row in rows:
        item_id = row.get("id", "")
        if not item_id:
            continue
        if item_id not in items_map:
            items_map[item_id] = {
                "id": item_id,
                "name": row.get("name", ""),
                "type": row.get("type", "other"),
                "description": None,
                "created_at": row.get("_time"),
                "reflections": [],
            }
        field = row.get("_field", "")
        value = row.get("_value", "")
        if field == "description" and value:
            items_map[item_id]["description"] = value

    items = list(items_map.values())

    # 查询每个项目的感悟
    for item in items:
        if item["name"]:
            result = list_game_reflections(theme="warmup", warmup_item=item["name"], limit=100)
            item["reflections"] = result.get("items", [])

    return items


def get_warmup_item_reflections(item_name: str) -> List[Dict[str, Any]]:
    """获取某个热身项目的所有感悟"""
    result = list_game_reflections(theme="warmup", warmup_item=item_name, limit=100)
    return result.get("items", [])


# ==================== 内部解析函数 ====================

def _parse_reflection_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """解析 InfluxDB 返回的感悟行"""
    tags_str = row.get("tags", "")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

    return {
        "id": row.get("id", ""),
        "title": row.get("title", ""),
        "content": row.get("content", ""),
        "theme": row.get("theme", ""),
        "game": row.get("game", ""),
        "date": row.get("date", ""),
        "mode": row.get("mode"),
        "map_name": row.get("map_name"),
        "agent_name": row.get("agent_name"),
        "warmup_item": row.get("warmup_item"),
        "scenario": row.get("scenario"),
        "tags": tags,
        "created_at": row.get("_time"),
    }
