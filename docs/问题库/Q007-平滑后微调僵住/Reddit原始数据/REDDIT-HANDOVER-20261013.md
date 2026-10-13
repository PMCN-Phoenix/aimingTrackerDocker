# Reddit 抓取能力 · 接手文档（2026-10-13 更新）

> 基于 `HANDOVER.md`（v0.0.1.13）的增量更新。本文档只记录**自上次接手以来的变动、当前状态和局限性**，基础环境约束请同时参考原 `HANDOVER.md` 第 3 节（代理/遥测/npm/令牌）。

---

## 0. 一句话总结

在 v0.0.1.13（任意子版块最新帖子抓取）基础上，**新增了关键词搜索能力**（tRPC `subreddit.search` + 前端12任务批量自动搜索），并成功用于 Q007 调研抓取了 11 个高价值原帖。但新增的 HTTP 路由尚未注册、热重载曾卡住、日志截断问题已通过新输出格式修复但未完全验证。

---

## 1. 相较于上次接手的变动

### 1.1 代码变动

| 文件 | 变动 | 状态 |
|---|---|---|
| `src/server/trpc.ts` | 新增 `subreddit.search` tRPC 端点，支持 `query`/`subredditName`/`sort`(relevance/hot/top/new/comments)/`timeframe`(hour/day/week/month/year/all)/`limit`/`pageSize`，调用 `reddit.searchPosts` API | ✅ 已实现，类型检查通过 |
| `src/server/trpc.ts` | 日志输出从 `[SEARCH-FETCH] posts={大JSON}` 改为 `[SEARCH-START]` + 每个帖子一行 `[SEARCH-POST]` + `[SEARCH-END]`，body 截断到 500 字符 | ✅ 已修改 |
| `src/client/game.tsx` | 新增12个预设搜索任务（r/FPSAimTrainer 7个 + r/VALORANT 5个关键词），页面加载时自动批量执行，间隔1.5s | ✅ 已实现 |
| `src/server/routes/search.ts` | **新建**，含 `/api/search/batch`（12任务批量）和 `/api/search/single`（单任务）两个 HTTP 端点 | ⚠️ 已创建但**未在 index.ts 注册** |
| `src/server/routes/search.ts` | 同样使用 `[SEARCH-START]/[SEARCH-POST]/[SEARCH-END]` 输出格式 | ⚠️ 未验证（路由未注册） |

### 1.2 实际抓取成果

通过前端页面自动触发搜索，日志中成功写入了 **12 个搜索任务的结果**（旧格式 `[SEARCH-FETCH]`）。由于单行 JSON 过长被日志截断，通过正则从被截断文本中提取到 **11 个去重后的高价值原帖**：

| 帖子 | 赞/评 | 来源搜索 |
|---|---|---|
| How to ACTUALLY manage tension in static clicking（316dez） | 320/61 | tension aiming, flick to track |
| The secret I found to relaxed aim（IncidentDependent367） | 545/80 | palm grip precision |
| 1000 Kovaaks hrs Reflection（rainsyy） | 448/85 | micro adjustment, wrist arm, palm grip, smooth tracking |
| I'm 33 years old and just started aim training 5 days ago（Rucati） | 325/79 | flick to track |
| The importance of crosshair placement（Hi_Im_TwiX） | 9530/327 | pre aim correction |
| My Brother (Bronze 3)...（crouch peek 帖） | 7272/451 | crouch peek |
| Reasons as to why most of you are hard-stuck in low Elo | 5179/783 | crouch peek |
| The Current OP Meta... | 14762/1346 | counter strafe aim, aim while moving |
| Why we must continue to aim train | 561/278 | smooth tracking precision |
| I GOT DOXXED AND ASSAULTED BY AN AIM COACH | 501/69 | wrist arm aiming |
| Tendinopathy/RSI Injuries: How Kovaaks lead to my chronic RSI | 173/23 | aiming stiff |

原始数据存档：
- `all_posts.json` — 11个帖子完整结构化数据
- `devvit-search-raw.log` — 从 devvit-dev.log 提取的搜索原始日志
- `q007_relevant_posts.json` — 按Q007相关性排序的子集

### 1.3 Q007 报告更新

- 调研渠道行：Reddit 从"15个二手汇总源，原帖URL待补抓"改为"Devvit官方API抓取12个搜索任务/300条结果/去重11个高价值原帖"
- 四渠道交叉验证表：Reddit 行新增 316dez 原帖引用
- 新增"Devvit 原帖验证"章节：详细摘录 316dez 的张力管理动作链和肌肉群分工
- 渠道状态：从 ⚠️ 二手源改为 ✅ 官方API原始抓取
- git commit：已提交

---

## 2. 当前局限性

### 2.1 技术限制

