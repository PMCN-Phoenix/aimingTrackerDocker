# -*- coding: utf-8 -*-
"""把手写「关联问题库」批注迁移到正式 annotation 块，并做往返验证。

用 stub 绕过 pydantic（本机无依赖，只测 markdown 层）。
"""
import sys, os, re, types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- stub pydantic 模型依赖 ----
stub = types.ModuleType("app.models.game_reflection")
stub.THEME_NAMES = {
    "warmup": "热身", "aim": "对枪/瞄准", "move": "身法/移动",
    "mind": "意识/决策", "map": "地图理解", "agent": "英雄/角色", "mindset": "心态/其他",
}
stub.THEME_ICONS = {
    "warmup": "🔥", "aim": "🎯", "move": "🏃", "mind": "🧠",
    "map": "🗺️", "agent": "🎭", "mindset": "💡",
}
stub.THEME_COLORS = {}
models_pkg = types.ModuleType("app.models")
models_pkg.game_reflection = stub
sys.modules["app.models"] = models_pkg
sys.modules["app.models.game_reflection"] = stub

from app.services import game_reflection_markdown as md

ANNOT_WATER = """> **关联问题库**：这条是 **Q016-疲劳状态下练枪有效性** 与 **Q011-跑步速度心率关系** 之间最低成本的一个「状态干预」数据点——不需要改动作、不需要换设备，只改输入。
>
> 机制侧有文献支撑：轻度脱水（约 1–2% 体重失水）即可损害认知表现与警觉性（*Eur J Clin Nutr* 2003「Impaired cognitive function and mental performance in mild dehydration」；Falcone et al. 2017 热+运动诱导的轻度脱水对认知功能的影响）。而瞄准是「视觉反应 + 精细运动」的串联，**反应时是最先退化的环节**，所以补水的收益会先体现在 Reflex Flick / 变向类场景，而不是静态点击类。
>
> **待验证**：练枪前 30 分钟补水 300–500 ml，对比同日 Avg TTK 与 Reflex Flick 分数；若差异稳定，可写进 Q016 的「训练前状态清单」。"""


ANNOT_POPCORN = """> **关联问题库**：这条是 tracking 类的「确定感时序」，把四条线串成一个循环——
> ① 上行段**欠瞄** = Q004.7 的「欠甩偏置」（修正欠甩=1 个事件，过冲=3 个事件）；
> ② **确定感到了再锁** = Q013 的「等确定感/等枪预判」窗口，而非无脑预压；
> ③ **锁住加速匹配** = speed match（ww3t 问答：先贴住再提速），也是 Q007「平滑后微调僵住」的反面解法；
> ④ 下落段**注意力放回准星等下一次上升** = Q017 的「外焦点」（注意力在准星/任务上防再投入），
> 也是 Q014.1「先降张力再动手」的节律版：跟着目标的呼吸节奏分配注意力，而不是全程死盯目标。"""


def extract_free_annotation(filepath: str) -> str:
    """从旧格式文件里提取游离的「关联问题库」引用块文本。"""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    m = re.search(r'((?:^> .*\n?)+)', raw, re.MULTILINE)
    return m.group(1).strip() if m and "**关联问题库**" in m.group(1) else ""


def migrate(date: str, annot_map: dict):
    items = md.read_date_reflections(date)
    print(f"[{date}] 解析 {len(items)} 条")
    changed = False
    for it in items:
        rid = it.get("id", "")
        if rid in annot_map and not it.get("annotation"):
            it["annotation"] = annot_map[rid]
            changed = True
            print(f"  挂载批注 -> {rid} ({len(annot_map[rid])} 字)")
    if changed:
        md.write_date_reflections(date, items)
        back = md.read_date_reflections(date)
        for it in back:
            print(f"  往返 {it.get('id')} annotation={'有' if it.get('annotation') else '无'}")
    return md.read_date_reflections(date)


# ---------- 1) 2026-10-18：多喝水（批注从 git b7ab9bf 恢复，硬编码在此） ----------
migrate("2026-10-18", {"ref_20261018_38777065": ANNOT_WATER})

# ---------- 2) 2026-10-19：popcorn（批注已被 08:43 重写吞掉，用之前抓取的原文重挂） ----------
p19 = md.get_markdown_path("2026-10-19")
free = extract_free_annotation(p19)
annot19 = free if free and "**关联问题库**" in free else ANNOT_POPCORN
print(f"\n[2026-10-19] 游离批注提取: {len(free)} 字; 使用来源: {'文件游离块' if free else '硬编码(已被重写吞掉,用抓取原文)'}")
migrate("2026-10-19", {"ref_20261019_66d9e27a": annot19})

# ---------- 3) 模拟导出路径：剥离 annotation 的裸数据整文件重写 ----------
print("\n[模拟导出]")
ok = True
for date in ("2026-10-18", "2026-10-19"):
    back = md.read_date_reflections(date)
    bare = [{k: v for k, v in it.items() if k != "annotation"} for it in back]
    md.write_date_reflections(date, bare)
    after = md.read_date_reflections(date)
    for it in after:
        has = bool(it.get("annotation"))
        print(f"  {date} {it.get('id')} {'保留' if has else '丢失'}")
        if not has:
            ok = False

print("\n结论:", "PASS——手写批注不再被整文件重写覆盖" if ok else "FAIL")
