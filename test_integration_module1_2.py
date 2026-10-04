# -*- coding: utf-8 -*-
"""
模块 1 + 模块 2 集成测试
验证数据访问层和 API 层的协作
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web", "backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.repositories import game_reflection_repo as repo

client = TestClient(app)


def test_integration():
    """集成测试：数据访问层 + API 层协作"""
    print("\n" + "=" * 60)
    print("【集成测试】模块 1 + 模块 2 协作验证")
    print("=" * 60)

    # 测试 1: 通过 API 创建，通过数据访问层查询
    print("\n1. 测试：API 创建 -> 数据层查询...")
    response = client.post("/api/game-reflections", json={
        "title": "[集成测试] API创建数据层查询",
        "content": "验证 API 创建的数据能否通过数据层查询到",
        "theme": "aim",
        "game": "valorant",
        "date": "2026-10-05",
        "tags": ["#集成测试"]
    })
    assert response.status_code == 200
    api_id = response.json()["data"]["id"]

    # 通过数据层查询
    data = repo.get_game_reflection_by_id(api_id)
    assert data is not None
    assert data["id"] == api_id
    assert data["title"] == "[集成测试] API创建数据层查询"
    print(f"   ✅ API 创建的数据通过数据层查询成功: {data['title']}")

    # 测试 2: 通过数据访问层创建，通过 API 查询
    print("\n2. 测试：数据层创建 -> API 查询...")
    result = repo.create_game_reflection(
        title="[集成测试] 数据层创建API查询",
        content="验证数据层创建的数据能否通过 API 查询到",
        theme="move",
        date="2026-10-05",
        tags=["#集成测试"]
    )
    repo_id = result["id"]

    # 通过 API 查询
    response = client.get(f"/api/game-reflections/{repo_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == repo_id
    assert data["title"] == "[集成测试] 数据层创建API查询"
    print(f"   ✅ 数据层创建的数据通过 API 查询成功: {data['title']}")

    # 测试 3: 通过 API 更新，通过数据层验证
    print("\n3. 测试：API 更新 -> 数据层验证...")
    response = client.put(f"/api/game-reflections/{api_id}", json={
        "title": "[集成测试] API更新后标题",
        "content": "更新后的内容"
    })
    assert response.status_code == 200

    # 通过数据层验证
    data = repo.get_game_reflection_by_id(api_id)
    assert data["title"] == "[集成测试] API更新后标题"
    assert data["content"] == "更新后的内容"
    print(f"   ✅ API 更新的数据通过数据层验证成功: {data['title']}")

    # 测试 4: 通过数据层更新，通过 API 验证
    print("\n4. 测试：数据层更新 -> API 验证...")
    repo.update_game_reflection(repo_id, {
        "title": "[集成测试] 数据层更新后标题",
        "tags": ["#集成测试", "#更新"]
    })

    # 通过 API 验证
    response = client.get(f"/api/game-reflections/{repo_id}")
    data = response.json()["data"]
    assert data["title"] == "[集成测试] 数据层更新后标题"
    assert len(data["tags"]) == 2
    print(f"   ✅ 数据层更新的数据通过 API 验证成功: {data['title']}")

    # 测试 5: 热身项目和感悟的关联
    print("\n5. 测试：热身项目和感悟的关联...")
    # 创建热身项目
    warmup_result = repo.create_warmup_item(
        name="[集成测试] 关联测试热身项目",
        type="tracking",
        description="用于测试热身项目和感悟的关联"
    )
    warmup_name = warmup_result["name"]

    # 创建关联到该热身项目的感悟
    reflection_result = repo.create_game_reflection(
        title="[集成测试] 热身项目关联感悟",
        content="这是关联到热身项目的感悟",
        theme="warmup",
        date="2026-10-05",
        warmup_item=warmup_name,
        tags=["#集成测试", "#热身"]
    )
    reflection_id = reflection_result["id"]

    # 通过 API 查询热身项目列表，验证感悟关联
    response = client.get("/api/warmup-items")
    assert response.status_code == 200
    items = response.json()["data"]
    found_warmup = None
    for item in items:
        if item["name"] == warmup_name:
            found_warmup = item
            break
    assert found_warmup is not None
    assert len(found_warmup["reflections"]) >= 1
    found_reflection = any(r["id"] == reflection_id for r in found_warmup["reflections"])
    assert found_reflection
    print(f"   ✅ 热身项目和感悟关联正常: 热身项目有 {len(found_warmup['reflections'])} 条感悟")

    # 通过 API 查询热身项目的感悟
    response = client.get(f"/api/warmup-items/{warmup_name}/reflections")
    assert response.status_code == 200
    reflections = response.json()["data"]
    assert len(reflections) >= 1
    print(f"   ✅ 通过 API 查询热身项目感悟正常: 返回 {len(reflections)} 条")

    # 测试 6: 统计数据一致性
    print("\n6. 测试：统计数据一致性...")
    # 通过数据层获取统计
    repo_stats = repo.get_game_reflection_stats()
    # 通过 API 获取统计
    response = client.get("/api/game-reflections/stats")
    api_stats = response.json()["data"]

    assert repo_stats["total_count"] == api_stats["total_count"]
    assert repo_stats["today_count"] == api_stats["today_count"]
    assert repo_stats["theme_count"] == api_stats["theme_count"]
    print(f"   ✅ 统计数据一致: 总数={repo_stats['total_count']}, 今日={repo_stats['today_count']}, 主题数={repo_stats['theme_count']}")

    # 测试 7: 列表查询一致性
    print("\n7. 测试：列表查询一致性...")
    # 通过数据层查询
    repo_result = repo.list_game_reflections(theme="aim", limit=10)
    # 通过 API 查询
    response = client.get("/api/game-reflections", params={"theme": "aim", "limit": 10})
    api_result = response.json()["data"]

    assert repo_result["total"] == api_result["total"]
    assert len(repo_result["items"]) == len(api_result["items"])
    print(f"   ✅ 列表查询一致: 总数={repo_result['total']}, 返回={len(repo_result['items'])} 条")

    # 清理测试数据
    print("\n8. 清理测试数据...")
    repo.delete_game_reflection(api_id)
    repo.delete_game_reflection(repo_id)
    repo.delete_game_reflection(reflection_id)
    print("   ✅ 测试数据清理完成")

    print("\n✅ 集成测试全部通过！")


if __name__ == "__main__":
    print("\n" + "🔗" * 30)
    print("模块 1 + 模块 2 集成测试")
    print("🔗" * 30)

    try:
        test_integration()

        print("\n" + "🎉" * 30)
        print("✅ 模块 1 + 模块 2 集成测试全部通过！")
        print("🎉" * 30)
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
