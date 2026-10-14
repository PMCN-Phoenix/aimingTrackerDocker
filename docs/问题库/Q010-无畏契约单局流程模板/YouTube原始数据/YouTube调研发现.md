# YouTube 调研发现：VALORANT 单局/单回合内的非枪法流程模板

> 调研日期：2026-10-14
> 范围：VALORANT 单局/单回合内流程（决策→信息→身位→道具→沟通→残局），不含每日练枪、不含长期段位路径
> 方法：yt-dlp 站内搜索 70+ 视频 → 精选 10 个 → 直接字幕被 bot 墙拦截 → 改用二手权威汇编（Google Doc「Valorant Concepts」逐 clip 标注 Woohoojin 出处；Dignitas 官方博客；BoostRoom 教练博客；VLR 社区）

---

## 一、核心发现（按权威性排序）

### 发现 1：Woohoojin「三支柱 + 死后复盘循环」是最接近"单回合 checklist"的现成框架
- **权威性**：职业教练 / Radiant 选手（Woohoojin = 前 Radiant，现 Thinking Man's Valorant 主理人）
- **来源**：Google Doc「Valorant Concepts」逐 clip 汇编（https://docs.google.com/document/d/1h6cl_3LRNmvmadWY6U3VlyL-X_BY9VZ_TbCEun86YnA/mobilebasic ）
- **框架原文**：
  > "All decisions and plays boil down to three things: **Awareness, Positioning, and Timing**."
- **配套死后复盘循环**：
  > "If a teammate dies and you were not there to trade them out (or better yet, whenever a teammate takes an engagement, regardless if they died or not), **rewind 5-10 seconds** and check if there were any mistakes in your Awareness, Positioning, or Timing. Check for any clues (minimap, body language, etc.) that could have alerted you to this engagement... ask yourself what you could have done to help."
- **可量化部分**：死后复盘 = 固定回看 5-10 秒；三个检查项固定
- **对应视频**：Woohoojin 多条 Radiant Coaching 合集（TwVJ5TEGfd0「How to Make Plans Like a Radiant」、Cd_RRi6iQEQ「This is why your defensive plans suck」）

### 发现 2：回合时钟蓝图（Round-Clock Blueprint）—— 时间分段决策
- **权威性**：职业教练博客（BoostRoom，VCT 教练团队运营）
- **来源**：https://boostroom.com/blog/attack-side-guide-building-a-default-that-creates-free-picks
- **结构**（与 Q005 场景09 已验证的蓝图交叉一致）：
  | 时间段 | 动作 |
  |--------|------|
  | 0:00–0:20 | Anti-push + 早期信息（hold for aggression，不 sprint 进未知） |
  | 0:20–0:45 | 抢占第一层空间（safe first layer，可 trade、可重复） |
  | 0:45–1:05 | 试探反应 + 拉道具（recon/smoke/flash 试探防守方怎么应对） |
  | 1:05–1:25 | **决策窗口**：hit / split / fake / pivot |
  | 最后 ~25 秒 | 结构化 commit（打则 execute，不打则 save/regroup） |
- **关键提醒**：
  > "If you wait until the last 20 seconds to decide, you're begging to lose."
  > "Even a wrong decision is better than a last-second panic rush, because you learn faster."
- **可量化部分**：5 个时间段精确到秒；决策窗口固定在 1:05-1:25

### 发现 3：Default 三种阵型模板（进攻方中段默认结构）
- **权威性**：BoostRoom 教练博客 + Dignitas 官方战术博客（https://dignitas.gg/articles/the-art-of-defaulting-in-valorant ）
- **三种模板**：
  - **2-1-2**（最适合排位）：两路各 2 人施压，1 人带 Spike 居中浮动。优点：自然形成 trade、Spike 安全、pivot 灵活。
  - **1-3-1**（中路控制型）：两侧各 1 人，3 人控中。中路成为 pivot 高速。
  - **1-1-3**（快速接触型）：A、B 各 1 个 lurker，3 人组"决策组"按信息打。
- **Default 的 4 个目标**（每回合自问）：
  1. 不孤立决斗（contest multiple lanes safely）
  2. 拿"能守住的"地图控制（owned space，不是 borrowed space）
  3. 拉防守方道具 + 摸清站位（pull utility, learn setup）
  4. 形成 pivot 打最弱的点（hit weakest site）
- **空间三分类**：Borrowed space（踩了但守不住）/ Owned space（有 crossfire+道具+退路）/ Converted space（用 owned 换到 pick/rotation/entry）
- **对应视频**：Sero「In-Depth Guide to Defaulting」vcnZdu2lDDQ

