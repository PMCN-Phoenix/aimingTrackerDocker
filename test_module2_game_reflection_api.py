# -*- coding: utf-8 -*-
"""
模块 2 四重验证测试脚本
测试游戏感悟 CRUD API
"""
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web", "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_unit():
    """单元检验：单个 API 接口是否正确"""
    print("\n" + "=" * 60)
    print("【单元检验】单个 API 接口验证")
    print("=" * 60)

    # 测试 1: 健康检查
    print("\n1. 测试健康检查接口...")
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("   ✅ 健康检查接口正常")

    # 测试 2: 创建感悟
    print("\n2. 测试创建感悟接口...")
    response = client.post("/api/game-reflections", json={
        "title": "[API测试] 预瞄要放在头部高度",
        "content": "这是 API 测试内容，测试创建感悟接口是否正常。",
        "theme": "aim",
        "game": "valorant",
        "mode": "ranked",
        "map_name": "Ascent",
        "agent_name": "Jett",
        "scenario": "中路对枪测试",
        "tags": ["#api测试", "#预瞄"],
        "date": "2026-10-05"
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert "id" in result["data"]
    test_id = result["data"]["id"]
    print(f"   ✅ 创建感悟成功: {test_id}")

    # 测试 3: 根据 ID 查询
    print("\n3. 测试根据 ID 查询感悟接口...")
    response = client.get(f"/api/game-reflections/{test_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert result["data"]["id"] == test_id
    assert result["data"]["title"] == "[API测试] 预瞄要放在头部高度"
    print(f"   ✅ 查询感悟成功: {result['data']['title']}")

    # 测试 4: 查询不存在的 ID
    print("\n4. 测试查询不存在的 ID...")
    response = client.get("/api/game-reflections/nonexistent_id_12345")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 404
    print("   ✅ 不存在的 ID 正确返回 404")

    # 测试 5: 更新感悟
    print("\n5. 测试更新感悟接口...")
    response = client.put(f"/api/game-reflections/{test_id}", json={
        "title": "[API测试] 更新后的标题",
        "content": "更新后的内容"
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0

    # 验证更新
    response = client.get(f"/api/game-reflections/{test_id}")
    assert response.json()["data"]["title"] == "[API测试] 更新后的标题"
    print("   ✅ 更新感悟成功")

    # 测试 6: 删除感悟
    print("\n6. 测试删除感悟接口...")
    response = client.delete(f"/api/game-reflections/{test_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert result["data"]["deleted"] == True

    # 验证删除
    response = client.get(f"/api/game-reflections/{test_id}")
    assert response.json()["code"] == 404
    print("   ✅ 删除感悟成功")

    print("\n✅ 单元检验全部通过！")


def test_cross():
    """交叉检验：API 返回格式/协议是否正确"""
    print("\n" + "=" * 60)
    print("【交叉检验】API 返回格式验证")
    print("=" * 60)

    # 测试 1: 列表查询返回格式
    print("\n1. 测试列表查询返回格式...")
    response = client.get("/api/game-reflections", params={"theme": "aim", "limit": 10})
    assert response.status_code == 200
    result = response.json()
    assert "code" in result
    assert "message" in result
    assert "data" in result
    assert "total" in result["data"]
    assert "items" in result["data"]
    assert isinstance(result["data"]["items"], list)
    print(f"   ✅ 列表格式正确: total={result['data']['total']}, items={len(result['data']['items'])}")

    # 测试 2: 统计数据返回格式
    print("\n2. 测试统计数据返回格式...")
    response = client.get("/api/game-reflections/stats")
    assert response.status_code == 200
    result = response.json()
    assert "code" in result
    data = result["data"]
    assert "total_count" in data
    assert "today_count" in data
    assert "consecutive_days" in data
    assert "theme_count" in data
    assert "theme_distribution" in data
    assert isinstance(data["theme_distribution"], dict)
    print(f"   ✅ 统计格式正确: 总数={data['total_count']}, 今日={data['today_count']}, 主题数={data['theme_count']}")

    # 测试 3: 创建感悟参数校验（缺少必填字段）
    print("\n3. 测试创建感悟参数校验（缺少必填字段）...")
    response = client.post("/api/game-reflections", json={
        "content": "缺少标题和主题",
        "date": "2026-10-05"
    })
    assert response.status_code == 422  # Pydantic 校验错误
    print("   ✅ 缺少必填字段正确返回 422")

    # 测试 4: 创建感悟参数校验（非法主题）
    print("\n4. 测试创建感悟参数校验（非法主题）...")
    response = client.post("/api/game-reflections", json={
        "title": "测试",
        "content": "测试",
        "theme": "invalid_theme",
        "date": "2026-10-05"
    })
    assert response.status_code == 422
    print("   ✅ 非法主题正确返回 422")

    # 测试 5: 热身项目列表返回格式
    print("\n5. 测试热身项目列表返回格式...")
    response = client.get("/api/warmup-items")
    assert response.status_code == 200
    result = response.json()
    assert "code" in result
    assert isinstance(result["data"], list)
    print(f"   ✅ 热身项目列表格式正确: 共 {len(result['data'])} 个项目")

    print("\n✅ 交叉检验全部通过！")


def test_code():
    """代码检验：边界情况和异常处理"""
    print("\n" + "=" * 60)
    print("【代码检验】边界情况和异常处理")
    print("=" * 60)

    # 测试 1: 分页参数边界
    print("\n1. 测试分页参数边界...")
    # limit 超过最大值
    response = client.get("/api/game-reflections", params={"limit": 999})
    assert response.status_code == 422  # 超过 le=200
    print("   ✅ limit 超过最大值正确返回 422")

    # limit 小于最小值
    response = client.get("/api/game-reflections", params={"limit": 0})
    assert response.status_code == 422  # 小于 ge=1
    print("   ✅ limit 小于最小值正确返回 422")

    # offset 小于 0
    response = client.get("/api/game-reflections", params={"offset": -1})
    assert response.status_code == 422
    print("   ✅ offset 小于 0 正确返回 422")

    # 测试 2: 多条件组合筛选
    print("\n2. 测试多条件组合筛选...")
    response = client.get("/api/game-reflections", params={
        "theme": "aim",
        "game": "valorant",
        "mode": "ranked",
        "date": "2026-10-05",
        "limit": 5
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    print(f"   ✅ 多条件组合筛选正常: 返回 {len(result['data']['items'])} 条")

    # 测试 3: 创建热身项目
    print("\n3. 测试创建热身项目...")
    response = client.post("/api/warmup-items", json={
        "name": "[API测试] 测试热身项目",
        "type": "tracking",
        "description": "这是 API 测试创建的热身项目"
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert "id" in result["data"]
    warmup_id = result["data"]["id"]
    print(f"   ✅ 创建热身项目成功: {warmup_id}")

    # 测试 4: 获取热身项目的感悟
    print("\n4. 测试获取热身项目的感悟...")
    response = client.get("/api/warmup-items/%5BAPI%E6%B5%8B%E8%AF%95%5D%20%E6%B5%8B%E8%AF%95%E7%83%AD%E8%BA%AB%E9%A1%B9%E7%9B%AE/reflections")
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    assert isinstance(result["data"], list)
    print(f"   ✅ 获取热身项目感悟正常: 返回 {len(result['data'])} 条")

    # 测试 5: 空标签列表
    print("\n5. 测试空标签列表...")
    response = client.post("/api/game-reflections", json={
        "title": "[API测试] 空标签测试",
        "content": "测试空标签",
        "theme": "mindset",
        "date": "2026-10-05",
        "tags": []
    })
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 0
    test_id = result["data"]["id"]

    # 验证标签为空
    response = client.get(f"/api/game-reflections/{test_id}")
    assert response.json()["data"]["tags"] == []

    # 清理
    client.delete(f"/api/game-reflections/{test_id}")
    print("   ✅ 空标签列表处理正确")

    print("\n✅ 代码检验全部通过！")


def test_e2e():
    """端到端检验：完整的 CRUD 流程"""
    print("\n" + "=" * 60)
    print("【端到端检验】完整 CRUD 流程验证")
    print("=" * 60)

    # 完整流程：创建 -> 查询 -> 列表 -> 统计 -> 更新 -> 删除
    print("\n1. 创建感悟...")
    response = client.post("/api/game-reflections", json={
        "title": "[E2E测试] 完整流程测试",
        "content": "这是端到端测试，验证完整的 CRUD 流程。",
        "theme": "move",
        "game": "valorant",
        "mode": "deathmatch",
        "map_name": "Haven",
        "agent_name": "Phoenix",
        "tags": ["#e2e", "#身法"],
        "date": "2026-10-05"
    })
    assert response.status_code == 200
    test_id = response.json()["data"]["id"]
    print(f"   ✅ 创建成功: {test_id}")

    print("\n2. 查询感悟详情...")
    response = client.get(f"/api/game-reflections/{test_id}")
    data = response.json()["data"]
    assert data["title"] == "[E2E测试] 完整流程测试"
    assert data["theme"] == "move"
    assert data["game"] == "valorant"
    assert len(data["tags"]) == 2
    print(f"   ✅ 查询成功: {data['title']}")

    print("\n3. 列表查询（按主题筛选）...")
    response = client.get("/api/game-reflections", params={"theme": "move"})
    items = response.json()["data"]["items"]
    found = any(item["id"] == test_id for item in items)
    assert found
    print(f"   ✅ 列表查询成功: 在 move 主题中找到测试感悟")

    print("\n4. 统计数据...")
    response = client.get("/api/game-reflections/stats")
    stats = response.json()["data"]
    assert stats["total_count"] >= 1
    assert "move" in stats["theme_distribution"]
    print(f"   ✅ 统计成功: 总数={stats['total_count']}, move主题={stats['theme_distribution'].get('move', 0)}")

    print("\n5. 更新感悟...")
    response = client.put(f"/api/game-reflections/{test_id}", json={
        "title": "[E2E测试] 更新后的标题",
        "tags": ["#e2e", "#身法", "#更新"]
    })
    assert response.status_code == 200

    response = client.get(f"/api/game-reflections/{test_id}")
    data = response.json()["data"]
    assert data["title"] == "[E2E测试] 更新后的标题"
    assert len(data["tags"]) == 3
    print(f"   ✅ 更新成功: 标题={data['title']}, 标签数={len(data['tags'])}")

    print("\n6. 删除感悟...")
    response = client.delete(f"/api/game-reflections/{test_id}")
    assert response.status_code == 200

    response = client.get(f"/api/game-reflections/{test_id}")
    assert response.json()["code"] == 404
    print("   ✅ 删除成功: 已确认删除")

    print("\n✅ 端到端检验全部通过！")


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("模块 2：感悟 CRUD API - 四重验证")
    print("🚀" * 30)

    try:
        test_unit()    # 单元检验
        test_cross()   # 交叉检验
        test_code()    # 代码检验
        test_e2e()     # 端到端检验

        print("\n" + "🎉" * 30)
        print("✅ 模块 2 四重验证全部通过！")
        print("🎉" * 30)
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
