#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B 看板数据物化器（aim_bench_row / aim_bench_meta）
==================================================
看板 B 的「格子填色总表」需要一行一个场景、同时带 9 档达标线 + 当前分 + 已达档数。
用 Flux 现算需要复杂 pivot（易踩坑），所以采用**物化视图**模式：
  读「档位线定义（S2-成绩诊断.json）+ 清单分组（scenario_lists.json）+ 最新成绩（InfluxDB）」
  → 写入 InfluxDB：
    - aim_bench_row  : 一行一个场景（tags: list/scenario/cat/sub/rank/subRank；fields: score/pct/achIdx/gapPct/t1..t9）
    - aim_bench_meta : 一行一份清单的汇总（fields: ranked/unranked/total/lowestSubIdx/stuckSubs/avgGap）

时间戳 = 本次同步时刻（重跑覆盖写，天然幂等）。

用法:
  python bench_rows.py            # 物化并写库
  python bench_rows.py --show     # 只打印，不写库
"""
import sys
import os
import json
import io
import csv
import urllib.request
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
LISTS = os.path.join(BASE, "scenario_lists.json")
DIAG = os.path.join(BASE, "docs", "清单", "Viscose基准-原始数据", "S2-成绩诊断.json")

INFLUX = "http://127.0.0.1:8087"
ORG, BUCKET = "aim-org", "aim"
TOKEN = "aim-super-secret-token-2026"
TIERS = ["Lemming", "Hare", "Ermine", "Puffin", "Penguin", "Fox", "Mammoth", "Orca", "Seal"]


def parse_csv(body):
    rows, header = [], None
    for line in body.replace("\r", "").split("\n"):
        if not line or line.startswith("#"):
            continue
        cells = next(csv.reader([line]))
        if cells and cells[0] == "":
            cells = cells[1:]
        if len(cells) > 2 and cells[2] == "_time":
            header = cells
            continue
        if header is None:
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def flux(script):
    req = urllib.request.Request("%s/api/v2/query?org=%s" % (INFLUX, ORG),
                                data=script.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    return parse_csv(body)


def delete_measurement(name):
    """清空物化表的旧数据（同一 measurement，无 OR 谓词）。每次同步 = 清空 + 重写，保证幂等。"""
    req = urllib.request.Request(
        "%s/api/v2/delete?org=%s&bucket=%s" % (INFLUX, ORG, BUCKET),
        data=json.dumps({"start": "1970-01-01T00:00:00Z", "stop": "2030-01-01T00:00:00Z",
                         "predicate": '_measurement="%s"' % name}).encode("utf-8"),
        method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status not in (204, 200):
            raise RuntimeError("delete HTTP %s" % r.status)


def write(lines):
    if not lines:
        return
    req = urllib.request.Request(
        "%s/api/v2/write?org=%s&bucket=%s&precision=s" % (INFLUX, ORG, BUCKET),
        data="\n".join(lines).encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 204:
            raise RuntimeError("InfluxDB write HTTP %s" % r.status)


def esc(s):
    return str(s).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def main():
    cfg = json.load(open(LISTS, encoding="utf-8"))["lists"]["viscose-s2-easier"]
    diag = {r["name"]: r for r in json.load(open(DIAG, encoding="utf-8-sig"))}
    subrank = cfg.get("subrank", {})
    groups = cfg["groups"]

    # 场景 → (大类, 子类)
    where = {}
    for cat, subs in groups.items():
        for sub, scenes in subs.items():
            for s in scenes:
                where[s] = (cat, sub)

    # 最新成绩（一次查询全部 S2 场景）
    rows = flux('from(bucket: "aim") |> range(start: -30d) '
                '|> filter(fn: (r) => r._measurement == "aim_scenario" '
                'and (r._field == "score" or r._field == "accuracy") '
                'and r.list == "viscose-s2-easier") '
                '|> keep(columns: ["_time", "_value", "_field", "scenario"])')
    # 基准榜按【最佳分】记（同一次 run 的 score/accuracy 共享时间戳）
    pts = {}
    for r in rows:
        pts.setdefault((r["scenario"], r["_time"]), {})[r["_field"]] = float(r["_value"])
    best = {}
    for (sc, t), v in pts.items():
        if "score" not in v:
            continue
        if sc not in best or v["score"] > best[sc][0]:
            best[sc] = (v["score"], t, v.get("accuracy"))
    latest = {sc: (s, t) for sc, (s, t, _a) in best.items()}
    latest_acc = {sc: (a, t) for sc, (_s, t, a) in best.items() if a is not None}
    best_date = {sc: t[:10] for sc, (_s, t, _a) in best.items()}

    now = int(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).timestamp())
    lines, table = [], []
    ranked = unranked = 0
    gaps = []

    # 官方顺序：大类 → 子类 → 场景（JSON 里 dict 保序）
    order_map, i = {}, 0
    for cat, subs in groups.items():
        for sub, scenes in subs.items():
            for sc in scenes:
                i += 1
                order_map[sc] = i

    # ── 第一遍：算每个场景已达档数，再由「子类里最高场景」定子类档位 ──
    # （evxl 判档算法，09-17 用 9/16 静态数据回测 14/14 一致：
    #   子类档位 = 该子类中分数最高场景达到的档位；总档位 = 14 个子类里最低的那档）
    ach_of, sub_ach = {}, {}
    for scene, d in diag.items():
        cat, sub = where.get(scene, ("UNKNOWN", "UNKNOWN"))
        score = latest.get(scene, (d["score"], ""))[0]
        a = len([t for t in d["targets"] if score >= t])
        ach_of[scene] = a
        if a > sub_ach.get(sub, -1):
            sub_ach[sub] = a
    sub_rank = {s: (TIERS[a - 1] if a > 0 else "Unranked") for s, a in sub_ach.items()}
    lowest = min([TIERS.index(r) if r in TIERS else -1 for r in sub_rank.values()] or [-1])
    stuck_names = sorted([s for s, r in sub_rank.items() if (TIERS.index(r) if r in TIERS else -1) == lowest])

    for scene, d in sorted(diag.items()):
        cat, sub = where.get(scene, ("UNKNOWN", "UNKNOWN"))
        targets = d["targets"]
        score = latest.get(scene, (d["score"], ""))[0]
        ach = ach_of[scene]                                    # 已达档数
        full = ach >= len(targets)
        cur_line = targets[ach - 1] if ach > 0 else 0
        next_line = targets[ach] if not full else targets[-1]
        pct = 100.0 if full else round((score - cur_line) / (next_line - cur_line) * 100, 1)
        gap = 0.0 if full else round((next_line - score) / next_line * 100, 1)
        rank = TIERS[ach - 1] if ach > 0 else "Unranked"
        if rank == "Unranked":
            unranked += 1
        else:
            ranked += 1
        sr_rank = sub_rank.get(sub, "Unranked")
        sr_idx = TIERS.index(sr_rank) if sr_rank in TIERS else -1
        gaps.append(gap)

        fields = ["score=%g" % score, "pct=%g" % pct, "achIdx=%di" % ach, "gapPct=%g" % gap,
                  "subRankIdx=%di" % sr_idx, "nextLine=%g" % next_line]
        fields += ["t%d=%g" % (i + 1, t) for i, t in enumerate(targets)]
        # 整行打包成 JSON 字符串：给自绘面板用（避免 Grafana 把 tag 列拆成多帧 / pivot 参数被当正则）
        row = {"scenario": scene, "cat": cat, "sub": sub, "ord": order_map.get(scene, 999),
               "rank": rank, "subRank": sr_rank, "subPct": subrank.get("%s|%s" % (cat, sub), {}).get("pct"),
               "score": score, "acc": (latest_acc.get(scene, (None, ""))[0]), "pct": pct,
               "bestDate": best_date.get(scene, ""),
               "achIdx": ach, "gapPct": gap, "targets": targets, "full": full}
        js = json.dumps(row, ensure_ascii=False).replace("\\", "\\\\").replace('"', '\\"')
        fields.append('rowJson="%s"' % js)
        lines.append("aim_bench_row,list=viscose-s2-easier,scenario=%s,cat=%s,sub=%s,rank=%s,subRank=%s %s %d"
                     % (esc(scene), esc(cat), esc(sub), esc(rank), esc(sr_rank),
                        ",".join(fields), now))
        table.append((cat, sub, scene, score, rank, next_line, gap))

    stuck = len(stuck_names)
    avg_gap = round(sum(gaps) / len(gaps), 1) if gaps else 0.0

    # meta 附带：档位分布计数（供分布图直接出 9 根柱子）+ 文本字段（供统计卡显示）
    tier_count = {t: 0 for t in TIERS}
    tier_count["Unranked"] = unranked
    for cat, sub, scene, score, rank, nl, gap in table:
        if rank in tier_count:
            tier_count[rank] += 1
    counts = ",".join("%s=%di" % ("c" + t, tier_count.get(t, 0)) for t in TIERS)
    stuck_text = " / ".join(stuck_names) if stuck_names else "无"
    lines.append("aim_bench_meta,list=viscose-s2-easier,stuck=\"%s\" ranked=%di,unranked=%di,total=%di,"
                 "lowestSubIdx=%di,stuckSubs=%di,avgGap=%g,rankedText=\"%d / %d\",stuckText=\"%s\",%s %d"
                 % (esc(stuck_text.replace('"', "")), ranked, unranked, ranked + unranked,
                    lowest, stuck, avg_gap, ranked, ranked + unranked,
                    stuck_text.replace('"', ""), counts, now))

    if "--show" in sys.argv:
        for cat, sub, scene, score, rank, nl, gap in table:
            print("%-18s %-12s %-46s %10g %-9s 下一档 %-9g 差 %5.1f%%" % (cat, sub, scene, score, rank, nl, gap))
        print("\n汇总: 已上榜 %d / 未上榜 %d / 总 %d / 最低子类档位序号 %d / 卡住子类 %d 个 / 平均离下一档 %.1f%%"
              % (ranked, unranked, ranked + unranked, lowest, stuck, avg_gap))
        return

    delete_measurement("aim_bench_row")
    delete_measurement("aim_bench_meta")
    write(lines)
    print(json.dumps({"ok": True, "rows": len(table), "ranked": ranked, "unranked": unranked,
                      "lowestSubIdx": lowest, "stuckSubs": stuck, "avgGap": avg_gap,
                      "written": len(lines)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
