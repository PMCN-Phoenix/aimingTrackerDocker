# VDIM 训练记录页面 - 技术设计文档

> 版本：v1.0（MVP）
> 创建日期：2026-10-08
> 状态：设计中

---

## 一、产品概述

### 1.1 目标
为用户提供 VDIM（Voltaic Daily Improvement Method）训练的记录、追踪和进度可视化页面。

### 1.2 核心功能
1. **训练日管理**：Day1-Day6 循环，每天一个主题，自动对应"今天练什么"
2. **分数记录**：自动从 Kovaak's stats 导入 + 手动补录，按训练日 Day 归类
3. **训练打卡**：连续打卡天数、本周完成率
4. **训练感悟**：复用现有感悟系统，加 tag 区分（vdim / viscose）
5. **进度追踪**（第二版）：6 大主题进步曲线、Gold Complete 进度、基准测试对比

### 1.3 VDIM 训练循环（用户定制顺序）
| Day | 主题 | 分享码（S4旧版） | 说明 |
| --- | --- | --- | --- |
| Day1 | 平滑跟枪 (Smooth Tracking) | `KovaaKsStrikingAfkBm` | 用户最弱主题 |
| Day2 | 反应跟枪 (Reactive Tracking) | `KovaaKsSwitchingAfkSeason` | 第二弱主题 |
| Day3 | 速度转火 (Speed Switching) | `KovaaKsTaggingAlmightyHip` | 最均衡主题 |
| Day4 | 移动瞄准/自由 (Movement) | `KovaaKsTimewarpingAngelicAttachment` | 或补弱项 |
| Day5 | 动态点击 (Dynamic Clicking) | `KovaaKsStarting10xLoadout` | - |
| Day6 | 静态点击 (Static Clicking) | `KovaaKsStrafingAcedDps` | - |
| Day7 | 休息 | - | 恢复 |

**开始日期**：2026-10-09（周五）= Day1

---

## 二、页面结构和布局

### 2.1 整体布局
```
┌─────────────────────────────────────────────────────────┐
│  导航栏：首页 | Viscose清单 | 🔥 VDIM训练 | 基准总览 | 感悟  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 顶部概览卡片（一行 4 个）                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ 今天练什么 │ │ 连续打卡  │ │ 本周完成率│ │Gold进度  │ │
│  │ Day1 平滑  │ │ 🔥 N 天  │ │ x/6 y%   │ │10/12 83% │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📅 训练日切换 Tab                                      │
│  [Day1 平滑] [Day2 反应] [Day3 速度] [Day4 移动]     │
│  [Day5 动态] [Day6 静态] [😴 休息]                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  当前训练日详情区                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 🎯 Day1：平滑跟枪 (Smooth Tracking)             │  │
│  │ 分享码：[KovaaKsStrikingAfkBm] [复制]          │  │
│  │ 为什么练：你的最弱主题，Wrist 子类整体 Hare     │  │
│  │ 上次训练：2026-10-09 | 分数：xxx | 感悟：xxx   │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📋 基准场景（有档位对比）                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 场景名          分数   档位   趋势  详情按钮    │  │
│  │ Smoothsphere    9372   Penguin  ↑    [详情]     │  │
│  │ ...                                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  📋 训练场景（只有分数，无档位）                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │ 场景名          分数   历史最高  详情按钮         │  │
│  │ Centering I     1234   1500     [详情]          │  │
│  │ ...                                             │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ✅ 打卡 + 📝 感悟区                                   │
│  [今天练了！打卡]  [手动补录分数]  [写训练感悟]       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📈 底部进度区（第二版，Tab 切换）                      │
│  [6大主题曲线] [Gold Complete进度] [基准测试对比]      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 页面路由
- `/vdim` - VDIM 训练主页（默认显示今天对应的训练日）
- `/vdim/history` - 历史记录页面（第二版）

---

## 三、数据结构设计

### 3.1 InfluxDB Measurements

#### 3.1.1 vdim_score（VDIM 训练分数）
```
measurement: vdim_score
tags:
  - day: Day1 / Day2 / ... / Day6
  - theme: smooth_tracking / reactive_tracking / ...
  - scenario: 场景名
  - scenario_type: benchmark / training （基准场景 / 训练场景）
fields:
  - score: float （分数）
time: 训练实际日期时间
```

**说明**：
- 按训练日 Day 归类（用户选择的补录逻辑）
- scenario_type 区分基准场景（有档位线）和训练场景（只有分数）
- time 是实际训练日期，用于历史记录

#### 3.1.2 vdim_training_log（训练打卡记录）
```
measurement: vdim_training_log
tags:
  - date: 2026-10-09 （实际日期）
  - day: Day1 / Day2 / ... （训练日）
  - theme: smooth_tracking / ...
