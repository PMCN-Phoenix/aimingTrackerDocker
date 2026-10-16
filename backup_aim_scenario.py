#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aim_scenario 旧表全量备份脚本（2026-10-16 成绩表迁移 · 决策①）
==============================================================
背景：权威成绩表已迁移到 kovaak_score（新表，含 hits/misses），
旧表 aim_scenario 的 740 个成绩点经实测已 100% 并入新表
（见 docs/接手报告-20261016.md）。

本脚本把 aim_scenario 全量数据导出为 InfluxDB 原生 annotated CSV，
落到 backup/ 目录，作为「观察 2-4 周后删除旧表」动作的安全网。
导出内容不做任何转换，最大程度保留原始信息。

用法（需在宿主机执行，能访问 InfluxDB）:
    python backup_aim_scenario.py            # 导出到 backup/aim_scenario_backup_<时间戳>.csv
    python backup_aim_scenario.py --dry-run  # 只统计不落盘

安全设计:
    - 查询范围 1970-01-01 ~ 2030-01-01，覆盖全部历史
    - 导出后自检：文件非空、含 annotated CSV 头、数据行数 > 0
    - 自检失败则删除刚写的文件并以非零退出，避免留下假备份
"""
import csv
import io
import json
import os
import sys
import urllib.request
import urllib.error
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE, "backup")

INFLUX = "http://127.0.0.1:8087"
ORG, BUCKET = "aim-org", "aim"
TOKEN = "aim-super-secret-token-2026"
MEASUREMENT = "aim_scenario"

FLUX = (
    'from(bucket: "%s") '
    "|> range(start: 1970-01-01T00:00:00Z, stop: 2030-01-01T00:00:00Z) "
    '|> filter(fn: (r) => r._measurement == "%s") '
    '|> yield(name: "csv")'
) % (BUCKET, MEASUREMENT)


def fetch_annotated_csv(flux: str = FLUX) -> str:
    """执行 Flux 查询，返回 InfluxDB 原生 annotated CSV 文本"""
    url = "%s/api/v2/query?org=%s" % (INFLUX, ORG)
    req = urllib.request.Request(url, data=flux.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    req.add_header("Accept", "application/csv")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", "replace")


def summarize_annotated_csv(text: str) -> dict:
    """解析 annotated CSV，返回统计信息（纯函数，可离线单测）

    返回 {"rows": 数据行数, "scenarios": 去重场景数, "fields": 去重字段集合,
          "min_time": 最早时间, "max_time": 最晚时间, "has_header": 是否有表头}
    """
    lines = [ln for ln in text.replace("\r", "").split("\n") if ln]
    header_idx = -1
    for i, ln in enumerate(lines):
        if ln.startswith(",result,"):
            header_idx = i
            break
    if header_idx == -1:
        return {"rows": 0, "scenarios": 0, "fields": set(),
                "min_time": None, "max_time": None, "has_header": False}

    reader = csv.DictReader(io.StringIO("\n".join(lines[header_idx:])))
    rows = 0
    scenarios, fields = set(), set()
    times = []
    for row in reader:
        value = row.get("_value")
        if not value and not row.get("_time"):
            continue  # 跳过结果元数据行
        rows += 1
        if row.get("scenario"):
            scenarios.add(row["scenario"])
        if row.get("_field"):
            fields.add(row["_field"])
        if row.get("_time"):
            times.append(row["_time"])
    return {
        "rows": rows,
        "scenarios": len(scenarios),
        "fields": fields,
        "min_time": min(times) if times else None,
        "max_time": max(times) if times else None,
        "has_header": True,
    }


def main():
    dry_run = "--dry-run" in sys.argv
    print("查询 aim_scenario 全量数据（%s）..." % INFLUX)
    try:
        text = fetch_annotated_csv()
    except urllib.error.URLError as e:
        print("✗ 连不上 InfluxDB（%s）：%s" % (INFLUX, e))
        print("  请在宿主机执行（Docker 容器 aim-influxdb 需在运行）")
        sys.exit(2)
    except Exception as e:
        print("✗ 查询失败: %s" % e)
        sys.exit(2)

    stats = summarize_annotated_csv(text)
    print("统计: %d 个数据点 / %d 个场景 / 字段 %s / 时间范围 %s ~ %s"
          % (stats["rows"], stats["scenarios"], sorted(stats["fields"]),
             stats["min_time"], stats["max_time"]))

    if stats["rows"] == 0:
        print("✗ 旧表无数据或查询异常——若旧表已删除则无需备份，否则请检查")
        sys.exit(3)

    if dry_run:
        print("（--dry-run，未写文件）")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BACKUP_DIR, "aim_scenario_backup_%s.csv" % stamp)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    # 自检：文件非空 + 含表头 + 行数吻合
    size = os.path.getsize(path)
    with open(path, encoding="utf-8") as f:
        head = f.readline()
    if size == 0 or ",result," not in head:
        os.remove(path)
        print("✗ 自检失败（文件为空或缺少 annotated CSV 头），已删除 %s" % path)
        sys.exit(4)

    print("✅ 备份完成: %s（%.1f KB，%d 个数据点）"
          % (path, size / 1024.0, stats["rows"]))
    print("   后续：观察 2-4 周确认新表无遗漏后，可按 docs/接手报告-20261016.md 决策①删除旧表")


if __name__ == "__main__":
    main()
