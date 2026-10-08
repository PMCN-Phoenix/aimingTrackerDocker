"""
分析 2026-10-08 完整基准测试结果
1. 提取各场景档位线
2. 对比当前分数判断档位
3. 按子类分类汇总
4. 和 VDIM 难度匹配
5. 保存起点记录
"""
import json
import urllib.request
from collections import defaultdict

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
BENCH_FILE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\Viscose基准-原始数据\benches_full.json"
OUTPUT_FILE = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\记录\VDIM起点基准-20261008.md"

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
    tiers = list(targets.items())
    tiers.sort(key=lambda x: x[1])  # 按分数升序
    current_tier = "Unranked"
    for tier_name, tier_score in tiers:
        if score >= tier_score:
            current_tier = tier_name
    return current_tier

def get_next_tier(score, targets):
    """获取下一个档位和差距"""
    tiers = list(targets.items())
    tiers.sort(key=lambda x: x[1])
    for tier_name, tier_score in tiers:
        if score < tier_score:
            return tier_name, tier_score - score
    return "Max", 0

def main():
    # 1. 读取基准档位线
    with open(BENCH_FILE, "r", encoding="utf-8") as f:
        benches = json.load(f)

    easier_scenarios = benches["Easier Scenarios"]["scenarios"]
    print("Easier 基准场景数: %d" % len(easier_scenarios))

    # 建立场景名 -> 档位线映射
    bench_map = {}
    for s in easier_scenarios:
        name = s["scenario"]
        bench_map[name] = {
            "category": s.get("category", ""),
            "sub": s.get("sub", ""),
            "targets": s.get("targets", {})
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

    # 3. 对比分析
    output = []
    output.append("# VDIM 训练起点基准记录（2026-10-08）")
    output.append("")
    output.append("> 作为 VDIM Novice 训练的起点，2周后（10-20）和4周后（11-03）对比进步")
    output.append("")

    # 按子类分组
    subclass_results = defaultdict(list)

    for scenario_name, bench_info in bench_map.items():
        if scenario_name in current_scores:
            score = current_scores[scenario_name]
            targets = bench_info["targets"]
            tier = get_tier(score, targets)
            next_tier, gap = get_next_tier(score, targets)
            category = bench_info["category"]
            sub = bench_info["sub"]

            result = {
                "scenario": scenario_name,
                "score": score,
                "tier": tier,
                "next_tier": next_tier,
                "gap": gap,
                "category": category,
                "sub": sub,
                "targets": targets
            }
            subclass_results[sub].append(result)

    # 4. 输出各子类分析
    output.append("## 一、各子类当前状态")
    output.append("")

    tier_order = ["Unranked", "Lemming", "Hare", "Ermine", "Penguin", "Fox", "Mammoth", "Orca", "Seal"]

    for sub, results in sorted(subclass_results.items()):
        output.append("### %s 子类" % sub)
        output.append("")
        output.append("| 场景 | 当前分数 | 当前档位 | 下一档位 | 差距 | 类别 |")
        output.append("| --- | --- | --- | --- | --- | --- |")
        for r in sorted(results, key=lambda x: x["score"], reverse=True):
            output.append("| %s | %.0f | %s | %s | +%.0f | %s |" % (
                r["scenario"], r["score"], r["tier"], r["next_tier"], r["gap"], r["category"]))
        output.append("")

        # 子类整体评估
        tiers_in_sub = [r["tier"] for r in results]
        tier_counts = defaultdict(int)
        for t in tiers_in_sub:
            tier_counts[t] += 1
        dominant_tier = max(tier_counts, key=tier_counts.get)
        output.append("**子类整体水平**：%s（%d/%d 场景）" % (
            dominant_tier, tier_counts[dominant_tier], len(results)))
        output.append("")

    # 5. 全局统计
    output.append("## 二、全局档位分布")
    output.append("")
    all_tiers = []
    for sub, results in subclass_results.items():
        for r in results:
            all_tiers.append(r["tier"])

    tier_counts = defaultdict(int)
    for t in all_tiers:
        tier_counts[t] += 1

    output.append("| 档位 | 场景数 | 占比 |")
    output.append("| --- | --- | --- |")
    for t in tier_order:
        if t in tier_counts:
            output.append("| %s | %d | %.0f%% |" % (t, tier_counts[t], tier_counts[t] / len(all_tiers) * 100))
    output.append("")
    output.append("**总基准场景数**：%d" % len(all_tiers))
    output.append("")

    # 6. VDIM 难度匹配建议
    output.append("## 三、VDIM 难度匹配分析")
    output.append("")

    # 计算各档位占比
    ermine_and_above = sum(1 for t in all_tiers if tier_order.index(t) >= tier_order.index("Ermine"))
    penguin_and_above = sum(1 for t in all_tiers if tier_order.index(t) >= tier_order.index("Penguin"))
    leming_and_below = sum(1 for t in all_tiers if tier_order.index(t) <= tier_order.index("Lemming"))

    output.append("### 当前水平分布")
    output.append("- Ermine 及以上：%d/%d（%.0f%%）" % (ermine_and_above, len(all_tiers), ermine_and_above / len(all_tiers) * 100))
    output.append("- Penguin 及以上：%d/%d（%.0f%%）" % (penguin_and_above, len(all_tiers), penguin_and_above / len(all_tiers) * 100))
    output.append("- Lemming 及以下：%d/%d（%.0f%%）" % (leming_and_below, len(all_tiers), leming_and_below / len(all_tiers) * 100))
    output.append("")

    output.append("### VDIM 各级别适用范围")
    output.append("| VDIM 级别 | 适用基准水平 | 你的匹配度 |")
    output.append("| --- | --- | --- |")
    output.append("| Entry | Unranked → Bronze | 太低 |")
    output.append("| **Novice** | **Bronze → Gold（Ermine 附近）** | **✅ 推荐** |")
    output.append("| Intermediate | Gold → Diamond（Penguin-Fox） | 偏难，部分场景可挑战 |")
    output.append("| Advanced | Diamond → Master | 太高 |")
    output.append("")

    output.append("### 结论与建议")
    output.append("")
    if ermine_and_above / len(all_tiers) >= 0.5:
        output.append("你有超过一半的场景在 Ermine 及以上，整体处于 **Ermine → Penguin** 过渡阶段。")
        output.append("")
        output.append("**推荐使用 VDIM Novice**，原因：")
        output.append("1. 仍有部分场景在 Lemming/Hare 水平，基础需要巩固")
        output.append("2. Novice 的场景难度适合你当前水平，能保证动作质量")
        output.append("3. 等大部分场景稳定到 Penguin 以上，再升 Intermediate")
        output.append("")
        output.append("**进阶 Intermediate 的条件**：")
        output.append("- 70% 以上场景达到 Penguin 及以上")
        output.append("- 没有任何场景低于 Ermine")
        output.append("- VDIM Novice playlist 做起来感觉轻松（不需要频繁暂停）")
    else:
        output.append("你大部分场景在 Ermine 以下，整体处于 **Hare → Ermine** 阶段。")
        output.append("")
        output.append("**强烈推荐使用 VDIM Novice**，先打好基础。")

    output.append("")
    output.append("### 重点关注的弱项（差距最大的场景）")
    output.append("")
    all_results = []
    for sub, results in subclass_results.items():
        all_results.extend(results)
    all_results.sort(key=lambda x: x["gap"], reverse=True)

    output.append("| 排名 | 场景 | 当前分数 | 当前档位 | 下一档位 | 差距 | 子类 |")
    output.append("| --- | --- | --- | --- | --- | --- | --- |")
    for i, r in enumerate(all_results[:10]):
        output.append("| %d | %s | %.0f | %s | %s | +%.0f | %s |" % (
            i + 1, r["scenario"], r["score"], r["tier"], r["next_tier"], r["gap"], r["sub"]))
    output.append("")

    # 7. 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("\n分析完成，已保存到: %s" % OUTPUT_FILE)
    print("\n=== 快速摘要 ===")
    print("总基准场景数: %d" % len(all_tiers))
    for t in tier_order:
        if t in tier_counts:
            print("  %s: %d" % (t, tier_counts[t]))
    print("\nErmine 及以上: %d/%d (%.0f%%)" % (ermine_and_above, len(all_tiers), ermine_and_above / len(all_tiers) * 100))

if __name__ == "__main__":
    main()
