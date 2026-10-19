# -*- coding: utf-8 -*-
"""Q019 PubMed 第二轮：恢复时程/顺序效应/急性反应时/晚间训练与睡眠"""
import urllib.request, urllib.parse, json, time, io, os, sys

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
QUERIES = [
    ('I 抗阻训练后神经肌肉恢复时程', '"neuromuscular fatigue"[tiab] AND ("resistance exercise"[tiab] OR "resistance training"[tiab]) AND (recovery[tiab] OR "time course"[tiab])'),
    ('J 同期训练顺序效应', '("exercise order"[tiab] OR sequencing[tiab]) AND ("resistance training"[tiab] OR strength[tiab]) AND (endurance[tiab] OR aerobic[tiab])'),
    ('K 急性抗阻运动与反应时', '("acute resistance exercise"[tiab] OR "acute strength exercise"[tiab]) AND ("reaction time"[tiab] OR "choice reaction"[tiab] OR "cognitive"[tiab])'),
    ('L 晚间力量训练与睡眠', '("evening"[tiab] OR "night"[tiab]) AND ("resistance exercise"[tiab] OR "strength training"[tiab]) AND ("sleep quality"[tiab] OR "sleep architecture"[tiab] OR "sleep latency"[tiab])'),
    ('M 握力与电竞/游戏玩家', '("handgrip strength"[tiab] OR "grip strength"[tiab]) AND (esports[tiab] OR "video game*"[tiab] OR gamer*[tiab])'),
    ('N 离心运动与上肢精细控制', ('eccentric[tiab] AND ("upper limb"[tiab] OR "elbow flexors"[tiab] OR forearm[tiab]) AND ("motor control"[tiab] OR "force control"[tiab] OR precision[tiab])')),
    ('O 运动诱导肌肉损伤与运动表现', '"exercise-induced muscle damage"[tiab] AND ("sport-specific"[tiab] OR "skill performance"[tiab] OR "motor skill"[tiab])'),
    ('P 抗阻训练与睡眠质量', '"resistance training"[tiab] AND ("sleep quality"[tiab] OR insomnia[tiab]) AND ("meta-analysis"[pt] OR "systematic review"[pt])'),
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
        out.append(f"\n## {label}\n检索失败\n"); print(f"[{label}] 失败"); continue
    ids = json.loads(raw).get("esearchresult", {}).get("idlist", [])
    print(f"[{label}] {len(ids)} 篇")
    if not ids:
        out.append(f"\n## {label}\n（无结果）\n"); continue
    time.sleep(0.4)
    su = E + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids)
    raw2 = get(su)
    if not raw2:
        out.append(f"\n## {label}\n摘要获取失败 ids={ids}\n"); continue
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
    time.sleep(0.4)

path = os.path.join(os.path.dirname(__file__), "英文社区与学术原始数据.md")
with io.open(path, "a", encoding="utf-8") as f:
    f.write("\n---\n\n# 第二轮定向检索（恢复时程/顺序/急性反应/睡眠）\n" + "\n".join(out))
print("appended")
