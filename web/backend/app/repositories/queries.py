# -*- coding: utf-8 -*-
"""数据查询函数——对应文档里定义的所有查询模式"""
from typing import List, Dict, Any, Optional
from .influx_client import db


# ==================== aim_scenario 查询 ====================

def get_scenario_best(scenario: str, start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> Dict[str, Any]:
    """查某个场景在某段时间内的最佳成绩（score / accuracy）"""
    from datetime import datetime
    
    # 把时间戳转成 RFC3339 格式的时间字符串（UTC）
    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
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
    from datetime import datetime
    
    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
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
    from datetime import datetime
    
    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
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
        if field in ["start_ts", "end_ts", "items", "rounds_total", "created_at"]:
            try:
                result[field] = int(float(value))
            except:
                result[field] = value
        else:
            result[field] = value
    return result


def get_daylist_progress_data(daylist: str) -> Dict[str, Any]:
    """获取清单的完整进度数据（包含 rows）"""
    from datetime import datetime, timedelta

    # 1. 查清单行
    rows = get_daylist_rows(daylist)
    if not rows:
        return {"daylist": daylist, "rows": []}

    # 2. 查元数据
    meta = get_daylist_meta(daylist)

    # 3. 计算时间范围
    exec_dates = meta.get("exec_dates", "")
    if exec_dates:
        dates = [d.strip() for d in exec_dates.split(',') if d.strip()]
        if dates:
            first_date = datetime.strptime(dates[0], '%Y-%m-%d')
            start_ts = int(first_date.timestamp())
            last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
            last_dt = last_date + timedelta(days=1) - timedelta(seconds=1)
            end_ts = int(last_dt.timestamp())
        else:
            start_ts = meta.get("start_ts", 0)
            end_ts = meta.get("end_ts", 0)
    else:
        start_ts = meta.get("start_ts", 0)
        end_ts = meta.get("end_ts", 0)

    # 4. 判断是否是加练清单
    is_extra = meta.get("type") == "extra"
    created_at = meta.get("created_at", 0)

    # 5. 查所有场景的轮数
    if is_extra and created_at:
        rounds_map = {}
        for row in rows:
            scn = row.get("scenario", "")
            rounds_map[scn] = get_extra_scenario_rounds(scn, start_ts, end_ts, created_at)
    else:
        rounds_map = get_all_scenarios_rounds(start_ts, end_ts)

    # 6. 组合数据
    result_rows = []
    for row in rows:
        scn = row.get("scenario", "")
        required = row.get("rounds", 0)
        done = rounds_map.get(scn, 0)

        if done == 0:
            status = "未开始"
        elif done >= required:
            status = "已完成"
        else:
            status = "进行中"

        result_rows.append({
            "order": row.get("order", 0),
            "scenario": scn,
            "role": row.get("role", ""),
            "required_rounds": required,
            "done_rounds": done,
            "status": status
        })

    return {
        "daylist": daylist,
        "label": meta.get("label", ""),
        "name": meta.get("name", ""),
        "type": meta.get("type", "main"),
        "parent_daylist": meta.get("parent_daylist", ""),
        "created_at": created_at,
        "run_date": meta.get("run_date", ""),
        "exec_dates": exec_dates,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "items": meta.get("items", len(result_rows)),
        "rounds_total": meta.get("rounds_total", 0),
        "rows": result_rows
    }


def get_daylist_extras(parent_daylist: str) -> List[Dict[str, Any]]:
    """查某个主清单的所有加练清单（包含完整进度）"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta")
  |> filter(fn: (r) => r._field == "parent_daylist" and r._value == "{parent_daylist}")
  |> keep(columns: ["_value", "daylist"])
'''
    rows = db.query(flux)
    extras = []
    seen = set()
    for row in rows:
        daylist = row.get("daylist")
        if daylist and daylist not in seen:
            seen.add(daylist)
            # 获取完整进度（包含 rows）
            progress = get_daylist_progress_data(daylist)
            extras.append(progress)
    # 按 created_at 排序
    extras.sort(key=lambda x: x.get("created_at", 0))
    return extras


def get_extra_scenario_rounds(
    scenario: str,
    start_ts: int,
    end_ts: int,
    created_at: int,
    list_name: str = "viscose-s2-easier"
) -> int:
    """查加练清单中某个场景的轮数（只统计 created_at 之后的）"""
    from datetime import datetime, timedelta

    # 加练清单的开始时间是 created_at
    extra_start = created_at if created_at else start_ts

    # 如果 created_at 超出了 end_ts，扩展 end_ts 到 created_at + 1天
    if extra_start > end_ts:
        end_ts = extra_start + 86400  # 加 1 天

    start_str = datetime.utcfromtimestamp(extra_start).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')

    # 转义场景名里的引号
    scenario_escaped = scenario.replace('"', '\\"')

    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "{scenario_escaped}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''
    rows = db.query(flux)
    if rows:
        return int(float(rows[0].get("_value", 0)))
    return 0


def create_extra_daylist(
    parent_daylist: str,
    name: str,
    exec_dates: str,
    items: List[Dict[str, Any]],
    created_at: int = None
) -> Dict[str, Any]:
    """创建加练清单"""
    import time
    import json

    if created_at is None:
        created_at = int(time.time())

    # 生成加练清单 ID：{parent}-extra-{序号}
    extras = get_daylist_extras(parent_daylist)
    next_num = len(extras) + 1
    daylist_id = f"{parent_daylist}-extra-{next_num}"

    # 计算总轮数
    rounds_total = sum(item.get("rounds", 0) for item in items)

    # 计算时间范围
    from datetime import datetime, timedelta
    dates = [d.strip() for d in exec_dates.split(',') if d.strip()]
    if dates:
        first_date = datetime.strptime(dates[0], '%Y-%m-%d')
        start_ts = int(first_date.timestamp())
        last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
        last_dt = last_date + timedelta(days=1) - timedelta(seconds=1)
        end_ts = int(last_dt.timestamp())
    else:
        start_ts = 0
        end_ts = 0

    # 写入元数据（用纳秒级时间戳）
    ts = int(time.time())
    ts_ns = ts * 1000000000
    meta_lines = [
        f'aim_daylist_meta,daylist={daylist_id} parent_daylist="{parent_daylist}" {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} type="extra" {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} name="{name}" {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} exec_dates="{exec_dates}" {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} created_at={created_at} {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} items={len(items)} {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} rounds_total={rounds_total} {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} start_ts={start_ts} {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} end_ts={end_ts} {ts_ns}',
        f'aim_daylist_meta,daylist={daylist_id} label="{parent_daylist} 加练" {ts_ns}',
    ]
    for line in meta_lines:
        db.write(line)

    # 写入清单项
    for item in items:
        row_json = json.dumps(item, ensure_ascii=False)
        # 转义 JSON 里的双引号
        row_json_escaped = row_json.replace('"', '\\"')
        scenario = item.get("scenario", "")
        role = item.get("role", "")
        scenario_tag = scenario.replace(' ', '\\ ').replace(',', '\\,')
        line = f'aim_daylist,daylist={daylist_id},scenario={scenario_tag},role={role} rowJson="{row_json_escaped}" {ts_ns}'
        db.write(line)

    return {
        "daylist": daylist_id,
        "parent_daylist": parent_daylist,
        "name": name,
        "type": "extra",
        "created_at": created_at,
        "items": len(items),
        "rounds_total": rounds_total
    }


def delete_extra_daylist(daylist: str) -> Dict[str, Any]:
    """删除加练清单（只删除元数据和清单项，不删除成绩数据）"""
    # 删除元数据
    flux_delete_meta = f'''
import "influxdata/influxdb/v1"
v1.delete(
    bucket: "{db.bucket}",
    org: "{db.org}",
    predicate: "_measurement=\\"aim_daylist_meta\\" AND daylist=\\"{daylist}\\"",
    start: 1970-01-01T00:00:00Z,
    stop: 2099-12-31T23:59:59Z
)
'''
    try:
        db.query(flux_delete_meta)
    except:
        pass

    # 删除清单项
    flux_delete_rows = f'''
import "influxdata/influxdb/v1"
v1.delete(
    bucket: "{db.bucket}",
    org: "{db.org}",
    predicate: "_measurement=\\"aim_daylist\\" AND daylist=\\"{daylist}\\"",
    start: 1970-01-01T00:00:00Z,
    stop: 2099-12-31T23:59:59Z
)
'''
    try:
        db.query(flux_delete_rows)
    except:
        pass

    return {"daylist": daylist, "deleted": True}


def generate_playlist_json(daylist: str, name: str = None) -> Dict[str, Any]:
    """生成 Kovaak's playlist.json 格式的数据"""
    import time

    rows = get_daylist_rows(daylist)
    meta = get_daylist_meta(daylist)

    playlist_name = name or meta.get("name") or meta.get("label") or daylist

    # 构建 scenarioList
    scenario_list = []
    for row in rows:
        scenario = row.get("scenario", "")
        rounds = row.get("rounds", 1)
        # Kovaak's playlist 里同一个场景可以分多次，这里直接用总轮数
        scenario_list.append({
            "scenario_name": scenario,
            "play_Count": rounds
        })

    playlist = {
        "playlistName": playlist_name,
        "playlistId": int(time.time()) % 1000000,
        "authorSteamId": "76561199835441317",
        "authorName": "铎克",
        "scenarioList": scenario_list,
        "description": f"{playlist_name} - 共 {len(rows)} 个场景，{sum(r.get('rounds', 0) for r in rows)} 轮",
        "hasOfflineScenarios": False,
        "hasEdited": True,
        "shareCode": "",
        "version": 31,
        "updated": int(time.time()),
        "isPrivate": False
    }

    return playlist


def export_playlist_to_kovaaks(daylist: str, name: str = None) -> Dict[str, Any]:
    """导出 playlist 到 Kovaak's Playlists 目录"""
    import json
    import os
    import shutil

    playlist = generate_playlist_json(daylist, name)
    playlist_name = playlist.get("playlistName", daylist)

    # 生成文件名（去掉特殊字符）
    safe_name = playlist_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    filename = f"{safe_name}.json"

    # Kovaak's Playlists 目录
    kovaaks_playlists = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists"

    # 先保存到项目临时目录
    temp_dir = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\temp_playlists"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)

    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)

    # 复制到 Kovaak's Playlists 目录
    copied = False
    if os.path.exists(kovaaks_playlists):
        dest_path = os.path.join(kovaaks_playlists, filename)
        shutil.copy2(temp_path, dest_path)
        copied = True

    return {
        "daylist": daylist,
        "playlist_name": playlist_name,
        "filename": filename,
        "temp_path": temp_path,
        "copied_to_kovaaks": copied,
        "kovaaks_path": os.path.join(kovaaks_playlists, filename) if copied else None
    }


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
    import json
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_bench_row" and r.list == "{list_name}")
  |> keep(columns: ["_value", "_field", "scenario"])
