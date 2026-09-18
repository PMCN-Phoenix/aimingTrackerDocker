# Viscose S2 Easier · 每日训练处方（精确版）

> 数据来源：`evxl.app/u/76561199835441317/Viscose%20Benchmarks%20S2/Easier?tab=charts`（2026-09-16 抓取）
> + 2026-09-16 首轮 39 场景实测成绩与命中率
> 生成日期：2026-09-16 ｜ 本文档**取代** `Viscose基准-14天训练计划.md` 的排期部分（那版粒度太粗）

---

## 〇、先搞懂 evxl 那张表的判档规则（这决定了练什么）

我用你 39 个场景的数据反推、并逐一验证了这张表的算法：

| 规则 | 内容 | 验证 |
| --- | --- | --- |
| **子类别档位** | = 该子类别里**分数最高的那个场景**达到的档位（不看平均、不看最低） | 14/14 子类全部吻合 |
| **子类别进度 %** | = 那个场景「从当前档线到下一档线」走了多少 | 如 Precision 的 +7% = `1w3ts` 的 (758−750)/(860−750) |
| **总档位** | = **14 个子类别里最低的那一档** | 你最低两格是 Lemming → 总分就卡在 Lemming |

**这两条合起来就是全部战术**：

> 你不需要所有场景都变强。
> **你只需要在每个「卡住的子类别」里，把任意一个场景推过下一档线。**

你现在有 **14 个子类别**，其中 **12 个已经 ≥ Hare**，只有 **2 个还卡在 Lemming** —— 这就是你从 Lemming 上 Hare 的**全部障碍**。

---

## 一、诊断：你的 14 个子类别

| 子类别 | 官方分类 | 当前档位 | 撑住它的场景 | 该场景分数 | 命中率 |
| --- | --- | --- | --- | --- | --- |
| **Blending** ⛔ | CONTROL TRACKING | **Lemming** | PGTI Voltaic Easy Smoother | 696 | 13.8% |
| **Reading** ⛔ | CLICK TIMING | **Lemming** | VT Bounceshot Viscose Easier | 300 | 58.8% |
| Arm | CONTROL TRACKING | Hare | Smoothsphere Viscose Easier | 6,825 | 38.6% |
| Wrist | CONTROL TRACKING | Hare | Leapstrafes Control wobin Easier | 1,697 | 29.1% |
| Stability | CLICK TIMING | Hare | VoxTS Click Easier | 61 | 87.1% |
| Fingertip | CONTROL TRACKING | Ermine | Air Angelic 4 Voltaic Easy 70% | 3,722 | 62.7% |
| Control | REACTIVE TRACKING | Ermine | Ground Plaza Sparky v3 Easy | 835.1 | 39.4% |
| Speed | REACTIVE TRACKING | Ermine | Plink Palace Easy Less Blinks | 2,114 | 37.8% |
| Reading | REACTIVE TRACKING | Ermine | Air Pure Easier No UFO | 912.7 | 48.6% |
| Speed | FLICK TECH | Ermine | voxTargetSwitch 2 Large | 82.95 | 43.8% |
| Precision | CLICK TIMING | Puffin | 1w3ts Pasu Perfected … | 758 | 92.8% |
| Micro | FLICK TECH | Penguin | waldoTS Novice | 99.75 | 52.7% |
| Post-Flick | FLICK TECH | Penguin | kinTS Voltaic Easy 85% | 54.25 | 36.6% |
| Stability | FLICK TECH | Fox | StaticSwitchingVox | 104.8 | 59.3% |

**注意 12 个已达标子类里，有 5 个是「差 1–3% 就能再升一格」的**（Ground Plaza Sparky +1.2%、Air Pure +0.7%、voxTargetSwitch 2 +1.2%、Plink Palace +2.8%、VT Floating Heads +1.9%）——这些是后面几天的顺手分，先别动。

---

## 二、升档阶梯：从 Lemming 到 Puffin 只需要推 10 个场景

**每格只需要「组内任意一个场景过线」**，所以下面是每格最省力的那个场景：

### 目标 1：Lemming → **Hare**（今天就能到，只需 2 格）

