# -*- coding: utf-8 -*-
"""Q021 学术补充：第二轮定向检索 + 关键文献摘要抓取"""
import os, json, requests, time
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
os.makedirs(OUT, exist_ok=True)

QS2 = {
    "motor_output_variability": "motor output variability theory accuracy rapid movements",
    "submovement_model": "optimized submovement model rapid aimed movements",
    "primary_submovement": "primary submovement corrective submovement endpoint",
    "target_switching_eyhand": "target switching eye hand coordination sequential targets",
    "co_contraction_aiming": "co-contraction muscle activity precision aiming",
    "grip_pressure_mouse": "mouse grip pressure force aiming performance",
    "fitts_throughput": "Fitts law throughput pointing device performance",
    "endpoint_error_velocity": "peak velocity endpoint error accuracy constraint",
    "quiet_eye_expert": "quiet eye expert novice aiming differences",
    "anticipatory_control": "anticipatory control predictive pursuit target motion",
}

res2 = {}
for k, q in QS2.items():
    for attempt in range(2):
        try:
            r = requests.get(B + "esearch.fcgi",
                             params={"db": "pubmed", "term": q, "retmax": 5,
                                     "retmode": "json", "sort": "relevance"},
                             proxies=P, timeout=45).json()
            ids = r["esearchresult"]["idlist"]
            res2[k] = {"query": q, "count": r["esearchresult"].get("count"), "items": []}
            print(f"\n## {k} ({q}) -> {res2[k]['count']}")
            if ids:
                s = requests.get(B + "esummary.fcgi",
                                 params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
                                 proxies=P, timeout=45).json()
                for i in ids:
                    d = s["result"].get(i, {})
                    res2[k]["items"].append({"pmid": i, "date": d.get("pubdate", ""),
                                             "journal": d.get("source", ""), "title": d.get("title", "")})
                    print("  %s | %s | %s | %s" % (i, d.get("pubdate", ""), d.get("source", ""), d.get("title", "")[:110]))
            break
        except Exception as e:
            print(f"## {k} ERR({attempt+1}) {e}")
            time.sleep(2)

with open(os.path.join(OUT, "pubmed第二轮.json"), "w", encoding="utf-8") as f:
    json.dump(res2, f, ensure_ascii=False, indent=2)

# ---- 关键文献摘要 ----
PMIDS = [
    "16575577",  # corrective modifications cost
    "19401895",  # speed & energy expenditure
    "37930988",  # quiet eye: visual info + fixation stillness
    "30392140",  # why quiet eye improves accuracy
    "35112083",  # predictive saccade spatial accuracy
    "15322786",  # pursuit abrupt direction change
    "30809706",  # saccade switch cost
    "26223578",  # grip forces fast point-to-point vs continuous
    "35294273",  # eye-hand coordination online corrections
    "26902290",  # visual monitoring of aiming
]
print("\n\n########## 摘要 ##########")
chunks = []
for pid in PMIDS:
    try:
        r = requests.get(B + "efetch.fcgi",
                         params={"db": "pubmed", "id": pid, "rettype": "abstract", "retmode": "text"},
                         proxies=P, timeout=60)
        txt = r.text.strip()
        chunks.append(f"\n===== PMID {pid} =====\n{txt}\n")
        print(f"  {pid} ok {len(txt)} chars")
    except Exception as e:
        print(f"  {pid} ERR {e}")
    time.sleep(0.4)

with open(os.path.join(OUT, "pubmed摘要.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(chunks))
print("摘要已保存")
