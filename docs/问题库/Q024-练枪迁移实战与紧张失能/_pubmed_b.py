# -*- coding: utf-8 -*-
"""PubMed 补检索：Q024 第一轮漏掉的方向（reinvestment / 自我聚焦 / 特定性假说 / 社会评价下的肌肉活动）"""
import os, json, requests, time
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")

QS = {
    "reinvestment_masters": "reinvestment movement specific conscious processing sport",
    "conscious_processing": "conscious processing hypothesis skill performance",
    "explicit_monitoring": "explicit monitoring skilled motor performance breakdown",
    "self_focus_choking": "self-focus attention choking sport expert",
    "specificity_learning": "specificity of learning hypothesis motor transfer",
    "social_evaluation_emg": "social evaluative threat muscle activity tremor performance",
    "tremor_anxiety": "physiological tremor anxiety precision aiming",
    "evaluation_apprehension": "evaluation apprehension fine motor accuracy",
    "pressure_decrement": "pressure induced performance decrement incentive",
    "near_transfer_far": "near transfer far transfer training specificity",
    "dual_task_pressure": "dual task training protects choking pressure",
    "esports_anxiety_hr": "esports competitive anxiety heart rate variability",
    "grip_force_anxiety": "grip force anxiety precision task",
    "attention_narrowing": "attention narrowing arousal peripheral vision",
}

out = {}
for k, q in QS.items():
    for attempt in range(3):
        try:
            r = requests.get(B + "esearch.fcgi", params={"db": "pubmed", "term": q, "retmax": 6,
                             "retmode": "json", "sort": "relevance"}, proxies=P, timeout=45).json()
            ids = r["esearchresult"]["idlist"]
            out[k] = {"query": q, "count": r["esearchresult"].get("count"), "items": []}
            print(f"\n## {k} -> {out[k]['count']}")
            if ids:
                sm = requests.get(B + "esummary.fcgi", params={"db": "pubmed", "id": ",".join(ids),
                                  "retmode": "json"}, proxies=P, timeout=45).json()
                for i in ids:
                    d = sm["result"].get(i, {})
                    out[k]["items"].append({"pmid": i, "date": d.get("pubdate", ""),
                                            "journal": d.get("source", ""), "title": d.get("title", "")})
                    print("  %s | %s | %s | %s" % (i, d.get("pubdate",""), d.get("source",""), d.get("title","")[:100]))
            break
        except Exception as e:
            print(f"## {k} ERR({attempt+1}) {type(e).__name__}")
            time.sleep(3)

json.dump(out, open(os.path.join(OUT, "pubmed检索结果-补充.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n保存完成")
