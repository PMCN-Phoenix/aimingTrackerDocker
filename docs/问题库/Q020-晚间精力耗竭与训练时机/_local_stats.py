# -*- coding: utf-8 -*-
"""Q020 本地数据分析：按本地时段(+8h)聚合 kovaak_score，按场景归一化。

输出: 学术原始数据/本地数据-时段表现.json
"""
import json, os, sys, collections
import urllib.request

URL = "http://127.0.0.1:8087/api/v2/query?org=aim-org"
TOKEN = "aim-super-secret-token-2026"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学术原始数据", "本地数据-时段表现.json")

FLUX = '''from(bucket:"aim")
  |> range(start: 2026-08-01T00:00:00Z)
  |> filter(fn:(r) => r._measurement=="kovaak_score" and (r._field=="score" or r._field=="hits" or r._field=="misses"))
  |> keep(columns:["_time","_field","_value","scenario"])'''

req = urllib.request.Request(URL, data=FLUX.encode(), method="POST", headers={
    "Authorization": f"Token {TOKEN}", "Content-Type": "application/vnd.flux", "Accept": "application/csv"})
raw = urllib.request.urlopen(req, timeout=60).read().decode()

rows = []
for line in raw.splitlines():
    if not line or line.startswith("#") or line.startswith(",result"):
        continue
    parts = line.split(",")
    # _,result,table,_start,_stop,_time,_value,_field,scenario (列序不保证，按header解析)
    hdr = None
    rows.append(parts)

# 按header解析
header = None
data = []
for line in raw.splitlines():
    if not line or line.startswith("#"):
        continue
    parts = line.split(",")
    if parts[0] == "" and "result" in parts[1:3]:
        header = parts
        continue
    if header is None:
        continue
    rec = dict(zip(header, parts))
    try:
        data.append({
            "time": rec["_time"], "field": rec["_field"],
            "value": float(rec["_value"]), "scenario": rec.get("scenario", ""),
        })
    except (KeyError, ValueError):
        continue

# UTC -> 本地 +8h
import datetime
def local_hour(t):
    dt = datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))
    return (dt + datetime.timedelta(hours=8)).hour, (dt + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")

def bucket(h):
    if 5 <= h < 9:  return "清晨5-9"
    if 9 <= h < 13: return "上午9-13"
    if 13 <= h < 17: return "午后13-17"
    if 17 <= h < 21: return "傍晚17-21"
    return "深夜21-5"

# score: 按场景归一化（score/场景均值），再按时段聚合
score_rows = [d for d in data if d["field"] == "score"]
sc_mean = collections.defaultdict(list)
for d in score_rows:
    sc_mean[d["scenario"]].append(d["value"])
sc_mean = {k: sum(v)/len(v) for k, v in sc_mean.items()}

norm = collections.defaultdict(list)
for d in score_rows:
    if sc_mean[d["scenario"]] > 0:
        h, _ = local_hour(d["time"])
        norm[bucket(h)].append(d["value"] / sc_mean[d["scenario"]])

score_summary = {}
for b in ("清晨5-9", "上午9-13", "午后13-17", "傍晚17-21", "深夜21-5"):
    vals = norm.get(b, [])
    if vals:
        score_summary[b] = {"n": len(vals), "rel_mean": round(sum(vals)/len(vals), 4),
                            "rel_median": round(sorted(vals)[len(vals)//2], 4)}

# hit rate: hits/(hits+misses) 按时段
pairs = collections.defaultdict(lambda: [0.0, 0.0])  # scenario->time->? 简化: 全局按时段
hits_by_bucket = collections.defaultdict(lambda: [0.0, 0.0])
for d in data:
    if d["field"] in ("hits", "misses"):
        h, _ = local_hour(d["time"])
        idx = 0 if d["field"] == "hits" else 1
        hits_by_bucket[bucket(h)][idx] += d["value"]

hitrate = {}
for b, (hi, mi) in hits_by_bucket.items():
    if hi + mi > 0:
        hitrate[b] = {"hits": int(hi), "misses": int(mi), "hit_rate": round(hi/(hi+mi), 4)}

# 深夜场景级明细（验证10-18发现的Smoothsphere衰减）
late = collections.defaultdict(lambda: {"n": 0, "rel": []})
for d in score_rows:
    h, _ = local_hour(d["time"])
    if h >= 21 or h < 5:
        late[d["scenario"]]["n"] += 1
        late[d["scenario"]]["rel"].append(d["value"]/sc_mean[d["scenario"]])
late_summary = {}
for s, v in sorted(late.items(), key=lambda x: -x[1]["n"])[:12]:
    late_summary[s] = {"n": v["n"], "rel_mean": round(sum(v["rel"])/len(v["rel"]), 4)}

out = {
    "说明": "kovaak_score 按场景自身均值归一化后按本地时段(+8h)聚合；rel_mean>1 表示该时段高于个人该场景平均",
    "数据范围": "2026-08-01 起",
    "score条数": len(score_rows),
    "场景数": len(sc_mean),
    "按时段归一化分数": score_summary,
    "按时段命中率": hitrate,
    "深夜段场景明细_TOP12": late_summary,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
