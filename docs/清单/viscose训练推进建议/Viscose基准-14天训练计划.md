# Viscose S2 Easier · 14 天训练计划（数据诊断版）

> 依据：2026-09-16 首轮 39 场景实测 + `Viscose基准-原始数据/S2-成绩诊断.json`（每场景档位/下一档线）
> 前提：**每天 1h，目标是追 rank（不是实战上分）**
> 生成日期：2026-09-16

> ⚠️ **排期部分已被取代** → 看 `Viscose基准-每日训练处方.md`（按 evxl charts 官方子类别卡口重做，精确到每天打哪个场景 × 几轮 × 目标分）
> 本文档保留价值：分组诊断与练法要点仍有效。
>
> **与已有文档的分工（别重复看）**
> - `Viscose基准-我的诊断与提升方案.md` —— **战略层**：rank 全景、三个核心发现、按优先级的提升步骤
> - `Viscose基准-低分提升指南.md` —— **方法层**：Viscose 逐类别攻略、社区实证方法
> - `Viscose基准-训练状态与长期结构.md` —— **框架层**：主项/维护/归因三层结构与长期机制
> - **本文档 —— 日程层**：把上面三份的结论落成"每天 1h 具体打什么"的 14 天排期

---

## 一、一句话结论

**你的短板不是"跟枪"两个字，而是「移动目标处理」这一类：动态跟枪/控枪（19 个，平均离下一档 7.6%）+ 动态点击（2 个，平均差 20.6%）；静态点击/切换（18 个）平均只差 4.6%，是你的强项和"送分池"。**

所以 1h 的分配原则是：**主项全给移动目标，静态只做"维持 + 顺手升级"。**

---

## 二、数据诊断（今天首轮的实况）

### 1）档位分布：底子在中低位，但离升级都不远

| 档位 | 场景数 |
| --- | --- |
| Unranked（还没上榜） | 7 |
| Lemming | 9 |
| Hare | 9 |
| Ermine | 6 |
| Puffin | 4 |
| Penguin | 3 |
| Fox | 1（StaticSwitchingVox） |

### 2）按短板类型分组（关键表）

| 分组 | 场景数 | 平均离下一档 | 命中率区间 | 判断 |
| --- | --- | --- | --- | --- |
| **动态跟枪 / 控枪** | 19 | **7.6%** | 13.8% – 62.7% | **主项**（命中率整体偏低 = 修正跟不上） |
| **动态点击**（弹跳/移动靶） | 2 | **20.6%** | 29.3% / 58.8% | **主项**（同源短板） |
| 静态点击 / 切换 | 18 | 4.6% | 42% – 96.6% | 维护项 + 送分池 |

### 3）差距最大的 13 个（这就是主项名单）

| 场景 | 分组 | 得分 | 命中率 | 当前档 | 距下一档 |
| --- | --- | --- | --- | --- | --- |
| cloverRawControl Viscose Easier 50cm | 跟枪 | 2928 | 16.5% | Unranked | **41.4%** |
| VT Bounceshot Viscose Easier | 动态点击 | 300 | 58.8% | Lemming | **21.1%** |
| Popcorn MV Easier | 动态点击 | 120 | 29.3% | Lemming | **20.0%** |
| Leapstrafes Control wobin Easier | 跟枪 | 1697 | 29.1% | Hare | 16.2% |
| Smoothsphere Viscose Easier | 跟枪 | 6825 | 38.6% | Hare | 15.2% |
| VT Controlsphere Viscose Easier | 跟枪 | 1388 | 23.5% | Lemming | 13.2% |
| Controlsphere SuperbAim Viscose Easier | 跟枪 | 4533 | 25.8% | Lemming | 11.1% |
| SmoothBot Perfected Easier | 跟枪 | 2723.5 | 41.3% | Hare | 9.2% |
| Flower Easier 50cm | 跟枪 | 968 | 16.5% | Unranked | 7.8% |
| Air Angelic 4 Voltaic Easy 70% | 跟枪 | 3722 | 62.7% | Ermine | 5.8% |
| Whisphere Viscose Easier | 跟枪 | 9000 | 30.5% | Lemming | 4.3% |
| B180T Voltaic Easy Slower | 跟枪 | 40.4 | 22.8% | Hare | 3.8% |
| RawControlSphere Easier | 跟枪 | 4560 | 25.7% | Unranked | 3.0% |

### 4）两个立刻要处理的机制问题