| # | 卡口 | 要推的场景 | 现在 | 需要 | 涨幅 | 现在命中率 |
| --- | --- | --- | --- | --- | --- | --- |
| **A** | CONTROL TRACKING / Blending | **PGTI Voltaic Easy Smoother** | 696 | **700** | **+0.6%** | 13.8% |
| B | CLICK TIMING / Reading | **Pasu Voltaic Reload Easier** | 37 | **46** | **+19.6%** | 60.7% |

> 卡口 A 只差 **4 分**。你任何一次正常发挥的 PGTI 都可能直接过线。
> 备选：`Air CELESTIAL No UFO Easier` 810.81 → 817（+0.8%）

### 目标 2：Hare → **Ermine**（再补 3 格）

| # | 卡口 | 要推的场景 | 现在 | 需要 | 涨幅 | 现在命中率 |
| --- | --- | --- | --- | --- | --- | --- |
| C | CLICK TIMING / Stability | **VoxTS Click Easier** | 61 | **64** | **+4.7%** | 87.1% |
| D | CONTROL TRACKING / Arm | **SmoothBot Perfected Easier** | 2,723.5 | **3,000** | **+9.2%** | 41.3% |
| E | CONTROL TRACKING / Wrist | **Leapstrafes Control wobin Easier** | 1,697 | **2,025** | **+16.2%** | 29.1% |

### 目标 3：Ermine → **Puffin**（再补 5 格，多数几乎是白送）

| # | 卡口 | 要推的场景 | 现在 | 需要 | 涨幅 |
| --- | --- | --- | --- | --- | --- |
| F | REACTIVE / Reading | Air Pure Easier No UFO | 912.74 | 919 | **+0.7%** |
| G | REACTIVE / Control | Ground Plaza Sparky v3 Easy | 835.11 | 845 | **+1.2%** |
| H | FLICK / Speed | voxTargetSwitch 2 Large | 82.95 | 84 | **+1.2%** |
| I | REACTIVE / Speed | Plink Palace Easy Less Blinks | 2,114 | 2,175 | **+2.8%** |
| J | CONTROL TRACKING / Fingertip | Air Angelic 4 Voltaic Easy 70% | 3,722 | 3,950 | **+5.8%** |

---

## 三、Day 1 处方（明天 9/17，精确到分钟）

**今天的目标：拿下卡口 A（几乎白送）+ 开打卡口 B（真正的硬骨头）**

> 节奏基准：**1 轮 ≈ 75 秒**（60 秒挑战 + 加载/重置），轮次之间停 10–15 秒。
> 全程：**关打击音效**（用眼睛判断，不用耳朵）。

### 00:00 – 00:05｜热身（用强项把手唤醒，不追分）

| 场景 | 轮数 | 为什么 |
| --- | --- | --- |
| `1w2ts reload smallflicks larger` | ×2 | 命中率 96.2%，纯校准手感 |
| `ww5t Voltaic Slightly Larger` | ×2 | 命中率 95.7%，找回"上靶再开火"的感觉 |

要求：**不许赶速度**。这两项只是让你确认"眼睛在看哪里、准星在哪里"。

---

### 00:05 – 00:13｜卡口 A：拿掉 Blending（差 4 分，今天必须清掉）

| 场景 | 轮数 | 目标 | 现在 |
| --- | --- | --- | --- |
| `PGTI Voltaic Easy Smoother` | ×3 | **700**（过线即解锁 Hare） | 696 |
| `Air CELESTIAL No UFO Easier` | ×3 | **817**（备用过线点） | 810.81 |

⚠️ **PGTI 的命中率只有 13.8%——全清单最低之一。** 这个场景的唯一正确做法是：
**把速度降到你觉得"这也太慢了"的程度，先做到能一直贴在目标上，再想分数。**

✅ **判定**：任一场过线 → `CONTROL TRACKING / Blending` 从 Lemming 升 **Hare**，往 evxl 刷新页面就能看到。

---

### 00:13 – 00:43｜主项：CLICK TIMING / Reading（今天真正的主攻）

这三个场景**全是移动靶点击**，也是你命中率 54–61% 的地方。分数 = 命中次数，所以提分 = 提命中率。

