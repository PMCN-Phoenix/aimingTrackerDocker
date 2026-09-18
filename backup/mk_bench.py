import json, io, os
base = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker"
os.makedirs(os.path.join(base, "reports"), exist_ok=True)
bench = {
    "_comment": "Voltaic reference thresholds. source=legacy Voltaic S3/S4 benchmarks, Iron band is an approximate extension below Bronze. null means no reliable official mapping; those scenarios use personal-history grading only.",
    "source": "https://github.com/VoltaicHQ + legacy Voltaic KovaaK's benchmarks (S3/S4), Iron extrapolated",
    "ranks": ["iron", "bronze", "silver", "gold", "platinum", "diamond"],
    "scenarios": {
        "Centering 90 Easy+ No Strafes": None,
        "Air Voltaic Close Long Strafes Very Easy": None,
        "GP Far Long Strafes Easy": None,
        "GP Close Long Strafes Easy": None,
        "B90TI Iron": None,
        "Smoothbot Iron": {"benchmark": "Smoothbot Voltaic Easy", "thresholds": [1400, 1700, 2100, 2400, 2800, 3100]},
        "Pasu Voltaic Iron": {"benchmark": "Pasu Voltaic Easy", "thresholds": [32, 40, 50, 56, 66, 75]},
        "Tamspeed 2bp Iron": {"benchmark": "Popcorn Voltaic Easy (approx)", "thresholds": [75, 100, 150, 200, 250, 310]},
        "Wide Wall 3 Targets TE": {"benchmark": "ww3t Voltaic", "thresholds": [70, 83, 93, 103, 113, 123]},
        "1w2t TE Reload": {"benchmark": "1w4ts Voltaic (approx)", "thresholds": [60, 70, 82, 91, 100, 110]},
        "B90T Voltaic Easy Very Slow": {"benchmark": "B180T Voltaic Easy", "thresholds": [32, 40, 51, 60, 69, 77]},
        "patTS Voltaic Iron": {"benchmark": "patTS Voltaic Easy", "thresholds": [55, 65, 80, 85, 91, 98]},
    },
}
p = os.path.join(base, "nodered_data", "benchmarks.json")
io.open(p, "w", encoding="utf-8").write(json.dumps(bench, ensure_ascii=False, indent=2))
print("wrote", p)