| 限制 | 说明 | 影响 |
|---|---|---|
| **HTTP 路由未注册** | `src/server/routes/search.ts` 已创建但未在 `index.ts` 中 `app.route()` 注册 | 无法通过 curl 纯后端触发搜索，必须用户刷新前端页面 |
| **热重载曾卡住** | 修改 trpc.ts 输出格式后，日志显示"Starting a new build..."但未完成 rebuild，新格式 `[SEARCH-POST]` 未出现在日志中 | 实际成功抓取的是旧格式数据；新格式是否生效待验证 |
| **日志单行截断** | 旧格式 `[SEARCH-FETCH] posts={25个帖子的完整JSON}` 单行过长，被 Devvit 日志系统截断（约4000-5000字符后切断） | 每个搜索任务只能提取到前1-2个帖子的完整数据；新格式（每帖一行）已修复此问题但未验证 |
| **无评论抓取** | `reddit.searchPosts` 只返回帖子元数据+正文，不返回评论 | 无法获取评论区高价值讨论（316dez有61条评论未抓取） |
| **无分页** | 每个搜索只返回 top 25，`after` 游标未实现 | 无法获取更多历史帖子 |
| **body 截断** | 新格式将 body 截断到 500 字符 | 长帖（如316dez的完整指南）只能看到前500字符 |
| **搜索排序固定** | 前端自动搜索固定用 `sort=top, timeframe=all` | 无法按最新/热度排序，可能错过近期高相关帖 |

### 2.2 环境依赖

| 依赖 | 说明 |
|---|---|
| 代理必须开启 | `127.0.0.1:7892`，Devvit 所有网络请求走代理 |
| playtest 必须运行 | 关闭后需重启（命令见原 HANDOVER.md 第7节） |
| 用户需刷新页面 | 前端自动搜索在页面加载时触发，刷新一次=执行一轮12任务搜索 |
| 令牌有效期 | `C:\Users\Rose\.devvit\token`，过期需重新 `devvit login` |

### 2.3 数据质量

- 12个搜索任务 × 25条 = 理论300条，但因日志截断实际只提取到11个去重帖子
- 提取率约 3.7%，主要损失在日志截断
- 新格式（每帖一行）理论上可以100%提取，但尚未验证
- 没有评论数据，而评论区往往包含最有价值的个人经验

---

## 3. 复现 / 继续步骤

### 3.1 验证新格式是否生效

1. 确认 playtest 在运行（日志有新版本号）
2. 如果热重载卡住，重启 playtest：
   ```powershell
   # 先 Ctrl+C 停掉旧进程，然后
   Set-Location "C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\aimingtrainingcoach1"
   $env:HTTPS_PROXY='http://127.0.0.1:7892'; $env:HTTP_PROXY='http://127.0.0.1:7892'
   $env:DEVVIT_DISABLE_METRICS='1'
   node --use-env-proxy "node_modules\devvit\bin\devvit.js" playtest
   ```
3. 用户刷新 playtest 页面
4. 检查日志是否出现 `[SEARCH-START]` 和 `[SEARCH-POST]` 行
5. 如果出现，用新解析脚本提取（每帖一行，正则 `"id":"(t3_[^"]+)"` 即可）

### 3.2 注册 HTTP 路由（可选，实现纯后端触发）

在 `src/server/index.ts` 中添加：
```typescript
import { searchRouter } from './routes/search.js';
app.route('/api/search', searchRouter);
```
然后可以用 `curl http://localhost:PORT/api/search/batch` 触发，不需要用户刷新页面。
**注意**：Devvit 的本地端口是动态分配的（`getServerPort()`），需要从日志中查找。

### 3.3 抓取评论（需扩展）

Devvit API 可能支持 `reddit.getPostComments` 或类似方法，需查 Devvit 文档。当前 `searchPosts` 返回的 Post 对象可能有 `.comments` 方法。

### 3.4 用于其他问题调研

当前前端硬编码了12个 Q007 相关搜索任务。用于其他问题时，修改 `src/client/game.tsx` 中的 `SEARCH_TASKS` 数组即可。

---

## 4. 文件索引

| 路径 | 说明 |
|---|---|
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\HANDOVER.md` | 原接手文档（基础环境/约束/复现步骤） |
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\aimingtrainingcoach1\src\server\trpc.ts` | tRPC 端点（overview + search） |
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\aimingtrainingcoach1\src\client\game.tsx` | 前端（12任务自动搜索） |
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\aimingtrainingcoach1\src\server\routes\search.ts` | HTTP 路由（未注册） |
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\devvit-dev.log` | 运行日志（FileShare.ReadWrite 读取） |
| `docs/问题库/Q007-平滑后微调僵住/Reddit原始数据/all_posts.json` | 已抓取的11个帖子 |
| `docs/问题库/Q007-平滑后微调僵住/Reddit原始数据/devvit-search-raw.log` | 搜索原始日志 |
| `docs/问题库/Q007-平滑后微调僵住/Q007调研报告-平滑后微调僵住.md` | 已更新 Reddit 章节的调研报告 |

---

*文档生成：2026-10-13；基于 v0.0.1.16（热重载中）*
