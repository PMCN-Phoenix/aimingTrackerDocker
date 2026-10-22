# -*- coding: utf-8 -*-
"""Q024 补充分析：
A) 修正版方差分解 —— 各天均值本身含抽样误差，between 必须扣掉 within/n
B) 热身曲线 —— 同一天同场景内，第 k 轮相对当天最好成绩的比值（k=1..6）
"""
import os, re, json, statistics
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
FN = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")


def score_of(path):
    for l in open(path, encoding="utf-8", errors="ignore"):
        p = l.split(",")
        if len(p) > 1 and p[0].strip() == "Score:":
            try:
                return float(p[1])
            except Exception:
                return None
    return None


sessions = defaultdict(lambda: defaultdict(list))
for fn in os.listdir(STATS):
    m = FN.match(fn)
    if not m:
        continue
    sc = score_of(os.path.join(STATS, fn))
    if sc is None:
        continue
    sessions["%s-%s-%s" % (m.group(2), m.group(3), m.group(4))][m.group(1).strip()].append(
        ("%s:%s:%s" % (m.group(5), m.group(6), m.group(7)), sc))

# ---------- A) 修正方差分解 ----------
print("=" * 96)
print("【A】修正方差分解（between 已扣除抽样误差 within/n）")
print("=" * 96)
rows = []
for scen, dd in ((s, d) for s, d in
                 ((scen, {day: [x[1] for x in runs] for day, runs in scens.items()})
                  for scen, scens in
                  ((k, {d: v for d, v in dd.items()}) for k, dd in
                   {}.items()))):
    pass

scen_days = defaultdict(lambda: defaultdict(list))
for day, scens in sessions.items():
    for scen, runs in scens.items():
        for _, sc in runs:
            scen_days[scen][day].append(sc)

for scen, dd in scen_days.items():
    groups = [v for v in dd.values() if len(v) >= 2]
    if len(groups) < 4:
        continue
    grand = statistics.mean([x for g in groups for x in g])
    if grand <= 0:
        continue
    within_vars = [statistics.variance(g) for g in groups if len(g) >= 2]
    ns = [len(g) for g in groups]
    within_v = statistics.mean(within_vars)
    # 各天均值的方差，期望 = true_between + within/n（用平均 n 近似）
    obs_between_v = statistics.variance([statistics.mean(g) for g in groups])
    true_between_v = max(obs_between_v - within_v / statistics.mean(ns), 0.0)
    rows.append((scen, len(groups), within_v ** .5 / grand * 100,
                 true_between_v ** .5 / grand * 100,
                 (within_v ** .5) / (true_between_v ** .5) if true_between_v > 0 else 999))

rows.sort(key=lambda r: -r[4])
print("\n  %-40s %4s %10s %10s %8s" % ("scenario", "天数", "日内SD%", "日间SD%", "日内/日间"))
for r in rows[:16]:
    print("  %-40s %4d %9.1f%% %9.1f%% %8.2f" % (r[0][:40], r[1], r[2], r[3], r[4]))
if rows:
    print("\n  中位比值 %.2f" % statistics.median(r[4] for r in rows))

# ---------- B) 热身曲线 ----------
print()
print("=" * 96)
print("【B】热身曲线：同一天同场景内，第 k 轮 / 当天最好一轮")
print("=" * 96)
curve = defaultdict(list)
for day, scens in sessions.items():
    for scen, runs in scens.items():
        runs = sorted(runs)
        if len(runs) < 3:
            continue
        best = max(s for _, s in runs)
        if best <= 0:
            continue
        for k, (_, s) in enumerate(runs[:6], 1):
            curve[k].append(s / best * 100)

print("\n  %-6s %6s %10s %10s" % ("轮次", "样本", "相对最好%", "到平台"))
prev = None
for k in sorted(curve):
    v = curve[k]
    m = statistics.mean(v)
    flag = ""
    if prev is not None and m - prev < 0.5 and k > 1:
        flag = "← 已到平台"
    print("  %-6s %6d %9.1f%% %10s" % ("第%d轮" % k, len(v), m, flag))
    prev = m

# 按场景族看：WARMUP 场景 vs 正式场景
print()
print("  分组（第 1 轮 / 第 2 轮 / 第 3+ 轮 相对当天最好）")
for label, cond in [("WARMUP 场景", lambda s: "WARMUP" in s.upper()),
                    ("正式场景", lambda s: "WARMUP" not in s.upper())]:
    c = defaultdict(list)
    for day, scens in sessions.items():
        for scen, runs in scens.items():
            if not cond(scen):
                continue
            runs = sorted(runs)
            if len(runs) < 3:
                continue
            best = max(s for _, s in runs)
            if best <= 0:
                continue
            c[1].append(runs[0][1] / best * 100)
            c[2].append(runs[1][1] / best * 100)
            c[3].append(statistics.mean([s for _, s in runs[2:6]]) / best * 100)
    if c[1]:
        print("  %-12s n=%-4d 第1轮 %5.1f%%  第2轮 %5.1f%%  第3+轮 %5.1f%%"
              % (label, len(c[1]), statistics.mean(c[1]), statistics.mean(c[2]), statistics.mean(c[3])))

json.dump({"variance_fixed": [{"scenario": r[0], "days": r[1], "within_sd": r[2],
                               "between_sd": r[3], "ratio": r[4]} for r in rows],
           "warmup_curve": {k: {"n": len(v), "pct_of_best": statistics.mean(v)} for k, v in curve.items()}},
          open(os.path.join(OUT, "本地数据-热身曲线.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n保存 -> 学术原始数据/本地数据-热身曲线.json")
