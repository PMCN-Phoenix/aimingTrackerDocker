
## 16. V3 验证记录（2026-08-14 优化说明 + 速率 + 感悟）

- 容器：6 容器全部 Up；Grafana /api/health ok；Node-RED 无启动错误。
- 导入改造：重导后 imported:142, kills:8186；aim_scenario 计数 284 不变（无重复），aim_kill 计数 16372（=8186点×2字段）；重复触发 imported:0, skipped:142。
- 逐杀解析：抽查 1w2t attempt 第2次前几杀 interval/offset 0→0、0.533→0.533、0.402→0.935，逻辑自洽。
- 持久化：docker restart aim-influxdb 后 aim_scenario=284、aim_kill=16372 不变。
- 分析：POST /analyze-aim 返回 12 场景评级；POST /analyze-aim?mode=weekly 生成周总结；reports/场景优化日志.md、每周训练总结.md 生成成功。
- 速率窗口：修复后最快/最慢 10 秒窗数值合理（如 patTS 最慢 11-12 杀/10s）。
- 感悟：POST /add-note 中文 UTF-8 写入 InfluxDB aim_note + reports/训练感悟日志.md 成功；测试数据已清理（aim_note 0 点，报告文件重置）。
- Grafana：看板 aim-scenarios-v2 从 24 面板增至 30（新增 6 个速率面板）；1w2t interval 30 天 597 点有数据。
- 隔离：training-* 三容器运行正常，未触碰。
- 结论：V3 全部验证绿灯。