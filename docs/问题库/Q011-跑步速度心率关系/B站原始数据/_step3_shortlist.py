# -*- coding: utf-8 -*-
"""Step3: 手工精选 14 个视频, 覆盖 6 大主题"""
import json, os

OUT = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q011-跑步速度心率关系\B站原始数据"
scored = json.load(open(os.path.join(OUT, "scored_top.json"), encoding="utf-8"))

# 按标题关键词挑
PICK_TITLES = [
    # (匹配关键词, 主题标签, 选择理由)
    ("心率区间与配速区间匹配不上", "1-基础关系+反面", "周观云:心率与配速对不上的原因,含心率设备不准讨论"),
    ("一个视频讲清楚关于运动心率", "1-基础关系", "鞋吧:469k播放,系统讲运动心率基础"),
    ("如何正确使用心率】燃脂", "1-基础关系", "子章老师:293k播放,最大心率怎么测+心率区间怎么用"),
    ("不同心率下身体会发生什么", "1-基础关系", "柏柏湾:911k播放,科普向心率与身体反应"),
    ("如何打造怪兽级有氧系统", "2-长时间有氧", "RunnerLoc:有氧系统打造,Z2堆量"),
    ("Zone 3（第三心率区间）", "2-长时间有氧+反面", "RunnerLoc:Zone3的价值与误解,灰区讨论"),
    ("从无效有氧到自杀式无氧", "2-长时间有氧", "斌哥:187k播放,心率区间过宽危害"),
    ("同样配速，心率越跑越高", "2-长时间有氧-心率漂移", "阿斗:心率漂移直接讲解"),
    ("乳酸阈值跑是什么？3*20min", "3-短时间间歇", "周观云:乳酸阈值跑实操"),
    ("t阈值跑:长跑训练的版本答案", "3-短时间间歇", "容易PB:乳酸阈值入门"),
    ("8个2000m间歇训练间歇是唯一", "3-短时间间歇", "钟佳萌:间歇提高乳酸阈值"),
    ("丹尼尔斯 VDOT 训练法实测", "4-通用方法-VDOT", "奥多夫斯基:VDOT实测记录"),
    ("VDOT跑力值超细解析", "4-通用方法-VDOT", "容易PB:VDOT跑力值解析"),
    ("储备心率区间】", "4-通用方法-心率区间", "RunnerLoc:储备心率区间设置"),
    ("快速计算心率区间", "5-实操换算", "songtao:储备心率快速计算"),
    ("教你设置佳明手表的心率区间", "5-实操换算", "非正常跑步数据研究所:设备实操"),
    ("有氧心率必须140以内", "6-反面意见", "西卡卡卡:跑圈谣言,心率140误区"),
    ("最高效有氧训练｜乳酸阈值", "3-短时间间歇", "ColdFire71:乳酸阈值教学"),
]

by_title = {}
for v in scored:
    by_title[v["title"][:30]] = v

selected = []
used_bv = set()
for kw, theme, reason in PICK_TITLES:
    found = None
    for v in scored:
        if kw in (v.get("title") or ""):
            found = v
            break
    if not found:
        print(f"[MISS] {kw}")
        continue
    if found["bvid"] in used_bv:
        continue
    used_bv.add(found["bvid"])
    found["_theme"] = theme
    found["_reason"] = reason
    selected.append(found)

print(f"\nSelected: {len(selected)} videos")
for i, v in enumerate(selected):
    print(f"{i+1:2d}. [{v['_theme']}] {v['bvid']} play={v.get('play')} dur={v.get('duration')}")
    print(f"    {v['title'][:60]}")
    print(f"    UP: {v.get('author','')}")

with open(os.path.join(OUT, "shortlist.json"), "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)
print(f"\n[saved] shortlist.json ({len(selected)} videos)")
