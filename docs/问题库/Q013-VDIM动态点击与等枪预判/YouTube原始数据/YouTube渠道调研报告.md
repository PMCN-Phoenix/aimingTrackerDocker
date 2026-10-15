# YouTube 渠道调研报告：VDIM 动态点击中的等枪/预判/跟枪技术
## ——含追加主题：小目标+垂直抖动微定位、Floating Heads Timing 400% 训练法

> 调研日期：2026-10-14 ｜ 调研执行：YouTube 站内搜索（yt-dlp ytsearch）+ 英文字幕全文挖掘
> 用户背景：VDIM Novice 6 天计划 / Kovaak's / VALORANT；自述"跟枪会慢"、"现在是匹配目标速度才点击"

---

## 1. 搜索覆盖率

| 项目 | 数量 |
|---|---|
| 关键词组（主问题 10 组 + 追加 8+7 组） | 25 组 |
| 去重后候选视频 | ~130 个 |
| 精选视频 | 24 个（18 新 + 6 复用 Q003/Q007 已有字幕） |
| 本次成功获取字幕（自动英文字幕） | 12 个 |
| 复用已有字幕 | 6 个 |
| 字幕未获取（429 限流/无字幕/区域不可用） | 4 个（已如实标注） |

**字幕获取方式标注规则**：下文引用均可在 `subtitles/` 找到对应 `.vtt/.txt`；标注【429未获取】的视频只引用标题级信息，不编造时间戳内容。

---

## 2. 核心发现

### 2.1 Dynamic Clicking（动态点击）的官方定义

**Voltaic 官方定义**（最权威口径）：
> "Dynamic clicking is a voltaic benchmark subcategory containing any scenario with several moving targets that are eliminated via a set amount of clicks. The word dynamic is a descriptor for the target's movements which will typically have varying levels of predictability."
> —— Voltaic 官方视频 [01:26-01:42](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)

