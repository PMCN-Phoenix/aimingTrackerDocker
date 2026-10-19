# -*- coding: utf-8 -*-
"""VDIM 工具函数：周期计算、配置读取、stats 解析"""
import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# 配置文件路径
VDIM_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "vdim_playlists.json"
)

# 实际训练日映射表（日期 → cycle/day）。训练不按日历走，以实际内容为准。
VDIM_DAY_MAP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "vdim_day_map.json"
)

# Kovaak's stats 目录
STATS_DIR = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"

# 全局配置缓存
_vdim_config = None
_vdim_day_map = None


def load_vdim_config() -> Dict[str, Any]:
    """加载 VDIM playlist 配置（带缓存）"""
    global _vdim_config
    if _vdim_config is not None:
        return _vdim_config
    with open(VDIM_CONFIG_PATH, "r", encoding="utf-8") as f:
        _vdim_config = json.load(f)
    return _vdim_config


def get_start_date() -> datetime:
    """获取 VDIM 开始日期"""
    config = load_vdim_config()
    return datetime.strptime(config["start_date"], "%Y-%m-%d")


def load_day_map() -> Dict[str, Dict[str, Any]]:
    """加载「实际训练日映射表」（带缓存）。文件不存在时返回空表，退回纯日历推算。"""
    global _vdim_day_map
    if _vdim_day_map is not None:
        return _vdim_day_map
    try:
        with open(VDIM_DAY_MAP_PATH, "r", encoding="utf-8") as f:
            _vdim_day_map = json.load(f).get("days", {})
    except FileNotFoundError:
        _vdim_day_map = {}
    except Exception as e:
        print(f"[警告] 读取 vdim_day_map.json 失败，退回日历推算: {e}")
        _vdim_day_map = {}
    return _vdim_day_map


def _advance_cycle_day(cycle: int, day: str, delta_days: int) -> Tuple[int, str]:
    """把 (cycle, day) 按 7 天周期往后推 delta_days 天"""
    idx = int(day.replace("Day", "")) - 1 + delta_days
    return cycle + idx // 7, "Day%d" % (idx % 7 + 1)


def get_cycle_and_day(target_date: datetime) -> Tuple[int, str]:
    """
    根据日期计算是第几周第几天。

    返回: (cycle, day)
    - cycle: 第几周（从1开始）
    - day: Day1, Day2, ..., Day7

    优先级：
      1. `vdim_day_map.json` 里登记的日期 → 直接用（这是「实际练了什么」的事实）
      2. 未登记但晚于表内最早日期 → 从**最近一次已登记日期**顺延推算
         （训练中间会断档，纯日历推算会错位）
      3. 早于映射表 → 退回 `vdim_playlists.json` 的 start_date 日历推算
    """
    d = target_date.date()
    key = d.isoformat()
    day_map = load_day_map()

    if key in day_map:
        entry = day_map[key]
        return int(entry["cycle"]), entry["day"]

    prior = sorted(k for k in day_map if k <= key)
    if prior:
        base_key = prior[-1]
        base_date = datetime.strptime(base_key, "%Y-%m-%d").date()
        entry = day_map[base_key]
        return _advance_cycle_day(int(entry["cycle"]), entry["day"], (d - base_date).days)

    start_date = get_start_date()
    delta_days = (d - start_date.date()).days
    cycle = delta_days // 7 + 1
    return cycle, "Day%d" % (delta_days % 7 + 1)


def get_date_for_cycle_day(cycle: int, day: str) -> datetime:
    """
    获取某周期某天的日期。

    1. 映射表里有这个 (cycle, day) → 用它。同一 (cycle, day) 可能有多条日期
       （拆成两天练），取 `primary=true` 的那条；没有 primary 就取最晚一条。
    2. 该周期有别的登记日、但没有这一天 → 以**该周期最晚登记日**为锚点顺推。
       不能用 start_date 全局推算：日历周期和实际训练已经错位，算出来的日期
       会和已登记的日期撞车（导致一周完成率把同一天数两遍）。
    3. 整个周期都没登记过 → 退回 start_date 日历推算。
    """
    day_map = load_day_map()
    target_idx = int(day.replace("Day", "")) - 1  # 0-6

    candidates = [(k, v) for k, v in day_map.items()
                  if int(v.get("cycle", 0)) == cycle and v.get("day") == day]
    if candidates:
        primary = [c for c in candidates if c[1].get("primary")]
        chosen_key = (primary or sorted(candidates))[-1][0]
        return datetime.strptime(chosen_key, "%Y-%m-%d")

    same_cycle = [(k, v) for k, v in day_map.items() if int(v.get("cycle", 0)) == cycle]
    if same_cycle:
        anchor_key, anchor = max(same_cycle, key=lambda c: c[0])
        anchor_date = datetime.strptime(anchor_key, "%Y-%m-%d")
        anchor_idx = int(anchor["day"].replace("Day", "")) - 1
        return anchor_date + timedelta(days=target_idx - anchor_idx)

    start_date = get_start_date()
    return start_date + timedelta(days=(cycle - 1) * 7 + target_idx)


