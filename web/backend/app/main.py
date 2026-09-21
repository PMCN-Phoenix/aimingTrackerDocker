# -*- coding: utf-8 -*-
"""FastAPI 后端主程序"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel

from app.repositories import queries

app = FastAPI(title="练枪看板 API", version="0.1.0")

# CORS 配置：允许前端开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 通用响应模型
class ApiResponse(BaseModel):
    code: int = 0
    message: str = ""
    data: Optional[dict | list] = None


# ==================== 清单接口 ====================

@app.get("/api/daylists", response_model=ApiResponse)
async def get_daylists():
    """获取所有清单列表"""
    try:
        data = queries.get_all_daylists()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/daylists/{daylist}", response_model=ApiResponse)
async def get_daylist_meta(daylist: str):
    """获取某个清单的元数据"""
    try:
        data = queries.get_daylist_meta(daylist)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/daylists/{daylist}/rows", response_model=ApiResponse)
async def get_daylist_rows(daylist: str):
    """获取某个清单的所有行"""
    try:
        data = queries.get_daylist_rows(daylist)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/daylists/{daylist}/progress", response_model=ApiResponse)
async def get_daylist_progress(daylist: str):
    """获取完成度面板的完整数据"""
    try:
        # 1. 查清单行
        rows = queries.get_daylist_rows(daylist)
        if not rows:
            return ApiResponse(code=0, data={"daylist": daylist, "rows": []})

        # 2. 查元数据（获取时间范围）
        meta = queries.get_daylist_meta(daylist)
        start_ts = meta.get("start_ts", 0)
        end_ts = meta.get("end_ts", 0)

        # 3. 查所有场景的轮数
        rounds_map = queries.get_all_scenarios_rounds(start_ts, end_ts)

        # 4. 组合数据
        result_rows = []
        for row in rows:
            scn = row.get("scenario", "")
            required = row.get("rounds", 0)
            done = rounds_map.get(scn, 0)

            # 计算状态
            if done == 0:
                status = "未开始"
            elif done >= required:
                status = "已完成"
            else:
                status = "进行中"

            result_rows.append({
                "order": row.get("order", 0),
                "scenario": scn,
                "role": row.get("role", ""),
                "required_rounds": required,
                "done_rounds": done,
                "status": status
            })

        data = {
            "daylist": daylist,
            "label": meta.get("label", ""),
            "run_date": meta.get("run_date", ""),
            "items": meta.get("items", len(result_rows)),
            "rounds_total": meta.get("rounds_total", 0),
            "rows": result_rows
        }
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 场景接口 ====================

@app.get("/api/scenarios/{scenario}/score", response_model=ApiResponse)
async def get_scenario_score(
    scenario: str,
    start_ts: int = Query(...),
    end_ts: int = Query(...),
    list: str = Query("viscose-s2-easier")
):
    """获取某个场景在某段时间的最佳成绩"""
    try:
        data = queries.get_scenario_best(scenario, start_ts, end_ts, list)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/scenarios/{scenario}/rounds", response_model=ApiResponse)
async def get_scenario_rounds(
    scenario: str,
    start_ts: int = Query(...),
    end_ts: int = Query(...),
    list: str = Query("viscose-s2-easier")
):
    """获取某个场景在某段时间的打靶轮数"""
    try:
        rounds = queries.get_scenario_rounds(scenario, start_ts, end_ts, list)
        data = {"scenario": scenario, "rounds": rounds}
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/scenarios/{scenario}/history", response_model=ApiResponse)
async def get_scenario_history(
    scenario: str,
    days: int = Query(30),
    list: str = Query("viscose-s2-easier")
):
    """获取某个场景的历史成绩趋势"""
    try:
        data = queries.get_scenario_history(scenario, days, list)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/scenarios/{scenario}/reflections", response_model=ApiResponse)
async def get_scenario_reflections(
    scenario: str,
    days: int = Query(30)
):
    """获取某个场景的所有历史感悟"""
    try:
        data = queries.get_scenario_reflections(scenario, days)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/scenarios/{scenario}/bench", response_model=ApiResponse)
async def get_scenario_bench(
    scenario: str,
    list: str = Query("viscose-s2-easier")
):
    """获取某个场景的基准数据"""
    try:
        data = queries.get_scenario_bench(scenario, list)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/scenarios/{scenario}/popup", response_model=ApiResponse)
async def get_scenario_popup(
    scenario: str,
    start_ts: int = Query(...),
    end_ts: int = Query(...),
    list: str = Query("viscose-s2-easier")
):
    """获取感悟弹窗的完整数据"""
    try:
        # 1. 当天成绩
        score = queries.get_scenario_best(scenario, start_ts, end_ts, list)

        # 2. 基准数据
        bench = queries.get_scenario_bench(scenario, list)

        # 3. 历史感悟
        reflections = queries.get_scenario_reflections(scenario, 30)

        data = {
            "scenario": scenario,
            "today_score": score,
            "bench": bench,
            "reflections": reflections
        }
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# ==================== 基准总览接口 ====================

@app.get("/api/bench/scenarios", response_model=ApiResponse)
async def get_bench_scenarios(
    list: str = Query("viscose-s2-easier")
):
    """获取某个清单下所有场景的基准数据"""
    try:
        data = queries.get_all_bench_scenarios(list)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/bench/groups", response_model=ApiResponse)
async def get_bench_groups(
    list: str = Query("viscose-s2-easier")
):
    """获取基准总览的分组数据（4 大类 14 子类）"""
    try:
        data = queries.get_bench_groups(list)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 感悟接口 ====================

class ReflectionCreate(BaseModel):
    scenario: str
    note: str
    daylist: Optional[str] = None

@app.post("/api/reflections", response_model=ApiResponse)
async def create_reflection(reflection: ReflectionCreate):
    """新增一条感悟"""
    try:
        data = queries.create_reflection(reflection.scenario, reflection.note, reflection.daylist)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 数据更新接口 ====================

@app.post("/api/data/update", response_model=ApiResponse)
async def update_data():
    """触发数据更新"""
    try:
        import subprocess
        import os
        
        # 项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # 执行更新脚本
        result = subprocess.run(
            ["python", "update_all.py"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return ApiResponse(code=0, data={
                "status": "success",
                "output": result.stdout
            })
        else:
            return ApiResponse(code=500, message=result.stderr)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))
