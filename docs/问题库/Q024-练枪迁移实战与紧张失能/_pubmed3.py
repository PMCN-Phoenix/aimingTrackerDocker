# -*- coding: utf-8 -*-
"""PubMed 第三批摘要：Q024 核心机制文献（Baumeister 原始 / 意识加工 / 内焦点 / 认知隧道 / 迁移）"""
import os, re, time, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")

ALL = [
    "6707866",   # Baumeister 1984: self-consciousness & paradoxical effects of incentives
    "11055814",  # State anxiety and motor performance: conscious processing hypothesis
    "32909081",  # Internal focus instruction increases stress with conscious motor processing
    "20425657",  # Thoughts and attention of athletes under pressure: skill-focus or worries
    "26265344",  # Movement-specific reinvestment and performance in demanding contexts
    "37665924",  # Reinvestment in one-on-one in-field vs shoot-out field hockey
    "11765737",  # Automaticity of complex motor skill learning as function of attentional focus
    "21684618",  # Monetary reward/punishment on psychological, physiological, behavioral performance
    "32116972",  # 3D-MOT training on near, mid and far transfer
    "30652908",  # near- and far-transfer meta-analysis
    "9138624",   # Psychosocial influences on central and peripheral vision under demand
    "6844068",   # Cognitive tunneling: use of visual information under stress
]


def efetch(ids):
    for attempt in range(4):
        try:
            r = requests.get(B + "efetch.fcgi", params={"db": "pubmed", "id": ",".join(ids),
                             "retmode": "text", "rettype": "abstract"}, proxies=P, timeout=60)
            if r.status_code == 200 and len(r.text) > 200:
                return r.text
            print("  空返回，重试")
        except Exception as e:
            print(f"  ERR({attempt+1}) {type(e).__name__}")
        time.sleep(4)
    return ""


chunks = []
for i in range(0, len(ALL), 3):
    part = ALL[i:i + 3]
    print(f"fetch {part}")
    t = efetch(part)
    if t:
        chunks.append(t)

text = "\n\n" + ("\n\n" + "=" * 78 + "\n\n").join(chunks)
with open(os.path.join(OUT, "pubmed摘要-补充.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print(f"\n总字符 {len(text)}  疑似条目 {len(re.findall(r'^\d+\.\s', text, re.M))}")
