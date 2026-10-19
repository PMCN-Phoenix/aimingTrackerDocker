# -*- coding: utf-8 -*-
"""Q022 本地数据：跟丢 → 回血 的代价量化

核心指标
--------
Kovaak's stats CSV 每次击杀一行，含 `Damage Done`（本次击杀实际造成的伤害 / 目标总血量）。
- Damage Done = 1.00 → 干净击杀，一次没跟丢
- Damage Done = 1.50 → 多打了 50% 伤害 = 目标回过 50% 血
- Damage Done = 3.55 → 多打 255%，跟丢两次

`excess = Damage Done - 1` 就是「跟丢代价」的货币单位。
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
        rows.append({"ttk": ttk, "shots": f("Shots"), "hits": f("Hits"),
                     "dmg": f("Damage Done"), "eff": f("Efficiency")})
    return rows

agg = defaultdict(lambda: {"kills": 0, "ttk": [], "dmg": [], "clean": 0, "regen1": 0,
                           "regen2": 0, "hits": 0, "shots": 0, "runs": 0})
for fn in os.listdir(STATS):
    m = FN.match(fn)
    if not m:
        continue
    scn = m.group(1)
    if "psalm" not in scn.lower() and "regens" not in scn.lower():
        continue
    rows = parse(os.path.join(STATS, fn))
    if not rows:
        continue
    a = agg[scn]
    a["runs"] += 1
    for r in rows:
        if r["dmg"] is None:
            continue
        a["kills"] += 1
        a["dmg"].append(r["dmg"])
        if r["ttk"]:
            a["ttk"].append(r["ttk"])
        a["hits"] += r["hits"] or 0
        a["shots"] += r["shots"] or 0
        ex = r["dmg"] - 1.0
        if ex <= 0.001:
            a["clean"] += 1
        elif ex <= 0.6:
            a["regen1"] += 1
        else:
            a["regen2"] += 1

rows_out = []
for scn, a in agg.items():
    t = sorted(a["ttk"])
    d = a["dmg"]
    rows_out.append({
        "scenario": scn,
        "runs": a["runs"],
        "kills": a["kills"],
        "clean_pct": round(a["clean"] / a["kills"] * 100, 1) if a["kills"] else None,
        "regen_light_pct": round(a["regen1"] / a["kills"] * 100, 1) if a["kills"] else None,
        "regen_heavy_pct": round(a["regen2"] / a["kills"] * 100, 1) if a["kills"] else None,
        "mean_dmg": round(statistics.mean(d), 3) if d else None,
        "mean_excess_pct": round((statistics.mean(d) - 1) * 100, 1) if d else None,
        "median_ttk": round(statistics.median(t), 3) if t else None,
        "p90_ttk": round(t[int(len(t) * 0.9)], 3) if len(t) >= 10 else None,
        "p90_over_p50": round(t[int(len(t) * 0.9)] / statistics.median(t), 2)
                        if len(t) >= 10 and statistics.median(t) else None,
        "hit_rate": round(a["hits"] / a["shots"] * 100, 1) if a["shots"] else None,
    })
rows_out.sort(key=lambda r: -(r["kills"] or 0))
os.makedirs(OUT, exist_ok=True)
json.dump({"rows": rows_out}, open(os.path.join(OUT, "本地数据-回血代价.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("%-34s %4s %5s %7s %7s %7s %8s %7s %7s" % (
    "scenario", "runs", "kills", "clean%", "轻回血%", "重回血%", "均伤%", "medTTK", "p90/p50"))
for r in rows_out:
    print("%-34s %4s %5s %7s %7s %7s %8s %7s %7s" % (
        r["scenario"][:34], r["runs"], r["kills"], r["clean_pct"], r["regen_light_pct"],
        r["regen_heavy_pct"], r["mean_excess_pct"], r["median_ttk"], r["p90_over_p50"]))

# 专项：VT psalmTS Advanced Regen 的 TTK × 回血 联合分布
scn = "VT psalmTS Advanced Regen"
if scn in agg:
    a = agg[scn]
    pairs = [(r["ttk"], r["dmg"]) for r in
             [x for x in (parse(os.path.join(STATS, f)) for f in os.listdir(STATS) if FN.match(f) and FN.match(f).group(1) == scn)
              for x in x]
             if r["ttk"] and r["dmg"]]
    print("\n=== %s 单次击杀：TTK × 伤害 ===" % scn)
    print("击杀数", len(pairs))
    for lo, hi, label in [(0, 0.6, "<0.6s"), (0.6, 1.0, "0.6-1.0s"), (1.0, 1.5, "1.0-1.5s"), (1.5, 99, ">1.5s")]:
        sub = [p for p in pairs if lo <= p[0] < hi]
        if sub:
            print("  %-9s n=%3d | 均伤 %.2f | 干净击杀 %4.1f%%" % (
                label, len(sub), statistics.mean(x[1] for x in sub),
                sum(1 for x in sub if x[1] <= 1.001) / len(sub) * 100))
