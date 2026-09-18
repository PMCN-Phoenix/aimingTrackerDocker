# Viscose Benches 从零上手 · 超细操作手册

> 针对你这台机器实测撰写（2026-09-16）。所有 Sharecode、Steam ID、路径都已核对过，可直接照抄。

---

## 〇、开始前必读：现在有三个版本，别装错

我在 evxl.app 上实测确认，Viscose 的 benchmark 已经更新过，现在同时存在三套：

| 版本 | 档位 | Sharecode | 状态 |
| --- | --- | --- | --- |
| **Viscose Entry Benchmarks** | Entry | `KovaaKsDinkingVibrantInfiltration` | 入门版 |
| **Viscose Benchmarks S2** ⭐ | Easier / Medium / Hard / Expert | 见下表 | **当前主推（推荐）** |
| Viscose Benchmarks（旧版） | Easier / Medium / Hard | 见下表 | 已归档到 Legacy，**更难** |

**S2 各档 Sharecode**：

| 档位 | Sharecode |
| --- | --- |
| Easier | `KovaaKsScreamingPulledEgg` |
| Medium | `KovaaKsPeakingNarrowImpact` |
| Hard | `KovaaKsPlunderingOlivegreenClutch` |
| Expert | `KovaaKsRaidingPeriwinkleWindow` |

**旧版各档 Sharecode**（就是你之前那份 Google 表格对应的版本，想练更难的用这套）：

| 档位 | Sharecode |
| --- | --- |
| Easier | `KovaaKsGearingMehLowground` |
| Medium | `KovaaKsVibratingFlankedLurker` |
| Hard | `KovaaksTrollingFedCallout` |

**怎么选**：从 **S2 的 Easier** 开始。旧版留作以后"加难"用（评论区原话："新的简单老的难，老的多磨一磨"）。

**S2 的 rank 阶梯（9 级）**：
`Lemming → Hare → Ermine → Puffin → Penguin → Fox → Mammoth → Orca → Seal`

> 注意 S2 比旧版**多了一个 Puffin**，所以两版的分数字段不能直接对比。

---

## 一、你的现状（我已经核对过了）

| 项目 | 值 | 结论 |
| --- | --- | --- |
| Kovaak's 安装路径 | `D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer` | ✅ 已就绪 |
| Steam ID64 | `76561199835441317` | ✅ 下面要用 |
| Steam 昵称 | 铎克 | ✅ evxl.app 已能识别 |
| **FOV** | **103** | ✅ **正好满足 Viscose 的「≥103 hfov」硬性要求** |
| DPI | 400 | — |
| 灵敏度 | XSens = YSens = 0.14（Valorant 刻度） | ⚠️ 见下方说明 |
| 当前 playlist | Voltaic Fundamentals - Iron（12 场景） | 你的旧体系，保留 |
| 成绩页 | `https://evxl.app/u/76561199835441317` | ✅ 已能打开 |

### ⚠️ 灵敏度需要你确认一件事

Viscose 表格的硬性要求是：**fingertip 类场景，灵敏度慢于 50cm（cm/360）的分数无效**。

我在 S2 的场景名里看到直接带 `50cm` 标记的场景（如 `cloverRawControl Viscose Easier 50cm`、`Flower Easier 50cm`）——作者是直接把灵敏度门槛写进场景名了。

**你需要做的**：打开 Kovaak's → Settings → 灵敏度那一栏，看界面显示的 **cm/360** 数值。

- **≥ 50cm** → 不用动任何设置，直接开练 ✅
- **< 50cm**（也就是比 50cm 更灵敏）→ 那些带 `50cm` 标记的 fingertip 场景对你无效，要么调低灵敏度，要么跳过这类场景

---

## 二、第 1 步：打开你的成绩页（约 3 分钟）

这一步不用登录，不用注册（evxl.app 明确写了 "No Login Required"）。

1. 浏览器打开：**`https://evxl.app/`**
2. 页面正中有一个输入框，提示文字是 `Enter a Steam ID, Vanity ID, or Profile URL`（或按快捷键 `Ctrl + K` 直接聚焦）
3. 在框里粘贴**这一整串**（用完整链接最稳，实测直接填数字会被当成 vanity ID 报错）：
   ```
   https://steamcommunity.com/profiles/76561199835441317
   ```
4. 点右边的 **Search** 按钮
5. 页面会跳到 **`https://evxl.app/u/76561199835441317`**，顶部显示你的昵称「铎克」

**建议直接收藏这个地址**，以后每次复测都从这里进：
```
https://evxl.app/u/76561199835441317
```

> 如果访问不了：这个站在国内需要梯子（评论区有人专门为这个做了网盘备份）。

**记一下这个地址，它是你的"总面板"**：
```
https://evxl.app/u/76561199835441317
```

---

