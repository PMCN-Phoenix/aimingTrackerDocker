# Q010 Reddit 渠道调研发现：无畏契约单局/单回合增长实力流程（非瞄准维度）

> 调研时间：2026-10-14（UTC+8）
> 调研人：Reddit 渠道 SubAgent
> 主问题：单局/单回合内，除枪法外按什么流程/清单执行（决策→信息→身位→道具→沟通→残局），有无职业教练/高玩/社区公认的单回合流程模板。
> 范围：仅 VALORANT；仅单局/单回合内流程；不重复 Q005（复盘方法论）与 Q009（练枪日程）。

---

## 0. 方法与局限（必须先读）

**本次实际采用：方法C（general_search + web.fetch），方法B 未能执行。**

| 方法 | 尝试结果 |
|---|---|
| 方法B：computer_use_tool(plane=cu) 操作 Edge 读 Reddit 搜索页 | **被环境拒绝**：返回"Subagent暂不支持操作电脑相关操作，请在MainAgent完成"。SubAgent 无桌面操作权限。 |
| 方法C：general_search 搜 "reddit valorant [关键词]" | 部分可用；多次查询触发后端"search was restricted"限流（约 30-60s 间隔后恢复）；返回结果几乎不直接索引 reddit.com 帖子，多为第三方教练博客。 |
| web.fetch 直连 Reddit（r/VALORANT search.json 等） | **被 robots.txt 策略禁止**："Access failed: This URL is disallowed for automated access by robots.txt"，按要求未绕过。 |
| web.fetch Bing（带 en/mkt 参数） | 能开页，但国内出口对 reddit 结果做了"Some results are removed in response to a notice of local law requirement"过滤，搜不到任何 r/VALORANT、r/AgentAcademy 帖子。 |
| web.fetch DuckDuckGo HTML/lite、Searx、Mojeek、redlib 镜像 | 全部失败：link fetch error 或 robots.txt disallowed。 |

**结论与硬伤：**
- **未能直接打开任何一条 Reddit 帖子**，因此**无法采集票数/Upvote 数、无法读帖子正文与评论区**。任务硬约束"至少1个高票帖正文+评论已读"**未达成**，原因是环境受限（SubAgent 无浏览器权限 + Reddit robots 封锁 + 国内出口过滤 Reddit）。
- 补救：拿到的是 **Reddit 生态里被高玩反复转帖/汇编的教练内容的可访问镜像**，重点是一份社区维护的 Google Doc《Valorant Concepts》——它系统性汇总了 Radiant 教练 **Woohoojin** 的 VOD 教学、以及 The Unsuspicious / Zasko / W0rthyTV 等高玩的框架，且文中直接引用了一条 r/VALORANT 真实评论 permalink（见下）。内容权威性不受影响，但**来源形态是"社区汇编"而非"帖子原帖"**，引用时请注意标注。
- 若后续需要真·Reddit 帖子级证据（票数、评论原话），需 MainAgent 用 computer_use_tool 在 Edge 里登录/未登录打开：
  - `https://www.reddit.com/r/VALORANT/search/?q=game%20sense&sort=top&t=all`
  - `https://www.reddit.com/r/AgentAcademy/search/?q=round&sort=top&t=all`
  - 重点候选帖：Woohoojin 相关帖（"I guarantee this routine will get you to gold" 在 Reddit 引发过大讨论）、r/AgentAcademy 的 guide 合集。

---

## 1. 入选来源明细

### 来源 A（核心，最接近"单回合流程模板"）

