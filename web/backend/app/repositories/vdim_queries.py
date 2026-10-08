# -*- coding: utf-8 -*-
"""VDIM 相关数据查询函数"""
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from .influx_client import db
from ..utils import vdim_utils


# ==================== 工具函数 ====================

def _ts_to_rfc3339(ts: int) -> str:
    """时间戳（UTC 秒）转 RFC3339 格式（UTC）"""
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%SZ')


def _escape_tag(value: str) -> str:
    """转义 InfluxDB Line Protocol tag 值中的逗号、空格、等号"""
    return value.replace(',', '\\,').replace(' ', '\\ ').replace('=', '\\=')


def _flux_escape(value: str) -> str:
    """转义 Flux 查询字符串中的双引号（防止注入）"""
    return value.replace('\\', '\\\\').replace('"', '\\"')


def _escape_field_string(value: str) -> str:
    """转义 InfluxDB field 字符串值中的引号和反斜杠"""
    return value.replace('\\', '\\\\').replace('"', '\\"')


# ==================== 查询函数 ====================

def get_vdim_today() -> Dict[str, Any]:
    """获取今天的训练信息（周期、Day、主题、场景列表）"""
    now = datetime.now()  # 北京时间
    cycle, day = vdim_utils.get_cycle_and_day(now)
    day_config = vdim_utils.get_day_config(day)

    if not day_config:
        return {
            "date": now.strftime("%Y-%m-%d"),
            "cycle": cycle,
            "day": day,
            "theme": "rest",
            "theme_label": "休息",
            "share_code": "",
            "checked_in": False,
            "scenarios_total": 0,
            "scenarios_done": 0,
            "is_rest_day": True
        }

    # 检查今天是否已打卡
    checked_in = _is_checked_in(now.strftime("%Y-%m-%d"))

    # 统计已完成场景数
    scenarios_done = _count_done_scenarios(cycle, day)

    return {
        "date": now.strftime("%Y-%m-%d"),
        "cycle": cycle,
        "day": day,
        "theme": day_config.get("theme", ""),
        "theme_label": day_config.get("theme_label", ""),
        "share_code": day_config.get("share_code", ""),
        "checked_in": checked_in,
        "scenarios_total": len(day_config.get("scenarios", [])),
        "scenarios_done": scenarios_done,
        "is_rest_day": False
    }


def get_vdim_day(cycle: int, day: str) -> Dict[str, Any]:
    """获取某周期某天的完整数据（场景分数+打卡状态）"""
    day_config = vdim_utils.get_day_config(day)
    target_date = vdim_utils.get_date_for_cycle_day(cycle, day)
    date_str = target_date.strftime("%Y-%m-%d")

    if not day_config:
        # Day7 休息
        return {
            "cycle": cycle,
            "day": day,
            "theme": "rest",
            "theme_label": "休息",
            "share_code": "",
            "date": date_str,
            "checked_in": _is_checked_in(date_str),
            "checkin_time": None,
            "benchmark_scenarios": [],
            "training_scenarios": [],
            "is_rest_day": True
        }

    # 获取打卡状态
    checkin_info = _get_checkin_info(date_str)

    # 分离基准场景和训练场景
    all_scenarios = day_config.get("scenarios", [])
    benchmark_scenarios = []
    training_scenarios = []

    for s in all_scenarios:
        scenario_name = s["scenario_name"]
        scenario_type = s.get("scenario_type", "training")

        # 查询该场景在该周期该天的分数
        score_info = _get_scenario_score(cycle, day, scenario_name)

        scenario_data = {
            "order": s.get("order", 0),
            "scenario": scenario_name,
            "scenario_type": scenario_type,
            "latest_score": score_info.get("latest_score"),
            "best_score": score_info.get("best_score"),
            "train_count": score_info.get("train_count", 0),
            "status": "已完成" if score_info.get("train_count", 0) > 0 else "未开始"
        }

        if scenario_type == "benchmark":
            # 基准场景：补充档位信息
            bench_info = _get_benchmark_info(scenario_name)
            scenario_data.update(bench_info)
            benchmark_scenarios.append(scenario_data)
        else:
            training_scenarios.append(scenario_data)

    return {
        "cycle": cycle,
        "day": day,
        "theme": day_config.get("theme", ""),
        "theme_label": day_config.get("theme_label", ""),
        "share_code": day_config.get("share_code", ""),
        "date": date_str,
        "checked_in": checkin_info.get("checked_in", False),
        "checkin_time": checkin_info.get("checkin_time"),
        "benchmark_scenarios": benchmark_scenarios,
        "training_scenarios": training_scenarios,
        "is_rest_day": False
    }