### 发现 4：优势/劣势回合的二元规则（Numbers Advantage / Disadvantage Playbook）
- **权威性**：Woohoojin coaching clips 汇编
- **优势方规则**（人数/枪械/位置占优时）：
  > "Don't take risks. Don't give up guns. Buddy system. Prevent 1v1s from happening. Box the enemy in, cutting off rotations."
  > 对敌方 eco 回合："think twice about lurking. The risk of a lurk goes up significantly as a failed lurk gives a valuable gun to the enemy."
- **劣势方规则**（eco 或 1v2/1v3 时）：
  > "Quickly take risks to equalize. On eco rounds, don't try to play normal angles and hope to win. Instead take risks by pushing sites, stacking sites, or playing positions where you can hopefully steal a gun."
  > 1vX："Don't camp in a corner waiting for something to happen. Good teams will setup and then double/triple peek you and guarantee the win. Instead, look to play fast and actively search for isolated 1v1s that you can take, before the enemy groups up."
- **可量化部分**：明确"优势方保守 / 劣势方激进"的切换触发器

### 发现 5：防守方道具 = Stalling vs Separating 二选一
- **权威性**：Woohoojin VOD 复盘汇编（标注具体 VOD："This angle doesn't get cleared"）
- **框架**：
  > "There are two ways to use utility on defense: **for stalling, and for separating**. Stalling is less effective, and is to simply buy time for your team to rotate... In most cases, you cannot stall an enemy team for an entire round. You have to choose when and where to fight."
  > "Utility for separating is far more effective because it usually results in kills. Once the enemy team commits to hitting a site, use utility to keep the rest of the enemy team stuck while you kill the lone entry fragger."
- **配套"ebb and flow"资源兑换思维**：
  > "If attackers spend a lot of resources to take space (dog + flashes + Phoenix ult + Raze ult + smokes), defenders either match with resources or give up space and play retake. If the enemy barely spends resources but your team burns a bunch of smokes/mollies/rotations, your team is susceptible to fakes."

### 发现 6：Lurk = 红灯/绿灯小游戏 + Tempo 匹配
- **权威性**：Woohoojin clip + The Unsuspicious（社区高赞）
- **Lurk 节奏规则**：
  > "When the round is progressing slowly, no action around the map = **red light**: lurk slowly, clear all angles, keep gun out. When the round is progressing quickly, enemy executing, lots of gunfights = **green light**: lurk quickly, possibly knife out."
- **Tempo 原则**：
  > "If the round's tempo is high, you need to play high tempo too. If low, play slow."
- **Lurk 失效触发器**：
  > "If you hear 'LAST PLAYER STANDING' and you couldn't possibly speed up your lurk any faster, lurking is no good. Instead play fast rotate to ensure you are part of those gunfights."

### 发现 7：残局（Clutch）反"分析瘫痪"规则
- **权威性**：Woohoojin coaching 汇编
- **原文**：
  > "The most common mistake when clutching in low elo is **'analysis paralysis'**. When suddenly thrown into a 1v2 or higher, the clutcher fails not because they are incapable, but because they suddenly freeze up and fall back to instincts of doing nothing while they think about options. Meanwhile the timer ticks down and soon there are no more good options.
  > **Simple fix: just pick an option, any option, and commit to it.** After the play/round is over, reflect whether it was best. Next time reiterate."
- **这同时是本调研的"反面意见"**（见第四节）

### 发现 8：下包后防守方（Post-Plant Defense）两个硬规则
- **权威性**：Woohoojin VOD 复盘汇编
- **炸弹 tap 规则**：
  > "On defense when the bomb is planted, besides clearing site, **99% of the time your primary goal is to go for a bomb tap as soon as possible**. Tapping the bomb plays the full defuse sound, pressures attackers to peek the bomb or send molly/ult lineups. The sooner you bait this utility out, the more time you'll have to defuse or make a play after they've wasted utility."
- **回防 smoke 规则**：
  > "In post-plant retake situations, **always use smokes on the bomb**. Smoking anywhere else could accidentally give cover to the enemy to safely spam the defuser. You want the enemy to take risks and peek angles."
- **下包位置规则**：
  > "When planting, tuck the bomb into a wall or corner. This reduces the area where defenders can stand while defusing (cuts the circle in half/quarter), making it easier to spray through smoke or cover with molly."

### 发现 9：沟通（Comms）三规则
- **权威性**：W0rthyTV + Woohoojin VOD 汇编
- **信任规则**：
  > "When receiving a comm, **trust it 100% with conviction**. It's more efficient to blindly trust the callout and immediately adapt, rather than spending time validating. If the comm is bad, criticize after the round or during VOD review."
- **报点公式**：
  > "Every time you see an enemy, hold PTT and say **location, agent name, any damage** — e.g. 'Hut, Sage, hit 88' or '1 mid boiler, dead'."
