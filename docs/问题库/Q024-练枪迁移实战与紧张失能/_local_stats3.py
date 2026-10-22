# -*- coding: utf-8 -*-
"""Q024 修正：冷启动效应必须用场景自身的轮间标准差归一化（否则高方差场景会假性放大）

同时检验「越弱的场景冷启动损失越大」这个假设：
   x = 该场景的长期水平（用各天最好成绩的中位数作代理，跨场景不可比，改用「场景内相对位置」）
   y = 冷启动效应（Cohen's d = 第一轮偏离 / 轮间SD）
更干净的做法：直接看 d 值排序，并报告与场景 CV 的关系（如果 d 与 CV 无关，说明不是噪声放大）。
"""
import os, re, json, statistics
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
FN = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")


def score_of(p):
    for l in open(p, encoding="utf-8", errors="ignore"):
        q = l.split(",")
        if len(q) > 1 and q[0].strip() == "Score:":
            try:
                return float(q[1])
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

rows = []
for scen in {s for scens in sessions.values() for s in scens}:
    firsts, rests, sds = [], [], []
    for day, scens in sessions.items():
        runs = scens.get(scen)
        if not runs or len(runs) < 3:
            continue
        runs = sorted(runs)
        f = runs[0][1]
        rest = [r[1] for r in runs[1:4]]
        if not rest:
            continue
        m_rest = statistics.mean(rest)
        if m_rest <= 0:
            continue
        firsts.append(f)
        rests.append(m_rest)
        sds.append(statistics.pstdev([r[1] for r in runs]) / m_rest * 100)
    if len(firsts) < 4:
        continue
    grand = statistics.mean(rests)
    diff_pct = (statistics.mean(firsts) / grand - 1) * 100
    # 用该场景所有轮次的整体 SD（相对均值）作为分母，换算成 d
    all_sd = statistics.mean(sds) if sds else 0
    d = diff_pct / all_sd if all_sd else 0
    rows.append({"scenario": scen, "days": len(firsts), "first": statistics.mean(firsts),
                 "rest": grand, "diff_pct": diff_pct, "within_sd_pct": all_sd, "d": d})

rows.sort(key=lambda r: r["d"])
print("=" * 104)
print("【冷启动效应 · 方差归一化版】 d = (第1轮均值 − 后续均值) / 该场景轮间SD")
print("  |d| < 0.2 可忽略；0.2–0.5 小；0.5–0.8 中；> 0.8 大")
print("=" * 104)
print("\n  %-40s %4s %9s %8s %9s %6s" % ("scenario", "天数", "原始差%", "轮间SD%", "Cohen d", "判定"))
for r in rows:
    lvl = "可忽略" if abs(r["d"]) < 0.2 else "小" if abs(r["d"]) < 0.5 else "中" if abs(r["d"]) < 0.8 else "大"
    print("  %-40s %4d %+8.1f%% %7.1f%% %+9.2f %6s" % (r["scenario"][:40], r["days"], r["diff_pct"],
                                                       r["within_sd_pct"], r["d"], lvl))

ds = [r["d"] for r in rows]
cvs = [r["within_sd_pct"] for r in rows]
print("\n  场景数 %d｜d 中位 %+.2f｜d<−0.2 的场景 %d 个｜d>+0.2 的场景 %d 个"
      % (len(ds), statistics.median(ds), sum(1 for x in ds if x < -0.2), sum(1 for x in ds if x > 0.2)))

# d 与 CV 的相关（检验「是不是高方差场景在假性放大」）
if len(ds) >= 6:
    md, mc = statistics.mean(ds), statistics.mean(cvs)
    cov = sum((a - md) * (b - mc) for a, b in zip(ds, cvs))
    den = (sum((a - md) ** 2 for a in ds) * sum((b - mc) ** 2 for b in cvs)) ** .5
    print("  d 与「轮间SD」的相关 r = %+.2f  （≈0 = 冷启动效应不是方差假象；明显负 = 噪声放大）"
          % (cov / den if den else 0))

json.dump(rows, open(os.path.join(OUT, "本地数据-冷启动效应量.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n保存 -> 学术原始数据/本地数据-冷启动效应量.json")
