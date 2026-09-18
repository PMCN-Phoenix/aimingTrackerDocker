#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清单同步器（scenario_lists.json ⇄ Node-RED flows.json）
=======================================================
「清单」是数据层概念：每个场景属于哪个清单，在导入时打 tag `list=<清单id>`。

  --build   从各数据源生成/更新 scenario_lists.json（唯一事实来源）
  默认      按 scenario_lists.json 更新 nodered_data/flows.json 的
            ALLOWED / CLICK_SCENARIOS / LIST_OF
  --check   只检查是否一致，不写文件

用法:
  python sync_lists.py --build
  python sync_lists.py            # 前先停 aim-nodered
"""
import sys
import os
import re
import json
import shutil
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
LISTS_JSON = os.path.join(BASE, "scenario_lists.json")
FLOWS = os.path.join(BASE, "nodered_data", "flows.json")
KOVAAKS_S2 = (r"D:/1_game/1_steam/steamapps/common/FPSAimTrainer/FPSAimTrainer"
              r"/Saved/SaveGames/Playlists/Viscose Benchmark S2 - Easier.json")

# ---- Voltaic Iron（原 12 场景，来自《整合练枪计划.md》）----
VOLTAIC_SCENARIOS = [
    "Centering 90 Easy+ No Strafes", "Air Voltaic Close Long Strafes Very Easy",
    "GP Far Long Strafes Easy", "GP Close Long Strafes Easy", "B90TI Iron",
    "Smoothbot Iron", "Pasu Voltaic Iron", "Tamspeed 2bp Iron",
    "Wide Wall 3 Targets TE", "1w2t TE Reload", "B90T Voltaic Easy Very Slow",
    "patTS Voltaic Iron",
]
VOLTAIC_CLICK = ["Pasu Voltaic Iron", "Tamspeed 2bp Iron", "Wide Wall 3 Targets TE",
                 "1w2t TE Reload", "B90T Voltaic Easy Very Slow", "patTS Voltaic Iron"]

# ---- Viscose S2 Easier：官方 4 大类 / 14 子类（来自 evxl.app charts 页）----
S2_GROUPS = {
    "CONTROL TRACKING": {
        "Arm": ["Smoothsphere Viscose Easier", "Whisphere Viscose Easier", "SmoothBot Perfected Easier"],
        "Wrist": ["Leapstrafes Control wobin Easier", "Controlsphere SuperbAim Viscose Easier",
                  "VT Controlsphere Viscose Easier"],
        "Fingertip": ["Air Angelic 4 Voltaic Easy 70%", "cloverRawControl Viscose Easier 50cm",
                      "Flower Easier 50cm"],
        "Blending": ["PGTI Voltaic Easy Smoother", "Air CELESTIAL No UFO Easier", "RawControlSphere Easier"],
    },
    "REACTIVE TRACKING": {
        "Control": ["Ground Plaza Sparky v3 Easy", "Air Spectral Easy 85%"],
        "Speed": ["VT Aether Bot 1 Easier", "Plink Palace Easy Less Blinks"],
        "Reading": ["Air Pure Easier No UFO", "Air Voltaic Invincible 4 Easier"],
    },
    "FLICK TECH": {
        "Speed": ["ww5t Voltaic Slightly Larger", "voxTargetSwitch 2 Large",
                  "aimerz+ Static Switching 6 Bot Slightly Larger"],
        "Stability": ["1w6ts reload v2 20% bigger", "beanTS Larger", "StaticSwitchingVox"],
        "Micro": ["1w2ts reload smallflicks larger", "eth Pasu Micro Easier", "waldoTS Novice"],
        "Post-Flick": ["kinTS Voltaic Easy 85%", "domiSwitch Easier", "B180T Voltaic Easy Slower"],
    },
    "CLICK TIMING": {
        "Reading": ["Pasu Voltaic Reload Easier", "VT Bounceshot Viscose Easier", "CatClick Easier"],
        "Precision": ["1w3ts Pasu Perfected Micro Goated Larger 80%", "Popcorn MV Easier",
                      "skyClick Goated Easier"],
        "Stability": ["VoxTS Click Easier", "VT Floating Heads Viscose Easier", "psalmTS Viscose Click Easier"],
    },
}

# 官方已给：14 个子类别的当前档位与进度%（2026-09-16 evxl 抓取）
S2_SUBRANK = {
    ("CONTROL TRACKING", "Arm"): ("Hare", 45), ("CONTROL TRACKING", "Wrist"): ("Hare", 23),
    ("CONTROL TRACKING", "Fingertip"): ("Ermine", 39), ("CONTROL TRACKING", "Blending"): ("Lemming", 97),
    ("REACTIVE TRACKING", "Control"): ("Ermine", 18), ("REACTIVE TRACKING", "Speed"): ("Ermine", 65),
    ("REACTIVE TRACKING", "Reading"): ("Ermine", 11),
    ("FLICK TECH", "Speed"): ("Ermine", 83), ("FLICK TECH", "Stability"): ("Fox", 54),
    ("FLICK TECH", "Micro"): ("Penguin", 34), ("FLICK TECH", "Post-Flick"): ("Penguin", 5),
    ("CLICK TIMING", "Reading"): ("Lemming", None), ("CLICK TIMING", "Precision"): ("Puffin", 7),
    ("CLICK TIMING", "Stability"): ("Hare", 57),
}

# S2 里要设节拍的点击/移动靶类（值先占位 None）
S2_TEMPO_PLACEHOLDER = [
    "Pasu Voltaic Reload Easier", "VT Bounceshot Viscose Easier", "CatClick Easier",
    "VoxTS Click Easier", "skyClick Goated Easier", "eth Pasu Micro Easier",
    "psalmTS Viscose Click Easier", "Popcorn MV Easier", "1w6ts reload v2 20% bigger",
    "1w2ts reload smallflicks larger",
]


def read_flows():
    with open(FLOWS, encoding="utf-8-sig") as f:
        return json.load(f)


def get_func(flows, node_id):
    for n in flows:
        if n.get("id") == node_id:
            return n
    raise KeyError(node_id)


def js_array(names):
    return "[" + ",".join(json.dumps(n, ensure_ascii=False) for n in names) + "]"


def flat(groups):
    return [s for sub in groups.values() for lst in (sub.values() if isinstance(sub, dict) else [sub])
            for s in lst]


def build():
    with open(KOVAAKS_S2, encoding="utf-8-sig") as fh:
        s2 = [x["scenario_name"] for x in json.load(fh)["scenarioList"]]
    want = flat(S2_GROUPS)
    if sorted(want) != sorted(s2):
        raise SystemExit("分组与清单不一致！多: %s  缺: %s"
                         % (sorted(set(want) - set(s2)), sorted(set(s2) - set(want))))

    with open(os.path.join(BASE, "tempo_config.json"), encoding="utf-8") as fh:
        vtempo = json.load(fh).get("current", {})

    doc = {
        "说明": "清单定义（唯一事实来源）。sync_lists.py --build 重建，默认同步进 Node-RED flows.json。",
        "lists": {
            "voltaic-iron": {
                "label": "Voltaic Iron", "dashboard": "aim-scenarios-v2",
                "scenarios": VOLTAIC_SCENARIOS, "click": VOLTAIC_CLICK, "tempo": vtempo,
            },
            "viscose-s2-easier": {
                "label": "Viscose S2 Easier", "dashboard": "viscose-s2-easier",
                "shareCode": "KovaaKsScreamingPulledEgg",
                "scenarios": s2, "click": s2,
                "tempo": {n: None for n in S2_TEMPO_PLACEHOLDER},
                "groups": S2_GROUPS,
                "subrank": {"%s|%s" % k: {"rank": v[0], "pct": v[1]} for k, v in S2_SUBRANK.items()},
            },
        },
    }
    with open(LISTS_JSON, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print("已生成", LISTS_JSON)
    print("  voltaic-iron:", len(VOLTAIC_SCENARIOS), "场景 /", len(VOLTAIC_CLICK), "解析击杀")
    print("  viscose-s2-easier:", len(s2), "场景 / 4 大类", len(S2_SUBRANK), "子类")
    for cat, subs in S2_GROUPS.items():
        print("   ", cat, "->", {k: len(v) for k, v in subs.items()})


def sync(check_only=False):
    with open(LISTS_JSON, encoding="utf-8") as fh:
        doc = json.load(fh)["lists"]

    all_names, click_names, list_of = [], [], {}
    for lid, d in doc.items():
        for n in d["scenarios"]:
            all_names.append(n)
            list_of[n] = lid
        click_names.extend(d.get("click") or [])
    click_names = sorted(set(click_names))

    flows = read_flows()
    node = get_func(flows, "aim-import-main")
    f = node["func"]
    new = f
    new = re.sub(r"const ALLOWED = \[.*?\];",
                 "const ALLOWED = " + js_array(all_names) + ";", new, count=1, flags=re.S)
    new = re.sub(r"const CLICK_SCENARIOS = \[.*?\];",
                 "const CLICK_SCENARIOS = " + js_array(click_names) + ";", new, count=1, flags=re.S)
    mapping = "const LIST_OF = " + json.dumps(list_of, ensure_ascii=False, separators=(",", ":")) + ";"
    if "const LIST_OF" in new:
        new = re.sub(r"const LIST_OF = \{.*?\};", mapping, new, count=1, flags=re.S)
    else:
        new = new.replace("const GAP_MS", mapping + "\nconst GAP_MS", 1)
    old_tag = "tags: { scenario: rec.scenario, session_id: rec.session_id, attempt_no: rec.attempt_no, source: 'stats' },"
    new_tag = ("tags: { scenario: rec.scenario, session_id: rec.session_id, attempt_no: rec.attempt_no, "
               "source: 'stats', list: LIST_OF[rec.scenario] || 'unknown' },")
    new = new.replace(old_tag, new_tag)

    changed = (new != f)
    print("场景总数:", len(all_names), "| 解析击杀:", len(click_names), "| flows 有改动:", changed)
    if check_only:
        return 0 if changed else 1
    if changed:
        shutil.copy(FLOWS, FLOWS + ".bak-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        node["func"] = new
        with open(FLOWS, "w", encoding="utf-8") as fh:
            json.dump(flows, fh, ensure_ascii=False, indent=4)
        print("flows.json 已更新（旧文件已备份）")
    else:
        print("flows.json 已是最新")
    return 0


if __name__ == "__main__":
    if "--build" in sys.argv:
        build()
    elif "--check" in sys.argv:
        sync(check_only=True)
    else:
        sync()
