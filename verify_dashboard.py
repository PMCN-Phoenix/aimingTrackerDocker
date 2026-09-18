#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
看板原子检验器
==============
从 Grafana 取回指定看板的 JSON，逐个面板跑它的每条查询，输出：
  面板 id / 标题 / 类型 / 查询条数 / 返回帧数 / 是否有数据 / 错误信息
变量（$day、$scenario 等）用 --var 传入替换。

用法:
  python verify_dashboard.py --uid viscose-s2-easier
  python verify_dashboard.py --uid viscose-daylist --var day=Day1 --var "scenario=Pasu Voltaic Reload Easier"
  python verify_dashboard.py --uid viscose-s2-easier --json
"""
import sys
import json
import base64
import urllib.request
import urllib.error

GRAFANA = "http://127.0.0.1:3001"
AUTH = base64.b64encode(b"admin:admin").decode()


def get_dashboard(uid):
    req = urllib.request.Request("%s/api/dashboards/uid/%s" % (GRAFANA, uid))
    req.add_header("Authorization", "Basic " + AUTH)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))["dashboard"]


def ds_query(flux, frm, to):
    payload = {"queries": [{"refId": "A", "datasource": {"type": "influxdb", "uid": "influxdb-aim"},
                            "query": flux, "rawQuery": True}], "from": frm, "to": to}
    req = urllib.request.Request(GRAFANA + "/api/ds/query",
                                 data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Authorization", "Basic " + AUTH)
    req.add_header("Content-Type", "application/json")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))["results"]["A"], None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return json.loads(body)["results"]["A"], None
        except Exception:
            return None, "HTTP %s: %s" % (e.code, body[:200])


def subst(text, variables):
    out = text
    for k, v in variables.items():
        out = out.replace("${%s}" % k, v).replace("$%s" % k, v)
    return out


def main():
    args = sys.argv[1:]
    uid = None
    variables = {}
    as_json = "--json" in args
    i = 0
    while i < len(args):
        if args[i] == "--uid":
            uid = args[i + 1]; i += 2
        elif args[i] == "--var":
            k, v = args[i + 1].split("=", 1); variables[k] = v; i += 2
        else:
            i += 1
    if not uid:
        raise SystemExit("用法: python verify_dashboard.py --uid <dashboard-uid> [--var k=v]")

    dash = get_dashboard(uid)
    time_range = dash.get("time") or {"from": "now-6h", "to": "now"}
    frm, to = time_range.get("from", "now-6h"), time_range.get("to", "now")
    results = []
    flat = []
    for p in dash.get("panels", []):
        if p.get("type") == "row":
            for sp in p.get("panels", []) or []:
                flat.append((sp, p.get("title")))
        else:
            flat.append((p, None))
    for p, row_title in flat:
        for t in p.get("targets", []) or []:
            flux = subst(t.get("query", ""), variables)
            if not flux.strip():
                continue
            res, err = ds_query(flux, frm, to)
            frames = (res or {}).get("frames", [])
            series_err = (res or {}).get("error")
            rows = 0
            for f in frames:
                vals = f.get("data", {}).get("values") or []
                # 一帧里可能有多个字段（时间+值），取最长字段的行数
                n = max([len(v) for v in vals if isinstance(v, list)] or [0])
                rows += n
            results.append({
                "panel": p.get("id"),
                "title": (row_title + " / " if row_title else "") + (p.get("title") or ""),
                "type": p.get("type"),
                "refId": t.get("refId"), "frames": len(frames), "rows": rows,
                "ok": bool(frames) and rows > 0 and not series_err and not err,
                "empty": (not series_err and not err and rows == 0),
                "error": err or series_err or "",
            })
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("看板 %s（%s）| 时间范围 %s → %s" % (uid, dash.get("title"), frm, to))
    bad = empty = 0
    for r in results:
        flag = "OK  " if r["ok"] else ("EMPTY" if r.get("empty") else "FAIL")
        if flag == "FAIL":
            bad += 1
        elif flag == "EMPTY":
            empty += 1
        print("  [%s] id=%-4s %-28s %-22s 帧=%-3d 行=%-4d %s"
              % (flag, r["panel"], (r["title"] or "")[:26], r["type"][:20], r["frames"], r["rows"],
                 r["error"][:60] if flag == "FAIL" else ("返回空（可能该时段确实无数据）" if flag == "EMPTY" else "")))
    print("  合计 %d 条查询：通过 %d，空 %d，失败 %d" % (len(results), len(results) - bad - empty, empty, bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
