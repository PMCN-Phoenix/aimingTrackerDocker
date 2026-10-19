# -*- coding: utf-8 -*-
"""PubMed 检索：Q022 跟枪初速度匹配与「加速带」
核心：平滑追踪启动/预期、间歇控制、速度匹配与拦截制导、前馈内部模型
"""
import os, json, requests, time
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
os.makedirs(OUT, exist_ok=True)

QS = {
    "pursuit_initiation": "smooth pursuit initiation latency acceleration target velocity",
    "anticipatory_pursuit": "anticipatory smooth pursuit prediction target motion",
    "pursuit_gain": "smooth pursuit gain velocity error catch up",
    "pursuit_learning": "smooth pursuit adaptation learning prediction",
    "intermittent_control": "intermittent control manual tracking corrective submovements",
    "internal_model_tracking": "internal model feedforward visuomotor tracking prediction",
    "interception_velocity": "interception velocity matching hand movement moving target",
    "pursuit_guidance": "pursuit guidance law proportional navigation interception human",
    "lead_pursuit": "lead pursuit interception strategy predictive",
    "catchup_saccade": "catch-up saccade pursuit lag position error",
    "optic_flow_control": "optic flow velocity estimation manual control tracking",
    "predictive_tracking_hand": "predictive tracking hand movement moving target occlusion",
    "tracking_delay": "visuomotor delay prediction compensation tracking",
    "smooth_pursuit_hand": "smooth pursuit eye hand coordination tracking gain",
    "motor_priming_velocity": "movement priming initial velocity state aiming",
    "bimanual_tracking": "continuous tracking task performance variability practice",
}

out = {}
for k, q in QS.items():
    for attempt in range(3):
        try:
            r = requests.get(B + "esearch.fcgi", params={"db": "pubmed", "term": q, "retmax": 5,
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
                    print("  %s | %s | %s | %s" % (i, d.get("pubdate",""), d.get("source",""), d.get("title","")[:105]))
            break
        except Exception as e:
            print(f"## {k} ERR({attempt+1}) {type(e).__name__}")
            time.sleep(3)

json.dump(out, open(os.path.join(OUT, "pubmed检索结果.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\n保存完成")
