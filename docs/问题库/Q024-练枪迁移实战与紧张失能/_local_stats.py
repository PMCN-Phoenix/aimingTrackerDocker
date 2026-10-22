# -*- coding: utf-8 -*-
"""Q024 本地数据分析：练枪表现里的「状态成分」有多大

三个问题：
1) 冷启动代价 —— 每天同一场景的第 1 轮 vs 后续轮，差多少？（= 热身衰减 warm-up decrement）
2) 方差分解   —— 同一场景的表现波动，是「天与天之间」大还是「同一天内轮与轮之间」大？
                 （日内大 = 状态问题；日间大 = 能力问题）
3) 局内衰减   —— 一轮里前半 vs 后半，命中率/TTK 怎么走？（= 60 秒内能不能撑住）
"""
import os, re, json, statistics
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
FN = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")


def parse(path):
    L = open(path, encoding="utf-8", errors="ignore").readlines()
    meta = {}
    for l in L:
        p = l.split(",")
        if len(p) > 1 and p[0].strip().endswith(":"):
            meta[p[0].strip()] = p[1].strip()
    hi = next((i for i, l in enumerate(L) if l.startswith("Kill #")), None)
    kills = []
    if hi is not None:
        cols = [c.strip() for c in L[hi].rstrip().split(",")]
        for l in L[hi + 1:]:
            q = l.rstrip().split(",")
            if len(q) < len(cols) or not q[0].strip().isdigit():
                break
            r = dict(zip(cols, q))
            m = re.match(r"([\d.]+)s", (r.get("TTK") or "").strip())
            try:
                kills.append({
                    "ttk": float(m.group(1)) if m else None,
                    "shots": float(r.get("Shots") or 0),
                    "hits": float(r.get("Hits") or 0),
                })
            except Exception:
                pass
    return meta, kills


def fnum(s):
    try:
        return float(s)
    except Exception:
        return None


# ---------- 载入 ----------
# day -> scenario -> [(time_str, score, acc, kills, half_stats)]
sessions = defaultdict(lambda: defaultdict(list))
for fn in os.listdir(STATS):
    m = FN.match(fn)
    if not m:
        continue
    scen = m.group(1).strip()
    day = "%s-%s-%s" % (m.group(2), m.group(3), m.group(4))
    tstr = "%s:%s:%s" % (m.group(5), m.group(6), m.group(7))
    meta, kills = parse(os.path.join(STATS, fn))
    score = fnum(meta.get("Score:"))
    acc = fnum((meta.get("Accuracy:") or "").replace("%", ""))
    if score is None:
        continue
    # 局内前后半
    half = None
    if len(kills) >= 8:
        h = len(kills) // 2
        def agg(ks):
            sh = sum(k["shots"] for k in ks)
            hi = sum(k["hits"] for k in ks)
            tt = [k["ttk"] for k in ks if k["ttk"]]
            return (hi / sh * 100 if sh else None,
                    statistics.median(tt) if tt else None)
        a1, t1 = agg(kills[:h])
        a2, t2 = agg(kills[h:])
        if a1 and a2 and t1 and t2:
            half = {"acc1": a1, "acc2": a2, "ttk1": t1, "ttk2": t2, "n": len(kills)}
    sessions[day][scen].append({"t": tstr, "score": score, "acc": acc,
                                "kills": len(kills), "half": half})

# ---------- 1. 冷启动代价 ----------
# 对每个 (day, scenario)，按时间排序，取第 1 轮 vs 第 2~4 轮
first_vs_rest = []
per_scen = defaultdict(lambda: {"first": [], "rest": []})
for day, scens in sessions.items():
    for scen, runs in scens.items():
        if len(runs) < 2:
            continue
        runs = sorted(runs, key=lambda r: r["t"])
        f = runs[0]["score"]
        rest = [r["score"] for r in runs[1:4]]
        if not rest:
            continue
        rel = (f / statistics.mean(rest) - 1) * 100
        first_vs_rest.append(rel)
        per_scen[scen]["first"].append(f)
        per_scen[scen]["rest"].append(statistics.mean(rest))

print("=" * 100)
print("【1】冷启动代价：同一天同场景「第 1 轮」相对「第 2~4 轮均值」的偏差")
print("     （负 = 第一轮更差 = 需要热身；样本 = %d 个 日×场景 组合）" % len(first_vs_rest))
print("=" * 100)
if first_vs_rest:
    print("  中位数 %+.1f%%   均值 %+.1f%%   明显偏冷(< -3%%) 占比 %.0f%%   明显偏热(> +3%%) 占比 %.0f%%"
          % (statistics.median(first_vs_rest), statistics.mean(first_vs_rest),
             sum(1 for x in first_vs_rest if x < -3) / len(first_vs_rest) * 100,
             sum(1 for x in first_vs_rest if x > 3) / len(first_vs_rest) * 100))

