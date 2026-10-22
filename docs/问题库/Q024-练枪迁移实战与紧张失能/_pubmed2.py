# -*- coding: utf-8 -*-
"""PubMed 全文摘要抓取：Q024 练枪迁移实战 + 压力下紧张失能"""
import os, re, time, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")

# A. choking 的机制与干预
PMID_A = [
    "39270654",  # A neural basis of choking under pressure (Neuron 2024)
    "25713517",  # Choking under pressure: neuropsychological mechanisms of incentive-induced decrement
    "41951087",  # Counteracting choking under pressure in sport: meta-analysis of interventions
    "38376935",  # Conquering pressure! mild-anxiety training on motor performance under pressure
    "29777527",  # Limiting motor skill knowledge via incidental training protects against choking
    "33406149",  # Factors of choking under pressure in musicians
]
# B. 迁移与练习特异性
PMID_B = [
    "29445348",  # Taekwondo fighting in training does not simulate affective/cognitive demands of competition
    "39205981",  # contextual interference on transfer - systematic review and meta-analysis
    "38987617",  # High contextual interference improves retention - meta-analysis
    "38081160",  # Relationship between skill training and skill transfer (bimanual)
    "24782722",  # Are videogame training gains specific or general?
    "39427852",  # No transfer of 3D-MOT training on soccer game performance
]
# C. 热身衰减
PMID_C = [
    "23611248",  # Task difficulty and the time scales of warm-up and motor learning
    "7563292",   # Warm-up decrement as a function of interpolated open and closed motor tasks
    "29684760",  # Unifying practice schedules in the timescales of motor learning and performance
]
# D. 压力下的注视与肌肉张力
PMID_D = [
    "17827115",  # Performing under pressure: physiological arousal, cognitive anxiety, gaze control
    "21807433",  # Performing under pressure: gaze control, decision making, elite vs rookie
    "17926174",  # State anxiety and visual attention: quiet eye period
    "19701628",  # Music performance anxiety in skilled pianists: social-evaluative situation EMG
    "12001884",  # Muscle tension and physiologic hyperarousal, performance
    "41309875",  # inverted-U between stress and performance in elite shooting
]
# E. 电竞侧
PMID_E = [
    "41035706",  # Effects of a playoff match on competitive anxiety and autonomic regulation in pro esports
    "40340544",  # Enhancing pressurized esports performance
]

ALL = PMID_A + PMID_B + PMID_C + PMID_D + PMID_E


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
for i in range(0, len(ALL), 4):
    part = ALL[i:i + 4]
    print(f"fetch {part}")
    t = efetch(part)
    if t:
        chunks.append(t)

text = "\n\n" + ("\n\n" + "=" * 78 + "\n\n").join(chunks)
with open(os.path.join(OUT, "pubmed摘要.txt"), "w", encoding="utf-8") as f:
    f.write(text)

print(f"\n总字符 {len(text)}")
print(f"疑似条目 {len(re.findall(r'^\d+\.\s', text, re.M))}")
