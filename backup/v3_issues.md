
## V3 章节：2026-08-14 优化说明 + 速率分析 + 感悟记录

### V3-B1 Docker Desktop 再次停止（第 5 次）
- 现象：docker compose 报 npipe 连接失败，WSL docker-desktop 为 Stopped，无 Docker Desktop 进程。
- 原因：会话开始时 Docker Desktop 已被关闭（历史 V2-B8/B11/B13/B14 同类）。
- 解决：Start-Process 被拒绝访问后，改用 explorer.exe 启动 Docker Desktop，确认进程出现后再轮询 docker version。
- 验证：引擎 29.6.2 就绪，6 容器恢复。
- 影响：无。
- 经验：Start-Process 被拒时用 explorer.exe 启动 GUI 可行。

### V3-B2 PowerShell 写 JSON 带 BOM 导致 Node-RED JSON.parse 失败
- 现象：清空 imported_files.json 后 /import-aim 返回“保存导入记录失败: Unexpected token 在 JSON at position 0”。
- 原因：PowerShell Set-Content -Encoding UTF8 写入 BOM；Node-RED JSON.parse 不接受 BOM。
- 解决：改用 Python io.open(...,encoding='utf-8').write() 无 BOM 重写 state 文件。
- 验证：重新导入成功 imported:142。
- 影响：首次导入已写入 InfluxDB 但状态未保存；重导覆盖同点，无重复。

### V3-B3 逐杀“最慢10秒窗”被结尾 1 杀污染
- 现象：速率分析最慢10秒窗几乎都显示 1杀/10s，起始约 58s。
- 原因：滑窗把“末尾不足 10 秒”的窗口也算入，最后一个击杀单独成窗。
- 解决：仅统计 start <= maxOffset - 10 的完整 10 秒窗口。
- 验证：修复后最慢窗为 11-12 杀/10s，符合实际。
- 影响：无（分析文本阶段即发现并修复）。

### V3-B4 PowerShell Invoke-WebRequest 中文 body 乱码
- 现象：用 PowerShell 测试 /add-note 时中文变成问号。
- 原因：PS5.1 请求体未按 UTF-8 发送。
- 解决：用 Python urllib UTF-8 字节发送验证；浏览器页面不受影响（fetch 原生 UTF-8）。
- 验证：Python 发送中文正确入库入文。
- 影响：仅测试工具问题，非系统缺陷；临时乱码数据已清理。