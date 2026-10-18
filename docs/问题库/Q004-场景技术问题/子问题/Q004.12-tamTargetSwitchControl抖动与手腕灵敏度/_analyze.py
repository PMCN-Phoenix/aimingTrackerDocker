# -*- coding: utf-8 -*-
"""Q004.12 抖动量化：误差分布 / 抖动 RMS / 频谱 / 反向次数
关键前提：准星固定在屏幕正中，所以 e = 目标屏幕坐标 - (960,540) 就是「准星离目标多远」。
玩家已经锁住目标时（|e| 小），目标在屏幕上几乎不动 → e 的残余波动 = 纯手部抖动。
"""
import json, sys
import numpy as np
from scipy import signal

FOV_H = 103.0                       # KovaaK's 默认水平 FOV
PX_PER_DEG = (1920 / 2.0) / np.tan(np.radians(FOV_H / 2)) * np.pi / 180.0
CX, CY = 960.0, 540.0


def load(p):
    d = json.load(open(p, encoding="utf-8"))
    r = d["rows"]
    x = np.array([np.nan if a["x"] is None else a["x"] for a in r])
    y = np.array([np.nan if a["y"] is None else a["y"] for a in r])
    return x, y, d["fps"]


def runs(valid, minlen=1):
    out, s = [], None
    for i, v in enumerate(valid):
        if v and s is None:
            s = i
        if not v and s is not None:
            if i - s >= minlen:
                out.append((s, i))
            s = None
    if s is not None and len(valid) - s >= minlen:
        out.append((s, len(valid)))
    return out


def main(p):
    x, y, fps = load(p)
    ex, ey = x - CX, y - CY
    e = np.hypot(ex, ey)
    valid = np.isfinite(e)

    print(f"总帧 {len(x)}  有效 {valid.sum()} ({100*valid.mean():.1f}%)")
    print(f"|e|<10px 占全部帧 {100*np.nanmean(e<10):.1f}%   <20px {100*np.nanmean(e<20):.1f}%   "
          f"<40px {100*np.nanmean(e<40):.1f}%")
    print(f"|e| P50={np.nanmedian(e):.1f}  P90={np.nanpercentile(e,90):.1f} px")

    ENG = 40.0                      # 「贴身」阈值：4 个点半径
    eng = valid & (e < ENG)
    print(f"贴身帧(|e|<{ENG:.0f}px) {eng.sum()} ({100*eng.mean():.1f}%)，"
          f"其中 P50={np.nanmedian(e[eng]):.1f} P90={np.nanpercentile(e[eng],90):.1f} px")

    # ---------- 逐段高通，得到纯抖动 ----------
    win = int(round(0.25 * fps))        # 0.25 s ≈ 4 Hz 以上保留
    half = win // 2
    hp_all, seg_ok = [], []
    for a, b in runs(valid, minlen=win * 2):
        v = ex[a:b].copy()
        seg_e = e[a:b]
        # 移动平均（段内，避免 NaN 污染）
        k = np.ones(win) / win
        sm = np.convolve(v, k, mode="same")
        hp = v - sm
        # 只保留「窗口完全落在贴身区」的帧
        ok = np.ones(len(v), bool)
        for i in range(len(v)):
            lo, hi = max(0, i - half), min(len(v), i + half + 1)
            if not np.all(seg_e[lo:hi] < ENG):
                ok[i] = False
        if ok.sum() >= int(0.3 * fps):
            hp_all.append(hp[ok])
            seg_ok.append((a, b, ok))
    if hp_all:
        hp = np.concatenate(hp_all)
        jrms = float(np.sqrt(np.mean(hp ** 2)))
        print(f"\n【手抖 RMS】{jrms:.2f} px = {jrms/PX_PER_DEG:.2f}°   "
              f"(贴身帧 {len(hp)} 帧 = {len(hp)/fps:.1f}s)")
        print(f"   抖动峰峰值 P90-P10 = "
              f"{np.percentile(hp,90)-np.percentile(hp,10):.2f} px")

    # ---------- 频谱（Welch，固定 nperseg）----------
    NP = 64
    psds, fr = [], None
    for a, b, ok in seg_ok:
        v = ex[a:b][ok]
        v = v - v.mean()
        if len(v) < NP:
            continue
        f, P = signal.welch(v, fs=fps, nperseg=NP, noverlap=NP // 2)
        fr = f
        psds.append(P)
    if psds:
        P = np.mean(np.vstack(psds), axis=0)
        m = (fr >= 0.5) & (fr <= 28)
        tot = np.trapz(P[m], fr[m])
        print("\n【频谱能量占比】0.5–28 Hz")
        for lo, hi in [(0.5, 3), (3, 8), (8, 14), (14, 28)]:
            mm = (fr >= lo) & (fr < hi)
            print(f"   {lo:>4.1f}–{hi:<4.1f} Hz : {100*np.trapz(P[mm],fr[mm])/tot:5.1f}%")
        sub = fr > 1
        print(f"   峰值频率 ≈ {fr[sub][np.argmax(P[sub])]:.2f} Hz")

    # ---------- 误差反向次数 ----------
    cnt, tot_t = 0, 0.0
    for a, b, ok in seg_ok:
        v = ex[a:b][ok]
        dv = np.diff(v)
        sg = np.sign(dv)
        sg = sg[sg != 0]
        if len(sg) < 2:
            continue
        cnt += int(np.sum(sg[1:] != sg[:-1]))
        tot_t += len(v) / fps
    print(f"\n【误差反向】{cnt} 次 / {tot_t:.1f}s = {cnt/max(tot_t,1e-9):.1f} 次/秒")

    # ---------- 目标自身摆动：找「没在打」的点 ----------
    return dict(jrms=jrms if hp_all else None, nseg=len(seg_ok))


if __name__ == "__main__":
    main(sys.argv[1])
