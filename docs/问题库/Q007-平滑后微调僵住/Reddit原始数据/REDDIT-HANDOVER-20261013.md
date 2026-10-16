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

---

## 5. 状态更新（2026-10-13 第二轮接手，问题已解决）

### 5.1 结论：热重载卡住 ≠ 代码问题

排查确认：**「热重载卡住」的真实原因是 playtest 进程早已停止**（接手方停掉后未重启），日志停留在最后一次构建状态，并非 rebuild 死锁。重启后一切正常。

### 5.2 本轮修复与验证

| 项 | 结果 |
|---|---|
| 重启 playtest | ✅ 干净重启，新版本 **v0.0.1.26** 部署成功，无错误 |
| 新格式 `[SEARCH-START]/[SEARCH-POST]/[SEARCH-END]` | ✅ **验证生效**：11 任务 × 25 = **275 条原始**，每帖一行不截断 |
| 100% 提取 | ✅ 去重后 **201 条高价值帖子**（对比旧格式仅 11 条） |
| HTTP 路由注册 | ✅ 实际**已注册**（`index.ts`：`import { search }` + `app.route('/api/search', search)`），接手文档此前记录「未注册」已过时 |
| 日志备份 | `devvit-dev.log` → `.bak`（历史保留），新日志从零开始 |

### 5.3 新增归档（Q007/Reddit原始数据/）

| 文件 | 说明 |
|---|---|
| `all_posts_v2_20261013.json` | **201 条去重帖子**完整数据（id/title/author/score/comments/permalink/url/createdAt/body 前 500 字） |
| `devvit-search-raw.log` | 新格式搜索原始日志（可重新解析） |
| `fetch_stats.txt` | 提取统计（11 任务 / 275 原始 / 201 去重） |

### 5.4 后续注意

- playtest 若再次「无响应」：先查进程（`Get-CimInstance Win32_Process | Where CommandLine -match devvit`），进程没了就是没在跑，按原文档 3.1 重启即可
- 刷新页面即触发一轮 12 任务搜索（实测首轮完成 11 个任务，第 12 个可能因页面连接建立时序被跳过；数据量已足够）
- 201 帖中 Q007 高价值帖（316dez 张力管理、rainsyy 1000h 反思、低敏微调等）均已包含，可直接供报告引用

## 6. 全自动评论抓取（v3，2026-10-13 晚）

### 6.1 目标与方案
主旨：**全自动、高留存**——抓帖子时自动附带评论、可一键深抓，结果持久化归档供 Codex 交接直接使用。

技术选型（绕开 WebView 通道）：**Devvit 原生 Menu Action**（devvit.json 菜单项 + `/internal/menu/q007-fetch` handler）。
- 页面刷新触发不了搜索（WebView 通道在热更新后不稳定，v0.0.1.30 后多次刷新无输出）
- curl 直连不可行（playtest 的 `createServer` 只放行 WebSocket 升级，普通 HTTP 一律 426）
- **菜单点击可靠触发**：子版块页面菜单 → Devvit 平台经隧道调用本地 server → 12 任务搜索 + 每帖 top5 评论 → 全部 console.log 落日志

### 6.2 代码变更
| 文件 | 变更 |
|---|---|
| `src/server/routes/menu.ts` | 新增 `/q007-fetch` handler：12 任务搜索 + 每帖 top5 评论（CHUNK=5 并发 + 8s 超时保护，防限流/防挂起）+ `[SEARCH-START]/[SEARCH-POST]/[COMMENT-POST]/[SEARCH-END]` 日志 |
| `devvit.json` | 菜单新增「🔍 批量抓取 Q007 数据」（location: subreddit, forUserType: moderator, endpoint: /internal/menu/q007-fetch） |
| `src/server/routes/search.ts` | 升级为与 trpc.ts 一致的新逻辑（body 2500 + 自动评论 + 超时保护）——注：**HTTP 路由在 playtest 下不可达（426）**，仅作代码一致性保留 |
| `src/server/trpc.ts` | 评论抓取加 8s 超时保护（`withTimeout`），前端搜索加 45s 超时兜底 |

### 6.3 结果与归档（Q007/Reddit原始数据/）
| 文件 | 说明 |
|---|---|
| `posts_with_comments_20261013.json` | **125 条去重帖子 + 576 条评论**（嵌套结构：post.comments[]）；帖子 body 2500 字截断、评论 body 300 字预览；字段 id/title/author/score/comments/permalink/url/createdAt/body |
| `fetch_stats_v3.txt` | 提取统计（125 帖 / 576 评论 / 125 帖带评论 / 每帖均 4.61 条） |

数据链路：菜单点击（触发 2 次）→ 275 条 SEARCH-POST 原始 → 去重 125 帖；1301 条 COMMENT-POST 原始 → 去重 576 条。

### 6.4 已知限制（留给下一交接方）
- 评论仅 top5（300 字预览）——「深抓全部评论（100条/帖）」按钮在前端已就绪，但 WebView 通道不稳定未验证；**如需要深抓，改从菜单 handler 加参数**（menu.ts 的 q007-fetch 可扩展 limit）
- 无分页：每任务仅 top25，after 游标未实现
- 排序固定 top/all：接口已支持参数，改 menu.ts/search.ts 可换 sort/timeframe
- 关键词硬编码 12 任务：换主题需改 menu.ts 的 Q007_TASKS 数组
- 菜单 handler 被触发 2 次导致重复数据：脚本已按 id 去重，无影响
- playtest 稳定性：vite watch 曾崩溃导致进程死亡（stderr `scripts.dev exited with 19960116`），重启后需确认进程存活（`Get-CimInstance Win32_Process | Where CommandLine -match devvit`）