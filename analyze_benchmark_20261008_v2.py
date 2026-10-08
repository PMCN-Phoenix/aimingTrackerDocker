"""
分析 2026-10-08 完整基准测试结果 V2
使用 S2-官方分类诊断.json 的准确场景名和档位线
"""
import json
import urllib.request
from collections import defaultdict

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
TOKEN = "aim-super-secret-token-2026"
DIAG_FILE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\S2-官方分类诊断.json"
OUTPUT_FILE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\记录\VDIM起点基准-20261008.md"

TIER_NAMES = ["Lemming", "Hare", "Ermine", "Penguin", "Fox", "Mammoth", "Orca", "Seal", "Celestial"]

def query_influx(flux):
    req = urllib.request.Request(
        "%s/api/v2/query?org=%s" % (INFLUX, ORG),
        data=flux.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")

def parse_csv(result):
    lines = [l for l in result.splitlines() if l and not l.startswith("#")]
    if not lines:
        return []
    header = lines[0].split(",")
    rows = []
    for l in lines[1:]:
        cells = l.split(",")
        row = {}
        for i, h in enumerate(header):
            if i < len(cells):
                row[h] = cells[i]
        rows.append(row)
    return rows

def get_tier(score, targets):
    """根据分数和档位线判断当前档位"""
    for i in range(len(targets) - 1, -1, -1):
        if score >= targets[i]:
            return TIER_NAMES[i] if i < len(TIER_NAMES) else "Max"
    return "Unranked"

def get_next_tier(score, targets):
    """获取下一个档位和差距"""
    for i, t in enumerate(targets):
        if score < t:
            tier_name = TIER_NAMES[i] if i < len(TIER_NAMES) else "Max"
            return tier_name, t - score
    return "Max", 0

def main():
    # 1. 读取 S2 官方分类诊断（获取场景名、分类、档位线）
    with open(DIAG_FILE, "r", encoding="utf-8") as f:
        diag = json.load(f)

    scenarios_data = diag["scenarios"]
    print("S2 基准场景数: %d" % len(scenarios_data))

    # 建立场景名 -> 信息映射
    bench_map = {}
    for s in scenarios_data:
        name = s["name"]
        bench_map[name] = {
            "cat": s.get("cat", ""),
            "sub": s.get("sub", ""),
            "targets": s.get("targets", [])
        }

    # 2. 从 InfluxDB 拉取本次基准测试各场景最高分
    flux = '''from(bucket: "aim")
  |> range(start: 2026-10-08T08:00:00Z, stop: 2026-10-08T12:00:00Z)
  |> filter(fn: (r) => r._measurement == "kovaak_score" and r._field == "score")
  |> keep(columns: ["scenario", "_value"])
  |> max()'''
    result = query_influx(flux)
    rows = parse_csv(result)

    current_scores = {}
    for r in rows:
        scenario = r.get("scenario", "")
        value = r.get("_value", "")
        if scenario and value:
            try:
                current_scores[scenario] = float(value)
            except:
                pass

    print("本次基准有数据的场景数: %d" % len(current_scores))

    # 3. 匹配分析
    matched = []
    unmatched_bench = []
    for scenario_name, bench_info in bench_map.items():
        if scenario_name in current_scores:
            score = current_scores[scenario_name]
            targets = bench_info["targets"]
            tier = get_tier(score, targets)
            next_tier, gap = get_next_tier(score, targets)
            matched.append({
                "scenario": scenario_name,
                "score": score,
                "tier": tier,
                "next_tier": next_tier,
                "gap": gap,
                "cat": bench_info["cat"],
                "sub": bench_info["sub"],
                "targets": targets
            })
        else:
            unmatched_bench.append(scenario_name)

    print("匹配成功的场景数: %d" % len(matched))
    print("基准中有但本次没跑的场景: %d" % len(unmatched_bench))
    if unmatched_bench:
        print("  未跑场景:", ", ".join(unmatched_bench[:10]))

    # 4. 按子类分组
    subclass_results = defaultdict(list)
    for r in matched:
        subclass_results[r["sub"]].append(r)

    # 5. 生成报告
    output = []
    output.append("# VDIM 训练起点基准记录（2026-10-08）")
    output.append("")
    output.append("> 作为 VDIM Novice 训练的起点，2周后（10-20）和4周后（11-03）对比进步")
    output.append("")

    # 全局统计
    all_tiers = [r["tier"] for r in matched]
    tier_counts = defaultdict(int)
    for t in all_tiers:
        tier_counts[t] += 1

    output.append("## 一、全局档位分布")
    output.append("")
    output.append("| 档位 | 场景数 | 占比 |")
    output.append("| --- | --- | --- |")
    for t in TIER_NAMES:
        if t in tier_counts:
            output.append("| %s | %d | %.0f%% |" % (t, tier_counts[t], tier_counts[t] / len(matched) * 100))
    output.append("")
    output.append("**已测基准场景总数**：%d / %d" % (len(matched), len(bench_map)))
    if unmatched_bench:
        output.append("**未跑场景**：%s" % ", ".join(unmatched_bench))
    output.append("")

    # 各子类分析
    output.append("## 二、各子类当前状态")
    output.append("")

    for sub in ["Arm", "Wrist", "Fingertip", "Blending", "Control", "Speed", "Reading", "Stability", "Micro", "Evasive", "Precision", "Linear"]:
        if sub not in subclass_results:
            continue
        results = subclass_results[sub]
        output.append("### %s 子类（%d 个场景）" % (sub, len(results)))
        output.append("")
        output.append("| 场景 | 当前分数 | 当前档位 | 下一档位 | 差距 | 类别 |")
        output.append("| --- | --- | --- | --- | --- | --- |")
        for r in sorted(results, key=lambda x: x["score"], reverse=True):
            output.append("| %s | %.0f | %s | %s | +%.0f | %s |" % (
                r["scenario"], r["score"], r["tier"], r["next_tier"], r["gap"], r["cat"]))
        output.append("")

        # 子类整体评估
        tiers_in_sub = [r["tier"] for r in results]
        sub_tier_counts = defaultdict(int)
        for t in tiers_in_sub:
            sub_tier_counts[t] += 1
        dominant_tier = max(sub_tier_counts, key=sub_tier_counts.get)
        avg_score = sum(r["score"] for r in results) / len(results)
        output.append("**子类整体**：%s（%d/%d 场景），平均 %.0f 分" % (
            dominant_tier, sub_tier_counts[dominant_tier], len(results), avg_score))
        output.append("")

    # VDIM 难度匹配
    output.append("## 三、VDIM 难度匹配分析")
    output.append("")

    ermine_idx = TIER_NAMES.index("Ermine")
    penguin_idx = TIER_NAMES.index("Penguin")
    hare_idx = TIER_NAMES.index("Hare")

    ermine_and_above = sum(1 for t in all_tiers if TIER_NAMES.index(t) >= ermine_idx)
    penguin_and_above = sum(1 for t in all_tiers if TIER_NAMES.index(t) >= penguin_idx)
    hare_and_below = sum(1 for t in all_tiers if TIER_NAMES.index(t) <= hare_idx)

    output.append("### 当前水平分布")
    output.append("- Ermine 及以上：%d/%d（%.0f%%）" % (ermine_and_above, len(matched), ermine_and_above / len(matched) * 100))
    output.append("- Penguin 及以上：%d/%d（%.0f%%）" % (penguin_and_above, len(matched), penguin_and_above / len(matched) * 100))
    output.append("- Hare 及以下：%d/%d（%.0f%%）" % (hare_and_below, len(matched), hare_and_below / len(matched) * 100))
    output.append("")

    output.append("### VDIM 各级别适用范围")
    output.append("| VDIM 级别 | 适用基准水平 | 你的匹配度 |")
    output.append("| --- | --- | --- |")
    output.append("| Entry | Unranked → Bronze | 太低 |")
    output.append("| **Novice** | **Bronze → Gold（Lemming-Ermine）** | **✅ 推荐** |")
    output.append("| Intermediate | Gold → Diamond（Penguin-Fox） | 偏难 |")
    output.append("| Advanced | Diamond → Master | 太高 |")
    output.append("")

    output.append("### 结论")
    output.append("")
    if ermine_and_above / len(matched) >= 0.5:
        output.append("你有超过一半的场景在 Ermine 及以上，整体处于 **Ermine → Penguin** 过渡阶段。")
        output.append("")
        output.append("**推荐使用 VDIM Novice**，等大部分场景稳定到 Penguin 以上再升 Intermediate。")
    elif hare_and_below / len(matched) >= 0.5:
        output.append("你大部分场景在 Hare 及以下，整体处于 **Lemming → Hare** 阶段。")
        output.append("")
        output.append("**强烈推荐使用 VDIM Novice**，先打好基础。")
    else:
        output.append("你的场景分布比较分散，从 Lemming 到 Ermine 都有，整体处于 **Hare → Ermine** 过渡阶段。")
        output.append("")
        output.append("**推荐使用 VDIM Novice**，适合你当前的混合水平。")

    output.append("")
    output.append("### 进阶 Intermediate 的条件")
    output.append("- 70% 以上场景达到 Penguin 及以上")
    output.append("- 没有任何场景低于 Ermine")
    output.append("- VDIM Novice playlist 做起来感觉轻松（不需要频繁暂停）")
    output.append("")

    # 弱项排行
    output.append("## 四、重点关注的弱项（差距最大的场景）")
    output.append("")
    all_sorted = sorted(matched, key=lambda x: x["gap"], reverse=True)
    output.append("| 排名 | 场景 | 当前分数 | 当前档位 | 下一档位 | 差距 | 子类 |")
    output.append("| --- | --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(all_sorted[:15]):
        output.append("| %d | %s | %.0f | %s | %s | +%.0f | %s |" % (
            i + 1, r["scenario"], r["score"], r["tier"], r["next_tier"], r["gap"], r["sub"]))
    output.append("")

    # 强项排行
    output.append("## 五、表现最好的场景")
    output.append("")
    all_sorted_asc = sorted(matched, key=lambda x: x["score"], reverse=True)
    output.append("| 排名 | 场景 | 当前分数 | 当前档位 | 子类 |")
    output.append("| --- | --- | --- | --- | --- |")
    for i, r in enumerate(all_sorted_asc[:10]):
        output.append("| %d | %s | %.0f | %s | %s |" % (
            i + 1, r["scenario"], r["score"], r["tier"], r["sub"]))
    output.append("")

    # 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("\n分析完成，已保存到: %s" % OUTPUT_FILE)
    print("\n=== 快速摘要 ===")
    print("已测基准场景: %d / %d" % (len(matched), len(bench_map)))
    for t in TIER_NAMES:
        if t in tier_counts:
            print("  %s: %d (%.0f%%)" % (t, tier_counts[t], tier_counts[t] / len(matched) * 100))
    print("\nErmine 及以上: %d/%d (%.0f%%)" % (ermine_and_above, len(matched), ermine_and_above / len(matched) * 100))
    print("Penguin 及以上: %d/%d (%.0f%%)" % (penguin_and_above, len(matched), penguin_and_above / len(matched) * 100))

if __name__ == "__main__":
    main()
