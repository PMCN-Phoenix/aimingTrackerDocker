# -*- coding: utf-8 -*-
"""Q004.12 抖动量化 v2
e(t) = 准星(屏幕正中) 到「最近目标」的距离 —— 这就是玩家此刻的偏差。
所有目标位置逐帧保存，因此不需要连续性跟踪。
"""
import json, sys
import numpy as np
from scipy import signal

FOV_H = 103.0
PX_PER_DEG = (1920 / 2.0) / np.tan(np.radians(FOV_H / 2)) * np.pi / 180.0
CX, CY = 960.0, 540.0
ENG = 40.0          # 贴身阈值 px


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    return d["frames"], d["fps"]


def build(frames):
    n = len(frames)
    e = np.full(n, np.nan)
    ex = np.full(n, np.nan)
    ey = np.full(n, np.nan)
    idx = np.full(n, -1)
    nb = np.array([len(f) for f in frames])
    for i, f in enumerate(frames):
        if not f:
            continue
        d = [np.hypot(x - CX, y - CY) for x, y, a in f]
        j = int(np.argmin(d))
        e[i] = d[j]
        ex[i] = f[j][0] - CX
        ey[i] = f[j][1] - CY
        idx[i] = j
    return e, ex, ey, idx, nb


def runs(mask, minlen=1):
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s >= minlen:
                out.append((s, i))
            s = None
    if s is not None and len(mask) - s >= minlen:
        out.append((s, len(mask)))
    return out


def main(p):
    frames, fps = load(p)
    e, ex, ey, idx, nb = build(frames)
    v = np.isfinite(e)
    print(f"帧 {len(frames)}  有效 {v.sum()} ({100*v.mean():.1f}%)  "
          f"平均可见目标 {nb.mean():.2f} 个")

    for r in (10, 15, 20, 30, 40):
        print(f"  最近目标距离 < {r:>2} px 的帧占比: {100*np.nanmean(e<r):5.1f}%")
    print(f"  |e| P25={np.nanpercentile(e,25):.1f}  P50={np.nanmedian(e):.1f}  "
          f"P75={np.nanpercentile(e,75):.1f} px")

    eng = v & (e < ENG)
    # 只保留「最近目标身份稳定」的帧：相邻帧最近目标位移 < 60 px
    stable = np.zeros(len(e), bool)
    for i in range(1, len(e)):
        if eng[i] and eng[i - 1] and abs(ex[i] - ex[i - 1]) < 60 and abs(ey[i] - ey[i - 1]) < 60:
            stable[i] = True
    print(f"  贴身且稳定 {stable.sum()} 帧 = {stable.sum()/fps:.1f}s")

    # ---- 抖动 RMS（段内 0.25s 高通）----
    win = int(round(0.25 * fps))
    half = win // 2
    hps = []
    for a, b in runs(stable, minlen=win * 2):
        seg = ex[a:b]
        if np.any(~np.isfinite(seg)):
            continue
        sm = np.convolve(seg, np.ones(win) / win, mode="same")
        hp = seg - sm
        ok = np.ones(len(seg), bool)
        for i in range(len(seg)):
            lo, hi = max(0, i - half), min(len(seg), i + half + 1)
            if hi - lo < win:
                ok[i] = False
        if ok.sum() > 0:
            hps.append(hp[ok])
    if hps:
        hp = np.concatenate(hps)
        print(f"\n【手抖 RMS】{np.sqrt(np.mean(hp**2)):.2f} px = "
              f"{np.sqrt(np.mean(hp**2))/PX_PER_DEG:.2f}°  ({len(hp)} 帧 = {len(hp)/fps:.1f}s)")
        print(f"   峰峰 P90-P10 = {np.percentile(hp,90)-np.percentile(hp,10):.2f} px")

    # ---- 频谱 ----
    NP = 64
    psds, fr = [], None
    for a, b in runs(stable, minlen=NP):
        seg = ex[a:b]
        if np.any(~np.isfinite(seg)):
            continue
        seg = seg - seg.mean()
        f, P = signal.welch(seg, fs=fps, nperseg=NP, noverlap=NP // 2)
        fr = f
        psds.append(P)
    if psds:
        P = np.mean(np.vstack(psds), axis=0)
        m = (fr >= 0.5) & (fr <= 28)
        tot = np.trapezoid(P[m], fr[m])
        print("\n【频谱能量占比】0.5–28 Hz")
        for lo, hi in [(0.5, 3), (3, 8), (8, 14), (14, 28)]:
            mm = (fr >= lo) & (fr < hi)
            print(f"   {lo:>4.1f}–{hi:<4.1f} Hz : {100*np.trapezoid(P[mm],fr[mm])/tot:5.1f}%")
        s2 = fr > 1
        print(f"   峰值频率 ≈ {fr[s2][np.argmax(P[s2])]:.2f} Hz")

    # ---- 误差反向 ----
    cnt, tot_t = 0, 0.0
    for a, b in runs(stable, minlen=NP):
        seg = ex[a:b]
        if np.any(~np.isfinite(seg)):
            continue
        sg = np.sign(np.diff(seg))
        sg = sg[sg != 0]
        if len(sg) < 2:
            continue
        cnt += int(np.sum(sg[1:] != sg[:-1]))
        tot_t += len(seg) / fps
    print(f"\n【误差反向】{cnt} 次 / {tot_t:.1f}s = {cnt/max(tot_t,1e-9):.1f} 次/秒")

    # ---- 目标自身摆动：两目标间距（相机项抵消）----
    dx_runs, pair = [], None
    for i in range(len(frames)):
        f = frames[i]
        if len(f) != 2:
            pair = None
            continue
        f = sorted(f, key=lambda z: z[0])
        d = f[1][0] - f[0][0]
        if pair is None or abs(d - pair[-1]) > 25:
            if pair and len(pair) > 90:
                dx_runs.append(np.array(pair))
            pair = [d]
        else:
            pair.append(d)
    if pair and len(pair) > 90:
        dx_runs.append(np.array(pair))
    if dx_runs:
        print(f"\n【两点水平间距】{len(dx_runs)} 段，共 "
              f"{sum(len(x) for x in dx_runs)/fps:.1f}s")
        allv = np.concatenate([x - x.mean() for x in dx_runs])
        print(f"   波动 RMS {np.sqrt(np.mean(allv**2)):.2f} px，"
              f"P90-P10 {np.percentile(allv,90)-np.percentile(allv,10):.2f} px")
        ps, f2 = [], None
        for x in dx_runs:
            if len(x) < 128:
                continue
            x = x - x.mean()
            ff, PP = signal.welch(x, fs=fps, nperseg=128, noverlap=64)
            f2 = ff
            ps.append(PP)
        if ps:
            PP = np.mean(np.vstack(ps), axis=0)
            mm = (f2 > 0.4) & (f2 < 15)
            order = np.argsort(PP[mm])[::-1][:3]
            print("   主频（前 3）: " +
                  ", ".join(f"{f2[mm][k]:.2f} Hz" for k in order))


if __name__ == "__main__":
    main(sys.argv[1])
