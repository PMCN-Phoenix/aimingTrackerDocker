# 交接单 · 为「铎克」制作 Viscose S2 练习清单（Day4）

> 本文件是给**另一个 AI/Agent** 的任务交接说明。读这一份 + 下面 §1 列的文件，就能独立完成。
> 生成：2026-09-20

---

## 0. 你要产出什么

给一位玩家（Kovaak's ID「铎克」，Steam `76561199835441317`）做一份 **Day4 每日练习清单**，交付两份东西：

1. **Markdown 清单** —— 可打勾的打印版（格式约束见 §4.1）
2. **`playlist.json`** —— 可直接被 Kovaak's 读取的播放列表（格式约束见 §4.2），并**写入游戏目录**

核心要求一句话：**主项必须是"他最弱子类里、他从来没认真练过的场景"，不是"最容易升档的场景"。** 详见 §3。

---

## 1. 必读文件（按优先级）

所有路径的根都是 `D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\`

| # | 文件 | 作用 | 重点读哪部分 |
| --- | --- | --- | --- |
| ★1 | `清单\viscose训练推进建议\Viscose基准-场景能力映射与清单有效性.md` | **最重要**。39 个场景逐个「练什么」+ 有效性判断标准 + 排布方法论 + 对已有清单的诊断 | §1.2（39 场景表）、§2（检验标准）、§3（排布规则）、§4（诊断）、§7（改法） |
| ★2 | `记录\viscose\日期执行结果\Viscose基准-Day2-执行结果.md` | 最近一次实测的完整结果 + 三个卡口现在差多少 | §二（档线更正）、§五、§九（加量分配） |
| 3 | `记录\viscose\日期执行结果\Viscose基准-Day1-执行结果.md` | 前一次实测 | §三 逐项结果、§六 下一步 |
| 4 | `清单\viscose训练提升清单日期推进\Viscose基准-Day3-游玩清单.md` | **上一版清单，格式参照 + 现状基线** | 整份（尤其文首的目标线更正块） |
| 5 | `清单\viscose训练推进建议\Viscose基准-平滑跟枪与变向专项.md` | 跟枪动作要点（三段式、变向不停枪、握力紧松紧） | §1、§5、§6 |
| 6 | `清单\viscose训练推进建议\Viscose基准-每日训练处方.md` | 判档机制 + 14 子类诊断 + 完整处方表 | §〇（判档规则）、§一、§附（39 场景表） |
| 7 | `清单\viscose训练推进建议\Viscose基准-训练状态与长期结构.md` | 三层训练结构、轮换周期 | §二、§三、§九 |
| 8 | `清单\viscose训练推进建议\Viscose基准-低分提升指南.md` | 逐类别攻略 + 社区实证 | §二 |
| 9 | `清单\Viscose基准-原始数据\S2-官方分类诊断.json` | 39 场景的结构化数据（主类/子类/分数/9 档达标线） | 全部，用于算目标线 |

---

## 2. 当前状态（不用重新查，直接用）

### 2.1 玩家参数

| 项 | 值 |
| --- | --- |
| 灵敏度 | DPI 3200 × sens 0.14 = eDPI 448 → **cm/360 ≈ 29.2cm** |
| FOV | **103**（Viscose 硬性要求 ≥103，满足） |
| 每天可投入 | **1 小时** |
| 目标 | **纯追 rank**（不是"提升瓦的段位"） |
| 灵敏度肌群档位 | 26–31cm = "手腕主导大半、手臂辅助小半" |

### 2.2 benchmark 概况

| 项 | 值 |
| --- | --- |
| 清单 | **Viscose Benchmarks S2 · Easier**（39 场景，4 主类 / 14 子类） |
| 9 档阶梯 | Lemming → Hare → Ermine → Puffin → Penguin → Fox → Mammoth → Orca → Seal |
| **总档位** | **Hare**（14 子类里最低那档） |
| 已上榜 | 34 / 39（5 个未上榜见 §2.4） |

### 2.3 三个卡口 + 现在的距离（★ 全部按"子类的 Ermine 线"算）

| 子类 | 撑杆场景 | 现在 | **要打到** | 差距 | 备注 |
| --- | --- | --- | --- | --- | --- |
| **Wrist** | `Controlsphere SuperbAim Viscose Easier` | 6,126 | **6,200** | **1.2%** | 最便宜 |
| **Blending** | `Air CELESTIAL No UFO Easier` | 836.1 | **842** | **0.7%** | 数值最小，但要破历史最佳；**1 轮约 3 分钟，很贵** |
| **Blending**（备选） | `RawControlSphere Easier` | 4,560 | **4,700** | 3.0% | 只摸底过一次，空间大 |
| **Arm** | `SmoothBot Perfected Easier` | 2,723.5 | **3,000** | **10.2%** | **Arm 里最便宜的一条** |
| Arm（备选） | `Smoothsphere Viscose Easier` | 6,825 | 8,050 | 17.9% | 从没认真打过 |
| Arm（备选） | `Whisphere Viscose Easier` | 9,000 | 10,300 | 14.4% | ⚠️ **不是 9,400**，9,400 只是它的 Hare 线 |
| Wrist（备选） | `Leapstrafes Control wobin Easier` | 1,697 | 2,025 | 19.3% | 变向占比高 |
| Wrist（备选） | `VT Controlsphere Viscose Easier` | 1,388 | 1,600 | 15.3% | 从没认真打过 |

### 2.4 长期最弱项（★ 本次要重点解决）

以下场景从 2026-09-16 摸底后**一次都没有认真练过**（清单主项从没选过它们）：

| 场景 | 子类 | 现在 | 下一档线 | 差距 | 命中率 |
| --- | --- | --- | --- | --- | --- |
| `cloverRawControl Viscose Easier 50cm` | CONTROL·Fingertip | 2,928 | 5,000 | **41.4%** | **16.5%** |
| `Popcorn MV Easier` | CLICK·Precision | 120 | 150 | **20.0%** | 29.3% |
| `VT Controlsphere Viscose Easier` | CONTROL·Wrist | 1,388 | 1,600 | 15.3% | 23.5% |
| `Flower Easier 50cm` | CONTROL·Fingertip | 968 | 1,050 | 7.8% | 16.5% |
| `skyClick Goated Easier` | CLICK·Stability | 59 | 60 | 1.7% | 78.7%（**未上榜**） |
| `psalmTS Viscose Click Easier` | CLICK·Stability | 30 | 31 | 3.2% | 51.7%（**未上榜**） |

> **证据支撑**：`Controlsphere SuperbAim` 在 9/16 摸底只有 4,533，9/20 被认真打了 8 轮 → **6,126（+35%）**。
> **结论：摸底分 ≈ 真实水平的下限。"从没练过"的场景，进步空间最大。**

### 2.5 一条必须用上的实测规律

**两个跟枪场景都是"前 5 轮白给、后段才出成绩"**（9/20 实测）：

| 场景 | 前段均值 | 后段均值 | 变化 |
| --- | --- | --- | --- |
| Whisphere | 6,947（命中率 23.5%） | 8,107（27.4%） | **+16.7%** |
| Controlsphere | 4,980（28.3%） | 5,817（32.7%） | **+16.8%** |
| Air CELESTIAL | 819.9 | 823.7 | +0.5% |
| Pasu | 38.8 | 42.5 | +9.7% |

→ **给跟枪场景的轮数不能少（≥6），且前 1/3 轮要明确标成"校准段（刻意慢速、不看分）"。**

---

## 3. ★ 选场景的三条硬规则（本次核心，务必遵守）

### 规则 1：主项 = "最弱子类里、没认真练过的场景"

**不要再用"哪一格差得最少就打哪个"来选主项。** 这是为**升档**优化的排法，不是为**能力**优化。
（上一版清单就是这么排的，结果：Arm 子类反而退步 9,000 → 8,810，而 §2.4 的最弱项一次没碰。）

### 规则 2：每天固定留 4 轮给"长期最弱项"

从 §2.4 里挑**一个**（建议轮流：`cloverRawControl` → `Popcorn` → `Flower`），
**不追分、不看分数，只练动作**。否则它们会被"更划算的"永远挤掉。

### 规则 3：便宜的那条线降级为"收尾验收"

放在清单**最后 3–4 轮**，作用是**确认这个子类通了没有**，不是**用它来练这个子类**。

### 附带：目标线的取法（★ 上一版在这里出过错）

> **必须取「你想升到的那个档的子类线」，不能取「这个场景自己当前档位的下一档线」。**

自检句式：**"如果这个场景打到我给它定的目标线，哪一个子类会升档？"**
答不上来 / 答案是"都不升" → 目标线取错了。

---

## 4. 输出格式约束（不遵守会破坏下游系统）

### 4.1 Markdown 清单

文件放 `docs\清单\viscose训练提升清单日期推进\Viscose基准-Day4-游玩清单.md`

下游脚本 `aim-tracker-docker\daylist_sync.py` 会**解析这份 md** 并写进 Grafana 看板，所以格式有硬约束：

| 约束 | 说明 |
| --- | --- |
| 首行 | 必须是 `# Viscose Day4 · 本地游玩清单（9/22）` —— **括号里的 `M/D` 会被当作执行日** |
| **只有主清单表**的首列可以是数字 | 其余任何表格的首列**必须是文字**，否则会被误当成清单条目 |
| 主清单表每行 | `\| 序号 \| \`场景名\` \| ×轮数 \| 角色/目标描述 \| ☐ \|` —— 场景名必须用**反引号**包住 |
| 角色关键词 | **只能用「热身 / 卡口 / 主项 / 巩固」四个**（按此顺序匹配，一行里别混用两个） |
| 目标分写法 | `目标 **6200**`（这样才能被解析） |
| 命中率门槛写法 | `命中率 ≥33%`（"命中率 96%"这种纯描述**不算**门槛） |
| 自检 | 写完先跑 `python daylist_sync.py --list`（dry-run），确认条数/轮数/角色/目标都解析正确，再正式跑 |

