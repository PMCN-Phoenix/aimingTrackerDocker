# -*- coding: utf-8 -*-
"""
补录缺失的 stats 数据到 InfluxDB（幂等：按 scenario + 时间戳判重）

用法：
    python backfill_missing_stats.py            # dry-run，只报告
    python backfill_missing_stats.py --write    # 实际写入

list tag 规则（按日期）：
    2026-10-19 -> viscose-s2-easier（与当天已录的 42 条一致）
    2026-10-20 -> viscose-s2-easier（主课 patTS/psalmTS/voxTS/skyTS 系 + LG56 热身）
    2026-10-21 -> strafe-aiming-day9（重打 Day9 清单，与 10-14 同一套 14 场景）
"""
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
CST = timezone(timedelta(hours=8))

# 日期 -> list tag
DATE_LIST = {
    "2026-10-19": "viscose-s2-easier",
    "2026-10-20": "viscose-s2-easier",
    "2026-10-21": "strafe-aiming-day9",
}


def q(flux):
    req = urllib.request.Request("%s/api/v2/query?org=%s" % (INFLUX, ORG), data=flux.encode(), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def write(lines):
    data = "\n".join(lines).encode("utf-8")
    req = urllib.request.Request(
        "%s/api/v2/write?org=%s&bucket=%s&precision=ns" % (INFLUX, ORG, BUCKET),
        data=data, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def existing_ts(lo, hi):
    """返回该时间窗内 DB 已存在的 ns 时间戳集合（不区分 scenario/list）"""
    flux = ('from(bucket:"aim") |> range(start:%s, stop:%s) '
            '|> filter(fn:(r)=>r._measurement=="kovaak_score" and r._field=="score") '
            '|> keep(columns:["_time"])' % (lo, hi))
    txt = q(flux)
    # keep(_time) 后 _time 是每行最后一列；用正则整体抽取，避免多段 header 导致的列错位
    ts = set()
    for t in re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", txt):
        try:
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            ts.add(int(dt.timestamp() * 1e9))
        except Exception:
            pass
    return ts


def parse_ns(date_str, time_str):
    dt = datetime.fromisoformat("%sT%s+08:00" % (date_str, time_str.replace(".", ":")))
    return int(dt.timestamp() * 1e9)


def esc(s):
    return s.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,")


def main():
    do_write = "--write" in sys.argv
    lines = []
    report = []

    for date_str, list_name in DATE_LIST.items():
        dotted = date_str.replace("-", ".")
        lo = "%sT00:00:00+08:00" % date_str
        hi = "%sT23:59:59+08:00" % date_str
        have = existing_ts(lo, hi)
        files = [f for f in sorted(os.listdir(STATS))
                 if f.endswith(".csv") and ("- %s-" % dotted) in f]
        miss = []
        for f in files:
            m = re.match(r"^(.+?) - (?:Challenge|Freeplay) - (\d{4}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2}) Stats\.csv$", f)
            if not m:
                continue
            scenario, d, t = m.group(1), m.group(2).replace(".", "-"), m.group(3)
            ns = parse_ns(d, t)
            if ns in have:
                continue
            with open(os.path.join(STATS, f), encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            sm = re.search(r"Score:,([\d.]+)", content)
            if not sm:
                continue
            score = float(sm.group(1))
            fields = "score=%s" % score
            am = re.search(r"Accuracy:,([\d.]+)", content)
            if am:
                fields += ",accuracy=%s" % am.group(1)
            hm = re.search(r"Hit Count:,(\d+)", content)
            if hm:
                fields += ",hits=%s" % hm.group(1)
            mm = re.search(r"Miss Count:,(\d+)", content)
            if mm:
                fields += ",misses=%s" % mm.group(1)
            lines.append("kovaak_score,scenario=%s,list=%s %s %d" % (esc(scenario), list_name, fields, ns))
            miss.append((d, t, scenario, score))

        report.append((date_str, list_name, len(files), len(miss), miss))

    total_miss = sum(r[3] for r in report)
    print("=" * 62)
    print("%-12s %-20s %6s %6s" % ("日期", "list", "文件数", "缺失数"))
    print("-" * 62)
    for date_str, list_name, nf, nm, _ in report:
        print("%-12s %-20s %6d %6d" % (date_str, list_name, nf, nm))
    print("-" * 62)
    print("合计待写入: %d 条" % total_miss)

    for date_str, list_name, nf, nm, miss in report:
        if not miss:
            continue
        print("\n--- %s（%s）缺失明细 ---" % (date_str, list_name))
        for d, t, s, sc in miss:
            print("   %s  %-42s %s" % (t, s[:42], sc))

    if not do_write:
        print("\n[dry-run] 未写入。加 --write 实际写入。")
        return

    if not lines:
        print("\n无缺失，无需写入。")
        return

    st = write(lines)
    print("\n写入 HTTP %d，共 %d 条" % (st, len(lines)))

    # 复核
    for date_str in DATE_LIST:
        lo = "%sT00:00:00+08:00" % date_str
        hi = "%sT23:59:59+08:00" % date_str
        txt = q('from(bucket:"aim") |> range(start:%s, stop:%s) '
                '|> filter(fn:(r)=>r._measurement=="kovaak_score" and r._field=="score") '
                '|> group() |> count()' % (lo, hi))
        vals = [l.split(",")[-1] for l in txt.strip().split("\n")[1:] if l and not l.startswith(",")]
        print("  %s 现在共 %s 条" % (date_str, vals[0] if vals else "0"))


if __name__ == "__main__":
    main()
