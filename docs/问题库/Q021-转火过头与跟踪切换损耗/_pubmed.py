# -*- coding: utf-8 -*-
"""PubMed 检索：Q021 转火过头与跟踪切换损耗
核心：快速指向动作的"过冲/欠冲"机制、视觉-手部耦合、切换成本
"""
import os, json, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

qs = {
    "submovement": "submovement ballistic corrective aimed movement",
    "impulse_variability": "impulse variability theory rapid aiming accuracy",
    "speed_accuracy": "speed accuracy tradeoff aiming movement endpoint error",
    "online_control": "online control goal-directed aiming visual feedback",
    "saccade_pursuit": "saccade smooth pursuit interaction target change",
    "saccade_latency": "saccadic latency double step target displacement",
    "quiet_eye": "quiet eye gaze fixation aiming accuracy",
    "gaze_anchoring": "gaze behaviour interceptive action accuracy",
    "task_switching_motor": "task switching cost motor set reconfiguration",
    "sequential_aiming": "sequential aiming movements chunking",
    "grip_force": "grip force modulation precision aiming",
    "visual_delay": "delayed visual feedback manual aiming endpoint error",
    "overshoot": "overshoot undershoot aiming movement endpoint",
    "practice_variability": "practice reduces endpoint variability aiming",
    "movement_time_pressure": "time pressure movement planning endpoint accuracy",
    "motor_imagery_transfer": "motor imagery transfer aiming accuracy",
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

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "pubmed检索结果.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("\n保存完成")
