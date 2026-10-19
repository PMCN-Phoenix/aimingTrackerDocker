# -*- coding: utf-8 -*-
"""Q019 关键文献摘要抓取"""
import urllib.request, urllib.parse, time, io, os

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PMIDS = [
    ("42666305", "电竞选手运动干预与多维认知：RCT 系统综述+meta"),
    ("42174296", "急性/长期运动对电竞表现：系统综述"),
    ("42827798", "电竞选手有氧能力、力量与认知表现"),
    ("34357937", "运动诱导肌肉损伤对板球专项运动技能的影响"),
    ("42866183", "精英运动员同期训练中的高强度抗阻：系统综述"),
    ("41750194", "神经肌肉疲劳与手部灵巧度的关系"),
    ("41900950", "向心 vs 离心疲劳对上肢本体感觉与动作控制"),
    ("41168935", "急性抗阻运动改善执行功能（行为+神经电）"),
    ("38322615", "晚间抗阻/耐力运动对睡眠脑电与皮质醇"),
    ("42881562", "Timing Matters：抗阻训练中与训练后的疲劳评估"),
    ("42759564", "同期高强度间歇+力量训练对肌肉功能与有氧能力"),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(2)

blocks = ["\n---\n\n# 关键文献摘要（efetch 原文摘要，便于核对口径）\n"]
for pid, label in PMIDS:
    u = E + "efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=" + pid
    t = get(u)
    if not t:
        blocks.append(f"\n## {label}（PMID {pid}）\n抓取失败\n")
        print(f"[{pid}] 失败")
        continue
    t = t.strip()
    blocks.append(f"\n## {label}（PMID {pid}）\n\n```\n{t}\n```\n")
    print(f"[{pid}] ok ({len(t)}字)")
    time.sleep(0.5)

path = os.path.join(os.path.dirname(__file__), "英文社区与学术原始数据.md")
with io.open(path, "a", encoding="utf-8") as f:
    f.write("\n".join(blocks))
print("appended abstracts")