def get_vdim_overview() -> Dict[str, Any]:
    """获取顶部概览卡片数据"""
    today_info = get_vdim_today()

    # 计算连续打卡天数
    streak_days = _calculate_streak()

    # 计算本周完成率
    week_done, week_total = _calculate_week_progress(today_info["cycle"])

    # Gold Complete 进度（从基准数据计算）
    gold_complete, gold_total, gold_missing = _calculate_gold_progress()

    return {
        "today": {
            "cycle": today_info["cycle"],
            "day": today_info["day"],
            "theme_label": today_info["theme_label"],
            "share_code": today_info["share_code"],
            "is_rest_day": today_info.get("is_rest_day", False)
        },
        "streak_days": streak_days,
        "streak_label": "今天还没练" if not today_info["checked_in"] else f"已连续 {streak_days} 天",
        "week_done": week_done,
        "week_total": week_total,
        "week_percent": int(week_done / week_total * 100) if week_total > 0 else 0,
        "gold_complete": gold_complete,
        "gold_total": gold_total,
        "gold_percent": int(gold_complete / gold_total * 100) if gold_total > 0 else 0,
        "gold_missing": gold_missing
    }


def create_vdim_checkin(date: str, note: str = None) -> Dict[str, Any]:
    """训练打卡"""
    cycle, day = vdim_utils.get_cycle_and_day(datetime.strptime(date, "%Y-%m-%d"))
    theme, theme_label = vdim_utils.get_theme_for_day(day)
    if not theme:
        theme = "rest"
    checkin_time = int(time.time())

    # 构建 Line Protocol
    tags = (
        f"date={_escape_tag(date)},"
        f"cycle={cycle},"
        f"day={_escape_tag(day)},"
        f"theme={_escape_tag(theme)}"
    )

    fields = f"checked_in=true,checkin_time={checkin_time}"
    if note:
        fields += f',note="{_escape_field_string(note)}"'

    line = f"vdim_training_log,{tags} {fields} {checkin_time * 1000000000}"
    db.write(line)

    return {
        "date": date,
        "cycle": cycle,
        "day": day,
        "theme": theme,
        "checked_in": True,
        "checkin_time": checkin_time
    }


def create_vdim_score(
    cycle: int, day: str, scenario: str,
    score: float, accuracy: float = None,
    date: str = None, source: str = "manual"
) -> Dict[str, Any]:
    """手动补录分数"""
    theme, theme_label = vdim_utils.get_theme_for_day(day)
    if not theme:
        theme = "rest"
    scenario_type = vdim_utils.get_scenario_type(scenario, day)

    # 确定时间戳
    if date:
        target_dt = datetime.strptime(date, "%Y-%m-%d").replace(hour=20, minute=0, second=0)
        timestamp = int(target_dt.timestamp())
    else:
        timestamp = int(time.time())

    # 构建 Line Protocol
    tags = (
        f"cycle={cycle},"
        f"day={_escape_tag(day)},"
        f"theme={_escape_tag(theme)},"
        f"scenario={_escape_tag(scenario)},"
        f"scenario_type={_escape_tag(scenario_type)},"
        f"source={_escape_tag(source)}"
    )

    fields = f"score={score}"
    if accuracy is not None:
        fields += f",accuracy={accuracy}"
    fields += f',date="{_escape_field_string(date or datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"))}"'

    line = f"vdim_score,{tags} {fields} {timestamp * 1000000000}"
    db.write(line)

    return {
        "cycle": cycle,
        "day": day,
        "scenario": scenario,
        "scenario_type": scenario_type,
        "score": score,
        "accuracy": accuracy,
        "source": source,
        "timestamp": timestamp
    }