**① rank 门槛 = 每个子类别至少 1 个分数。** 你现在有 **7 个场景 Unranked**，其中 **5 个只差 1.7–3.2%**：

| 场景 | 差多少到 Lemming | 命中率 |
| --- | --- | --- |
| skyClick Goated Easier | 1.7%（59 → 60） | 78.7% |
| Pasu Voltaic Reload Easier | 2.6%（37 → 38） | 60.7% |
| RawControlSphere Easier | 3.0%（4560 → 4700） | 25.7% |
| psalmTS Viscose Click Easier | 3.2%（30 → 31） | 51.7% |
| CatClick Easier | 7.4%（25 → 27） | 54.3% |
| Flower Easier 50cm | 7.8%（968 → 1050） | 16.5% |
| cloverRawControl Viscose Easier 50cm | 41.4%（2928 → 5000） | 16.5% |

**② 你的分数不差，差的是命中率→分数的转化。** 跟枪场景命中率 13–48%，而 Viscose 明确说："**如果你大部分修正回目标的动作都没跟上，你需要放慢速度，直到建立起能稳定完成这些修正的能力**"。你现在最该做的就是这件事——**降速**。

---

## 三、14 天计划

### 每日 1h 骨架（固定不变）

| 时段 | 时长 | 内容 | 要点 |
| --- | --- | --- | --- |
| ① 热身 / 送分 | 8 min | 静态点击类挑 **2 个离升级最近的**场景，各 2 轮 | 顺手把 StaticSwitchingVox、1w6ts 这类往上推一档 |
| ② 主项 | 35 min | **只打一个子类别**：3 个场景 × 3–4 轮 | 降速；命中率优先于分数；关打击音效 |
| ③ 疲劳巩固 | 7 min | 今天最差的那个主项场景，再打 3 轮 | 练"累了也稳" |
| ④ 归因 | 10 min | 记分数 + 写 2 条：今天最低分场景是谁/为什么；这个场景逼我改进的技术点是 ___ | 这是"测试"而不是"播放列表"的分界线 |

### 第 1 周（9/17 – 9/23）主项 = **Control Tracking（球类 / 控球）**

| 轮次 | 场景组（每天挑 1 轮） |
| --- | --- |
| A | Smoothsphere Viscose Easier｜SmoothBot Perfected Easier｜Whisphere Viscose Easier |
| B | VT Controlsphere Viscose Easier｜Controlsphere SuperbAim Viscose Easier｜RawControlSphere Easier |
| C | Leapstrafes Control wobin Easier｜Flower Easier 50cm｜cloverRawControl Viscose Easier 50cm |

- 每天 1 轮（3 场景 × 3–4 轮 = 9–12 次 ≈ 30–35 min），按 A→B→C→A→B→C 轮换，第 7 天用 C 轮收尾。
- **cloverRawControl 是全场最差（差 41%）**，但它只在 C 轮出现，避免天天打崩心态——它的价值是"fingerprint 级微修正"，进度会最慢。

### 第 2 周（9/24 – 9/30）主项 = **Reactive / 反应型 + 动态点击**

| 轮次 | 场景组 |
| --- | --- |
| A | Air CELESTIAL No UFO Easier｜Air Pure Easier No UFO｜Air Spectral Easy 85%｜Air Angelic 4 Voltaic Easy 70% |
| B | Ground Plaza Sparky v3 Easy｜Plink Palace Easy Less Blinks｜VT Aether Bot 1 Easier｜B180T Voltaic Easy Slower |
| C | **VT Bounceshot Viscose Easier｜Popcorn MV Easier**（动态点击专项，各打 5–6 轮） |

### 第 14 天（9/30 或就近）：**全量复测**

- 39 场景各打 1 次（约 50 min），当天不打别的。
- 把复测结果给我 → 我重算诊断、换下一周期主项（**主项是轮换的，这是"一直进步"的机制**）。

### 送分池（每天从里面挑 2 个做热身，按差距从小到大）

| 优先级 | 场景（距下一档） |
| --- | --- |
| 第一梯队（≤3.5%） | voxTargetSwitch 2 Large 1.2%｜skyClick Goated 1.7%｜VT Floating Heads 1.9%｜aimerz+ Static Switching 1.9%｜ww5t 2.2%｜Pasu Voltaic Reload 2.6%｜StaticSwitchingVox 3.0%（差 3% 上 Mammoth）｜psalmTS 3.2%｜beanTS 3.8%｜eth Pasu Micro 4.0% |
| 第二梯队 | VoxTS Click 4.7%｜1w6ts reload 5.5%｜1w2ts reload 5.7%｜waldoTS 6.8%｜domiSwitch 7.2%｜CatClick 7.4%｜kinTS 8.1%｜1w3ts Pasu Perfected 11.9% |

