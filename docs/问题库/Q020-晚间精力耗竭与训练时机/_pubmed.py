# -*- coding: utf-8 -*-
"""PubMed 检索：Q020 晚间精力耗竭与训练时机（时间生物学/心理疲劳/晚间运动与睡眠/自我损耗）"""
import os, json, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

qs = {
    "time_of_day_motor": "time of day diurnal variation motor performance fine motor",
    "circadian_skill": "circadian rhythm skilled performance reaction time learning",
    "mental_fatigue_endurance": "mental fatigue endurance performance Marcora",
    "mental_fatigue_sport": "mental fatigue sport performance psychobiological",
    "evening_exercise_sleep": "evening exercise sleep quality timing",
    "exercise_timing_sleep_meta": "exercise performed evening effects sleep meta-analysis",
    "selfcontrol_depletion": "ego depletion self-control replication registered replication",
    "decision_fatigue": "decision fatigue depletion choices",
    "vigilance_decrement": "vigilance decrement sustained attention time on task",
    "morningness_eveningness": "morningness eveningness chronotype physical performance",
    "cognitive_work_exercise": "prolonged cognitive work subsequent physical exercise performance",
    "training_after_work": "after work exercise adherence fatigue employees",
}

out = {}
for k, q in qs.items():
    try:
        r = requests.get(B + "esearch.fcgi",
                         params={"db": "pubmed", "term": q, "retmax": 5,
                                 "retmode": "json", "sort": "relevance"},
                         proxies=P, timeout=45).json()
        ids = r["esearchresult"]["idlist"]
        out[k] = {"query": q, "count": r["esearchresult"].get("count"), "items": []}
        print(f"\n## {k}  ({q}) -> 命中{out[k]['count']}")
        if not ids:
            continue
        s = requests.get(B + "esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
                         proxies=P, timeout=45).json()
        for i in ids:
            d = s["result"].get(i, {})
            item = {"pmid": i, "date": d.get("pubdate", ""), "journal": d.get("source", ""),
                    "title": d.get("title", "")}
            out[k]["items"].append(item)
            print("  %s | %s | %s | %s" % (i, d.get("pubdate", ""), d.get("source", ""), d.get("title", "")[:110]))
    except Exception as e:
        print(f"## {k} ERR {e}")
        out[k] = {"query": q, "error": str(e)}

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "学术原始数据", "pubmed检索结果.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\nsaved -> 学术原始数据/pubmed检索结果.json")
