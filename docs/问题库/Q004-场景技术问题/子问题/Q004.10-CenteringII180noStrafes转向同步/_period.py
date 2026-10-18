# -*- coding: utf-8 -*-
"""不依赖位移估计的周期性检验：画面在零位移下的自相似度 vs 时间间隔。
若镜头以 T 秒为周期来回扫，则 lag=T 处应出现相似度峰值。"""
import os, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, "B站原始数据", "_tmp_bar")
files = sorted(glob.glob(os.path.join(TMP, "*.pgm")))
FPS = 10

def load(i):
    a = np.asarray(Image.open(files[i]), dtype=np.float32)
    a = a[60:330, 30:610]                      # 去掉 HUD 与黑边
    a = a - a.mean()
    return a

base = load(150)                               # 15.0s
n = len(files)
print("lag(s)  zncc 与 t=15.0s 的帧")
for lag in range(0, 601, 5):
    if 150 + lag >= n:
        break
    b = load(150 + lag)
    d = np.sqrt((base * base).sum() * (b * b).sum())
    z = float((base * b).sum() / d)
    bar = "#" * int(max(0, z) * 60)
    print(f"{lag/FPS:6.1f}  {z:+.3f}  {bar}")
