# -*- coding: utf-8 -*-
"""
Step2: 精选15个视频 → 抓网页HTML拿aid/cid → 抓wbi字幕 → Top5抓评论
"""
import sys, os, re, json, time, hashlib, urllib.parse
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
import requests

OUT_DIR = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q007-平滑后微调僵住\B站原始数据"
SUB_DIR = os.path.join(OUT_DIR, "字幕")
os.makedirs(SUB_DIR, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]
PROXIES = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}

# 精选15个视频
SELECTED = [
    "BV1pQuN6LEwd",  # 手腕流还是手臂流？用一个训练找准有效瞄准范围 (Aimlabs官方)
    "BV1ho5TztEzD",  # 手臂流还是手腕流？也许两者都不应该 (24min深度)
    "BV1aXyuYeEc8",  # 手指才是微调的关键!平滑瞄准没有意义 (25万)
    "BV1Cz421f7To",  # 如何正确使用「手臂流」(23万,偏航)
    "BV12b8L6YEJA",  # 你不是状态差，而是瞄准太僵硬 (12万)
    "BV1C2Hi6AEAa",  # 微调一快就空，一慢就被秒 (11万)
    "BV1VEnzzKEge",  # 为什么趴握是fps最低级的握法 (45万,大东彦/夜莲,反面)
    "BV1G34y167Vv",  # 帮助你提升微调精准度的握姿小技巧 (12万)
    "BV1Jg411i7CR",  # 5分钟教你快速提升微调能力 (44万,大东彦)
    "BV1A9KpzTEHL",  # 张力控制全攻略 (48万)
    "BV1EZ4y1m7EA",  # 跟枪不平滑？停枪时会抖 (29万)
    "BV1T3he6QEwd",  # 3个练习 掌握定位 微调的确认感 (16万)
    "BV1X14y1s7i9",  # 瞄准该如何真正的去放松 (8.7万)
    "BV1PwmvBdEwX",  # 一个技巧解决实战时手臂手腕结合僵硬
    "BV1eRm8YeEJx",  # 瞄准的减速过程有哪些方法
]
# Top 5 抓评论
TOP5_COMMENTS = [
    "BV1A9KpzTEHL",  # 张力控制 48万
    "BV1VEnzzKEge",  # 趴握 45万
    "BV1Jg411i7CR",  # 微调能力 44万
    "BV1aXyuYeEc8",  # 手指微调 25万
    "BV1Cz421f7To",  # 手臂流 23万
]

def make_session(pool):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    })
    s.proxies.update(PROXIES)
    s.headers["Cookie"] = pool.get_cookie()
    return s

def get_wbi_keys(s):
    nav = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = nav["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]

def sign(p, mixin):
    p = dict(p)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

def fetch_video_info(s, pool, bvid):
    """抓网页HTML拿aid/cid/title/owner"""
    url = f"https://www.bilibili.com/video/{bvid}/"
    for attempt in range(3):
        try:
            r = s.get(url, timeout=25)
            t = r.text
            m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
                 or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
            if not m:
                print(f"  [!] {bvid} 未找到 __INITIAL_STATE__")
                return None
            v = json.loads(m.group(1))["videoData"]
            pool.report_success()
            return {
                "aid": v.get("aid"),
                "cid": v.get("cid"),
                "title": v.get("title"),
                "owner": (v.get("owner") or {}).get("name"),
                "duration": v.get("duration"),
                "desc": (v.get("desc") or "")[:800],
                "pages": [{"cid": p.get("cid"), "part": p.get("part")} for p in (v.get("pages") or [])],
            }
        except Exception as e:
            print(f"  [!] {bvid} info attempt{attempt}: {e}")
            time.sleep(3)
    return None

def fetch_subtitle(s, pool, mixin, bvid, cid):
    """wbi字幕"""
    q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    for attempt in range(4):
        try:
            d = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                      timeout=20).json()
            subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
            if not subs:
                # 可能是412
                if d.get("code") == -412:
                    pool.report_412()
                    s.headers["Cookie"] = pool.get_cookie()
                    time.sleep(3)
                    continue
                return None  # 无AI字幕
            pool.report_success()
            # 选语言
            pick = next((x for pref in ["zh-Hans","zh-CN","zh","ai-zh"] for x in subs if x.get("lan") == pref), subs[0])
            u = pick.get("subtitle_url") or ""
            if not u:
                time.sleep(3)
                continue
            if u.startswith("//"):
                u = "https:" + u
            body = s.get(u, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25).json()["body"]
            return {"lan": pick.get("lan"), "body": body}
        except Exception as e:
            print(f"  [!] {bvid} sub attempt{attempt}: {e}")
            time.sleep(3)
    return None

