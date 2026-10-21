# -*- coding: utf-8 -*-
"""Q023 PubMed E-utilities 检索：手部温度 → 精细运动表现 / 局部加温效应"""
import urllib.request, urllib.parse, json, time, io, os, sys

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = [
    ('A 手温与精细运动', '("hand"[tiab] OR "finger"[tiab]) AND ("skin temperature"[tiab] OR "local cooling"[tiab] OR "cold exposure"[tiab]) AND ("manual dexterity"[tiab] OR "fine motor"[tiab] OR "motor performance"[tiab])'),
    ('B 冷暴露与灵巧度', '("cold"[tiab] OR "cooling"[tiab]) AND ("hand"[tiab] OR "finger"[tiab]) AND ("dexterity"[tiab] OR "tactile"[tiab] OR "sensory"[tiab]) AND performance[tiab]'),
    ('C 局部加温与血流', '("local heating"[tiab] OR "passive heating"[tiab] OR "hand warming"[tiab]) AND ("blood flow"[tiab] OR "skin blood flow"[tiab] OR "nerve conduction"[tiab])'),
    ('D 手温与反应时', '("hand temperature"[tiab] OR "finger temperature"[tiab]) AND ("reaction time"[tiab] OR "response time"[tiab] OR "cognitive performance"[tiab])'),
    ('E 加温与握力/力量', '("muscle temperature"[tiab] OR "warm-up"[tiab] OR "heat application"[tiab]) AND ("grip strength"[tiab] OR "force production"[tiab] OR "muscle performance"[tiab])'),
    ('F 冷手与震颤', '("cold hands"[tiab] OR "finger cooling"[tiab]) AND ("tremor"[tiab] OR "steadiness"[tiab] OR "force fluctuation"[tiab])'),
    ('G 手温与游戏/电竞', '(esport*[tiab] OR "video game*"[tiab] OR "gaming"[tiab]) AND (temperature[tiab] OR "cold hands"[tiab] OR warming[tiab])'),
    ('H 局部冷热与神经肌肉', '("thermal"[tiab] OR "temperature"[tiab]) AND ("neuromuscular"[tiab] OR "motor unit"[tiab] OR "muscle activation"[tiab]) AND (hand[tiab] OR forearm[tiab])'),
    ('I 手套与操作表现', '("glove*"[tiab]) AND ("dexterity"[tiab] OR "manual performance"[tiab] OR "hand function"[tiab])'),
    ('J 冷环境与认知运动', '("cold environment"[tiab] OR "cold ambient"[tiab]) AND ("cognitive performance"[tiab] OR "motor performance"[tiab] OR "fine motor skill*"[tiab])'),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                print("   fail:", str(e)[:80])
                return None
            time.sleep(2)

out = []
total = 0
for label, term in QUERIES:
    u = E + "esearch.fcgi?db=pubmed&retmode=json&retmax=6&term=" + urllib.parse.quote(term)
    raw = get(u)
    if not raw:
        out.append(f"\n## {label}\n检索失败\n")
        print(f"[{label}] 检索失败")
        continue
    ids = json.loads(raw).get("esearchresult", {}).get("idlist", [])
    print(f"[{label}] {len(ids)} 篇")
    if not ids:
        out.append(f"\n## {label}\n（无结果）\n")
        continue
    time.sleep(0.4)
    su = E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)
    raw2 = get(su)
    if not raw2:
        out.append(f"\n## {label}\n摘要获取失败 ids={ids}\n")
        continue
    res = json.loads(raw2).get("result", {})
    block = [f"\n## {label}\n", f"> 检索式：`{term}`\n"]
    for pid in ids:
        it = res.get(pid, {})
        title = it.get("title", "")
        journal = it.get("fulljournalname") or it.get("source", "")
        year = (it.get("pubdate") or "")[:4]
        authors = ", ".join(a.get("name", "") for a in (it.get("authors") or [])[:3])
        block.append(f"- **{title}**（{authors}｜{journal} {year}｜PMID {pid}）")
        print("   -", title[:95], "|", year)
        total += 1
    out.append("\n".join(block) + "\n")
    time.sleep(0.4)

print("\n题录合计:", total)
txt = "\n".join(out)
path = os.path.join(os.path.dirname(__file__), "学术题录原始数据.md")
header = """# Q023 学术题录原始数据（PubMed E-utilities）

> 采集：2026-10-21 ｜ 渠道：NCBI E-utilities 官方 API（esearch + esummary）
> 主题：手部温度 ↔ 精细运动/灵巧度/反应时；局部加温 ↔ 血流/神经传导/力量；手套 ↔ 操作表现
> 说明：题录为 API 真实返回，未做二手转述。

"""
with io.open(path, "w", encoding="utf-8") as f:
    f.write(header + txt)
print("saved:", path)