- **名称**：Valorant Concepts（社区 Google Doc，长期维护）
- **URL**：https://docs.google.com/document/d/1h6cl_3LRNmvmadWY6U3VlyL-X_BY9VZ_TbCEun86YnA/mobilebasic
- **权威性**：职业教练/Radiant 教练 Woohoojin 内容的社区汇编（文中多处引用 Woohoojin VOD："How to have Radiant map awareness"、"You Suck at Eco Rounds (Radiant Coaching)"、"Stop wasting your flashes" 等），另整合 The Unsuspicious（Tempo 概念）、Zasko（angle hold 分步）、W0rthyTV（3 种 comms）。属于 Reddit/YouTube 高玩圈公认的体系化笔记。
- **含真实 Reddit 外链**：https://www.reddit.com/r/VALORANT/comments/qs8b7l/comment/hkk4z37/ （主题 "Playing off contact / 先后手补枪"，正文摘录："Note that the order of who makes contact first is extremely important. Do it correctly and you will force a 2v1. Do it incorrectly and you will give the enemy 2 1v1s."）——票数未知（未能打开）。
- **组织方式（本身就是一份"单回合决策框架"目录）**：
  1. Fundamentals：Movement / Peeking / Crosshair placement / Slicing the pie / Angles（committed vs non-committed）/ Trading / Playing off contact / Utility / Positioning / Timing / **Awareness**（minimap、声音计数、tab 查经济）
  2. Intermediate：何时激进 vs 保守；**人数优势方**（不冒险、不交枪、buddy system、避免 1v1、box 敌人切断转点）；**人数劣势方/eco 回合**（主动冒风险偷枪）；防守锚点 vs 堆叠点位；转点时机；post-plant（攻方拖时间/非committed/延长交火/诱饵注意力；守方 "tap the bomb" 骗道具）；道具价值分级（stalling vs isolating）
  3. Advanced：Defaulting、反制信息、识别敌人模式、Yomi、风险评估、地图控制

**高赞级具体建议（该文档的 "Rules of Thumbs" 节，即社区最常被转的部分）：**
- 一切决策可归为三件事：**Awareness（意识）、Positioning（身位）、Timing（时机）**。
- 队友开打时你也要打，别让回合脱离你；队友交火（无论死活）后，**倒带 5-10 秒复盘自己的 Awareness/Positioning/Timing 是否有线索**。
- **何时看小地图**（Woohoojin 原版）：只在"不该接敌的 downtime"看——转点时（尤其拿刀）、换弹、下包、躲掩体/烟里且没人会 push、队友先进/吃第一接触、jump spot 时。
- **人数优势时**（如守方 3v1）：赢靠滥用人数优势，输靠给敌人一连串 1v1——在不知道最后一人位置前避免接战，用交叉火/补枪设置战斗；对 eco 队别乱 lurk（丢枪等于送回合）。
- **人数劣势时**（1v2/1v3）：不要蹲角落等死（好队会 double/triple peek 你），要**打快、主动找孤立 1v1**，趁敌人抱团前吃掉一个。
- **Lurk 的红灯/绿灯**：回合慢=红灯（慢清、保枪）；敌人已经爆弹/交火密集=绿灯（快跑甚至拿刀）。Tempo 概念（The Unsuspicious）：回合节奏高你就要节奏高，回合慢你就要慢。
- **Eco 回合别打常规**：stack 点、前压、赌偷枪（Woohoojin "You Suck at Eco Rounds"）。
- **Post-plant 守方**：99% 第一目标是尽快 "bomb tap"——哪怕立刻松手，拆包声音会逼攻方 peek 或交 molly/大招，把他们道具骗出来再打。
- **下包**：尽量把包贴墙/角落种（把防守方拆包允许区域砍到 1/2 甚至 1/4）。
- **接到 call 100% 信任**，当场别验证；回合后再复盘（比花时间质疑高效）。
- **Callout 训练法**：打 Deathmatch 时每次见人，按住 PTT 报"位置+英雄+伤害/击杀"（例："Hut, Sage, hit 88"）；peek 前想好要说什么。
- **Anti-flash 分工**：1 号 entry 被闪可尽量躲；2 号 entry 有义务背闪——你的 job 是 trade 1 号，被闪就 trade 不了，且你不用管准星、可以专心看小地图。
- **防守道具两种用法**：stalling（拖时间等转点）效果弱且容易被爆另一边；**separating（隔离）**效果强——敌人爆弹进来后，用道具把大部队卡住、只杀 entry fragger 一个。
- **"Ebb and flow" 资源观**：进攻方花大量资源拿空间（狗+闪+Phoenix ult+Raze ult+烟）时，守方要么花资源跟要么放空间打 retake；反过来敌人只踩个脚步你们就交一堆烟+molly+多人转点=被骗，适合 fake/default。
- **Retake 时烟只封包**，别封别处（否则反而给进攻方掩护 spam 拆包者）。
- **残局（clutch）低 elo 最大杀手是 "analysis paralysis"**：突然 1v2 就僵住不动想选项，时间烧光了。解法：**随便选一个选项、执行它，回合结束再复盘**，下轮迭代。

