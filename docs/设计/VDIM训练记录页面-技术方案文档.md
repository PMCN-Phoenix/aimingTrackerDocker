# VDIM 训练记录页面 - 技术方案文档

> 版本：v1.0
> 创建日期：2026-10-08
> 状态：待实现
> 技术栈：FastAPI + React 19 + Ant Design 6 + InfluxDB

---

## 一、概述

### 1.1 目标
为用户提供 VDIM（Voltaic Daily Improvement Method）训练的记录、追踪和进度可视化页面。

### 1.2 核心功能（MVP）
1. **训练日管理**：Day1-Day6 循环，每天一个主题，自动对应"今天练什么"
2. **分数记录**：自动从 Kovaak's stats 导入 + 手动补录，按训练日 Day 归类
3. **训练打卡**：连续打卡天数、本周完成率
4. **训练感悟**：复用现有感悟系统，加 tag 区分（vdim / viscose）
5. **顶部概览卡片**：今天练什么、连续打卡、本周完成率、Gold Complete 进度

### 1.3 第二版功能（预留）
- 6 大主题进步曲线
- Gold Complete 进度可视化
- 基准测试对比（起点→第2次→第4次）
- 历史记录页面（/vdim/history）

### 1.4 VDIM 训练循环（用户定制顺序）
| Day | 主题 | 分享码（S4旧版/LG56） | 场景数 |
| --- | --- | --- | --- |
| Day1 | 平滑跟枪 (Smooth Tracking) | `KovaaKsStrikingAfkBm` | 16 |
| Day2 | 反应跟枪 (Reactive Tracking) | `KovaaKsSwitchingAfkSeason` | 15 |
| Day3 | 速度转火 (Speed Switching) | `KovaaKsTaggingAlmightyHip` | 12 |
| Day4 | 移动瞄准/自由 (Movement) | `KovaaKsTimewarpingAngelicAttachment` | 15 |
| Day5 | 动态点击 (Dynamic Clicking) | `KovaaKsStarting10xLoadout` | 16 |
| Day6 | 静态点击 (Static Clicking) | `KovaaKsStrafingAcedDps` | 17 |
| Day7 | 休息 | - | - |

**开始日期**：2026-10-09（周五）= 第1周 Day1
**总计**：91 个场景

---

## 二、技术栈

### 2.1 后端
| 层 | 技术 | 说明 |
| --- | --- | --- |
| 框架 | FastAPI | 和现有项目一致 |
| 数据库 | InfluxDB | 时序数据存储 |
| 数据访问 | 自定义 queries.py + influx_client.py | 复用现有 |
| 模型 | Pydantic BaseModel | 请求/响应校验 |
| 静态文件 | FastAPI StaticFiles | 生产模式服务前端 dist |

### 2.2 前端
| 层 | 技术 | 说明 |
| --- | --- | --- |
| 框架 | React 19 + Vite 8 | 和现有项目一致 |
| UI 组件库 | Ant Design 6.x | 主要 UI |
| 状态管理 | Zustand | 全局状态 |
| 数据请求 | @tanstack/react-query | 服务端状态 |
| 路由 | react-router-dom 7 | 页面路由 |
| 图表 | ECharts 6 + echarts-for-react | 第二版进步曲线 |
| 日期 | dayjs | 日期处理 |

### 2.3 数据存储
| 存储 | 用途 |
| --- | --- |
| InfluxDB | 时序数据（vdim_score、vdim_training_log、aim_reflection） |
| JSON 配置文件 | vdim_playlists.json（场景配置） |
| Markdown 文件 | 感悟双写备份（复用现有 game_reflection_markdown） |

---

## 三、数据结构设计

### 3.1 InfluxDB Measurement: vdim_score

VDIM 训练分数，每个场景每次训练一条记录。