fields:
  - completed: bool （是否完成）
  - duration_min: int （训练时长，分钟）
  - scenarios_completed: int （完成的场景数）
  - scenarios_total: int （总场景数）
  - note: string （备注，可选）
time: 打卡时间
```

#### 3.1.3 aim_reflection（感悟，复用现有，加 tag）
```
measurement: aim_reflection （已有，扩展）
tags:
  - scenario: 场景名
  - date: 日期
  - type: vdim / viscose / game （新增，区分来源）
  - day: Day1 / Day2 / ... （VDIM 感悟专用，可选）
  - theme: smooth_tracking / ... （VDIM 感悟专用，可选）
fields:
  - reflection: string （感悟内容）
time: 创建时间
```

**说明**：复用现有 aim_reflection measurement，新增 type tag 区分 VDIM / Viscose / 游戏感悟。VDIM 感悟额外加 day 和 theme tag。

### 3.2 配置文件

#### 3.2.1 vdim_playlists.json（VDIM playlist 场景配置）
```json
{
  "start_date": "2026-10-09",
  "days": [
    {
      "day": "Day1",
      "theme": "smooth_tracking",
      "theme_name": "平滑跟枪",
      "share_code": "KovaaKsStrikingAfkBm",
      "description": "你的最弱主题，Wrist 子类整体 Hare",
      "scenarios": [
        {
          "name": "Smoothsphere Viscose Easier",
          "type": "benchmark",
          "category": "Control Tracking",
          "sub": "Arm"
        },
        {
          "name": "Centering I Easy",
          "type": "training"
        }
      ]
    }
  ]
}
```

**说明**：场景列表可配置，S4 旧版场景后面补充，S5 新版可以随时替换。

---

## 四、后端 API 设计

### 4.1 基础信息

- Base URL: `/api/vdim`
- 框架：FastAPI（复用现有后端）
- 数据源：InfluxDB（复用现有 influx_client）

### 4.2 API 列表

#### 4.2.1 获取今天的训练日信息
```
GET /api/vdim/today
Response:
{
  "date": "2026-10-09",
  "day": "Day1",
  "day_number": 1,
  "theme": "smooth_tracking",
  "theme_name": "平滑跟枪",
  "share_code": "KovaaKsStrikingAfkBm",
  "description": "你的最弱主题，Wrist 子类整体 Hare",
  "is_rest_day": false,
  "trained_today": false,
  "streak_days": 0
}
```

**逻辑**：根据 start_date 和当前日期计算是第几天，然后对 7 取模（Day1-Day6 + 休息）。

#### 4.2.2 获取指定训练日详情
```
GET /api/vdim/day/{day}
Query:
  - date: 2026-10-09 （可选，指定查看哪次训练，默认最新）
Response:
{
  "day": "Day1",
  "theme": "smooth_tracking",
  "theme_name": "平滑跟枪",
  "share_code": "KovaaKsStrikingAfkBm",
  "description": "...",
  "benchmark_scenarios": [
    {
      "name": "Smoothsphere Viscose Easier",
      "latest_score": 9372,
      "best_score": 9372,
      "rank": "Penguin",
      "next_rank": "Fox",
      "gap": 828,
      "history_count": 5,
      "last_trained": "2026-10-09"
    }
  ],
  "training_scenarios": [
    {
      "name": "Centering I Easy",
      "latest_score": 1234,
      "best_score": 1500,
      "history_count": 3,
      "last_trained": "2026-10-09"
    }
  ],
  "training_log": {
    "completed": true,
    "duration_min": 65,
    "scenarios_completed": 8,
    "scenarios_total": 10,
    "trained_at": "2026-10-09T20:30:00+08:00"
  },
  "reflections": [
    {
      "id": "...",
      "content": "今天感觉手腕放松了很多",
      "created_at": "2026-10-09T21:00:00+08:00"
    }
  ]
}
```

#### 4.2.3 打卡
```
POST /api/vdim/checkin
Body:
{
  "day": "Day1",
  "duration_min": 65,
  "scenarios_completed": 8,
  "scenarios_total": 10,
  "note": "今天状态不错"
}
Response:
{
  "success": true,
  "streak_days": 1,
  "weekly_completion": "1/6"
}
```

#### 4.2.4 手动录入分数
```
POST /api/vdim/score
Body:
{
  "day": "Day1",
  "scenario": "Smoothsphere Viscose Easier",
  "score": 9372,
  "date": "2026-10-09" （可选，默认今天，用于补录）
}
Response:
{
  "success": true,
  "scenario": "Smoothsphere Viscose Easier",
  "score": 9372,
  "rank": "Penguin"
}
```

#### 4.2.5 批量导入分数（从 stats 文件）
```
POST /api/vdim/import
Body:
{
  "day": "Day1",
  "stats_directory": "D:\\...\\stats", （可选，默认 Kovaak's stats 目录）
  "date": "2026-10-09" （可选，默认今天）
}
Response:
{
  "success": true,
  "imported": 8,
  "skipped": 2,
  "scenarios": [
    {"name": "Smoothsphere Viscose Easier", "score": 9372, "imported": true},
    {"name": "Unknown Scenario", "score": 1234, "imported": false, "reason": "不在 playlist 配置中"}
  ]
}
```

**逻辑**：
1. 读取指定日期的 stats 文件
2. 解析每个文件的场景名和分数
3. 匹配该 Day 的 playlist 配置中的场景
4. 匹配上的写入 vdim_score，匹配不上的跳过并报告

#### 4.2.6 获取概览卡片数据
```
GET /api/vdim/overview
Response:
{
  "today": {
    "day": "Day1",
    "theme_name": "平滑跟枪",
    "share_code": "KovaaKsStrikingAfkBm",
    "trained_today": false
  },
  "streak_days": 0,
  "weekly_completion": {
    "completed": 0,
    "total": 6,
    "percentage": 0
  },
  "gold_complete": {
    "completed": 10,
    "total": 12,
    "percentage": 83,
    "missing_subcategories": ["Wrist", "Reading"]
  }
}
```

#### 4.2.7 获取训练历史（第二版）
```
GET /api/vdim/history
Query:
  - page: 1
  - page_size: 20
  - day: Day1 （可选，按训练日筛选）
  - start_date: 2026-10-01 （可选）
  - end_date: 2026-10-31 （可选）
