# Day3 速度转火（Speed Switching）训练指南

> **一句话总结**：直线路径 + 初始 flick 落上去 + 眼睛提前看下一个 + flick 后无缝跟踪 + 不打残血。首次打不要冲速度，用 70% 速度把 5 个技术做对，感觉对了再加速。

---

## 一、这个主题在练什么——本质定义

速度转火不是"比谁 flick 快"，它是 **Click Timing + Tracking 的混合体**，核心在**两个目标之间的过渡质量**：

> **初始 flick 落在目标上 → 立即无缝过渡到平滑跟踪 → 击杀 → 眼睛已经锁定下一个目标 → 直线路径切过去**

VDIM 官方对 Switching I 的定义原文：
> "Landing your initial flick on each target whenever possible and smoothly tracking its path will be the main aspects of a successful run. **Micro-corrections should be few and far between**, and partially damaged bots should be avoided whenever possible."

翻译：**每次尽量让初始 flick 直接落在目标上，然后平滑跟踪它的路径。微修正越少越好，尽量别打残血 bot。**

**你的起点**：只有 1 个未达标场景（VoxTS Click Easier 差 6 分，Stability 子类），基础不错。但速度转火是最容易"看起来强但实际有漏洞"的主题——低难度下靠反应速度能撑，高难度会集中爆发。

---

## 二、首次打必须抓住的 5 个核心技术（可实操、可固化）

### 🔑 技术 1：直线路径（Pathing）——最重要的一条

**是什么**：从目标 A 到目标 B，鼠标走的是**直线**，不是弧线、不是 S 形、不是先往上再往下。

**为什么重要**：Voltaic Speed Routine 设计者 ViscoseCanine 说——
> "The two static switching scenarios develop speed by making you focus intently on accuracy and not overshooting rather than just raw speed. **Making your lines straighter and more direct will lead to more efficient mouse movement, resulting in faster and more accurate switches.**"

速度不是靠手甩得快，是靠**路径短**。直线是两点之间最短路径。

**怎么练（首次打就用这个自检）**：
- 每一次切换后问自己："我刚才走的是直线吗？"
- 如果发现路径是弯的，**下一把刻意放慢速度，只走直线**
- 用手臂走大角度，手腕收尾，不要用手腕走全程

**固化标志**：你能感觉到"从 A 到 B 是一条直线"，而不是"我在移动鼠标"。

---

### 🔑 技术 2：初始 flick 直接落上去，微修正越少越好

**是什么**：flick 结束时准星**已经在目标上**，不需要再拖回来或推过去。

**为什么重要**：VDIM 官方明确说"Micro-corrections should be few and far between"。微修正多 = 初始 flick 不准 = 浪费时间。

**常见错误**（你可能会犯的）：
- ❌ flick 超过目标，然后拖回来（over-flicking）
- ❌ flick 没到目标，然后推过去（under-flicking）
- ❌ flick 上去后抖几下才稳定

**怎么练**：
- **前 3 把刻意放慢**：flick 到目标附近时**主动减速**，让准星"落"在目标上，而不是"撞"上去
- 3D Aim Trainer 的建议："Aim to arrive just on the target rather than past it, and let the crosshair settle for a beat before you fire instead of dragging back."
- 如果你一直滑过去 → **说明摆动太快，放慢节奏**，直到射击在到达时命中，再逐渐加速

**固化标志**：10 次切换里有 7 次以上初始 flick 直接落在目标上，不需要明显修正。

---

### 🔑 技术 3：眼睛先动，手跟随——"下一个目标已经在脑子里"

**是什么**：**在打当前目标的时候，眼睛已经看到了下一个目标**，手打完当前目标后直接切过去，不需要"找"下一个目标。

**官方原文**：
- "Always make sure to have the next target in mind."（voxTargetSwitch Smooth 的官方说明）
- "Move your eyes to the target first, then let the hand follow the visual decision."（fpstrain.us）

**为什么重要**：这是速度转火和静态点击最大的区别。静态点击是"打完一个 → 找下一个 → flick"，速度转火是"打这个的时候已经看到下一个 → 打完直接切"。

**怎么练**：
- 打当前目标时，**用余光扫描下一个目标的位置**
- 击杀当前目标的瞬间，**眼睛已经移到下一个目标**
- 手跟随眼睛的方向走直线
- 如果你发现自己"打完一个愣一下才找下一个"→ 说明眼睛没跟上，**下一把刻意提前看**

**固化标志**：击杀一个目标后，准星移动方向是**直接指向下一个目标**，没有停顿和搜索。

---

