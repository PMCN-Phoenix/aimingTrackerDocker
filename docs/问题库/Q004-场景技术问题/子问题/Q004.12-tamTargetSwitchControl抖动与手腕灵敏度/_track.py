# -*- coding: utf-8 -*-
"""Q004.12 逐帧跟踪被瞄准的目标，输出误差信号 e(t)"""
import sys, json
import numpy as np
import cv2
from _detect import detect, CX, CY

MAXJUMP = 170.0     # 帧间跳变上限（超过视为换目标）
GAP = 4             # 允许丢失帧数


def track(path, out_json):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    rows = []       # (frame, x, y, nblob)
    prev = None
    lost = 0
    idx = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        blobs = detect(fr)
        pick = None
        if blobs:
            if prev is not None and lost <= GAP:
                cand = [(np.hypot(x - prev[0], y - prev[1]), x, y) for x, y, a, w, h, f in blobs]
                cand.sort()
                if cand[0][0] <= MAXJUMP:
                    pick = (cand[0][1], cand[0][2])
            if pick is None:
                # 重新选：离屏幕中心最近的那个
                cand = sorted([(np.hypot(x - CX, y - CY), x, y) for x, y, a, w, h, f in blobs])
                pick = (cand[0][1], cand[0][2])
            lost = 0
            prev = pick
        else:
            lost += 1
            if lost > GAP:
                prev = None
        rows.append((idx, pick[0] if pick else None, pick[1] if pick else None, len(blobs)))
        idx += 1
    cap.release()

    arr = []
    for f, x, y, n in rows:
        arr.append({"f": f, "x": x, "y": y, "n": n})
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump({"fps": fps, "n": len(arr), "rows": arr}, fh)
    valid = sum(1 for a in arr if a["x"] is not None)
    print(f"{path}: {len(arr)} 帧, 有效 {valid} ({valid/max(len(arr),1)*100:.1f}%), fps={fps:.2f}")


if __name__ == "__main__":
    track(sys.argv[1], sys.argv[2])
