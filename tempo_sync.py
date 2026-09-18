#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节拍同步器（aim_scenario.bpm 字段）
====================================
「节拍」= 每分钟拍子（出手）数，由用户手动指定；不提即一直延续上一次的值。
本脚本把配置里的节拍值，按生效日期写入 InfluxDB 的 aim_scenario 测量（field=bpm），
与 score/accuracy 同一条时间线上，供 Grafana 面板展示。

特性：
- 生效日期（from）决定历史点位取哪个节拍值；改配置后重跑会**覆盖重写**历史点位。
- 幂等：同 tags + 同时间戳重复写会覆盖，不会产生重复数据。

用法:
  python tempo_sync.py                                  # 按配置同步（默认）
  python tempo_sync.py --set "Pasu Voltaic Iron=45"     # 改某场景节拍（今天生效）后再同步
  python tempo_sync.py --json                           # 输出 JSON 统计
"""
import sys
import os
import csv
import io
import json
import urllib.request
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "tempo_config.json")

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"

TZ = datetime.timezone(datetime.timedelta(hours=8))


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def flux_query(script):
    url = f"{INFLUX}/api/v2/query?org={ORG}"
    req = urllib.request.Request(url, data=script.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    req.add_header("Accept", "application/csv")
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8", "replace")
    lines = [ln for ln in body.replace("\r", "").split("\n") if ln and not ln.startswith("#")]
    if not lines:
        return []
    rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
    return rows


def write_points(lines):
    if not lines:
        return
    body = "\n".join(lines).encode("utf-8")
    url = f"{INFLUX}/api/v2/write?org={ORG}&bucket={BUCKET}&precision=ms"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 204:
            raise RuntimeError(f"InfluxDB write HTTP {r.status}")


def esc(s):
    return str(s).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def effective_bpm(cfg, scenario, day):
    """按生效日期取该场景在 day（datetime.date）应使用的节拍值；无则 None。"""
    best = None
    for h in cfg.get("history", []):
        if h.get("scenario") != scenario:
            continue
        try:
            frm = datetime.date.fromisoformat(h["from"])
        except Exception:
            continue
        if frm <= day and (best is None or frm >= best[0]):
            best = (frm, h["bpm"])
    return best[1] if best else None


def parse_time(s):
    """RFC3339(UTC) -> 北京时间 datetime"""
    t = s.replace("Z", "+00:00")
    dt = datetime.datetime.fromisoformat(t)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(TZ)


def apply_set(cfg, expr):
    """--set "场景=节拍"：追加历史记录（今天生效）并更新 current。"""
    if "=" not in expr:
        raise SystemExit('--set 格式应为 "场景=节拍"，例如 --set "Pasu Voltaic Iron=45"')
    scene, val = expr.rsplit("=", 1)
    scene = scene.strip()
    bpm = float(val.strip())
    bpm_out = int(bpm) if float(bpm).is_integer() else bpm
    today = datetime.datetime.now(TZ).date().isoformat()
    cfg.setdefault("history", []).append({"scenario": scene, "bpm": bpm_out, "from": today})
    cfg.setdefault("current", {})[scene] = bpm_out
    save_config(cfg)
    return scene, bpm_out, today


def main():
    cfg = load_config()
    changed = None
    if "--set" in sys.argv:
        expr = sys.argv[sys.argv.index("--set") + 1]
        changed = apply_set(cfg, expr)

    scenes = list(cfg.get("current", {}).keys())
    if not scenes:
        print("配置里没有任何场景")
        return

    earliest = min(h["from"] for h in cfg.get("history", []))
    scene_filter = " or ".join([f'r.scenario == "{s}"' for s in scenes])
    script = (
        'from(bucket: "aim")\n'
        f'  |> range(start: {earliest}T00:00:00+08:00)\n'
        '  |> filter(fn: (r) => r._measurement == "aim_scenario" and r._field == "score")\n'
        f'  |> filter(fn: (r) => {scene_filter})\n'
        '  |> keep(columns: ["_time", "scenario", "session_id", "attempt_no"])'
    )
    rows = flux_query(script)

    lines = []
    per_scene = {}
    skipped = 0
    for r in rows:
        scene = r.get("scenario")
        try:
            dt = parse_time(r["_time"])
        except Exception:
            skipped += 1
            continue
        bpm = effective_bpm(cfg, scene, dt.date())
        if bpm is None:
            skipped += 1
            continue
        ts_ms = int(dt.timestamp() * 1000)
        lines.append(
            "aim_scenario,scenario=" + esc(scene)
            + ",session_id=" + esc(r.get("session_id", ""))
            + ",attempt_no=" + esc(r.get("attempt_no", ""))
            + ",source=tempo bpm=" + str(bpm) + " " + str(ts_ms)
        )
        per_scene[scene] = per_scene.get(scene, 0) + 1

    write_points(lines)

    out = {
        "ok": True,
        "message": "节拍同步完成",
        "changed": changed,
        "written": len(lines),
        "skipped": skipped,
        "perScene": per_scene,
        "current": cfg.get("current", {}),
        "accuracyStandard": cfg.get("accuracy_standard"),
    }
    if "--json" in sys.argv:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