---

## 四、练法要点（这次搜索交叉验证过的，直接照做）

1. **降速**：三个独立来源结论一致——先慢到能 100% 完成修正，速度自然回来。练主项时，**命中率不达标就再降速**。
2. **眼神先走**：打完当前目标 → **把注意力迅速移到下一个目标** → 用**余光**看准星 → 准星移过去 → 做二次修正。跟枪"跟不上"很大一部分是眼睛没提前到位。
3. **关打击音效**（Viscose 的方法）；少听歌、避免感官钝化。
4. **每次练之前先定"今天这一把是为了练什么"**。
5. **不预判刷分**："能挤出当前最好成绩，但不会养成良好的技巧"。

---

## 五、与现有体系的衔接（需要你定）

| 体系 | 现状 | 建议 |
| --- | --- | --- |
| **Viscose S2（39 场景）** | 未进追踪系统（库里只有 12 个 Voltaic 场景） | **纳入追踪**：先纳入上面"主项 13 个 + 送分池 10 个"共约 20 个，看板新增 S2 分区，画「分数 ÷ 下一档线」进度线 + rank 变动 |
| **Kovaak's Voltaic 12 场景** | 每天 3 次×7 + 每天 1 次×5（原计划） | **降级**：不再天天整套。只保留单点 4 场景的**节拍练习**（Pasu 40 / Tam 100 / Wide Wall 100 / 1w2t 110，门槛 ≥95%）；其余 8 个放到每 2 周复测日顺带打 1 轮 |
| **Aim Lab（Sixshot 等）** | 已接入 `aimlab_task` | 暂时冻结为"手感维护"，不占 1h 预算 |
| **健身（推拉蹲）** | 3 天一轮 | **练胸背/手臂的当天不打分数**（有实测反馈"练胸背或手臂很影响枪法"）；练完手酸就别硬打 |
| 时间 | 昨天：18:10–18:58 练枪 → 19:03 蹲日 | 保持"练枪在力量训练之前"这个顺序，别反过来 |

---

## 六、判据与红线

**判据（只看这两个）**
1. **命中率先动，分数后动**：跟枪场景命中率分阶段目标 40% → 50% → 60%（当前基线 13–48%）。
2. 每 2 周看两个比值：**最低分 ÷ 该子类升级线**（是否收窄）、**子类之间差距的方差**（是否变小 = 变全面）。

**红线**
- ❌ 不换灵敏度、不换外设（"越换就越感觉自己不行，陷入死循环"）
- ❌ 不因为几天没动分就否定方法（"练几天肯定没成效，你练一周再看看"；进步不是线性的）
- ❌ 不每天全量测 39 个（会吃掉整 1h）
- ❌ 不把 60% 以上时间花在自己已经强的静态点击上（滑回舒适区）
- ❌ 连续 2 周没写归因 = 已经退化成播放列表模式

---

## 七、周期检验（写下来打勾）

**每次训练后（30 秒）**
- [ ] 四段都做了（送分 / 主项 / 疲劳 / 归因）
- [ ] 主项**只攻了一个子类别**
- [ ] 今天至少有一次是"慢到不慌"完成的
- [ ] 写了 ≥1 条具体技术归因

**每 2 周**
- [ ] 全量复测 39 场景、更新表格
- [ ] 最低分子类是否收窄 / 子类差距方差是否变小
- [ ] 决定下一周期主项换成谁

**每月**
- [ ] 有没有 >60% 时间在打强项？（是 → 回舒适区了）
- [ ] 连续 2 周没写归因？（是 → 退化了）
- [ ] 灵敏度/外设动过吗？（动过 → 换回去）

---

## 八、明天（9/17）具体怎么做

```
8 min   热身送分：voxTargetSwitch 2 Large ×2 + skyClick Goated ×2
35 min  主项 A 轮：Smoothsphere ×3 / SmoothBot Perfected ×3 / Whisphere ×3
        每轮之间停 10 秒，问自己"刚才哪几发修正没跟上"，下一轮把速度压下来
7 min   今天最差的那个（预计 Smoothsphere）再打 3 轮
10 min  归因：写 2 条（最低分场景 + 它逼你改进的技术点）
```

**先不看分数。** 这一周只看一件事：跟枪场景命中率能不能从 30% 上下推到 40%+。
