# 多渠道调研标准SOP（四渠道全覆盖）

> 目的：每次实战问题调研必须覆盖 B站 + YouTube + Reddit + Discord 四个渠道，不得遗漏。
> 创建日期：2026-10-12
> 适用：Q005对局复盘及所有后续实战问题调研

---

## 一、四渠道分工与优先级

| 渠道 | 信息类型 | 获取方式 | 限制 | 优先级 |
|---|---|---|---|---|
| **B站** | 中文教学视频、UP主复盘、靶场训练法 | Python脚本搜索+抓字幕（已自动化） | 评论抓取会被风控 | ★★★★★ 主力 |
| **YouTube** | 英文深度教学、职业选手分析、瞄准理论 | yt-dlp抓字幕+通用搜索 | 需要代理+Cookie | ★★★★★ 主力 |
| **Reddit** | 真实玩家经验、个人记录帖、评论区高玩建议 | 浏览器登录态读取 / 用户贴链接 / general_search间接搜 | 必须登录，web.fetch被拦 | ★★★★ 重要补充 |
| **Discord** | 社区固定资源文档、实时问答、教练反馈 | #resources频道固定文档（用户贴链接） | 必须登录，无公开搜索API | ★★★ 按需 |

---

## 二、标准调研流程（每次必须走完）

### 第1步：B站（必做，已自动化）
- 9组关键词搜索（3个主题方向×3组关键词）
- 去重后加权打分，精选12-15个视频
- 抓字幕（AI字幕优先，无字幕的标记跳过）
- 评论抓取（限速，风控则跳过并记录）
- 输出：搜索结果JSON + 精选列表JSON + 字幕文件

### 第2步：YouTube（必做）
- 英文关键词搜索（general_search + YouTube站内搜索）
- 精选5-10个视频
- 用yt-dlp抓字幕（需要Cookie+代理）
- 输出：字幕文件 + 关键引用

### 第3步：Reddit（必做，三选一）
**方式A：用户贴链接（最可靠）**
- 你在Reddit搜到相关帖子，把链接贴给我
- 我用浏览器登录态读取完整内容+评论

**方式B：Edge浏览器自动搜索（已验证可行，2026-10-12）**
- 我用computer_use_tool操作Edge浏览器（plane="cu"）
- 直接导航到搜索URL：`https://www.reddit.com/r/VALORANT/search/?q=[关键词]&sort=top&t=all`
- 按Top of all time排序，读取前5-10个帖子的标题和票数
- 精选1-3个高票帖子双击打开，读取正文+滚动看评论区
- **注意**：r/VALORANT比r/VALORANTCompetitive更适合个人技巧搜索（后者偏比赛讨论）
- **未登录也能看**：帖子正文和大部分评论可见，只是右上角显示"登录"按钮
- **已验证的搜索词**："1v1 clutch tips how to win"、"how to peek when enemy holding angle behind cover"
- **典型产出**：3040票的Peeking Guide（4种peek类型详解）、166票的"知道对方架角度怎么peek"（1038赞评论：对方蹲下时预瞄身体）

**方式C：general_search间接搜（兜底）**
- 搜"reddit valorant [关键词]"
- 从搜索结果摘要中提取有用信息
- 局限性：只能看到摘要，看不到评论区

**Reddit搜索关键词模板**：
```
r/VALORANT: [问题关键词] tips how to improve
r/VALORANT: how to [具体动作] when [场景]
r/FPSAimTrainer: [瞄准相关关键词]
按 Top of all time 排序
```

### 第4步：Discord（必做，用户配合获取）

**加入的3个核心服务器**：
| 服务器 | 邀请链接 | 主要价值 |
|---|---|---|
| Voltaic | discord.gg/voltaic | 瞄准训练routine、#resources固定文档 |
| Woohoojin | discord.gg/woohoojin | 无畏契约职业教练，VOD review、残局分析 |
| r/VALORANT官方 | discord.gg/valorant | 最大社区，#guides、#gameplay-discussion |

**用户获取内容的方式**：
1. **方式A（最简单）**：看到有用消息直接复制文本贴给我
2. **方式B（带上下文）**：右键消息→"复制消息链接"→贴给我
3. **方式C（批量）**：截图有用的讨论，我OCR识别

**搜索方法**：
- Discord内按Ctrl+F或点右上角搜索图标
- 关键词："1v1"、"clutch"、"how to peek"、"enemy holding angle"
- 按"热门"排序看高赞回复

**重点频道**：
- Voltaic: #resources（固定文档）、#general、#vod-review
- Woohoojin: #resources、#vod-review、#advice
- r/VALORANT: #guides、#gameplay-discussion、#clips

**重点关注内容类型**：
- 教练/高玩的具体建议（不是"多练"）
- 个人复盘帖（"我这个1v1输了哪里错了"+教练回复）
- #resources固定文档
- 争议讨论（两种观点对立，看高赞回复）

---

## 三、各渠道调研检查清单

每次调研结束前，逐项确认：

- [ ] B站：搜索完成、精选完成、字幕抓取完成、覆盖率报告
- [ ] YouTube：搜索完成、精选完成、字幕抓取或摘要提取
- [ ] Reddit：至少用了方式A/B/C中的一种，记录了获取方式和局限
- [ ] Discord：检查了已知资源文档，或请用户提供了相关频道内容
- [ ] 整合报告：四个渠道的发现交叉验证，标注每个结论的来源渠道
- [ ] 反面意见：每个渠道至少找1条与主流结论不同的观点

---

## 四、Reddit和Discord的用户配合事项

### Reddit需要你做的
1. 确保浏览器已登录Reddit（我可以用浏览器工具读取）
2. 或者你搜到好帖子直接把链接贴给我
3. 重点关注：个人记录帖（Progress/Journey/8 weeks）、高赞评论区的具体建议

### Discord需要你做的
1. 加入Voltaic和Woohoojin的Discord
2. 在#resources频道找到相关文档，把内容复制贴给我
3. 或者在对应频道提问，把回复贴给我

---

## 五、已验证的技术限制

1. **Reddit web.fetch**：未登录状态返回登录页，无法直接抓取
2. **Reddit搜索API**：需要OAuth认证，未配置
3. **Discord**：无公开搜索API，必须通过用户手动获取内容
4. **B站评论**：连续抓取会被风控（返回非JSON），字幕不受影响
5. **YouTube字幕**：需要Cookie+代理，yt-dlp可用

---

## 六、渠道间的交叉验证原则

- **B站+YouTube一致**：可信度高，可作为核心结论
- **B站说A，YouTube说B**：列出两种观点，分析适用场景差异
- **Reddit评论区高玩说C**：作为补充视角，标注"社区经验"
- **Discord官方文档说D**：作为权威参考，标注"社区官方资源"
- **只有一个渠道提到**：标注"单一来源，待验证"

---

## 七、后续改进方向

1. 配置Reddit API OAuth，实现自动搜索+抓取
2. 建立Discord资源文档本地库，定期更新
3. 对每个实战问题，建立"四渠道发现对照表"
