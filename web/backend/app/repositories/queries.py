# -*- coding: utf-8 -*-
"""数据查询函数——对应文档里定义的所有查询模式"""
import re
from typing import List, Dict, Any, Optional, Tuple
from .influx_client import db


# ==================== 成绩表迁移期兼容（2026-10-16 修订） ====================
# 背景：权威成绩表已迁移到 kovaak_score（含 hits/misses），旧表 aim_scenario
# 的 740 个成绩点经实测已 100% 并入新表（见 docs/接手报告-20261016.md P0-1）。
# 2026-10-16 用户决策①：旧表先备份 CSV（backup_aim_scenario.py）并标记弃用，
# 观察 2-4 周确认新表无遗漏后删除；届时本文件的旧表兜底分支可一并移除。
# 迁移期查询规则——严禁两表计数相加（旧表数据已包含在新表内，相加会双算）：
#   计数类（轮数）：以新表为准，新表无数据时才按场景粒度回退旧表；
#   极值类（最佳分）：两表取 max（幂等不会双算，且能兜底旧表独有的点）；
#   趋势类（历史）：以新表为准，新表无数据才整体回退旧表（避免同一点重复出现）。
NEW_SCORE_MEASUREMENT = "kovaak_score"
OLD_SCORE_MEASUREMENT = "aim_scenario"  # DEPRECATED：待观察期后删除，勿再写入


def _flux_count_rounds(measurement: str, scenario: str, start_str: str, end_str: str, list_name: str) -> str:
    """生成「单表单场景轮数计数」的 Flux"""
    return f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "{measurement}" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''


def _flux_count_all(measurement: str, start_str: str, end_str: str, list_name: str) -> str:
    """生成「单表全场景轮数计数」的 Flux"""
    return f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "{measurement}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> group(columns: ["scenario"])
  |> count()
'''


def _flux_history(measurement: str, scenario: str, days: int, list_name: str) -> str:
    """生成「单表历史成绩」的 Flux"""
    return f'''
from(bucket: "{db.bucket}")
  |> range(start: -{days}d)
  |> filter(fn: (r) => r._measurement == "{measurement}" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "_value", "scenario"])
'''


def _query_count(flux: str, measurement: str) -> int:
    """执行计数查询，失败返回 0"""
    try:
        rows = db.query(flux)
        if rows:
            return int(float(rows[0].get("_value", 0)))
    except Exception as e:
        print(f"查询 {measurement} 失败: {e}")
    return 0


def _query_count_map(flux: str, measurement: str) -> Dict[str, int]:
    """执行全场景计数查询，返回 {scenario: count}，失败返回 {}"""
    result: Dict[str, int] = {}
    try:
        rows = db.query(flux)
        for row in rows:
            scenario = row.get("scenario")
            if scenario:
                result[scenario] = int(float(row.get("_value", 0)))
    except Exception as e:
        print(f"查询 {measurement} 失败: {e}")
    return result


def _count_rounds_new_first(scenario: str, start_str: str, end_str: str, list_name: str) -> int:
    """单场景轮数：新表优先，新表无数据才回退旧表（防止双表双算）"""
    total = _query_count(
        _flux_count_rounds(NEW_SCORE_MEASUREMENT, scenario, start_str, end_str, list_name),
        NEW_SCORE_MEASUREMENT,
    )
    if total > 0:
        return total
    return _query_count(
        _flux_count_rounds(OLD_SCORE_MEASUREMENT, scenario, start_str, end_str, list_name),
        OLD_SCORE_MEASUREMENT,
    )


# ==================== aim_scenario 查询 ====================

def get_scenario_best(scenario: str, start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> Dict[str, Any]:
    """查某个场景在某段时间内的最佳成绩（score / accuracy）。

    同时查询 aim_scenario 和 kovaak_score 取 max：max 幂等，
    旧表数据即使已含在新表内也不会双算，还能兜底旧表独有的点。
    """
    from datetime import datetime
    
    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    result = {"scenario": scenario, "score": None, "accuracy": None}
    
    for measurement in ["aim_scenario", "kovaak_score"]:
        flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "{measurement}" and r.scenario == "{scenario}" and r.list == "{list_name}")
  |> filter(fn: (r) => r._field == "score" or r._field == "accuracy")
  |> keep(columns: ["_time", "_value", "_field", "scenario"])
  |> group(columns: ["scenario", "_field"])
  |> max()
'''
        try:
            rows = db.query(flux)
            for row in rows:
                field = row.get("_field")
                value = row.get("_value")
                if field == "score" and value:
                    val = float(value)
                    if result["score"] is None or val > result["score"]:
                        result["score"] = val
                elif field == "accuracy" and value:
                    val = float(value)
                    if result["accuracy"] is None or val > result["accuracy"]:
                        result["accuracy"] = val
        except Exception as e:
            print(f"查询 {measurement} 失败: {e}")
    
    return result


