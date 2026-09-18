# -*- coding: utf-8 -*-
import json, io
p = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\grafana\provisioning\dashboards\aim-scenarios.json"
d = json.load(io.open(p, encoding="utf-8"))
click = ["Pasu Voltaic Iron","Tamspeed 2bp Iron","Wide Wall 3 Targets TE","1w2t TE Reload","B90T Voltaic Easy Very Slow","patTS Voltaic Iron"]

max_y = max((pan["gridPos"]["y"] + pan["gridPos"]["h"]) for pan in d["panels"])
print("start y", max_y)

def target(scenario, attempt):
    return {
        "refId": attempt,
        "datasource": {"type": "influxdb", "uid": "influxdb-aim"},
        "query": 'option location = {zone: "Asia/Shanghai", offset: 8h}\nfrom(bucket: "aim")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r._measurement == "aim_kill" and r.scenario == "' + scenario + '" and r._field == "interval" and r.attempt_no == "' + attempt + '")\n  |> keep(columns: ["_time", "_value", "_field"])\n  |> map(fn: (r) => ({ r with _field: "第' + attempt + '次" }))\n  |> group(columns: ["_field"])',
        "hide": False
    }

def panel(scenario, idx):
    y = max_y + (idx // 2) * 7
    x = (idx % 2) * 12
    overrides = []
    for attempt, color in [("1", "#e53935"), ("2", "#fb8c00"), ("3", "#43a047")]:
        overrides.append({
            "matcher": {"id": "byName", "options": "第" + attempt + "次"},
            "properties": [
                {"id": "color", "value": {"fixedColor": color, "mode": "fixed"}},
                {"id": "custom.drawStyle", "value": "line"},
                {"id": "custom.showPoints", "value": "always"},
                {"id": "custom.lineWidth", "value": 1},
                {"id": "custom.pointSize", "value": 4},
            ]
        })
    return {
        "id": 300 + idx,
        "type": "timeseries",
        "title": scenario + " · 速率（击杀间隔）",
        "datasource": {"type": "influxdb", "uid": "influxdb-aim"},
        "description": "逐杀间隔（秒）；红=第1次 橙=第2次 绿=第3次",
        "gridPos": {"h": 7, "w": 12, "x": x, "y": y},
        "fieldConfig": {
            "defaults": {
                "color": {"mode": "palette-classic"},
                "custom": {
                    "drawStyle": "line",
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "fillOpacity": 0,
                    "showPoints": "always",
                    "pointSize": 4,
                    "spanNulls": False,
                    "stacking": {"mode": "none", "group": None},
                    "axisPlacement": "auto",
                    "scaleDistribution": {"type": "linear"}
                },
                "unit": "s",
                "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}
            },
            "overrides": overrides
        },
        "targets": [target(scenario, "1"), target(scenario, "2"), target(scenario, "3")],
    }

for idx, scenario in enumerate(click):
    d["panels"].append(panel(scenario, idx))

io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
print("added 6 rate panels, total panels", len(d["panels"]))