def get_date_range_for_cycle_day(cycle: int, day: str) -> Tuple[datetime, datetime]:
    """
    获取某周期某天的日期范围（当天 00:00:00 到 23:59:59，北京时间）。
    """
    target_date = get_date_for_cycle_day(cycle, day)
    start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = target_date.replace(hour=23, minute=59, second=59, microsecond=0)
    return start, end


def get_day_config(day: str) -> Optional[Dict[str, Any]]:
    """获取某个训练日的配置（主题、分享码、场景列表）"""
    config = load_vdim_config()
    for d in config["days"]:
        if d["day"] == day:
            # 统一字段名，方便后续使用
            result = dict(d)
            result["theme_label"] = d.get("theme_name", d.get("theme", ""))
            # 统一场景字段名
            scenarios = []
            for s in d.get("scenarios", []):
                scenarios.append({
                    "order": s.get("order", s.get("play_order", 0)),
                    "scenario_name": s.get("name", s.get("scenario_name", "")),
                    "scenario_type": s.get("type", s.get("scenario_type", "training")),
                    "play_count": s.get("play_count", 0)
                })
            result["scenarios"] = scenarios
            return result
    return None


def get_all_days_config() -> List[Dict[str, Any]]:
    """获取所有训练日配置（统一字段名）"""
    config = load_vdim_config()
    result = []
    for d in config["days"]:
        result.append(get_day_config(d["day"]))
    return result


def get_scenario_type(scenario_name: str, day: str = None) -> str:
    """
    获取场景类型（benchmark 或 training）。
    如果指定了 day，只在该 day 的场景列表中查找。
    """
    days_to_search = [get_day_config(day)] if day else get_all_days_config()
    for d in days_to_search:
        if not d:
            continue
        for s in d["scenarios"]:
            if s["scenario_name"].lower() == scenario_name.lower():
                return s.get("scenario_type", "training")
    return "training"


def get_theme_for_day(day: str) -> Tuple[str, str]:
    """获取某天的主题（theme, theme_label）"""
    d = get_day_config(day)
    if d:
        return d.get("theme", ""), d.get("theme_label", "")
    return "", ""


def normalize_scenario_name(name: str) -> str:
    """
    标准化场景名，用于匹配。
    - 去除首尾空格
    - 转小写
    - 去除版本后缀如 " v2", " v3"
    """
    name = name.strip().lower()
    # 去除版本后缀
    name = re.sub(r'\s+v\d+$', '', name)
    return name


def match_scenario(scenario_name: str, scenario_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    在场景列表中匹配场景名（模糊匹配）。
    返回匹配到的场景配置，没找到返回 None。
    """
    normalized = normalize_scenario_name(scenario_name)
    for s in scenario_list:
        if normalize_scenario_name(s["scenario_name"]) == normalized:
            return s
    return None


def parse_stats_file(filepath: str) -> Optional[Tuple[str, float, str]]:
    """
    解析单个 stats csv 文件，返回 (scenario, score, timestamp_iso)。
    timestamp_iso 格式：YYYY-MM-DDTHH:MM:SS+08:00
    """
    filename = os.path.basename(filepath)
    # 从文件名提取场景名："Scenario Name - Challenge - 2026.10.08-16.24.33 Stats.csv"
    m = re.match(
        r"^(.+?) - Challenge - (\d{4}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2}) Stats\.csv$",
        filename
    )
    if not m:
        return None
    scenario = m.group(1)
    date_str = m.group(2).replace(".", "-")
    time_str = m.group(3).replace(".", ":")
    timestamp_str = f"{date_str}T{time_str}+08:00"

    # 从文件内容读取 Score
    score = None
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # 找 "Score:," 后面的数字
        score_match = re.search(r"Score:,([\d.]+)", content)
        if score_match:
            score = float(score_match.group(1))
    except Exception:
        pass

    if score is None:
        return None

    return scenario, score, timestamp_str


def get_stats_files_for_date(date_str: str) -> List[str]:
    """
    获取指定日期的所有 stats 文件路径。
    date_str 格式：YYYY-MM-DD
    """
    if not os.path.exists(STATS_DIR):
        return []

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    files = []
    for f in os.listdir(STATS_DIR):
        if not f.endswith(".csv"):
            continue
        filepath = os.path.join(STATS_DIR, f)
        mtime = os.path.getmtime(filepath)
        mtime_dt = datetime.fromtimestamp(mtime)
        if mtime_dt.date() == target_date:
            files.append(filepath)

    files.sort(key=lambda x: os.path.getmtime(x))
    return files
