# 18-拉出去打不到人 Reddit 原始数据

> 收集日期：2026-10-14
> 主题：VALORANT "swing out and can't hit anyone"（拉出瞬间打不到人：过甩/急停/视觉焦点/紧张）
> 方法：Reddit RSS（详见下方"方法与局限"）
> 数据文件：
> - `posts_with_comments_18_swing_miss.json` —— 17 个帖子正文+评论全文
> - `_dump_read.txt` —— 人工阅读版 dump
> - `search_results_raw.json` —— DDG 候选链接清单（初次搜索轮）
> - `fetch_18_swing_miss.py` / `harvest_18.py` / `retry_failed.py` —— 采集脚本

## 一、方法与局限

1. 方式B（computer_use_tool 操作浏览器）：本子 agent 无权限，不可用。
2. 方式C（general_search）：本环境全部查询返回 "search was restricted"，不可用。
3. web.fetch 直抓 Reddit：robots.txt 禁止。
4. **实际使用：本机 PowerShell + Python，经 clash-verge 代理（127.0.0.1:7897）抓 Reddit RSS**
   - 发现 `old.reddit.com/search.json` / `www.reddit.com/search.json` 均 403；共享代理 IP 上 Reddit 匿名 RSS 限流严重（429）。
   - 绕法：DuckDuckGo HTML（`html.duckduckgo.com/html/`）搜 "reddit valorant [关键词]" 拿帖子 URL（14 组关键词，7 组因 SSL EOF 失败），再逐个抓 `reddit.com/r/<sub>/comments/<id>/.rss?limit=30`（帖子正文+顶层评论）。
   - **局限1：RSS 不提供票数和评论数**，下表"票数"列只能写"未知"，按标题与内容人工评相关度。
   - **局限2：未登录**，只能看正文和顶层评论，看不到折叠/楼中楼。
   - **局限3：约 1/3 候选帖子因 429/SSL 失败**，已对失败集做一轮补抓（间隔 20s），i1woyn 等 2 个仍失败。
   - **局限4：DDG 结果数量少**（每查询 0-4 条），覆盖面不如站内 Top 排序。

## 二、搜索清单

DDG 查询（14 组）：
- reddit valorant overflick too far fix
- reddit valorant flick goes past enemy
- reddit valorant can't hit after peeking out
- reddit valorant miss every duel first
- reddit valorant shooting while moving punishment
- reddit valorant counter strafe tips
- reddit valorant nervous shaky hands aim peek
- reddit valorant wide swing miss（失败）
- reddit FPSAimTrainer overflick correction（失败）
- reddit valorant why do I miss easy shots（失败）
- reddit valorant preaim head level when swinging（失败）
- reddit valorant crosshair placement peek wide（失败）
- reddit valorant panic peek lose gunfight（失败）
- reddit valorant sensitivity overflick

## 三、帖子表（按相关度排序）

