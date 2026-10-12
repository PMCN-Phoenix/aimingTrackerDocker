# Discord 挖掘发现：平滑跟枪后微调僵住 & 蹲拉peek预瞄偏差后大角度修正

> 数据来源：Woohoojin Discord #vod-review 频道，12 个原始文件（约 2.1MB）
> 原始目录：`docs/问题库/Q005-对局复盘与实战迁移/实战场景-Discord原始数据/`
> 挖掘时间：2026-10-13
> 对应问题 Q007：palm grip 下，大肌肉平滑追踪结束后切换到手腕/手指微调时僵住、张力卸不下来；以及反向场景——静止预瞄保持后需要大角度flick时同样卡住。

---

## 〇、搜索关键词与命中统计

| 关键词 | 命中数 | 与本问题相关性 |
|---|---|---|
| tension / tense / tensed | 2 | 低（均指心理紧张，非肌肉） |
| relax / relaxed / relaxing | 8 | 低（均指心理放松/局势放松，非肌肉放松） |
| stiff / stiffen / frozen / freeze | 5 | 中（"stiff"指整体不流畅，归因硬件/游戏感；"freeze up"指心理僵住） |
| grip / gripping / clench | 0 | **零命中——数据集中无人讨论握鼠力度** |
| palm / claw / fingertip / hybrid grip | 0 | **零命中——数据集中无人讨论握法类型** |
| wrist / forearm / elbow | 20+ | 低（绝大多数"elbow"指 Bind 地图拐角，非解剖学肘；仅 2 处真正讨论手臂/手腕发力） |
| micro-adjust / microadjust / micro-flick | 26 | 高（大量讨论 flick 后微调） |
| transition / switch mode | 3 | 低（无"发力模式切换"讨论） |
| flick / flicks | 大量 | 高 |
| overaim / underaim | 67 | 高 |
| crouch / crouching | 大量 | 中（主要讨论何时蹲，非蹲姿对瞄准的力学影响） |
| pre-aim / preaim / crosshair placement | 大量 | 高 |
| choppy / jagged / staccato / smooth crosshair / fluidity | 41 | 高 |
| sensitivity / edpi / dpi / mouse space | 63 | 中 |
| hesitate / hesitation / stuck | 少量 | 低（"stuck"指走位/决策卡住，非肌肉卡住） |

---

## 一、核心结论（先说结果）

### 结论 1：Q006 标注的缺口被确认——Discord 数据集中**完全没有**肌肉张力/握法/桌面支撑层面的讨论

在 12 个文件（约 2.1MB，数千条复盘）中：
- **grip / gripping / clench：0 命中**
- **palm / claw / fingertip / hybrid grip：0 命中**
- **tension 作为肌肉术语：0 命中**（仅有的 2 处 "tense" 指 "tense rounds" 紧张局势）
- **relax 作为肌肉放松：0 命中**（仅有的 8 处 "relax" 指 "just relax, conserve energy" 心理放松，或 "to relax" 躲到角落平复心态）
- **forearm on desk / desk height / chair height / wrist rest：0 命中**

这意味着：**Woohoojin #vod-review 社区复盘的语言体系里，根本不存在"握法、肌肉张力、桌面支撑"这一层**。复盘者全部在"现象层"（准星在哪、动作顺不顺、开枪时机对不对）和"决策层"（peek 节奏、预瞄位置、移动选择）讨论问题，从未下探到"你用哪块肌肉、握多紧、支点在哪"。

这不是漏挖——是这个数据集的语言体系里就没有这套词汇。

### 结论 2：最接近"平滑→微调僵住"的复盘语言是"crosshair stagnated when micro adjusting"和"choppy/jagged crosshair movement"

复盘者确实观察到了"大范围动作后微调接不上"的现象，但他们的描述方式是：
- "你的准星在微调时停滞了"（stagnated）
- "你的准星移动是碎的/锯齿状的"（choppy / jagged / staccato）
- "你缺乏流畅性"（lack fluidity）
- "你有点硬"（a little stiff）

但他们给的**归因和解决方案**全部是：灵敏度、DPI、鼠标垫空间、开枪太快、预瞄不对、FPS 不够——**没有一个人归因到"发力肌肉切换"或"张力没卸下来"**。

### 结论 3：flick→micro-adjust 的时序，数据集中有非常清晰的方法论（Dannew 帧级分析）

