# -*- coding: utf-8 -*-
"""
测「Smooth Thin Strafes Raspberry Easy」的变向节奏（v3）。
用 scipy.ndimage.label 找连通块，只保留「竖长条」形状的黑色块（= 目标胶囊）。
"""
import os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "YouTube原始数据", "_tmp")
files = sorted(glob.glob(os.path.join(D, "g_*.jpg")))
FPS = 60

def pill_x(p):
    a = np.asarray(Image.open(p).convert("L"), dtype=np.uint8)
    dark = a < 48
    lab, n = ndimage.label(dark)
    if n == 0:
        return None, 0
    best = None
    for sl, idx in zip(ndimage.find_objects(lab), range(1, n + 1)):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        area = int((lab[sl] == idx).sum())
        if not (28 <= h <= 130 and 5 <= w <= 26 and area >= 250):
            continue
        if not (3.0 <= h / max(w, 1) <= 14.0):
            continue
        score = area
        if best is None or score > best[0]:
            best = (score, sl, idx)
    if best is None:
        return None, 0
    _, sl, idx = best
    ys, xs = np.nonzero(lab[sl] == idx)
    return float(xs.mean()) + sl[1].start, len(xs)

rows = []
for i, p in enumerate(files):
    x, n = pill_x(p)
    rows.append((i / FPS, x, n))

valid = [(t, x) for t, x, n in rows if x is not None]
print(f"检出 {len(valid)}/{len(rows)}")
t = np.array([r[0] for r in valid])
x = np.array([r[1] for r in valid])
print(f"x 范围 {x.min():.0f}..{x.max():.0f}（960 宽，中心 480），标准差 {x.std():.1f}")

v = np.gradient(x, t)
def medf(a, k=5):
    pad = np.pad(a, k // 2, mode="edge")
    return np.array([np.median(pad[i:i + k]) for i in range(len(a))])
vm = medf(v, 5)
sm = np.convolve(vm, np.ones(9) / 9, mode="same")
print(f"|v| 中位 {np.median(np.abs(sm)):.1f} px/s，P90 {np.percentile(np.abs(sm),90):.1f}")

HY = 30.0
state, revs = 0, []
for i in range(len(sm)):
    if abs(sm[i]) < HY:
        continue
    sg = 1 if sm[i] > 0 else -1
    if state != 0 and sg != state:
        revs.append(t[i])
    state = sg
print(f"\n变向 {len(revs)} 次 / {t[-1]-t[0]:.1f}s")
d = np.diff(revs)
if len(d):
    print(f"间隔：均值 {d.mean():.2f}s 中位 {np.median(d):.2f}s min {d.min():.2f} max {d.max():.2f}")
    print("序列:", " ".join(f"{q:.2f}" for q in d))

print("\n前 5 秒速度曲线（每 1/30 s）:")
for i in range(0, min(len(t), 300), 2):
    bar = "#" * int(min(50, abs(sm[i]) / 10))
    print(f"  t={t[i]:5.2f} x={x[i]:6.1f} v={sm[i]:+7.1f} {bar}")
