# -*- coding: utf-8 -*-
"""PubMed 检索：练习频率 / 分散练习 / 技能保持 / 停练衰退 / 电竞过度训练"""
import os, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

qs = {
    "distributed_practice": "distributed practice versus massed practice motor skill learning retention",
    "spacing_effect": "spacing effect practice schedule skill acquisition",
    "detraining_motor": "detraining motor skill retention cessation of practice",
    "warmup_decrement": "warm-up decrement motor skill performance after rest",
    "consolidation_sleep": "sleep dependent motor skill consolidation practice",
    "esports_load": "esports training load overtraining burnout players",
    "esports_injury": "esports players practice hours musculoskeletal pain",
    "transfer_specificity": "specificity of practice transfer motor learning game",
    "contextual_interference": "contextual interference effect motor learning",
    "overtraining_cognitive": "cognitive fatigue prolonged cognitive work decision making",
}

for k, q in qs.items():
    try:
        r = requests.get(B + "esearch.fcgi",
                         params={"db": "pubmed", "term": q, "retmax": 5,
                                 "retmode": "json", "sort": "relevance"},
                         proxies=P, timeout=45).json()
        ids = r["esearchresult"]["idlist"]
        print(f"\n## {k}  ({q}) -> {len(ids)}")
        if not ids:
            continue
        s = requests.get(B + "esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
                         proxies=P, timeout=45).json()
        for i in ids:
            d = s["result"].get(i, {})
            print("  %s | %s | %s | %s" % (i, d.get("pubdate", ""),
                                           d.get("source", ""), d.get("title", "")[:120]))
    except Exception as e:
        print(f"## {k} ERR {e}")
