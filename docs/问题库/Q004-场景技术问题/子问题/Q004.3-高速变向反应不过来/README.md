# P003 - Midrange Short Strafes Invincible Raspberry Easy - 高速变向反应不过来

> 记录日期：2026-10-10
> 场景：Midrange Short Strafes Invincible Raspberry Easy
> 大类：Reactive Tracking（反应跟枪）
> 对应VDIM：Day2 反应跟枪
> 状态：未解决

---

## 问题描述

### 用户自述
"这是一个高速平滑加一个高速减速转向加速的情景，我一直反应不过来"

### 场景特点分析
- **Midrange**：中距离目标，目标在屏幕上的移动幅度中等
- **Short Strafes**：短距离快速变向移动，不是长距离平滑移动
- **Invincible**：无敌目标，不需要击杀，纯跟枪训练
- **Raspberry Easy**：Easy难度版本，目标速度相对较慢

### 目标运动模式
用户分析的运动周期（已核实正确）：
1. **高速平滑阶段**：目标以恒定速度向一个方向移动
2. **高速减速阶段**：目标接近变向点时快速减速
3. **转向加速阶段**：目标变向后快速加速到新方向的匀速
4. **循环**：重复上述过程

**B站高玩拆解的运动模式**：
- 模式1（主流）：变向 → 平滑运动 → 变向 → 平滑运动 → ...
- 模式2（偶尔）：变向 → 立即再变向（假动作/连续变向）

**核心难点**：在"减速→转向→加速"的瞬间，目标的速度和方向同时变化，需要快速反应并调整跟枪速度。

---

## 可能的原因（待验证）

1. **没有用undertracking（欠跟）**：准星放目标正中心，变向时没有缓冲
2. **在预测变向，而不是反应变向**：一直在"等"目标变向，全程紧张
3. **变向后没有立即进入平滑跟踪**：一直在"修正"，没有commit到新方向
4. **眼睛看准星而不是看目标**：手眼协调不足
5. **Long Strafes基础没打牢**：可能跳过了基础阶段直接练Short Strafes
6. **紧张导致手臂/手腕僵硬**：高速变向时肌肉紧张，影响微调能力

---

## 多渠道调研记录

### 渠道1：Voltaic 官方 Reactive Tracking 技术指导
**来源**：Voltaic x KovaaKs - Fundamental Aim Training Routines 2.5

> "Attempt to find opportunities to **undertrack** your target and position your crosshair **within the target** such that you have a **buffer** to react to sudden direction changes."

**核心技术：Undertracking（欠跟）**
- 不要把准星放在目标正中心
- 而是放在目标**偏后一点**的位置（目标移动方向的反方向边缘）
- 这样当目标变向时，准星有一个"缓冲距离"，不会立刻被甩出去
- 变向后，只需要从小幅度调整开始，而不是从完全脱离目标开始

### 渠道2：VDIM 官方 LG56 的 Reactive Tracking 指导
**来源**：Voltaic Daily Improvement Method for Aimlabs by Lowgravity56

> "Focus more on the **target** than your crosshair."
> "Try to **match the target's movement** instead of chasing after it."
> "**Be reactive, not predictive.**"
> "An additional tip is to **assume the target won't change directions**, and to only react when it actually does, then smoothly return back to the target."

**4个关键点：**
1. **眼睛看目标，不是看准星**
2. **匹配目标速度，不是追赶目标**——目标匀速时你也匀速，目标减速时你也减速
3. **反应，不要预测**——不要提前猜目标什么时候变向
4. **假设目标不会变向**——只在目标实际变向的瞬间才反应，然后立刻回到平滑跟踪

### 渠道3：Voltaic Game Specific Routines 指导
**来源**：Voltaic x KovaaKs - Game specific aim training routines

> "react to direction changes as fast as you can, but make sure to **transition into a smooth tracking motion committing to the direction that the bot is going**, focus on reacting not predicting"
> "Also make sure to focus on the target instead of just looking at it or eye-locking on your crosshair. By focusing on the target, you essentially help yourself to read the target's movement better."

**关键：变向后立即"commit"到新方向**
- 变向瞬间：快速反应，调整方向
- 变向后**立即**进入平滑跟踪状态，不要一直"反应模式"
- 心里想着"目标现在往这个方向走了，我要平滑地跟住它"

### 渠道4：4Banger 反应跟枪进阶路径
**来源**：4Banger KovaaK's Improvement Guide & FAQ for 2024

> "Nr 1, work on fundamentals of reactive, that is your **long strafes**, centering and generally easy versions of fast strafe scenarios. Important is to get really good on each one of these fields before moving onto step Nr 2, which is to **SPAM reactive strafes**, this is your close fast strafes, midrange fast strafes, vss gp9 ETC."

**进阶路径（用户可能跳过了第一步）：**
1. **基础阶段**：Long Strafes（长距离变向慢）、Centering、Easy版本的Fast Strafe
2. **进阶阶段**：Midrange Short Strafes、Close Fast Strafes、VSS GP9

**用户情况**：直接练了 Midrange Short Strafes，但可能 Long Strafes 的基础还没打牢。

### 渠道5：B站高玩"理解变向"方法论
**来源**：https://www.bilibili.com/video/BV1P6Tu6pEzt/

> "脑子里不要觉得目标只会左右变向，把它的运动模式拆解为模式1：变向—平滑运动—变向，其次模式2：变向—变向。"
> "在目标变向后你去继续阅读有没有马上变向，没有就默认目标按照1运动，去做好平滑部分的跟踪，心里只想着怎么去做好平滑，目标继续运动下去我的手会转动到什么幅度。"

