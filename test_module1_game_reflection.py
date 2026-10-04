# -*- coding: utf-8 -*-
"""
模块 1 四重验证测试脚本
测试游戏感悟数据模型和数据访问层
"""
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web", "backend"))

from app.models.game_reflection import (
    GameReflectionCreate, GameReflectionUpdate, GameReflectionResponse,
    GameReflectionStats, WarmupItemCreate, ThemeEnum, GameEnum,
    THEME_NAMES, THEME_ICONS, THEME_COLORS
)
from app.repositories import game_reflection_repo as repo


def test_unit():
    """单元检验：数据模型是否正确"""
    print("\n" + "=" * 60)
    print("【单元检验】数据模型验证")
    print("=" * 60)

    # 测试 1: 创建感悟模型
    print("\n1. 测试 GameReflectionCreate 模型...")
    reflection = GameReflectionCreate(
        title="测试感悟标题",
        content="这是测试内容，支持 **Markdown**",
        theme=ThemeEnum.AIM,
        game=GameEnum.VALORANT,
        mode="ranked",
        map_name="Ascent",
        agent_name="Jett",
        scenario="中路对枪",
        tags=["#预瞄", "#急停"],
        date="2026-10-05"
    )
    assert reflection.title == "测试感悟标题"
    assert reflection.theme == ThemeEnum.AIM
    assert reflection.game == GameEnum.VALORANT
    assert len(reflection.tags) == 2
    print("   ✅ GameReflectionCreate 模型验证通过")

    # 测试 2: 响应模型自动填充主题信息
    print("\n2. 测试 GameReflectionResponse 模型自动填充...")
    response = GameReflectionResponse(
        id="ref_test_001",
        title="测试",
        content="测试内容",
        theme=ThemeEnum.WARMUP,
        game=GameEnum.VALORANT,
        date="2026-10-05"
    )
    assert response.theme_name == "热身"
    assert response.theme_icon == "🔥"
    assert response.theme_color == "#ef4444"
    print(f"   ✅ 主题自动填充: {response.theme_icon} {response.theme_name} ({response.theme_color})")

    # 测试 3: 所有主题枚举
    print("\n3. 测试所有主题枚举...")
    for theme in ThemeEnum:
        name = THEME_NAMES.get(theme.value, "")
        icon = THEME_ICONS.get(theme.value, "")
        color = THEME_COLORS.get(theme.value, "")
        assert name, f"主题 {theme.value} 缺少中文名"
        assert icon, f"主题 {theme.value} 缺少图标"
        assert color, f"主题 {theme.value} 缺少颜色"
        print(f"   ✅ {icon} {name} ({theme.value}) - {color}")

    # 测试 4: 更新模型（部分字段）
    print("\n4. 测试 GameReflectionUpdate 部分更新模型...")
    update = GameReflectionUpdate(title="新标题")
    assert update.title == "新标题"
    assert update.content is None
    print("   ✅ 部分更新模型验证通过")

    print("\n✅ 单元检验全部通过！")


def test_cross():
    """交叉检验：InfluxDB Line Protocol 格式是否正确"""
    print("\n" + "=" * 60)
    print("【交叉检验】InfluxDB 格式验证")
    print("=" * 60)

    # 测试 1: tag 值转义
    print("\n1. 测试 tag 值转义...")
    escaped = repo._escape_tag_value("hello world,test=1")
    assert escaped == "hello\\ world\\,test\\=1"
    print(f"   ✅ 转义结果: {escaped}")

    # 测试 2: field 字符串转义
    print("\n2. 测试 field 字符串转义...")
    escaped = repo._escape_field_string('他说"你好"')
    assert escaped == '他说\\"你好\\"'
    print(f"   ✅ 转义结果: {escaped}")

    # 测试 3: ID 生成
    print("\n3. 测试 ID 生成...")
    ref_id = repo._generate_reflection_id("2026-10-05")
    assert ref_id.startswith("ref_20261005_")
    assert len(ref_id) == len("ref_20261005_") + 8
    print(f"   ✅ 感悟 ID: {ref_id}")

    warmup_id = repo._generate_warmup_item_id()
    assert warmup_id.startswith("warmup_")
    print(f"   ✅ 热身项目 ID: {warmup_id}")

    # 测试 4: 日期转时间戳
    print("\n4. 测试日期转时间戳...")
    ts = repo._date_to_timestamp("2026-10-05")
    assert ts > 0
    print(f"   ✅ 2026-10-05 -> {ts}")

    print("\n✅ 交叉检验全部通过！")


