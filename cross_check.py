#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交叉检验：InfluxDB 数据一致性"""
import urllib.request

URL = "http://127.0.0.1:8087/api/v2/query?org=aim-org"
TOKEN = "aim-super-secret-token-2026"

def query(flux):
    req = urllib.request.Request(URL, data=flux.encode(), headers={
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/vnd.flux",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def count_rows(csv_text):
    """统计 annotated CSV 中的数据行数（跳过注释和表头）"""
    lines = csv_text.strip().splitlines()
    data_lines = [l for l in lines if l and not l.startswith("#") and not l.startswith(",result,table")]
    return len(data_lines)

def get_value(csv_text, col="_value"):
    """从单行 CSV 中提取某列的值"""
    lines = csv_text.strip().splitlines()
    header = None
    for l in lines:
        if l.startswith(",result,table"):
            header = l.split(",")
            continue
        if l and not l.startswith("#") and header:
            vals = l.split(",")
            if col in header:
                idx = header.index(col)
                if idx < len(vals):
                    return vals[idx]
    return None

print("=== 1. aim_bench_row rowJson 行数（应=39）===")
q1 = 'from(bucket: "aim") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "aim_bench_row" and r._field == "rowJson")'
r1 = query(q1)
n1 = count_rows(r1)
print(f"  aim_bench_row rowJson: {n1} 行 {'✅' if n1 == 39 else '❌'}")

print("\n=== 2. aim_bench_row nextLine 行数（应=39）===")
q2 = 'from(bucket: "aim") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "aim_bench_row" and r._field == "nextLine")'
r2 = query(q2)
n2 = count_rows(r2)
print(f"  aim_bench_row nextLine: {n2} 行 {'✅' if n2 == 39 else '❌'}")

print("\n=== 3. aim_daylist Day1 行数（应=7）===")
q3 = 'from(bucket: "aim") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "aim_daylist" and r.daylist == "Day1" and r._field == "order")'
r3 = query(q3)
n3 = count_rows(r3)
print(f"  aim_daylist Day1: {n3} 行 {'✅' if n3 == 7 else '❌'}")

print("\n=== 4. aim_scenario list=viscose-s2-easier 场景数（应=39）===")
q4 = 'from(bucket: "aim") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "aim_scenario" and r.list == "viscose-s2-easier" and r._field == "score") |> group(columns: ["scenario"]) |> count() |> group()'
r4 = query(q4)
n4 = count_rows(r4)
print(f"  aim_scenario S2 场景数: {n4} {'✅' if n4 == 39 else '❌'}")

print("\n=== 5. aimlab_task 数据行数（应>0）===")
q5 = 'from(bucket: "aim") |> range(start: -1000d) |> filter(fn: (r) => r._measurement == "aimlab_task") |> group() |> count()'
r5 = query(q5)
v5 = get_value(r5)
print(f"  aimlab_task 总行数: {v5} {'✅' if v5 and int(v5) > 0 else '❌'}")

print("\n=== 6. aim_bench_meta 汇总（ranked/avgGap/stuckText）===")
q6 = 'from(bucket: "aim") |> range(start: -1y) |> filter(fn: (r) => r._measurement == "aim_bench_meta")'
r6 = query(q6)
lines = [l for l in r6.strip().split("\n") if l and not l.startswith("#") and not l.startswith(",result,table")]
for l in lines:
    parts = l.split(",")
    if len(parts) >= 7:
        field = parts[5] if len(parts) > 5 else "?"
        value = parts[6] if len(parts) > 6 else "?"
        print(f"  {field} = {value}")

print("\n=== 交叉检验完成 ===")
