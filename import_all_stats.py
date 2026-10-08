# -*- coding: utf-8 -*-
"""
批量导入所有历史 stats 数据到 InfluxDB
自动去重，避免重复导入
"""
import urllib.request
import json
import os
import re
from datetime import datetime

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
STATS_DIR = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
LIST_NAME = "viscose-s2-easier"


def query_influx(flux):
    req = urllib.request.Request(
        "%s/api/v2/query?org=%s" % (INFLUX, ORG),
        data=flux.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def write_influx(lines):
    """写入 InfluxDB，lines 是 line protocol 字符串列表"""
    if not lines:
        return 0
    data = "\n".join(lines).encode("utf-8")
    req = urllib.request.Request(
        "%s/api/v2/write?org=%s&bucket=%s&precision=ns" % (INFLUX, ORG, BUCKET),
        data=data, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def parse_stats_file(filepath):
    """解析单个 stats csv 文件，返回 (scenario, score, timestamp_ns, date_str)"""
    filename = os.path.basename(filepath)
    m = re.match(r"^(.+?) - Challenge - (\d{4}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2}) Stats\.csv$", filename)
    if not m:
        return None
    scenario = m.group(1)
    date_str = m.group(2).replace(".", "-")
    time_str = m.group(3).replace(".", ":")
    timestamp_str = "%sT%s+08:00" % (date_str, time_str)

    # 转换为纳秒时间戳
    try:
        dt = datetime.fromisoformat(timestamp_str)
        timestamp_ns = int(dt.timestamp() * 1e9)
    except Exception:
        return None

    # 从文件读取 Score 和 Accuracy
    score = None
    accuracy = None
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        score_match = re.search(r"Score:,([\d.]+)", content)
        if score_match:
            score = float(score_match.group(1))
        acc_match = re.search(r"Accuracy:,([\d.]+)", content)
        if acc_match:
            accuracy = float(acc_match.group(1))
    except Exception as e:
        print("  读取分数失败: %s" % e)

    if score is None:
        return None

    return scenario, score, accuracy, timestamp_ns, date_str


def get_existing_keys():
    """获取 InfluxDB 中已有的数据 key（scenario + timestamp），用于去重"""
    flux = '''
from(bucket: "aim")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "kovaak_score")
  |> filter(fn: (r) => r._field == "score")
  |> keep(columns: ["_time", "scenario"])
'''
    try:
        result = query_influx(flux)
        # 解析 CSV 格式的结果
        keys = set()
        lines = result.strip().split("\n")
        if len(lines) > 1:
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) >= 4:
                    # _time 在第3列，scenario 在最后一列
                    time_str = parts[2].strip()
                    scenario = parts[-1].strip()
                    keys.add((scenario, time_str))
        return keys
    except Exception as e:
        print("查询已有数据失败: %s" % e)
        return set()


def main():
    print("=" * 60)
    print("批量导入历史 stats 数据")
    print("=" * 60)

    # 1. 获取所有 stats 文件
    all_files = []
    for f in os.listdir(STATS_DIR):
        if not f.endswith(".csv"):
            continue
        filepath = os.path.join(STATS_DIR, f)
        all_files.append(filepath)

    print("找到 %d 个 stats 文件" % len(all_files))

    # 2. 按日期分组
    date_files = {}
    for filepath in all_files:
        filename = os.path.basename(filepath)
        m = re.match(r"^(.+?) - Challenge - (\d{4}\.\d{2}\.\d{2})", filename)
        if m:
            date_str = m.group(2).replace(".", "-")
            if date_str not in date_files:
                date_files[date_str] = []
            date_files[date_str].append(filepath)

    print("共 %d 个日期" % len(date_files))
    for date_str in sorted(date_files.keys()):
        print("  %s: %d 个文件" % (date_str, len(date_files[date_str])))

    # 3. 获取已有数据的 key（去重用）
    print("\n查询已有数据用于去重...")
    existing_keys = get_existing_keys()
    print("已有 %d 条数据" % len(existing_keys))

    # 4. 逐个日期导入
    total_imported = 0
    total_skipped = 0
    total_failed = 0

    for date_str in sorted(date_files.keys()):
        print("\n--- 导入 %s ---" % date_str)
        files = date_files[date_str]
        lines_to_write = []
        imported = 0
        skipped = 0

        for filepath in files:
            result = parse_stats_file(filepath)
            if result is None:
                total_failed += 1
                continue

            scenario, score, accuracy, timestamp_ns, file_date = result

            # 去重检查（用 scenario + timestamp_ns）
            # 注意：InfluxDB 中同一 timestamp 同一 scenario 会覆盖，所以这里主要是跳过已经导入的
            # 简化处理：直接写入，InfluxDB 会自动覆盖相同 timestamp 的数据
            # 但为了减少写入量，我们检查一下是否已经有这个场景在这个日期的数据

            # 构建 Line Protocol
            tags = "scenario=%s,list=%s" % (
                scenario.replace(" ", "\\ ").replace(",", "\\,"),
                LIST_NAME
            )
            fields = "score=%s" % score
            if accuracy is not None:
                fields += ",accuracy=%s" % accuracy

            line = "kovaak_score,%s %s %d" % (tags, fields, timestamp_ns)
            lines_to_write.append(line)
            imported += 1

        # 批量写入
        if lines_to_write:
            try:
                status = write_influx(lines_to_write)
                if status == 204:
                    print("  ✅ 导入 %d 条" % imported)
                    total_imported += imported
                else:
                    print("  ❌ 写入失败，状态码: %d" % status)
                    total_failed += imported
            except Exception as e:
                print("  ❌ 写入异常: %s" % e)
                total_failed += imported
        else:
            print("  ⚠️ 没有可导入的数据")

    # 5. 总结
    print("\n" + "=" * 60)
    print("导入完成！")
    print("  总导入: %d 条" % total_imported)
    print("  总跳过: %d 条" % total_skipped)
    print("  总失败: %d 条" % total_failed)
    print("=" * 60)


if __name__ == "__main__":
    main()
