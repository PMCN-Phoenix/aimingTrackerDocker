# -*- coding: utf-8 -*-
"""Q004.12 只算屏幕中心 ROI：目标靠近准星时，暗色圆盘的质心就是目标中心。
好处：准星（彩色）压在目标上时只会挖个洞，填洞后质心不变 → 贴身时的抖动也能测到。
"""
import sys, json
import numpy as np
import cv2
from scipy import ndimage

W, H = 1920, 1080
CX, CY = W // 2, H // 2
R = 110                      # ROI 半宽


def roi_measure(bgr):
    y0, y1 = CY - R, CY + R
    x0, x1 = CX - R, CX + R
    sub = bgr[y0:y1, x0:x1]
    g = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY)
    b, gr, r = sub[:, :, 0].astype(np.int16), sub[:, :, 1].astype(np.int16), sub[:, :, 2].astype(np.int16)
    dark = g < 60
    colorful = (np.abs(gr - r) > 40) | (np.abs(gr - b) > 40) | (np.abs(r - b) > 40)
    dark &= ~colorful
    dark = ndimage.binary_closing(dark, structure=np.ones((5, 5), bool))
    lab, n = ndimage.label(dark)
    if n == 0:
        return None
    best = None
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if not (7 <= h <= 50 and 7 <= w <= 50):
            continue
        if not (0.5 <= w / float(h) <= 2.0):
            continue
        m = (lab[sl] == i)
        area = int(m.sum())
        if area < 40:
            continue
        if area > best[0] if best else True:
            best = (area, sl, i)
    if best is None:
        return None
    area, sl, i = best
    m = ndimage.binary_fill_holes(lab[sl] == i)
    ys, xs = np.nonzero(m)
    return (float(xs.mean()) + sl[1].start + x0,
            float(ys.mean()) + sl[0].start + y0,
            float(area))


def main(path, out):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    rows = []
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        m = roi_measure(fr)
        rows.append([round(m[0], 2), round(m[1], 2), int(m[2])] if m else None)
        i += 1
    cap.release()
    json.dump({"fps": fps, "n": i, "rows": rows}, open(out, "w", encoding="utf-8"))
    hit = sum(1 for x in rows if x)
    print(f"{path}: {i} 帧, ROI 内检出目标 {hit} ({100*hit/i:.1f}%) -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