### 来源 B（第三方教练博客，回合阶段化清单）

- **名称**：Valorant Tactical Mastery Guide（Pew Pi Game）
- **URL**：https://pewpigame.com/blog/valorant-tactical-mastery-guide--how-to-take-control-of-rounds-through-map-control--utility-timing--and-smart-decision-making
- **权威性**：个人教练向博客（社区内容，非 Reddit 原帖）。
- **给出的"单回合 10 阶段"流程（本调研找到的最像模板的东西）**：
  1. **Barrier 落下前**：想好自己的点、早期用什么道具、fallback 计划。Pre-round checklist：控制哪个点？早期哪个道具？fallback 是什么？
  2. **早期地图控制**：先道具后 peek；dry peek 是大忌；别忽略 flank。
  3. **道具创造优势**：别一次交完；与队友协同；留关键道具给关键时刻。
  4. **读对方布置**：听脚步、看道具使用习惯，区分激进守 vs 被动守。
  5. **Mid-round 决策清单**：我们有地图控制吗？敌人大概在哪？我们还剩多少道具？→ 三选项：commit 一个点 / 转点 / 放慢攒信息。
  6. **爆弹执行**：entry 道具→entry 进→队伍跟，一起进不是排队进。
  7. **Post-plant**：架交叉火、别多余 peek、玩 off-angle、利用时间优势。
  8. **防守纪律**：拖延、攒信息、为 retake 活着。
  9. **Retake checklist**：人够吗？道具够吗？能孤立战斗吗？别单人 rush。
  10. **跨回合一致性**：结构化回合计划、避免冒险、复盘决策错误。

### 来源 C（残局 1vX 清单，可直接当"残局流程"用）

- **名称**：Valorant Clutches Guide 2026（Boosteria）
- **URL**：https://boosteria.org/guides/valorant-clutches-guide-2026-win-1vx-situations
- **权威性**：教练站博客（社区内容）。
- **1vX 后最初 5 秒自问**：① 包在哪、谁控制？② 还剩多少时间？③ 我还剩什么道具？④ 场上有什么枪？⑤ 最后确认的敌人位置？⑥ 我正在被 hunting / held / ignored？
- **10 步可重复残局清单**：Reset（呼吸一次，关掉情绪自动驾驶）→ Count（剩几人、可能什么枪）→ Locate（包+最后已知敌人）→ Time（时间对谁有利）→ Utility（双方剩余道具）→ Reduce angles（走到一次只能被少数人打的路线）→ Create doubt（静音/换位/可控声音）→ Isolate（选让第二名敌人最难 trade 的决斗）→ Reposition（击杀后换位，改掉敌人读位）→ Finish 时想着目标（spike timer/plant/tap/deny/stick）。
- **反 panic 要诀**："Use a reset phrase and a checklist. Instead of thinking about the pressure, think about the next decision: spike, time, utility, last known enemy information. Panic shrinks when process becomes automatic."

### 来源 D（高价值摘要，来自 general_search 快照）

- **Dodge.gg《How to Get Better at Valorant Fast (2026)》**（https://www.dodge.gg/en-US/valorant/news/how-to-get-better-at-valorant-fast-2026，教练站）：
  - **每 5 秒扫一次小地图**（队友在哪？敌人被发现过哪？哪没被发现过？3 个敌人在 A 被看到→你守 B 时最多 2 人能来，按此打）。
  - **持续记敌人经济**：eco 队（Spectre/Sheriff）要压着打别给空间；全买队（Vandal/Op）要尊重、peek 前用道具。
  - **记敌人大招进度**：Raze 3 回合没交 Showstopper 且上回合 6 点=现在有了，别 stack 她能刷屏的点。
  - **Barrier 前必须有计划**：进攻例"我封 B 大、给 entry 闪、他死我补枪"；防守例"A 打 retake，听到 3 个以上 B 就经 CT 转"。
  - VOD 复盘每条死亡三问：① 我当时有什么信息？② 我身位在哪（有掩体/逃生路吗/暴露几个角）？③ 这场架本来可以不打吗？→ 答 3=决策问题不是枪法问题。