def get_scenario_rounds(scenario: str, start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> int:
    """查某个场景在某段时间内打了多少轮（新表 kovaak_score 优先，旧表 aim_scenario 仅作兜底，不相加）"""
    from datetime import datetime

    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')

    return _count_rounds_new_first(scenario, start_str, end_str, list_name)


def get_all_scenarios_rounds(start_ts: int, end_ts: int, list_name: str = "viscose-s2-easier") -> Dict[str, int]:
    """查某段时间内所有场景的打靶轮数。

    新表 kovaak_score 优先；新表整体无数据时整体回退旧表 aim_scenario；
    新表有数据时，仅对「新表计数为 0」的场景按粒度用旧表兜底。严禁两表相加（会双算）。
    """
    from datetime import datetime

    start_str = datetime.utcfromtimestamp(start_ts).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.utcfromtimestamp(end_ts).strftime('%Y-%m-%dT%H:%M:%SZ')

    # 1. 新表全量计数
    result = _query_count_map(
        _flux_count_all(NEW_SCORE_MEASUREMENT, start_str, end_str, list_name),
        NEW_SCORE_MEASUREMENT,
    )
    if not result:
        # 2. 新表完全无数据 → 整体回退旧表
        return _query_count_map(
            _flux_count_all(OLD_SCORE_MEASUREMENT, start_str, end_str, list_name),
            OLD_SCORE_MEASUREMENT,
        )

    # 3. 新表有数据：仅对新表缺失（计数为 0）的场景用旧表兜底，已双算的场景不重复计
    old_counts = _query_count_map(
        _flux_count_all(OLD_SCORE_MEASUREMENT, start_str, end_str, list_name),
        OLD_SCORE_MEASUREMENT,
    )
    for scenario, count in old_counts.items():
        if result.get(scenario, 0) == 0:
            result[scenario] = count
    return result


def get_scenario_history(scenario: str, days: int = 30, list_name: str = "viscose-s2-easier") -> List[Dict[str, Any]]:
    """查某个场景的历史成绩趋势（新表 kovaak_score 优先，旧表仅作兜底，避免同一点在两表重复出现）"""
    result = []
    for measurement in [NEW_SCORE_MEASUREMENT, OLD_SCORE_MEASUREMENT]:
        flux = _flux_history(measurement, scenario, days, list_name)
        try:
            rows = db.query(flux)
            for row in rows:
                result.append({
                    "time": row.get("_time"),
                    "score": float(row.get("_value", 0)),
                    "scenario": row.get("scenario")
                })
        except Exception as e:
            print(f"查询 {measurement} 失败: {e}")
        if result:
            break  # 新表已查到数据，不再查旧表（旧表数据已含在新表内，避免趋势点重复）

    # 按时间排序
    result.sort(key=lambda x: x.get("time", ""))
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


def _escape_tag(value: str) -> str:
    """Line Protocol tag 值转义：反斜杠、空格、逗号、等号必须转义"""
    return (value.replace("\\", "\\\\")
                 .replace(" ", "\\ ")
                 .replace(",", "\\,")
                 .replace("=", "\\="))


def _escape_field_string(value: str) -> str:
    """Line Protocol 字符串 field 转义：只需转义反斜杠和双引号

    注意：空格和逗号在双引号内是合法字符，**不能**转义，
    否则反斜杠会被当成内容存进库（历史 bug）。
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def create_reflection(scenario: str, note: str, daylist: str = None) -> Dict[str, Any]:
    """新增一条感悟"""
    import time
    ts = int(time.time())

    # 构建 Line Protocol
    tags = f"scenario={_escape_tag(scenario)}"
    if daylist:
        tags += f",daylist={_escape_tag(daylist)}"

    note_escaped = _escape_field_string(note)

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
    """查某个清单的所有行

    注意 range 用 -1y 而不是 -30d：清单的时间戳 = 清单执行日，
    30 天窗口会让老清单（如 Day1/Day2）在 30 天后从下拉里凭空消失。
    """
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1y)
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
    """查所有清单列表

    range 用 -1y（不是 -30d）：清单时间戳 = 执行日，30 天窗口会让
    Day1/Day2 这类老清单到期后从下拉里静默消失。
    """
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1y)
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
    # 按清单序号倒序（Day10 必须排在 Day9 之前；按字符串排会把 Day10 排到最后）
    def _day_num(item):
        m = re.search(r"(\d+)", item.get("daylist") or "")
        return int(m.group(1)) if m else -1

    result.sort(key=_day_num, reverse=True)
    return result


# ==================== aim_daylist_meta 查询 ====================

def get_daylist_meta(daylist: str) -> Dict[str, Any]:
    """查某个清单的元数据（range -1y，理由同 get_all_daylists）"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1y)
  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r.daylist == "{daylist}")
  |> keep(columns: ["_value", "_field", "daylist", "label"])
