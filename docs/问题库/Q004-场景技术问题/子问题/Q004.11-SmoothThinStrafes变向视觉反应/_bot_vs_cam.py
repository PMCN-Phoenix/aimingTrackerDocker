# -*- coding: utf-8 -*-
"""第二窗口复核：bot 速度 vs 相机速度（同一套算法）"""
import os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 60
PX_PER_DEG = 960 / 103.7

def run(folder, label):
    files = sorted(glob.glob(os.path.join(HERE, "YouTube原始数据", folder, "g_*.jpg")))
    # --- bot ---
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
    vb = np.gradient(x, t)
    pad = np.pad(vb, 2, mode="edge")
    vb = np.array([np.median(pad[i:i + 5]) for i in range(len(vb))])

    # --- camera flow ---
    Y0, Y1, X0, X1 = 4, 92, 20, 940
    def load(p):
        a = np.asarray(Image.open(p).convert("L"), dtype=np.float32)[Y0:Y1, X0:X1]
        k = 31
        pp = np.pad(a, ((0, 0), (k // 2, k // 2)), mode="edge")
        cs = np.cumsum(pp, axis=1)
        cs = np.concatenate([np.zeros((cs.shape[0], 1)), cs], axis=1)
        return a - (cs[:, k:] - cs[:, :-k]) / k

    def zncc(a, b, s):
        if s >= 0:
            u, v = a[:, s:], b[:, :a.shape[1] - s]
        else:
            u, v = a[:, :s], b[:, -s:]
        if u.shape[1] < 300:
            return -2.0
        u = u.ravel() - u.mean(); v = v.ravel() - v.mean()
        d = np.sqrt((u * u).sum() * (v * v).sum())
        return float((u * v).sum() / d) if d > 1e-9 else -2.0

    prev = load(files[0]); sh = []
    for p in files[1:]:
        cur = load(p)
        best = max(((zncc(prev, cur, s), s) for s in range(-14, 15)), key=lambda z: z[0])
        sh.append(best[1]); prev = cur
    vc = np.array(sh, dtype=float) * FPS
    pad = np.pad(vc, 2, mode="edge")
    vc = np.array([np.median(pad[i:i + 5]) for i in range(len(vc))])

    print(f"\n=== {label} ({len(files)} 帧 / {len(files)/FPS:.1f}s) ===")
    print(f"bot   屏幕位移范围 {x.min():.0f}..{x.max():.0f}px  σ={x.std():.1f}px"
          f"  |v| 中位 {np.median(np.abs(vb)):.0f}px/s  P90 {np.percentile(np.abs(vb),90):.0f}px/s")
    print(f"相机  |v| 中位 {np.median(np.abs(vc)):.1f}px/s  P90 {np.percentile(np.abs(vc),90):.1f}px/s")
    print(f"      换算：bot |v| 中位 {np.median(np.abs(vb))/PX_PER_DEG:.1f}°/s，"
          f"相机 |v| 中位 {np.median(np.abs(vc))/PX_PER_DEG:.2f}°/s")
    ratio = np.median(np.abs(vb)) / max(np.median(np.abs(vc)), 1e-6)
    print(f"      bot/相机 速度比 ≈ {ratio:.1f}x")

run("_tmp", "窗口 A：40–52s")
run("_tmp2", "窗口 B：62–72s")
