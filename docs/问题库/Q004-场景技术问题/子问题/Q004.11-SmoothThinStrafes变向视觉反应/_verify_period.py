# -*- coding: utf-8 -*-
"""复核：1) 长时程背景位移 2) bot 残差速度的主周期（自相关）"""
import os, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "YouTube原始数据", "_tmp")
files = sorted(glob.glob(os.path.join(D, "g_*.jpg")))
FPS = 60
Y0, Y1, X0, X1 = 4, 92, 20, 940

def load(p):
    a = np.asarray(Image.open(p).convert("L"), dtype=np.float32)[Y0:Y1, X0:X1]
    k = 31
    pad = np.pad(a, ((0, 0), (k // 2, k // 2)), mode="edge")
    cs = np.cumsum(pad, axis=1)
    cs = np.concatenate([np.zeros((cs.shape[0], 1)), cs], axis=1)
    return a - (cs[:, k:] - cs[:, :-k]) / k

def zncc(a, b, s):
    if s >= 0:
        x, y = a[:, s:], b[:, :a.shape[1] - s]
    else:
        x, y = a[:, :s], b[:, -s:]
    if x.shape[1] < 300:
        return -2.0
    x = x.ravel() - x.mean(); y = y.ravel() - y.mean()
    d = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / d) if d > 1e-9 else -2.0

print("=== 长时程背景位移（相机累计转角）===")
a = load(files[0])
for gap in (60, 180, 360, 600):
    if gap >= len(files):
        continue
    b = load(files[gap])
    best = max(((zncc(a, b, s), s) for s in range(-120, 121)), key=lambda x: x[0])
    px_per_deg = 960 / 103.7
    print(f"  {gap/FPS:5.1f}s 后：位移 {best[1]:+4d}px  zncc={best[0]:.3f}  "
          f"≈ {best[1]/px_per_deg:+.1f}°")

# 复算 bot 残差速度（与 _track_strafe3 同法），做自相关
from scipy import ndimage
def pill_x(p):
    a = np.asarray(Image.open(p).convert("L"), dtype=np.uint8)
    lab, n = ndimage.label(a < 48)
    best = None
    for idx, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        area = int((lab[sl] == idx).sum())
        if 28 <= h <= 130 and 5 <= w <= 26 and area >= 250 and 3.0 <= h / max(w, 1) <= 14.0:
            if best is None or area > best[0]:
                best = (area, sl, idx)
    if best is None:
        return None
    _, sl, idx = best
    ys, xs = np.nonzero(lab[sl] == idx)
    return float(xs.mean()) + sl[1].start

xs = [pill_x(p) for p in files]
ok = [i for i, v in enumerate(xs) if v is not None]
t = np.array(ok) / FPS
x = np.array([xs[i] for i in ok])
v = np.gradient(x, t)
pad = np.pad(v, 2, mode="edge")
vm = np.array([np.median(pad[i:i + 5]) for i in range(len(v))])
vm = vm - vm.mean()

ac = np.correlate(vm, vm, mode="full")[len(vm) - 1:]
ac = ac / ac[0]
print("\n=== 残差速度自相关（找主周期）===")
for lag in range(6, 120, 3):
    if lag < len(ac):
        print(f"  {lag/FPS:4.2f}s  {ac[lag]:+.3f}  {'#' * int(max(0, ac[lag]) * 50)}")
