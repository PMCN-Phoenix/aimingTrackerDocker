# Discord 获取清单：18-拉出去打不到人（swing out and can't hit）

> 用途：用户去 Discord 各频道复制粘贴搜索，把结果贴回给我整理
> 创建时间：2026-10-14
> 参照格式：`../Discord可获取资源索引.md`
> 本主题候选关键词：swing and miss / crosshair placement / peek timing / wide swing / counter strafe / over flick / shooting while moving

---

## 一、Woohoojin Discord（discord.gg/woohoojin）——主阵地

> 已有存量：#vod-review 的 clutch+1v1 原始数据（1579 条）已挖过，本清单是**增量补充搜索**，针对"拉出去打不到"这个具体症状。
> 排序规则：按"命中'peek 后瞄准落空'概率"从高到低。

| 优先级 | 频道 | 搜索关键词 | 预期价值 |
|---|---|---|---|
| 🔴 P0 | #vod-review | `swing and miss` / `swung and missed` / `whiffed the swing` | 直接命中"拉出去打空"的复盘案例，看复盘者归因（预瞄？急停？flick overshoot？） |
| 🔴 P0 | #vod-review | `crosshair placement` | 预瞄高度/贴墙距离/头线，#vod-review 高频话题，存量数据里已有大量（见 Q006 摘要 C10/C11、主题3），增量看新案例 |
| 🔴 P0 | #vod-review | `counter strafe` / `counter-strafing` / `not stopping` / `shooting while moving` | 急停时机、移动中开枪散弹问题；存量已有"80ms 减速窗"（Dannew），增量找"急停了还是打不到"的差异案例 |
| 🔴 P1 | #vod-review | `wide swing` / `jiggle peek` / `jiggle into wide` | 大拉被秒/小身位骗枪后大拉的时机；存量已有"jiggle tight→退回→wide swing"套路（frenzy），增量看具体执行 |
| 🟠 P1 | #vod-review | `flick` + `overshoot` / `overflick` / `flicked past` / `flicked over` | 拉枪过头、准星飞过目标的纠错；存量 Q007 已挖过 flick→micro-adjust 时序（Dannew 帧级），增量找"overshoot 本身"的训练法 |
| 🟠 P1 | #vod-review | `peek timing` / `when to shoot` / `target confirmation` / `shoot before ready` | 拉出后多久开枪、target confirmation 纪律；存量已有 Holmster"shoot well before you are ready"，增量找更多"抢开枪"案例 |
| 🟡 P2 | #advice | `how to peek` / `better at peeking` / `missing when i swing` | 新手自曝"拉出去打不到"的求助帖，看高赞教练回复（带 coach/radiant 标签优先） |
| 🟡 P2 | #guides | `peeking guide` / `crosshair placement guide` | 频道 pinned/精华指南贴，直接收藏 |
| 🟡 P2 | #vod-review | `holding angle` / `pre-aim` / `off angle` | 架枪侧视角：敌人拉出来我为什么先开枪却打不死（与"我拉出去打不到"互为镜像） |

### 优先看的高价值用户（参照索引文件已验证名单）
- **Dannew** —— 热图/帧级分析，本主题最对口（80ms 减速窗、flick 是为了给微调争取时间）
- **Holmster [AIM]** —— "shoot before ready"首发失准诊断
- **Zabil [GUP]** —— "准星随墙角走 track the wall"
- **frenzy** —— pre-aim vs tracking 的角度框架
- **stratosphere** —— 简洁直接点核心错误

---

## 二、Voltaic Discord（discord.gg/voltaic）——瞄准训练侧补充

| 优先级 | 频道 | 搜索关键词 | 预期价值 |
|---|---|---|---|
| 🟠 P1 | #general | `overshoot` / `flick overshoot` / `first shot flick` | 纯瞄准训练语境下，flick 过头的训练法（scenario 名、routine）；与游戏侧"peek 打不到"互补 |
| 🟡 P2 | #vod-review | `crosshair placement valorant` / `peeking aim` | Voltaic 用户做的 valorant 瞄准迁移讨论 |
| 🟢 P3 | #resources | （看 pinned）`smoothness` / `reactivity` routine | 已知曲目：VT x WHJ Smooth Strafe Sphere Easy（Q006 存量推荐过），确认 2026 最新版本 |

---

## 三、r/VALORANT 官方 Discord（discord.gg/valorant）——社区经验侧

| 优先级 | 频道 | 搜索关键词 | 预期价值 |
|---|---|---|---|
| 🟡 P2 | #gameplay-discussion | `why do i miss when i peek` / `swinging out missing` | 普通玩家踩坑讨论，可能有与教练视角不同的归因（网络、灵敏度、分辨率） |
| 🟢 P3 | #guides | `peek guide` / `counter strafe guide` | 社区攻略长贴 |
| 🟢 P3 | #clips | `whiffed swing`（看评论区分析） | 实战翻车片段 + 评论区复盘 |

---

## 四、获取执行提示（沿用索引文件规则）

1. 每个频道搜索后**按"热门"排序**，只看高赞回复。
2. 优先点带 `coach` / `radiant` / `immortal` 标签的用户回复。
3. VOD review 评论很长，只提取"具体操作建议 + 原文"，跳过"打得不错"类废话。
4. 拿到内容贴回后，我会归档到本目录，并与 Q006（移动中瞄准）、Q007（平滑后微调僵住）的已有结论做交叉去重。

---

## 五、与已有存量的关系（避免重复获取）

以下结论**已经在存量数据里**，本次 Discord 增量不需要再找：
- 急停 80ms 减速窗、边减速边瞄准（Dannew，Q006 摘要 C1）
- "flick → micro-adjust → 确认 → fire"时序（Dannew 帧级，Q007 主题 A）
- 准星贴墙随墙角走（Zabil，Q006 C10）
- pre-aim vs tracking 的角度优劣框架（frenzy，Q006 C11）
- "shoot before ready"首发失准（Holmster，Q006 C7）
- jiggle tight → 退回 → wide swing 套路（frenzy，Q006 主题3）

**本次增量真正缺的**：
1. 大量"swing and miss"真实复盘案例里，归因到底是预瞄还是急停还是 flick overshoot（占比分布）；
2. overshoot 的专门训练法（Voltaic 侧）；
3. 教练对"拉出去后 freeze/僵住"的直接建议。
