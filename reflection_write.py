#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日感悟写入器（aim_reflection）
==================================
将用户在对话中提供的场景感悟写入 InfluxDB，供 D 看板 800 面板弹窗展示。

数据模型：
  measurement: aim_reflection
  tags:        scenario（场景名）, daylist（清单日，可选）
  field:       note（string，感悟文本）
  time:        感悟对应的日期（当天 00:00 +08:00）

唯一性：scenario + daylist + date 唯一，同天同场景覆盖写入（InfluxDB 同 tag+field+time 自动覆盖）。

用法:
  python reflection_write.py --scenario "1w2ts reload smallflicks larger" --note "今天手感不错"
  python reflection_write.py --scenario "场景名" --note "感悟" --date 2026-09-18 --daylist Day1
  python reflection_write.py --scenario "场景名" --note "感悟" --check   # 只校验不写入
"""
import sys
import os
import json
import argparse
import urllib.request
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
INFLUX = "http://127.0.0.1:8087"
ORG, BUCKET = "aim-org", "aim"
TOKEN = "aim-super-secret-token-2026"
TZ_CN = datetime.timezone(datetime.timedelta(hours=8))
DAYLIST_DATES = os.path.join(BASE, "daylist_dates.json")


def esc_tag(s):
    """转义 tag 值中的特殊字符（空格、逗号、等号）"""
    return str(s).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def esc_field_string(s):
    """转义 field string 值中的双引号和反斜杠"""
    return str(s).replace("\\", "\\\\").replace('"', '\\"')


def infer_daylist(date_str):
    """从 daylist_dates.json 推断日期对应的清单日"""
    try:
        with open(DAYLIST_DATES, encoding="utf-8") as f:
            data = json.load(f)
        # 格式可能是 {"dates": {"2026-09-18": "Day1", ...}} 或直接 {"2026-09-18": "Day1"}
        if isinstance(data, dict) and "dates" in data:
            return data["dates"].get(date_str)
        if isinstance(data, dict):
            return data.get(date_str)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def check_scenario_exists(scenario):
    """校验场景名是否存在于 aim_scenario 中，返回 (exists, 建议)"""
    flux = (
        'from(bucket: "aim") |> range(start: -30d, stop: 2d)\n'
        '  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "%s")\n'
        '  |> keep(columns: ["scenario"]) |> limit(n: 1)' % scenario.replace('"', '\\"')
    )
    req = urllib.request.Request(
        "%s/api/v2/query?org=%s" % (INFLUX, ORG),
        data=flux.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8")
        # 有数据行说明存在
        for line in body.splitlines():
            if line and not line.startswith("#") and "," in line:
                cells = line.split(",")
                if len(cells) > 2 and cells[2] != "_time" and cells[2] != "":
                    return True, None
        return False, "aim_scenario 中未找到该场景（可能是新场景或拼写错误）"
    except Exception as e:
        return None, "校验查询失败: %s" % e


def write_reflection(scenario, note, date_str, daylist=None, dry_run=False):
    """写入一条感悟到 InfluxDB"""
    # 计算时间戳：当天 00:00 +08:00
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=TZ_CN)
    except ValueError:
        print("错误：日期格式应为 YYYY-MM-DD，实际: %s" % date_str)
        return False
    timestamp = int(dt.timestamp())

    # 构造 Line Protocol
    # tag 值需要转义空格
    tags = "scenario=%s" % esc_tag(scenario)
    if daylist:
        tags += ",daylist=%s" % esc_tag(daylist)
    # field string 值用双引号包裹，内部双引号转义
    fields = 'note="%s"' % esc_field_string(note)
    line = "aim_reflection,%s %s %d" % (tags, fields, timestamp)

    print("=== 写入内容 ===")
    print("  scenario : %s" % scenario)
    print("  daylist  : %s" % (daylist or "（未指定）"))
    print("  date     : %s" % date_str)
    print("  timestamp: %d" % timestamp)
    print("  note     : %s" % (note[:80] + ("..." if len(note) > 80 else "")))
    print("  Line Proto: %s" % line)

    if dry_run:
        print("  [dry-run] 未实际写入")
        return True

    req = urllib.request.Request(
        "%s/api/v2/write?org=%s&bucket=%s&precision=s" % (INFLUX, ORG, BUCKET),
        data=line.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status == 204:
                print("✅ 写入成功（HTTP 204）")
                return True
            else:
                print("❌ 写入失败（HTTP %s）" % r.status)
                return False
    except urllib.error.HTTPError as e:
        print("❌ 写入失败（HTTP %s）: %s" % (e.code, e.read().decode("utf-8", errors="replace")))
        return False
    except Exception as e:
        print("❌ 写入异常: %s" % e)
        return False


def main():
    parser = argparse.ArgumentParser(description="每日感悟写入器（aim_reflection）")
    parser.add_argument("--scenario", required=True, help="场景名（与 aim_scenario 完全一致）")
    parser.add_argument("--note", required=True, help="感悟文本内容")
    parser.add_argument("--date", default=None, help="感悟对应的日期（YYYY-MM-DD），默认当天")
    parser.add_argument("--daylist", default=None, help="所属清单日（如 Day1），默认自动推断")
    parser.add_argument("--check", action="store_true", help="只校验场景名，不写入")
    parser.add_argument("--dry-run", action="store_true", help="显示写入内容但不实际写入")
    args = parser.parse_args()

    # 日期
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.datetime.now(TZ_CN).strftime("%Y-%m-%d")

    # 清单日
    daylist = args.daylist
    if not daylist:
        daylist = infer_daylist(date_str)
        if daylist:
            print("（自动推断 daylist=%s，来自 daylist_dates.json）" % daylist)

    # 校验场景名
    exists, hint = check_scenario_exists(args.scenario)
    if exists is False:
        print("⚠️  警告：%s" % hint)
        print("   仍将继续写入（可能是新场景首次有感悟）")
    elif exists is None:
        print("⚠️  场景名校验跳过：%s" % hint)

    if args.check:
        print("\n=== 校验模式，未写入 ===")
        return

    # 写入
    ok = write_reflection(args.scenario, args.note, date_str, daylist, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
