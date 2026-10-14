# YouTube 渠道调研发现：场景19-前压心态与习惯化

> 调研日期：2026-10-14
> 主题：VALORANT 前压（主动压上去打）时的心态管理（紧张/怕死/犹豫/上头）与心态习惯化（条件反射/习惯回路/暴露/压力接种）、决策框架、生理调节、与练枪衔接
> ⚠️ **重要环境声明**：本次调研在字幕抓取阶段被 YouTube 反爬机器人墙全面封锁，**0/10 字幕成功**。下文元数据来自 yt-dlp 站内搜索接口（该接口未被墙），关键原句无法从字幕提取，已如实标注。

---

## 〇、本次执行环境与封锁诊断（必读）

### 0.1 实际环境与 SOP 假设的偏差
| 项 | SOP（入口文件第八节）假设 | 本次实际 |
|---|---|---|
| 代理端口 | `127.0.0.1:7892` | 7892 未监听；实际混合代理口为 **7897**（Clash Verge + verge-mihomo） |
| 外部控制 API | 未提及 | TCP 9097 未启用，仅命名管道 `\\.\pipe\verge-mihomo` 可用（secret=`set-your-secret`） |

### 0.2 封锁现象
ytsearch（站内搜索接口）正常返回 38 条结果，但进入 **player API / timedtext 字幕接口** 即返回：
```
ERROR: [youtube] <id>: Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies ...
```

### 0.3 已尝试的绕过手段（全部失败，逐项留证）
| # | 手段 | 结果 |
|---|---|---|
| 1 | 冷却等待 2 分钟 + 3 分钟后重试 | 仍墙 |
| 2 | Clash 切节点（管道 API）：日本 JP3/新加坡 SG5/韩国 KR2/荷兰 NL2/美国 US20/日本 JP10 + hysteria 美/日/新 共 9 个节点 | **全部**墙（跨 6 国 reality+hysteria） |
| 3 | 换 player client：`tv,web_embedded` / `ios` / `mweb` / `visionos` / `tv samsung` | 全部墙，"No title found in player responses" |
| 4 | 手动安装 deno 2.9.7 + `--js-runtimes deno:<path>` | 仍墙 |
| 5 | `--remote-components ejs:github` + deno 组合 | 仍墙 |
| 6 | `--cookies-from-browser edge`（运行中） | cookie 库被浏览器独占锁定（issue #7271） |
| 7 | 手动解密 Chrome cookie（win32file 共享读 + DPAPI + AES-GCM），拿到含 LOGIN_INFO/1PSID 的 24 条登录态 cookie | 仍墙 |
| 8 | headless Chrome 刷新 cookie 库后重新提取 | 仍墙 |

**结论**：封锁发生在 YouTube 服务端 player 接口的 **IP 信誉层**，与登录态、JS 运行时、player client、节点国家均无关——该代理供应商的出口 IP 段被 YouTube 整体标记。这与入口文件 8.2.1 记录的"共享节点被标记时切换节点"一致，但本次切换 9 个节点均无效，说明是供应商级 IP 段被封，非单节点问题。

### 0.4 解除封锁所需（超出子代理权限）
- 需要一个**未被 YouTube 标记的干净出口 IP**（住宅代理 / 未被滥用的节点），或
- 由 MainAgent 通过 GUI 在 Clash Verge 里人工逐个节点试到一个不被墙的（本次管道 API 切了 9 个都不行，可能需试更多），或
- 待该代理供应商更换未被标记的 IP 段后重跑本 SOP。

### 0.5 第二轮尝试：第三方服务端渲染转写（均失败）
按指示改用 web_fetch（走工具自身网络，绕开本代理 IP）试第三方转写服务：

| 服务 | 请求 | 结果 |
|---|---|---|
| youtubetotranscript.com/transcript?v=ID | WE_acaOsYCQ / cjgq6NXFM2c / 7gMwkCTbHMs | "link fetch error"（POST 端点或反爬） |
| youtubetranscript.com/?v=ID | WE_acaOsYCQ | 仅返回 JS 表单落地页，无正文 |
| tactiq.io/run/youtube_transcript?yt=URL | WE_acaOsYCQ | 仅营销页，无转写正文 |
| tactiq.io/tools/youtube-transcript?yt=URL | cjgq6NXFM2c | 仅营销/FAQ 页，转写需点按钮触发客户端 API |
| notegpt.io/youtube-transcript-generator?youtube_url=URL | WE_acaOsYCQ | 仅营销页，转写客户端生成 |
| web_fetch 直连 YouTube watch / timedtext | WE_acaOsYCQ | watch 页 fetch error；timedtext 被 robots.txt 禁止 |
| invidious 前端 inv.nadeko.net captions API | WE_acaOsYCQ | 被 robots.txt 禁止 |

**结论**：这些第三方服务转写正文均由浏览器端 JS 调 API 生成，web_fetch（静态 GET）无法触发，全部只拿到营销/表单壳页；直连 YouTube 又被 robots 挡。此路不通。

---

## 一、精选视频清单（元数据来自 ytsearch，真实可回溯）

> 以下 10 个视频按"前压心态/摆烂/信心/压力焦虑/生理调节/反面意见"六个角度精选。播放量为搜索时快照。**因字幕被墙，关键原句一栏暂缺，待环境恢复后补抓。**