Dannew 在 2024/2/27 做了一段帧级拆解，明确描述了"大动作→微调→开火"的标准时序。这是数据集中对"切换"最精细的描述，但他描述的是**时间节奏**（flick 用多少帧、微调留多少帧），不是**肌肉切换**。

### 结论 4：蹲拉 peek（crouch peek）在数据集中被大量讨论，但全部是"何时该蹲/何时不该蹲"的决策层讨论，**没有一条讨论蹲姿对瞄准力学/张力的影响**

蹲拉 peek 是常见复盘点，复盘者反复说"别老蹲着""蹲是为了躲头线不是为了spray""近程蹲spray远程burst strafe"，但没有任何一条说"蹲着的时候手臂支点变了/张力变了/导致你大flick挪不动"。

---

## 二、按主题分类的原文引用

### 主题 A：flick → micro-adjust 的标准时序（最接近本问题的"切换"讨论）

#### A1. Dannew 帧级拆解（2024/2/27）——"flick 是为了给微调争取时间"
> **来源**：Woohoojin2 - 副本 (4).md:477，Dannew，2024/2/27 02:02
>
> "The main thing we can work on is that we rush out shots. Some of these fights lack proper target acquisition... There is no way we saw that we were on him and tried to micro readjust. We just flicked and clicked. **We should be, flicking to the head, then micro readjusting if needed and if not needed then click.** One frame is 16.6ms in a 60fps recording. No human can react that fast... **Flicks can be practiced to become more consistent but they are never going to become consistent enough to depend on. Flicking is used to get close to the target as fast as we can to give us time to micro readjust.** Here is an example of a very similar peek but executed by Fnatic Derke... Frame 13 (this is the frame he fires in)... Summary: Practice taking your time to fire, make sure you are close enough to the target when you decide to stop. **Close enough means that after we have started slowing down all we have to do is micro adjust and then fire. (not flick and fire)**"

**对 Q007 的意义**：Dannew 明确描述了"flick（大动作）→ 减速 → micro adjust（微调）→ fire"的三段式。但他说的"slowing down"是**动作减速**，不是"卸张力"。他没有解释为什么有人在 flick 结束后 micro adjust 会卡住——他默认这是时间不够/开枪太快。

#### A2. Your Internet（2025/3/8）——"先大flick，再小flick修正"
> **来源**：Woohoojin2 - 副本 (2).md:618，Your Internet，2025/3/8 06:51
>
> "Everytime you peek an enemie/one peeks you, where you need to make a bigger flick to land on their head, you flick and imideatly shoot (and mostly whiff). **It is better make the first flick, and then micro adjust onto your target with a second smaller flick. Make sure you really think that you are on their head when you are shooting.**"

#### A3. Biboom（2024/4/27）——引用 Hooj 的"circle"理论：近小flick快、远大flick慢微调
> **来源**：Woohoojin2 - 副本 (4).md:7，Biboom，2024/4/27 11:56
>
> "Check out any Hooj's video on target confirmation where he talks about 'the circle'. **Basically you can go fast in small flicks close to your crosshair but need to slow down and microadjust more attentively with medium-long range flicks.**"

**对 Q007 的意义**：这是数据集中唯一一处提到"flick 距离不同，速度策略不同"的地方。Hooj 的"circle"理论区分了近距小flick（快）和远距大flick（慢、需专注微调）。但仍然是**速度/注意力**层面，不是肌肉层面。

#### A4. vlad?（2025/4/9）——反向错误："该用移动时却用手微调"
> **来源**：Woohoojin2 - 副本 (2).md:218，vlad?，2025/4/9 07:52
>
> "I was pretty confident I had it in the bag until I went over the second video 'Everything you need to master my overaim drill' and saw I was making a bunch of small mistakes like **microadjusting instead of using my movement** etc."

**对 Q007 的意义**：这是一个反向问题——差一点没对齐时应该挪步子（用移动把准星走过去），而不是纯用手小挪鼠标。对 Q007 的启示：微调僵住时，**也许应该用身体移动代替手微调**，而不是硬逼手做精细动作。

---

### 主题 B：准星"碎/锯齿/停滞"——最接近"平滑→微调接不上"的现象描述

#### B1. _anterior（2024/8/2）——"准星在微调整时停滞了"（数据集中最接近 Q007 症状的描述）
> **来源**：Woohoojin2 - 副本 (3).md:747，_anterior，2024/8/2 11:06
>
> "Second: Not much to say other than work on target prioritization and microadjusting, **i also noticed how in the first round your crosshair kind of stagnated when it came to micro adjusting**, SIX SHOT and the woohoojin intermediate drill can help with this, another key thing you can learn is **deadzoning** as moving around in gold almost immediately causes the enemy to whiff... Takeaway: Micro adjusting, target prioritization and overall mouse precision"