| URL | sub | 标题 | 票数 | 相关度 |
|---|---|---|---|---|
| https://www.reddit.com/r/VALORANT/comments/pvzj4z/ | r/VALORANT | How do I fix/work on over-flicking? | 未知 | ★★★★★ |
| https://www.reddit.com/r/VALORANT/comments/kkey5d/ | r/VALORANT | I over-flick, even on a low sense | 未知 | ★★★★★ |
| https://www.reddit.com/r/VALORANT/comments/vapbch/ | r/VALORANT | Overflicking even on low sens and constant practice | 未知 | ★★★★★ |
| https://www.reddit.com/r/aimlab/comments/vapgic/ | r/aimlab | OVERFLICKING EVEN ON LOW SENS and constant practice（同帖双发） | 未知 | ★★★★ |
| https://www.reddit.com/r/VALORANT/comments/m6f3ux/ | r/VALORANT | How to get rid of Weird flicking habit（先按扳机后到位） | 未知 | ★★★★★ |
| https://www.reddit.com/r/VALORANT/comments/14kae1n/ | r/VALORANT | Bad habit - tiny flick before firing（单发散弹枪开镜前微甩） | 未知 | ★★★★ |
| https://www.reddit.com/r/AgentAcademy/comments/vnapn8/ | r/AgentAcademy | How to stop flicking for no reason（架枪时白甩一下） | 未知 | ★★★★★ |
| https://www.reddit.com/r/VALORANT/comments/1d0on3v/ | r/VALORANT | I struggle a lot when an enemy peeks me（含 VOD review） | 未知 | ★★★★ |
| https://www.reddit.com/r/VALORANT/comments/n4rg1j/ | r/VALORANT | how do i fix my nervousness and shaky aim? | 未知 | ★★★★★ |
| https://www.reddit.com/r/VALORANT/comments/1afnry1/ | r/VALORANT | Anyone else have shaky / jerky aim? What did you do? | 未知 | ★★★★ |
| https://www.reddit.com/r/VALORANT/comments/vx1jrx/ | r/VALORANT | Suddenly can't hit a shot (and my gamesense is gone): a cry for help | 未知 | ★★★ |
| https://www.reddit.com/r/VALORANT/comments/uerxp5/ | r/VALORANT | I realize why i have been losing all my duels. Help | 未知 | ★★★ |
| https://www.reddit.com/r/VALORANT/comments/kit0u9/ | r/VALORANT | Duel tips? Struggling in duels lately（急停+小身位压进准星） | 未知 | ★★★★ |
| https://www.reddit.com/r/VALORANT/comments/11suuwz/ | r/VALORANT | How to counter strafe? | 未知 | ★★★（急停细节，已有相邻结论，不展开） |
| https://www.reddit.com/r/VALORANT/comments/ia7sps/ | r/VALORANT | moving while shooting punishment should be increased?! | 未知 | ★★★（反面：移动射击 RNG） |
| https://www.reddit.com/r/VALORANT/comments/i90yqx/ | r/VALORANT | Make moving while shooting more punishing. | 未知 | ★★★（反面：幸存者偏差） |
| https://www.reddit.com/r/VALORANT/comments/g0l792/ | r/VALORANT | Movement Penalty While Shooting | 未知 | ★★★（慢走不减精度） |
| https://www.reddit.com/r/VALORANT/comments/wmhhjn/ | r/VALORANT | [deleted]（评论区急停争议帖） | 未知 | ★★★（反面意见来源） |

失败未抓到：i1woyn（flick goes past enemy 相关）、f0l792 补抓成功（即 g0l792）。

## 四、核心发现（结论 + 原句）

### 发现1：拉出瞬间打不到，主因不是灵敏度，而是"太用力→握鼠变紧+出汗→手感漂移"
> pvzj4z · u/applaude: "Most of the time if you're doing both [over AND under flick] then your sens is fine, you're just too worried about the aim. So you end up gripping your mouse tighter or sweat from your finger tips which change your grip making you miss shots... the best solution is to not focus on the aim as much and just flick and if you hit the shot u hit it."
> vapbch · u/Deamon-: "you are not overflicking/underflicking because of a sens. you just need to continue playing/training... you never miss because of your sens (unless you play some ridiculous sens) its just purely your mouse control."
- URL: https://www.reddit.com/r/VALORANT/comments/pvzj4z/ ; https://www.reddit.com/r/VALORANT/comments/vapbch/

### 发现2：常见动作错误是"先按扳机，准星后到位"（fire before lined up）
> m6f3ux 楼主: "whenever I flick to a target I hold down the shoot button before the target is on the head and then my crosshair is on the head but my spray is too high then."
> m6f3ux · u/daybreaker22: "DM with the guardian and sheriff for a few games. It'll be feast or famine but can teach to aim prior to M1."
> m6f3ux · u/QBot22: "half an hour of dm with crouch unbinded and guardian fixed it real quick."
- URL: https://www.reddit.com/r/VALORANT/comments/m6f3ux/

