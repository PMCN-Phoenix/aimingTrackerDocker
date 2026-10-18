# -*- coding: utf-8 -*-
"""Steam 创意工坊搜索：KovaaK's (appid 824270) 找 tamTargetSwitch 系列场景 id"""
import re, sys, json, time
import requests

PROXIES = {"http": "http://127.0.0.1:7892", "https": "http://127.0.0.1:7892"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"}
s = requests.Session()
s.headers.update(UA)


def browse(text, page=1):
    url = ("https://steamcommunity.com/workshop/browse/?appid=824270"
           f"&searchtext={text}&browsesort=textsearch&section=readytouseitems&p={page}")
    r = s.get(url, proxies=PROXIES, timeout=30)
    r.raise_for_status()
    html = r.text
    # 每个条目：filedetails/?id=NNNN  +  <img ... alt="标题"
    out = []
    for m in re.finditer(r'sharedfiles/filedetails/\?id=(\d+)"[^>]*>(.{0,3000}?)</a>', html, re.S):
        fid, block = m.group(1), m.group(2)
        am = re.search(r'alt="([^"]+)"', block)
        title = am.group(1) if am else ""
        out.append((fid, title))
    # 去重保序
    seen, res = set(), []
    for fid, t in out:
        if fid in seen:
            continue
        seen.add(fid)
        res.append((fid, t))
    return res


def details(ids):
    """官方 GetPublishedFileDetails，拿标题+描述"""
    body = {"itemcount": str(len(ids))}
    for i, x in enumerate(ids):
        body[f"publishedfileids[{i}]"] = x
    r = s.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
               data=body, proxies=PROXIES, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("publishedfiledetails", [])


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "tamTargetSwitch"
    allres = []
    for p in (1, 2):
        try:
            got = browse(text, p)
        except Exception as e:
            print("browse fail", p, e)
            got = []
        print(f"--- page {p}: {len(got)} ---")
        for fid, t in got:
            print(fid, t)
        allres += got
        time.sleep(1)

    ids = [f for f, _ in allres]
    print("\n===== 官方描述 =====")
    rows = []
    for i in range(0, len(ids), 10):
        for d in details(ids[i:i + 10]):
            row = {
                "id": d.get("publishedfileid"),
                "title": d.get("title"),
                "time_created": d.get("time_created"),
                "subs": d.get("subscriptions"),
                "desc": (d.get("description") or "").strip(),
            }
            rows.append(row)
            print(f"\n[{row['id']}] {row['title']}  (订阅 {row['subs']})")
            if row["desc"]:
                print("  " + row["desc"].replace("\n", "\n  ")[:600])
        time.sleep(1)
    with open("steam_result.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n共 {len(rows)} 条 -> steam_result.json")
