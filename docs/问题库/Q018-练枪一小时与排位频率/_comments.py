# -*- coding: utf-8 -*-
"""B站评论：排位频率 / 练枪时长 / 生活平衡"""
import sys, json, time, requests
sys.path.insert(0, r"D:/11.project/iwen-codex/bilibili-cookies")
from cookie_manager import BiliCookiePool

pool = BiliCookiePool()
s = requests.Session()
s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

VIDS = [
    ("BV1K94y1E7Z8", "每天练枪一小时 这是她瞄准发生的变化"),
    ("BV1aupu6qEuD", "神话杂谈 上分练枪经验分享"),
    ("BV1kpbv6LEsm", "每天练枪还是没提升 12个错误"),
    ("BV1qoAceeEpf", "花太多时间在瞄准训练上的样子"),
]
KW = ["排位", "每天", "一周", "小时", "分钟", "几把", "多久", "频率", "上分", "段位",
      "累", "休息", "生活", "上班", "时间", "坚持", "练枪", "把"]


def aid_of(bv):
    s.headers["Cookie"] = pool.get_cookie()
    r = s.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}", timeout=20).json()
    if r.get("code") != 0:
        return None, r.get("message")
    return r["data"]["aid"], None


out = {}
for bv, title in VIDS:
    aid, err = aid_of(bv)
    if not aid:
        print(f"  aid失败 {bv} {err}")
        continue
    rows = []
    for pn in (1, 2):
        r = s.get("https://api.bilibili.com/x/v2/reply",
                  params={"type": 1, "oid": aid, "pn": pn, "ps": 20, "sort": 2},
                  timeout=25).json()
        if r.get("code") != 0:
            print(f"  reply {bv} p{pn} code={r.get('code')} {r.get('message')}")
            break
        for rep in r["data"].get("replies") or []:
            rows.append({"msg": rep["content"]["message"], "like": rep["like"],
                         "rc": rep["rcount"]})
        time.sleep(0.8)
    out[bv] = {"title": title, "n": len(rows), "replies": rows}
    print(f"  {bv} {len(rows)} 条")
    time.sleep(1.0)

json.dump(out, open("B站原始数据/评论.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("\n=== 命中关键词的评论 ===")
for bv, d in out.items():
    hit = [x for x in d["replies"] if any(k in x["msg"] for k in KW)]
    hit.sort(key=lambda x: -x["like"])
    print(f"\n## {bv} {d['title']}  ({len(hit)}/{d['n']})")
    for x in hit[:6]:
        print(f"  [{x['like']:>4}赞] {x['msg'][:170]}")