**对 Q007 的意义**：这是整条数据集中**唯一**一条用"stagnated（停滞）"描述 micro-adjust 状态的复盘。但 _anterior 给的解决方案是"SIX SHOT 练习 + WHJ intermediate drill + deadzoning（用移动代替手微调）"——**没有归因到肌肉张力**。

#### B2. Vex_DK（2025/3/28）——"准星移动是碎的（choppy）"
> **来源**：Woohoojin2 - 副本 (2).md:264，Vex_DK，2025/3/28 22:01
>
> "Also **your crosshair movement is super choppy here, I don't know if its a sensitivity thing, but it should be a lot more smoother.**"

#### B3. mayafuni [BTR!]（2025/3/8）——"清角动作锯齿状，建议 strafetracking"
> **来源**：Woohoojin2 - 副本 (2).md:614，mayafuni [BTR!]，2025/3/8 11:57
>
> "When you clear it, it's like you're tryin to slice the pie but your crosshair moves up or down and **your movements aren't a smooth clear, so it's very jagged and you have to readjust.** That leads you to do a more staccato clear... **Try strafetracking** — it sounds counterintuitive, but strafetracking helps your crosshair maintain a smooth movement while following a target... leading to easier duels since you know your crosshair is already adjusted."

#### B4. LongNameMan [ARC]（2023/5/29）——"准星移动不流畅，频繁重置鼠标，可能只用手腕瞄"
> **来源**：Woohoojin2 - 副本 (6).md:281，LongNameMan [ARC]，2023/5/29 02:57
>
> "-Cause you have really shaky aim which most of the time is because of too high a DPI but here might be a lack of mouse control. **-You don't have smooth crosshair movement when moving around like you're resetting your mouse very often which might mean you're DPI is too low relative to your mouse space or you're not using all the mouse space for aiming (eg. only using wrist for aiming)** -You also track corners really badly because of the above problem"

**对 Q007 的意义**：这是数据集中**唯一一处**提到"only using wrist for aiming"（只用手腕瞄）作为负面诊断。LongNameMan 把"不流畅+频繁重置鼠标"归因到"鼠标空间不够/只用手腕"——这与 Q007 用户的 palm grip + 前臂手腕都靠桌面的场景直接相关。但他给的解决方案是"用满鼠标垫空间/调灵敏度"，不是"切换发力肌肉"。

#### B5. Salzi（2024/2/3）——"smooth/clean aim 对一致性很重要"
> **来源**：Woohoojin2 - 副本 (4).md:819，Salzi，2024/2/3 15:02
>
> "As someone who is a very good aimer in Valorant aswell as specifically in aimtrainers, I can tell you that **smooth/clean aim is much better for consistency**... I can also give you decent aimtraining playlists (if you dont already use ones from Voltaic or aimerz) that will make you imrpove your smooth aim a lot more."

#### B6. Holmster [AIM]（2024/3/8）——"你缺乏流畅性，有点硬（stiff）"
> **来源**：Woohoojin2 - 副本 (4).md:429，Holmster [AIM]，2024/3/8 15:46
>
> "One main thing I noticed is you lack fluidity. **You seem a little stiff when playing the game, and I think I can attribute that to three things.** 1. Your FPS. With more FPS, and potentially a 144hz monitor, the game feels much more smooth and fluid... 2. Your peeking. You do not seem to feel comfortable when peeking angles... 3. You lack awareness."

**对 Q007 的意义**：Holmster 用了 "stiff" 这个词，但他的归因是 FPS/显示器/peek 技巧/awareness——**没有归因到肌肉**。这再次说明：复盘者观察到了"硬"，但语言体系里不往肌肉方向想。

---

### 主题 C：手臂/手腕/支点——数据集中仅有的两处解剖学讨论

#### C1. KittFoonya（2023/9/6）——"以肘为轴转动时，鼠标自然会上下飘"
> **来源**：Woohoojin2 - 副本 (5).md:972，KittFoonya，2023/9/6 07:44
>
> "Also I noticed that when you turn (especially if you turn really wide, like more than 90deg) your crosshair moves up/down a significant amount... **It's hard to do because if your arm rotates about your elbow then the mouse will naturally move up/down a little bit depending on how far you translate it side to side, but if you try to really focus on keeping your turns smooth and always leaving your crosshair at head level then your flicks will be more consistent** and it will feel much less cumbersome to turn because you will naturally keep your crosshair at the right height and only have to focus deliberately on aiming horizontally."

