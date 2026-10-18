# -*- coding: utf-8 -*-
"""最终指标：准星-目标偏差分布 + 目标高速运动的时间占比 + 变向间隔"""
import os, glob
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 60
PX_PER_DEG = 960 / 103.7
CENTER = 480.0

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
    return float(xs.mean()) + sl[1].start, (sl[1].stop - sl[1].start), (sl[0].stop - sl[0].start)

for folder, label in (("_tmp", "A 40–52s"), ("_tmp2", "B 62–72s")):
    files = sorted(glob.glob(os.path.join(HERE, "YouTube原始数据", folder, "g_*.jpg")))
    res = [pill_x(p) for p in files]
    ok = [i for i, r in enumerate(res) if r]
    t = np.array(ok) / FPS
    x = np.array([res[i][0] for i in ok])
    w = np.array([res[i][1] for i in ok])
    h = np.array([res[i][2] for i in ok])
    e = np.abs(x - CENTER)

    v = np.gradient(x, t)
    pad = np.pad(v, 2, mode="edge")
    v = np.array([np.median(pad[i:i + 5]) for i in range(len(v))])

    print(f"\n===== 窗口 {label}（{len(files)/FPS:.1f}s）=====")
    print(f"目标屏幕尺寸（960 宽标尺）：宽 {np.median(w):.0f}px（{np.median(w)/PX_PER_DEG:.2f}°）"
          f"  高 {np.median(h):.0f}px")
    print(f"目标 x：均值 {x.mean():.0f}  范围 {x.min():.0f}–{x.max():.0f}  σ={x.std():.1f}px"
          f"（{x.std()/PX_PER_DEG:.2f}°）")
    print(f"准星-目标偏差 |e|：中位 {np.median(e):.1f}px（{np.median(e)/PX_PER_DEG:.2f}°）"
          f"  P75 {np.percentile(e,75):.1f}  P90 {np.percentile(e,90):.1f}  max {e.max():.1f}")
    print(f"  |e| < 6px 占比 {100*(e<6).mean():.0f}%   <12px {100*(e<12).mean():.0f}%"
          f"   <20px {100*(e<20).mean():.0f}%")
    print(f"目标速度 |v|：中位 {np.median(np.abs(v)):.0f}px/s（{np.median(np.abs(v))/PX_PER_DEG:.1f}°/s）"
          f"  P90 {np.percentile(np.abs(v),90):.0f}px/s（{np.percentile(np.abs(v),90)/PX_PER_DEG:.1f}°/s）")
    print(f"  |v|>150px/s 时间占比 {100*(np.abs(v)>150).mean():.0f}%"
          f"   |v|>250px/s {100*(np.abs(v)>250).mean():.0f}%")

    # 变向
    sm = np.convolve(v, np.ones(7)/7, mode="same")
    HY = 60.0
    state, revs = 0, []
    for i in range(len(sm)):
        if abs(sm[i]) < HY:
            continue
        sg = 1 if sm[i] > 0 else -1
        if state != 0 and sg != state:
            revs.append(t[i])
        state = sg
    d = np.diff(revs)
    print(f"变向 {len(revs)} 次 → 中位间隔 {np.median(d):.2f}s，均值 {d.mean():.2f}s"
          f"（{len(revs)/(t[-1]-t[0]):.1f} 次/秒）")
