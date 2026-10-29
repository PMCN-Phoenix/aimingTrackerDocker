# -*- coding: utf-8 -*-
"""G1 状态分析 v2：四格的真实分布、判定强度、状态杠杆

核心指标：缺口 ÷ 波动（SD）
  << 1  → 过线是概率事件，靠轮数采样
  ~ 1   → 状态能左右结果
  >> 1  → 能力缺口，状态优化无效

输出：
1) 每格全部轮次（按日分组）
2) 每格的均值/日内SD/日间SD/缺口÷SD/单轮过线概率
3) 拿到「同日 2 轮过线」需要打几轮（二项分布）
4) 今日四格判定（真过/假过/不过）
"""
import os, re, statistics as st
from collections import defaultdict
from math import erf, sqrt

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
FN = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$")

TARGETS = {
    "Air Pure Easier No UFO":            ("B", 919.0),
    "Plink Palace Easy Less Blinks":     ("A", 2175.0),
    "Pasu Voltaic Reload Easier":        ("C", 52.0),
    "VT Floating Heads Viscose Easier":  ("D", 580.0),
}


def norm_cdf(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def parse(path):
    for line in open(path, encoding="utf-8", errors="ignore"):
        p = [x.strip() for x in line.split(",")]
        if len(p) > 1 and p[0] == "Score:":
            try:
                return float(p[1])
            except ValueError:
                return None
    return None


rows = []
for f in os.listdir(STATS):
    m = FN.match(f)
    if not m or m.group(1) not in TARGETS:
        continue
    tag, line = TARGETS[m.group(1)]
    s = parse(os.path.join(STATS, f))
    if s is None:
        continue
    rows.append(dict(tag=tag, name=m.group(1), line=line,
                     day=f"{m.group(2)}-{m.group(3)}-{m.group(4)}",
                     t=f"{m.group(5)}:{m.group(6)}:{m.group(7)}", score=s))
rows.sort(key=lambda r: (r["day"], r["t"]))

by_tag = defaultdict(list)
for r in rows:
    by_tag[r["tag"]].append(r)

TODAY = "2026-10-29"

print("=" * 84)
print("一、每格全部轮次")
print("=" * 84)
for tag in "ABCD":
    rs = by_tag[tag]
    line = rs[0]["line"]
    print(f"\n[{tag}] {rs[0]['name']}   线 = {line:g}")
    days = defaultdict(list)
    for r in rs:
        days[r["day"]].append(r)
    for d in sorted(days):
        seg = days[d]
        vals = [x["score"] for x in seg]
        cells = "  ".join(f"{v:>8.1f}{'*' if v >= line else ' '}" for v in vals)
        npass = sum(1 for v in vals if v >= line)
        print(f"  {d} ({len(vals):>2}轮) {cells}   过线 {npass}/{len(vals)}")

print()
print("=" * 84)
print("二、波动结构：缺口 ÷ SD（决定「状态」是不是有效杠杆）")
print("=" * 84)
hdr = f"{'格':<3}{'轮数':>4}{'均值':>9}{'日内SD':>8}{'总体SD':>8}{'线':>8}{'缺口%':>8}{'缺口/SD':>8}{'单轮过线率':>9}"
print(hdr)
stats = {}
for tag in "ABCD":
    rs = by_tag[tag]
    line = rs[0]["line"]
    vals = [r["score"] for r in rs]
    mu = st.mean(vals)
    sd_all = st.pstdev(vals)
    days = defaultdict(list)
    for r in rs:
        days[r["day"]].append(r["score"])
    within = [st.pstdev(v) for v in days.values() if len(v) >= 2]
    sd_w = st.mean(within) if within else float("nan")
    gap = (line - mu) / mu * 100
    ratio = (line - mu) / sd_all if sd_all else float("nan")
    p = 1 - norm_cdf((line - mu) / sd_all) if sd_all else float("nan")
    stats[tag] = dict(mu=mu, sd=sd_all, sd_w=sd_w, line=line, gap=gap, ratio=ratio, p=p, n=len(vals))
    print(f"{tag:<3}{len(vals):>4}{mu:>9.1f}{sd_w:>8.1f}{sd_all:>8.1f}{line:>8g}{gap:>+8.2f}%{ratio:>8.2f}{p * 100:>8.1f}%")

print()
print("=" * 84)
print("三、拿到「同日 2 轮过线」需要打几轮（假设各轮独立，二项分布）")
print("=" * 84)
from math import comb
for tag in "ABCD":
    p = stats[tag]["p"]
    if p != p:
        continue
    if p < 0.01:
        print(f"[{tag}] 单轮过线率 {p * 100:.1f}% → 需要 >100 轮，实际不可能")
        continue
    need = None
    for n in range(2, 60):
        pr = 1 - sum(comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(2))
        if pr >= 0.80:
            need = (n, pr)
            break
    if need:
        print(f"[{tag}] 单轮过线率 {p * 100:>5.1f}% → 打 {need[0]} 轮才有 80% 把握拿到 2 轮过线")
    else:
        print(f"[{tag}] 单轮过线率 {p * 100:>5.1f}% → 60 轮内做不到")

print()
print("=" * 84)
print("四、今日（%s）判定" % TODAY)
print("=" * 84)
for tag in "ABCD":
    seg = [r for r in by_tag[tag] if r["day"] == TODAY]
    if not seg:
        print(f"[{tag}] 今日无数据")
        continue
    line = seg[0]["line"]
    vals = [r["score"] for r in seg]
    npass = sum(1 for v in vals if v >= line)
    if npass >= 2:
        verdict = "真过"
    elif npass == 1:
        verdict = "假过（同日仅 1 轮过线）"
    else:
        verdict = "不过"
    print(f"[{tag}] {len(vals)} 轮 {vals} → 过线 {npass}/{len(vals)} → {verdict}")
