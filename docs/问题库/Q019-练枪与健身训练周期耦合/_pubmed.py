# -*- coding: utf-8 -*-
"""Q019 PubMed E-utilities 检索（绕过网页 cookie 墙）"""
import urllib.request, urllib.parse, json, time, io, os, sys

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = [
    ('A 肌肉疲劳与手部稳定', '"muscle fatigue"[MeSH] AND ("hand"[tiab] OR "steadiness"[tiab] OR "tremor"[tiab])'),
    ('B 抗阻训练与精细动作', '("resistance training"[MeSH] OR "resistance exercise"[tiab]) AND ("fine motor"[tiab] OR "manual dexterity"[tiab] OR "motor control"[tiab])'),
    ('C 电竞与身体活动', '(esports[tiab] OR "electronic sports"[tiab] OR "video game*"[tiab]) AND ("physical activity"[tiab] OR exercise[tiab] OR "strength training"[tiab]) AND (cognition[tiab] OR "reaction time"[tiab] OR performance[tiab])'),
    ('D 同期训练干扰效应', '"concurrent training"[tiab] AND ("interference effect"[tiab] OR strength[tiab])'),
    ('E DOMS 与动作表现', '"delayed onset muscle soreness"[tiab] AND ("reaction time"[tiab] OR "motor performance"[tiab] OR "motor control"[tiab])'),
    ('F PAP 后激活增强', '"post-activation potentiation"[tiab] AND ("reaction time"[tiab] OR "cognitive"[tiab] OR "motor performance"[tiab])'),
    ('G 运动与认知执行功能', '(acute exercise[tiab] OR "resistance exercise"[tiab]) AND ("executive function"[tiab] OR "cognitive performance"[tiab]) AND "meta-analysis"[pt]'),
    ('H 握力与神经肌肉疲劳', '"grip strength"[tiab] AND ("neuromuscular fatigue"[tiab] OR "central fatigue"[tiab])'),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(2)

out = []
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
    out.append("\n".join(block) + "\n")
    time.sleep(0.4)

txt = "\n".join(out)
path = os.path.join(os.path.dirname(__file__), "英文社区与学术原始数据.md")
header = """# Q019 英文社区与学术原始数据

> 采集：2026-10-19 ｜ 渠道：PubMed E-utilities（学术）+ B站/英文社区补充
> 说明：本次 WebSearch 接口故障（fetch failed，与 Q014 期间同类），英文社区侧改用定点源；学术侧走 NCBI 官方 API 直取，题录为真实返回，未做二手转述。

"""
sys.stdout.buffer.write((header + txt).encode("utf-8"))
with io.open(path, "w", encoding="utf-8") as f:
    f.write(header + txt)
print("\nsaved:", path)
