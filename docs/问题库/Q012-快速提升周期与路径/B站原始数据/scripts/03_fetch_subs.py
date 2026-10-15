# -*- coding: utf-8 -*-
"""
Q012 B站调研 - 第3步：抓字幕
流程：抓网页HTML拿aid/cid -> wbi /x/player/wbi/v2 -> 下载subtitle_url
输出：字幕/{bvid}.json + 字幕/{bvid}.txt
"""
import sys, os, time, json, re, hashlib, urllib.parse, requests
from pathlib import Path

sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool

OUT_DIR = Path(r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q012-快速提升周期与路径\B站原始数据")
SUB_DIR = OUT_DIR / "字幕"
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
    """抓网页HTML拿aid/cid"""
    r = s.get(f"https://www.bilibili.com/video/{bvid}/",
              headers={"Referer": "https://www.bilibili.com/"}, timeout=25)
    t = r.text
    m = (re.search(r"window\.__INITIAL_STATE__=(.*?);\(function", t, re.S)
         or re.search(r"window\.__INITIAL_STATE__=(.*?);\s*</script>", t, re.S))
    if not m:
        return None, None, None
    try:
        v = json.loads(m.group(1))["videoData"]
        aid = v.get("aid")
        cid = v.get("cid")
        title = v.get("title")
        pages = v.get("pages", [])
        return aid, cid, {"title": title, "pages": pages, "desc": v.get("desc", ""),
                          "owner": v.get("owner", {}).get("name", ""),
                          "duration": v.get("duration", 0)}
    except Exception as e:
        print(f"  解析失败: {e}")
        return None, None, None


def fetch_subtitle(bvid, cid, mixin, s):
    """wbi接口拿字幕URL"""
    q = sign({"bvid": bvid, "cid": str(cid), "web_location": "333.1007"}, mixin)
    r = s.get("https://api.bilibili.com/x/player/wbi/v2", params=q,
              headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=20)
    d = r.json()
    if d.get("code") != 0:
        return None, f"code={d.get('code')} msg={d.get('message')}"
    subs = ((d.get("data") or {}).get("subtitle") or {}).get("subtitles") or []
    if not subs:
        return None, "no_subtitle"
    # 语言优先级
    pick = None
    for pref in ["zh-Hans", "zh-CN", "zh", "ai-zh"]:
        for x in subs:
            if x.get("lan") == pref:
                pick = x
                break
        if pick:
            break
    if not pick:
        pick = subs[0]
    url = pick.get("subtitle_url", "")
    if url.startswith("//"):
        url = "https:" + url
    return {"lan": pick.get("lan"), "url": url, "lan_doc": pick.get("lan_doc", "")}, None


def download_subtitle(url, bvid, s):
    for attempt in range(4):
        try:
            r = s.get(url, headers={"Referer": f"https://www.bilibili.com/video/{bvid}/"}, timeout=25)
            body = r.json().get("body", [])
            if body:
                return body
        except Exception as e:
            print(f"  下载字幕尝试{attempt+1}失败: {e}")
        time.sleep(3)
    return None


def fmt_ts(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}:{s:02d}"


def main():
    pool = BiliCookiePool()
    sel = json.load(open(OUT_DIR / "精选列表.json", encoding="utf-8"))
    items = sel["selected"]
    print(f"待抓字幕: {len(items)} 个")

    stats = {"success": 0, "no_sub": 0, "failed": 0, "skipped_exist": 0}

    for i, item in enumerate(items):
        bvid = item["bvid"]
        json_path = SUB_DIR / f"{bvid}.json"
        if json_path.exists():
            print(f"[{i+1}/{len(items)}] {bvid} 已存在，跳过")
            stats["skipped_exist"] += 1
            continue

        print(f"[{i+1}/{len(items)}] {bvid} | {item['title'][:40]}")
        cookie = pool.get_cookie()
        s = make_session(cookie)

        # 1. 拿aid/cid
        try:
            aid, cid, meta = fetch_cid(bvid, s)
        except Exception as e:
            print(f"  抓网页异常: {e}")
            aid, cid, meta = None, None, None
            pool.report_412()

        if not cid:
            print(f"  [失败] 拿不到cid")
            stats["failed"] += 1
            item["_subtitle_status"] = "no_cid"
            time.sleep(2)
            continue

        print(f"  aid={aid} cid={cid} duration={meta.get('duration') if meta else '?'}s")

        # 2. 拿wbi keys（每个cookie刷新一次）
        try:
            mixin = get_wbi_keys(s)
        except Exception as e:
            print(f"  wbi keys失败: {e}")
            pool.report_412()
            time.sleep(2)
            stats["failed"] += 1
            continue

        # 3. 抓字幕（多P只抓P1，因为精选视频都是单P）
        sub_info, err = fetch_subtitle(bvid, cid, mixin, s)
        if err:
            print(f"  [无字幕] {err}")
            stats["no_sub"] += 1
            item["_subtitle_status"] = f"no_subtitle:{err}"
            # 保存空标记
            json_path.write_text(json.dumps({
                "bvid": bvid, "aid": aid, "cid": cid, "meta": meta,
                "status": "no_subtitle", "error": err, "body": []
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(2)
            continue

        print(f"  字幕语言: {sub_info['lan']} | 下载中...")
        body = download_subtitle(sub_info["url"], bvid, s)
        if not body:
            print(f"  [失败] 下载字幕为空")
            stats["failed"] += 1
            time.sleep(2)
            continue

        # 4. 保存json
        result = {
            "bvid": bvid, "aid": aid, "cid": cid,
            "meta": meta, "subtitle_info": sub_info,
            "status": "ok", "segment_count": len(body),
            "body": body,
        }
        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        # 5. 保存txt（纯文本带时间戳）
        txt_lines = [f"# {meta.get('title','') if meta else ''}",
                     f"# UP主: {meta.get('owner','') if meta else ''}",
                     f"# 时长: {meta.get('duration',0) if meta else 0}s | 字幕段数: {len(body)}",
                     ""]
        for seg in body:
            txt_lines.append(f"[{fmt_ts(seg['from'])}] {seg['content']}")
        (SUB_DIR / f"{bvid}.txt").write_text("\n".join(txt_lines), encoding="utf-8")

        coverage = body[-1]["to"] / meta["duration"] if (meta and meta.get("duration")) else 0
        print(f"  完成: {len(body)}段, 覆盖率={coverage:.1%}")
        stats["success"] += 1
        pool.report_success()
        time.sleep(2)

    print(f"\n=== 字幕抓取统计 ===")
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    # 更新精选列表的字幕状态
    sel["subtitle_stats"] = stats
    (OUT_DIR / "精选列表.json").write_text(
        json.dumps(sel, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
