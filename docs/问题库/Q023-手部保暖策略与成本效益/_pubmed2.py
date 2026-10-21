# -*- coding: utf-8 -*-
"""Q023 PubMed 第二轮：经典文献精准回源（冷→灵巧度阈值 / 局部加温 / 手套触觉）"""
import urllib.request, urllib.parse, json, time, io, os

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = [
    ('K1 Havenith 冷与手动性能', 'Havenith G[au] AND (cold[tiab] OR "manual performance"[tiab] OR dexterity[tiab])'),
    ('K2 手指温度与灵巧度阈值', '("finger skin temperature"[tiab] OR "finger temperature"[tiab]) AND ("dexterity"[tiab] OR "manual performance"[tiab]) AND (threshold*[tiab] OR "15"[tiab] OR "cut-off"[tiab])'),
    ('K3 手部冷却与触觉敏感度', '("hand cooling"[tiab] OR "finger cooling"[tiab]) AND ("tactile"[tiab] OR "sensation"[tiab] OR "sensitivity"[tiab])'),
    ('K4 冷环境办公/打字表现', '("cold"[tiab] OR "cool"[tiab]) AND ("office"[tiab] OR "indoor"[tiab]) AND ("performance"[tiab] OR "productivity"[tiab] OR "typing"[tiab]) AND (temperature[tiab])'),
    ('K5 手指冷诱导血管扩张 CIVD', '("cold-induced vasodilation"[tiab] OR CIVD[tiab]) AND (finger[tiab] OR hand[tiab])'),
    ('K6 局部加热与手指血流', '("local heating"[tiab] OR "localised heating"[tiab] OR "localized heating"[tiab]) AND ("finger"[tiab] OR "hand"[tiab]) AND ("blood flow"[tiab] OR "skin temperature"[tiab])'),
    ('K7 手套与触觉反馈', '("glove*"[tiab]) AND ("tactile feedback"[tiab] OR "force control"[tiab] OR "grip force"[tiab]) AND ("performance"[tiab] OR "precision"[tiab])'),
    ('K8 冷应激与反应时', '("cold stress"[tiab] OR "cold exposure"[tiab]) AND ("reaction time"[tiab] OR "psychomotor"[tiab]) AND (hand[tiab] OR finger[tiab] OR "upper limb"[tiab])'),
    ('K9 手部加温与运动表现', '("hand warming"[tiab] OR "hand heating"[tiab] OR "palm heating"[tiab]) AND ("performance"[tiab] OR "strength"[tiab] OR "fatigue"[tiab])'),
    ('K10 冷手与精细操作职业人群', '("fine motor"[tiab] OR "manual dexterity"[tiab]) AND ("cold"[tiab] OR "low temperature"[tiab]) AND ("workers"[tiab] OR "occupational"[tiab] OR "musicians"[tiab] OR "surgeons"[tiab])'),
    ('K11 体感温度与热舒适区间', '("thermal comfort"[tiab]) AND ("indoor temperature"[tiab] OR "operative temperature"[tiab]) AND (performance[tiab] OR "cognitive"[tiab])'),
    ('K12 冷手指温度与力量控制', '("finger"[tiab] AND "temperature"[tiab]) AND ("force"[tiab] OR "grip"[tiab]) AND ("variability"[tiab] OR "steadiness"[tiab] OR "tremor"[tiab])'),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                print("   fail:", str(e)[:70])
                return None
            time.sleep(2)

out = []
total = 0
for label, term in QUERIES:
    u = E + "esearch.fcgi?db=pubmed&retmode=json&retmax=5&sort=relevance&term=" + urllib.parse.quote(term)
    raw = get(u)
    if not raw:
        out.append(f"\n## {label}\n检索失败\n")
        continue
    ids = json.loads(raw).get("esearchresult", {}).get("idlist", [])
    print(f"[{label}] {len(ids)} 篇")
    if not ids:
        out.append(f"\n## {label}\n（无结果）\n")
        continue
    time.sleep(0.4)
    raw2 = get(E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids))
    if not raw2:
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
path = os.path.join(os.path.dirname(__file__), "学术题录第二轮-经典回源.md")
header = """# Q023 学术题录第二轮（经典文献精准回源）

> 采集：2026-10-21 ｜ 渠道：NCBI E-utilities（sort=relevance）
> 目的：第一轮检索式过宽（混入大量无关 2026 新文），本轮按作者/阈值/机制词精准回源
> 重点：Havenith 冷-手动性能系列、手指温度-灵巧度阈值、CIVD、局部加热-血流、手套-触觉反馈

"""
with io.open(path, "w", encoding="utf-8") as f:
    f.write(header + txt)
print("saved:", path)
