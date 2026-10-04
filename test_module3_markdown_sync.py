# -*- coding: utf-8 -*-
"""
模块 3 四重验证测试脚本
测试 Markdown 文件同步功能
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web", "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.services import game_reflection_markdown as md_service
from app.repositories import game_reflection_repo as repo

client = TestClient(app)

# 测试日期
TEST_DATE = "2026-10-05"


def test_unit():
    """单元检验：Markdown 服务单个函数是否正确"""
    print("\n" + "=" * 60)
    print("【单元检验】Markdown 服务函数验证")
    print("=" * 60)

    # 测试 1: 感悟转 Markdown
    print("\n1. 测试感悟转 Markdown...")
    reflection = {
        "id": "ref_test_001",
        "title": "测试感悟标题",
        "content": "这是测试内容，支持 **Markdown** 格式。",
        "theme": "aim",
        "game": "valorant",
        "mode": "ranked",
        "map_name": "Ascent",
        "agent_name": "Jett",
        "scenario": "中路对枪",
        "tags": ["#预瞄", "#急停"],
        "date": TEST_DATE
    }
    md = md_service.reflection_to_markdown(reflection)
    assert "测试感悟标题" in md
    assert "对枪/瞄准" in md
    assert "valorant" in md
    assert "Ascent" in md
    assert "#预瞄" in md
    assert "ref_test_001" in md
    print("   ✅ 感悟转 Markdown 正确")

    # 测试 2: Markdown 解析
    print("\n2. 测试 Markdown 解析...")
    parsed = md_service.parse_markdown_reflections(md)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "测试感悟标题"
    assert parsed[0]["id"] == "ref_test_001"
    assert parsed[0]["theme"] == "aim"
    assert len(parsed[0]["tags"]) == 2
    print(f"   ✅ Markdown 解析正确: {parsed[0]['title']}")

    # 测试 3: 写入和读取
    print("\n3. 测试写入和读取 Markdown 文件...")
    reflections = [reflection]
    success = md_service.write_date_reflections(TEST_DATE, reflections)
    assert success

    read_back = md_service.read_date_reflections(TEST_DATE)
    assert len(read_back) >= 1
    found = any(r["id"] == "ref_test_001" for r in read_back)
    assert found
    print("   ✅ 写入和读取 Markdown 文件正确")

    # 测试 4: 增量同步
    print("\n4. 测试增量同步...")
    new_reflection = {
        "id": "ref_test_002",
        "title": "第二条感悟",
        "content": "这是第二条测试内容。",
        "theme": "move",
        "game": "valorant",
        "tags": ["#身法"],
        "date": TEST_DATE
    }
    success = md_service.sync_reflection_to_markdown(new_reflection)
    assert success

    read_back = md_service.read_date_reflections(TEST_DATE)
    assert len(read_back) >= 2
    found = any(r["id"] == "ref_test_002" for r in read_back)
    assert found
    print("   ✅ 增量同步正确")

    # 测试 5: 列出所有日期
    print("\n5. 测试列出所有日期...")
    dates = md_service.list_all_markdown_dates()
    assert TEST_DATE in dates
    print(f"   ✅ 列出日期正确: {dates}")

    print("\n✅ 单元检验全部通过！")


def test_cross():
    """交叉检验：API 返回格式/协议是否正确"""
    print("\n" + "=" * 60)
    print("【交叉检验】API 返回格式验证")
    print("=" * 60)

    # 测试 1: 列出 Markdown 日期
    print("\n1. 测试列出 Markdown 日期 API...")
    response = client.get("/api/game-reflections/markdown/dates")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert "dates" in result["data"]
    assert isinstance(result["data"]["dates"], list)
    print(f"   ✅ 日期列表格式正确: {len(result['data']['dates'])} 个日期")

    # 测试 2: 读取指定日期的 Markdown
    print("\n2. 测试读取指定日期 Markdown API...")
    response = client.get(f"/api/game-reflections/markdown/{TEST_DATE}")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert "date" in result["data"]
    assert "filepath" in result["data"]
    assert "count" in result["data"]
    assert "reflections" in result["data"]
    print(f"   ✅ 日期 Markdown 格式正确: {result['data']['count']} 条感悟")

    # 测试 3: 导出到 Markdown
    print("\n3. 测试导出到 Markdown API...")
    response = client.post("/api/game-reflections/markdown/export")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert "total" in result["data"]
    assert "dates" in result["data"]
    print(f"   ✅ 导出格式正确: 导出 {result['data']['total']} 条到 {result['data']['dates']} 个日期")

    print("\n✅ 交叉检验全部通过！")


def test_code():
    """代码检验：边界情况和异常处理"""
    print("\n" + "=" * 60)
    print("【代码检验】边界情况和异常处理")
    print("=" * 60)

    # 测试 1: 读取不存在的日期
    print("\n1. 测试读取不存在的日期...")
    reflections = md_service.read_date_reflections("2099-01-01")
    assert reflections == []
    print("   ✅ 不存在的日期返回空列表")

    # 测试 2: 删除感悟
    print("\n2. 测试从 Markdown 删除感悟...")
    success = md_service.delete_reflection_from_markdown(TEST_DATE, "ref_test_002")
    assert success

    read_back = md_service.read_date_reflections(TEST_DATE)
    found = any(r["id"] == "ref_test_002" for r in read_back)
    assert not found
    print("   ✅ 从 Markdown 删除感悟正确")

    # 测试 3: 删除不存在的感悟（不报错）
    print("\n3. 测试删除不存在的感悟...")
    success = md_service.delete_reflection_from_markdown(TEST_DATE, "nonexistent_id")
    assert success
    print("   ✅ 删除不存在的感悟不报错")

    # 测试 4: 空感悟列表写入
    print("\n4. 测试空感悟列表写入...")
    success = md_service.write_date_reflections("2099-01-02", [])
    assert success
    # 空列表也会创建文件（只有标题）
    print("   ✅ 空感悟列表写入正确")

    # 测试 5: 特殊字符处理
    print("\n5. 测试特殊字符处理...")
    special_reflection = {
        "id": "ref_test_special",
        "title": "特殊字符测试：引号\"单引号'括号()",
        "content": "内容中有 **粗体** 和 *斜体* 和 `代码`",
        "theme": "mindset",
        "game": "valorant",
        "tags": ["#特殊", "#字符"],
        "date": TEST_DATE
    }
    md = md_service.reflection_to_markdown(special_reflection)
    assert "特殊字符测试" in md
    assert "粗体" in md

    # 解析回来
    parsed = md_service.parse_markdown_reflections(md)
    assert len(parsed) == 1
    print("   ✅ 特殊字符处理正确")

    print("\n✅ 代码检验全部通过！")


def test_e2e():
    """端到端检验：完整的双写流程"""
    print("\n" + "=" * 60)
    print("【端到端检验】完整双写流程验证")
    print("=" * 60)

    # 完整流程：API 创建 -> InfluxDB 查询 -> Markdown 查询 -> API 更新 -> API 删除
    print("\n1. 通过 API 创建感悟（双写）...")
    response = client.post("/api/game-reflections", json={
        "title": "[E2E测试] Markdown双写测试",
        "content": "这是端到端测试，验证 InfluxDB + Markdown 双写是否正常。",
        "theme": "aim",
        "game": "valorant",
        "mode": "deathmatch",
        "map_name": "Haven",
        "tags": ["#e2e", "#双写"],
        "date": TEST_DATE
    })
    assert response.status_code == 200
    test_id = response.json()["data"]["id"]
    print(f"   ✅ API 创建成功: {test_id}")

    print("\n2. 验证 InfluxDB 中有数据...")
    data = repo.get_game_reflection_by_id(test_id)
    assert data is not None
    assert data["title"] == "[E2E测试] Markdown双写测试"
    print(f"   ✅ InfluxDB 查询成功: {data['title']}")

    print("\n3. 验证 Markdown 文件中有数据...")
    md_reflections = md_service.read_date_reflections(TEST_DATE)
    found = any(r["id"] == test_id for r in md_reflections)
    assert found
    print("   ✅ Markdown 文件中有数据")

    print("\n4. 通过 API 更新感悟（双写）...")
    response = client.put(f"/api/game-reflections/{test_id}", json={
        "title": "[E2E测试] 更新后的双写测试",
        "tags": ["#e2e", "#双写", "#更新"]
    })
    assert response.status_code == 200

    # 验证 InfluxDB 更新
    data = repo.get_game_reflection_by_id(test_id)
    assert data["title"] == "[E2E测试] 更新后的双写测试"
    assert len(data["tags"]) == 3

    # 验证 Markdown 更新
    md_reflections = md_service.read_date_reflections(TEST_DATE)
    found = next((r for r in md_reflections if r["id"] == test_id), None)
    assert found is not None
    assert found["title"] == "[E2E测试] 更新后的双写测试"
    print("   ✅ API 更新成功，双写同步")

    print("\n5. 通过 API 删除感悟（双写）...")
    response = client.delete(f"/api/game-reflections/{test_id}")
    assert response.status_code == 200

    # 验证 InfluxDB 删除
    data = repo.get_game_reflection_by_id(test_id)
    assert data is None

    # 验证 Markdown 删除
    md_reflections = md_service.read_date_reflections(TEST_DATE)
    found = any(r["id"] == test_id for r in md_reflections)
    assert not found
    print("   ✅ API 删除成功，双写同步")

    print("\n6. 测试 Markdown 导入功能...")
    # 先创建一条感悟
    response = client.post("/api/game-reflections", json={
        "title": "[E2E测试] 导入测试",
        "content": "测试从 Markdown 导入功能。",
        "theme": "move",
        "game": "valorant",
        "date": TEST_DATE
    })
    import_id = response.json()["data"]["id"]

    # 从 InfluxDB 删除（但保留 Markdown）
    repo.delete_game_reflection(import_id)

    # 验证 InfluxDB 中已删除
    data = repo.get_game_reflection_by_id(import_id)
    assert data is None

    # 从 Markdown 导入
    response = client.post("/api/game-reflections/markdown/import")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    print(f"   ✅ Markdown 导入成功: 导入 {result['data']['imported']} 条，跳过 {result['data']['skipped']} 条")

    # 清理
    repo.delete_game_reflection(import_id)
    md_service.delete_reflection_from_markdown(TEST_DATE, import_id)

    print("\n✅ 端到端检验全部通过！")


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("模块 3：Markdown 文件同步 - 四重验证")
    print("🚀" * 30)

    try:
        test_unit()    # 单元检验
        test_cross()   # 交叉检验
        test_code()    # 代码检验
        test_e2e()     # 端到端检验

        print("\n" + "🎉" * 30)
        print("✅ 模块 3 四重验证全部通过！")
        print("🎉" * 30)
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
