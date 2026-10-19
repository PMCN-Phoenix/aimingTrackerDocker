# -*- coding: utf-8 -*-
"""Q021 本地数据：从 Kovaak's stats CSV 量化"切换损耗"

关键口径说明
------------
1. 跟踪类场景（VSS/Smoothbot/Pasu 等）的 Accuracy 是"准星在靶时间占比"，与
   点击/切换类场景的 Accuracy（命中/发射）**不是同一个量**，不能跨类比较。
2. 因此本脚本只在**同族内**做比较，并对切换类场景构造一个直接对应"跳过头"的指标：
   每杀多打的子弹数 = Shots - Hits（LG 类武器 20 发命中即击杀）。
   - 0 损耗 = 干净的一次 flick 落点（shots == hits）
   - 多打 1-2 发 = 轻微过头/微修正
   - 多打 >=3 发 = 明显过头或抖动
3. 同时统计 TTK（击杀耗时），它是"切换速度"的直接度量。
"""
import os, re, csv, json, statistics
from collections import defaultdict

STATS = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")

FNAME = re.compile(r"^(.+?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2})")

def parse_file(path):
    """返回 dict: scenario, dt, kills(list of dict), score, accuracy"""
    base = os.path.basename(path)
    m = FNAME.match(base)
    if not m:
        return None
    scenario = m.group(1)
    dt = "%s-%s-%s %s:%s:%s" % (m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7))
    kills = []
    score = accuracy = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    # 击杀明细：表头以 "Kill #" 开头
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("Kill #"):
            header_idx = i
            break
    if header_idx is not None:
        cols = [c.strip() for c in lines[header_idx].rstrip("\n").split(",")]
        for ln in lines[header_idx + 1:]:
            parts = ln.rstrip("\n").split(",")
            if len(parts) < len(cols) or not parts[0].strip().isdigit():
                break
            row = dict(zip(cols, parts))
            def f(k):
                try:
                    return float(row.get(k, ""))
                except Exception:
                    return None
            ttk = row.get("TTK", "")
            ttk_v = None
            mm = re.match(r"([\d.]+)s", ttk.strip()) if ttk else None
            if mm:
                ttk_v = float(mm.group(1))
            kills.append({"shots": f("Shots"), "hits": f("Hits"),
                          "acc": f("Accuracy"), "ttk": ttk_v,
                          "weapon": row.get("Weapon", "").strip()})
    for ln in lines:
        mm = re.search(r"^Score:,([\d.]+)", ln)
        if mm:
            score = float(mm.group(1))
        mm = re.search(r"^Accuracy:,([\d.]+)", ln)
        if mm:
            accuracy = float(mm.group(1))
    return {"scenario": scenario, "dt": dt, "kills": kills, "score": score, "accuracy": accuracy}

# ---------- 场景族分类 ----------
def family(name):
    n = name.lower()
    if any(k in n for k in ["ts ", " ts", "ts_", "switch", "switching"]):
        return "切换类"
    if any(k in n for k in ["click", "1w", "ww", "6 sphere", "multiclick", "reflex", "bounce", "flick"]):
        return "点击类"
    if any(k in n for k in ["strafe", "tracking", "smooth", "pasu", "sphere", "popcorn", "glider",
                            "celestial", "air ", "controlsphere", "rawcontrol", "revolving",
                            "plaza", "tamspeed", "wide wall", "pressure", "xy ", "lgc3",
                            "centering", "e1se", "pole", "cycle", "kindaclose", "whisphere",
                            "flower", "cat", "leap", "ground", "pgti", "vss", "b360", "b180", "b90"]):
        return "跟踪类"
    return "其他"

# ---------- 主流程 ----------
per_scn = defaultdict(lambda: {"kills": 0, "shots": 0, "hits": 0, "clean": 0, "small": 0,
                               "big": 0, "ttk": [], "files": 0, "accs": [], "scores": [],
                               "dt_min": "9999", "dt_max": "0000"})