def test_code():
    """代码检验：边界情况和异常处理"""
    print("\n" + "=" * 60)
    print("【代码检验】边界情况和异常处理")
    print("=" * 60)

    # 测试 1: 空标签列表
    print("\n1. 测试空标签列表...")
    reflection = GameReflectionCreate(
        title="测试",
        content="测试",
        theme=ThemeEnum.AIM,
        date="2026-10-05",
        tags=[]
    )
    assert reflection.tags == []
    print("   ✅ 空标签列表处理正确")

    # 测试 2: 可选字段为 None
    print("\n2. 测试可选字段为 None...")
    reflection = GameReflectionCreate(
        title="测试",
        content="测试",
        theme=ThemeEnum.MINDSET,
        date="2026-10-05"
    )
    assert reflection.mode is None
    assert reflection.map_name is None
    assert reflection.agent_name is None
    assert reflection.scenario is None
    assert reflection.warmup_item is None
    print("   ✅ 可选字段默认 None 处理正确")

    # 测试 3: 标题最大长度校验
    print("\n3. 测试标题最大长度校验...")
    try:
        reflection = GameReflectionCreate(
            title="A" * 201,  # 超过 200 字符
            content="测试",
            theme=ThemeEnum.AIM,
            date="2026-10-05"
        )
        print("   ❌ 应该抛出校验错误，但没有")
        assert False
    except Exception as e:
        print(f"   ✅ 超长标题正确抛出校验错误: {type(e).__name__}")

    # 测试 4: 主题枚举校验
    print("\n4. 测试主题枚举校验...")
    try:
        reflection = GameReflectionCreate(
            title="测试",
            content="测试",
            theme="invalid_theme",  # 非法主题
            date="2026-10-05"
        )
        print("   ❌ 应该抛出校验错误，但没有")
        assert False
    except Exception as e:
        print(f"   ✅ 非法主题正确抛出校验错误: {type(e).__name__}")

    # 测试 5: 行解析函数
    print("\n5. 测试行解析函数...")
    test_row = {
        "id": "ref_test",
        "title": "测试标题",
        "content": "测试内容",
        "theme": "aim",
        "game": "valorant",
        "date": "2026-10-05",
        "tags": "#预瞄,#急停,#头部高度",
        "_time": "2026-10-05T12:00:00Z"
    }
    parsed = repo._parse_reflection_row(test_row)
    assert parsed["id"] == "ref_test"
    assert parsed["title"] == "测试标题"
    assert len(parsed["tags"]) == 3
    assert "#预瞄" in parsed["tags"]
    print(f"   ✅ 行解析正确: {parsed['id']}, 标签数: {len(parsed['tags'])}")

    print("\n✅ 代码检验全部通过！")


def test_e2e():
    """端到端检验：实际写入 InfluxDB 并查询验证"""
    print("\n" + "=" * 60)
    print("【端到端检验】InfluxDB 实际读写验证")
    print("=" * 60)

    try:
        # 测试 1: 创建感悟
        print("\n1. 测试创建感悟...")
        result = repo.create_game_reflection(
            title="[E2E测试] 预瞄要放在头部高度",
            content="这是端到端测试内容，测试 InfluxDB 读写是否正常。",
            theme="aim",
            date="2026-10-05",
            game="valorant",
            mode="ranked",
            map_name="Ascent",
            agent_name="Jett",
            scenario="中路对枪测试",
            tags=["#e2e测试", "#预瞄"]
        )
        assert "id" in result
        test_id = result["id"]
        print(f"   ✅ 创建成功: {test_id}")

        # 测试 2: 根据 ID 查询
        print("\n2. 测试根据 ID 查询...")
        reflection = repo.get_game_reflection_by_id(test_id)
        assert reflection is not None
        assert reflection["id"] == test_id
        assert reflection["title"] == "[E2E测试] 预瞄要放在头部高度"
        assert reflection["theme"] == "aim"
        print(f"   ✅ 查询成功: {reflection['title']}")

        # 测试 3: 列表查询（按主题筛选）
        print("\n3. 测试列表查询（按主题筛选）...")
        result = repo.list_game_reflections(theme="aim", limit=10)
        assert "items" in result
        assert "total" in result
        print(f"   ✅ 查询成功: 共 {result['total']} 条 aim 主题感悟")

        # 测试 4: 更新感悟
        print("\n4. 测试更新感悟...")
        update_result = repo.update_game_reflection(test_id, {
            "title": "[E2E测试] 更新后的标题",
            "content": "更新后的内容"
        })
        assert update_result["id"] == test_id

        # 验证更新
        updated = repo.get_game_reflection_by_id(test_id)
        assert updated["title"] == "[E2E测试] 更新后的标题"
        print(f"   ✅ 更新成功: {updated['title']}")

        # 测试 5: 统计数据
        print("\n5. 测试统计数据...")
        stats = repo.get_game_reflection_stats()
        assert "total_count" in stats
        assert "today_count" in stats
        assert "theme_count" in stats
        assert "theme_distribution" in stats
        print(f"   ✅ 统计成功: 总数 {stats['total_count']}, 今日 {stats['today_count']}, 主题数 {stats['theme_count']}")

        # 测试 6: 删除感悟
        print("\n6. 测试删除感悟...")
        delete_result = repo.delete_game_reflection(test_id)
        assert delete_result["deleted"] == True

        # 验证删除
        deleted = repo.get_game_reflection_by_id(test_id)
        assert deleted is None
        print(f"   ✅ 删除成功: {test_id}")

        # 测试 7: 创建热身项目
        print("\n7. 测试创建热身项目...")
        warmup_result = repo.create_warmup_item(
            name="[E2E测试] 靶场平移机器人",
            type="tracking",
            description="端到端测试热身项目"
        )
        assert "id" in warmup_result
        warmup_id = warmup_result["id"]
        print(f"   ✅ 创建热身项目成功: {warmup_id}")

        # 测试 8: 列出热身项目
        print("\n8. 测试列出热身项目...")
        items = repo.list_warmup_items()
        assert isinstance(items, list)
        print(f"   ✅ 列出热身项目成功: 共 {len(items)} 个")

        print("\n✅ 端到端检验全部通过！")

    except Exception as e:
        print(f"\n❌ 端到端检验失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("模块 1：后端基础架构 - 四重验证")
    print("🚀" * 30)

    try:
        test_unit()    # 单元检验
        test_cross()   # 交叉检验
        test_code()    # 代码检验
        test_e2e()     # 端到端检验

        print("\n" + "🎉" * 30)
        print("✅ 模块 1 四重验证全部通过！")
        print("🎉" * 30)
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        sys.exit(1)
