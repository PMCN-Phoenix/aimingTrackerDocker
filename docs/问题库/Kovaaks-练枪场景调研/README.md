# Kovaaks 练枪场景调研 — Reddit 数据抓取记录

> 调研主题：Kovaaks 5 个练枪场景问题（XY Tracking Dodge / Pasu Track Dodge / PSGS 急停 / 移动定位 / Mirror-AntiMirror）
> 抓取日期：2026-10-14（两轮合并）
> 数据通道：aimingtrainingcoach1 Devvit playtest（菜单触发）

---

## 1. 调研问题（用户提供）

| # | 问题 | 关键词 |
|---|---|---|
| 1 | XY Tracking Dodge | "XY Tracking Dodge" kovaaks / "XY Tracking" strafe aiming / movement tracking scenario |
| 2 | Pasu Track Dodge / Pasu Dodge | "Pasu Track Dodge" kovaaks / "Pasu Dodge" training / anti-mirroring pasu |
| 3 | PSGS 1 Shot No Mag / 移动中急停开枪 | "PSGS 1 Shot No Mag" / counter strafe shooting timing / "movement aiming" click timing |
| 4 | 移动中定位 vs 静止打移动靶 | "movement aiming" vs stationary / strafe aiming fundamentals / aim trainer doesn't translate |
| 5 | Mirror / Anti-Mirror 转换时机 | mirroring anti-mirroring strafe aiming / patstrafe mirror anti-mirror ratio |

推荐 Subreddit：r/FPSAimTrainer、r/KovaaKs、r/Voltaic、r/aimlab、r/VALORANT、r/GlobalOffensive

## 2. 执行过程

| 步骤 | 操作 | 结果 |
|---|---|---|
| 1 | 用户关键词整理成 12 任务（覆盖 FPSAimTrainer/KovaaKs/Voltaic/VALORANT） | 写入 menu.ts RESEARCH_TASKS |
| 2 | 菜单 label 改通用「🔍 批量抓取当前调研」（devvit.json） | 重启 v0.0.1.65 生效 |
| 3 | **第一轮触发（带引号关键词）** | 12 任务完成：107 帖 + 480 评论；**5 个带引号任务全部 0 结果** |
| 4 | 诊断：引号问题 → 去引号改任务数组 | v0.0.1.67 部署 |
| 5 | **第二轮触发（去引号补抓）** | 12 任务完成：补上 XY/Pasu/PSGS 等主题 |
| 6 | 两轮合并提取归档 | **187 帖 + 855 评论** |

## 3. 遇到的问题与解决方案（重要记录）

| # | 问题 | 原因 | 解决 | 状态 |
|---|---|---|---|---|
| 1 | **带引号关键词 0 结果** | Devvit `searchPosts` 对含引号的精确短语查询返回空（`"Pasu Track Dodge" kovaaks` → count:0），Reddit 搜索 API 的引号语义未透传 | **去掉关键词中的引号**（`Pasu Track Dodge kovaaks` → count:25）；去引号后重跑一轮补抓 | ✅ 已解决 |
| 2 | **点击菜单无反应（第 2 次点击）** | v0.0.1.67 刚热更新部署时点击，新版本未完全就绪；页面/隧道瞬断 | 等部署稳定（connected 出现）后再点，第 3 次点击成功触发 | ✅ 已解决 |
| 3 | **其他对话改过任务数组** | 手册交接后被其他对话用于别的主题（Odin 防守），RESEARCH_TASKS 已被覆盖 | 直接再改成本主题关键词即可（每次覆盖前先 Read 确认现状） | ✅ 已解决 |
| 4 | 菜单 label 与任务主题不符 | label 是 manifest 配置，热更新不生效 | 改 label 后需重启（本次重启 v0.0.1.65 生效）；已改通用名避免再改 | ✅ 已解决 |
| 5 | mirroring 关键词在 r/KovaaKs 空结果 | 该子版块此主题帖少 | 不处理（相关讨论主要在 r/FPSAimTrainer） | 可接受 |

## 4. 结果数据

| 指标 | 数值 |
|---|---|
| 去重帖子数 | **187** |
| 评论总数 | **855** |
| 带评论帖子数 | 185（98.9%） |
| 每帖平均评论 | 4.62 |
| 高相关帖子（标题命中核心场景词） | 13 |

高价值帖示例：
- "What is the consensus about Strafe Aim(Movement Aim) in shooters"（30 分）— 问题 4/5
- "Does relying on mirror/strafe aiming have any big downsides I should know"（21 分）— 问题 5
- "Is 'mirror strafing' considered a bad habit?"（16 分）— 问题 5
- "Not sure if im understanding mirroring and anti mirroring"（14 分）— 问题 5
- "Try these playlists out if you are struggling with Preciseorb!"（38 分）— 问题 3/4
- "Voltaic Fundamental Aim Training Routines 2.5 - Strafe Routines"（40 分）— 问题 1/2

## 5. 归档文件（产物位置）

| 文件 | 说明 |
|---|---|
| `D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Kovaaks-练枪场景调研\Reddit原始数据\posts_with_comments_kovaaks_20261014.json` | **187 帖 + 855 评论** 全量数据（帖子 body 2500 字截断、评论 300 字预览；meta 含关键词/两轮说明/统计） |
| `D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Kovaaks-练枪场景调研\Reddit原始数据\fetch_stats_v3_kovaaks.txt` | 提取统计 |
| `C:\Users\Rose\Doubao\chats\2026-10-13\new-chat\extract-kovaaks.py` | 提取脚本（从第一个 [MENU-RESEARCH] 起，可复用） |

## 6. 已知限制与建议

- **评论仅 top5（300 字预览）**：深抓需改 menu.ts 的 limit（5 → 100）
- **引号关键词不可用**（Devvit searchPosts）：以后设计关键词**不要带引号**
- 每任务 top25 无分页；排序固定 top/all
- 部分高分帖是 Routine/工具推荐帖而非问题讨论，引用时按 5 个问题分组甄别
- 若要更聚焦：可针对"strafe aiming fundamentals"、"mirror bad habit"再补一轮 relevance 排序

## 7. 产物索引

| 文件 | 说明 |
|---|---|
| `README.md` | 本文件（抓取过程记录） |
| `Reddit数据补充报告.md` | ★ 2026-10-14 数据分析报告（187帖+855评论按5问题分组、交叉验证、额外发现、直接建议） |
| `分类结果.json` | 按5问题分组的帖子+评论结构化数据 |
| `Reddit原始数据/posts_with_comments_kovaaks_20261014.json` | 全量原始数据（590KB） |
| `Reddit原始数据/fetch_stats_v3_kovaaks.txt` | 抓取统计 |

**关键结论速览**：
- Mirror 决策加 TTK 条件（只在 TTK 优势时 mirror）
- TacFPS 补充场景：anima micro v2 + hand independence playlist（cycle strafes）
- 移动定位底层 = smoothness 提升感知能力
- 练枪圈存在"过度思考 strafe aiming"反面派（狂打 DM + crosshair placement）