```
measurement: vdim_score

tags:
  - cycle: int          # 第几周（1, 2, 3...）
  - day: string         # 训练日（Day1, Day2, ..., Day6）
  - theme: string       # 主题（smooth, reactive, speed, movement, dynamic, static）
  - scenario: string    # 场景名
  - scenario_type: string  # 场景类型（benchmark=基准场景, training=训练场景）
  - source: string      # 数据来源（auto=stats自动导入, manual=手动补录）

fields:
  - score: float        # 分数
  - accuracy: float     # 准确率（可选，0-100）
  - timestamp: int      # 训练时间戳（UTC 秒）
  - date: string        # 训练日期（YYYY-MM-DD，北京时间）
```

**查询示例**：
- 获取某周期某天的所有场景最新分数：`SELECT last(score) FROM vdim_score WHERE cycle=1 AND day='Day1' GROUP BY scenario`
- 获取某场景的历史最高：`SELECT max(score) FROM vdim_score WHERE scenario='Controlsphere'`
- 获取某场景的训练次数：`SELECT count(score) FROM vdim_score WHERE scenario='Controlsphere'`

### 3.2 InfluxDB Measurement: vdim_training_log

训练打卡记录，每天一条。

```
measurement: vdim_training_log

tags:
  - date: string        # 日期（YYYY-MM-DD，北京时间）
  - cycle: int          # 第几周
  - day: string         # 训练日（Day1-Day7）
  - theme: string       # 主题（Day7 为 rest）

fields:
  - checked_in: bool    # 是否打卡
  - checkin_time: int   # 打卡时间戳
  - scenarios_done: int # 完成的场景数
  - scenarios_total: int # 总场景数
  - note: string        # 备注（可选）
```

### 3.3 aim_reflection 扩展（复用现有）

现有 aim_reflection measurement 增加 tag 区分来源。

```
measurement: aim_reflection（现有，扩展 tags）

tags（新增）:
  - type: string        # 感悟类型（vdim / viscose / game）
  - vdim_cycle: int     # VDIM 周期（仅 type=vdim 时有）
  - vdim_day: string    # VDIM 训练日（仅 type=vdim 时有）
  - vdim_theme: string  # VDIM 主题（仅 type=vdim 时有）

fields（现有，不变）:
  - scenario: string    # 场景名
  - note: string        # 感悟内容
  - date: string        # 日期
  - timestamp: int      # 时间戳
```

**注意**：现有 aim_reflection 已经有 scenario、note、date 等字段，新增 type tag 即可区分。查询 VDIM 感悟时加 `WHERE type='vdim'` 过滤。

### 3.4 配置文件: vdim_playlists.json

已创建，路径：`web/backend/app/config/vdim_playlists.json`

```json
{
  "start_date": "2026-10-09",
  "days": [
    {
      "day": "Day1",
      "theme": "smooth",
      "theme_label": "平滑跟枪",
      "share_code": "KovaaKsStrikingAfkBm",
      "scenarios": [
        {
          "order": 1,
          "scenario_name": "Controlsphere",
          "scenario_type": "benchmark"
        },
        {
          "order": 2,
          "scenario_name": "Revolving Tracking Slow",
          "scenario_type": "training"
        }
      ]
    }
  ]
}
```

---

## 四、周期计算逻辑

### 4.1 核心函数

```python
from datetime import datetime, timedelta

START_DATE = datetime.strptime("2026-10-09", "%Y-%m-%d")

def get_cycle_and_day(target_date: datetime) -> tuple[int, str]:
    """
    根据日期计算是第几周第几天。
    
    返回: (cycle, day)
    - cycle: 第几周（从1开始）
    - day: Day1, Day2, ..., Day7
    """
    delta_days = (target_date.date() - START_DATE.date()).days
    cycle = delta_days // 7 + 1
    day_index = delta_days % 7  # 0-6
    day = f"Day{day_index + 1}"
    return cycle, day

def get_date_range_for_cycle_day(cycle: int, day: str) -> tuple[datetime, datetime]:
    """
    获取某周期某天的日期范围（当天 00:00:00 到 23:59:59，北京时间）。
    用于查询当天的训练分数。
    """
    day_index = int(day.replace("Day", "")) - 1  # 0-6
    target_date = START_DATE + timedelta(days=(cycle - 1) * 7 + day_index)
    start = target_date.replace(hour=0, minute=0, second=0)
    end = target_date.replace(hour=23, minute=59, second=59)
    return start, end
```