| 场景 | 轮数 | 现在分数 | 目标分数 | 现在命中率 | **要求命中率** |
| --- | --- | --- | --- | --- | --- |
| `Pasu Voltaic Reload Easier` | ×7 | 37 | **46** | 60.7% | **≥75%** |
| `VT Bounceshot Viscose Easier` | ×7 | 300 | **380** | 58.8% | **≥75%** |
| `CatClick Easier` | ×6 | 25 | **35** | 54.3% | **≥75%** |

**为什么统一是 75%？** 因为在你现在的出手次数下，只要命中率到 75%，分数就正好过线：

- Pasu：37 ÷ 0.607 = 61 次出手 → 46 ÷ 61 = **75.4%**
- Bounceshot：300 ÷ 0.588 = 510 次出手 → 380 ÷ 510 = **74.5%**
- CatClick：25 ÷ 0.543 = 46 次出手 → 35 ÷ 46 = **76.0%**

**唯一规则**（这是 Viscose 的原话，不是提速，是提确定性）：

> 每一发都必须**确认准星已经在目标上**再开火。
> 命中率没到 75% → **把节奏再压一档**，不是加快。

**自检句**（每轮结束后问自己）：*"我刚才是在平滑地贴上目标，还是猛地甩过去再修？"* → 如果是后者，下一轮继续降速。

---

### 00:43 – 00:50｜疲劳巩固

今天**命中率最低**的那个场景（预计是 `CatClick` 或 `VT Bounceshot`）再打 **×3**。
目的：练"累了也稳"——比赛不会在你状态最好的时候来。

### 00:50 – 00:58｜归因（写在纸上或备忘录，不能省）

1. 今天最低分 / 最低命中率的场景是？
2. 我是在**平滑贴住**，还是**猛甩再修**？
3. 明天要改的**一个具体动作**是：______

### 00:58 – 01:00｜刷新 evxl 看两件事

- `CONTROL TRACKING / Blending` 是否变 Hare？
- `CLICK TIMING / Reading` 那三个数字涨了多少？（**只盯命中率，不盯分数**）

**今天的成功标准只有一条**：三个移动靶场景的命中率有没有从 55–60% 推到 70%+。分数会滞后，别慌。

---

## 四、Day 2 – Day 7 处方（按卡口推进，清了就往下走）

**每天固定骨架**：热身 5min → 卡口主攻 30min → 卡口次攻 12min → 疲劳巩固 5min → 归因 5min（≈57min）

| 日期 | 热身（各 ×2） | **主攻 30min** | 次攻 12min | 疲劳巩固 ×3 |
| --- | --- | --- | --- | --- |
| **D1 9/17** | 1w2ts / ww5t | **卡口 B**：Pasu ×7、Bounceshot ×7、CatClick ×6（命中率目标 75%） | **卡口 A**：PGTI ×3、Air CELESTIAL ×3 | 今日命中率最低的场景 |
| **D2 9/18** | VoxTS Click / skyClick | **卡口 B 复攻**：Pasu ×8、Bounceshot ×8、CatClick ×6 | **卡口 C**：VoxTS Click ×5（61→64） | 同上 |
| **D3 9/19** | VoxTS Click / VT Floating Heads | **卡口 B 若未清 → 继续；已清 → 卡口 D**：SmoothBot Perfected ×7（→3000）、Smoothsphere ×5（→8050） | **卡口 C**：VT Floating Heads ×5（490.47→580） | 同上 |
| **D4 9/20** | 1w6ts reload / beanTS | **卡口 D**：SmoothBot Perfected ×7、Whisphere ×6（9000→10300） | **卡口 E**：Leapstrafes ×5（1697→2025） | 同上 |
| **D5 9/21** | voxTargetSwitch 2 / aimerz+ | **卡口 E**：Leapstrafes ×8、Controlsphere SuperbAim ×6（4533→6200） | **顺手分**：voxTargetSwitch 2 ×4（82.95→84）、Ground Plaza Sparky ×4（835.11→845） | 同上 |
| **D6 9/22** | 1w2ts / ww5t | **深层短板（fingertip 50cm）**：Flower Easier 50cm ×7（968→1050）、cloverRawControl 50cm ×7（2928→5000） | **顺手分**：Air Pure ×4（912.74→919）、Plink Palace ×4（2114→2175） | 同上 |
| **D7 9/23** | 1w6ts / skyClick | **卡口复测**：把 A–J 十个卡口场景各打 ×2，看还有哪些没清 | 今天最差的那个 ×5 | 同上 |