### 🔑 技术 4：flick → 跟踪的无缝过渡——"落上去就开始跟"

**是什么**：flick 结束的瞬间，**立即开始平滑跟踪**目标的移动，没有停顿、没有抖动。

**官方原文**：
- "Your transition to smoothness upon coming out of your initial flick should ideally be both seamless and immediate."（VDIM Switching II 说明，同样适用于 Speed）
- "Static target switching requires an immediate stop and dynamic requires an immediate direction change."（Aiming.Pro 定义）

**为什么重要**：速度转火的目标是**移动的**（不像静态点击目标是静止的）。flick 上去后如果停顿一下，目标已经移走了，你就需要重新追。

**怎么练**：
- flick 到目标时，**手臂不要完全锁死**，保持一点"活性"，目标一动你就能跟
- 想象你的准星是"粘"在目标上的，落上去就粘住
- 如果发现 flick 上去后准星是"停"在那里而不是"跟"着目标 → 说明手臂锁太死，**放松一点**

**固化标志**：flick 上去后，准星和目标之间**没有相对运动**（你在跟着它走）。

---

### 🔑 技术 5：不打残血，按住开火——"效率优先"

**是什么**：
- **尽量打满血目标**，不要在残血目标上浪费时间（VDIM 官方："partially damaged bots should be avoided whenever possible"）
- **按住开火键不放**（VDIM 官方："Preferably, hold down fire during the entire duration of the scenario"）

**为什么重要**：
- 打残血目标需要更多子弹才能击杀，同样的时间你可以打 2 个满血目标
- 按住开火键强迫你"在移动中射击"，而不是"停下来瞄准再射击"——这更接近实战

**怎么练**：
- 如果一个目标被别人打残了（或者你打了几枪没打死），**立刻切换到下一个满血目标**
- 全程按住左键，不要松开
- "Do not follow a single target for more than one click, if you miss target switch to the next one anyways."（Voltaic x WHJ 说明）

**固化标志**：你会主动"跳过"残血目标，优先打满血的。

---

## 三、12 个场景逐个拆解——每个场景练什么、注意什么

| 场景 | 类型 | 练什么 | 首次打注意 |
|---|---|---|---|
| **patTargetSwitch easy** | 训练 | 基础切换速度 + 直线路径 | 放慢速度，只走直线，初始 flick 落上去 |
| **patTargetSwitch 90 easy** | 训练 | 90度角切换 | 注意大角度用手臂，不要用手腕甩 |
| **patCircleSwitch NR** | 训练 | flick 后平滑精确（官方："Good for being smooth and precise after flicking"） | flick 上去后立刻开始跟，不要停 |
| **psalmTS Voltaic Easy** | 基准 | 综合速度转火能力 | 这是基准场景，正常打，记录分数 |
| **psalmTS Voltaic LowTTK** | 训练 | 低 TTK 下的快速击杀 | 击杀更快，切换更频繁，注意眼睛提前看下一个 |
| **VT psalmTS Advanced Regen** | 训练 | 再生血量下的持续输出 | 目标会回血，注意不要打残血就走 |
| **VT psalmTS Novice** | 训练 | psalmTS 的降级版 | 比 Easy 更简单，用来热身和找感觉 |
| **Pokevox Easy LG56** | 训练 | LG56 定制的速度转火 | 按住开火，直线路径 |
| **voxTS Voltaic LowTTK** | 训练 | 极低 TTK + 慢速横向移动的 180 度切换 | 官方："Focus on smoothly tracking each bot with as little jitter as possible before switching" |
| **VoxTS Voltaic Jumbo Smooth** | 训练 | 大目标下的平滑切换 | 目标大，更容易初始 flick 落上去，重点练平滑过渡 |
| **voxTS Viscose Varied** | 训练 | 大小变化的目标切换 | 目标从大变小，注意小目标时的精度 |
| **VT skyTS Novice** | 训练 | 空中目标的速度转火 | 目标在空中，注意垂直方向的切换 |

---

## 四、首次打 Day3 的完整流程建议

### 热身（5 分钟）
- 用 Easy 热身 playlist（`KovaaKsChattingThinDeserteagle`）打 2-3 个场景
- 重点：活动手腕和手臂，找到"直线移动"的感觉

### 主训练（30-40 分钟）
按清单顺序打，**前 3 个场景用 70% 速度**，重点找技术感觉：

1. **patTargetSwitch easy × 4**：第一把 50% 速度只走直线，第二把 70%，第三把正常，第四把冲分
2. **patTargetSwitch 90 easy × 4**：注意大角度用手臂
3. **patCircleSwitch NR × 4**：flick 后立刻跟
4. **psalmTS Voltaic Easy × 3**：基准场景，正常打，记录分数
5. 后续场景按推荐次数打