### 4.2 playlist.json（Kovaak's 可读）

**格式参考现成文件**：`docs\清单\viscose训练提升清单日期推进\Viscose基准-Day3游玩清单.playlist.json`

| 约束 | 说明 |
| --- | --- |
| 编码 | **UTF-8（无 BOM）+ tab 缩进 + 结尾换行**（游戏自写的格式就是这样；注意旧导入文件可能是 UTF-16，**别猜，看参考文件**） |
| 顶层字段 | `playlistName / playlistId / authorSteamId / authorName / scenarioList / description / hasOfflineScenarios / hasEdited / shareCode / version / updated / isPrivate` |
| scenarioList | `[{"scenario_name": "…", "play_Count": N}, …]` —— **场景名大小写敏感，必须与游戏内完全一致** |
| 写入前 | **必须确认 Kovaak's 已关闭**，否则游戏会覆盖你的写入 |
| 写入位置 | `D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists\Viscose Day4 - <名字>.json` |
| 备份 | 同时在项目内留一份 `Viscose基准-Day4游玩清单.playlist.json` |
| 写完回读校验 | 用 `json.loads` 读回来，逐条比对场景名是否与 `Playlists\Viscose Benchmark S2 - Easier.json` 里的一致 |

**场景名可从这取**（权威来源）：`...\Saved\SaveGames\Playlists\Viscose Benchmark S2 - Easier.json`

