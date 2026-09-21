#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日清单同步器（aim_daylist / aim_daylist_meta）
================================================
把 `Viscose基准-DayN-游玩清单.md` 里的任务表解析进 InfluxDB：
  - measurement aim_daylist     : tags {daylist, scenario, role}；fields {rounds, order, target_score, target_acc}
                                  （成员表 = "哪天的清单里有哪些场景"，供看板 D 的变量与重复行使用）
  - measurement aim_daylist_meta: tags {daylist, label}；fields {items, rounds_total}；timestamp = 清单生效日
                                  （供看板的"清单日"标记 / 日期排序 / 默认选中最新）

关键原则：**不给成绩数据打 daylist 标签**（同一场景会在多天清单里重复出现），
每日清单只是一张"视图定义"表。

用法:
  python daylist_sync.py                 # 扫描目录下所有 Viscose基准-Day*-游玩清单.md，幂等 upsert
  python daylist_sync.py --list          # 只列出解析结果，不写库
  python daylist_sync.py --date Day1=2026-09-18   # 记录某份清单的「实际执行日」
"""
import sys
import os
import re
import glob
import json
import urllib.request
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, "docs", "清单", "viscose训练提升清单日期推进")  # DayN 游玩清单目录
PATTERN = os.path.join(ROOT, "Viscose基准-Day*-游玩清单.md")

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
TZ = datetime.timezone(datetime.timedelta(hours=8))

# 实际执行日期覆盖（清单标题日期 ≠ 真练日期时用），持久化在 docker 目录
DATES_FILE = os.path.join(BASE, "daylist_dates.json")

ROLE_ORDER = {"热身": 0, "卡口": 1, "主项": 2, "巩固": 3}


def esc(s):
    return str(s).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def parse_file(path):
    text = open(path, encoding="utf-8").read()
    name = os.path.basename(path)

    m_day = re.search(r"Day\s*(\d+)", name)
    day_num = int(m_day.group(1)) if m_day else 0
    daylist = "Day%d" % day_num

    # 日期：优先标题行里的 （9/17），再退到正文的完整日期
    run_date = None
    first_line = text.split("\n")[0] if text else ""
    m_d = re.search(r"（\s*(\d{1,2})/(\d{1,2})\s*）", first_line)
    if m_d:
        run_date = datetime.date(datetime.date.today().year, int(m_d.group(1)), int(m_d.group(2)))
    if run_date is None:
        m_full = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
        if m_full:
            run_date = datetime.date(int(m_full.group(1)), int(m_full.group(2)), int(m_full.group(3)))
    if run_date is None:
        run_date = datetime.date.fromtimestamp(os.path.getmtime(path))

    # 清单名：优先同名的 playlist.json 里的 playlistName（去掉 "Viscose DayN - " 前缀）
    label = ""
    pl = os.path.join(ROOT, "Viscose基准-Day%d游玩清单.playlist.json" % day_num)
    if os.path.exists(pl):
        try:
            with open(pl, encoding="utf-8-sig") as fh:
                pname = json.load(fh).get("playlistName", "")
            label = re.sub(r"^Viscose\s+Day\s*\d+\s*[-－]\s*", "", pname).strip()
        except Exception:
            label = ""
    if not label:
        m_lab = re.search(r"Viscose\s+Day\s*\d+\s*[·\-]\s*([^\n（(]+)", text)
        if m_lab:
            label = m_lab.group(1).strip()

    items = []
    for line in text.split("\n"):
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        order = int(cells[0])
        m_sc = re.search(r"`([^`]+)`", cells[1])
        scenario = m_sc.group(1).strip() if m_sc else cells[1].strip()
        m_r = re.search(r"(\d+)", cells[2])
        rounds = int(m_r.group(1)) if m_r else 1
        desc = cells[3]

        role = "其他"
        for k in ROLE_ORDER:
            if k in desc:
                role = k
                break
        # 目标分：目标 **700** / 目标分 46 / 25 → **35**
        tscore = None
        m_t = re.search(r"目标\s*(?:分)?\s*\*{0,2}(\d+(?:\.\d+)?)", desc)
        if not m_t:
            m_t = re.search(r"→\s*\*{0,2}(\d+(?:\.\d+)?)\*{0,2}\s*[，,]", desc)
        if m_t:
            tscore = float(m_t.group(1))
        # 命中率门槛：必须是"≥/大于"口径（"命中率 96.2%"这种只是现状描述，不算门槛）
        tacc = None
        m_a = re.search(r"命中率[^。\n]{0,12}?[≥>]=?\s*\*{0,2}(\d+(?:\.\d+)?)", desc)
        if m_a:
            tacc = float(m_a.group(1))

        items.append({"order": order, "scenario": scenario, "rounds": rounds,
                      "role": role, "target_score": tscore, "target_acc": tacc})

    items.sort(key=lambda x: x["order"])
    return {"daylist": daylist, "label": label, "run_date": run_date,
            "file": name, "items": items}


def clear_measurement(m):
    """先清后写（幂等）—— 清单日期一变就会写出新时间戳的点，不清则新旧并存、看板行翻倍"""
    url = "%s/api/v2/delete?org=%s&bucket=%s" % (INFLUX, ORG, BUCKET)
    payload = json.dumps({"start": "1970-01-01T00:00:00Z", "stop": "2030-01-01T00:00:00Z",
                          "predicate": '_measurement="%s"' % m}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status


def write_points(lines):
    if not lines:
        return
    body = "\n".join(lines).encode("utf-8")
    url = "%s/api/v2/write?org=%s&bucket=%s&precision=s" % (INFLUX, ORG, BUCKET)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 204:
            raise RuntimeError("InfluxDB write HTTP %s" % r.status)


def load_date_overrides():
    """实际执行日期覆盖（清单标题写的日期 ≠ 真练的日期时用）

    存 `daylist_dates.json`：{"Day1": "2026-09-18"}，持久化 —— 否则每次
    update_all.py 重跑都会退回标题里的日期，看板 D 的「完成度」就统计不到。
    """
    if os.path.exists(DATES_FILE):
        try:
            return json.load(open(DATES_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_date_overrides(d):
    json.dump(d, open(DATES_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def main():
    # --date Day1=2026-09-18 （可重复）→ 记录该清单的实际执行日
    overrides = load_date_overrides()
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--date" and i + 1 < len(argv) and "=" in argv[i + 1]:
            day, date = argv[i + 1].split("=", 1)
            overrides[day.strip()] = date.strip()
            save_date_overrides(overrides)
            print("已记录 %s 的实际执行日 = %s" % (day.strip(), date.strip()))

    paths = sorted(glob.glob(PATTERN))
    if not paths:
        print("没有找到任何 Viscose基准-Day*-游玩清单.md")
        return
    lines = []
    summary = []
    for p in paths:
        d = parse_file(p)
        ov = overrides.get(d["daylist"])
        # 处理 exec_dates：支持单日字符串或多日列表
        if ov:
            if isinstance(ov, list):
                exec_dates = ov
                first = ov[0]
            else:
                exec_dates = [ov]
                first = ov
            y, m, dd = (int(x) for x in first.split("-"))
            d["run_date"] = datetime.date(y, m, dd)
        else:
            exec_dates = [d["run_date"].isoformat()]
        # 时间戳 = 清单生效日 00:00（本地时区）——**必须稳定**，否则重跑会产生重复点位。
        ts = int(datetime.datetime(d["run_date"].year, d["run_date"].month, d["run_date"].day,
                                   tzinfo=TZ).timestamp())
        total_rounds = sum(i["rounds"] for i in d["items"])
        summary.append({"daylist": d["daylist"], "label": d["label"], "run_date": str(d["run_date"]),
                        "items": len(d["items"]), "rounds": total_rounds, "file": d["file"]})
        for i in d["items"]:
            fields = ["rounds=%d" % i["rounds"], "order=%d" % i["order"]]
            if i["target_score"] is not None:
                fields.append("target_score=%g" % i["target_score"])
            if i["target_acc"] is not None:
                fields.append("target_acc=%g" % i["target_acc"])
            # 整行打包成 JSON 字符串（给看板 D 的自绘面板用，避免 tag 列把数据拆成多帧）
            row = {"daylist": d["daylist"], "label": d["label"], "run_date": d["run_date"].isoformat(),
                   "exec_dates": exec_dates,
                   "order": i["order"], "scenario": i["scenario"], "role": i["role"],
                   "rounds": i["rounds"], "target_score": i["target_score"], "target_acc": i["target_acc"]}
            js = json.dumps(row, ensure_ascii=False).replace("\\", "\\\\").replace('"', '\\"')
            fields.append('rowJson="%s"' % js)
            lines.append("aim_daylist,daylist=%s,scenario=%s,role=%s %s %d"
                         % (esc(d["daylist"]), esc(i["scenario"]), esc(i["role"]),
                            ",".join(fields), ts))
        # 计算 start_ts 和 end_ts（本地时区，第一天 00:00 到最后一天 23:59:59）
        first_y, first_m, first_d = (int(x) for x in exec_dates[0].split("-"))
        last_y, last_m, last_d = (int(x) for x in exec_dates[-1].split("-"))
        start_ts = int(datetime.datetime(first_y, first_m, first_d, 0, 0, 0, tzinfo=TZ).timestamp())
        end_ts = int(datetime.datetime(last_y, last_m, last_d, 23, 59, 59, tzinfo=TZ).timestamp())
        exec_dates_str = ",".join(exec_dates)
        lines.append("aim_daylist_meta,daylist=%s,label=%s items=%d,rounds_total=%d,run_date=\"%s\",exec_dates=\"%s\",start_ts=%d,end_ts=%d %d"
                     % (esc(d["daylist"]), esc(d["label"]), len(d["items"]), total_rounds,
                        d["run_date"].isoformat(), exec_dates_str, start_ts, end_ts, ts))

    if "--list" in sys.argv:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    import time as _t
    for m in ("aim_daylist", "aim_daylist_meta"):
        clear_measurement(m)
    _t.sleep(2)
    write_points(lines)
    print(json.dumps({"ok": True, "written": len(lines), "days": summary},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