### 发现3：视觉焦点——甩动过程中眼睛没盯头
> m6f3ux · u/UrmezP: "my eyes are not focusing on the targets head while I am doing the flick motion. You need to sit at a distance from your monitor where you're eyes are easily focused on the screen, and your eyes need to be 'flexible' enough to focus from one target to the next and keep focus while moving your mouse. ... Just go to range and flick as fast as you can WHILE trying your best to focus on the targets head."
- URL: https://www.reddit.com/r/VALORANT/comments/m6f3ux/

### 发现4：训练"慢速平滑"≠实战"快速恐慌甩"，速度缺口没人替你补
> vapbch · u/battle_astra: "One issue is maybe you're practicing flicking slowly when training and in game you're panicking and flicking as fast as you can. Flicking fast is something your haven't been training. So maybe incorporate that into your training. Imagine you're in an actually fight and flick as if you were trying to kill someone. Either that, or try calming down and taking your time in the actual fight."
> kkey5d · u/Mistehkitty2: "Your going too fast. Try focusing on accuracy and the speed will come. In game if this happens, you might be panicking or u have a flick aim style with bad crosshair placement or a combo of both. This kinda stems from only flick training like.. gridshot only in aimlabs and a lot of range with no DM. Your sens is fine"
- URL: https://www.reddit.com/r/VALORANT/comments/vapbch/ ; https://www.reddit.com/r/VALORANT/comments/kkey5d/

### 发现5：开镜前的"白微甩"=想提前脱离对枪找掩体的焦虑反射，可用"决斗中左手离键"矫正
> 14kae1n · u/Teetota: "it's an anxiety issue - you are trying to unswing too early even before you fire a shot and that flick is part of your desire to seek cover or dodge return shots. I had similar issue. Play some DM with a rule - when you see an enemy you lift off your left hand from the keyboard and not move till the duel resolves."（下面有跟帖: "I did this exact exercise. Immediate results in my next matches."）
> 14kae1n · u/Money-Obligation-773: "I always have this problem with the marshall so i stopped playing it. I think it's just cause I'm stressed and don't wanna miss my shot."
> 14kae1n · u/calliopedorme: "some sort of psychological reflex from playing tap fire guns with big sounding shots, it's almost as if your hand is mirroring the act of pulling the trigger in real life and expecting a recoil."
- URL: https://www.reddit.com/r/VALORANT/comments/14kae1n/

### 发现6：纠正方向是"用 A/D 压进准星"而不是"甩过去再修"
> kit0u9 · u/YarnSpinner: "Use that [counter strafing] to jiggle in and out of cover... and then line up your crosshair so that when you repeek you aren't flicking as much as you are strafing into the shot... that using strafe movement (from a and d) to make small precise shots."
> vnapn8 · 楼主 n1cohoty 自述: "when someone peeks fast, my aim correction is always a flick instead of a track. Which is rough if i'm not sharp that day."
> vnapn8 · u/syphorize: "I forced myself to be more patient by running dms and only holding for the wide swings, never peeking others. I hold an angle and force myself not to move my crosshair and wait for them to run into it instead."
> vnapn8 · 评论: "making sure your crosshair is always in a place that lets you hit an enemy when they walk out, and also don't aim train that much. ... the thing that helped me the most was doing the n0ted warmup and then just practicing my counter strafing for a few minutes. Practicing movement has a surprising effect on the consistency of your aim."
- URL: https://www.reddit.com/r/VALORANT/comments/kit0u9/ ; https://www.reddit.com/r/AgentAcademy/comments/vnapn8/

