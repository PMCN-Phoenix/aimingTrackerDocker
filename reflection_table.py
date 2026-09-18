#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练枪感悟表格 · 成绩变动计算器
读 InfluxDB(aim bucket) 的 aim_scenario,按"本地日期(Asia/Shanghai)"分组,
计算 12 个场景的今日得分/命中率、得分环比、vs30天均值、vs历史最佳、命中环比。
输出 Markdown 表格(感悟列留空,由助手在对话中回填)。

用法:
  python reflection_table.py 2026-09-01 [--json]
"""
import sys
import json
import urllib.request
from datetime import datetime, timedelta, timezone

INFLUX_URL = "http://127.0.0.1:8087/api/v2/query"
ORG = "aim-org"
TOKEN = "aim-super-secret-token-2026"
BUCKET = "aim"
TZ_CN = timezone(timedelta(hours=8))

# 12 个跟踪场景(表格行序)
SCENARIOS = [
    "Centering 90 Easy+ No Strafes",
    "Air Voltaic Close Long Strafes Very Easy",
    "GP Far Long Strafes Easy",
    "GP Close Long Strafes Easy",
    "B90TI Iron",
    "Smoothbot Iron",
    "Pasu Voltaic Iron",
    "Tamspeed 2bp Iron",
    "Wide Wall 3 Targets TE",
    "1w2t TE Reload",
    "B90T Voltaic Easy Very Slow",
    "patTS Voltaic Iron",
]


def query_flux(flux: str) -> str:
    body = flux.encode("utf-8")
    req = urllib.request.Request(INFLUX_URL + "?org=" + ORG, data=body, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    req.add_header("Accept", "application/csv")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def parse_annotated_csv(text: str):
    """返回 (header, rows),跳过 # 注释行。"""
    header = None
    rows = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        if header is None:
            header = line.split(",")
            continue
        rows.append(line.split(","))
    return header, rows


def local_date(iso: str) -> str:
    """UTC ISO8601 -> 北京时间 YYYY-MM-DD。"""
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    dt = datetime.fromisoformat(iso)
    return dt.astimezone(TZ_CN).strftime("%Y-%m-%d")


def mean(vals):
    if not vals:
        return None
    return sum(vals) / len(vals)


def fmt(v, nd=1):
    if v is None:
        return "—"
    return f"{v:.{nd}f}"


def fmt_diff(v, nd=1):
    """差值 -> ↑/↓ 前缀。"""
    if v is None:
        return "—"
    if abs(v) < 1e-9:
        return "0"
    arrow = "↑" if v > 0 else "↓"
    return f"{arrow}{abs(v):.{nd}f}"


def fmt_best(today, best):
    """距历史最佳。破纪录返回 NEW,否则返回 差X。"""
    if best is None:
        return "—"
    if today is not None and today > best:
        return "NEW"
    return f"差{fmt(best - today if today is not None else None)}"


def build_table(date_str: str):
    flux = (
        f'from(bucket: "{BUCKET}") '
        f'|> range(start: -180d) '
        f'|> filter(fn: (r) => r._measurement == "aim_scenario") '
        f'|> keep(columns: ["_time", "_field", "_value", "scenario"])'
    )
    text = query_flux(flux)
    header, rows = parse_annotated_csv(text)
    idx = {name: i for i, name in enumerate(header)}
    for need in ("scenario", "_field", "_value", "_time"):
        if need not in idx:
            raise RuntimeError(f"Flux 返回缺列: {need}")

    # data[scenario] = [(本地日期, field, value), ...]
    data = {}
    for r in rows:
        if len(r) <= max(idx.values()):
            continue
        sc = r[idx["scenario"]]
        f = r[idx["_field"]]
        try:
            v = float(r[idx["_value"]])
        except ValueError:
            continue
        d = local_date(r[idx["_time"]])
        data.setdefault(sc, []).append((d, f, v))

    target = date_str
    t_dt = datetime.strptime(target, "%Y-%m-%d").replace(tzinfo=TZ_CN)
    cutoff30 = (t_dt - timedelta(days=30)).strftime("%Y-%m-%d")

    result_rows = []
    for sc in SCENARIOS:
        recs = data.get(sc, [])
        by_date = {}
        for d, f, v in recs:
            by_date.setdefault(d, {}).setdefault(f, []).append(v)

        today_score = mean(by_date.get(target, {}).get("score", []))
        today_acc = mean(by_date.get(target, {}).get("accuracy", []))

        prev_dates = sorted(d for d in by_date if d < target)
        prev = prev_dates[-1] if prev_dates else None
        prev_score = mean(by_date.get(prev, {}).get("score", [])) if prev else None
        prev_acc = mean(by_date.get(prev, {}).get("accuracy", [])) if prev else None

        hist30 = [v for d, f, v in recs if cutoff30 <= d < target and f == "score"]
        avg30 = mean(hist30) if hist30 else None

        hist_best = max((v for d, f, v in recs if d < target and f == "score"), default=None)

        d_score_prev = (today_score - prev_score) if (today_score is not None and prev_score is not None) else None
        d_score_30 = (today_score - avg30) if (today_score is not None and avg30 is not None) else None
        d_acc_prev = (today_acc - prev_acc) if (today_acc is not None and prev_acc is not None) else None

        result_rows.append({
            "scenario": sc,
            "today_score": today_score,
            "d_score_prev": d_score_prev,
            "prev_date": prev,
            "d_score_30": d_score_30,
            "best": hist_best,
            "today_acc": today_acc,
            "d_acc_prev": d_acc_prev,
        })

    return result_rows


def render_markdown(rows):
    lines = []
    lines.append("| 场景 | 感悟 | 得分(今日) | 得分环比 | vs30天 | vs最佳 | 命中率 | 命中环比 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        sc = r["scenario"]
        ts = fmt(r["today_score"])
        dp = fmt_diff(r["d_score_prev"])
        d30 = fmt_diff(r["d_score_30"])
        best = fmt_best(r["today_score"], r["best"])
        ta = (f"{r['today_acc']:.1f}%" if r["today_acc"] is not None else "—")
        da = fmt_diff(r["d_acc_prev"])
        lines.append(f"| {sc} |  | {ts} | {dp} | {d30} | {best} | {ta} | {da} |")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python reflection_table.py YYYY-MM-DD [--json]")
        sys.exit(1)
    date_str = sys.argv[1]
    rows = build_table(date_str)
    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(rows))
