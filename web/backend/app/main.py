# -*- coding: utf-8 -*-
"""FastAPI 后端主程序"""
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from pydantic import BaseModel

from app.repositories import queries
from app.repositories import vdim_queries

app = FastAPI(title="练枪看板 API", version="0.1.0")

# CORS 配置：允许前端开发服务器跨域访问
# 注意：localhost 与 127.0.0.1 是**不同 origin**，两者都要放行，
# 否则浏览器会拦截响应（表现为页面全空 + "数据更新失败"），但后端日志仍是 200。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
    """获取完成度面板的完整数据

    统一走 repositories.queries.get_daylist_progress_data()——这里原本有一份
    逐行复制的实现，导致仓库层加字段（today_score / bench）后接口拿不到，
    前端「目标对比」表全空。保留单一实现，避免再次漂移。
    """
    try:
        return ApiResponse(code=0, data=queries.get_daylist_progress_data(daylist))
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 加练清单接口 ====================

@app.get("/api/daylists/{daylist}/extras", response_model=ApiResponse)
async def get_daylist_extras(daylist: str):
    """获取某个主清单的所有加练清单"""
    try:
        extras = queries.get_daylist_extras(daylist)
        return ApiResponse(code=0, data=extras)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/daylists/{daylist}/with-extras", response_model=ApiResponse)
async def get_daylist_with_extras(daylist: str):
    """获取主清单 + 所有加练清单的完整数据"""
    try:
        # 1. 主清单进度
        main_response = await get_daylist_progress(daylist)
        main_data = main_response.data if hasattr(main_response, 'data') else main_response.get('data')

        # 2. 所有加练清单进度
        extras_meta = queries.get_daylist_extras(daylist)
        extras_data = []
        for extra in extras_meta:
            extra_id = extra.get("daylist")
            if extra_id:
                extra_response = await get_daylist_progress(extra_id)
                extra_data.append(extra_response.data if hasattr(extra_response, 'data') else extra_response.get('data'))

        data = {
            "main": main_data,
            "extras": extras_data
        }
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


class ExtraDaylistCreate(BaseModel):
    parent_daylist: str
    name: str
    exec_dates: str
    items: list


@app.post("/api/daylists/extras", response_model=ApiResponse)
async def create_extra_daylist(extra: ExtraDaylistCreate):
    """创建加练清单"""
    try:
        data = queries.create_extra_daylist(
            parent_daylist=extra.parent_daylist,
            name=extra.name,
            exec_dates=extra.exec_dates,
            items=extra.items
        )
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.delete("/api/daylists/extras/{extra_id}", response_model=ApiResponse)
async def delete_extra_daylist(extra_id: str):
    """删除加练清单"""
    try:
        data = queries.delete_extra_daylist(extra_id)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/daylists/{daylist}/export-playlist", response_model=ApiResponse)
async def export_playlist(daylist: str, name: str = Query(None)):
    """导出清单为 Kovaak's playlist.json 并复制到游戏目录"""
    try:
        data = queries.export_playlist_to_kovaaks(daylist, name)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/daylists/{daylist}/playlist", response_model=ApiResponse)
