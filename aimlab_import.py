#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aim Lab 练枪数据导入器（aimlab_task measurement）
==================================================
读 Aim Lab 本地 Replay JSON（AppData/LocalLow/Statespace/aimlab_tb/Users/*/Replay/*.json），
按练枪计划白名单（Sixshot 六目标 / Strafetrack 水平跟枪 / Multilinetrace 多段直线，预留 yay）
过滤后写入 InfluxDB（bucket=aim, measurement=aimlab_task）。

与 Kovaak's stats 导入（Node-RED /import-aim, aim_scenario）互相独立，互不影响。
"更新"流程 = python aimlab_import.py && curl -X POST http://localhost:1881/import-aim

用法:
  python aimlab_import.py              # 增量导入（默认）
  python aimlab_import.py --json       # 输出 JSON 统计
"""
import sys
import json
import glob
import urllib.request

INFLUX_WRITE = "http://127.0.0.1:8087/api/v2/write"
ORG = "aim-org"
BUCKET = "aim"
TOKEN = "aim-super-secret-token-2026"
PRECISION = "ms"  # Replay startedAt 为毫秒

REPLAY_GLOB = r"C:/Users/Rose/AppData/LocalLow/Statespace/aimlab_tb/Users/*/Replay/*.json"
STATE_FILE = r"D:/11.project/iwen-codex/codex-list/aim-tracker-docker/aimlab_imported.json"

# 白名单：练枪计划(aimlab练枪.md)对应任务 + 预留 yay
# taskName 与 taskId 任一命中即导入
ALLOWED_NAMES = {"Sixshot", "Strafetrack", "Multilinetrace"}
ALLOWED_IDS = {"sixshot", "strafetrack", "multilinetrace", "yay"}


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            st = json.load(f)
            if "files" not in st:
                st = {"files": {}}
            return st
    except Exception:
        return {"files": {}}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def write_influx(points):
    """points: list of (line_protocol_string)。批量写，失败抛异常。"""
    if not points:
        return
    body = "\n".join(points).encode("utf-8")
    url = f"{INFLUX_WRITE}?org={ORG}&bucket={BUCKET}&precision={PRECISION}"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "text/plain; charset=utf-8")
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status != 204:
            raise RuntimeError(f"InfluxDB write HTTP {r.status}")


def esc_tag(s):
    return s.replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def main():
    state = load_state()
    files = sorted(glob.glob(REPLAY_GLOB))
    new_points = []
    per_task = {}
    scanned = 0
    skipped = 0
    damaged = 0
    new_tasks = {}

    for fp in files:
        fname = fp.replace("\\", "/").rsplit("/", 1)[-1]  # xxx.json
        scanned += 1
        # 去重：文件名(uuid)已导入则跳过
        if fname in state["files"]:
            skipped += 1
            continue
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            damaged += 1
            continue
        task_name = str(d.get("taskName") or "")
        task_id = str(d.get("taskId") or "")
        # 白名单过滤
        if task_name not in ALLOWED_NAMES and task_id not in ALLOWED_IDS:
            skipped += 1
            continue
        score = d.get("score")
        pd = d.get("performanceData") or {}
        acc = pd.get("accTotal")
        started = d.get("startedAt")
        if score is None or acc is None or not started:
            skipped += 1
            continue
        score_f = float(score)
        acc_f = round(float(acc), 1)
        line = (
            f"aimlab_task,task={esc_tag(task_name)},taskId={esc_tag(task_id)},source=aimlab "
            f"score={score_f:g},accuracy={acc_f:g} {int(started)}"
        )
        new_points.append(line)
        new_tasks[fname] = {"task": task_name, "score": score_f, "time_ms": int(started)}
        per_task[task_name] = per_task.get(task_name, 0) + 1

    # 写库
    imported = len(new_points)
    if imported:
        write_influx(new_points)
        state["files"].update(new_tasks)
        save_state(state)

    result = {
        "ok": True,
        "message": "Aim Lab 导入完成",
        "scanned": scanned,
        "imported": imported,
        "skipped": skipped,
        "damaged": damaged,
        "perTask": per_task,
    }
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