**卡口推进原则**：一格清了就**不再花时间**（子类别档位由最高分场景决定，其他场景掉分不影响）。
**唯一例外**：`CLICK TIMING / Reading` 是唯一需要「真练」而不是「顺手一推」的卡口——它值得整个 D1–D3 的主攻时间。

---

## 五、深层短板（长期，但不占卡口时间）

这两项差得远，**不是这周的卡口**，但决定了你后面能不能走远：

| 场景 | 现在 | Lemming 线 | 差 | 命中率 |
| --- | --- | --- | --- | --- |
| `cloverRawControl Viscose Easier 50cm` | 2,928 | 5,000 | **+41.4%** | 16.5% |
| `Flower Easier 50cm` | 968 | 1,050 | **+7.8%** | 16.5% |

两个都是 **fingertip + 50cm 标记**场景。你的 cm/360 ≈ 29.2cm，**比 50cm 门槛快**，所以分数有效、不存在设置问题——纯技术。
`Flower` 只要 82 分就上榜，D6 打一次大概率就有了；`cloverRawControl` 是全场最难的，当长跑。

---

## 六、每天必须记的三个数（30 秒）

```
日期 / 主攻场景 / 命中率 / 分数 / 自评（这次是"平滑贴上"还是"猛甩再修"）
```

- **只看命中率，不看分数**：分数滞后，命中率先动（跟枪类终极目标 40% → 50% → 60%）
- **不管别的场景掉没掉分**：子类别档位只看最高分场景，掉分不影响 rank
- **不换灵敏度、不换外设**（"越换就越感觉自己不行，陷入死循环"）

**红线**
- ❌ 连续 2 天没写归因 → 已经退化成"播放列表模式"，不是在训练
- ❌ 每天 39 个全量测 → 吃掉整 1h，还看不出趋势（只在每 2 周做一次）
- ❌ 为了过线去"预判刷分" → 能挤分但会固化坏技术

---

## 附：39 场景完整处方表（含命中率与还差多少）

