# 02-API设计文档

## 1. 概述

本文档定义前后端通信契约，基于模块 1 的数据查询函数，设计 RESTful API 接口，供前端调用。

**基础信息**：
- 后端框架：FastAPI
- 基础路径：`/api`
- 数据格式：JSON
- 认证方式：无（本地工具，不需要认证）
- 跨域：允许前端开发服务器（localhost:5173）跨域访问

---

## 2. 接口总览

| 接口 | 方法 | 路径 | 说明 |
| --- | --- | --- | --- |
| 清单列表 | GET | `/api/daylists` | 获取所有清单列表 |
| 清单元数据 | GET | `/api/daylists/{daylist}` | 获取某个清单的元数据 |
| 清单行列表 | GET | `/api/daylists/{daylist}/rows` | 获取某个清单的所有行 |
| 完成度面板数据 | GET | `/api/daylists/{daylist}/progress` | 获取完成度面板的完整数据 |
| 场景成绩 | GET | `/api/scenarios/{scenario}/score` | 获取某个场景在某段时间的最佳成绩 |
| 场景轮数 | GET | `/api/scenarios/{scenario}/rounds` | 获取某个场景在某段时间的打靶轮数 |
| 场景历史 | GET | `/api/scenarios/{scenario}/history` | 获取某个场景的历史成绩趋势 |
| 场景感悟 | GET | `/api/scenarios/{scenario}/reflections` | 获取某个场景的所有历史感悟 |
| 场景基准数据 | GET | `/api/scenarios/{scenario}/bench` | 获取某个场景的基准数据 |
| 感悟弹窗数据 | GET | `/api/scenarios/{scenario}/popup` | 获取感悟弹窗的完整数据 |

---

## 3. 接口详细设计

### 3.1 清单列表

**GET** `/api/daylists`

**说明**：获取所有清单列表，用于前端下拉选择。

**请求参数**：无

**返回格式**：
```json
{
  "code": 0,
  "data": [
    {
      "daylist": "Day3",
      "label": "攻Fingertip",
      "run_date": "2026-09-21"
    },
    {
      "daylist": "Day2",
      "label": "推Ermine",
      "run_date": "2026-09-19"
    }
  ]
}
```

**错误码**：
- `0`：成功
- `500`：服务器内部错误

---

### 3.2 清单元数据

**GET** `/api/daylists/{daylist}`

**说明**：获取某个清单的元数据，包括时间范围、场景数、总轮数等。

**路径参数**：
- `daylist`：清单名（如 `Day3`）

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "daylist": "Day3",
    "label": "攻Fingertip",
    "run_date": "2026-09-21",
    "exec_dates": "[\"2026-09-21\"]",
    "start_ts": 1789920000,
    "end_ts": 1790006399,
    "items": 9,
    "rounds_total": 32
  }
}
```

---

### 3.3 清单行列表

**GET** `/api/daylists/{daylist}/rows`

**说明**：获取某个清单的所有行，包括场景名、角色、轮数等。

**路径参数**：
- `daylist`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": [
    {
      "daylist": "Day3",
      "label": "攻Fingertip",
      "run_date": "2026-09-21",
      "order": 1,
      "scenario": "1w2ts reload smallflicks larger",
      "role": "热身",
      "rounds": 2,
      "target_score": null,
      "target_acc": null
    }
  ]
}
```

---

### 3.4 完成度面板数据

**GET** `/api/daylists/{daylist}/progress`

**说明**：获取完成度面板的完整数据，前端直接用来渲染表格。

