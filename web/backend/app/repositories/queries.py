# -*- coding: utf-8 -*-
"""数据查询函数——对应文档里定义的所有查询模式"""
from typing import List, Dict, Any, Optional
from .influx_client import db


# ==================== aim_scenario 查询 ====================

def get_scenario_best(scenario: str, start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> Dict[str, Any]:
    """查某个场景在某段时间内的最佳成绩（score / accuracy）"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: int(v: {start_ts}) * 1000000000, stop: int(v: {end_ts}) * 1000000000)
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score" or r._field == "accuracy")
  |> keep(columns: ["_time", "_value", "_field", "scenario"])
  |> group(columns: ["scenario", "_field"])
  |> max()
'''
    rows = db.query(flux)
    result = {"scenario": scenario, "score": None, "accuracy": None}
    for row in rows:
        field = row.get("_field")
        value = row.get("_value")
        if field == "score":
            result["score"] = float(value) if value else None
        elif field == "accuracy":
            result["accuracy"] = float(value) if value else None
    return result


def get_scenario_rounds(scenario: str, start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> int:
    """查某个场景在某段时间内打了多少轮"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: int(v: {start_ts}) * 1000000000, stop: int(v: {end_ts}) * 1000000000)
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''
    rows = db.query(flux)
    if rows:
        return int(float(rows[0].get("_value", 0)))
    return 0


def get_all_scenarios_rounds(start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> Dict[str, int]:
    """查某段时间内所有场景的打靶轮数"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: int(v: {start_ts}) * 1000000000, stop: int(v: {end_ts}) * 1000000000)
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''
    rows = db.query(flux)
    result = {}
    for row in rows:
        scenario = row.get("scenario")
        count = int(float(row.get("_value", 0)))
        result[scenario] = count
    return result


def get_scenario_history(scenario: str, days: int = 30, list_name: str = "viscose-s2-easier") -> List[Dict[str, Any]]:
    """查某个场景的历史成绩趋势"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -{days}d)
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario"])
'''
    rows = db.query(flux)
    result = []
    for row in rows:
        result.append({
            "time": row.get("_time"),
            "score": float(row.get("_value", 0)),
            "scenario": row.get("scenario")
        })
    return result


# ==================== aim_reflection 查询 ====================

def get_scenario_reflections(scenario: str, days: int = 30) -> List[Dict[str, Any]]:
    """查某个场景的所有历史感悟"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -{days}d)
  |> filter(fn: (r) => r._measurement == "aim_reflection" and r.scenario == "{scenario}")
  |> keep(columns: ["_time", "_value", "scenario"])
'''
    rows = db.query(flux)
    result = []
    for row in rows:
        result.append({
            "date": row.get("_time"),
            "note": row.get("_value"),
            "scenario": row.get("scenario")
        })
    # 按日期倒序
    result.sort(key=lambda x: x["date"], reverse=True)
    return result


def create_reflection(scenario: str, note: str, daylist: str = None) -> Dict[str, Any]:
    """新增一条感悟"""
    import time
    ts = int(time.time())
    
    # 构建 Line Protocol
    tags = f"scenario={scenario}"
    if daylist:
        tags += f",daylist={daylist}"
    
    # 转义感悟里的逗号和空格
    note_escaped = note.replace(',', '\\,').replace(' ', '\\ ')
    
    line = f"aim_reflection,{tags} note=\"{note_escaped}\" {ts * 1000000000}"
    
    # 写入 InfluxDB
    db.write(line)
    
    return {
        "scenario": scenario,
        "note": note,
        "daylist": daylist,
        "time": ts
    }


# ==================== aim_daylist 查询 ====================

def get_daylist_rows(daylist: str) -> List[Dict[str, Any]]:
    """查某个清单的所有行"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist" and r.daylist == "{daylist}")
  |> filter(fn: (r) => r._field == "rowJson")
  |> keep(columns: ["_value", "scenario", "role"])
'''
    rows = db.query(flux)
    result = []
    for row in rows:
        import json
        try:
            row_json = json.loads(row.get("_value", "{}"))
            result.append(row_json)
        except:
            pass
    # 按 order 排序
    result.sort(key=lambda x: x.get("order", 0))
    return result


def get_all_daylists() -> List[Dict[str, Any]]:
    """查所有清单列表"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "run_date")
  |> keep(columns: ["_value", "daylist", "label"])
'''
    rows = db.query(flux)
    result = []
    for row in rows:
        result.append({
            "daylist": row.get("daylist"),
            "label": row.get("label"),
            "run_date": row.get("_value")
        })
    # 按 daylist 倒序
    result.sort(key=lambda x: x["daylist"], reverse=True)
    return result


# ==================== aim_daylist_meta 查询 ====================

def get_daylist_meta(daylist: str) -> Dict[str, Any]:
    """查某个清单的元数据"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "{daylist}")
  |> keep(columns: ["_value", "_field", "daylist"])
'''
    rows = db.query(flux)
    result = {"daylist": daylist}
    for row in rows:
        field = row.get("_field")
        value = row.get("_value")
        if field in ["start_ts", "end_ts", "items", "rounds_total"]:
            try:
                result[field] = int(float(value))
            except:
                result[field] = value
        else:
            result[field] = value
    return result


# ==================== aim_bench_row 查询 ====================

def get_scenario_bench(scenario: str, list_name: str = "viscose-s2-easier") -> Dict[str, Any]:
    """查某个场景的基准数据"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_bench_row" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> keep(columns: ["_value", "_field", "scenario"])
'''
    rows = db.query(flux)
    result = {"scenario": scenario, "nextLine": None, "pct": None, "gapPct": None, "achIdx": None, "rank": None, "sub": None, "subRank": None}
    for row in rows:
        field = row.get("_field")
        value = row.get("_value")
        if field in ["nextLine", "pct", "gapPct", "achIdx"]:
            try:
                result[field] = float(value)
            except:
                result[field] = value
        elif field in ["rank", "sub", "subRank"]:
            result[field] = value
    return result


# ==================== 基准总览查询 ====================

def get_all_bench_scenarios(list_name: str = "viscose-s2-easier") -> List[Dict[str, Any]]:
    """查某个清单下所有场景的基准数据"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_bench_row" and r.list == "{list_name}")
  |> keep(columns: ["_value", "_field", "scenario", "cat", "sub"])
'''
    rows = db.query(flux)
    # 按场景分组
    scenarios = {}
    for row in rows:
        scenario = row.get("scenario")
        if scenario not in scenarios:
            scenarios[scenario] = {
                "scenario": scenario,
                "cat": row.get("cat"),
                "sub": row.get("sub"),
                "nextLine": None,
                "pct": None,
                "gapPct": None,
                "achIdx": None,
                "rank": None,
                "subRank": None
            }
        field = row.get("_field")
        value = row.get("_value")
        if field in ["nextLine", "pct", "gapPct", "achIdx"]:
            try:
                scenarios[scenario][field] = float(value)
            except:
                scenarios[scenario][field] = value
        elif field in ["rank", "subRank"]:
            try:
                scenarios[scenario][field] = int(float(value))
            except:
                scenarios[scenario][field] = value
    return list(scenarios.values())


def get_bench_groups(list_name: str = "viscose-s2-easier") -> Dict[str, Any]:
    """查基准总览的分组数据（4 大类 14 子类）"""
    scenarios = get_all_bench_scenarios(list_name)
    
    # 按大类和子类分组
    groups = {}
    for scn in scenarios:
        cat = scn.get("cat", "未分类")
        sub = scn.get("sub", "未分类")
        if cat not in groups:
            groups[cat] = {}
        if sub not in groups[cat]:
            groups[cat][sub] = []
        groups[cat][sub].append(scn)
    
    # 计算档位分布
    rank_distribution = {}
    for scn in scenarios:
        rank = scn.get("rank", 0)
        if rank not in rank_distribution:
            rank_distribution[rank] = 0
        rank_distribution[rank] += 1
    
    return {
        "groups": groups,
        "rank_distribution": rank_distribution,
        "total": len(scenarios)
    }