def fetch_comments(s, pool, bvid, aid, max_pages=8):
    """主评论分页 + 楼中楼"""
    comments = []
    total = 0
    for pn in range(1, max_pages + 1):
        try:
            d = s.get("https://api.bilibili.com/x/v2/reply/wbi/main",
                      params=sign({"oid": aid, "type": 1, "pn": pn, "ps": 20, "sort": 2}, mixin_global),
                      headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                      timeout=25).json()
        except Exception as e:
            print(f"    [!] comment pn{pn}: {e}")
            time.sleep(2)
            continue
        if d.get("code") == -412:
            pool.report_412()
            s.headers["Cookie"] = pool.get_cookie()
            time.sleep(3)
            continue
        dd = d.get("data") or {}
        reps = dd.get("replies") or []
        if not reps:
            break
        total = (dd.get("page") or {}).get("count") or total
        for rep in reps:
            msg = rep.get("content", {}).get("message", "")
            item = {
                "uname": (rep.get("member") or {}).get("uname"),
                "like": rep.get("like", 0),
                "rcount": rep.get("rcount", 0),
                "rpid": rep.get("rpid"),
                "message": msg,
                "subs": [],
            }
            # 楼中楼
            if rep.get("rcount", 0) > 0:
                try:
                    d2 = s.get("https://api.bilibili.com/x/v2/reply/reply",
                               params={"oid": aid, "type": 1, "root": rep.get("rpid"), "pn": 1, "ps": 20},
                               headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"},
                               timeout=20).json()
                    subs = (d2.get("data") or {}).get("replies") or []
                    for sub in subs[:20]:
                        item["subs"].append({
                            "uname": (sub.get("member") or {}).get("uname"),
                            "like": sub.get("like", 0),
                            "message": sub.get("content", {}).get("message", ""),
                        })
                    time.sleep(0.8)
                except Exception as e:
                    print(f"    [!] subcomment: {e}")
            comments.append(item)
        pool.report_success()
        print(f"    pn{pn}: 累计{len(comments)}条 (total={total})")
        if len(comments) >= total:
            break
        time.sleep(1.2)
    return {"count": total, "comments": comments}

mixin_global = None

def main():
    global mixin_global
    pool = BiliCookiePool()
    s = make_session(pool)
    mixin_global = get_wbi_keys(s)
    print(f"[OK] wbi mixin={mixin_global[:8]}...")

    results = {}

    for i, bvid in enumerate(SELECTED):
        print(f"\n[{i+1}/{len(SELECTED)}] {bvid}")
        info = fetch_video_info(s, pool, bvid)
        if not info:
            print(f"  [!] 无法获取信息, 跳过")
            continue
        print(f"  title: {info['title'][:50]}")
        print(f"  owner: {info['owner']} | aid={info['aid']} cid={info['cid']} dur={info['duration']}")

        entry = dict(info)
        entry["bvid"] = bvid

        # 抓字幕
        if info.get("cid"):
            sub = fetch_subtitle(s, pool, mixin_global, bvid, info["cid"])
            if sub:
                entry["subtitle_lan"] = sub["lan"]
                entry["subtitle_segments"] = len(sub["body"])
                entry["subtitle_coverage"] = round(
                    (sub["body"][-1]["to"] / info["duration"]) if info["duration"] and sub["body"] else 0, 3)
                # 存字幕文件
                sub_path = os.path.join(SUB_DIR, f"{bvid}.json")
                with open(sub_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "bvid": bvid, "title": info["title"], "owner": info["owner"],
                        "duration": info["duration"], "lan": sub["lan"],
                        "body": sub["body"],
                    }, f, ensure_ascii=False, indent=2)
                # 同时存纯文本
                txt_path = os.path.join(SUB_DIR, f"{bvid}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"# {info['title']} | UP: {info['owner']} | {bvid}\n\n")
                    for seg in sub["body"]:
                        m, sec = divmod(int(seg["from"]), 60)
                        f.write(f"[{m:02d}:{sec:02d}] {seg['content']}\n")
                print(f"  字幕: {len(sub['body'])}段, 覆盖{entry['subtitle_coverage']*100:.1f}%")
            else:
                entry["subtitle_lan"] = None
                print(f"  字幕: 无AI字幕")
            time.sleep(1.5)

        # 抓评论
        if bvid in TOP5_COMMENTS and info.get("aid"):
            print(f"  抓评论中...")
            c = fetch_comments(s, pool, bvid, info["aid"])
            entry["comments_count"] = c["count"]
            entry["comments_fetched"] = len(c["comments"])
            entry["comments"] = c["comments"]
            # 存评论
            cmt_path = os.path.join(OUT_DIR, f"评论_{bvid}.json")
            with open(cmt_path, "w", encoding="utf-8") as f:
                json.dump({bvid: entry}, f, ensure_ascii=False, indent=2)
            print(f"  评论: {len(c['comments'])}条 (total={c['count']})")

        results[bvid] = entry
        time.sleep(1.5)

    # 存精选列表
    sel_path = os.path.join(OUT_DIR, "精选列表.json")
    with open(sel_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 精选列表已保存: {sel_path}")

if __name__ == "__main__":
    main()