'''
    rows = db.query(flux)
    # 按场景分组
    scenarios = {}
    for row in rows:
        scenario = row.get("scenario")
        if scenario not in scenarios:
            scenarios[scenario] = {
                "scenario": scenario,
                "cat": None,
                "sub": None,
                "nextLine": None,
                "pct": None,
                "gapPct": None,
                "achIdx": None,
                "rank": None,
                "subRank": None,
                "score": None,
                "acc": None,
                "targets": None
            }
        field = row.get("_field")
        value = row.get("_value")
        
        # rowJson 是完整的 JSON 字符串，解析它
        if field == "rowJson":
            try:
                row_data = json.loads(value)
                scenarios[scenario]["cat"] = row_data.get("cat")
                scenarios[scenario]["sub"] = row_data.get("sub")
                scenarios[scenario]["rank"] = row_data.get("rank")
                scenarios[scenario]["subRank"] = row_data.get("subRank")
                scenarios[scenario]["score"] = row_data.get("score")
                scenarios[scenario]["acc"] = row_data.get("acc")
                scenarios[scenario]["targets"] = row_data.get("targets")
                scenarios[scenario]["achIdx"] = row_data.get("achIdx")
                scenarios[scenario]["pct"] = row_data.get("pct")
                scenarios[scenario]["gapPct"] = row_data.get("gapPct")
                # 下一档线：targets 数组里 achIdx 对应的下一个
                targets = row_data.get("targets", [])
                ach_idx = row_data.get("achIdx", 0)
                if targets and ach_idx < len(targets):
                    scenarios[scenario]["nextLine"] = targets[ach_idx]
            except:
                pass
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


# ==================== Aim Lab 查询 ====================

def get_aimlab_tasks() -> List[Dict[str, Any]]:
    """查所有 Aim Lab 任务的最佳成绩"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -90d)
  |> filter(fn: (r) => r._measurement == "aimlab_task")
  |> filter(fn: (r) => r._field == "score" or r._field == "accuracy")
  |> keep(columns: ["_time", "_value", "_field", "task"])
  |> group(columns: ["task", "_field"])
  |> max()
'''
    rows = db.query(flux)
    
    # 按任务分组
    tasks = {}
    for row in rows:
        task = row.get("task", "未知")
        if task not in tasks:
            tasks[task] = {
                "task": task,
                "best_score": None,
                "best_accuracy": None,
            }
        field = row.get("_field")
        value = row.get("_value")
        if field == "score":
            tasks[task]["best_score"] = float(value) if value else None
        elif field == "accuracy":
            tasks[task]["best_accuracy"] = float(value) if value else None
    
    return list(tasks.values())


def get_aimlab_task_history(task: str, days: int = 30) -> List[Dict[str, Any]]:
    """查某个 Aim Lab 任务的历史成绩"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -{days}d)
  |> filter(fn: (r) => r._measurement == "aimlab_task" and r.task == "{task}")
  |> filter(fn: (r) => r._field == "score" or r._field == "accuracy")
  |> keep(columns: ["_time", "_value", "_field", "task"])
  |> sort(columns: ["_time"])
'''
    rows = db.query(flux)
    
    # 按时间分组，把 score 和 accuracy 放一起
    history = {}
    for row in rows:
        time = row.get("_time")
        if time not in history:
            history[time] = {
                "time": time,
                "score": None,
                "accuracy": None,
            }
        field = row.get("_field")
        value = row.get("_value")
        if field == "score":
            history[time]["score"] = float(value) if value else None
        elif field == "accuracy":
            history[time]["accuracy"] = float(value) if value else None
    
    return list(history.values())
