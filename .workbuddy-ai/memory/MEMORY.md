# aim-tracker-docker · 项目长期记忆

> 日志：`D:/11.project/iwen-codex/codex-list/aim-tracker-docker/.workbuddy/memory/YYYY-MM-DD.md`（追加式，每天一份）。
> 本文件只放跨会话有效的长期事实。最后更新：2026-10-29。

## 当前目标状态（Viscose S2 → Seal，切 5 块 G1–G5 串行推进）

- **G1（Ermine→Puffin）进行中：1 真过（C）/ 2 假过（A、D）/ 1 硬缺口（B）**
- 四卡口线：A `Plink Palace Easy Less Blinks` 2175 ｜ B `Air Pure Easier No UFO` 919（专项目标 = 6 轮均值 921，当前 909.5）｜ C `Pasu Voltaic Reload Easier` 52 ｜ D `VT Floating Heads Viscose Easier` 580
- 判定规则（2026-10-29 改版）：同日 ≥2 轮 = 真过；恰好 1 轮 = 假过；连续两次假过 = 降级不过；**单格过 = 两个不同训练日各一次真过**；缺口÷SD<1 的线只能靠采样
- **下一步**：T=10-31（六）打游戏内 playlist「G1 收关v2 - 避开头尾废轮」（10 轮，已部署）→ 用户发「打完了」+日期 → 跑 `docs/清单/目标卡/_g1_state.py` 判定；T+2 复打锁 A/C/D；T+4/6/8 B 单独 6 轮（指令：目标反向瞬间主动减速；过冲 73→≤50 发）；≈11-10 关 G1 开 G2 批 1（Pasu +20%/Popcorn +19%/Floating Heads +13%）

## 用户个人配置（锁定，改动即基线作废）

- sens **0.09**（XSens，刻度 = **Valorant** 0.06996）· DPI **3200** → **45.4 cm/360** · FOV **103h**（Overwatch 横向）
- 官方红线：Fingertip 慢于 50cm 无效 → **sens ≥ 0.082**；FOV ≥ 103h。已复核通过（10-29）
- 身体规则：手温 22.9℃（Q023）｜ 隔天训练，收缩日=连续第 2–5 天（Q027）｜ 有效轮位 #4–#8（Q024）｜ 单次 ≤10 轮
- B 的方向 = 变向减速（OverShots 73 发/轮 > 所需提升 50 发），与 Q022 加速带同源

## 文件地图

- **日常执行入口**：`docs/清单/目标卡/G1-四步平铺-完全个性化.md`（零跳转）
- 规则依据：`G1-总档Ermine到Puffin.md` ｜ 总览：`00-Seal切块总图.md` ｜ 分支：`G1-执行方略.md` ｜ 索引：`docs/清单/目标卡/README.md`
- **Viscose S2 唯一阈值来源**：`docs/清单/Viscose基准-原始数据/S2-官方分类诊断.json`；`benches_full.json` 是 Voltaic 主基准，**禁用**
- 阈值漂移监控：关卡确认日 + 全量重测日各 diff 一次 evxl，其余不盯
- 问题库：`docs/问题库/`（Q021 慢握/Q022 卸力/Q024 轮位/Q025 分数=状态闸门/Q027 收缩日/Q028 阶梯合理性）
- 对外简报：`docs/简报/进度简报.md`（AGENTS.md 规则 7：实质产出必须更新）
- 统计 CSV：`D:/1_game/1_steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats`

## 硬规则（每次会话必须遵守）

1. **每次改动双远端备份**：`bash scripts/backup_push.sh "说明"`（Gitee origin + GitHub，三 SHA 一致才算完成，失败必须报告）
2. 每次 git commit；实质产出更新简报 + 当日 memory 日志
3. 灵敏度/FOV 不许再改；G1 判定后按 `docs/清单/目标卡/README.md` §五的固定清单更新文件
4. 问题与产物进 `docs/问题库/QXXX-描述/`，同步更新问题库 README
