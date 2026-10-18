# -*- coding: utf-8 -*-
"""Q004.12 目标检测 + 跟踪
KovaaK's tamTargetSwitch Control：黑色小球（目标）+ 上方血条 + 屏幕中心准星。
准星固定在屏幕正中 (960,540)，所以「误差 e = 球心 - 屏幕中心」就是玩家看到的偏差。
"""
import sys, json
import numpy as np
import cv2
from scipy import ndimage

W, H = 1920, 1080
CX, CY = W / 2.0, H / 2.0


def detect(bgr):
    """返回 [(x, y, area, w, h)]，只保留接近圆形的小黑块"""
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    b, gr, r = bgr[:, :, 0].astype(np.int16), bgr[:, :, 1].astype(np.int16), bgr[:, :, 2].astype(np.int16)
    dark = g < 48
    # 排除彩色像素（绿准星 / 红准星 / 橙色血条）
    colorful = (np.abs(gr - r) > 45) | (np.abs(gr - b) > 45) | (np.abs(r - b) > 45)
    dark &= ~colorful
    # 屏蔽 UI 区域（只屏蔽真正会误检的：顶部计时、左上计分板、右上 FPS、最底部条）
    dark[:62, :] = False
    dark[:150, :330] = False
    dark[:135, 1690:] = False
    dark[900:, :] = False

    # 准星压在球上会把它切成几块（红准星被 colorful 排除）→ 先闭运算补缝
    dark = ndimage.binary_closing(dark, structure=np.ones((5, 5), bool))

    lab, n = ndimage.label(dark)
    if n == 0:
        return []
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if not (8 <= h <= 46 and 8 <= w <= 46):
            continue
        if not (0.55 <= w / float(h) <= 1.80):
            continue
        m = (lab[sl] == i)
        area = int(m.sum())
        if area < 45:
            continue
        fill = area / float(w * h)
        if fill < 0.40:
            continue
        # 填洞（准星压在球上）
        mf = ndimage.binary_fill_holes(m)
        ys, xs = np.nonzero(mf)
        out.append((float(xs.mean()) + sl[1].start,
                    float(ys.mean()) + sl[0].start,
                    float(area), int(w), int(h), float(fill)))
    return out


def run(path, out_npz, stride=1, max_frames=10 ** 9):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    blobs = []
    idx = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if idx % stride == 0:
            blobs.append(detect(fr))
            frames.append(idx)
        idx += 1
        if idx >= max_frames:
            break
    cap.release()
    np.savez_compressed(out_npz, fps=fps, frames=np.array(frames),
                        blobs=np.array(blobs, dtype=object), allow_pickle=True)
    print(f"{path}: {idx} 帧 @ {fps:.2f} fps, 保留 {len(frames)} 帧, 平均 {np.mean([len(b) for b in blobs]):.2f} 个目标")


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