| 子类别 | 官方分类 | 该子类档位 | 撑住它的场景 | 分数 | 命中率 | 下一档线 | 还差 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Blending | CONTROL TRACKING | **Lemming ⛔** | **PGTI Voltaic Easy Smoother ★** | 696.00 | 13.8% | 700 | +0.6% |
|  |  | Lemming | Air CELESTIAL No UFO Easier | 810.81 | 37.0% | 817 | +0.8% |
|  |  | Unranked | RawControlSphere Easier | 4,560.00 | 25.7% | 4,700 | +3.0% |
| Reading | CLICK TIMING | **Lemming ⛔** | **VT Bounceshot Viscose Easier ★** | 300.00 | 58.8% | 380 | +21.1% |
|  |  | Unranked | Pasu Voltaic Reload Easier | 37.00 | 60.7% | 46 | +19.6% |
|  |  | Unranked | CatClick Easier | 25.00 | 54.3% | 35 | +28.6% |
| Arm | CONTROL TRACKING | Hare | Smoothsphere Viscose Easier ★ | 6,825.00 | 38.6% | 8,050 | +15.2% |
|  |  | Hare | SmoothBot Perfected Easier | 2,723.49 | 41.3% | 3,000 | +9.2% |
|  |  | Lemming | Whisphere Viscose Easier | 9,000.00 | 30.5% | 9,400 | +4.3% |
| Wrist | CONTROL TRACKING | Hare | Leapstrafes Control wobin Easier ★ | 1,697.00 | 29.1% | 2,025 | +16.2% |
|  |  | Lemming | Controlsphere SuperbAim Viscose Easier | 4,533.00 | 25.8% | 5,100 | +11.1% |
|  |  | Lemming | VT Controlsphere Viscose Easier | 1,388.00 | 23.5% | 1,600 | +13.2% |
| Stability | CLICK TIMING | Hare | VoxTS Click Easier ★ | 61.00 | 87.1% | 64 | +4.7% |
|  |  | Lemming | VT Floating Heads Viscose Easier | 490.47 | 76.7% | 500 | +1.9% |
|  |  | Unranked | psalmTS Viscose Click Easier | 30.00 | 51.7% | 31 | +3.2% |
| Fingertip | CONTROL TRACKING | Ermine | Air Angelic 4 Voltaic Easy 70% | 3,722.00 | 62.7% | 3,950 | +5.8% |
|  |  | Unranked | cloverRawControl Viscose Easier 50cm | 2,928.00 | 16.5% | 5,000 | +41.4% |
|  |  | Unranked | Flower Easier 50cm | 968.00 | 16.5% | 1,050 | +7.8% |
| Control | REACTIVE TRACKING | Ermine | Ground Plaza Sparky v3 Easy | 835.11 | 39.4% | 845 | +1.2% |
|  |  | Hare | Air Spectral Easy 85% | 902.26 | 53.6% | 907 | +0.5% |
| Speed | REACTIVE TRACKING | Ermine | Plink Palace Easy Less Blinks | 2,114.00 | 37.8% | 2,175 | +2.8% |
|  |  | Lemming | VT Aether Bot 1 Easier | 1,572.00 | 27.6% | 1,600 | +1.8% |
| Reading | REACTIVE TRACKING | Ermine | Air Pure Easier No UFO | 912.74 | 48.6% | 919 | +0.7% |
|  |  | Hare | Air Voltaic Invincible 4 Easier | 2,668.00 | 44.9% | 2,800 | +4.7% |
| Speed | FLICK TECH | Ermine | voxTargetSwitch 2 Large | 82.95 | 43.8% | 84 | +1.2% |
|  |  | Ermine | aimerz+ Static Switching 6 Bot … | 101.00 | 42.0% | 103 | +1.9% |
|  |  | Hare | ww5t Voltaic Slightly Larger | 90.00 | 95.7% | 92 | +2.2% |
| Precision | CLICK TIMING | Puffin | 1w3ts Pasu Perfected Micro Goated … | 758.00 | 92.8% | 860 | +11.9% |
|  |  | Lemming | Popcorn MV Easier | 120.00 | 29.3% | 150 | +20.0% |
|  |  | Unranked | skyClick Goated Easier | 59.00 | 78.7% | 60 | +1.7% |
| Micro | FLICK TECH | Penguin | waldoTS Novice | 99.75 | 52.7% | 107 | +6.8% |
|  |  | Puffin | 1w2ts reload smallflicks larger | 100.00 | 96.2% | 106 | +5.7% |
|  |  | Hare | eth Pasu Micro Easier | 744.00 | 85.6% | 775 | +4.0% |
| Post-Flick | FLICK TECH | Penguin | kinTS Voltaic Easy 85% | 54.25 | 36.6% | 59 | +8.1% |
|  |  | Puffin | domiSwitch Easier | 5,009.60 | 44.0% | 5,400 | +7.2% |
|  |  | Hare | B180T Voltaic Easy Slower | 40.40 | 22.8% | 42 | +3.8% |
| Stability | FLICK TECH | Fox | StaticSwitchingVox | 104.80 | 59.3% | 108 | +3.0% |
|  |  | Penguin | beanTS Larger | 102.00 | 56.8% | 106 | +3.8% |
|  |  | Puffin | 1w6ts reload v2 20% bigger | 86.00 | 96.6% | 91 | +5.5% |

> 「下一档线」= 该场景**自己下一档**所需的分数（不是子类别目标）。
> ⛔ = 卡住总分档位的子类别 ｜ ★ = 该子类别当前的"撑杆"场景

---

## 七、与你现有体系怎么共存

| 体系 | 处理 |
| --- | --- |
| **Viscose S2（本文档）** | **主课，占满 1h**，按上面卡口阶梯走 |
| Kovaak's Voltaic 12 场景 | 降为**维护**：只保留单点 4 场景的节拍练习（Pasu 40 / Tam 100 / Wide Wall 100 / 1w2t 110，命中率门槛 ≥95%），其余放每 2 周复测日 |
| Aim Lab | 冻结（手感维护），不占 1h |
| 健身（推拉蹲） | **练胸背/手臂当天不打分数**；依旧保持"练枪在力量训练之前" |
