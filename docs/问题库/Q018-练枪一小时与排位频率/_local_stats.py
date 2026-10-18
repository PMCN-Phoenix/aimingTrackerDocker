# -*- coding: utf-8 -*-
"""Q018 本地数据：训练频率 / 间隔 / 单日相对水平 的关系。"""
import os, json, csv, io, requests
from collections import defaultdict
from datetime import datetime, timedelta
import statistics as st

os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
URL = "http://127.0.0.1:8087/api/v2/query?org=aim-org"
H = {"Authorization": "Token aim-super-secret-token-2026",
     "Accept": "application/csv", "Content-Type": "application/vnd.flux"}

Q = ('from(bucket:"aim") |> range(start:-2y) '
     '|> filter(fn:(r)=> r._measurement == "kovaak_score") '
     '|> filter(fn:(r)=> r._field == "score") '
     '|> sort(columns:["_time"])')

r = requests.post(URL, headers=H, data=Q.encode(), timeout=90)
rows = list(csv.DictReader(io.StringIO(r.text)))
print("原始行", len(rows))

# (date, scenario) -> [scores]
day_sc = defaultdict(list)
for x in rows:
    sc = (x.get("scenario") or "").strip()
    if not sc:
        continue
    try:
        v = float(x["_value"])
    except Exception:
        continue
    d = x["_time"][:10]
    day_sc[(d, sc)].append(v)

# 每个场景的均值/标准差（用于 z）
per_sc = defaultdict(list)
for (d, sc), vs in day_sc.items():
    per_sc[sc].append(st.mean(vs))
mu = {sc: st.mean(v) for sc, v in per_sc.items() if len(v) >= 5}
sd = {sc: (st.pstdev(v) or 1.0) for sc, v in per_sc.items() if len(v) >= 5}
print("可用场景数", len(mu))

# 每日：只取有 >=3 个已知场景的日子，算 z 均值
day_z = {}
day_rounds = defaultdict(int)
for (d, sc), vs in day_sc.items():
    day_rounds[d] += len(vs)
for d in sorted({k[0] for k in day_sc}):
    zs = []
    for (dd, sc), vs in day_sc.items():
        if dd != d or sc not in mu:
            continue
        zs.append((st.mean(vs) - mu[sc]) / sd[sc])
    if len(zs) >= 3:
        day_z[d] = st.mean(zs)

days = sorted(day_z)
print("训练日数", len(days), "区间", days[0], "→", days[-1])

# 周统计
week = defaultdict(list)
for d in days:
    dt = datetime.strptime(d, "%Y-%m-%d")
    wk = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
    week[wk].append(d)
print("\n## 每周训练天数（最近 12 周）")
for wk in sorted(week)[-12:]:
    print("  %s  天数 %d  轮数 %4d  z均值 %+.2f" % (
        wk, len(week[wk]), sum(day_rounds[d] for d in week[wk]),
        st.mean(day_z[d] for d in week[wk])))

# 间隔 vs 当日水平
print("\n## 间隔（距上次训练天数）→ 当日 z 均值")
buckets = defaultdict(list)
for i, d in enumerate(days):
    if i == 0:
        continue
    gap = (datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(days[i - 1], "%Y-%m-%d")).days
    if gap == 1:
        k = "1天(连练)"
    elif gap == 2:
        k = "2天"
    elif gap == 3:
        k = "3天"
    elif gap <= 7:
        k = "4-7天"
    else:
        k = "8天+"
    buckets[k].append(day_z[d])
for k in ["1天(连练)", "2天", "3天", "4-7天", "8天+"]:
    v = buckets.get(k, [])
    if v:
        print("  %-9s n=%3d  z均值 %+.3f  中位 %+.3f" % (k, len(v), st.mean(v), st.median(v)))

# 连续训练天数（streak）vs 当日水平
print("\n## 连续训练第 N 天 → 当日 z 均值")
streak = {}
cur, prev = 0, None
for d in days:
    dt = datetime.strptime(d, "%Y-%m-%d")
    if prev and (dt - prev).days == 1:
        cur += 1
    else:
        cur = 1
    streak[d] = cur
    prev = dt
sb = defaultdict(list)
for d in days:
    n = streak[d]
    k = "1" if n == 1 else ("2" if n == 2 else ("3" if n == 3 else "4+"))
    sb[k].append(day_z[d])
for k in ["1", "2", "3", "4+"]:
    v = sb.get(k, [])
    if v:
        print("  第 %-2s 天  n=%3d  z均值 %+.3f" % (k, len(v), st.mean(v)))

# 单日轮数 vs 当日水平
print("\n## 单日轮数 → 当日 z 均值")
rb = defaultdict(list)
for d in days:
    n = day_rounds[d]
    k = "<=10" if n <= 10 else ("11-20" if n <= 20 else ("21-35" if n <= 35 else "36+"))
    rb[k].append(day_z[d])
for k in ["<=10", "11-20", "21-35", "36+"]:
    v = rb.get(k, [])
    if v:
        print("  %-6s n=%3d  z均值 %+.3f" % (k, len(v), st.mean(v)))

json.dump({"days": days, "day_z": day_z, "day_rounds": dict(day_rounds),
           "week": {k: len(v) for k, v in week.items()},
           "streak": streak},
          open("本地数据分析.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已写 本地数据分析.json")
