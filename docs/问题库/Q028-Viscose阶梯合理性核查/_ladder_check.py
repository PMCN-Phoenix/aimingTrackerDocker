# -*- coding: utf-8 -*-
"""Viscose S2 阶梯校准检查：档与档之间的跨度是否均匀

判断一个阶梯「合理」的最直接办法：看相邻档的百分比跨度。
- 若各档跨度大致一致（或单调递增）→ 阶梯是刻意校准过的
- 若某些档只差 2%、某些差 30% → 阶梯是拍脑袋定的，或者档名只是标签

同时检查：每一档的「跨越难度」是否与档位高低相关（越往上越难 = 合理）。
"""
import json, statistics as st
from collections import defaultdict

P = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\S2-官方分类诊断.json"
TIERS = ["Lemming", "Hare", "Ermine", "Puffin", "Penguin", "Fox", "Mammoth", "Orca", "Seal"]

d = json.load(open(P, encoding="utf-8"))
scs = [s for s in d["scenarios"] if s.get("targets") and len(s["targets"]) == 9]
print(f"参与分析的场景数：{len(scs)}（每个有完整 9 档阈值）\n")

# 每个档位跃迁的百分比跨度
gaps = defaultdict(list)
for s in scs:
    t = s["targets"]
    for i in range(8):
        if t[i] and t[i] > 0:
            gaps[i].append((t[i + 1] - t[i]) / t[i] * 100)

print("=" * 74)
print("一、相邻档之间的百分比跨度（跨全部场景）")
print("=" * 74)
print(f"{'跃迁':<22}{'场景数':>6}{'中位':>8}{'均值':>8}{'最小':>8}{'最大':>8}{'极差':>8}")
rows = []
for i in range(8):
    v = gaps[i]
    if not v:
        continue
    name = f"{TIERS[i]} → {TIERS[i + 1]}"
    rows.append((name, len(v), st.median(v), st.mean(v), min(v), max(v)))
    print(f"{name:<22}{len(v):>6}{st.median(v):>7.1f}%{st.mean(v):>7.1f}%"
          f"{min(v):>7.1f}%{max(v):>7.1f}%{max(v) - min(v):>7.1f}pp")

med = [r[2] for r in rows]
print()
print(f"八段中位跨度的范围：{min(med):.1f}% – {max(med):.1f}%，"
      f"最大/最小 = {max(med) / min(med):.2f} 倍")
print(f"单调递增？{'是' if all(med[i] < med[i + 1] for i in range(len(med) - 1)) else '否'}")

print()
print("=" * 74)
print("二、累计跨度：从 Lemming 到各档要涨多少")
print("=" * 74)
cum = defaultdict(list)
for s in scs:
    t = s["targets"]
    for i in range(1, 9):
        if t[0] and t[0] > 0:
            cum[i].append((t[i] - t[0]) / t[0] * 100)
print(f"{'目标档':<12}{'相对 Lemming 的中位涨幅':>24}")
prev = 0
for i in range(1, 9):
    v = cum[i]
    m = st.median(v)
    print(f"{TIERS[i]:<12}{m:>22.0f}%    （本段 +{m - prev:.0f}pp）")
    prev = m

print()
print("=" * 74)
print("三、同一个子类内，不同场景的阈值是否一致（跨场景可比性）")
print("=" * 74)
bysub = defaultdict(list)
for s in scs:
    bysub[(s["cat"], s["sub"])].append(s)

print(f"{'子类':<28}{'场景数':>5}{'Puffin 线离散度(CV)':>20}{'Fox 线离散度(CV)':>18}")
for k, v in sorted(bysub.items()):
    if len(v) < 2:
        continue
    p = [s["targets"][3] for s in v if s["targets"][3]]
    f = [s["targets"][5] for s in v if s["targets"][5]]
    cvp = st.pstdev(p) / st.mean(p) * 100 if len(p) > 1 else 0
    cvf = st.pstdev(f) / st.mean(f) * 100 if len(f) > 1 else 0
    print(f"{k[0] + ' / ' + k[1]:<28}{len(v):>5}{cvp:>18.0f}%{cvf:>17.0f}%")

print()
print("=" * 74)
print("四、各档在全库的分布（越往上人越少 = 阶梯有区分度）")
print("=" * 74)
cnt = defaultdict(int)
for s in scs:
    cnt[s["rank"]] += 1
for t in TIERS:
    print(f"  {t:<12}{cnt[t]:>4} 个场景")
