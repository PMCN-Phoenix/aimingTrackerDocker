
## 6. V3 优化说明 / 速率分析 / 感悟

**入口**
- 训练分析页面：http://localhost:1881/analyze-aim-ui （按钮：生成今日分析 / 生成周总结）
- 命令行：
  - curl.exe -X POST http://localhost:1881/analyze-aim
  - curl.exe -X POST "http://localhost:1881/analyze-aim?mode=weekly"
- 感悟页面：http://localhost:1881/note-ui
- 感悟命令行：curl.exe -X POST http://localhost:1881/add-note -H "Content-Type: application/json" -d "{\"date\":\"2026-08-14\",\"scenario\":\"1w2t TE Reload\",\"note\":\"...\"}"

**输出文件（reports/ 目录）**
- 场景优化日志.md（每次训练分析）
- 每周训练总结.md（周总结）
- 训练感悟日志.md（日期 + 可选项目 + 感悟）

**速率分析范围**
- 6 个点击场景：Pasu Voltaic Iron、Tamspeed 2bp Iron、Wide Wall 3 Targets TE、1w2t TE Reload、B90T Voltaic Easy Very Slow、patTS Voltaic Iron。
- 指标：相邻击杀间隔（秒）；自动找最快/最慢连续 10 秒窗，与整场中位数对比。
- 跟枪 3 个（Centering 90、B90TI、Smoothbot）无逐杀行，不做速率。

**Voltaic 基准说明**
- 7 个场景有近似官方映射（见 nodered_data/benchmarks.json）；其余 5 个无可靠映射，用个人历史分位评级。
- 评级为近似参考，阈值可在 benchmarks.json 修改。

**周总结**
- 每周日 09:00 自动生成，也可手动触发。