### 4.2 时间戳转换注意事项
- Python 进程时区是北京时间（UTC+8）
- `datetime.timestamp()` 返回的是 UTC 时间戳，InfluxDB 存储的是 UTC 时间
- 查询时用北京时间的 datetime 转 timestamp 即可，不需要手动加减 8 小时

---

## 五、后端 API 设计

### 5.1 API 列表

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/vdim/today` | 获取今天的训练信息（周期、Day、主题、场景列表） |
| GET | `/api/vdim/day/{cycle}/{day}` | 获取某周期某天的完整数据（场景分数+打卡状态） |
| GET | `/api/vdim/overview` | 获取顶部概览卡片数据（连续打卡、本周完成率、Gold进度） |
| POST | `/api/vdim/checkin` | 训练打卡 |
| POST | `/api/vdim/score` | 手动补录分数 |
| POST | `/api/vdim/import` | 从 Kovaak's stats 导入分数 |
| GET | `/api/vdim/playlists` | 获取 VDIM playlist 配置（场景列表） |
| GET | `/api/vdim/scenario/{scenario}/history` | 获取某场景的历史分数（第二版曲线用） |

### 5.2 详细 API 设计

#### GET /api/vdim/today
获取今天的训练信息。

**响应**：
```json
{
  "code": 0,
  "data": {
    "date": "2026-10-09",
    "cycle": 1,
    "day": "Day1",
    "theme": "smooth",
    "theme_label": "平滑跟枪",
    "share_code": "KovaaKsStrikingAfkBm",
    "checked_in": false,
    "scenarios_total": 16,
    "scenarios_done": 0
  }
}
```

#### GET /api/vdim/day/{cycle}/{day}
获取某周期某天的完整数据。

**路径参数**：
- `cycle`: int，第几周
- `day`: string，Day1-Day6

**响应**：
```json
{
  "code": 0,
  "data": {
    "cycle": 1,
    "day": "Day1",
    "theme": "smooth",
    "theme_label": "平滑跟枪",
    "share_code": "KovaaKsStrikingAfkBm",
    "date": "2026-10-09",
    "checked_in": false,
    "checkin_time": null,
    "benchmark_scenarios": [
      {
        "order": 1,
        "scenario": "Controlsphere",
        "scenario_type": "benchmark",
        "latest_score": null,
        "best_score": null,
        "train_count": 0,
        "rank": null,
        "next_rank": "Ermine",
        "gap": 461,
        "status": "未开始"
      }
    ],
    "training_scenarios": [
      {
        "order": 2,
        "scenario": "Revolving Tracking Slow",
        "scenario_type": "training",
        "latest_score": null,
        "best_score": null,
        "train_count": 0,
        "status": "未开始"
      }
    ]
  }
}
```

**状态判断逻辑**：
- `train_count == 0` → "未开始"
- `train_count > 0` → "已完成"（VDIM 不要求固定轮数，打过就算完成）

#### GET /api/vdim/overview
获取顶部概览卡片数据。

**响应**：
```json
{
  "code": 0,
  "data": {
    "today": {
      "cycle": 1,
      "day": "Day1",
      "theme_label": "平滑跟枪",
      "share_code": "KovaaKsStrikingAfkBm"
    },
    "streak_days": 0,
    "streak_label": "今天还没练",
    "week_done": 0,
    "week_total": 6,
    "week_percent": 0,
    "gold_complete": 10,
    "gold_total": 12,
    "gold_percent": 83,
    "gold_missing": ["Wrist", "Reading"]
  }
}
```

**连续打卡计算逻辑**：
- 从今天往前数，连续有 checked_in=true 的天数
- 如果今天没打卡，streak 从昨天开始算（不中断）
- 如果今天打卡了，streak 包含今天

**本周完成率计算逻辑**：
- 当前周期内，Day1-Day6 中 checked_in=true 的天数 / 6
- Day7（休息）不计入

#### POST /api/vdim/checkin
训练打卡。

**请求体**：
```json
{
  "date": "2026-10-09",
  "note": "今天状态不错"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "date": "2026-10-09",
    "cycle": 1,
    "day": "Day1",
    "checked_in": true,
    "checkin_time": 1728470400
  }
}
```

**逻辑**：
1. 根据 date 计算 cycle 和 day
2. 写入 vdim_training_log（checked_in=true, checkin_time=当前时间戳）
3. 如果同一天已经打卡，更新 checkin_time（不重复创建）

#### POST /api/vdim/score
手动补录分数。

**请求体**：
```json
{
  "cycle": 1,
  "day": "Day1",
  "scenario": "Controlsphere",
  "score": 8500,
  "accuracy": 85.5,
  "date": "2026-10-09"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "cycle": 1,
    "day": "Day1",
    "scenario": "Controlsphere",
    "score": 8500,
    "source": "manual"
  }
}
```

**逻辑**：
1. 从 vdim_playlists.json 获取 scenario_type（benchmark/training）和 theme
2. 写入 vdim_score（source=manual）
3. timestamp 用 date 的 20:00:00（手动补录默认晚上训练时间）

#### POST /api/vdim/import
从 Kovaak's stats 目录导入分数。

**请求体**：
```json
{
  "cycle": 1,
  "day": "Day1",
  "date": "2026-10-09"
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "imported": 5,
    "skipped": 0,
    "scenarios": [
      {"scenario": "Controlsphere", "score": 8500},
      {"scenario": "Smoothsphere", "score": 9372}
    ]
  }
}
```

**逻辑**：
1. 获取该 day 的场景列表（从 vdim_playlists.json）
2. 扫描 Kovaak's stats 目录中 date 当天的 stats 文件
3. 匹配场景名（忽略大小写、忽略版本后缀如 " v2"）
4. 取每个场景当天的最佳分数
5. 写入 vdim_score（source=auto）
6. 返回导入结果

**stats 文件解析**：复用现有 `queries.py` 中的 stats 解析逻辑（Kovaak's stats 是 CSV 格式，第一行是表头，包含 Score、Accuracy 等字段）。

#### GET /api/vdim/playlists
获取 VDIM playlist 配置。

**响应**：
```json
{
  "code": 0,
  "data": {
    "start_date": "2026-10-09",
    "days": [
      {
        "day": "Day1",
        "theme": "smooth",
        "theme_label": "平滑跟枪",
        "share_code": "KovaaKsStrikingAfkBm",
        "scenarios": [...]
      }
    ]
  }
}
```

#### GET /api/vdim/scenario/{scenario}/history
获取某场景的历史分数（第二版进步曲线用）。

**查询参数**：
- `days`: int，最近多少天，默认 30

**响应**：
```json
{
  "code": 0,
  "data": {
    "scenario": "Controlsphere",
    "history": [
      {"date": "2026-10-09", "score": 8500},
      {"date": "2026-10-16", "score": 8700}
    ]
  }
}
```

---

## 六、前端组件设计

### 6.1 页面路由
- `/vdim` - VDIM 训练主页（默认显示今天对应的训练日）

### 6.2 组件结构

```
VdimDashboard (页面主组件)
├── VdimFilterBar (过滤器栏：周期选择 + 训练日选择 + 日期范围 + 刷新)
├── VdimOverviewCards (顶部概览卡片：4个)
│   ├── TodayCard (今天练什么)
│   ├── StreakCard (连续打卡)
│   ├── WeekProgressCard (本周完成率)
│   └── GoldProgressCard (Gold Complete 进度)
├── VdimDayDetail (训练日详情卡片)
├── VdimActionBar (操作栏：打卡 + 导入 + 补录 + 写感悟)
├── VdimScenarioTable (场景表格，分两组)
│   ├── BenchmarkScenarioTable (基准场景表，有档位对比)
│   └── TrainingScenarioTable (训练场景表，只有分数)
├── VdimRelatedLinks (相关页面跳转：基准总览 + 感悟 + Viscose清单)
└── VdimVersion2Placeholder (第二版预留占位)
```

### 6.3 关键组件说明

#### VdimFilterBar
- 周期选择：Select，选项动态生成（第1周、第2周...，根据当前日期计算最大周期）
- 训练日选择：Select，Day1-Day7
- 日期范围：RangePicker（可选，用于自定义查询）
- 刷新按钮
- 右侧显示当前选中的周期+Day+主题

#### VdimOverviewCards
- 4 个 Card，一行排列（Row + Col span=6）
- 数据来自 `/api/vdim/overview`
- 用 react-query 缓存

#### VdimDayDetail
- 显示当前训练日的主题、分享码、场景数
- 分享码可复制（CopyOutlined 按钮）
- 显示推荐 FOV、灵敏度（从配置读取）

#### VdimActionBar
- 打卡按钮（主按钮，CheckCircleOutlined）
- 从 stats 导入按钮（ImportOutlined）
- 手动补录按钮（EditOutlined）→ 打开 Modal
- 写感悟按钮（FileTextOutlined）→ 打开 Modal（复用现有感悟表单）

#### VdimScenarioTable
- 分两个 Table：基准场景 + 训练场景
- 基准场景列：顺序、场景名、分类、子类、最新分数、档位、下一档位、差距、状态
- 训练场景列：顺序、场景名、最新分数、历史最高、训练次数、状态
- 场景名可点击 → 打开场景详情弹窗（复用现有 ScenarioPopup）

#### 补录 Modal
- 表单：场景选择（Select，从该 day 的场景列表）、分数（InputNumber）、准确率（InputNumber，可选）、日期（DatePicker）
- 提交调用 `/api/vdim/score`

### 6.4 导航栏
在 App.jsx 的导航栏菜单中加「VDIM训练」项，路由 `/vdim`。

---

## 七、开发计划（模块划分）

按照 AGENTS.md 的 Web 版开发流程：写文档 → 实现 → 四重验证 → 集成测试。

### 模块1：VDIM 页面设计文档 ✅ 已完成
- 产品设计文档
- 技术方案文档（本文档）
- vdim_playlists.json 配置

### 模块2：VDIM 后端 API
**目标**：实现所有 8 个 API 端点，数据可读写。

**子任务**：
1. 在 `queries.py` 中新增 VDIM 相关查询函数
   - `get_vdim_today()`
   - `get_vdim_day(cycle, day)`
   - `get_vdim_overview()`
   - `create_vdim_checkin(date, note)`
   - `create_vdim_score(cycle, day, scenario, score, accuracy, date, source)`
   - `import_vdim_scores_from_stats(cycle, day, date)`
   - `get_vdim_playlists()`
   - `get_vdim_scenario_history(scenario, days)`
2. 在 `main.py` 中新增 8 个 API 路由
3. 周期计算工具函数（可放在 queries.py 或新建 utils.py）

**验收标准**：
- 所有 API 返回正确的 JSON 格式
- InfluxDB 读写正常
- 周期计算正确（第1周 Day1 = 2026-10-09）

### 模块3：VDIM 前端页面
**目标**：实现 /vdim 页面，所有 MVP 功能可用。

**子任务**：
1. 新建 `src/pages/VdimDashboard.jsx`
2. 新建子组件（可放在 `src/components/vdim/` 目录）
   - `VdimFilterBar.jsx`
   - `VdimOverviewCards.jsx`
   - `VdimDayDetail.jsx`
   - `VdimActionBar.jsx`
   - `VdimScenarioTable.jsx`
   - `VdimRelatedLinks.jsx`
3. 修改 `App.jsx`：加路由 + 导航栏菜单项
4. 新建 `src/api/vdim.js`：API 调用封装
5. 补录 Modal、感悟 Modal（复用现有）

**验收标准**：
- 页面正常渲染，无 JS 错误
- 周期选择、训练日选择正常切换
- 概览卡片数据正确显示
- 场景表格分两组显示
- 打卡、导入、补录功能可用
- 和现有页面风格一致（Ant Design）

### 模块4：四重验证
按照 AGENTS.md 的四重验证流程：

1. **单元检验**：单个数据点/接口是否正确
   - 测试每个 API 端点的返回格式
   - 测试周期计算函数（边界情况：第1周第1天、第1周第7天、第2周第1天）
   - 测试 InfluxDB 写入和查询

2. **交叉检验**：格式/协议是否正确
   - API 返回的 JSON 格式和前端期望一致
   - InfluxDB 的 tags/fields 和设计一致
   - 前端组件的 props 传递正确

3. **代码检验**：逻辑是否正确（边界情况、异常处理）
   - 打卡重复调用的处理（同一天多次打卡）
   - 导入时场景名不匹配的处理
   - 补录时分数为负数的校验
   - 日期超出范围的处理
   - 异常情况的错误返回（不崩溃）

4. **端到端检验**：实际效果是否正确
   - 浏览器打开 /vdim 页面，确认渲染正常
   - 测试完整流程：选择周期+Day → 查看场景 → 打卡 → 导入分数 → 补录分数 → 写感悟
   - 和 Grafana/Viscose 页面对比数据一致性
   - 导航栏跳转正常

### 模块5：集成测试
- VDIM 页面和现有页面的集成（导航栏跳转、感悟系统共用、基准数据共用）
- 生产模式打包测试（npm run build + FastAPI 静态文件服务）
- 多清单支持测试（VDIM 和 Viscose 数据互不干扰）

---

## 八、四重验证详细计划

### 8.1 单元检验清单

| 编号 | 检验项 | 方法 | 预期结果 |
| --- | --- | --- | --- |
| U1 | 周期计算：2026-10-09 | 调用 get_cycle_and_day | (1, "Day1") |
| U2 | 周期计算：2026-10-15 | 调用 get_cycle_and_day | (1, "Day7") |
| U3 | 周期计算：2026-10-16 | 调用 get_cycle_and_day | (2, "Day1") |
| U4 | 周期计算：2026-10-08（开始前一天） | 调用 get_cycle_and_day | (0, "Day7") 或异常处理 |
| U5 | 日期范围：第1周 Day1 | 调用 get_date_range_for_cycle_day | 2026-10-09 00:00:00 ~ 23:59:59 |
| U6 | API: GET /api/vdim/today | curl 调用 | 返回正确的 cycle/day/theme |
| U7 | API: GET /api/vdim/day/1/Day1 | curl 调用 | 返回场景列表，分 benchmark/training 两组 |
| U8 | API: POST /api/vdim/checkin | curl 调用 | 写入 vdim_training_log，返回 checked_in=true |
| U9 | API: POST /api/vdim/score | curl 调用 | 写入 vdim_score，返回 score |
| U10 | API: GET /api/vdim/overview | curl 调用 | 返回 streak/week/gold 数据 |

### 8.2 交叉检验清单

| 编号 | 检验项 | 方法 | 预期结果 |
| --- | --- | --- | --- |
| C1 | API 响应格式 | 检查所有 API 返回 | 统一 ApiResponse 格式（code/message/data） |
| C2 | InfluxDB tags | 写入后查询 | cycle/day/theme/scenario/scenario_type/source 都正确 |
| C3 | 前端 props 传递 | 代码审查 | 父组件传给子组件的 props 名称和类型一致 |
| C4 | 场景名匹配 | 导入测试 | stats 文件名和 vdim_playlists.json 中的场景名能匹配 |
| C5 | 感悟 tag | 写 VDIM 感悟后查询 | type=vdim, vdim_cycle, vdim_day, vdim_theme 正确 |

### 8.3 代码检验清单

| 编号 | 检验项 | 方法 | 预期结果 |
| --- | --- | --- | --- |
| L1 | 重复打卡 | 同一天调用两次 checkin | 不重复创建，更新 checkin_time |
| L2 | 场景名不匹配 | 导入时 stats 中有不在列表的场景 | 跳过，记录 skipped，不崩溃 |
| L3 | 分数校验 | 补录负数分数 | 返回错误，不写入 |
| L4 | 日期超出范围 | 查询第100周 Day1 | 返回空数据，不崩溃 |
| L5 | 异常处理 | InfluxDB 连接失败 | API 返回 code=500，不崩溃 |
| L6 | 空数据处理 | 新周期无数据时 | 场景列表显示，分数为 null，状态"未开始" |
| L7 | Day7 休息 | 查询 Day7 | 返回休息提示，无场景列表 |

### 8.4 端到端检验清单

| 编号 | 检验项 | 方法 | 预期结果 |
| --- | --- | --- | --- |
| E1 | 页面渲染 | 浏览器打开 /vdim | 页面正常显示，无控制台错误 |
| E2 | 周期切换 | 选择第2周 | 场景列表刷新，日期显示正确 |
| E3 | 训练日切换 | 选择 Day2 | 主题变为反应跟枪，场景列表更新 |
| E4 | 打卡流程 | 点击打卡按钮 | 打卡成功，概览卡片 streak 更新 |
| E5 | 导入流程 | 点击从 stats 导入 | 导入成功，场景分数更新 |
| E6 | 补录流程 | 点击手动补录，填写表单 | 补录成功，场景分数更新 |
| E7 | 感悟流程 | 点击写感悟，填写内容 | 感悟写入，感悟页面可查 |
| E8 | 导航跳转 | 点击导航栏其他页面 | 正常跳转，返回 VDIM 状态保留 |
| E9 | 数据一致性 | 对比 VDIM 页面和 Viscose 页面的基准场景分数 | 一致 |
| E10 | 生产模式 | npm run build + 启动 FastAPI | 页面正常访问，API 正常 |

---

## 九、风险和注意事项

### 9.1 风险
1. **stats 文件名和场景名不匹配**：Kovaak's stats 文件名可能包含版本号、特殊字符，需要做模糊匹配
2. **InfluxDB 时序查询性能**：vdim_score 数据量增长后，查询历史最高和训练次数可能变慢，需要考虑聚合查询
3. **周期计算边界**：开始日期之前的日期、跨年夜等特殊情况需要测试
4. **Ant Design 6.x 兼容性**：部分组件 API 可能和 5.x 不同，需要参考现有页面的用法

### 9.2 注意事项
1. **时间戳**：所有时间戳用 UTC 秒，InfluxDB 存储 UTC，显示时转北京时间
2. **场景名匹配**：导入时忽略大小写、忽略首尾空格、忽略 " v2" 等版本后缀
3. **数据隔离**：vdim_score 和 kovaak_score 分开存储，互不干扰
4. **感悟复用**：aim_reflection 加 type tag，不新建 measurement
5. **配置驱动**：场景列表从 vdim_playlists.json 读取，不硬编码
6. **AGENTS.md 规则**：每次改动后 git commit、编写测试、按流程执行

---

## 十、第二版可优化内容（记录，不实现）

1. **6 大主题进步曲线**：用 ECharts 展示每个主题的平均分数随时间变化
2. **Gold Complete 进度可视化**：12 个子类的档位进度环形图
3. **基准测试对比**：起点→第2次→第4次基准测试的分数对比表
4. **历史记录页面**：/vdim/history，按日期列表展示所有训练记录
5. **训练提醒**：集成定时任务，每天提醒训练
6. **数据导出**：导出 VDIM 训练数据为 CSV/Excel
7. **分享功能**：生成训练进度分享图

---

**文档结束**