Response:
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "records": [
    {
      "date": "2026-10-09",
      "day": "Day1",
      "theme_name": "平滑跟枪",
      "completed": true,
      "duration_min": 65,
      "avg_score": 5000,
      "reflection_count": 2
    }
  ]
}
```

#### 4.2.8 感悟 CRUD（复用现有 API，扩展 type 参数）
现有感悟 API 增加 `type=vdim` 参数和 `day` 参数：
```
GET /api/reflections?type=vdim&day=Day1
POST /api/reflections （body 增加 type, day, theme 字段）
PUT /api/reflections/{id}
DELETE /api/reflections/{id}
```

---

## 五、前端组件设计

### 5.1 技术栈
- React + Vite + Tailwind CSS（复用现有前端）
- Ant Design（组件库，用户已选择）
- ECharts（图表，第二版）

### 5.2 组件结构
```
src/
├── pages/
│   └── VDim/
│       ├── index.jsx              # VDIM 主页
│       └── History.jsx            # 历史记录页（第二版）
├── components/
│   └── VDim/
│       ├── OverviewCards.jsx      # 顶部概览卡片（4个）
│       ├── DayTabs.jsx            # 训练日切换 Tab
│       ├── DayDetail.jsx          # 当前训练日详情
│       ├── ScenarioList.jsx        # 场景列表（基准/训练分组）
│       ├── ScenarioCard.jsx        # 单个场景卡片
│       ├── CheckinBar.jsx          # 打卡 + 补录 + 感悟 操作栏
│       ├── ScoreImportModal.jsx    # 分数导入弹窗
│       ├── ManualScoreModal.jsx    # 手动补录弹窗
│       ├── ReflectionModal.jsx     # 写感悟弹窗
│       └── ProgressSection.jsx     # 底部进度区（第二版）
├── services/
│   └── vdimApi.js                  # VDIM API 封装
├── config/
│   └── vdimPlaylists.js            # VDIM playlist 配置（从 JSON 导入）
└── utils/
    └── vdimUtils.js                 # 工具函数（计算训练日、档位等）