## 三、第 2 步：把 Viscose 场景装进 Kovaak's（约 5 分钟）

### 路线 A（推荐）：用 Sharecode 导入

1. **完全关闭 Kovaak's**（不是最小化，是退出进程）
2. 打开 Steam → 库 → 启动 Kovaak's
3. 进入主界面后，找到 **Playlist / 播放列表** 相关入口
   - 一般在主菜单里有 `Playlists` 或 `Import` 之类的按钮
4. 选择 **Import by Sharecode / 按分享码导入**
5. 粘贴这一串（**先只导这个**，别一次导 4 个）：
   ```
   KovaaKsScreamingPulledEgg
   ```
6. 确认导入 → 列表里会出现一个新的 playlist：**Viscose Benchmarks S2 · Easier**
7. 打开它，应该能看到约 **30 个场景**（第一屏是 CONTROL TRACKING / ARM 下的 Smoothsphere、Whisphere、SmoothBot 等）

### 其余档位（等你主档跑通了再导）

| 想导入 | 粘贴这个 |
| --- | --- |
| S2 · Medium | `KovaaKsPeakingNarrowImpact` |
| S2 · Hard | `KovaaKsPlunderingOlivegreenClutch` |
| S2 · Expert | `KovaaKsRaidingPeriwinkleWindow` |
| Entry 入门版 | `KovaaKsDinkingVibrantInfiltration` |
| 旧版 Easier | `KovaaKsGearingMehLowground` |
| 旧版 Medium | `KovaaKsVibratingFlankedLurker` |
| 旧版 Hard | `KovaaksTrollingFedCallout` |

### 路线 B（备用）：我直接帮你生成本地文件

你的 Kovaak's 的 playlist 就是本地 JSON 文件，存放在：
```
D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists\
```
里面现在已经有一个 `Voltaic Fundamentals - Iron.json`（UTF-16 编码）。

如果 Sharecode 导入失败，告诉我一声，我可以直接把三个档位的 playlist 文件写好丢进这个目录，你启动游戏就能看到。**前提是操作时游戏必须是关闭状态**。

### 导入后怎么确认成功

- 在 Kovaak's 的 playlist 列表里能看到名字
- 点开后有 30 个左右的场景
- **第一次打某个场景时，Kovaak's 会自动从创意工坊下载该场景**，可能要等几秒到几十秒，属正常现象

---

## 四、第 3 步：建立你的记分表（约 10 分钟）

### 为什么必须用 Google Sheets，不能用 Excel

我已经把官方表格导出成本地 xlsx 检查过了，里面用了 **Google Sheets 专有函数**：

- `IMPORTRANGE(...)`（跨表导入）
- `sparkline(...)`（迷你走势图）

在 Excel 里这些会变成无效函数（`__xludf.DUMMYFUNCTION`），**这就是评论区那哥们说"填了分数不出现进度条"的原因**。所以：

> **记分必须用 Google Sheets 网页版**，本地 Excel 只能当"看数字"的参考。

### 操作步骤

1. 打开官方表格（需梯子）：
   ```
   https://docs.google.com/spreadsheets/d/1bFAlt6g_Gm8P9RBkcAoObpbIGFwVS5gXIdIK9B_YyZE/edit
   ```
2. 左上角菜单 **File（文件） → Make a copy（建立副本）**
3. 选择保存到 **My Drive（我的云端硬盘）** → 确定
4. 会自动打开你的副本，标题类似 "Copy of The Viscose Benches"
5. **重命名一下**（点标题改名），比如 `Viscose S2 训练记分 - 铎克`
6. ⚠️ **不要在副本里动了模板结构**，只往 `SCORE` 那一列填数字

### 如果表格打不开（没有梯子）

评论区有人给了网盘备份：`https://pan.quark.cn/s/07ade15bedf9?pwd=7gFi`（提取码 `7gFi`）

⚠️ 但注意：从网盘拿到的大概率是 xlsx 文件，**它的公式在本地不工作**。可以拿它看场上名称和达标线，但记分还是想办法用 Google Sheets。

### 如果你实在用不了 Google Sheets

告诉我，我可以给你做一个**本地的简易记分表**（HTML 或 Excel），只保留核心功能：
- 每个场景当前分数
- 自动对比达标线、算出当前 rank
- 自动标出**最弱子类别**

功能会比官方表格少（没有 sparkline 走势图和跨表联动），但足够你按方法练。要的话说一声。

---

## 五、第 4 步：第一次摸底（约 60–90 分钟）

**目的**：拿到你的初始数据 —— 你现在什么水平、哪个子类别最弱。

### 具体做法

1. 打开 Kovaak's 里的 **Viscose Benchmarks S2 · Easier**
2. **从第一个场景开始，一个一个往下打**
3. **每个场景只打 1–3 遍**，不要追分、不要反复重来
   - 第一遍不熟，第二遍差不多，第三遍收手
   - 目标是"有个能填进表格的数字"，**不是刷好成绩**