files = 0
for fn in os.listdir(STATS):
    if not fn.endswith(".csv"):
        continue
    p = os.path.join(STATS, fn)
    try:
        d = parse_file(p)
    except Exception:
        continue
    if not d:
        continue
    files += 1
    a = per_scn[d["scenario"]]
    a["files"] += 1
    a["dt_min"] = min(a["dt_min"], d["dt"])
    a["dt_max"] = max(a["dt_max"], d["dt"])
    if d["accuracy"] is not None:
        a["accs"].append(d["accuracy"])
    if d["score"] is not None:
        a["scores"].append(d["score"])
    for k in d["kills"]:
        if k["shots"] is None or k["hits"] is None:
            continue
        a["kills"] += 1
        a["shots"] += k["shots"]
        a["hits"] += k["hits"]
        waste = k["shots"] - k["hits"]
        if waste <= 0:
            a["clean"] += 1
        elif waste <= 2:
            a["small"] += 1
        else:
            a["big"] += 1
        if k["ttk"]:
            a["ttk"].append(k["ttk"])

rows = []
for scn, a in per_scn.items():
    rows.append({
        "scenario": scn,
        "family": family(scn),
        "files": a["files"],
        "kills": a["kills"],
        "shots": a["shots"],
        "hits": a["hits"],
        "hit_rate": round(a["hits"] / a["shots"] * 100, 2) if a["shots"] else None,
        "clean_pct": round(a["clean"] / a["kills"] * 100, 1) if a["kills"] else None,
        "small_pct": round(a["small"] / a["kills"] * 100, 1) if a["kills"] else None,
        "big_pct": round(a["big"] / a["kills"] * 100, 1) if a["kills"] else None,
        "shots_per_kill": round(a["shots"] / a["kills"], 2) if a["kills"] else None,
        "waste_per_kill": round((a["shots"] - a["hits"]) / a["kills"], 2) if a["kills"] else None,
        "mean_ttk": round(statistics.mean(a["ttk"]), 3) if a["ttk"] else None,
        "median_ttk": round(statistics.median(a["ttk"]), 3) if a["ttk"] else None,
        "p90_ttk": round(sorted(a["ttk"])[int(len(a["ttk"]) * 0.9)], 3) if len(a["ttk"]) >= 10 else None,
        "ttk_cv": round(statistics.pstdev(a["ttk"]) / statistics.mean(a["ttk"]), 3)
                  if len(a["ttk"]) >= 10 and statistics.mean(a["ttk"]) else None,
        "mean_acc_field": round(statistics.mean(a["accs"]), 4) if a["accs"] else None,
        "runs": a["files"],
        "first_dt": a["dt_min"],
        "last_dt": a["dt_max"],
    })

rows.sort(key=lambda r: (r["family"], -(r["kills"] or 0)))

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "本地数据-切换损耗.json"), "w", encoding="utf-8") as f:
    json.dump({"files": files, "rows": rows}, f, ensure_ascii=False, indent=2)

E12 = ["patTargetSwitch easy", "patTargetSwitch 90 easy", "patCircleSwitch NR",
       "psalmTS Voltaic Easy", "psalmTS Voltaic LowTTK", "VT psalmTS Advanced Regen",
       "VT psalmTS Novice", "Pokevox Easy LG56", "voxTS Voltaic LowTTK",
       "VoxTS Voltaic Jumbo Smooth", "voxTS Viscose Varied", "VT skyTS Novice"]

print("文件数", files, "| 场景数", len(rows))
print("\n=== E 清单 12 项（切换类）===")
print("%-30s %5s %5s %7s %7s %7s %8s %8s" % ("scenario", "runs", "kills", "hit%", "clean%", "big%", "waste/k", "medTTK"))
for scn in E12:
    r = next((x for x in rows if x["scenario"] == scn), None)
    if not r:
        print("%-30s  —— 无数据" % scn)
        continue
    print("%-30s %5s %5s %7s %7s %7s %8s %8s" % (
        scn[:30], r["runs"], r["kills"], r["hit_rate"], r["clean_pct"], r["big_pct"],
        r["waste_per_kill"], r["median_ttk"]))