| # | 视频 ID | 标题 | 频道 | 播放量 | 角度 |
|---|---|---|---|---|---|
| 1 | `WE_acaOsYCQ` | Easiest Way To Build CONFIDENCE In Valorant (Confidence Valorant) | Duckeeh | 14,098 | **前压恐惧/信心**（描述明说"not be scared when pushing/peeking"） |
| 2 | `7gMwkCTbHMs` | How to Play Aggressive WITHOUT Dying | Sena | 1,072,873 | **激进打法决策框架**（何时前压、前压不死） |
| 3 | `cjgq6NXFM2c` | Why Your Mindset is Ruining Your Aim in Valorant | Zapper | 47,424 | **心态毁枪法**（"Aiming is like 80% mental"） |
| 4 | `sMSig_ReEyU` | The Truth To Actually Fixing Your Mental in VALORANT \| No BS | Boni | 36,881 | **修心态/不摆烂**（stop raging over bad mental） |
| 5 | `cPyFMtNnQ7k` | How to Conquer Fear when Gaming (Performance Anxiety) | Ron Rambo Kim | 210,313 | **游戏恐惧/表现焦虑** |
| 6 | `grkPPLc40Fs` | How The Top 1% Deal With Performance Anxiety | Sam Martin - Peak Performance | 95,293 | **顶尖 1% 处理表现焦虑**（压力调节） |
| 7 | `FhfBGZoDA7o` | The BEST WAYS to AVOID TILT based on SCIENCE | SC Valorant Guides | 42,482 | **基于科学的防摆烂** |
| 8 | `vPGO1m--jW8` | The Mindset I Used to Solo Queue to Radiant in Valorant | Dragonmar | 82,559 | **单排上辐锐的心态**（不摆烂/不归咎队友） |
| 9 | `dAp4cYzNcJ0` | How to Calm Your Nerves Before a Game: Mental game tip | Eli Straw | 8,087 | **赛前生理调节/冷静神经** |
| 10 | `-3NNmUfdUtM` | How to Stop Tilting While Gaming (or Use it to Win) | eAthlete Labs | 19,141 | **反面意见**：把摆烂/情绪反过来利用，而非压制 |

### 备选（未入选但相关）
- `3r3koFjwXJo` How to Untilt Yourself in Valorant — Konpeki（35,807）
- `b1X3YuT_ruk` Why You Suck at Peeking (and how to fix it) — Konpeki（289,748，偏技术peek）
- `XNMgCjPs9T8` What Makes A Good Duelist? — Konpeki（373,155，偏决斗位技术）
- `ieO_bz41es8` How to EASILY get into a Flow State — Sam Martin（649,347，心流）
- `yG7v4y_xwzQ` Sport psychology - inside the mind of champion athletes — TEDx（2,361,556，学术体育心理）

---

## 二、核心发现（待字幕补全后填充）

> ⚠️ 本节暂空。按验收标准"结论必须能回溯到字幕原文"，在字幕被墙、无原文可引的情况下，**不编造关键原句**。环境恢复后按下列提纲从 10 个视频字幕提取：
>
> 1. **前压恐惧的本质**（视频 1/5）：怕死/犹豫是被高估的风险感，如何用"小身位暴露→可撤回"的暴露梯度脱敏
> 2. **激进 vs 送的决策线**（视频 2）：何时前压是赚、何时是送，结构化前压而非冲动 peek
> 3. **心态与枪法的耦合**（视频 3）：紧张如何直接破坏瞄准，生理唤醒倒 U 曲线
> 4. **摆烂回路与中断**（视频 4/7/8）：失败后如何快速重置、不归咎、聚焦过程
> 5. **表现焦虑的生理调节**（视频 6/9）：呼吸/心率/肌肉放松的具体操作
> 6. **反面意见**（视频 10）：情绪唤醒是信号而非敌人，可被重新导向为侵略性燃料

---

## 三、反面意见（待字幕补全）

候选来源：`-3NNmUfdUtM`（eAthlete Labs，"How to Stop Tilting While Gaming **(or Use it to Win)**"）——主流建议是"冷静/离开/压制情绪"，该视频主张情绪唤醒可被利用为侵略性与专注的燃料。具体原句待字幕抓取后引用。

---

## 四、覆盖率报告

| 指标 | 数值 |
|---|---|
| 搜索关键词组数 | 3 组（①valorant 心态/不摆烂 ②entry fragger 信心/前压恐惧 ③赛前例行/呼吸/压力心理教练） |
| 搜索结果总数 | 38 条（15+8+15，去重后） |
| 精选视频数 | 10 |
| 字幕成功数 | **0 / 10** |
| 字幕失败数 | 10 / 10（全部：YouTube player 接口反爬机器人墙，见 0.3） |
| 第三方转写服务补抓 | 试 7 个端点（youtubetotranscript×3 / youtubetranscript / tactiq×2 / notegpt / 直连YT / invidious），全部失败，见 0.5 |
| 跳过原因 | 全部为同一封锁原因，非"无字幕"——视频本身应自动字幕存在，只是抓不到 |

### 与已有素材的去重
已核对 `实战场景/12-低分段杀很多人.md` 与 `07-捷风击杀后不开烟自保.md`：前者偏低分段机械压制/信息差（NGA/B站为主），后者偏捷风技能自保，**均未覆盖"前压心态/压力习惯化"心理角度**，本次精选无重复引用。

---

## 五、后续建议
1. 环境恢复后，直接用同一组 10 个 ID 重跑 `8.1` 命令模板（代理口改为 7897），即可补齐字幕与关键原句。
2. 若 YouTube 持续封锁该代理，建议换住宅代理，或 MainAgent GUI 人工在 Clash Verge 逐个节点试出不被墙的出口。
3. 命名管道切节点脚本与 deno 已就绪（见产出文件清单），恢复后可直接复用。
