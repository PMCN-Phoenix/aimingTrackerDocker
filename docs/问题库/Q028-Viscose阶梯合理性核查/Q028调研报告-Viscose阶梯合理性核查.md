# Q028 调研报告 · Viscose S2 阶梯是否合理

> 触发语："帮我找资料判断这个阶梯是否合理"（2026-10-29）
> 阶梯 = Viscose Benchmarks S2（Easier）的 9 档：Lemming → Hare → Ermine → **Puffin** → Penguin → Fox → Mammoth → Orca → Seal，以及我们在其上切的 5 块（G1→G5）
> 结论先行：**规则层合理且是官方的；数值层官方自己承认没校准；对我们路线图的含义是"可执行，但要防阈值漂移 + 先过两条有效性红线"**

---

## 一、用的资料（四个来源，三个官方）

| # | 来源 | 性质 | 本地留存 |
| --- | --- | --- | --- |
| 1 | 官方 Google Sheet「The Viscose Benches」README 区 | **官方**（作者 Viscose + pinguefy 联合出品） | `../Viscose基准-原始数据/gsheet.csv` |
| 2 | 官方追踪站 `evxl.app/benchmarks/Viscose Benchmarks S2`（含 9 档阈值表 + Global Rank Distributions） | **官方** | `../Viscose基准-原始数据/evxl-S2-Easier-charts页面.txt` |
| 3 | 《The Viscose Benchmarks, Explained》作者本人视频（115K 播放，2025-10-28） | **官方** | 简介（含作者全场景 PB 灵敏度）→ `YouTube原始数据/作者PB灵敏度.md` |
| 4 | 本地 39 场景 × 9 档阈值的量化检查 | 实测 | `_ladder_check.py`（输出见 §四） |

搜索引擎（WebSearch）对该主题返回的全是垃圾结果，Reddit 403 —— **社区评价侧存在证据缺口**，本报告主要靠官方一手资料 + 本地实测。

---

## 二、规则层：合理，且我们此前的理解全部正确

| # | 规则 | 官方原文 | 我们的用法 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | **总档 = 全部子类最低档** | "In order to get a rank, you need to get **at least one score in each subcategory**. It's hard and it takes forever to get a rank, but **I want to push people to be well rounded**." | 14 子类取 min，`calc_overall` 字段复核一致 | ✅ 官方 |
| 2 | **Puffin 是刻意插入的平滑档** | "One of the issues I tried to address with these benches is **how going between Intermediate and Advanced can feel like a huge jump**. To fix this, **I have added additional ranks in each difficulty**" | G1 = Ermine → Puffin | ✅ 官方，且**正是为"把大跳拆小"而设计的** |
| 3 | **子类档取组内最高场景** | "The number next to each scenario is your accumulated threads... **doesn't actually affect your rank**"（threads 只是进度参考） | 组内挑最易过线的场景撑杆 | ✅ 合法 |
| 4 | **每个场景有自己的阈值表** | 阈值表逐场景给出 | 跨场景比较用「档」不用「分」 | ✅ 我们一直是这么做的 |

**第 2 条是本次核查最重要的正面发现**：我们 G1 选 Puffin 当目标，不是随手挑的中间档——**作者加这一档就是为了让 Ermine→Penguin 之间有个台阶**。我们的 5 块切法（G1→Puffin / G2→Fox）与作者的设计意图同向。

---

## 三、数值层：官方自己承认没校准

**官方原话（README 第 14 行）**：

> "**Currently, the score targets are prospective.** On each difficulty, we have a link in the top right to a feedback form. **Please send your sheets and opinions so we can balance these targets!**"

——阈值是**前瞻性的（prospective）**，作者明确邀请玩家提交成绩来帮忙平衡。也就是说：**这套数值没有经过数据校准，是预设草稿，且作者保留了调整权。**

我们的实测（39 场景 × 9 档，见 §四）与这句话完全一致：