要点：
- "dynamic" 描述的是**目标的运动**（不同可预测度），不是"点击要动态"。
- Floating Heads 类目标 = 运动意图明显（可预测度高）；Angle Shot 类 = 更难读（可预测度低）[01:42-01:51](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。
- RiddBTW 的社区口径一致：动态点击 = "moving dots"类，需要 reading skills、target selection、**LEADING**（提前量）、pattern learning [00:54-01:02](https://www.youtube.com/watch?v=DcNP0F_gpOQ)。

### 2.2 命中移动目标只有两种技术：Hit Confirmation 与 Target Leading

Voltaic 官方把"消灭移动目标"的方法**明确收敛为两种**，可按目标互换使用：

| | Hit Confirmation（命中确认） | Target Leading（提前量/等枪） |
|---|---|---|
| 做法 | 先短暂追踪一个乱跳的目标，肉眼确认能打中了，再点击 | 把准星放到"预判接触点"，flick 到空间中一个固定点，等目标撞上来 |
| 适用 | 大目标 / 小目标但运动可预测 | 有一定预判把握的目标 |
| 阶段定位 | **新手期**：追踪时间会随着进步**不断缩短** | **进阶方向**：flick 到预测点，到达接触点与目标相遇之间的时间越短越好 |
| 引用 | [02:12-02:34](https://www.youtube.com/watch?v=nnDHvHPlQ1Y) | [03:12-03:29](https://www.youtube.com/watch?v=nnDHvHPlQ1Y) |

> "The second approach is Target leading — placing your Crosshair where you anticipated making contact with the target... after you make your educated guess you act on it by executing a flick to a stationary point in space. The less time that elapses between arriving at this point of contact and the target meeting the Crosshair, the better."
> —— [03:12-03:29](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)

**对用户"匹配目标速度才点击"的直接判定**：这正是 Voltaic 说的 Hit Confirmation（新手期技术）。官方明确说："as you become more proficient with hit confirming, the amount of time you'll need to track a target before firing will continually **decrease**" [02:29-02:34](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。即：**"先跟稳再点"不是错误起步，但它是应该随进步被压缩、最终过渡到"flick 到预测点等目标撞上来"的过渡阶段**。

### 2.3 "等枪"的操作细节

RiddBTW 在 Floating Heads Timing 400% 上直接示范了等枪的操作：
> "you are flicking and then micro adjusting just like you would in static, and you're flicking to where the target's going to be when you flick — that's essentially what you want to aim for."
> —— [31:00-31:05](https://www.youtube.com/watch?v=DcNP0F_gpOQ)

Voltaic 的 Popcorn 例子给出了具体提前量位置：
> "positioning our Crosshair beneath it on the y-axis and in front of it on the x-axis... we'll observe the horizontal motion through the x-axis to maintain the initial offset... the target will intercept our Crosshair as it begins descending to the floor."
> —— [04:30-04:50](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)

christmasiscancelled 给出"在最慢最可预测处点击"的原则：
> "in Bounce 180 you want to hit each bot at the apex of the jump. Try to keep your mouse near that height so you only need to move it horizontally."
> —— [01:01-01:08](https://www.youtube.com/watch?v=ZBNEAgaGjdQ)

**等枪的认知-运动链条**（综合 minigodcs）：
1. **Prediction（预测）**：猜目标接下来会到哪，预摆准星位置 [02:33-02:41](https://www.youtube.com/watch?v=DP954gl592E)
2. Prediction 失效时 → **Active reading（主动读靶）**：实时观察目标当下运动，持续微调 [02:43-02:53](https://www.youtube.com/watch?v=DP954gl592E)
3. 两者按目标可预测度**动态切换**，不是二选一。

### 2.4 "跟枪慢"的机制：不是跟枪方法错，是张力（tension）问题

MattyOW《Speed Matching in Precise Tracking》全篇核心：speed matching 的机制是**肌肉张力**：
> "too much tension in the fingers and the wrist will result in jerky skip ahead motions and even over correction... too little tension will result in your motion lagging behind the target"
> —— MattyOW [02:50-03:01](https://www.youtube.com/watch?v=-7n6q33We28)

用户的"跟枪会慢"= **张力不足 → 动作落后于目标**。修复方向不是"更努力地跟"，而是：
- 长距离匀速横移时保持恒定张力 [04:22](https://www.youtube.com/watch?v=-7n6q33We28)
- 变向时才把张力转移到手腕做快速微修正 [04:26-04:30](https://www.youtube.com/watch?v=-7n6q33We28)
- 不要往鼠标垫里压（sticky），用横向压力 [04:46-05:26](https://www.youtube.com/watch?v=-7n6q33We28)
- 起手就要 smooth 地接目标，不要"先急甩再硬跟" [05:38-06:01](https://www.youtube.com/watch?v=-7n6q33We28)

minigodcs 佐证：稳定性不足"comes from the inability to match their aiming speed to the target's velocity" [04:43-04:50](https://www.youtube.com/watch?v=DP954gl592E)。

### 2.5 三种技术的适用场景对比

| 技术 | 本质 | 什么时候用 | 引用 |
|---|---|---|---|
| **Flicking（甩枪）** | 静态/位移大目标的快速定位 | 目标静止、出现位置已知、需要快速切换 | RiddBTW #3 全篇 |
| **Tracking / Reactive（反应式跟枪）** | 实时跟随，靠频繁微修正贴住目标 | 目标运动不可预测、频繁变向（AD spam、抖动） | "Reactive tracking... requires high levels of reading, reactivity, endurance and muscle control" [00:50](https://www.youtube.com/watch?v=VFjx969H-cg) |
| **Anticipation / Leading（预测式等枪）** | 预摆到目标未来位置，flick 到预测点等目标撞来 | 目标轨迹可预测（Floating Heads、Bounce 180 弧线、Popcorn 抛物） | Voltaic ep2 [03:12](https://www.youtube.com/watch?v=nnDHvHPlQ1Y) |

关键边界（minigodcs）：**预测式打不可预测目标会害人**——预测失效时应切回主动读靶+微修正，而不是死守预判 [03:46-04:09](https://www.youtube.com/watch?v=DP954gl592E)。

### 2.6 从"跟枪"过渡到"等枪"的训练阶梯

1. **不要等目标进准星**（RiddBTW 称这是新手最大错误）：
   > "waiting for the bot to enter the crosshair — this is probably the biggest mistake that I see... assume the bot is gonna keep going in the same direction."
   > —— [36:05-36:32](https://www.youtube.com/watch?v=DcNP0F_gpOQ)
2. **从可预测轨迹开始**：Floating Heads Timing 400%、Bounce 180（弧线可预测）、Popcorn（抛物线可预测）——这类场景"很大一部分技术其实和静态一样：flick + 微调整" [30:49-31:05](https://www.youtube.com/watch?v=DcNP0F_gpOQ)。
3. **在目标最慢/最可预测处点击**：Bounce 180 打 apex [01:01](https://www.youtube.com/watch?v=ZBNEAgaGjdQ)。
4. **hit-confirmation 时间逐周压缩**：Voltaic 官方说追踪到开火的间隔应随进步持续缩短 [02:29-02:34](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。
5. **配合静态基础**："don't just focus so much on dynamic only because a large part of your technique is actually developed in static" [32:11-32:17](https://www.youtube.com/watch?v=DcNP0F_gpOQ)。

---

## 3. 精选视频列表

见 `selected_videos.json`（24 个，含 URL/频道/观看量/核心观点/字幕路径）。核心 12 个：

| # | 视频 | 频道 | 观看 | 一句话 |
|---|---|---|---|---|
| 1 | [Dynamic Clicking Crash Course #3](https://www.youtube.com/watch?v=DcNP0F_gpOQ) | RiddBTW | 114k | 动态点击=读靶+提前量+模式学习；FH Timing 400% 直接教学 |
| 2 | [Dynamic Clicking Squeakquel #4](https://www.youtube.com/watch?v=QXO77LHPV5Q) | RiddBTW | 20k | 等枪与"等目标进准星"的边界；edge tracking |
| 3 | [Speed Matching in Precise Tracking](https://www.youtube.com/watch?v=-7n6q33We28) | MattyOW | 135k | 跟枪慢=张力不足；张力管理是核心机制 |
| 4 | [Dynamic Aim Ep.2（官方）](https://www.youtube.com/watch?v=nnDHvHPlQ1Y) | Voltaic | 112k | 两种打法：hit confirmation（新手）vs target leading（进阶） |
| 5 | [Reactive Tracking Crash Course #11](https://www.youtube.com/watch?v=VFjx969H-cg) | RiddBTW | 82k | 反应式跟枪=最难机制，靠频繁微修正 |
| 6 | [Why you still struggle with moving targets](https://www.youtube.com/watch?v=DP954gl592E) | minigodcs/Lorys | 75k | 预测 vs 主动读靶；抖动目标要 under-aim |
| 7 | [HOW TO: MOVING DOTS](https://www.youtube.com/watch?v=ZBNEAgaGjdQ) | christmasiscancelled | 33k | 选最安全时机点击；打弧线 apex |
| 8 | [HOW TO: Thin Gauntlet](https://www.youtube.com/watch?v=oVOL2u2tg-0) | christmasiscancelled | 22k | 孤立弱 bot；外部注意力 vs 内部注意力 |
| 9 | [Fix Shaky/Jittery Aim（官方）](https://www.youtube.com/watch?v=6pJGSYXcbCc) | KovaaKs | 674k | 抖动瞄准修复官方短教学 |
| 10 | [Fix Microadjusting](https://www.youtube.com/watch?v=Hj8fYdea4tQ) | 4BangerKovaaks | 5k | 微定位问题多半根子在 flick 不准 |
| 11 | [Fix Overflicking](https://www.youtube.com/watch?v=XNIYrW6dTQM) | 4BangerKovaaks | 55k | under-aim 再微调，不要过甩 |
| 12 | [Shaky Aim 7 Solutions](https://www.youtube.com/watch?v=feUxul6TGyQ) | 4BangerKovaaks | 120k | 抖动=肩部/手指/前臂张力位置不对 |

---

## 4. 反面意见 / 重要 nuance

### 4.1 "等目标进准星"并非全无是处——高手确实会等，但原因不同

RiddBTW 借观众 SS Ninja 之口指出：
> "sometimes you DO want to wait for targets to come into your crosshair... high level aimers... do that often, and that's because they are basically reading the entire map... they are going to passively wait for a target that they know is immediately going to fall into their crosshair. So there definitely IS situations where you do want to do it, but as a general rule when I'm helping NEW players... [don't]."
> —— Squeakquel #4 [02:54-03:37](https://www.youtube.com/watch?v=QXO77LHPV5Q)

**解读**：高手"等"是**地图阅读后的预摆**（知道目标必然经过这里），新手"等"是**反应慢的借口**。两者动作像、本质不同。用户当前属于后者，所以 RiddBTW 的规则"不要等"适用于用户。

### 4.2 纯预判在变向/抖动目标上反而有害

> "predictions, while useful, can actually be harming us during the active aiming process... causing us to feel stiff with our micros."
> —— minigodcs [03:53-04:09](https://www.youtube.com/watch?v=DP954gl592E)

即：**等枪不是无脑提前量**——遇到不规律抖动，死守预判会导致微定位僵硬、越修越难受。正确做法是预测用于"大方向预摆"，抖动部分交给主动读靶+微修正。

### 4.3 不要孤立练微定位

> "The problem isn't actually with your micro adjusting, but your flicks being bad at its core."
> —— 4Banger [01:34-01:38](https://www.youtube.com/watch?v=Hj8fYdea4tQ)

微定位难受，多半不是"微定位肌肉"的问题，而是大 flick 落点不准→每次都要大幅补救。

---

## 5. 关键引用原文（Top 10）

1. **"flicking to where the target's going to be when you flick — that's essentially what you want to aim for."** — RiddBTW #3 [31:00](https://www.youtube.com/watch?v=DcNP0F_gpOQ)
2. **"The less time that elapses between arriving at this point of contact and the target meeting the Crosshair, the better the target lead execution."** — Voltaic [03:23-03:29](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)
3. **"The amount of time you'll need to track a target before firing will continually decrease."** — Voltaic [02:29-02:34](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)
4. **"Too little tension will result in your motion lagging behind the target."** — MattyOW [02:57-03:01](https://www.youtube.com/watch?v=-7n6q33We28)
5. **"Waiting for the bot to enter the crosshair — this is probably the biggest mistake that I see."** — RiddBTW #3 [36:05](https://www.youtube.com/watch?v=DcNP0F_gpOQ)
6. **"Assume the bot is gonna keep going in the same direction."** — RiddBTW #3 [36:18](https://www.youtube.com/watch?v=DcNP0F_gpOQ)
7. **"We risk ourselves to over adjust... that's why our approach would shift into under aiming in order to properly speed match."** — minigodcs [05:11-05:17](https://www.youtube.com/watch?v=DP954gl592E)
8. **"Positioning our Crosshair beneath it on the y-axis and in front of it on the x-axis."** — Voltaic Popcorn 例 [04:30-04:35](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)
9. **"Internal focus is when you are focused on your body such as your wrist or your arm... external focus has shown to have faster rates of improvement."** — christmasiscancelled [01:59-02:10](https://www.youtube.com/watch?v=oVOL2u2tg-0)
10. **"The problem isn't actually with your micro adjusting, but your flicks being bad at its core."** — 4Banger [01:34-01:38](https://www.youtube.com/watch?v=Hj8fYdea4tQ)

---

# 追加主题 1：小球平移 + 垂直不规律抖动时的微定位（"微定位感觉很难受"）

## A1. 为什么会"难受"——三个叠加原因

1. **内部注意力（internal focus）绑架**：盯着手腕/手指的小动作 → 意识控制每一次微修正 → 越控越僵。christmasiscancelled（Thin Gauntlet 榜前 4）：
   > "Internal focus is when you are focused on your body such as your wrist or your arm... external focus has shown to have faster rates of improvement over internal."
   > —— [01:59-02:10](https://www.youtube.com/watch?v=oVOL2u2tg-0)
   > "When you popped off in game, no part of you was thinking about mechanics — you were externally focused." [02:39-02:44](https://www.youtube.com/watch?v=oVOL2u2tg-0)
2. **预测失效导致"僵硬微修正"**：垂直抖动是随机的，你的预判模型失效 → 身体 freeze → 手动逐点追 = 难受。minigodcs：
   > "Prediction... causing us to feel stiff with our micros. An ideal approach would be enforcing focus on actively reading the strafes and changes of direction."
   > —— [04:05-04:14](https://www.youtube.com/watch?v=DP954gl592E)
3. **过修正（over-correction）循环**：水平跟枪慢→补偿时用力过猛→垂直方向甩过头→再反向修→抖动放大。MattyOW：张力过高 = "jerky skip ahead motions and over correction" [02:50-02:57](https://www.youtube.com/watch?v=-7n6q33We28)；4Banger 专片《Fix Overflicking》[XNIYrW6dTQM](https://www.youtube.com/watch?v=XNIYrW6dTQM)。

## A2. 复合运动目标的正确策略：水平等枪 + 垂直主动读

综合 Voltaic + minigodcs + christmasiscancelled：

- **水平主方向**：保持 tracking / speed match，准星维持一个小的前向 offset（提前量），不要追在目标正后方——"offsetting in front of it, we'll be able to focus on the target when it's slower and most predictable" [Voltaic 04:21-04:28](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。
- **垂直抖动**：**不要试图逐帧跟垂直抖动**。它是随机的、不可预判的——预测它必输。正确做法是：
  1. 降低瞄准强度（aiming intensity），deliberately **under-aim**（故意欠一点），靠小幅度平滑修正贴回去，而不是每抖一下就大补 [minigodcs 05:11-05:17](https://www.youtube.com/watch?v=DP954gl592E)。
  2. 把注意力放在**目标整体运动的节奏和方向变化**上，而不是准星与目标的瞬时像素差 [minigodcs 04:10-04:19](https://www.youtube.com/watch?v=DP954gl592E)。
  3. 微修正要"自动发生"：4Banger——"helping your body adjust automatically when you're not even thinking about it"，靠 evasive side-to-side bot 场景练出来 [02:21-02:25](https://www.youtube.com/watch?v=Hj8fYdea4tQ)。
- **Edge tracking 思路**（RiddBTW 转述 Aimer7）：对频繁变向的目标，把准星放在两条轨迹中间，预判反向时刻，而不是全程贴中心跑——"it's less wasteful in your mouse movement to follow the bot through its movements" [Squeakquel 04:15-04:33](https://www.youtube.com/watch?v=QXO77LHPV5Q)。

## A3. 训练阶梯（可照做）

| 阶段 | 场景 | 专注点 |
|---|---|---|
| 1. 大目标+匀速 | Thin Gauntlet 大 bot / Smooth Sphere | 先建立 smooth speed match + 低张力 |
| 2. 中等目标+横移 | Thin Gauntlet 357-357（只练弱 bot 3/5/7）| 隔离弱项 bot，invincible 版本免惩罚 |
| 3. 加垂直抖动 | FLA XYC Target Switch / TAM Target Control（侧向往复小变向）| 让微修正"自动化"，不意识控制 |
| 4. 小目标+抖动 | Thin Gauntlet（thinner 版本）| under-aim + 外部注意力（听命中音） |
| 5. 心理调节 | 全程 | 低 sens 练 smoothness 找感觉，再回正常 sens 复现（ins 方法）[01:31-01:44](https://www.youtube.com/watch?v=oVOL2u2tg-0) |

**关键心法**（christmasiscancelled）："I try to hear the hit sounds in my head of a good performance, then try to match the hit sounds I actually hear to those in my head." [02:31-02:36](https://www.youtube.com/watch?v=oVOL2u2tg-0) —— 用声音节奏代替像素盯防。

---

# 追加主题 2：Floating Heads Timing 400% 的正确训练法

## B1. 场景机制

RiddBTW 亲自点名该场景：
> "The final dynamic bot type is floating heads... Floating Heads Timing 400% is probably the most popular one out there."
> —— [30:22-30:35](https://www.youtube.com/watch?v=DcNP0F_gpOQ)

Voltaic 官方分类：Floating Heads = "targets moving with **obvious intent**"（可预测度高）[01:42-01:46](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。

**这意味着该场景的正确技术 = 等枪（target leading），不是纯跟枪，也不是等目标进准星。**

## B2. 正确技术（RiddBTW 原话拆解）

> "A lot more of your typical static technique that you're applying here, because the bots are moving in such a predictable path. You are flicking and then micro adjusting just like you would in static, and you're flicking to where the target's going to be when you flick."
> —— [30:49-31:05](https://www.youtube.com/watch?v=DcNP0F_gpOQ)

> "You still want to avoid the bad habit of waiting for the target to come into your crosshair. That is not the method to improve... It's really important not to develop that habit."
> —— [31:06-31:25](https://www.youtube.com/watch?v=DcNP0F_gpOQ)

操作分解：
1. **预判轨迹**：Floating Heads 走固定漂浮路径 → 选一个目标时，直接 flick 到它**下一步会到的位置**（提前量 = 目标速度 × 你的 flick+反应时间）。
2. **微修正贴上去**：flick 落点和目标实际位置有差 → 像静态一样做小修正（不是重新跟枪）。
3. **点击时机**：目标撞进准星的瞬间点；不是准星追到目标身上才点。
4. **选目标优先级**：打"最容易被命中的目标"（viability）——路径慢/接近你预摆位置的优先 [christmasiscancelled 00:44-00:48](https://www.youtube.com/watch?v=ZBNEAgaGjdQ)。

## B3. 400% 难度的训练策略

YouTube 社区对 Floating Heads Timing 400% 没有"必须先 100% 再 200%"的明文阶梯（Valkie 的 Click Timing Guide [wBhCFYuRzk4](https://www.youtube.com/watch?v=wBhCFYuRzk4) 与 Lew 的 Floating Heads [_5u0YN6gHbA](https://www.youtube.com/watch?v=_5u0YN6gHbA) 字幕均被 429 拦截，未能取证）。**基于已取证材料给出的可执行阶梯**：

| 步骤 | 做什么 | 专注技术点 |
|---|---|---|
| 1 | 降倍率（若场景可调）或换 Floating Heads 普通版 3-5 局 | 只练"flick 到预测点"的感觉，不追分 |
| 2 | 400% 打 3 组，每组只盯一件事：**flick 落点在目标前方（提前量），不是目标当前位置** | RiddBTW [31:00](https://www.youtube.com/watch?v=DcNP0F_gpOQ) |
| 3 | 每组后自检：有没有"等目标进准星"？有 → 下一组故意 flick 得更早 | [31:06](https://www.youtube.com/watch?v=DcNP0F_gpOQ) |
| 4 | 配合静态点击场景 5-10 分钟热身 | "large part of your technique is developed in static" [32:11](https://www.youtube.com/watch?v=DcNP0F_gpOQ) |
| 5 | 打不动时**降级不硬撑**：回普通 Floating Heads 或 Bounce 180（同样可预测轨迹） | Bounce 180 打 apex [01:01](https://www.youtube.com/watch?v=ZBNEAgaGjdQ) |

## B4. 常见错误（取证）

1. **等目标进准星**（最大错误）—— RiddBTW [36:05](https://www.youtube.com/watch?v=DcNP0F_gpOQ)。
2. **假设目标永远同向 → 变向时丢失** —— 教训来自 minigodcs 的 kosa 案例：死守"目标继续走同方向"的预测，被反向 strafe 惩罚 [03:37-03:46](https://www.youtube.com/watch?v=DP954gl592E)。Floating Heads 有路径折返点，到折返点附近要切换为主动读靶。
3. **只练动态不练静态** —— [32:11](https://www.youtube.com/watch?v=DcNP0F_gpOQ)。
4. **命中确认时间越来越长**（hit-confirmation 不收缩）—— 违背 Voltaic 进阶方向 [02:29](https://www.youtube.com/watch?v=nnDHvHPlQ1Y)。

## B5. 成绩基准

本次未取证到 Floating Heads Timing 的官方分数基准（Voltaic benchmark 表需另查 voltaic.gg；Valkie/Lew 视频字幕 429 未获取）。**如实标注：基准分待补**，建议下一步查 Voltaic 官方 benchmark sheet。

---

## 6. 对用户 VDIM 练习的直接建议（综合结论）

1. **"匹配目标速度才点击"是 hit confirmation 新手期技术**——本身不是错，但目标是随进步把"先跟稳再点"的时间压缩，最终过渡到"flick 到目标未来位置等它撞进来"（target leading）。Voltaic 官方背书此方向。
2. **"跟枪慢"的直接修复是张力管理**（MattyOW）：跟枪落后 = 手指/手腕张力不足。长直线保持恒定横向张力，变向时才用手腕快修。
3. **Floating Heads Timing 400% 用等枪打**：flick 到预测位置 + 小修正 + 目标撞上来时点；严禁等目标进准星。
4. **小球+垂直抖动**：水平方向保持小提前量 speed match；垂直抖动不逐帧追，改为 under-aim + 平滑微修 + 外部注意力（听命中音节奏）。
5. **微定位难受**不是手的问题，多半是：① 盯着手腕（内部注意力）② 预测失效后僵住 ③ over-correction。按 A3 阶梯从大目标/匀速开始加难度。

---

## 附：未获取字幕清单（如实标注）

| 视频 | 原因 |
|---|---|
| [YBbcYMk8-9o](https://www.youtube.com/watch?v=YBbcYMk8-9o) MattyOW Pure Reactivity | 该视频无任何英文字幕（手动/自动均无） |
| [F7S-mafDz08](https://www.youtube.com/watch?v=F7S-mafDz08) RiddBTW Smooth Tracking #7 | 字幕 CDN 持续 429，两轮退避未成功 |
| [00meppeDAC0](https://www.youtube.com/watch?v=00meppeDAC0) WestProter reload vs accuracy | 同上 429 |
| [wBhCFYuRzk4](https://www.youtube.com/watch?v=wBhCFYuRzk4) Valkie Click Timing Guide | 同上 429 |
| [_5u0YN6gHbA](https://www.youtube.com/watch?v=_5u0YN6gHbA) Lew Floating Heads | 同上 429 |
| [cmQh7HKSrdA](https://www.youtube.com/watch?v=cmQh7HKSrdA) Daniel Kapadia | 区域/客户端不可用 |