'''
    rows = db.query(flux)
    result = {"daylist": daylist}
    for row in rows:
        # label 是 tag（不是 _field），只出现在行上，必须单独取，
        # 否则 progress 的 label 永远是空字符串
        if row.get("label"):
            result["label"] = row.get("label")
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


def _get_scenarios_history_stats(scenarios: List[str], before_ts: int) -> Dict[str, Dict[str, Any]]:
    """取场景在 before_ts 之前的历史表现统计（首次基线 baseline、历史最高 PB、总场次）"""
    from datetime import datetime, timezone

    if not scenarios or not before_ts:
        return {}

    before_str = datetime.fromtimestamp(before_ts, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    clean_scns = [s.replace('"', '\\"') for s in scenarios if s]
    if not clean_scns:
        return {}

    filter_expr = ' or '.join([f'r.scenario == "{s}"' for s in clean_scns])
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1y, stop: {before_str})
  |> filter(fn: (r) => r._measurement == "{NEW_SCORE_MEASUREMENT}" and r._field == "score")
  |> filter(fn: (r) => {filter_expr})
  |> keep(columns: ["scenario", "_value", "_time"])
  |> sort(columns: ["_time"])
'''
    try:
        rows = db.query(flux)
    except Exception as e:
        print(f"查询历史统计失败: {e}")
        return {}

    res: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        scn = r.get("scenario")
        if not scn:
            continue
        try:
            val = float(r.get("_value") or 0)
        except (TypeError, ValueError):
            continue
        if scn not in res:
            res[scn] = {
                "baseline": round(val, 1),
                "best": round(val, 1),
                "count": 1
            }
        else:
            res[scn]["best"] = max(res[scn]["best"], round(val, 1))
            res[scn]["count"] += 1

    return res


