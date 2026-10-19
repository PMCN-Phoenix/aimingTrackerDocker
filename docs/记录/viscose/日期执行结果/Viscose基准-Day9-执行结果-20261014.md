# Viscose 基准 · Day9 执行结果（2026-10-14 · Strafe Aiming 移动瞄准）

> **说明**：Day9 于 2026-10-14 执行，分数当时已通过 `import_day9_scores.py` 写入 InfluxDB（`list=strafe-aiming-day9`），但**未写入 `aim_daylist_meta` / `aim_daylist`**，所以 Grafana 的 Day 下拉里一直看不到它。
> 本文件于 2026-10-19 补齐：清单结构按**实际执行顺序**回填，`role` 按「前 4 项热身 / 中段主项 / 末 3 项收尾」推断（当时没有 Day9 清单 md，属事后还原，非原始计划）。
> **会话窗口**：2026-10-14 09:08 → 11:11（约 2 小时 3 分）｜**14 场景 / 55 轮**

---

## 一、逐项结果（按实际执行顺序）

| # | 场景 | 轮 | 最佳 | 末轮 | 命中率 | 角色 |
|---|---|---|---|---|---|---|
| 1 | Revolving Tracking Strafes 80% | 2 | 2460 | 2460 | 25.6% | 热身 |
| 2 | Pole Long Dodge | 2 | 19753 | 19753 | 42.9% | 热身 |
| 3 | Close FS Easy Dodge | 2 | **7973** | **6514**（−18.3%） | 28.8% | 热身 |
| 4 | Cycle Strafes Mid Varied Easy | 2 | 184 | 184 | 23.9% | 热身 |
| 5 | lgc3 Reborn Easy | 5 | **18504** | **12567**（−32.1%） | 26.8% | 主项 |
| 6 | VT PatStrafe Platinum | 5 | 2271 | 2271 | 33.0% | 主项 |
| 7 | XY Tracking Dodge | 5 | 15512 | 14612（−5.8%） | 38.2% | 主项 |
| 8 | VT AirStrafe Novice | 5 | 2543 | 2515（−1.1%） | 41.4% | 主项 |
| 9 | Pasu Track Dodge | 3 | 125954 | 125954 | 15.6% | 主项 |
| 10 | Pasu Dodge | 5 | 79710 | **66835**（−16.1%） | 19.1% | 主项 |
| 11 | VT AngleStrafe Novice | 5 | 570 | 500（−12.3%） | 58.3% | 主项 |
| 12 | PSGS 1 Shot No Mag | 4 | 146920 | 146920 | 38.5% | 收尾 |
| 13 | Bounce CT Dodge Park | 5 | 4214 | 4150（−1.5%） | 51.8% | 收尾 |
| 14 | VT ArcStrafe Novice | 5 | 490 | 490 | 50.2% | 收尾 |

---

## 二、当天特征

**1. 这是一次「Voltaic Strafe Tracking 方案」的完整落地**
前 4 项（Revolving Tracking Strafes / Pole Long Dodge / Close FS Easy Dodge / Cycle Strafes）正好对应 hotrodre_ 那套 Strafe Tracking 方案的热身段——练的是**手的独立性**（左手移动不干扰右手瞄准）。这套方案在 D 清单的感悟库里被完整记录过（《Strafe Tracking 方案中的 Air 反应训练》）。

**2. 命中率梯度暴露了难度结构**
- 高命中（>50%）：VT AngleStrafe 58.3%、Bounce CT Dodge Park 51.8%、VT ArcStrafe 50.2% → 目标大/速度慢，是"送分池"
- 低命中（<20%）：Pasu Track Dodge 15.6%、Pasu Dodge 19.1% → 远距离 dodge 类，命中率天然低（分数高但每发都难）
- 说明**不要用命中率横向比较不同场景**，只能纵向看自己的趋势

**3. 三个明显衰减点（末轮 vs 最佳）**
| 场景 | 衰减 | 解读 |
|---|---|---|
| lgc3 Reborn Easy | **−32.1%** | 5 轮里第 1 轮最高，之后持续下滑 → 典型的新鲜度衰减/疲劳 |
| Close FS Easy Dodge | −18.3% | 只有 2 轮就掉这么多，热身段就出现疲劳信号 |
| Pasu Dodge | −16.1% | 5 轮后段明显掉，与 Q016.1「晚间/长时段精度衰减」方向一致 |

**4. 时间维度**：09:08 开练、11:11 结束，**上午段**。对照 Q020 的时段分析（上午 9-13 归一化 0.991，属正常水平），这次不属于"晚间涣散"场景，衰减更可能是**单场时长过长（2 小时）+ 场景切换频繁**造成的。

---

## 三、与 Q020 的关系

Day9 是**上午场**，且时长 2 小时，正好落在 Q020 说的两个风险点上：
- 单场 >90 分钟 → 后段质量下滑（lgc3 −32%、Pasu Dodge −16% 都出现在后半段）
- 建议下次同类场景按 **「前 60 分钟主项 + 后 30 分钟收尾」** 切，或中途插入 5 分钟低负荷恢复

---

## 四、数据口径

- 分数：`kovaak_score`，`list=strafe-aiming-day9`，`_field=score`；最佳 = 当日该场景最大，末轮 = 时间上最后一次
- 命中率：`hits/(hits+misses)` 当日累计，非单轮
- 时段：InfluxDB `_time` 为 UTC，本文件已 +8h 换算为本地时间
- 清单结构：`aim_daylist` / `aim_daylist_meta` 于 2026-10-19 回填，`role` 为推断值
