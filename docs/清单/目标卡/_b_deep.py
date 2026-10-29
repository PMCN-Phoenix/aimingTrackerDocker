# -*- coding: utf-8 -*-
"""B（Air Pure）的深化分析：把「差 1%」拆到目标类型层面

Air Pure 每轮有 4 个目标（AIR1_Short_close / AIR1_Short_far / AIR2_Long3D_mid / AIR2_Short_close），
每个目标固定吃满 1000 伤害，所以「打中要多少发」= 1000 / Accuracy，精度就是全部。

问题：B 的轮间 SD 只有 3.5 分（0.4%），但轮内 4 个目标的精度差到 11%。
如果某个目标类型在每一轮都最差，那 B 的缺口就不是「状态」也不是「整体能力」，
而是某个具体目标类型的技术问题。
"""
import os, re, statistics as st
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
FN = re.compile(r"^Air Pure Easier No UFO - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$")


def parse(path):
    L = open(path, encoding="utf-8", errors="ignore").readlines()
    meta = {}
    for l in L:
        p = [x.strip() for x in l.split(",")]
        if len(p) > 1 and p[0].endswith(":"):
            meta[p[0].rstrip(":")] = p[1]
    hi = next((i for i, l in enumerate(L) if l.startswith("Kill #")), None)
    rows = []
    if hi is not None:
        cols = [c.strip() for c in L[hi].rstrip().split(",")]
        for l in L[hi + 1:]:
            q = [x.strip() for x in l.rstrip().split(",")]
            if len(q) < len(cols) or not q[0].isdigit():
                break
            r = dict(zip(cols, q))
            rows.append(dict(
                bot=r["Bot"],
                ttk=float(r["TTK"].rstrip("s")),
                shots=float(r["Shots"]),
                hits=float(r["Hits"]),
                acc=float(r["Accuracy"]),
                over=float(r["OverShots"]),
                ts=r["Timestamp"],
            ))
    return meta, rows


rounds = []
for f in sorted(os.listdir(STATS)):
    m = FN.match(f)
    if not m:
        continue
    meta, rows = parse(os.path.join(STATS, f))
    rounds.append(dict(
        day=f"{m.group(1)}-{m.group(2)}-{m.group(3)}",
        t=f"{m.group(4)}:{m.group(5)}:{m.group(6)}",
        score=float(meta["Score"]),
        acc=float(meta["Hit Count"]) / float(meta["Hit Count"]) if False else
            float(meta["Hit Count"]) / (float(meta["Hit Count"]) + float(meta["Miss Count"])),
        rows=rows,
    ))

print("=" * 80)
print("一、逐轮总览")
print("=" * 80)
print(f"{'日期':<12}{'时刻':<10}{'Score':>9}{'总精度':>8}{'发数':>7}{'打中':>6}")
for r in rounds:
    sh = sum(x["shots"] for x in r["rows"])
    hi = sum(x["hits"] for x in r["rows"])
    print(f"{r['day']:<12}{r['t']:<10}{r['score']:>9.2f}{hi / sh:>8.4f}{sh:>7.0f}{hi:>6.0f}")

print()
print("=" * 80)
print("二、目标类型 × 每一轮 的精度（关键：有没有稳定的弱项）")
print("=" * 80)
bots = []
for r in rounds:
    for x in r["rows"]:
        if x["bot"] not in bots:
            bots.append(x["bot"])
hdr = f"{'目标':<22}" + "".join(f"{r['day'][5:] + ' ' + r['t'][:5]:>12}" for r in rounds) + f"{'均值':>9}{'极差':>8}"
print(hdr)
per_bot = defaultdict(list)
for b in bots:
    vals = []
    for r in rounds:
        hit = next((x for x in r["rows"] if x["bot"] == b), None)
        vals.append(hit["acc"] if hit else None)
    got = [v for v in vals if v is not None]
    per_bot[b] = got
    cells = "".join(f"{v:>12.4f}" if v is not None else f"{'—':>12}" for v in vals)
    print(f"{b:<22}{cells}{st.mean(got):>9.4f}{(max(got) - min(got)) * 100:>7.1f}pp")

print()
print("=" * 80)
print("三、同一轮内，最好目标 vs 最差目标")
print("=" * 80)
print(f"{'日期/时刻':<20}{'最差':<22}{'精度':>8}{'最好':<22}{'精度':>8}{'轮内差':>9}")
for r in rounds:
    if len(r["rows"]) < 2:
        continue
    lo = min(r["rows"], key=lambda x: x["acc"])
    hi = max(r["rows"], key=lambda x: x["acc"])
    print(f"{r['day'] + ' ' + r['t'][:5]:<20}{lo['bot']:<22}{lo['acc']:>8.4f}"
          f"{hi['bot']:<22}{hi['acc']:>8.4f}{(hi['acc'] - lo['acc']) * 100:>8.1f}pp")

print()
print("=" * 80)
print("四、目标类型的排序稳定性")
print("=" * 80)
order = sorted(per_bot.items(), key=lambda kv: st.mean(kv[1]))
print("按平均精度从差到好：")
for b, v in order:
    print(f"  {b:<22} {st.mean(v):.4f}  （{len(v)} 轮，{min(v):.4f}–{max(v):.4f}）")

print()
print("=" * 80)
print("五、OverShots（过冲发数）分布")
print("=" * 80)
for b in bots:
    ov = [next((x["over"] for x in r["rows"] if x["bot"] == b), None) for r in rounds]
    ov = [x for x in ov if x is not None]
    print(f"  {b:<22} {ov}  均值 {st.mean(ov):.1f}")

print()
print("=" * 80)
print("六、TTK（打死每个目标耗时）")
print("=" * 80)
for b in bots:
    t = [next((x["ttk"] for x in r["rows"] if x["bot"] == b), None) for r in rounds]
    t = [x for x in t if x is not None]
    print(f"  {b:<22} {[round(x, 2) for x in t]}  均值 {st.mean(t):.2f}s")