**核心思维转换：**
- ❌ 错误：一直想着"目标什么时候变向"，全程紧张
- ✅ 正确：变向后先观察"会不会马上再变向"，如果不会，就**全力做好平滑跟踪**，不想变向的事
- 平滑跟踪时，心里想着"目标继续走下去，我的手会转到什么幅度"——提前规划手臂的移动范围

### 渠道6：Aimlabs x Voltaic Fundamental Routines
**来源**：Aimlabs x Voltaic - Fundamental Aim Training routines

> "Focus on **smoothness in between small reactions** to a bot that changes direction fairly slowly."
> "Be able to react quickly when the bot does change direction **without over-flicking**, then **track smoothly until the next directional change**"

**节奏：反应（短）→ 平滑（长）→ 反应（短）→ 平滑（长）**
- 反应只是一瞬间的事
- 大部分时间应该是平滑跟踪
- 不要全程都在"反应"，那样会很累且不准

---

## 解决方案

### 技术层面

#### 技术1：Undertracking（欠跟）
- 目标向右移动时，把准星放在目标的**左边缘**（偏后）
- 目标向左移动时，把准星放在目标的**右边缘**
- 不要追求准星在正中心
- 变向后，准星从"偏后"到"居中"是一个自然的平滑过程

#### 技术2："假设不变向"
- 心里默念："目标不会变向，目标不会变向"
- 全力平滑跟踪，就像目标永远不会变向一样
- 只有当目标**实际变向**的瞬间，才快速反应
- 反应后**立即**回到"假设不变向"的平滑状态

#### 技术3：变向后"Commit"
- 目标变向后，心里默念："现在往X方向走了！"
- 立即把手臂/手腕调整到新方向的匀速跟踪
- 不要一直微调，要**commit**到新方向
- 就像开车变道后，立即回正方向盘，平稳行驶

#### 技术4：眼睛训练
- 练习时，刻意把注意力放在**目标的边缘**上
- 不要看准星，用余光感知准星位置
- 目标变向时，眼睛先跟着目标走，手再跟上

### 训练方法

#### 第1步：降级打基础（1-2周）
暂时把 Midrange Short Strafes 放一放，先练更基础的场景：

| 场景 | 练什么 | 时间 |
|------|--------|------|
| Midrange Long Strafes Invincible | 长距离变向慢，练平滑跟踪基础 | 5-8分钟 |
| Close Long Strafes Invincible Easy | 近距离长变向，练undertracking | 5分钟 |
| Ground Plaza Sparky v3 Easy | 多种变向模式，练反应基础 | 5分钟 |

#### 第2步：回到 Midrange Short Strafes（刻意练习）
每次打时，**只专注一个技术点**：

| 轮次 | 专注点 | 目标 |
|------|--------|------|
| 第1-2轮 | Undertracking | 变向前准星在目标偏后位置 |
| 第3-4轮 | 假设不变向 | 平滑阶段完全放松，不想变向 |
| 第5-6轮 | 变向后commit | 变向后1秒内进入平滑跟踪 |
| 第7-8轮 | 综合 | 把以上技术结合起来 |

#### 第3步：进阶（当Midrange Short Strafes稳定后）
- Close Fast Strafes Invincible
- VSS GP9
- Air Voltaic Easy

### 替代/降级场景
- Midrange Long Strafes Invincible（变向更慢，距离更长）
- Close Long Strafes Invincible Easy（更简单的长变向）
- Ground Plaza Sparky v3 Easy（多种变向模式的基础训练）

---

## 关键要点对比

| 现在可能的做法 | 正确的做法 |
|----------------|-----------|
| 准星放目标正中心 | **Undertracking：准星放目标偏后，留缓冲** |
| 一直在等目标变向（预测） | **假设不变向，只在实际变向时反应** |
| 变向后一直在微调修正 | **变向后立即commit到新方向的平滑跟踪** |
| 眼睛看准星 | **眼睛看目标，余光感知准星** |
| 直接练Short Strafes | **先打Long Strafes基础，再上Short Strafes** |
| 全程紧张反应 | **反应（短）→ 平滑（长）→ 反应（短）的节奏** |

> **核心理念**："Be reactive, not predictive. Assume the target won't change directions, and only react when it actually does."

---

## 验证清单（下次练习时检查）

- [ ] 变向前，准星是否在目标偏后位置（undertracking）？
- [ ] 平滑阶段，是否完全放松，没有在"等"变向？
- [ ] 变向后，是否1秒内进入平滑跟踪，而不是一直修正？
- [ ] 眼睛是否在看目标，而不是看准星？
- [ ] 打完后手臂是否酸痛（紧张的信号）？

---

## 复发记录

| 次数 | 日期 | 场景 | 表现 | 状态 |
|------|------|------|------|------|
| 1 | 2026-10-10 | Midrange Short Strafes Invincible Raspberry Easy | 高速变向反应不过来 | 未解决 |

---

## 相关链接
- VDIM Day2 反应跟枪训练日
- P001: tamTargetSwitch Smooth 方向性控制不对称
- P002: VT PreciseOrb Intermediate Small 小目标微调不行
- B站"理解变向"视频：https://www.bilibili.com/video/BV1P6Tu6pEzt/
- 4Banger改进指南：https://docs.google.com/document/d/1xDN-t9liQmMBSwkX8RMCOwEpYxo48_U7bRLd30Sx0GE/mobilebasic