```

### 5.3 核心组件说明

#### 5.3.1 OverviewCards（顶部概览卡片）
4 个卡片：
1. **今天练什么**：Day1 平滑跟枪 + 分享码 + 复制按钮
2. **连续打卡**：🔥 N 天 + 今天是否已练
3. **本周完成率**：x/6 + 进度条
4. **Gold 进度**：10/12 + 进度条 + 缺失子类

#### 5.3.2 DayTabs（训练日切换）
- Day1-Day6 + 休息，共 7 个 Tab
- 当前日期对应的 Day 高亮
- 已练的 Day 显示 ✅，未练的显示 ○
- 休息 Day 显示 😴

#### 5.3.3 DayDetail（训练日详情）
- 主题标题 + 分享码 + 复制按钮
- 主题描述（为什么练这个）
- 上次训练信息（日期、分数、感悟摘要）
- 基准场景列表（有档位对比）
- 训练场景列表（只有分数）
- 打卡操作栏

#### 5.3.4 ScenarioCard（场景卡片）
基准场景：
- 场景名 + 最新分数 + 档位标签（颜色区分）
- 下一档位 + 差距
- 趋势箭头（↑↓→）
- 详情按钮（点击展开历史曲线，第二版）

训练场景：
- 场景名 + 最新分数 + 历史最高
- 训练次数
- 详情按钮

#### 5.3.5 CheckinBar（操作栏）
3 个按钮：
1. **今天练了！打卡**：打卡弹窗（填写时长、完成场景数）
2. **手动补录分数**：补录弹窗（选择场景、输入分数、选择日期）
3. **写训练感悟**：感悟弹窗（输入感悟内容）

额外：
- **从 stats 导入**按钮：自动导入今天的分数

---

## 六、开发计划和里程碑

### 模块 1：设计文档 ✅（当前）
- 产品设计讨论
- 技术设计文档
- 数据结构设计
- API 设计

### 模块 2：后端 API
- [ ] vdim_score measurement 写入/查询
- [ ] vdim_training_log measurement 写入/查询
- [ ] aim_reflection 扩展（type=vdim, day, theme）
- [ ] GET /api/vdim/today
- [ ] GET /api/vdim/day/{day}
- [ ] POST /api/vdim/checkin
- [ ] POST /api/vdim/score
- [ ] POST /api/vdim/import
- [ ] GET /api/vdim/overview
- [ ] vdim_playlists.json 配置文件
- [ ] 单元测试

### 模块 3：前端页面
- [ ] 路由配置（/vdim）
- [ ] 导航栏加入口
- [ ] OverviewCards 组件
- [ ] DayTabs 组件
- [ ] DayDetail 组件
- [ ] ScenarioList / ScenarioCard 组件
- [ ] CheckinBar 组件
- [ ] 打卡弹窗
- [ ] 手动补录弹窗
- [ ] 感悟弹窗
- [ ] stats 导入功能
- [ ] 页面联调

### 模块 4：四重验证
- [ ] 单元检验：API 接口单测
- [ ] 交叉检验：数据格式/协议验证
- [ ] 代码检验：边界情况、异常处理
- [ ] 端到端检验：浏览器打开页面，实际操作验证

### 模块 5：集成测试
- [ ] VDIM 页面与 Viscose 页面导航互通
- [ ] 感悟系统共用验证
- [ ] InfluxDB 数据一致性验证
- [ ] 打卡/补录/导入全流程验证

### 第二版可优化内容（记录，不做）
- [ ] 6 大主题进步曲线（ECharts）
- [ ] Gold Complete 进度可视化
- [ ] 基准测试对比（简化版卡片 + 跳转）
- [ ] 历史记录页面（/vdim/history）
- [ ] 场景详情弹窗（历史曲线）
- [ ] 训练提醒/通知
- [ ] 数据导出（CSV/Excel）
- [ ] S5 新版 playlist 场景列表适配
- [ ] 移动端适配

---

## 七、与现有系统的关系

### 7.1 复用的现有功能
- **InfluxDB 连接**：复用 influx_client.py
- **感悟系统**：复用 aim_reflection measurement，扩展 tag
- **基准档位线**：复用 S2-官方分类诊断.json 的档位数据
- **前端组件**：复用 Ant Design 组件、Tailwind 样式
- **导航栏**：在现有导航栏加入口

### 7.2 新增的内容
- **vdim_score measurement**：VDIM 训练分数
- **vdim_training_log measurement**：训练打卡记录
- **vdim_playlists.json 配置**：VDIM playlist 场景配置
- **VDIM 页面**：/vdim 路由和相关组件
- **VDIM API**：/api/vdim/* 接口

### 7.3 数据隔离
- VDIM 分数和 Viscose 分数分开存储（不同 measurement）
- 感悟通过 type tag 区分（vdim / viscose / game）
- 基准测试数据仍用 kovaak_score measurement，VDIM 页面只做简化展示和跳转

---

## 八、风险和注意事项

1. **场景列表不完整**：S4 分享码的场景列表需要后续补充，先做配置化，不影响核心功能
2. **stats 文件自动识别**：VDIM 场景和 Viscose 场景可能有重叠，导入时需要按 Day 的 playlist 配置匹配，避免错配
3. **补录逻辑**：按训练日 Day 归类，实际日期只作参考，查询时需要注意时间范围
4. **感悟系统扩展**：修改现有 aim_reflection 的查询逻辑时，需要兼容旧数据（没有 type tag 的默认按 viscose 处理）
5. **Gold Complete 进度**：依赖 Viscose 基准数据，需要确保基准数据已导入，否则显示为空

---

## 九、参考文档

- VDIM 训练指南：`docs/设计/VDIM训练指南.md`
- VDIM 起点基准：`docs/记录/VDIM起点基准-20261008.md`
- 现有后端代码：`web/backend/app/`
- 现有前端代码：`web/frontend/src/`
- S2 档位线数据：`docs/清单/Viscose基准-原始数据/S2-官方分类诊断.json`
