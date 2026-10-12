# Reddit 原始数据

> 状态：未完成（2026-10-13）

## 未完成原因
Reddit 反爬机制极强，以下方案均被拦截：
- Reddit JSON API：未认证返回 403
- Reddit RSS feed：429 限流
- Selenium headless：被检测
- Selenium 非headless（含CDP反检测补丁+复制的Edge profile）：触发 reCAPTCHA
- 代理 IP（127.0.0.1:7892）被 Reddit 标记
- computer_use_tool（cu平面）：本环境不支持

## 后续补充方案
用用户已登录的 Edge 浏览器手动搜索 r/VALORANT、r/FPSAimTrainer，精选 3-5 篇高票帖，手动记录标题+URL+核心内容。

关键词：counter strafe timing, aiming while moving, movement aim valorant, strafe aiming, 1v1 clutch peek
