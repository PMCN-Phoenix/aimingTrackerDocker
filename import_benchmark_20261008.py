"""
导入 2026-10-08 完整基准测试数据到 InfluxDB
同时写入 Whisphere Viscose Easier 感悟
"""
import urllib.request
import urllib.parse
import json
import os
import re
from datetime import datetime

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
STATS_DIR = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"

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
    data = "\n".join(lines).encode("utf-8")
    req = urllib.request.Request(
        "%s/api/v2/write?org=%s&bucket=%s&precision=ns" % (INFLUX, ORG, BUCKET),
        data=data, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status

def parse_stats_file(filepath):
    """解析单个 stats csv 文件，返回 (scenario, score, timestamp)"""
    filename = os.path.basename(filepath)
    # 从文件名提取场景名："Scenario Name - Challenge - 2026.10.08-16.24.33 Stats.csv"
    m = re.match(r"^(.+?) - Challenge - (\d{4}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2}) Stats\.csv$", filename)
    if not m:
        return None
    scenario = m.group(1)
    date_str = m.group(2).replace(".", "-")
    time_str = m.group(3).replace(".", ":")
    timestamp_str = "%sT%s+08:00" % (date_str, time_str)

    # 从文件末尾读取 Score
    score = None
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # 找 "Score:," 后面的数字
        score_match = re.search(r"Score:,([\d.]+)", content)
        if score_match:
            score = float(score_match.group(1))
    except Exception as e:
        print("  读取分数失败: %s" % e)

    return scenario, score, timestamp_str

def main():
    # 找出今天（2026-10-08）16:00 之后的所有 stats 文件
    today_files = []
    for f in os.listdir(STATS_DIR):
        if not f.endswith(".csv"):
            continue
        filepath = os.path.join(STATS_DIR, f)
        mtime = os.path.getmtime(filepath)
        mtime_dt = datetime.fromtimestamp(mtime)
        if mtime_dt.date() == datetime(2026, 10, 8).date() and mtime_dt.hour >= 16:
            today_files.append(filepath)

    today_files.sort(key=lambda x: os.path.getmtime(x))
    print("找到 %d 个今天的 stats 文件" % len(today_files))

    # 解析所有文件
    results = []
    for filepath in today_files:
        parsed = parse_stats_file(filepath)
        if parsed:
            scenario, score, timestamp = parsed
            if score is not None:
                results.append((scenario, score, timestamp))
                print("  %s: %.2f (%s)" % (scenario, score, timestamp))
            else:
                print("  %s: 无分数" % scenario)

    print("\n共解析到 %d 条有效数据" % len(results))

    # 写入 InfluxDB
    lines = []
    for scenario, score, timestamp in results:
        # 转换时间戳为纳秒
        dt = datetime.fromisoformat(timestamp)
        ns = int(dt.timestamp() * 1e9)
        # 转义场景名中的空格和特殊字符
        scenario_escaped = scenario.replace(" ", "\\ ").replace(",", "\\,")
        line = "kovaak_score,scenario=%s score=%f %d" % (scenario_escaped, score, ns)
        lines.append(line)

    if lines:
        status = write_influx(lines)
        print("\n写入 InfluxDB 状态: %s" % status)
    else:
        print("\n没有数据可写入")

    # 写入 Whisphere Viscose Easier 感悟
    reflection_text = "眼睛的某个方位的肌肉收紧手向哪个方向收紧"
    reflection_scenario = "Whisphere Viscose Easier"
    reflection_date = "2026-10-08"

    # 检查是否已存在相同感悟
    check_flux = '''from(bucket: "aim")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "aim_reflection")
  |> filter(fn: (r) => r.scenario == "%s")
  |> filter(fn: (r) => r._value == "%s")
  |> keep(columns: ["_time", "_value"])''' % (reflection_scenario, reflection_text)

    check_result = query_influx(check_flux)
    if reflection_text in check_result:
        print("\n感悟已存在，跳过写入")
    else:
        # 写入感悟
        now_ns = int(datetime.now().timestamp() * 1e9)
        reflection_lines = [
            'aim_reflection,scenario=%s,date=%s,type=reflection reflection="%s" %d' % (
                reflection_scenario.replace(" ", "\\ "), reflection_date,
                reflection_text.replace('"', '\\"'), now_ns)
        ]
        status = write_influx(reflection_lines)
        print("\n写入 Whisphere 感悟状态: %s" % status)
        print("  场景: %s" % reflection_scenario)
        print("  感悟: %s" % reflection_text)
        print("  日期: %s" % reflection_date)

    print("\n=== 完成 ===")

if __name__ == "__main__":
    main()