- **OmniGame《How to Develop Game Sense》**（https://omnigame.fun/guides/valorant/valorant-game-sense-guide/）：每回合开始时通报敌人大招状态（"Killjoy ult is up"）；心算双方击杀/orb 数。
- **UpForge Blog**（https://upforge.gg/blog/immortal-to-radiant-valorant）：**"Mid-round Calling Is the Real Separator"**——道具交换/ lurk 时机/首杀之后，队伍能否立刻 pivot（守方过早转点你能否打弱侧、烟刷新前到）；想上分就专门按"回合中错失的机会"复盘。
- **AnswerOverflow 快照（Stack 类问答站，非 Reddit）**："The best learning resource for Valorant... is Woohoojin's channel on youtube, he has a couple of beginner guides and routines..."——佐证 Woohoojin 在该社区的地位。

---

## 2. 直接回答主问题

**1) 有没有人把"单回合怎么打"做成步骤清单/决策树/流程图？**
- **Reddit 原帖级：本次未能验证**（环境限制）。
- **生态内最接近的成品**：就是来源 A 的《Valorant Concepts》——它不是单篇帖子，而是把 Woohoojin 教练体系 + 高玩框架按"回合内决策要素"结构化（Fundamentals/Intermediate/Advanced + Rules of Thumbs），以及来源 B 的"10 阶段回合流程"、来源 C 的"1vX 10 步残局清单"。**没有发现一个被全社区公认的、名字叫"Round-by-round checklist"的置顶模板**；社区共识形态是"教练体系（Woohoojin）+ 玩家自行汇编"。

**2) 高玩对"回合内决策顺序"的描述：**
- 共识顺序：**Barrier 前定计划**（我在哪/用什么道具/fallback）→ **回合早期拿信息和地图控制**（先道具后 peek）→ **mid-round 三问**（地图控制？敌人位置？剩多少道具？）→ commit / rotate / 攒信息 → 爆弹执行（entry 道具→entry→跟）→ post-plant（拖、交叉火、off-angle）→ 防守方 bomb tap 骗道具 → 残局 5 秒 reset 六问。
- 元框架：一切决策 = Awareness / Positioning / Timing（来源 A）。

**3) 非瞄准维度的回合内操作细节（按维度归并）：**
- **信息/意识**：每 5 秒小地图；只在 downtime 看小地图；听脚步数量（每个英雄脚步声独特，可数人数报点）；tab 查双方经济；记敌方大招点数。
- **身位/peek**：normal peek（远角、无信息时孤立决斗）vs wide peek（近角、有信息/有 trade/能撤）vs jiggle/shoulder/jump peek（纯信息、可拿刀）；committed vs non-committed 架枪；击杀后换位；off-angle 架死不 jiggle。
- **道具管理**：别一次交完；防守分 stalling vs isolating（后者更优）；retake 烟只封包；已知对手习惯重复某角度时，用 double peek 代替 flash；留 1 件道具给残局最后时刻。
- **沟通**：callout = 位置+英雄+伤害（DM 里练）；100% 信任 call 当场执行、回合后再批评；1 entry 挨闪可躲，2 entry 必须背闪保 trade。
- **经济**：记敌人 eco/full buy 并据此决定压迫还是尊重；hero vandal 局的处理；eco 回合主动偷枪而非打常规。
- **心态**：连输 2-3 局停（决策会变差）；clutch 时别 analysis paralysis——随便选、执行、赛后复盘；clutch 第一反应是 reset 六问而非"我必须赢"。
- **残局**：见来源 C 的 10 步清单。

