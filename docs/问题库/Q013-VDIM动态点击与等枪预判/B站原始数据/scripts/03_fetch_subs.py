# -*- coding: utf-8 -*-
"""Q013 抓新视频字幕（跳过reuse_subtitle标记的）"""
import sys, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q013-VDIM动态点击与等枪预判\B站原始数据")
SUB_DIR = OUT_DIR / "subtitles"
SUB_DIR.mkdir(parents=True, exist_ok=True)

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"


def make_session(cookie_str):
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            s.cookies.set(k.strip().lstrip("\ufeff"), v.strip())
    return s


def get_wbi_keys(s):
    r = s.get("https://api.bilibili.com/x/web-interface/nav", timeout=20).json()
    wbi = r["data"]["wbi_img"]
    img = wbi["img_url"].rsplit("/", 1)[-1].split(".")[0]
    sub = wbi["sub_url"].rsplit("/", 1)[-1].split(".")[0]
    return "".join((img + sub)[i] for i in MIXIN)[:32]


def sign(params, mixin):
    p = dict(params)
    p["wts"] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p["w_rid"] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p


def fetch_cid(bvid, s):
    r = s.get(f"https://www.bilibili.com/video/{bvid}/",
              headers={"Referer": "https://www.bilibili.com/"}, timeout=25)
    t = r.text
    m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
         or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
    if not m:
        return None, None, None
    v = json.loads(m.group(1))["videoData"]
    return v.get("aid"), v.get("cid"), {
        "title": v.get("title"),
        "owner": v.get("owner", {}).get("name", ""),
        "duration": v.get("duration", 0),
        "desc": v.get("desc", ""),
    }


def fetch_subtitle(bvid, cid, mixin, s):
    q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
              headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20)
    d = r.json()
    if d.get("code") != 0:
        return None, f"code={d.get('code')}"
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    if not subs:
        return None, "no_subtitle"
    pick = None
    for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"]:
        for x in subs:
            if x.get("lan") == pref:
                pick = x; break
        if pick: break
    if not pick:
        pick = subs[0]
    url = pick.get("subtitle_url", "")
    if url.startswith("//"):
        url = "https:" + url
    return {"lan": pick.get("lan"), "url": url, "lan_doc": pick.get("lan_doc", "")}, None


def download_subtitle(url, bvid, s):
    for _ in range(4):
        try:
            r = s.get(url, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25)
            body = r.json().get("body", [])
            if body:
                return body
        except Exception as e:
            print(f"  下载失败 {e}")
        time.sleep(3)
    return None


def fmt_ts(sec):
    return f"{int(sec//60):02d}:{int(sec%60):02d}"


def main():
    pool = BiliCookiePool()
    sel = json.load(open(OUT_DIR / "selected_videos.json", encoding="utf-8"))
    items = sel["selected"]
    stats = {"ok": 0, "no_sub": 0, "failed": 0, "reused": 0}

    for i, item in enumerate(items):
        bvid = item["bvid"]
        if item.get("reuse_subtitle"):
            print(f"[{i+1}/{len(items)}] {bvid} 复用已有字幕: {item['reuse_subtitle'][:60]}")
            stats["reused"] += 1
            continue
        json_path = SUB_DIR / f"{bvid}.json"
        if json_path.exists():
            print(f"[{i+1}/{len(items)}] {bvid} 已抓过，跳过")
            stats["ok"] += 1
            continue

        print(f"[{i+1}/{len(items)}] {bvid} | {item['title'][:40]}")
        cookie = pool.get_cookie()
        s = make_session(cookie)
        try:
            aid, cid, meta = fetch_cid(bvid, s)
        except Exception as e:
            print(f"  抓网页异常 {e}")
            pool.report_412()
            stats["failed"] += 1; time.sleep(2); continue
        if not cid:
            print("  无cid")
            stats["failed"] += 1; time.sleep(2); continue

        try:
            mixin = get_wbi_keys(s)
        except Exception as e:
            print(f"  wbi失败 {e}")
            pool.report_412()
            stats["failed"] += 1; time.sleep(2); continue

        sub_info, err = fetch_subtitle(bvid, cid, mixin, s)
        if err:
            print(f"  无字幕: {err}")
            stats["no_sub"] += 1
            json_path.write_text(json.dumps({"bvid": bvid, "status": "no_subtitle", "error": err},
                                            ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(2); continue

        body = download_subtitle(sub_info["url"], bvid, s)
        if not body:
            print("  下载空")
            stats["failed"] += 1; time.sleep(2); continue

        json_path.write_text(json.dumps({
            "bvid": bvid, "aid": aid, "cid": cid, "meta": meta,
            "subtitle_info": sub_info, "status": "ok", "segment_count": len(body),
            "body": body,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

        lines = [f"# {meta.get('title','')}", f"# UP: {meta.get('owner','')}",
                 f"# 时长:{meta.get('duration',0)}s 段数:{len(body)}", ""]
        for seg in body:
            lines.append(f"[{fmt_ts(seg['from'])}] {seg['content']}")
        (SUB_DIR / f"{bvid}.txt").write_text("\n".join(lines), encoding="utf-8")

        print(f"  OK: {len(body)}段 lan={sub_info['lan']}")
        stats["ok"] += 1
        pool.report_success()
        time.sleep(2)

    print(f"\n=== 字幕统计 ===\n{json.dumps(stats, ensure_ascii=False, indent=2)}")
    sel["subtitle_stats"] = stats
    (OUT_DIR / "selected_videos.json").write_text(
        json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
