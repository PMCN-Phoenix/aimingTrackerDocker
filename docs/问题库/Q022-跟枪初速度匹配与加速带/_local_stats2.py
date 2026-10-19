# -*- coding: utf-8 -*-
"""Q022 本地数据（二）：跟丢的「惯性」——一次跟丢会不会拖累下一次

三个新指标
----------
1. 承接性 (carryover)：P(本次重跟丢 | 上次重跟丢) vs P(本次重跟丢 | 上次干净)
   如果前者显著更高，说明跟丢不是独立事件，会「粘」在下一段。
2. 局内漂移 (within-run drift)：同一局里前一半击杀 vs 后一半击杀的平均伤害。
   如果后半更差，说明是资源/注意力衰减；如果后半更好，说明是热身。
3. 重加速次数 (re-acceleration proxy)：每次击杀的 Misses = Shots - Hits。
   跟丢一次 → 重新加速一次 → 至少产生一段连续 miss。用 miss 数分布反推「一次击杀里
   被迫重新起步了几次」。
"""
import os, re, json, statistics
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
FN = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-")


def parse(path):
    lines = open(path, encoding="utf-8", errors="ignore").readlines()
    hi = next((i for i, l in enumerate(lines) if l.startswith("Kill #")), None)
    if hi is None:
        return []
    cols = [c.strip() for c in lines[hi].rstrip().split(",")]
    rows = []
    for l in lines[hi + 1:]:
        p = l.rstrip().split(",")
        if len(p) < len(cols) or not p[0].strip().isdigit():
            break
        r = dict(zip(cols, p))
        def f(k):
            try:
                return float(r.get(k, ""))
            except Exception:
                return None
        ttk = None
        m = re.match(r"([\d.]+)s", (r.get("TTK") or "").strip())
        if m:
            ttk = float(m.group(1))
        rows.append({"ttk": ttk, "shots": f("Shots"), "hits": f("Hits"), "dmg": f("Damage Done")})
    return rows


TARGETS = ["VT psalmTS Advanced Regen", "VT psalmTS Novice",
           "psalmTS Voltaic LowTTK", "psalmTS Voltaic Easy"]

runs = defaultdict(list)   # scn -> [ [rows...], ... ]
for fn in os.listdir(STATS):
    m = FN.match(fn)
    if not m:
        continue
    scn = m.group(1)
    if scn not in TARGETS:
        continue
    rows = [r for r in parse(os.path.join(STATS, fn)) if r["dmg"] is not None]
    if rows:
        runs[scn].append(rows)

HEAVY = 1.6   # excess > 0.6 视为重跟丢

out = {}
print("=" * 88)
print("1) 承接性：上一次跟丢，会不会把下一次也拖下水")
print("=" * 88)
print("%-30s %7s %7s %7s %7s %8s" % ("scenario", "n对", "P(重|重)", "P(重|净)", "倍数", "卡方感觉"))
for scn in TARGETS:
    if scn not in runs:
        continue
    hh = ht = th = tt = 0
    for rs in runs[scn]:
        for i in range(1, len(rs)):
            prev_heavy = rs[i - 1]["dmg"] > HEAVY
            cur_heavy = rs[i]["dmg"] > HEAVY
            if prev_heavy:
                th += 1
                hh += cur_heavy
            else:
                tt += 1
                ht += cur_heavy
    p_rr = hh / th * 100 if th else 0
    p_rn = ht / tt * 100 if tt else 0
    ratio = p_rr / p_rn if p_rn else 0
    print("%-30s %7d %6.1f%% %6.1f%% %7.2fx" % (scn[:30], th + tt, p_rr, p_rn, ratio))
    out.setdefault(scn, {})["carryover"] = {
        "n_pairs": th + tt, "p_heavy_after_heavy": round(p_rr, 1),
        "p_heavy_after_clean": round(p_rn, 1), "ratio": round(ratio, 2),
        "n_after_heavy": th, "n_after_clean": tt}

print()
print("=" * 88)
print("2) 局内漂移：一局的前一半 vs 后一半")
print("=" * 88)
print("%-30s %6s %8s %8s %8s" % ("scenario", "局数", "前半均伤", "后半均伤", "差值"))
for scn in TARGETS:
    if scn not in runs:
        continue
    first, second = [], []
    for rs in runs[scn]:
        k = len(rs) // 2
        if k < 2:
            continue
        first += [r["dmg"] for r in rs[:k]]
        second += [r["dmg"] for r in rs[k:]]
    if first and second:
        a, b = statistics.mean(first), statistics.mean(second)
        print("%-30s %6d %8.3f %8.3f %+8.3f" % (scn[:30], len(runs[scn]), a, b, b - a))
        out.setdefault(scn, {})["within_run"] = {
            "first_half_mean_dmg": round(a, 3), "second_half_mean_dmg": round(b, 3),
            "delta": round(b - a, 3)}

print()
print("=" * 88)
print("3) 重加速次数代理：每次击杀的 Misses = Shots - Hits")
print("=" * 88)
print("%-30s %6s %7s %7s %7s %7s %7s" % ("scenario", "击杀", "均miss", "中位", "p75", "p90", "0miss%"))
for scn in TARGETS:
    if scn not in runs:
        continue
    ms = []
    for rs in runs[scn]:
        for r in rs:
            if r["shots"] is not None and r["hits"] is not None:
                ms.append(max(0, r["shots"] - r["hits"]))
    if not ms:
        continue
    ms.sort()
    n = len(ms)
    print("%-30s %6d %7.2f %7.1f %7.1f %7.1f %6.1f%%" % (
        scn[:30], n, statistics.mean(ms), statistics.median(ms),
        ms[int(n * 0.75)], ms[int(n * 0.9)], sum(1 for x in ms if x == 0) / n * 100))
    out.setdefault(scn, {})["misses_per_kill"] = {
        "kills": n, "mean": round(statistics.mean(ms), 2), "median": statistics.median(ms),
        "p75": ms[int(n * 0.75)], "p90": ms[int(n * 0.9)],
        "zero_miss_pct": round(sum(1 for x in ms if x == 0) / n * 100, 1)}

json.dump(out, open(os.path.join(OUT, "本地数据-跟丢惯性.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n保存 → 本地数据-跟丢惯性.json")