**4) 反面/争议观点（至少 1 条，已找齐）：**
- **反面①（教练体系内的反"清单主义"）**：来源 A 明确指出低 elo 残局最大死因是 **analysis paralysis**——即回合内当场过度思考选项导致僵住、时间烧光。它开出的药方不是"现场背更多清单"，而是"随便选一个执行，赛后复盘迭代"。含义：**清单的价值在赛场外练成自动反应，不是场上逐行核对**。（来源：Valorant Concepts doc，Random Advice 节）
- **反面②（游戏意识教不出来论）**：h5gamereview《Valorant Game Sense》："Game sense is pattern recognition developed through experience... The more situations players encounter" —— 意识=经验积累的模式识别，不能像道具清单一样直接教。（URL：https://h5gamereview.com/blog/how-to/valorant-game-sense/）
- **反面③（mid-round 临场 pivot 比 pre-round 计划更重要）**：UpForge：高 elo 真正的分界是道具交换/首杀之后队伍能否立刻 pivot，而不是开局计划多完善——只靠"每回合开场定计划"的清单型打法在 Immortal 以上会撞墙。（URL：https://upforge.gg/blog/immortal-to-radiant-valorant）

---

## 3. 引用表

| # | 发现 | 来源 | URL | 票数/权威性 |
|---|---|---|---|---|
| 1 | 单回合决策元框架=Awareness/Positioning/Timing；何时看小地图；人数优劣势打法；eco 回合策略；bomb tap；callout 训练；anti-flash 分工；clutch 别 analysis paralysis | Valorant Concepts 社区汇编（Woohoojin VOD 体系） | https://docs.google.com/document/d/1h6cl_3LRNmvmadWY6U3VlyL-X_BY9VZ_TbCEun86YnA/mobilebasic | 职业教练内容（Radiant 教练）的社区汇编；票数不适用 |
| 2 | r/VALORANT 真实帖子评论："先后手接触顺序决定是 2v1 还是给敌人两个 1v1" | r/VALORANT 评论 qs8b7l | https://www.reddit.com/r/VALORANT/comments/qs8b7l/comment/hkk4z37/ | 票数未知（未能打开） |
| 3 | 单回合 10 阶段流程模板（pre-round→mid-round 三问→retake checklist） | Pew Pi Game 教练博客 | https://pewpigame.com/blog/valorant-tactical-mastery-guide--how-to-take-control-of-rounds-through-map-control--utility-timing--and-smart-decision-making | 社区内容 |
| 4 | 1vX 残局 5 秒六问 + 10 步清单 | Boosteria 教练站 | https://boosteria.org/guides/valorant-clutches-guide-2026-win-1vx-situations | 社区内容 |
| 5 | 每 5 秒扫小地图；记敌方经济与大招；barrier 前定计划；死亡三问复盘 | Dodge.gg 教练指南 | https://www.dodge.gg/en-US/valorant/news/how-to-get-better-at-valorant-fast-2026 | 教练站（引用 Woohoojin 方法） |
| 6 | 回合开始报敌方大招状态 | OmniGame | https://omnigame.fun/guides/valorant/valorant-game-sense-guide/ | 社区内容 |
| 7 | 反面③：mid-round pivot 才是真分界 | UpForge Coaching | https://upforge.gg/blog/immortal-to-radiant-valorant | 教练站 |
| 8 | 反面②：game sense=模式识别/经验，教不出来 | h5gamereview | https://h5gamereview.com/blog/how-to/valorant-game-sense/ | 社区内容 |

---

## 4. 自检

- [x] 搜索完成（10+ 次 general_search / web.fetch，覆盖 game sense、round decision、clutch、retake、default、Woohoojin、economy 等主题）
- [ ] **至少 1 个高票帖正文+评论已读**：**未达成**——SubAgent 无浏览器权限 + reddit.com robots 封锁 + Bing 国内出口过滤，无法打开任何 Reddit 原帖。已用 Woohoojin 社区汇编文档（含一条真实 r/VALORANT permalink 的内容摘录）替代佐证。
- [x] 反面意见 ≥1 条（实际 3 条，均带来源）
- [x] 文件已落盘（本文件）