---

## 5. 禁止事项

- ❌ 不要改灵敏度 / FOV / 外设（29.2cm、FOV 103 都合格，来回换会陷入死循环）
- ❌ 不要为过线设计"预判刷分"（Viscose 点名：能挤出当前最佳分，但**不会养成好技术**）
- ❌ 不要把主项继续设成"最便宜的那格"
- ❌ 不要只给跟枪场景 3–4 轮（实测它们需要 ≥6 轮才出成绩）
- ❌ 不要用「场景自己的下一档线」当目标（见 §3 附带）
- ❌ 不要动 `PlaylistOrder.json` / `LocalFavoritePlaylists.json`

---

## 6. 交付物清单

| 产出 | 位置 |
| --- | --- |
| Day4 清单 md | `…\docs\清单\viscose训练提升清单日期推进\Viscose基准-Day4-游玩清单.md` |
| playlist 备份 | `…\docs\清单\viscose训练提升清单日期推进\Viscose基准-Day4游玩清单.playlist.json` |
| 游戏内 playlist | `D:\1_game\1_steam\…\FPSAimTrainer\Saved\SaveGames\Playlists\Viscose Day4 - <名字>.json` |
| 看板同步（可选，需 Docker） | 跑 `python daylist_sync.py` → `python build_dashboard.py`（在 `aim-tracker-docker\` 下） |

**时间预算参考**：1 小时 ≈ **32–38 轮**（点击类约 50–65 秒/轮；跟枪类约 90–100 秒/轮；**`Air CELESTIAL` 约 180 秒/轮**，特别贵）

---

## 7. 环境备注（如果是同一个 Agent 环境）

- Python 用全路径：`D:\6_code\13_python\1_python3.11.0\python.exe`（PATH 里的 `python` 可能是 WindowsApps 占位符，会静默失败）
- 查成绩：`https://evxl.app/u/76561199835441317/Viscose%20Benchmarks%20S2/Easier?tab=charts`
- 本地库（可选）：InfluxDB `http://127.0.0.1:8087`，org `aim-org`，bucket `aim`，token `aim-super-secret-token-2026`，measurement `aim_scenario`（tag `list=viscose-s2-easier`）、`aim_bench_row` / `aim_bench_meta`（已物化档位）
- 原始逐杀记录：`D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats\*.csv`（汇总行里有 `Score:` / `Hit Count:` / `Miss Count:` / `Total Overshots:`）