- **Off-angle vs On-angle 行为差异**（W0rthyTV「3 Types of Comms」）：
  > "When holding an off angle, play to hold, do NOT jiggle. When holding an on angle, you can play to jiggle. Jiggle's purpose = gather info / catch off guard / harder to hit — none of that applies when you're already in an off angle."

### 发现 10：Mid-round 是 IGL 70% 的工作，FNS 是史上最佳 midrounder
- **权威性**：VLR.gg 职业社区共识（高赞讨论）
- **原文**：
  > "Pre rounding is like 70% of being an IGL. You need to understand how to call around your strengths and around your opponents' weaknesses while also trying to keep your team from getting tilted."
  > "FNS is undoubtedly the greatest midrounder in valorant history. His mechanical abilities are not top tier, but his calling ability easily makes up for that."
- **含义**：职业圈把"回合中临场改决策"视为独立技能，不是开局 strat 的附属。
- **对应视频**：Vapen「Mid Rounding Guide」zpveYa0L9Ws

---

## 二、现成模板清单（综合多个来源拼装的最完整版本）

> **结论：YouTube 上没有一个"官方/职业教练发布的、从买装备到残局的完整 10 步单回合 checklist"。** 最接近的是把上述发现按时间轴拼起来的版本。下面这个综合模板是把 BoostRoom 时间轴 + Woohoojin 三支柱 + Dignitas default 阵型 + 残局规则串成的"最佳拼装"，**不是任何单一创作者的原文**。

### 综合模板：VALORANT 单回合决策流程（拼装版）

**阶段 0：买完装备后 → 回合开始前（pre-round）**
1. 看 tab：己方经济 / 对方经济 / 己方道具冷却 / 对方关键大招（下包后谁有 molly/ult）
2. 定本局阵型：2-1-2 / 1-3-1 / 1-1-3？谁带 Spike？谁 lurk？谁 entry？谁 trade？
3. 一句 comm："Let's default 2-1-2. Hold for pushes first." / "Spike stays mid with me."

**阶段 1：0:00-0:20 Anti-push 期**
4. 不 sprint 进未知；站在可 trade 的位置；用 jiggle/shoulder jump peek 拿信息，不打 commit fight
5. 第一波信息工具每路最多 1 个（recon/drone），不清空道具预算

**阶段 2：0:20-0:45 抢第一层空间**
6. 拿 owned space（有 cover + 有 trade + 有退路），不拿 borrowed space
7. Spike 居中，不当 first contact；想深推就先 drop Spike

**阶段 3：0:45-1:05 试探期**
8. 用 1 个压力道具（smoke/flash threat）逼防守方反应，观察他们怎么 stop 你
9. 拉防守方道具出来 = late execute 更干净
10. 每路留 1 个关键道具给决策窗口（"go utility"）

**阶段 4：1:05-1:25 决策窗口**
11. 决策三选一：**Hit / Split / Fake-pivot**
12. 拿到 pick 后：① 不再打孤立 duel ② Spike 立刻向新 win condition 移动 ③ 5 秒内定 hit/hold/pivot ④ 防 trade-back（守方会 push 补枪）
13. 没拿到 pick：执行 saved "go" utility / fake 一侧打另一侧 / 等防守方道具 fade

**阶段 5：最后 25 秒 Commit**
14. execute 则结构化进点（contact explode）；不 execute 则 save/regroup
15. 下包时 tucked into corner（cut defuse circle in half）

**阶段 6：Post-Plant（攻方守包 / 守方回防）**
16. 攻方：slow defenders, play non-committed, prolong engagements, bait attention
17. 守方：① 先 bomb tap 逼道具 ② smoke 包上不是包外 ③ 清 site 不必 100% 清完

**阶段 7：残局 1vX**
18. **不要 freeze**。立刻 pick 一个方向，commit；回合后复盘
19. 主动找孤立 1v1，不等对方组 multi-peek

**阶段 8：死后（每回合固定复盘）**
20. rewind 5-10 秒，问自己：Awareness（小地图/声音/身体语言漏了什么？）/ Positioning（有没有 cover、trade、escape？）/ Timing（join fight 太早/太晚？）

---

## 三、引用表（发现 → 来源）