rows = []
for scen, d in per_scen.items():
    if len(d["first"]) >= 3:
        rows.append((scen, len(d["first"]),
                     statistics.mean(d["first"]), statistics.mean(d["rest"]),
                     (statistics.mean(d["first"]) / statistics.mean(d["rest"]) - 1) * 100))
rows.sort(key=lambda r: r[4])
print("\n  %-42s %5s %10s %10s %8s" % ("scenario", "n天", "第1轮均分", "后续均分", "差%"))
for r in rows[:10] + [("...", 0, 0, 0, 0)] + rows[-6:]:
    if r[0] == "...":
        print("  " + "-" * 80)
        continue
    print("  %-42s %5d %10.1f %10.1f %+7.1f%%" % (r[0][:42], r[1], r[2], r[3], r[4]))

# ---------- 2. 方差分解 ----------
print()
print("=" * 100)
print("【2】方差分解：表现波动来自「天」还是「轮」")
print("     within = 同一天内各轮的离散度（状态）; between = 各天均值的离散度（能力/长期）")
print("=" * 100)
var_rows = []
for scen, days in defaultdict(list).items():
    pass
scen_days = defaultdict(lambda: defaultdict(list))
for day, scens in sessions.items():
    for scen, runs in scens.items():
        for r in runs:
            scen_days[scen][day].append(r["score"])

for scen, dd in scen_days.items():
    daymeans = [statistics.mean(v) for v in dd.values() if len(v) >= 2]
    if len(daymeans) < 3:
        continue
    within = statistics.mean([statistics.pstdev(v) / statistics.mean(v) * 100
                              for v in dd.values() if len(v) >= 2 and statistics.mean(v) > 0])
    between = statistics.pstdev(daymeans) / statistics.mean(daymeans) * 100
    var_rows.append((scen, len(dd), len(daymeans), within, between, within / between if between else 0))
var_rows.sort(key=lambda r: -r[5])
print("\n  %-40s %4s %5s %9s %9s %7s" % ("scenario", "天数", "有效天", "日内CV%", "日间CV%", "比值"))
for r in var_rows[:14]:
    print("  %-40s %4d %5d %8.1f%% %8.1f%% %6.2f" % (r[0][:40], r[1], r[2], r[3], r[4], r[5]))
if var_rows:
    print("\n  中位比值 %.2f（>1 = 同一天内轮与轮之间比天与天之间波动更大 → 状态主导）"
          % statistics.median(r[5] for r in var_rows))

# ---------- 3. 局内衰减 ----------
print()
print("=" * 100)
print("【3】局内衰减：同一轮里后半段相对前半段")
print("=" * 100)
halves = []
for day, scens in sessions.items():
    for scen, runs in scens.items():
        for r in runs:
            if r["half"]:
                halves.append(r["half"])
if halves:
    da = [h["acc2"] - h["acc1"] for h in halves]
    dt = [h["ttk2"] - h["ttk1"] for h in halves]
    print("  样本 %d 轮（每轮 ≥8 杀）" % len(halves))
    print("  命中率 后半−前半：中位 %+.2f 个百分点，均值 %+.2f，变差占比 %.0f%%"
          % (statistics.median(da), statistics.mean(da), sum(1 for x in da if x < 0) / len(da) * 100))
    print("  TTK    后半−前半：中位 %+.3f 秒，均值 %+.3f，变慢占比 %.0f%%"
          % (statistics.median(dt), statistics.mean(dt), sum(1 for x in dt if x > 0) / len(dt) * 100))

# ---------- 保存 ----------
os.makedirs(OUT, exist_ok=True)
json.dump({
    "cold_start": {"n": len(first_vs_rest),
                   "median_pct": statistics.median(first_vs_rest) if first_vs_rest else None,
                   "mean_pct": statistics.mean(first_vs_rest) if first_vs_rest else None,
                   "by_scenario": [{"scenario": r[0], "days": r[1], "first": r[2], "rest": r[3], "diff_pct": r[4]} for r in rows]},
    "variance_decomp": [{"scenario": r[0], "days": r[1], "within_cv": r[3], "between_cv": r[4], "ratio": r[5]} for r in var_rows],
    "within_run": {"n": len(halves),
                   "acc_median_delta": statistics.median(da) if halves else None,
                   "ttk_median_delta": statistics.median(dt) if halves else None},
}, open(os.path.join(OUT, "本地数据-状态成分.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n保存 -> 学术原始数据/本地数据-状态成分.json")