**对 Q007 的意义**：这是数据集中**唯一一处**真正讨论手臂支点（肘）与鼠标轨迹关系的地方。KittFoonya 指出：以肘为轴左右旋转时，准星会自然上下飘——这是 palm grip/前臂贴桌用户做大角度转身时的经典问题。但他的解决方案是"刻意保持准星在头高"，不是"换支点/调张力"。

#### C2. LongNameMan（2023/5/29）——"只用手腕瞄"作为负面诊断
> 见 B4 原文。

**数据集中未找到的**：
- forearm on desk / wrist rest / 抬腕
- 椅子/桌子高度
- 握法（palm/claw/hybrid）的优劣讨论
- 握鼠力度（grip force）
- co-contraction（协同收缩）
- 桌面支撑点调整建议

---

### 主题 D：灵敏度 / 鼠标空间 / "microadjust 不了"的归因

#### D1. 副本(8).md:835——"edpi 太高导致无法微调"
> **来源**：Woohoojin2 - 副本 (8).md:835（复盘者未署名，在长回复列表中）
>
> "You do not poses the control over your aim that is required for higher leveled play. **This is probably due to your very high edpi, as it makes it neigh impossible to mircoadjust to enemies that you over/underaim.** I highly recommend you decrease your sense to a managable level."

#### D2. LongNameMan（2023/5/30）——"远距离微调困难 = 过度依赖flick"
> **来源**：Woohoojin2 - 副本 (6).md:273，LongNameMan [ARC]，2023/5/30 21:02
>
> "Other than that you have trouble with micro-adjustments in long range fights and pre-aiming into walls when moving around **which both seem to be symptoms of you over relying on your insane flicks as opposed to using your crosshair placement**."

#### D3. Namu（2025/4/3）——推荐 VT x WHJ Smooth Strafe Sphere Easy 减少抖动
> **来源**：Woohoojin2 - 副本 (2).md:256，Namu，2025/4/3 16:46
>
> "While moving, you have often your crosshair in walls, requiring you to make bigger flicks if someone peeks on this timing (2:41-2:49 is biggest example, **your aim is very jittery and often end up in the wrong place), working on smoothing it** (be more precise on your horizontal placement, less in walls, and if you do the voltaic playlist, **the VT x WHJ Smooth Strafe Sphere Easy is nice to reduce vertical jitter**)"

---

### 主题 E：开枪前"确认准星在头上"——target confirmation 的反复强调

数据集中有**大量**复盘强调"开枪前确认准星在头上"，这本质上就是"微调到位再扣扳机"的纪律：

- Holmster [AIM]（副本(4).md:459）："You tend to shoot well before you are ready. Meaning, either your crosshair is not on their head yet, or you have not stopped moving yet."
- OsOsOsOs（副本(4).md:375）："You shoot way too fast. take a second to make sure you are on the head."
- starmouse（副本(4).md:301）："dont shoot til u are on the head"
- frosty（副本(3).md:922）："you lack a sense of target confirmation... do not shoot unless you firmly believe your crosshair is on their head"
- Dannew（副本(4).md:477）：见 A1
- Scaff [PKR]（副本(8).md:816）："try to be more patient and actually shoot when you are on their heads... you can also just track their head for 2sec while straffing and then try to shoot when they are stopped"

**对 Q007 的意义**：这些复盘全部在说"慢一点、确认了再开枪"，但没有一条说"慢下来的同时要卸张力/松握"。他们默认"慢"是心理纪律问题，不是肌肉状态问题。

---

## 三、追加场景：蹲拉 peek 预瞄偏差后的大角度修正

### 场景描述（用户问题反向版）
蹲着拉peek出去→预瞄了一个角度→发现敌人位置偏很多→想快速大flick甩过去→**卡住挪不动**。
这是从"静止保持预瞄（等长收缩/静态张力）"切换到"大肌肉爆发flick"，静态张力切不到动态爆发。

### E1. 数据集中关于 crouch peek 的讨论——全部是"何时蹲"，无力学讨论