def import_vdim_scores_from_stats(cycle: int, day: str, date: str) -> Dict[str, Any]:
    """从 Kovaak's stats 目录导入分数"""
    day_config = vdim_utils.get_day_config(day)
    if not day_config:
        return {"imported": 0, "skipped": 0, "scenarios": [], "error": "无效的训练日"}

    scenario_list = day_config.get("scenarios", [])
    theme = day_config.get("theme", "")

    # 获取当天的 stats 文件
    stats_files = vdim_utils.get_stats_files_for_date(date)

    # 解析所有文件，按场景取最佳分数
    scenario_scores = {}  # scenario_name -> (score, timestamp)
    for filepath in stats_files:
        parsed = vdim_utils.parse_stats_file(filepath)
        if not parsed:
            continue
        scenario_name, score, timestamp_iso = parsed
        # 匹配场景
        matched = vdim_utils.match_scenario(scenario_name, scenario_list)
        if not matched:
            continue
        matched_name = matched["scenario_name"]
        # 取最佳分数
        if matched_name not in scenario_scores or score > scenario_scores[matched_name][0]:
            scenario_scores[matched_name] = (score, timestamp_iso)

    # 写入 InfluxDB
    imported = []
    for scenario_name, (score, timestamp_iso) in scenario_scores.items():
        scenario_type = vdim_utils.get_scenario_type(scenario_name, day)
        dt = datetime.fromisoformat(timestamp_iso)
        timestamp = int(dt.timestamp())

        tags = (
            f"cycle={cycle},"
            f"day={_escape_tag(day)},"
            f"theme={_escape_tag(theme)},"
            f"scenario={_escape_tag(scenario_name)},"
            f"scenario_type={_escape_tag(scenario_type)},"
            f"source=auto"
        )
        fields = f"score={score},date=\"{_escape_field_string(date)}\""
        line = f"vdim_score,{tags} {fields} {timestamp * 1000000000}"
        db.write(line)

        imported.append({"scenario": scenario_name, "score": score})

    return {
        "imported": len(imported),
        "skipped": len(stats_files) - len(imported),
        "scenarios": imported,
        "total_stats_files": len(stats_files)
    }


def get_vdim_playlists() -> Dict[str, Any]:
    """获取 VDIM playlist 配置"""
    return vdim_utils.load_vdim_config()


