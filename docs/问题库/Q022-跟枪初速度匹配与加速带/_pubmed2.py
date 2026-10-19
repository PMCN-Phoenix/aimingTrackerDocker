# -*- coding: utf-8 -*-
"""PubMed 全文摘要抓取：Q022 跟枪初速度匹配与「加速带」"""
import os, re, time, requests
os.environ.pop("http_proxy", None); os.environ.pop("https_proxy", None)
P = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
B = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据")
os.makedirs(OUT, exist_ok=True)

# 平滑追踪启动 / 预期 / 增益 / 追赶扫视
PMID_A = [
    "30709895",  # Eye Position Error Influence over "Open-Loop" Smooth Pursuit Initiation
    "39584660",  # Latency and amplitude of catch-up saccades to accelerating targets
    "31283450",  # Predictive Smooth Pursuit Eye Movements (Annu Rev Vis Sci)
    "39752177",  # Anticipatory SPE scale with probability of visual motion
    "20963581",  # Influence of previous target motion on anticipatory pursuit deceleration
    "1932405",   # model relating pursuit gain & catch-up saccade rate
    "27715479",  # Effects of Visual Error Timing on Smooth Pursuit Gain Adaptation
    "33356899",  # Confidence in predicted position error explains saccadic decisions
]
# 手部追踪 / 内部模型 / 拦截制导 / 速度匹配
PMID_B = [
    "41980556",  # Predictability of trajectory modulates manual tracking: real-time feedback -> internal model
    "15668793",  # submovements during circular manual tracking
    "36635938",  # Humans Can Track But Fail to Predict Accelerating Objects
    "24657827",  # Manual coordination with intermittent targets: velocity information for prospective control
    "17611282",  # Target interception: hand-eye coordination and strategies
    "26605840",  # Manual tracking enhances smooth pursuit eye movements
    "42068368",  # impact of varying cursor latency on visuomotor tracking
    "24599942",  # Predictability is necessary for closed-loop visual feedback delay adaptation
    "42516696",  # Predictive interception across speed profiles
]

ALL = PMID_A + PMID_B


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
# 统计抓到几条
got = len(re.findall(r"^\d+\.\s", text, re.M))
print(f"疑似条目 {got}")