| 说话人 | 日期 | 文件:行 | 原文要点 |
|---|---|---|---|
| Zabil [GUP] | 2024/10/25 | 副本(3).md:215 | "crouch peeking can be really broken"（短评，未展开） |
| frostyLZ | 2024/10/25 | 副本(3).md:219 | "im working on not crouching everytime i peek but only like a definite on angle in a corner where im not exposed to anything else"（蹲只用于死角） |
| Namu | 2025/4/3 | 副本(2).md:256 | "Be careful on crouching... you crouch despite not even being in a fight reinforces the pattern"（乱蹲是坏习惯） |
| veronicaLZ | 2023/9/6 | 副本(5).md:1053 | "you crouch after hitting a bullet not just after missing a few shots"（蹲应该在命中后，不是miss后） |
| xavour [MATH] | 2023/3/26 | 副本(8).md:226 | "try not to crouch peek in situations like that, instead just run n gun"（某些局面别蹲拉） |
| StupidBot | 2023/8/25 | 副本(5).md:1087 | "You are slow peeking, crouch peeking, and diagonal peeking constantly. It is very inconsistent."（peek 方式混乱） |
| ExiledLZ | 2023/10/11 | 副本(5).md:710 | "i see Jing do where he crouch peeks into the fight, but usually after 2-3 shots he stands and does some more crouching"（职业选手 Jing 的节奏：蹲拉→站起→再蹲） |
| brotski [AVFG] | 2023/3/29 | 副本(7).md:957 | "If they crouch peek you, you will still be on body"（对OP手：瞄准胃部，敌人蹲了仍在身上） |
| Supersteve1233 | 2025/5/18 | 精华提取:161 | "instead of a crouch commit swing"（批评蹲完直接commit swing） |
| BanditLZ | 2023/2/18 | 副本(8).md:901 | "I struggle with long range fights & panic shots when I just started crouching... especially when enemy crouches, or are somewhere below my crosshair (I can't adjust for some reason)"（用户自述：敌人蹲着/在准星下方时我调整不过来） |

**关键观察**：以上所有讨论都在"什么时候该蹲、蹲了以后怎么打"的层面，**没有一条**讨论"蹲姿本身如何改变手臂支点/张力/瞄准力学"。

### E2. 预瞄偏差 → 大flick修正的讨论

#### E2a. Vex_DK（2025/3/28）——预瞄距离决定修正量是micro-flick还是大flick
> **来源**：Woohoojin2 - 副本 (2).md:264
>
> "Your crosshair is way too close to the wall. If you hold an angle your crosshair should be further from the corner... **If you put your crosshair in the blue spot, if they under swing your crosshair its should be a easy micro flick for you**, and if they swing past your crosshair its not as far from it... **Also your crosshair movement is super choppy here.**"

**对 Q007 反向场景的意义**：Vex_DK 指出，预瞄位置离墙角远一点，敌人peek出来时你只需要"easy micro flick"；预瞄贴墙，敌人under-swing你就要大flick。这是**用预瞄位置来预防大角度修正**——数据集中没有教"大flick怎么做不卡"，而是教"怎么避免需要大flick"。

#### E2b. _anterior（2024/8/2）——预瞄要给反应时间留余量
> **来源**：Woohoojin2 - 副本 (3).md:747
>
> "Crosshair placement sticks out to me the most, it can be better with the vertical level youre aiming and **it also needs to be a bit further to accomodate for your reaction time.**"

#### E2c. Mang Tomas（2024/3/24）——"贴近墙peek要wide swing，边走边把准星摆到头高"
> **来源**：Woohoojin2 - 副本 (4).md:191
>
> "stop peeking too close to the wall. If you are going to peek close to the wall, **peek wide and don't stop until you aim your crosshair on the head while on the move.**"

**对 Q007 反向场景的意义**：Mang Tomas 的建议是"边走边把准星摆到头高，不要停"——这与 Q006 Dannew 的"减速中完成瞄准"一脉相承。**数据集中反复出现的解决方案是：不要在静止状态下完成大flick，要在移动中/减速中把准星带到位**。

#### E2d. Rone（2024/1/31）——"我打赌你在comp里peek到人会僵住（freeze up）"
> **来源**：Woohoojin2 - 副本 (4).md:959，Rone，2024/1/31 14:01
>
> "**i bet you freeze up after peeking someone in comp**"

**对 Q007 反向场景的意义**：这是数据集中唯一一条直接用"freeze up"描述 peek 后状态的话。但 Rone 说的是**心理僵住**（comp 紧张），不是肌肉僵住。不过"peek 到人后 freeze up"这个现象描述，与用户"蹲拉peek发现敌人偏很多，想甩过去但卡住"的主观感受高度相似——区别只在于归因（心理 vs 肌肉）。