def _get_window_scores(start_ts: int, end_ts: int) -> Tuple[Dict[str, Dict[str, Any]], Optional[Dict[str, Any]]]:
    """取时间窗内每个场景的最高分、命中率、轮次衰减统计，以及整体会话时段

    返回: (scores_map, session_dict)
      - scores_map: scenario -> {
          "score": float,
          "accuracy": float,
          "round_stats": {
              "n": int,
              "first": float,
              "last": float,
              "best": float,
              "drop_pct": float  # 负数代表末轮相比当日峰值衰减百分比，例如 -32.1
          }
        }
      - session_dict: {
          "start": "09:08",
          "end": "11:11",
          "duration_min": 123,
          "is_overtime": bool  # > 90 min 为 True，呼应 Q020 疲劳预警
        }
    """
    from datetime import datetime, timezone, timedelta

    if not start_ts or not end_ts:
        return {}, None

    start_str = datetime.fromtimestamp(start_ts, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = datetime.fromtimestamp(end_ts, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: {start_str}, stop: {end_str})
  |> filter(fn: (r) => r._measurement == "kovaak_score" and (r._field == "score" or r._field == "hits" or r._field == "misses"))
  |> keep(columns: ["_value", "_field", "scenario", "_time"])
'''
    acc: Dict[str, Dict[str, Any]] = {}
    all_timestamps = set()

    for row in db.query(flux):
        scn = row.get("scenario") or ""
        if not scn:
            continue
        field = row.get("_field")
        t = row.get("_time")
        try:
            val = float(row.get("_value") or 0)
        except (TypeError, ValueError):
            continue

        item = acc.setdefault(scn, {"scores": {}, "hits": 0.0, "misses": 0.0})
        if field == "score":
            if t:
                item["scores"][t] = val
                all_timestamps.add(t)
            else:
                idx = len(item["scores"])
                item["scores"][f"t_{idx}"] = val
        elif field == "hits":
            item["hits"] += val
        elif field == "misses":
            item["misses"] += val

    tz_bj = timezone(timedelta(hours=8))
    scores_res: Dict[str, Dict[str, Any]] = {}
    for scn, v in acc.items():
        total = v["hits"] + v["misses"]
        run_times = sorted(v["scores"].keys())
        n = len(run_times)
        if n > 0:
            first_score = v["scores"][run_times[0]]
            last_score = v["scores"][run_times[-1]]
            best_score = max(v["scores"].values())
            drop_pct = round((last_score - best_score) / best_score * 100, 1) if (best_score > 0 and n > 1) else 0.0
            round_stats = {
                "n": n,
                "first": round(first_score, 1),
                "last": round(last_score, 1),
                "best": round(best_score, 1),
                "drop_pct": drop_pct
            }
            score_val = round(best_score, 1)
        else:
            round_stats = None
            score_val = None

        scores_res[scn] = {
            "score": score_val,
            "accuracy": round(v["hits"] / total * 100, 1) if total else None,
            "round_stats": round_stats
        }

    session = None
    if all_timestamps:
        sorted_all = sorted(all_timestamps)
        try:
            t_start = datetime.fromisoformat(sorted_all[0].replace('Z', '+00:00')).astimezone(tz_bj)
            t_end = datetime.fromisoformat(sorted_all[-1].replace('Z', '+00:00')).astimezone(tz_bj)
            dur = int((t_end - t_start).total_seconds() / 60)
            session = {
                "start": t_start.strftime('%H:%M'),
                "end": t_end.strftime('%H:%M'),
                "duration_min": dur,
                "is_overtime": dur > 90
            }
        except Exception:
            session = None

    return scores_res, session


def _get_bench_map(list_name: str = "viscose-s2-easier") -> Dict[str, Dict[str, Any]]:
    """取基准表的下一档线映射：scenario -> {nextLine, pct, gapPct, rank, subRank, cat, sub, achIdx, targets}

    `targets` 是 9 档阶梯（Lemming→…→最高档）的分值数组，`achIdx` 是当前所处档位下标。
    前端「档位阶梯」直接用它画，不需要再单独请求 /api/bench/scenarios。
    """
    try:
        items = get_all_bench_scenarios(list_name)
    except Exception:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for it in items:
        out[it.get("scenario", "")] = {
            "nextLine": it.get("nextLine"),
            "pct": it.get("pct"),
            "gapPct": it.get("gapPct"),
            "rank": it.get("rank"),
            "subRank": it.get("subRank"),
            "cat": it.get("cat"),
            "sub": it.get("sub"),
            "achIdx": it.get("achIdx"),
            "targets": it.get("targets"),
        }
    return out


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

    # 5.5 批量取「当日成绩」、「轮次衰减」、「基准下一档线」与「历史基线/PB」
    today_scores, session_info = _get_window_scores(start_ts, end_ts)
    bench_map = _get_bench_map()
    scenario_list = [row.get("scenario", "") for row in rows if row.get("scenario")]
    history_map = _get_scenarios_history_stats(scenario_list, start_ts)

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

        sc_info = today_scores.get(scn) or {}
        today_score_dict = None
        if sc_info.get("score") is not None:
            today_score_dict = {
                "score": sc_info.get("score"),
                "accuracy": sc_info.get("accuracy")
            }

        result_rows.append({
            "order": row.get("order", 0),
            "scenario": scn,
            "role": row.get("role", ""),
            "required_rounds": required,
            "done_rounds": done,
            "status": status,
            "today_score": today_score_dict,
            "bench": bench_map.get(scn),
            "round_stats": sc_info.get("round_stats"),
            "history_stats": history_map.get(scn),
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
        "session": session_info,
        "items": meta.get("items", len(result_rows)),
        "rounds_total": meta.get("rounds_total", 0),
        "rows": result_rows
    }


def get_daylist_extras(parent_daylist: str) -> List[Dict[str, Any]]:
    """查某个主清单的所有加练清单（包含完整进度；range -1y 理由同上）"""
    flux = f'''
from(bucket: "{db.bucket}")
  |> range(start: -1y)
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
    """查加练清单中某个场景的轮数（只统计 created_at 之后的；新表 kovaak_score 优先，旧表仅作兜底，不相加）"""
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

    return _count_rounds_new_first(scenario_escaped, start_str, end_str, list_name)


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
