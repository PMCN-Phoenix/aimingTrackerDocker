# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第3步b：补抓4个备选视频字幕 + 重试6个无字幕视频
"""
import sys, os, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")
SUB_DIR = OUT_DIR / "字幕"

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

# 补抓列表：(bvid, theme, reason)
EXTRA = [
    ("BV1wznzzQEdu", "A", "每日7小时VCT魔鬼训练——具体时间投入案例"),
    ("BV1PVdPBxEFw", "C", "数学复盘浪费时间——反面意见/复盘方法论"),
    ("BV1YDHt6tEB5", "C", "nAts思维模式课——职业选手意识框架"),
    ("BV1yRKp6xEi7", "B", "十招逃出下三段——下段位提升清单"),
]

# 重试无字幕列表
RETRY_NO_SUB = [
    "BV12SxVeTEGX", "BV1a2VB6aE1T", "BV1konPzpEjc",
    "BV1pdVozEEbS", "BV1FaM86GEzd", "BV13rkyBHEeL",
]


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
        return None, None
    v = json.loads(m.group(1))["videoData"]
    return v.get("aid"), v.get("cid"), {
        "title": v.get("title"), "desc": v.get("desc", ""),
        "owner": v.get("owner", {}).get("name", ""),
        "duration": v.get("duration", 0),
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
    if not pick: pick = subs[0]
    url = pick.get("subtitle_url", "")
    if url.startswith("//"): url = "https:" + url
    return {"lan": pick.get("lan"), "url": url}, None


def download_subtitle(url, bvid, s):
    for _ in range(4):
        try:
            r = s.get(url, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25)
            body = r.json().get("body", [])
            if body: return body
        except Exception:
            pass
        time.sleep(3)
    return None


def fmt_ts(sec):
    m = int(sec // 60); s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def process(bvid, pool, extra_meta=None):
    json_path = SUB_DIR / f"{bvid}.json"
    if json_path.exists():
        old = json.load(open(json_path, encoding="utf-8"))
        if old.get("status") == "ok":
            return "already_ok"

    cookie = pool.get_cookie()
    s = make_session(cookie)
    try:
        aid, cid, meta = fetch_cid(bvid, s)
    except Exception as e:
        return f"web_fail:{e}"
    if not cid:
        return "no_cid"

    try:
        mixin = get_wbi_keys(s)
    except Exception:
        pool.report_412()
        return "wbi_fail"

    sub_info, err = fetch_subtitle(bvid, cid, mixin, s)
    if err:
        json_path.write_text(json.dumps({
            "bvid": bvid, "aid": aid, "cid": cid, "meta": meta,
            "status": "no_subtitle", "error": err, "body": []
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"no_sub:{err}"

    body = download_subtitle(sub_info["url"], bvid, s)
    if not body:
        return "download_empty"

    result = {
        "bvid": bvid, "aid": aid, "cid": cid, "meta": meta,
        "subtitle_info": sub_info, "status": "ok",
        "segment_count": len(body), "body": body,
    }
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    txt_lines = [f"# {meta.get('title','')}", f"# UP主: {meta.get('owner','')}",
                 f"# 时长: {meta.get('duration',0)}s | 字幕段数: {len(body)}", ""]
    for seg in body:
        txt_lines.append(f"[{fmt_ts(seg['from'])}] {seg['content']}")
    (SUB_DIR / f"{bvid}.txt").write_text("\n".join(txt_lines), encoding="utf-8")
    pool.report_success()
    return f"ok:{len(body)}段"


def main():
    pool = BiliCookiePool()

    print("=== 补抓4个备选 ===")
    extra_results = []
    for bvid, theme, reason in EXTRA:
        print(f"  {bvid} [{theme}] {reason[:30]}")
        res = process(bvid, pool)
        print(f"    -> {res}")
        extra_results.append({"bvid": bvid, "theme": theme, "reason": reason, "result": res})
        time.sleep(2)

    print("\n=== 重试6个无字幕 ===")
    retry_results = []
    for bvid in RETRY_NO_SUB:
        print(f"  {bvid}")
        res = process(bvid, pool)
        print(f"    -> {res}")
        retry_results.append({"bvid": bvid, "result": res})
        time.sleep(2)

    # 更新精选列表
    sel_path = OUT_DIR / "精选列表.json"
    sel = json.load(open(sel_path, encoding="utf-8"))
    sel["extra_videos"] = extra_results
    sel["retry_no_sub"] = retry_results

    # 统计最终字幕成功数
    all_subs = list(SUB_DIR.glob("*.json"))
    ok_count = 0
    for f in all_subs:
        try:
            d = json.load(open(f, encoding="utf-8"))
            if d.get("status") == "ok":
                ok_count += 1
        except Exception:
            pass
    sel["final_subtitle_ok_count"] = ok_count
    print(f"\n=== 最终字幕成功数: {ok_count} / {len(all_subs)} 个文件 ===")

    sel_path.write_text(json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