- 相邻档的中位跨度**单调递减**：20.8% → 15.8% → 11.2% → 9.7% → 10.4% → 8.7% → 7.0% → 6.5%，**最大/最小 = 3.2 倍**
- 同一个跃迁在不同场景之间从 **0.3% 到 66.7%**（Lemming→Hare 段极差 64.5pp）
- 结论：**档名是统一的，但"升一档"在物理上意味着什么，因场景而异**

**作者的自我定位（README 第 6 行）**：

> "While they are in benchmark form, **this is more of a practice playlist disguised as a benchmark**. That's why there are such a large number of scenarios and why **some categories are underrepresented**."

——它首先是一个**伪装成基准的练习清单**，其次才是测量工具；而且分类覆盖不均是有意的（这解释了为什么 14 个子类里有的只有 2 个场景）。

### 这一条与 Q025 闭环

Q025 的核心论点是"**能练 ≠ 能测 ≠ 值得测，练习分数层迁移证据≈0，Kovaak 分数只当状态闸门**"。本次核查给这个论点加上了**官方背书**：基准作者自己说这是练习清单、阈值没校准。所以：

> **"刷到 Seal"的真正价值在路上那 4–6 个月的练习量，不在 Seal 这个数字本身。** 把 Seal 当目标没有错（它提供了很好的块结构），但不要把"档位"当成对能力的精确测量——它连作者自己都只承诺到"前瞻性估计"。

---

## 四、量化检查输出（`_ladder_check.py`）

### 4.1 相邻档跨度（39 场景）

| 跃迁 | 中位 | 最小 | 最大 | 极差 |
| --- | --- | --- | --- | --- |
| Lemming → Hare | 20.8% | 2.1% | 66.7% | 64.5pp |
| Hare → Ermine | 15.8% | 1.3% | 50.0% | 48.7pp |
| Ermine → Puffin | 11.2% | 0.7% | 21.2% | 20.6pp |
| Puffin → Penguin | 9.7% | 0.4% | 17.5% | 17.1pp |
| Penguin → Fox | 10.4% | 0.5% | 21.8% | 21.3pp |
| Fox → Mammoth | 8.7% | 0.4% | 16.4% | 16.0pp |
| Mammoth → Orca | 7.0% | 0.3% | 15.4% | 15.1pp |
| Orca → Seal | 6.5% | 0.3% | 11.1% | 10.8pp |

### 4.2 累计涨幅（相对 Lemming）

| 目标档 | 累计 | 本段 |
| --- | --- | --- |
| Hare | 21% | +21pp |
| Ermine | 42% | +21pp |
| **Puffin** | **61%** | **+20pp** |
| Penguin | 77% | +16pp |
| Fox | 98% | +21pp |
| Mammoth | 117% | +19pp |
| Orca | 132% | +16pp |
| **Seal** | **143%** | **+10pp** |

前 4 档吃掉 61% 的涨幅，Puffin→Seal 再加 82pp —— **每一段都是实打实的台阶，没有"免费的档"**。

### 4.3 同子类内场景阈值的离散度（CV）

- 非常一致（3–8%）：FLICK/Speed、FLICK/Stability、REACTIVE/Control、REACTIVE/Speed
- 极度分散（79–137%）：CLICK/Precision、CLICK/Reading、CLICK/Stability、FLICK/Post-Flick、FLICK/Micro

→ 同一子类内三个场景的**绝对分数量纲差异巨大**（例如 CLICK/Reading 下既有 60 分场景也有 500 分场景）。**跨场景比较只能用档位，不能用分数**——这正是我们规则里"档位取组内最高场景"成立的另一个前提。

---

## 五、三条此前不知道的有效性红线 ⚠️

README 第 16 行（原文）：

> "Scores **slower than 50cm on fingertip scenarios are invalid**, and **103hfov is the minimum for all scenarios**."

加上分类说明的警告："These classifications **can break at certain sensitivities**"。