### 打完后（2 分钟）
- 记录 psalmTS Voltaic Easy 的分数（这是基准场景，用来追踪进步）
- 问自己 3 个问题：
  1. 今天哪次切换感觉"对了"？（初始 flick 直接落上去 + 直线 + 无缝跟踪）
  2. 最常见的错误是什么？（over-flick？路径弯？眼睛没提前看？）
  3. 下一把要改什么？

---

## 五、进步的感觉——怎么知道自己在进步

### 主观进步阶段（从低到高）

| 阶段 | 感觉 | 表现 |
|---|---|---|
| **阶段 1** | "每次切换都要找下一个目标" | 打完一个愣一下，搜索下一个，切换路径是弯的 |
| **阶段 2** | "我能提前看到下一个目标了" | 眼睛先动，手跟随，切换路径开始变直 |
| **阶段 3** | "初始 flick 经常直接落在目标上" | 微修正明显减少，flick 上去就能跟 |
| **阶段 4** | "切换是无缝的，像流水一样" | flick→跟踪→击杀→切换，整个过程没有停顿，准星像粘在目标上 |
| **阶段 5** | "我不用想，手自己就知道往哪走" | 完全内化，大脑只需要决定"打哪个"，手自动完成直线切换和跟踪 |

### 客观进步指标
1. **psalmTS Voltaic Easy 分数**：每 2 周对比，应该稳步上升
2. **初始 flick 命中率**：10 次切换里有几次直接落在目标上（阶段 3 应该 ≥70%）
3. **微修正次数**：每把明显的微修正次数应该越来越少
4. **切换路径直度**：回放时看鼠标轨迹，直线占比应该越来越高
5. **击杀效率**：同样时间内击杀数应该越来越多

---

## 六、最容易半途而废的 3 个陷阱 + 怎么避开

### 陷阱 1："这个主题我已经很强了，不用认真练"
**真相**：你只有 1 个未达标场景（VoxTS Click 差 6 分），说明你基础不错，但**速度转火是所有瞄准类型里最容易"看起来强但实际有漏洞"的**——你可能靠反应速度在撑，但路径不直、微修正多、flick→跟踪过渡差，这些问题在低难度下看不出来，到高难度会集中爆发。

**怎么办**：把 Day3 当成**打磨技术**的日子，不是"刷分"的日子。每把都用自检清单检查 5 个核心技术。

### 陷阱 2："速度转火就是越快越好，我要冲速度"
**真相**：Voltaic Speed Routine 的核心原理是**"通过精度和不过冲来发展速度，而不是原始速度"**。冲速度只会让你养成 over-flicking 的坏习惯，以后很难改。

**怎么办**：前半段训练用 70% 速度找直线路径和初始 flick 落点的感觉，后半段再冲分。**慢就是快**。

### 陷阱 3："打了几天没感觉，这个主题不适合我"
**真相**：速度转火的进步是**阶梯式**的——你会有 1-2 周感觉完全没变化，然后突然某一把"顿悟"了（就像那个 Reddit 高玩 ww5ts 卡了 9 小时后突然顿悟"我在用 1w3ts 的模式玩 ww5ts！"）。顿悟前的积累是必要的。

**怎么办**：每把都记录"对的感觉"出现的次数，哪怕只有一次。当你能稳定复现"对的感觉"时，分数自然会跳。

---

## 七、一句话总结

> **Day3 速度转火的核心 = 直线路径 + 初始 flick 落上去 + 眼睛提前看下一个 + flick 后无缝跟踪 + 不打残血。**
>
> **首次打不要冲速度，用 70% 速度把这 5 个技术做对，感觉对了再加速。进步的标志是"切换像流水一样无缝"，不是"分数涨了多少"。**

---

## 📎 参考来源

- VDIM S5 官方文档（Lowgravity56 & 4rk）：Switching I 章节
- Voltaic Fundamental Aim Training Routines 2.5：Speed Switching 章节
- Voltaic Speed Routine（ViscoseCanine & christmasdenier）：核心原理
- Voltaic x WHJ Routine：Speedswitch Click 技术细节
- Aiming.Pro：Target Switching 定义
- fpstrain.us：Target Switching Drill 要点
- 3D Aim Trainer：过冲分析与减速建议
- Reddit r/FPSAimTrainer：ww5ts 顿悟案例（27天 VDIM Intermediate → Master Complete）
- B站转载：Voltaic 社群游戏专项训练清单（voxTargetSwitch Smooth 说明）