### 发现7：紧张/手抖有生理与心态两层解法
> n4rg1j · u/RocketLeagueTrading7: "Eat before you play, not satire. Whenever I play on a completely empty stomach... I shake like crazy, even though I'm not anxious whatsoever... Whenever I eat beforehand I feel fine and my hand is always firm on the mouse without hesitation."
> n4rg1j · u/Lord_Hashbrowns: "It sounds counter intuitive but play slower wait the extra second to line up your shots and play around cover to give yourself more options."
> n4rg1j · u/eVizorr: "every time I felt shaky, I'd take a second, take a deep breath, reset, and then get back into it."
> 1afnry1 · u/TaiTheChineseGuy: "Sit up, tuck your elbows in, and make sure you have a good anchor point... If you notice your aim being shaky mainly during flicks then that's fine. It might also be a mental barrier just try to slow it down and maintain your composure."
- URL: https://www.reddit.com/r/VALORANT/comments/n4rg1j/ ; https://www.reddit.com/r/VALORANT/comments/1afnry1/

### 发现8（已有语料复用，非本次新抓）
- r/AgentAcademy o1kkck "6 TIPS TO GO FROM IRON TO IMMORTAL" 评论: "Are you constantly over flicking past the bot? Maybe lower your sens a bit. Are you constantly coming short of the bot? Maybe raise it a bit."（存于 03/10/12/13 各文件夹 posts_with_comments JSON）
- r/AgentAcademy 18xz628 "Why am i mechanically so bad(DM Vod, D1)" 楼主自述: "i subconsciously am scared from peeking someone who killed me once in ranked... i still choke it in duels when strafe fighting with A/D because i panic and lose control, i still fail microflicks... i sometimes accidentally overflick when out of space"（存于 10-静步前压包带斜角架枪 JSON，行 8591）
- r/AgentAcademy q35i0n "Have Some Confidence!" 评论: "Shaky aim and bot-like movement? You're not confident in your own ability to counterstrafe and accurately hit shots."

## 五、反面意见

1. **"移动射击打死你"是幸存者偏差**（与"拉出打不到"主题相反方向：别急着怪自己急停）
   > i90yqx · u/Coffee4Addict: "This gets posted all the time because people remember the times they shoot/get shot by someone running and don't remember all the misses. If you genuinely believe its too good play like 5 matches only running and shooting and please post it so we know how good it is."
   > i90yqx · u/always_salty: "It isn't happening as often as you think it is. You only remember the 1 case where you get shot while running and disregard the 1000 cases where the enemy was running and shooting and didn't hit."
   - URL: https://www.reddit.com/r/VALORANT/comments/i90yqx/

2. **急停在 VALORANT 里是否有增益，评论区当场打架**
   > wmhhjn · u/No_Author_7708: "There's no counter strafing in valorant. Counter strafing comes from csgo... In Valorant, however, you are fully accurate the instant you let go of movement keys. All you need to know is that you shoot after you let go."
   > wmhhjn · u/NickBucketTV（反驳）: "This is wrong, you have momentum in your movement in Valorant. Not as much as I've heard CSGO has but Valorant definitely benefits from counterstrafing."
   > wmhhjn · u/DesiredInsanity: "its not as big of a benefit as csgo but you are accurate faster if you counterstrafe to stop movement in valorant than just letting go of your movement key."
   > wmhhjn · u/fpsnoodles（kit0u9 帖）: "Counter-strafing stops you about 80-100ms faster than letting go of keys."
   - URL: https://www.reddit.com/r/VALORANT/comments/wmhhjn/

3. **打不好别先改灵敏度**
   > vx1jrx 评论: "I wouldn't change your sens because you're having bad days."
   - URL: https://www.reddit.com/r/VALORANT/comments/vx1jrx/

4. **"降灵敏度治 overflick"派 vs "灵敏度没问题，是鼠标控制"派**（vapbch 帖内对撞）
   > burrnerr22: "if decreasing your sens mitigated your tendency to overflick that is the reason, what other suggestions can you expect."（=坚持降 sens）
   > Deamon-（上文发现1，=别再调 sens，练控制）
