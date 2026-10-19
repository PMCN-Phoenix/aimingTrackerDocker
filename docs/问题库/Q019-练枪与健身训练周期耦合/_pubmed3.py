# -*- coding: utf-8 -*-
"""Q019 第三轮：运动作为技能学习的启动/巩固器"""
import urllib.request, urllib.parse, json, time, io, os

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = [
    ('Q 急性运动与运动记忆巩固', '(acute exercise[tiab]) AND ("motor memory"[tiab] OR "motor skill learning"[tiab] OR "motor learning"[tiab])'),
    ('R 运动启动技能学习', '(exercise[tiab]) AND (priming[tiab] OR "warm-up"[tiab]) AND ("skill learning"[tiab] OR "motor performance"[tiab])'),
    ('S 高强度间歇与认知', '"high-intensity interval"[tiab] AND ("cognitive"[tiab] OR "executive function"[tiab] OR "reaction time"[tiab])'),
    ('T 有氧运动与记忆 meta', '(exercise[tiab]) AND (memory[tiab]) AND "meta-analysis"[pt]'),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(2)

out = []
for label, term in QUERIES:
    u = E + "esearch.fcgi?db=pubmed&retmode=json&retmax=5&term=" + urllib.parse.quote(term)
    raw = get(u)
    if not raw:
        continue
    ids = json.loads(raw).get("esearchresult", {}).get("idlist", [])
    print(f"[{label}] {len(ids)}")
    if not ids:
        continue
    su = E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)
    raw2 = get(su)
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
        print("   -", title[:90], "|", year)
    out.append("\n".join(block) + "\n")
    time.sleep(0.5)

path = os.path.join(os.path.dirname(__file__), "英文社区与学术原始数据.md")
with io.open(path, "a", encoding="utf-8") as f:
    f.write("\n---\n\n# 第三轮（运动作为技能学习启动器）\n" + "\n".join(out))
print("ok")