async def get_playlist_json(daylist: str, name: str = Query(None)):
    """获取清单的 Kovaak's playlist.json 格式数据"""
    try:
        data = queries.generate_playlist_json(daylist, name)
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
    """获取感悟弹窗的完整数据（优化版：合并所有数据到一个接口）"""
    try:
        # 1. 当天成绩
        score = queries.get_scenario_best(scenario, start_ts, end_ts, list)

        # 2. 基准数据
        bench = queries.get_scenario_bench(scenario, list)

        # 3. 历史感悟
        reflections = queries.get_scenario_reflections(scenario, 30)

        # 4. 历史曲线数据（合并到 popup 接口，减少 HTTP 请求）
        history = queries.get_scenario_history(scenario, 30, list)

        data = {
            "scenario": scenario,
            "today_score": score,
            "bench": bench,
            "reflections": reflections,
            "history": history
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


# ==================== 游戏感悟接口 ====================

from app.models.game_reflection import (
    GameReflectionCreate, GameReflectionUpdate, WarmupItemCreate
)
from app.repositories import game_reflection_repo as gr_repo
from app.services import game_reflection_markdown as md_service


@app.get("/api/game-reflections", response_model=ApiResponse)
async def list_game_reflections(
    theme: Optional[str] = Query(None, description="主题筛选: warmup/aim/move/mind/map/agent/mindset"),
    game: Optional[str] = Query(None, description="游戏筛选: valorant/apex/cs2"),
    mode: Optional[str] = Query(None, description="模式筛选"),
    date: Optional[str] = Query(None, description="日期筛选: YYYY-MM-DD"),
    date_start: Optional[str] = Query(None, description="开始日期"),
    date_end: Optional[str] = Query(None, description="结束日期"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    warmup_item: Optional[str] = Query(None, description="热身项目筛选"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """获取游戏感悟列表（支持多维度筛选）"""
    try:
        data = gr_repo.list_game_reflections(
            theme=theme, game=game, mode=mode, date=date,
            date_start=date_start, date_end=date_end, tag=tag,
            warmup_item=warmup_item, limit=limit, offset=offset
        )
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/game-reflections/stats", response_model=ApiResponse)
async def get_game_reflection_stats():
    """获取游戏感悟统计数据"""
    try:
        data = gr_repo.get_game_reflection_stats()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/game-reflections/{ref_id}", response_model=ApiResponse)
async def get_game_reflection(ref_id: str):
    """根据 ID 获取单条游戏感悟"""
    try:
        data = gr_repo.get_game_reflection_by_id(ref_id)
        if not data:
            return ApiResponse(code=404, message="感悟不存在")
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/game-reflections", response_model=ApiResponse)
async def create_game_reflection(reflection: GameReflectionCreate):
    """创建一条游戏感悟（双写：InfluxDB + Markdown）"""
    try:
        # 1. 写入 InfluxDB
        data = gr_repo.create_game_reflection(
            title=reflection.title,
            content=reflection.content,
            theme=reflection.theme.value,
            date=reflection.date,
            game=reflection.game.value,
            mode=reflection.mode,
            map_name=reflection.map_name,
            agent_name=reflection.agent_name,
            scenario=reflection.scenario,
            tags=reflection.tags,
            warmup_item=reflection.warmup_item
        )

        # 2. 同步到 Markdown（异步，不阻塞主流程）
        try:
            full_reflection = gr_repo.get_game_reflection_by_id(data["id"])
            if full_reflection:
                md_service.sync_reflection_to_markdown(full_reflection)
        except Exception as md_error:
            # Markdown 同步失败不影响主流程
            print(f"[警告] Markdown 同步失败: {md_error}")

        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.put("/api/game-reflections/{ref_id}", response_model=ApiResponse)
async def update_game_reflection(ref_id: str, reflection: GameReflectionUpdate):
    """更新一条游戏感悟（双写：InfluxDB + Markdown）"""
    try:
        # 1. 获取旧数据（用于 Markdown 删除）
        old_data = gr_repo.get_game_reflection_by_id(ref_id)
        old_date = old_data.get("date", "") if old_data else ""

        # 2. 更新 InfluxDB
        updates = reflection.dict(exclude_unset=True)
        if "theme" in updates and updates["theme"]:
            updates["theme"] = updates["theme"].value
        if "game" in updates and updates["game"]:
            updates["game"] = updates["game"].value

        data = gr_repo.update_game_reflection(ref_id, updates)

        # 3. 同步到 Markdown
        try:
            # 如果日期变了，先从旧日期的 Markdown 删除
            new_data = gr_repo.get_game_reflection_by_id(ref_id)
            if new_data:
                new_date = new_data.get("date", "")
                if old_date and old_date != new_date:
                    md_service.delete_reflection_from_markdown(old_date, ref_id)
                # 同步到新日期的 Markdown
                md_service.sync_reflection_to_markdown(new_data)
        except Exception as md_error:
            print(f"[警告] Markdown 同步失败: {md_error}")

        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.delete("/api/game-reflections/{ref_id}", response_model=ApiResponse)
async def delete_game_reflection(ref_id: str):
    """删除一条游戏感悟（双写：InfluxDB + Markdown）"""
    try:
        # 1. 获取数据（用于 Markdown 删除）
        data = gr_repo.get_game_reflection_by_id(ref_id)
        date = data.get("date", "") if data else ""

        # 2. 从 InfluxDB 删除
        result = gr_repo.delete_game_reflection(ref_id)

        # 3. 从 Markdown 删除
        try:
            if date:
                md_service.delete_reflection_from_markdown(date, ref_id)
        except Exception as md_error:
            print(f"[警告] Markdown 删除失败: {md_error}")

        return ApiResponse(code=0, data=result)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 热身项目接口 ====================

@app.get("/api/warmup-items", response_model=ApiResponse)
async def list_warmup_items():
    """获取所有热身项目（含每个项目的感悟）"""
    try:
        data = gr_repo.list_warmup_items()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/warmup-items", response_model=ApiResponse)
async def create_warmup_item(item: WarmupItemCreate):
    """创建一个热身项目"""
    try:
        data = gr_repo.create_warmup_item(
            name=item.name,
            type=item.type,
            description=item.description
        )
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/warmup-items/{item_name}/reflections", response_model=ApiResponse)
async def get_warmup_item_reflections(item_name: str):
    """获取某个热身项目的所有感悟"""
    try:
        data = gr_repo.get_warmup_item_reflections(item_name)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== Markdown 同步接口 ====================

@app.get("/api/game-reflections/markdown/dates", response_model=ApiResponse)
async def list_markdown_dates():
    """列出所有有感悟的 Markdown 日期文件"""
    try:
        dates = md_service.list_all_markdown_dates()
        return ApiResponse(code=0, data={"dates": dates})
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/game-reflections/markdown/{date}", response_model=ApiResponse)
async def get_markdown_reflections(date: str):
    """读取指定日期的 Markdown 感悟文件"""
    try:
        reflections = md_service.read_date_reflections(date)
        filepath = md_service.get_markdown_path(date)
        return ApiResponse(code=0, data={
            "date": date,
            "filepath": filepath,
            "count": len(reflections),
            "reflections": reflections
        })
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/game-reflections/markdown/import", response_model=ApiResponse)
async def import_from_markdown():
    """从所有 Markdown 文件导入感悟到 InfluxDB"""
    try:
        # 1. 读取所有 Markdown 感悟
        all_reflections = md_service.import_all_from_markdown()

        # 2. 导入到 InfluxDB（跳过已存在的 ID）
        imported = 0
        skipped = 0
        for reflection in all_reflections:
            ref_id = reflection.get("id", "")
            if ref_id:
                # 检查是否已存在
                existing = gr_repo.get_game_reflection_by_id(ref_id)
                if existing:
                    skipped += 1
                    continue

            # 创建感悟
            try:
                gr_repo.create_game_reflection(
                    title=reflection.get("title", "无标题"),
                    content=reflection.get("content", ""),
                    theme=reflection.get("theme", "mindset"),
                    date=reflection.get("date", ""),
                    game=reflection.get("game", "valorant"),
                    mode=reflection.get("mode"),
                    map_name=reflection.get("map_name"),
                    agent_name=reflection.get("agent_name"),
                    scenario=reflection.get("scenario"),
                    tags=reflection.get("tags"),
                    warmup_item=reflection.get("warmup_item")
                )
                imported += 1
            except Exception as import_error:
                print(f"[警告] 导入失败: {import_error}")

        return ApiResponse(code=0, data={
            "total": len(all_reflections),
            "imported": imported,
            "skipped": skipped
        })
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/game-reflections/markdown/export", response_model=ApiResponse)
async def export_to_markdown():
    """将 InfluxDB 中所有感悟导出到 Markdown 文件"""
    try:
        # 1. 获取所有感悟
        result = gr_repo.list_game_reflections(limit=1000)
        all_reflections = result.get("items", [])

        # 2. 按日期分组
        date_groups = {}
        for reflection in all_reflections:
            date = reflection.get("date", "")
            if date:
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append(reflection)

        # 3. 写入每个日期的 Markdown 文件
        exported = 0
        for date, reflections in date_groups.items():
            md_service.write_date_reflections(date, reflections)
            exported += len(reflections)

        return ApiResponse(code=0, data={
            "total": exported,
            "dates": len(date_groups),
            "date_list": sorted(date_groups.keys())
        })
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


# ==================== Aim Lab 接口 ====================

@app.get("/api/aimlab/tasks", response_model=ApiResponse)
async def get_aimlab_tasks():
    """获取所有 Aim Lab 任务列表"""
    try:
        data = queries.get_aimlab_tasks()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/aimlab/tasks/{task}/history", response_model=ApiResponse)
async def get_aimlab_task_history(
    task: str,
    days: int = Query(30)
):
    """获取某个 Aim Lab 任务的历史成绩"""
    try:
        data = queries.get_aimlab_task_history(task, days)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== VDIM 训练接口 ====================

class VdimCheckinCreate(BaseModel):
    date: str
    note: Optional[str] = None

class VdimScoreCreate(BaseModel):
    cycle: int
    day: str
    scenario: str
    score: float
    accuracy: Optional[float] = None
    date: Optional[str] = None

class VdimImportRequest(BaseModel):
    cycle: int
    day: str
    date: str


@app.get("/api/vdim/today", response_model=ApiResponse)
async def get_vdim_today():
    """获取今天的 VDIM 训练信息"""
    try:
        data = vdim_queries.get_vdim_today()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/vdim/day/{cycle}/{day}", response_model=ApiResponse)
async def get_vdim_day(cycle: int, day: str):
    """获取某周期某天的 VDIM 完整数据"""
    try:
        data = vdim_queries.get_vdim_day(cycle, day)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/vdim/overview", response_model=ApiResponse)
async def get_vdim_overview():
    """获取 VDIM 顶部概览卡片数据"""
    try:
        data = vdim_queries.get_vdim_overview()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/vdim/checkin", response_model=ApiResponse)
async def create_vdim_checkin(checkin: VdimCheckinCreate):
    """VDIM 训练打卡"""
    try:
        data = vdim_queries.create_vdim_checkin(checkin.date, checkin.note)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/vdim/score", response_model=ApiResponse)
async def create_vdim_score(score: VdimScoreCreate):
    """VDIM 手动补录分数"""
    try:
        data = vdim_queries.create_vdim_score(
            cycle=score.cycle,
            day=score.day,
            scenario=score.scenario,
            score=score.score,
            accuracy=score.accuracy,
            date=score.date,
            source="manual"
        )
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.post("/api/vdim/import", response_model=ApiResponse)
async def import_vdim_scores(import_req: VdimImportRequest):
    """从 Kovaak's stats 导入 VDIM 分数"""
    try:
        data = vdim_queries.import_vdim_scores_from_stats(
            cycle=import_req.cycle,
            day=import_req.day,
            date=import_req.date
        )
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/vdim/playlists", response_model=ApiResponse)
async def get_vdim_playlists():
    """获取 VDIM playlist 配置"""
    try:
        data = vdim_queries.get_vdim_playlists()
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


@app.get("/api/vdim/scenario/{scenario}/history", response_model=ApiResponse)
async def get_vdim_scenario_history(scenario: str, days: int = Query(30)):
    """获取某 VDIM 场景的历史分数"""
    try:
        data = vdim_queries.get_vdim_scenario_history(scenario, days)
        return ApiResponse(code=0, data=data)
    except Exception as e:
        return ApiResponse(code=500, message=str(e))


# ==================== 生产模式：前端静态文件服务 ====================

# 前端 dist 目录路径
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "frontend", "dist"
)

if os.path.exists(frontend_dist):
    # 挂载静态资源（JS/CSS/图片等）
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # SPA 路由：所有非 API 请求都返回 index.html
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # API 请求已经被上面的路由处理了，这里只处理前端路由
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not built"}