#### E2e. starmouse（2024/3/14）——"别慌，慌了就打不准"
> **来源**：Woohoojin2 - 副本 (4).md:301
>
> "try not to panic! **okay when you take your time you can hit your shots but when you panic you mess up your aim.**"

### E3. 从"架枪保持"到"突然需要flick"的切换

数据集中**没有**专门讨论"架枪（hold angle）→ 突然flick"这个切换。相关的零散观察：

- Holmster（副本(4).md:467）："When playing dm, you want to be in a permanent state of expecting the re-fragger. Always expect another enemy to be coming around the next corner."（心理上保持准备状态）
- vlad?（副本(2).md:210）："strafing is a game of chicken almost, the one who stops first will be less accurate... strafing is mostly tracking in order to keep your crosshair on the enemys head"（对枪中保持移动/追踪）
- Mang Tomas（副本(4).md:191）："If you are actually holding an angle, try to always be mobile and strafe in intervals (not spamming ADADAD but A, wait, D, wait, A, wait, D) it keeps you focused an enemy swinging"（架枪时不要完全静止，要有间隔地微动）

**关键观察**：数据集中的建议是"架枪时不要完全静止（isometric hold），要有节奏地微动"——这间接说明**完全静止架枪是有害的**，但没有人从"静态张力切换不到动态爆发"的角度解释为什么。

---

## 四、确实未找到的主题（明确标注，不要编造）

以下主题在 12 个 Discord 原始文件中**确实没有找到**任何相关讨论：

1. **握法（grip style）**：palm grip / claw grip / fingertip grip / hybrid grip——0 命中
2. **握鼠力度（grip force / clench）**：0 命中
3. **肌肉张力（muscle tension / co-contraction / tension release）**：作为肌肉术语 0 命中
4. **桌面支撑（forearm on desk / wrist rest / elbow on desk）**：作为人体工学话题 0 命中（"elbow"全部是地图拐角）
5. **桌椅高度 / 坐姿 / 支点调整**：0 命中
6. **"从大肌肉发力切换到小肌肉发力"的任何描述**：0 命中
7. **"平滑追踪结束后卸张力"的任何建议**：0 命中
8. **抬腕（wrist lift）/ 腕部支点**：0 命中
9. **三指捏鼠 / 手指激活法**：0 命中（这是 Q004.2 从 Reddit/B站找来的，Discord 数据里没有）
10. **crouch peek 对瞄准力学/支点/张力的影响**：0 命中（所有 crouch 讨论都是决策层）
11. **"静止架枪后大flick卡"的肌肉层面解释**：0 命中（只有心理层面"freeze up/panic"）
12. **co-contraction、isometric hold、isometric-to-dynamic transition 等运动学术语**：0 命中

---

## 五、对 Q007 的可执行启示（从 Discord 数据能提炼什么）

虽然 Discord 数据没有肌肉张力层的讨论，但以下几条是复盘者反复给出、且与 Q007 症状相关的可执行建议：

1. **不要在静止状态下完成大flick，要在移动/减速中把准星带到位**（Dannew / Mang Tomas / Vex_DK）
   - 这与 Q007 反向场景（蹲拉静止→大flick卡住）直接相关：数据集会教你"边走边瞄"，而不是"停住再甩"。

2. **差一点没对齐时，优先用身体移动（strafe/deadzone）代替手微调**（vlad? / _anterior / LongNameMan）
   - 这与 Q007 正向场景（平滑追踪后微调卡住）直接相关：手卡住时，挪步子。

3. **flick 后要留"减速→确认→再开火"的时间窗，不要 flick 完立刻click**（Dannew 帧级分析 / Your Internet / OsOsOsOs）
   - 这给"微调"留了 >100ms 的有意识时间，但数据集中没有教这段时间里手该怎么做。

4. **预瞄离墙角远一点，让敌人peek出来时只需要 micro-flick 而不是大flick**（Vex_DK / _anterior）
   - 这是"预防大角度修正"的方案，间接减少"大flick卡住"的发生频率。

5. **架枪时不要完全静止，要有间隔地 A/D 微动**（Mang Tomas）
   - 间接保持手臂处于"动态准备"状态，避免完全等长收缩。

6. **练 smooth aim / 减少 jitter 的具体曲目**：VT x WHJ Smooth Strafe Sphere Easy（Namu 推荐）；Voltaic/aimerz playlist（Salzi 推荐）；WHJ intermediate drill（_anterior 推荐）。
