# -*- coding: utf-8 -*-
"""加强版：只保留「窄且孤立」的深色竖条（= 目标杆），统计残差分布并列出误差最大的时刻。"""
import os, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "B站原始数据", "_tmp_bar")
files = sorted(glob.glob(os.path.join(TMP, "*.pgm")))
FPS = 10
Y0, Y1 = 158, 208
PX_PER_DEG = 640 / 103.7

rows = []
for idx, p in enumerate(files):
    a = np.asarray(Image.open(p), dtype=np.float32)
    col = a[Y0:Y1, :].mean(axis=0)
    c = int(np.argmin(col))
    thr = col[c] + 20
    # 连通宽度
    l = c
    while l > 0 and col[l - 1] < thr:
        l -= 1
    r = c
    while r < 639 and col[r + 1] < thr:
        r += 1
    width = r - l + 1
    # 孤立性：±25px 外的最暗值应明显更亮
    mask = np.ones(640, bool); mask[max(0, c - 25):c + 26] = False
    outside = col[mask].min()
    ok = (col[c] < 110) and (2 <= width <= 9) and (outside > col[c] + 45)
    rows.append((idx / FPS, float(c), width, col[c], outside, ok))

ok_rows = [r for r in rows if r[5]]
print(f"有效帧 {len(ok_rows)}/{len(rows)} ({len(ok_rows)/len(rows)*100:.0f}%)")
e = np.array([abs(r[1] - 320) for r in ok_rows])
print(f"|误差|：中位 {np.median(e):.1f}px  均值 {e.mean():.1f}px  P75 {np.percentile(e,75):.1f}  "
      f"P90 {np.percentile(e,90):.1f}  P99 {np.percentile(e,99):.1f}  max {e.max():.1f}")
print(f"换算角度：中位 {np.median(e)/PX_PER_DEG:.2f}°  P90 {np.percentile(e,90)/PX_PER_DEG:.2f}°  "
      f"max {e.max()/PX_PER_DEG:.2f}°")

print("\n误差最大的 15 帧：")
for t, c, w, v, out, _ in sorted(ok_rows, key=lambda r: -abs(r[1] - 320))[:15]:
    print(f"  t={t:5.1f}s  x={c:6.1f}  err={c-320:+6.1f}px  ({(c-320)/PX_PER_DEG:+5.2f}°)  宽{w}px 暗度{v:.0f}")

# 残差符号变化次数（= 修正方向翻转次数）
sign = np.sign([r[1] - 320 for r in ok_rows])
flips = int((np.diff(sign) != 0).sum())
print(f"\n误差符号翻转 {flips} 次 / {len(ok_rows)} 帧 = 每 10s 约 {flips/(len(ok_rows)/FPS)*10:.1f} 次")