4. 打完一个，**立刻把 SCORE 抄到 Google 表格对应那一行**
5. 全部打完后，记下两个数字：
   - **你当前能稳定拿到哪一级 rank**（对比 Lemming→Seal 那 9 列）
   - **哪几个子类别相对最低**（Arm / Wrist / Fingertip / Blending，以及技术类）

### 第一次会遇到的正常现象

- **跟枪类（Control Tracking / Reactive Tracking）会非常难受** —— 评论区几乎所有人头几天都在说这个（"day1，跟枪要老命了"）
- **动态点击类（target switching）也难** —— 有玩家反馈"动态定位要老命"
- **有些场景会打很久没结束** —— 那是按**目标击杀数**计的，打完固定个数就结束，不是卡住了
- **某些场景小球移动速度跟不上** —— 如果你灵敏度偏灵敏（cm/360 < 50），这是预期的，那些场景对你无效

### 摸底完的档位判断（官方标准）

| 你的情况 | 下一步 |
| --- | --- |
| 能**舒适拿到 Mammoth** | 去试 **Medium** 档 |
| Medium 打到 **Lavender / Indigo 附近**（S2 里对应中段） | 去试 **Hard** 档 |
| 还在 Lemming–Penguin | 老实留在 Easier，先把每个子类都打出分 |

---

## 六、第 5 步：读懂你的结果

回到你的成绩页 `https://evxl.app/u/76561199835441317`，点进 **Viscose Benchmarks S2**，看三个东西：

1. **顶部 Unranked / 百分比 / Volts**
   - 全部场景都填了分，才会从 `Unranked` 变成具体 rank
   - 拿 rank 的硬门槛是：**每个子类别至少一个分数**
2. **每个场景的 SCORE 百分比**
   - 这一行显示你离下一级 rank 还有多远（`0%` 就是还没填分）
3. **哪几个子类别最低** ← **这是最重要的输出**
   - Viscose 这套东西的全部价值就在这里：低分不是笼统的"要练 tracking"，而是精确告诉你「**你的问题是小幅度精细控制**」或者「**是大范围位移发力**」这类具体的诊断

---

## 七、日常训练循环（照着做就行）

每次 40–60 分钟，四段结构，**第四段不能省**：

```
① 热身 5-10 分钟
   低档（= 技术精炼档）挑 2-3 个场景，每个打 3-5 遍
   只看动作质量，不看分数

② 主课 25-35 分钟
   主档里【一次只攻 1 个子类别】，把这个子类的 3 个场景全打
   例：今天攻 CONTROL TRACKING / WRIST →
        Leapstrafes Control、Controlsphere SuperbAim、VT Controlsphere
   目标：打到接近或超过该子类达标线

③ 压力 10-15 分钟
   往上一档挑 1-2 个场景，各打 3 遍
   不求分，只求暴露技术极限问题

④ 归因 5 分钟 ← 最关键
   对今天分数最低的那个场景，写一句话：
   "这个场景逼我改进的技术点是：______"
   "我具体做错了什么：______"
```

**为什么 ④ 不能省**：Viscose 视频里反复强调"我把每一个任务都当作**一个优化的测试**"。少了归因，这套东西就退化成普通的 playlist，全部价值就没了。

**每周加 1–2 次弱点补强**：找出最弱的子类，去 Kovaak's 里**搜基础场景名找变体**（例如搜 `cloverRawControl`，会出现 slower / faster / larger / 加 blink 等版本），每个变体练的东西不同：

| 变体 | 练什么 |
| --- | --- |
| slower 降速 | 动作质量、路径精度 |
| faster 提速 | 反应与预判（逼你提前量） |
| larger 加大目标 | 大范围位移发力（手臂主导） |
| smaller 缩小目标 | 精细控制（指尖主导） |
| 加 blink | 抗突然位移、重获取目标 |

---

## 八、执行检验（每次练完打勾）

### 每次训练后（30 秒）

- [ ] 四段结构都做了（热身 / 主课 / 压力 / 归因）
- [ ] 主课是**按子类别成组练**的，不是随机打
- [ ] 写了至少 1 条具体的归因（能说出"这个场景逼我改什么"）
- [ ] 如果整轮打完说不出任何技术问题 → **判定为自动驾驶，本轮不算数**

### 每 2 周复测一次

- [ ] 主档 36/30 个场景全部重打一遍，更新分数
- [ ] 对比上一次：rank 有没有升
- [ ] **关键指标**：最弱子类别有没有收窄（看"子类别最低分 ÷ 该子类达标线"这个比值有没有涨）
- [ ] 子类别之间的差距有没有变小（变小 = 你正在变全面，这正是 Viscose 的设计目标）

