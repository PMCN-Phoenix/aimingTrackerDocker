# -*- coding: utf-8 -*-
"""Q004.12 目标自身摆动：用「两个目标之间的水平距离」抵消相机运动
相机运动是所有目标共有的，两点间距 dx = x2-x1 完全不含相机项 → 纯目标自身运动。
"""
import sys
import numpy as np
import cv2
from scipy import signal
from _detect import detect


def main(path, t0, dur, fps=60.0):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(t0 * fps))
    n = int(dur * fps)
    seq = []
    for _ in range(n):
        ok, fr = cap.read()
        if not ok:
            break
        seq.append(detect(fr))
    cap.release()
    print(f"读了 {len(seq)} 帧，平均 {np.mean([len(b) for b in seq]):.2f} 个目标")

    # 找一对「大部分时间都在」的目标：用第一帧的目标做种子，逐帧最近邻延续
    if not seq or not seq[0]:
        print("首帧没目标")
        return
    # 选两个初始相距最远的目标
    seeds = sorted(seq[0], key=lambda z: z[0])
    if len(seeds) < 2:
        print("首帧目标不足 2 个")
        return
    A = [seeds[0][0], seeds[0][1]]
    B = [seeds[-1][0], seeds[-1][1]]
    ax, ay, bx, by = [], [], [], []
    for blobs in seq:
        if not blobs:
            ax.append(np.nan); ay.append(np.nan); bx.append(np.nan); by.append(np.nan)
            continue
        ca = min(blobs, key=lambda z: np.hypot(z[0] - A[0], z[1] - A[1]))
        cb = min(blobs, key=lambda z: np.hypot(z[0] - B[0], z[1] - B[1]))
        if np.hypot(ca[0] - A[0], ca[1] - A[1]) > 200 or np.hypot(cb[0] - B[0], cb[1] - B[1]) > 200:
            ax.append(np.nan); ay.append(np.nan); bx.append(np.nan); by.append(np.nan)
            continue
        A = [ca[0], ca[1]]; B = [cb[0], cb[1]]
        ax.append(ca[0]); ay.append(ca[1]); bx.append(cb[0]); by.append(cb[1])

    ax, ay, bx, by = map(np.array, (ax, ay, bx, by))
    dx = bx - ax
    dy = by - ay
    ok = np.isfinite(dx)
    print(f"成对有效 {ok.sum()} 帧 ({100*ok.mean():.1f}%)")
    if ok.sum() < 120:
        return
    # 去均值后的变化 = 两个目标各自摆动的差
    v = dx[ok] - np.nanmean(dx[ok])
    print(f"两点水平间距 均值 {np.nanmean(np.abs(dx[ok])):.0f} px, "
          f"波动 RMS {np.sqrt(np.mean(v**2)):.2f} px, P90-P10 {np.percentile(v,90)-np.percentile(v,10):.2f} px")
    vy = dy[ok] - np.nanmean(dy[ok])
    print(f"两点垂直间距 波动 RMS {np.sqrt(np.mean(vy**2)):.2f} px")
    # 谱
    v = v - v.mean()
    f, P = signal.welch(v, fs=fps, nperseg=min(256, len(v)), noverlap=128)
    m = (f > 0.4) & (f < 20)
    top = np.argsort(P[m])[::-1][:5]
    print("水平间距波动 主频（前 5）:")
    for i in top:
        print(f"   {f[m][i]:.2f} Hz  power={P[m][i]:.1f}")
    vy2 = vy - vy.mean()
    f2, P2 = signal.welch(vy2, fs=fps, nperseg=min(256, len(vy2)), noverlap=128)
    m2 = (f2 > 0.4) & (f2 < 20)
    print("垂直间距波动 主频:", f"{f2[m2][np.argmax(P2[m2])]:.2f} Hz")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 10.0,
         float(sys.argv[3]) if len(sys.argv) > 3 else 15.0)
