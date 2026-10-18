# -*- coding: utf-8 -*-
"""Q004.12 逐帧保存「所有」目标位置。
不再用连续性跟踪（换目标时会锁死旧目标），改为每帧记录全部目标，
分析时用「离屏幕中心最近的那个」= 玩家此刻在打的目标。
"""
import sys, json
import numpy as np
import cv2
from _detect import detect

path, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(path)
fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
i = 0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    b = detect(fr)
    frames.append([[round(x, 1), round(y, 1), int(a)] for x, y, a, w, h, f in b])
    i += 1
cap.release()
json.dump({"fps": fps, "n": i, "frames": frames}, open(out, "w", encoding="utf-8"))
print(f"{path}: {i} 帧, 平均 {np.mean([len(f) for f in frames]):.2f} 个目标 -> {out}")