### 每月自检（防跑偏）

- [ ] 有没有超过 60% 的时间都在打**自己已经能拿 rank 的简单场景**？→ 是的话你在刷舒适区，该加压力
- [ ] 有没有只打自己擅长的类别？→ 违反"每子类都要有分"的设计意图
- [ ] 有没有连续 2 周没写归因？→ 已经退化成 playlist 模式了

### 设置硬性检查（每次复测前确认）

- [ ] **fingertip 类场景灵敏度 ≥ 50cm/360**（否则分数无效）
- [ ] **FOV ≥ 103**（你已经是 103 ✅，别动它）

---

## 九、和你现有体系怎么配合

你现在跑的是 `Voltaic Fundamentals - Iron`（12 场景）+ 节拍（BPM）的日更体系。**不用推倒**，分工如下：

| | 你的现有体系 | Viscose Benches |
| --- | --- | --- |
| 角色 | **主课**（每天练） | **诊断 + 周期复测层** |
| 管什么 | 动作节奏（节拍）、命中率门槛 | 分数、技术弱点定位 |
| 频率 | 每天 | 每 2 周复测一次 |

**衔接方式**：
1. 现有 12 场景日更继续照跑（节拍目标 Pasu 40 / Tamspeed 100 / Wide Wall 100 / 1w2t 110 不变）
2. 每 2 周用 Viscose S2 做一次全量复测 → 得出**子类别弱点分布**
3. 把弱点结论喂回日更体系：例如复测显示 **Wrist 子类最低** → 在日更里加练 Wrist 类场景（Leapstrafes、Controlsphere 系）
4. 一个管「怎么动」（节拍），一个管「动得对不对」（分数与技术诊断），互不冲突

**可选**：如果你想把 Viscose 的复测分数也录进 InfluxDB，在 Grafana 里做子类别雷达图，让"最弱子类"的变化可视化 —— 说一声我可以接着搭（复用你现有的 8087 那套环境）。

---

## 附录：S2 · Easier 档完整场景（30 个）

按类别分组，方便你按"子类别成组练"：

**CONTROL TRACKING / ARM（手臂）**
1. Smoothsphere Viscose Easier
2. Whisphere Viscose Easier
3. SmoothBot Perfected Easier

**CONTROL TRACKING / WRIST（手腕）**
4. Leapstrafes Control wobin Easier
5. Controlsphere SuperbAim Viscose Easier
6. VT Controlsphere Viscose Easier

**CONTROL TRACKING / FINGERTIP（指尖）** ← 需要 cm/360 ≥ 50cm
7. Air Angelic 4 Voltaic Easy 70%
8. cloverRawControl Viscose Easier 50cm
9. Flower Easier 50cm

**CONTROL TRACKING / BLENDING（混合）**
10. PGTI Voltaic Easy Smoother
11. Air CELESTIAL No UFO Easier
12. RawControlSphere Easier

**REACTIVE TRACKING（反应跟枪）**
13. Air Spectral Easy 85%
14. VT Aether Bot 1 Easier
15. Air Pure Easier No UFO
16. Air Voltaic Invincible 4 Easier

**FLICK TECH（甩枪技术）**
17. ww5t Voltaic Slightly Larger
18. eth Pasu Micro Easier
19. kinTS Voltaic Easy 85%
20. domiSwitch Easier
21. B180T Voltaic Easy Slower

**CLICK TIMING / DYNAMIC CLICKING（点击）**
22. Pasu Voltaic Reload Easier
23. VT Bounceshot Viscose Easier
24. CatClick Easier
25. 1w3ts Pasu Perfected Micro Goated Larger 80%
26. Popcorn MV Easier
27. skyClick Goated Easier
28. VoxTS Click Easier
29. VT Floating Heads Viscose Easier
30. psalmTS Viscose Click Easier

---

## 附：这份手册用到的所有链接速查

| 用途 | 地址 |
| --- | --- |
| 你的成绩页（收藏它） | `https://evxl.app/u/76561199835441317` |
| evxl.app 首页 | `https://evxl.app/` |
| Raw Input 组页（三个 Viscose 版本入口） | `https://evxl.app/groups/raw-input` |
| 官方 Google 表格 | `https://docs.google.com/spreadsheets/d/1bFAlt6g_Gm8P9RBkcAoObpbIGFwVS5gXIdIK9B_YyZE/edit` |
| 表格网盘备份（评论区） | `https://pan.quark.cn/s/07ade15bedf9?pwd=7gFi`（码 `7gFi`） |
| 参考视频 | `https://www.bilibili.com/video/BV1m71vBoEh6/` |
| 原作者原视频 | `https://youtu.be/VARQNEdQYbw` |
| Raw Input Discord（问题反馈） | 见 evxl.app 页脚 |
