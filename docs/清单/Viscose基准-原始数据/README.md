# ⚠️ 本目录数据源警示（2026-10-29 定）

## `benches_full.json` —— 不是 Viscose S2，禁止作为 Viscose 阈值来源

- 它是 **Voltaic 主基准**（VoltaicHQ + legacy Voltaic KovaaK's benchmarks S3/S4，Iron 外推，见 `backup/mk_bench.py` 的 source 字段）
- **23 档**（Lemming…Seal 8 + Cinnabar…Silk 15，**无 Puffin、无 Viridian**），103 场景 / 3 难度
- 与 Viscose S2 的 39 个场景**零重名**

## Viscose S2 的唯一阈值来源

`S2-官方分类诊断.json`（本地冻结快照）+ evxl.app 实时页面（对账用）。

## 为什么保留这个文件而不是删除

1. `analyze_benchmark_20261008.py` 仍引用它（删除会使脚本断链）
2. 它是 Voltaic 主基准唯一留存的阈值数据，删除不可逆
3. 它本身没有"错"，只是**另一把尺子**——加此标记即消除误用风险

背景与量化核查见 `docs/问题库/Q028-Viscose阶梯合理性核查/Q028调研报告-Viscose阶梯合理性核查.md` §六。