def get_vdim_scenario_history(scenario: str, days: int = 30) -> Dict[str, Any]:
    """获取某场景的历史分数"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -{days}d)
  |> filter(fn: (r) => r._measurement == "vdim_score" and r.scenario == "{_flux_escape(scenario)}")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario", "cycle", "day"])
  |> sort(columns: ["_time"])
'''
    rows = db.query(flux)
    history = []
    for row in rows:
        time_str = row.get("_time", "")
        # 转换时间格式
        try:
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = time_str[:10] if time_str else ""
        history.append({
            "date": date_str,
            "score": float(row.get("_value", 0)),
            "cycle": row.get("cycle"),
            "day": row.get("day")
        })

    return {
        "scenario": scenario,
        "history": history
    }


# ==================== 内部辅助函数 ====================

def _is_checked_in(date: str) -> bool:
    """检查某天是否已打卡"""
    try:
        flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -90d)
  |> filter(fn: (r) => r._measurement == "vdim_training_log" and r.date == "{_flux_escape(date)}")
  |> filter(fn: (r) => r._field == "checked_in")
  |> last()
'''
        rows = db.query(flux)
        return len(rows) > 0
    except Exception as e:
        print(f"[警告] 查询打卡状态失败 {date}: {e}")
        return False


def _get_checkin_info(date: str) -> Dict[str, Any]:
    """获取某天的打卡信息"""
    try:
        flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -90d)
  |> filter(fn: (r) => r._measurement == "vdim_training_log" and r.date == "{_flux_escape(date)}")
  |> filter(fn: (r) => r._field == "checked_in" or r._field == "checkin_time")
  |> last()
'''
        rows = db.query(flux)
        result = {"checked_in": False, "checkin_time": None}
        for row in rows:
            field = row.get("_field")
            value = row.get("_value")
            if field == "checked_in":
                result["checked_in"] = str(value).lower() == "true"
            elif field == "checkin_time":
                result["checkin_time"] = int(float(value)) if value else None
        return result
    except Exception as e:
        print(f"[警告] 查询打卡信息失败 {date}: {e}")
        return {"checked_in": False, "checkin_time": None}


def _count_done_scenarios(cycle: int, day: str) -> int:
    """统计某周期某天已完成的场景数（有分数的场景数）"""
    try:
        flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "vdim_score" and r.cycle == "{cycle}" and r.day == "{_flux_escape(day)}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''
        rows = db.query(flux)
        return len(rows)
    except Exception as e:
        print(f"[警告] 统计完成场景数失败: {e}")
        return 0


def _get_scenario_score(cycle: int, day: str, scenario: str) -> Dict[str, Any]:
    """获取某场景在某周期某天的分数信息"""
    try:
        flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "vdim_score" and r.cycle == "{cycle}" and r.day == "{_flux_escape(day)}" and r.scenario == "{_flux_escape(scenario)}")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value"])
  |> sort(columns: ["_time"])
'''
        rows = db.query(flux)
        if not rows:
            return {"latest_score": None, "best_score": None, "train_count": 0}

        scores = [float(row.get("_value", 0)) for row in rows]
        return {
            "latest_score": scores[-1],
            "best_score": max(scores),
            "train_count": len(scores)
        }
    except Exception as e:
        print(f"[警告] 查询场景分数失败 {scenario}: {e}")
        return {"latest_score": None, "best_score": None, "train_count": 0}


def _get_benchmark_info(scenario: str) -> Dict[str, Any]:
    """获取基准场景的档位信息（从 kovaak_score 查询最新分数和档位）"""
    # 先尝试从基准配置文件获取档位线
    try:
        import json
        import os
        bench_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "..", "..", "docs", "清单", "Viscose基准-原始数据", "S2-官方分类诊断.json"
        )
        if os.path.exists(bench_file):
            with open(bench_file, "r", encoding="utf-8") as f:
                bench_data = json.load(f)
            # 查找场景
            for item in bench_data if isinstance(bench_data, list) else bench_data.get("scenarios", []):
                if item.get("scenario", "").lower() == scenario.lower():
                    return {
                        "rank": item.get("current_rank"),
                        "next_rank": item.get("next_rank"),
                        "gap": item.get("gap"),
                        "category": item.get("category", ""),
                        "subcategory": item.get("subcategory", "")
                    }
    except Exception:
        pass

    return {
        "rank": None,
        "next_rank": None,
        "gap": None,
        "category": "",
        "subcategory": ""
    }


def _calculate_streak() -> int:
    """计算连续打卡天数（从今天往前数）"""
    today = datetime.now()
    streak = 0
    # 从今天往前数 90 天
    for i in range(90):
        check_date = (today - __import__('datetime').timedelta(days=i)).strftime("%Y-%m-%d")
        if _is_checked_in(check_date):
            streak += 1
        else:
            # 如果今天没打卡，不中断，从昨天开始算
            if i == 0:
                continue
            break
    return streak


def _calculate_week_progress(cycle: int) -> tuple:
    """计算本周完成率（已打卡天数 / 6）"""
    done = 0
    for day_num in range(1, 7):  # Day1-Day6，不含 Day7
        day = f"Day{day_num}"
        target_date = vdim_utils.get_date_for_cycle_day(cycle, day)
        date_str = target_date.strftime("%Y-%m-%d")
        if _is_checked_in(date_str):
            done += 1
    return done, 6


def _calculate_gold_progress() -> tuple:
    """计算 Gold Complete 进度（12 子类中达到 Gold 的数量）"""
    # 简化：从基准分析结果读取，暂时返回固定值（后续可动态计算）
    # 12 个子类：Arm, Wrist, Fingertip, Micro, Reading, Precision, Speed, Reactivity, Evasive, Dynamic, Static, Movement
    # 当前已知：10/12，差 Wrist, Reading
    return 10, 12, ["Wrist", "Reading"]