| # | 红线 | 对我们的影响 |
| --- | --- | --- |
| 1 | **Fingertip 场景慢于 50cm/360 无效** | 我们的 Fingertip 锚定场景是 `Air Angelic 4 Voltaic Easy 70%`（作者自己打它用 40cm）。**若你 cm/360 > 50，Fingertip 子类无效** → 总档 = 14 子类最低档，一个无效子类会卡死整条路线 |
| 2 | **103 hFOV 最低** | 需确认当前 FOV |
| 3 | **肌群分类在特定灵敏度下会失真** | 你 10-08 把灵敏度从 0.14 降到 0.09（显著变慢），Arm/Wrist/Fingertip 的分类可能已经不在作者校准的区间里 |

**行动：开 KovaaK's 确认 cm/360 与 FOV，两个数各 10 秒。** 这是当前路线图上唯一可能"一票否决"的检查项。

作者本人的参考区间：**29–61cm**（Air CELESTIAL 29 / Air Pure 35 / 点击类 46–61），没有一个场景低于 29cm。

---

## 六、数据卫生：`benches_full.json` 不是 Viscose S2 ⚠️

核查中发现 `Viscose基准-原始数据/benches_full.json` 与 `S2-官方分类诊断.json` 对不上：

| | benches_full.json | S2-官方分类诊断.json |
| --- | --- | --- |
| 档位数 | **23**（Lemming…Seal 8 + Cinnabar…Silk 15），**无 Puffin、无 Viridian** | **9**（含 Puffin） |
| 场景名 | `WhisphereRawControl Larger + Slowed`、`Smoothbot Invincible Goa…` | `Whisphere Viscose Easier`、`Smoothsphere Viscose Easier` |
| 规模 | 103 场景 / 3 难度 | 39 场景 / Easier |

两个文件**零场景重名**。benches_full.json 更像是 **Voltaic 主基准**（或其旧版本），不是 Viscose S2。而 evxl.app 的 Global Rank Distributions 里 Puffin 和 Viridian 都在——说明档名阶梯是 Voltaic/Viscose 共用的，版本间有增删。

**处理**：`benches_full.json` 打上「非 Viscose S2，禁止作为阈值来源」标记；Viscose S2 的唯一阈值来源 = `S2-官方分类诊断.json` + evxl.app 实时页面。

---

## 七、对我们路线图的最终影响

| # | 影响 | 动作 |
| --- | --- | --- |
| 1 | 5 块切法与作者意图一致（Puffin = 官方平滑档） | **路线不变** ✅ |
| 2 | 阈值是 prospective，作者会调 | 把「阈值版本」记入数据口径（与灵敏度变更同级）；**阈值下调 = G2 的 13 格可能自动过关一部分（利好），上调 = 重排**。每次跑全量重测时顺带对一次 evxl 页面 |
| 3 | Fingertip 50cm 红线 + FOV 103 红线 | **下一步打收关 v2 之前先确认这两个数** |
| 4 | 分数只当状态闸门（Q025 + 本次官方背书） | G1–G5 的真正产出是练习量本身；档位是进度条，不是能力证书 |
| 5 | 作者建议同时打两套基准（难度间 ranks 重叠） | 维护段可以混入其他基准的场景——正好符合我们「维护 4–6 轮」的压缩方向 |

## 八、待拍板 3 项

1. **cm/360 和 FOV 现在确认吗？**（10 秒的事，但会决定 Fingertip 是否有效——建议确认后再打收关 v2）
2. **阈值漂移的监控方式**：每次全量重测时顺手抓一次 evxl 页面对比？还是不做监控、接受风险？
3. **benches_full.json 的处置**：直接删除，还是加标记保留？

## 九、局限

- 社区评价侧证据缺口：WebSearch 低质、Reddit 403，**没找到任何第三方对 Viscose 阈值校准的批评或验证**——"数值是否合理"目前只有官方自己的"prospective"表态和我们的本地实测
- "overall rank = min over subcategories" 的确认来自本地文件的 `calc_overall` 字段（可能是 evxl 计算的），官方 sheet 只写了"每个子类都要有成绩"；两者高度一致但不是逐字对齐
- 作者视频正文讲的是技术分解（跟踪/反应/甩枪/动态点击），不是排名规则——排名规则的信息全部来自 README 与页面