| # | 发现 | 来源 URL | 权威性 |
|---|------|----------|--------|
| 1 | 三支柱 Awareness/Positioning/Timing + 死后 5-10s 复盘 | https://docs.google.com/document/d/1h6cl_3LRNmvmadWY6U3VlyL-X_BY9VZ_TbCEun86YnA/mobilebasic （汇编 Woohoojin clips） | 职业教练（Woohoojin） |
| 2 | 回合时钟蓝图 0:00-0:20-0:45-1:05-1:25-末25s | https://boostroom.com/blog/attack-side-guide-building-a-default-that-creates-free-picks | 职业教练博客（BoostRoom） |
| 3 | Default 2-1-2 / 1-3-1 / 1-1-3 模板 + 空间三分类 | 同上 + https://dignitas.gg/articles/the-art-of-defaulting-in-valorant | 职业教练博客 + 俱乐部官方 |
| 4 | 优势方保守 / 劣势方激进二元规则 | Google Doc 同上（Woohoojin「You Suck at Eco Rounds」clip） | 职业教练 |
| 5 | 防守道具 Stalling vs Separating + ebb and flow | Google Doc 同上（Woohoojin VOD "This angle doesn't get cleared"） | 职业教练 |
| 6 | Lurk 红灯/绿灯 + Tempo 匹配 | Google Doc 同上（credit The Unsuspicious） | 社区高赞 + 教练 |
| 7 | 残局反分析瘫痪"pick any option and commit" | Google Doc 同上（Random Advice 段） | 职业教练 |
| 8 | Post-plant bomb tap / smoke on bomb / tucked plant | Google Doc 同上（Woohoojin VOD "THEY WERE READING DMS MIDROUND"） | 职业教练 |
| 9 | 沟通三规则（trust 100% / 报点公式 / off-angle 不 jiggle） | Google Doc 同上 + W0rthyTV「3 Types of Comms」 | 教练 + 内容创作者 |
| 10 | Mid-round = IGL 70%；FNS 史上最佳 | https://www.vlr.gg/173721/best-igl ; https://www.vlr.gg/725159/vlr-referees | 职业社区共识 |

---

## 四、反面意见（至少 1 条）

### 反面意见 1：过度结构化 = 分析瘫痪，残局反而要"别想太多"
- **来源**：Woohoojin coaching（Google Doc「Valorant Concepts」Random Advice 段）
- **原文**：
  > "The most common mistake when clutching in low elo is **'analysis paralysis'**... they suddenly freeze up and fall back to instincts of doing nothing while they think about options. Meanwhile the timer ticks down and soon there are no more good options. **Simple fix: just pick an option, any option, and commit to it.**"
- **含义**：把"每回合 20 步 checklist"当真、在残局里逐条对照，恰恰是低段位输残局的原因。checklist 是**练阶段/复盘阶段**用的，实战里必须内化成直觉。

### 反面意见 2：决策树/默认阵型不能教条化——"你不是 DRX"
- **来源**：VLR.gg Premier 讨论（https://www.vlr.gg/389908/premier ）
- **原文**：
  > "#4. **You aren't DRX.** If you're going to [run strats], keep them simple with as little [complexity] as possible."
- **含义**：职业级 default 阵型 / mid-round 体系是基于职业队磨合度的，排位单排生搬硬套反而崩溃。

### 反面意见 3：Lineups 不能每回合固定用
- **来源**：Woohoojin clip「Lineups are Situational, Stop Using them Every Round \| Diamond Sova Icebox Coaching」（Google Doc 引用）
- **含义**：把道具 lineup 当"每回合必做"的 checklist 项，是低段位坏习惯——道具必须按回合信息决定。

---

## 五、与已知锚点的交叉验证

| 已知锚点（Q005） | 本次发现 | 一致性 |
|------------------|----------|--------|
| BoostRoom round-clock 0:00-0:20-0:45-1:05-1:25-末25s | 发现 2 完全一致，且补充了每个时间段的具体动作 | ✅ 交叉验证通过 |
| 5 步回防 Regroup→Information→Isolation→Entry→Defuse | 发现 8 的 bomb tap / smoke on bomb 是回防子步骤 | ✅ 互补 |
| Trade spacing 1-2 秒原则 | 发现 3 的 "two-man rule: any contested angle watched by two players who can trade" | ✅ 一致 |

---

## 六、局限性与未完成项（诚实声明）

1. **直接字幕未抓到**：本 Clash 代理 IP 被 YouTube bot 墙标记，yt-dlp 所有 client 变体均失败；Cookie 导出因 Chrome v127+ app-bound 加密需 admin 无法完成；browser-use 服务未启动。所有"原文引用"来自二手汇编（Google Doc 逐 clip 标注 Woohoojin 出处），**不是从 YouTube 字幕直接提取**，因此时间戳精度有限。
2. **Vapen / ProGuides / Sero / Konpeki / LemurrUK 五个视频的具体内容未直接提取**，仅从标题和二手引用推断其主题。建议下次代理节点切换或拿到 cookies 后补抓。
3. **没有发现"官方 Riot 发布的单回合 checklist"**。Riot 官方新手站（val.qq.com）只有术语表，没有流程模板。