print("\n=== 全部切换类场景（kills>=20）===")
print("%-34s %5s %5s %7s %7s %7s %8s %8s" % ("scenario", "runs", "kills", "hit%", "clean%", "big%", "waste/k", "medTTK"))
for r in rows:
    if r["family"] == "切换类" and (r["kills"] or 0) >= 20:
        print("%-34s %5s %5s %7s %7s %7s %8s %8s" % (
            r["scenario"][:34], r["runs"], r["kills"], r["hit_rate"], r["clean_pct"],
            r["big_pct"], r["waste_per_kill"], r["median_ttk"]))

print("\n=== 家族汇总 ===")
for fam in ("切换类", "点击类", "跟踪类"):
    sub = [r for r in rows if r["family"] == fam and (r["kills"] or 0) > 0]
    if not sub:
        continue
    K = sum(r["kills"] for r in sub)
    S = sum(r["shots"] for r in sub)
    H = sum(r["hits"] for r in sub)
    clean = sum(r["clean_pct"] * r["kills"] / 100 for r in sub)
    big = sum(r["big_pct"] * r["kills"] / 100 for r in sub)
    print("%-6s 场景%3d | 击杀%6d | 命中率 %5.1f%% | clean %4.1f%% | big %4.1f%% | 每杀多打 %.2f 发" % (
        fam, len(sub), K, H / S * 100 if S else 0, clean / K * 100 if K else 0,
        big / K * 100 if K else 0, (S - H) / K if K else 0))

# ---- 关键对照：同为"点击型"（每目标独立开枪），静态 vs 切换 ----
print("\n=== 关键对照：点击型场景 静态 vs 切换（命中率可直接比较）===")
STATIC_CLICK = [r for r in rows if r["family"] == "点击类" and (r["kills"] or 0) >= 100
                and "ts" not in r["scenario"].lower()]
SWITCH_CLICK = [r for r in rows if (r["kills"] or 0) >= 60
                and "ts" in r["scenario"].lower() and "click" in r["scenario"].lower()]
def agg(sub, label):
    K = sum(r["kills"] for r in sub); S = sum(r["shots"] for r in sub); H = sum(r["hits"] for r in sub)
    clean = sum(r["clean_pct"] * r["kills"] / 100 for r in sub)
    print("%-12s 场景%2d | 击杀%5d | 命中率 %5.1f%% | clean %4.1f%%" % (
        label, len(sub), K, H / S * 100 if S else 0, clean / K * 100 if K else 0))
    for r in sub:
        print("    %-34s 击杀%4d 命中%5.1f%% clean%5.1f%%" % (
            r["scenario"][:34], r["kills"], r["hit_rate"], r["clean_pct"]))
agg(STATIC_CLICK, "静态点击")
agg(SWITCH_CLICK, "切换点击")

print("\n=== TTK 稳定性（切换类，kills>=60）===")
print("%-34s %5s %7s %7s %7s %7s" % ("scenario", "kills", "medTTK", "p90TTK", "p90/p50", "CV"))
for r in sorted(rows, key=lambda x: -(x["kills"] or 0)):
    if r["family"] != "切换类" or (r["kills"] or 0) < 60 or not r["median_ttk"]:
        continue
    ratio = round(r["p90_ttk"] / r["median_ttk"], 2) if r["p90_ttk"] and r["median_ttk"] else None
    print("%-34s %5s %7s %7s %7s %7s" % (
        r["scenario"][:34], r["kills"], r["median_ttk"], r["p90_ttk"], ratio, r["ttk_cv"]))