**路径参数**：
- `daylist`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "daylist": "Day3",
    "label": "攻Fingertip",
    "run_date": "2026-09-21",
    "items": 9,
    "rounds_total": 32,
    "rows": [
      {
        "order": 1,
        "scenario": "1w2ts reload smallflicks larger",
        "role": "热身",
        "required_rounds": 2,
        "done_rounds": 4,
        "status": "已完成"
      }
    ]
  }
}
```

**字段说明**：
- `required_rounds`：要求轮数
- `done_rounds`：已打轮数
- `status`：状态（`未开始 / 进行中 / 已完成`）

---

### 3.5 场景成绩

**GET** `/api/scenarios/{scenario}/score`

**说明**：获取某个场景在某段时间的最佳成绩。

**路径参数**：
- `scenario`：场景名（URL 编码）

**查询参数**：
- `start_ts`：开始时间戳（Unix 秒）
- `end_ts`：结束时间戳（Unix 秒）
- `list`：清单名（默认 `viscose-s2-easier`）

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "scenario": "Popcorn MV Easier",
    "score": 160.0,
    "accuracy": 52.0
  }
}
```

---

### 3.6 场景轮数

**GET** `/api/scenarios/{scenario}/rounds`

**说明**：获取某个场景在某段时间的打靶轮数。

**路径参数**：
- `scenario`：场景名

**查询参数**：
- `start_ts`：开始时间戳
- `end_ts`：结束时间戳
- `list`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "scenario": "Popcorn MV Easier",
    "rounds": 9
  }
}
```

---

### 3.7 场景历史

**GET** `/api/scenarios/{scenario}/history`

**说明**：获取某个场景的历史成绩趋势，用于画折线图。

**路径参数**：
- `scenario`：场景名

**查询参数**：
- `days`：天数（默认 30）
- `list`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": [
    {
      "time": "2026-09-16T10:43:35Z",
      "score": 100.0
    }
  ]
}
```

---

### 3.8 场景感悟

**GET** `/api/scenarios/{scenario}/reflections`

**说明**：获取某个场景的所有历史感悟，按日期倒序。

**路径参数**：
- `scenario`：场景名

**查询参数**：
- `days`：天数（默认 30）

**返回格式**：
```json
{
  "code": 0,
  "data": [
    {
      "date": "2026-09-20T16:00:00Z",
      "note": "要顺着轨迹，找到重合同步的时候确认点击..."
    }
  ]
}
```

---

### 3.9 场景基准数据

**GET** `/api/scenarios/{scenario}/bench`

**说明**：获取某个场景的基准数据，包括下一档线、档位等。

**路径参数**：
- `scenario`：场景名

**查询参数**：
- `list`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "scenario": "Popcorn MV Easier",
    "nextLine": 200.0,
    "pct": 33.3,
    "gapPct": 7.7,
    "achIdx": 2,
    "rank": "Hare",
    "sub": "Reading",
    "subRank": "Ermine"
  }
}
```

---

### 3.10 感悟弹窗数据

**GET** `/api/scenarios/{scenario}/popup`

**说明**：获取感悟弹窗的完整数据，前端直接用来渲染弹窗。

**路径参数**：
- `scenario`：场景名

**查询参数**：
- `start_ts`：开始时间戳
- `end_ts`：结束时间戳
- `list`：清单名

**返回格式**：
```json
{
  "code": 0,
  "data": {
    "scenario": "Popcorn MV Easier",
    "today_score": {
      "score": 160.0,
      "accuracy": 52.0
    },
    "bench": {
      "nextLine": 200.0,
      "rank": "Hare"
    },
    "reflections": [
      {
        "date": "2026-09-20T16:00:00Z",
        "note": "要顺着轨迹，找到重合同步的时候确认点击..."
      }
    ]
  }
}
```

---

## 4. 通用响应格式

所有接口都返回统一的格式：

```json
{
  "code": 0,        // 0=成功，非0=错误码
  "message": "",    // 错误信息（成功时为空）
  "data": {}       // 数据
}
```

---

## 5. 错误码约定

| 错误码 | 说明 |
| --- | --- |
| 0 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 6. CORS 配置

允许前端开发服务器跨域访问：
- 允许来源：`http://localhost:5173`
- 允许方法：`GET, POST, PUT, DELETE, OPTIONS`
- 允许头：`*`

---

## 7. 待确认问题

1. 场景名作为路径参数，需要 URL 编码，前端需要注意吗？
2. 是否需要缓存？比如清单元数据可以缓存 1 分钟？
3. 感悟弹窗数据是否需要按日期过滤？比如只返回最近 3 天的？
