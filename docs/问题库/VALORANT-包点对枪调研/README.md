# VALORANT 包点对枪调研 — Reddit 数据抓取记录

> 调研主题：**在包点门口和包点里面进行远程对枪，总是对不过怎么办**
> 抓取日期：2026-10-13
> 数据通道：aimingtrainingcoach1 Devvit playtest（菜单触发）

---

## 1. 任务目标

用 Reddit 调研 VALORANT 中「包点门口 / 包点内远程对枪打不过」的解决思路，全自动抓取帖子+评论并持久化归档，沉淀给后续对话交接。

## 2. 执行过程

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 主题拆解 → 英文关键词设计（12 个） | 覆盖 3 个子版块：r/VALORANT ×8、r/VALORANTCompetitive ×2、r/AgentAcademy ×2 |
| 2 | 改 `menu.ts`：`Q007_TASKS` → `RESEARCH_TASKS`（新关键词），日志标记 `[MENU-Q007]` → `[MENU-RESEARCH]` | 类型检查通过 |
| 3 | 改 `devvit.json`：菜单 label → 「🔍 批量抓取 VALORANT 对枪调研」 | 配置变更 |
| 4 | 热更新部署 → **v0.0.1.53** | 成功（含一次版本冲突自动重试） |
| 5 | 用户点击菜单触发 | `[MENU-RESEARCH]` 标记出现，12 任务全部完成 |
| 6 | 日志提取 → 归档新问题独立目录 | **198 帖 + 963 评论** |

## 3. 关键词设计（12 任务）

| # | subreddit | query |
|---|---|---|
| 1 | VALORANT | losing long range fights |
| 2 | VALORANT | site entry win duels |
| 3 | VALORANT | peeking into site dying |
| 4 | VALORANT | dry peek losing duels |
| 5 | VALORANT | wide swing vs jiggle peek |
| 6 | VALORANT | holding angles site |
| 7 | VALORANT | crosshair placement entry |
| 8 | VALORANT | retake site |
| 9 | VALORANTCompetitive | losing aim duels site |
| 10 | VALORANTCompetitive | angle advantage long range |
| 11 | AgentAcademy | improve long range duels |
| 12 | AgentAcademy | site defense aim tips |

## 4. 遇到的问题与解决方案（重要记录）

| # | 问题 | 原因 | 解决方案 | 状态 |
|---|---|---|---|---|
| 1 | **菜单点击「没反应」** | devvit playtest 进程已死亡（vite watch 崩溃，stderr `scripts.dev exited with 19960116`），server 不在监听，请求全部落空 | 重启 playtest + **存活监控**（`Get-CimInstance Win32_Process | Where CommandLine -match devvit`）；重启后确认进程存活再触发 | ✅ 已解决 |
| 2 | **curl 触发不可行** | playtest 的 `createServer` 只放行 WebSocket 升级通道，普通 HTTP（含 /api/trpc、/api/search）一律返回 426 Upgrade Required | 放弃 curl，改用 **Devvit 原生菜单动作**（devvit.json 菜单 + /internal/menu handler），经平台隧道可靠触发 | ✅ 已解决 |
| 3 | **前端刷新不触发搜索** | WebView 通道在热更新后不稳定（v0.0.1.30 后多次刷新无输出；需点 "Tap to Start" 进 game 视图才挂载触发） | 绕开 WebView，全部走菜单触发 | ✅ 已解决 |
| 4 | **"This AppVersion already exists"** | 热更新上传版本号冲突（前序构建残留） | devvit 自动重试，后续版本正常部署（v0.0.1.53） | ✅ 已解决（无需干预） |
| 5 | **菜单 label 热更新不生效** | devvit.json 菜单配置（label）是应用 manifest，热更新不重新加载，需重启 | **不影响功能**：endpoint 未变（/internal/menu/q007-fetch），点击执行的是最新代码（任务数组在 menu.ts） | ✅ 可接受 |
| 6 | **重复数据** | 菜单 handler 被触发多次（或 Devvit 重试），日志含重复 SEARCH-POST/COMMENT-POST | 提取脚本按 post id / comment id **去重** | ✅ 已解决 |
| 7 | **评论抓取挂起卡死** | 个别帖子的 getComments 请求挂起不返回，曾导致整个搜索流程卡死（SEARCH-START 都不打） | `withTimeout` 8 秒超时保护，挂起帖跳过；前端另加 45s 搜索超时兜底 | ✅ 已解决（前序 Q007 阶段） |

## 5. 结果数据

| 指标 | 数值 |
|---|---|
| 去重帖子数 | **198** |
| 评论总数 | **963** |
| 带评论帖子数 | 198（100%） |
| 每帖平均评论 | 4.86 |
| 高相关帖子（标题命中 site/peek/duel/entry/swing/angle/retake） | 33 |
| 最高分相关帖示例 | "Back With More Shock Dart Tech"（7438）、"New Split B Site Sage Off-Angle"（6947）、"Map pinging... OPer holding"（6362） |

## 6. 归档文件

| 文件 | 说明 |
|---|---|
| `posts_with_comments_valorant_site_20261013.json` | **198 帖 + 963 评论** 全量数据（帖子 body 2500 字截断、评论 300 字预览；meta 含关键词与统计） |
| `fetch_stats_v3_valorant.txt` | 提取统计 |

提取脚本：`C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\extract-valorant-site.py`（按 `[MENU-RESEARCH]` 起点截取，可复用）

## 7. 已知限制与后续建议

- **评论仅 top5（300 字预览）**：需要深抓（100 条/帖）时，改 `menu.ts` 的 `q007-fetch` handler 的 `limit`（当前 5 → 100）再触发一次
- **无分页**：每任务仅 top25；需要更多历史帖时，后续实现 after 游标
- **排序固定 top/all**：接口支持 sort/timeframe 参数，可按需调整（如换成 relevance 找新帖）
- **关键词硬编码**：换主题改 `menu.ts` 的 `RESEARCH_TASKS` 数组即可（本次即由 Q007 主题替换而来）
- **数据中部分高分帖是攻略/教程类**（如 Sova 箭、Sage one-way）而非对枪问题讨论，引用时注意甄别

## 8. 交接要点（给下一对话）

1. playtest 触发方式：子版块菜单点击（label 可能显示旧名，功能已是新的）
2. 提取方法：`extract-valorant-site.py`（起点 = 日志中 `[MENU-RESEARCH] ... 开始` 行）
3. 若进程死亡：按第 4 节问题 1 重启（代理 + DEVVIT_DISABLE_METRICS + --use-env-proxy），重启后确认存活再触发
4. 数据已在 Q007 之外的**独立问题目录**：`问题库/VALORANT-包点对枪调研/Reddit原始数据/`
