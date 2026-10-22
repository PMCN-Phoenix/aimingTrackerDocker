# -*- coding: utf-8 -*-
"""PubMed 检索：Q024 练枪迁移实战 + 压力下紧张失能
核心：choking under pressure / 迁移特异性 / 热身衰减 / reinvestment 自我监控 / 焦虑与精细动作
"""
import os, json, requests, time
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
os.makedirs(OUT, exist_ok=True)

QS = {
    "choking_pressure": "choking under pressure motor performance",
    "anxiety_fine_motor": "anxiety fine motor control precision accuracy",
    "anxiety_emg_tension": "anxiety muscle tension electromyography performance",
    "reinvestment": "reinvestment explicit monitoring skill breakdown",
    "self_focus": "self-focused attention motor automaticity performance",
    "specificity_practice": "specificity of practice transfer training",
    "transfer_training": "transfer of training motor skill learning",
    "warmup_decrement": "warm-up decrement motor performance",
    "contextual_interference": "contextual interference practice transfer retention",
    "variable_practice": "variable practice transfer novel task",
    "quiet_eye_pressure": "quiet eye anxiety aiming accuracy",
    "gaze_control_stress": "gaze control under pressure performance",
    "arousal_performance": "arousal performance relationship inverted U hypothesis",
    "cortisol_motor": "stress cortisol motor control dexterity",
    "psychological_skills": "psychological skills training performance under pressure",
    "simulation_training": "simulation training representativeness transfer sport",
    "perceptual_cognitive": "perceptual cognitive training transfer game",
    "esports_performance": "esports performance anxiety cognitive",
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

json.dump(out, open(os.path.join(OUT, "pubmed检索结果.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n保存完成")
