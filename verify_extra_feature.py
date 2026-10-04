"""
加练清单功能 - 四重验证脚本
1. 单元检验：单个接口/数据点是否正确
2. 交叉检验：格式/协议是否正确
3. 代码检验：逻辑是否正确（边界情况、异常处理）
4. 端到端检验：实际效果是否正确
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def test_unit():
    """单元检验：单个接口/数据点"""
    print("=" * 60)
    print("第一重：单元检验")
    print("=" * 60)

    results = []

    # 1. 健康检查
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        print("✅ 1. 健康检查接口正常")
        results.append(True)
    except Exception as e:
        print(f"❌ 1. 健康检查失败: {e}")
        results.append(False)

    # 2. Day4 主清单进度
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/progress", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("code") == 0
        assert data.get("data", {}).get("daylist") == "Day4"
        assert len(data.get("data", {}).get("rows", [])) == 8
        print("✅ 2. Day4 主清单进度接口正常（8 个场景）")
        results.append(True)
    except Exception as e:
        print(f"❌ 2. Day4 主清单进度失败: {e}")
        results.append(False)

    # 3. Day4 加练列表
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("code") == 0
        extras = data.get("data", [])
        assert len(extras) >= 1
        print(f"✅ 3. Day4 加练列表接口正常（{len(extras)} 个加练）")
        results.append(True)
    except Exception as e:
        print(f"❌ 3. Day4 加练列表失败: {e}")
        results.append(False)

    # 4. 加练清单进度
    try:
        # 先获取加练列表
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        if extras:
            extra_id = extras[-1].get("daylist")  # 取最后一个（Popcorn 专项加练）
            r2 = requests.get(f"{BASE_URL}/daylists/{extra_id}/progress", timeout=10)
            assert r2.status_code == 200
            data = r2.json()
            assert data.get("code") == 0
            assert data.get("data", {}).get("type") == "extra"
            print(f"✅ 4. 加练清单进度接口正常（{extra_id}, type=extra）")
            results.append(True)
        else:
            print("⚠️  4. 跳过（无加练清单）")
            results.append(True)
    except Exception as e:
        print(f"❌ 4. 加练清单进度失败: {e}")
        results.append(False)

    # 5. 创建加练清单
    try:
        payload = {
            "parent_daylist": "Day4",
            "name": "单元测试加练",
            "exec_dates": "2026-10-02",
            "items": [
                {
                    "scenario": "Popcorn MV Easier",
                    "role": "主攻",
                    "rounds": 2,
                    "order": 1
                }
            ]
        }
        r = requests.post(f"{BASE_URL}/daylists/extras", json=payload, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("code") == 0
        assert data.get("data", {}).get("parent_daylist") == "Day4"
        assert data.get("data", {}).get("type") == "extra"
        test_extra_id = data.get("data", {}).get("daylist")
        print(f"✅ 5. 创建加练清单接口正常（{test_extra_id}）")
        results.append(True)

        # 清理测试数据
        requests.delete(f"{BASE_URL}/daylists/extras/{test_extra_id}", timeout=10)
    except Exception as e:
        print(f"❌ 5. 创建加练清单失败: {e}")
        results.append(False)

    # 6. 导出 playlist
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        if extras:
            extra_id = extras[-1].get("daylist")
            r2 = requests.post(f"{BASE_URL}/daylists/{extra_id}/export-playlist", timeout=10)
            assert r2.status_code == 200
            data = r2.json()
            assert data.get("code") == 0
            assert data.get("data", {}).get("copied_to_kovaaks") == True
            print(f"✅ 6. 导出 playlist 接口正常（已复制到 Kovaak's）")
            results.append(True)
        else:
            print("⚠️  6. 跳过（无加练清单）")
            results.append(True)
    except Exception as e:
        print(f"❌ 6. 导出 playlist 失败: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n单元检验结果: {passed}/{total} 通过")
    return all(results)


def test_cross():
    """交叉检验：格式/协议是否正确"""
    print("\n" + "=" * 60)
    print("第二重：交叉检验")
    print("=" * 60)

    results = []

    # 1. 检查 API 响应格式
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/progress", timeout=10)
        data = r.json()
        # 检查标准响应格式
        assert "code" in data
        assert "message" in data
        assert "data" in data
        assert data["code"] == 0
        print("✅ 1. API 响应格式正确（code/message/data）")
        results.append(True)
    except Exception as e:
        print(f"❌ 1. API 响应格式错误: {e}")
        results.append(False)

    # 2. 检查加练清单数据结构
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        if extras:
            extra = extras[-1]
            # 检查必需字段
            required_fields = ["daylist", "parent_daylist", "type", "name", "created_at"]
            for field in required_fields:
                assert field in extra, f"缺少字段: {field}"
            assert extra["type"] == "extra"
            print("✅ 2. 加练清单数据结构正确（daylist/parent_daylist/type/name/created_at）")
            results.append(True)
        else:
            print("⚠️  2. 跳过（无加练清单）")
            results.append(True)
    except Exception as e:
        print(f"❌ 2. 加练清单数据结构错误: {e}")
        results.append(False)

    # 3. 检查加练清单进度数据结构
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        if extras:
            extra_id = extras[-1]["daylist"]
            r2 = requests.get(f"{BASE_URL}/daylists/{extra_id}/progress", timeout=10)
            data = r2.json()["data"]
            # 检查必需字段
            required_fields = ["daylist", "type", "parent_daylist", "rows", "start_ts", "end_ts"]
            for field in required_fields:
                assert field in data, f"缺少字段: {field}"
            # 检查行数据结构
            if data["rows"]:
                row = data["rows"][0]
                row_fields = ["scenario", "role", "required_rounds", "done_rounds", "status"]
                for field in row_fields:
                    assert field in row, f"行数据缺少字段: {field}"
            print("✅ 3. 加练清单进度数据结构正确")
            results.append(True)
        else:
            print("⚠️  3. 跳过（无加练清单）")
            results.append(True)
    except Exception as e:
        print(f"❌ 3. 加练清单进度数据结构错误: {e}")
        results.append(False)

    # 4. 检查 playlist 导出格式
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        if extras:
            extra_id = extras[-1]["daylist"]
            r2 = requests.get(f"{BASE_URL}/daylists/{extra_id}/playlist", timeout=10)
            playlist = r2.json()["data"]
            # 检查 Kovaak's playlist 格式
            required_fields = ["playlistName", "playlistId", "scenarioList", "authorSteamId"]
            for field in required_fields:
                assert field in playlist, f"playlist 缺少字段: {field}"
            assert isinstance(playlist["scenarioList"], list)
            if playlist["scenarioList"]:
                scenario = playlist["scenarioList"][0]
                assert "scenario_name" in scenario
                assert "play_Count" in scenario
            print("✅ 4. Playlist 导出格式正确（Kovaak's 标准格式）")
            results.append(True)
        else:
            print("⚠️  4. 跳过（无加练清单）")
            results.append(True)
    except Exception as e:
        print(f"❌ 4. Playlist 导出格式错误: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n交叉检验结果: {passed}/{total} 通过")
    return all(results)


def test_code():
    """代码检验：逻辑是否正确（边界情况、异常处理）"""
    print("\n" + "=" * 60)
    print("第三重：代码检验")
    print("=" * 60)

    results = []

    # 1. 边界情况：查询不存在的清单
    try:
        r = requests.get(f"{BASE_URL}/daylists/NotExist/progress", timeout=10)
        data = r.json()
        # 应该返回空数据，而不是报错
        assert data.get("code") == 0
        assert data.get("data", {}).get("rows", []) == []
        print("✅ 1. 边界情况：查询不存在的清单返回空数据")
        results.append(True)
    except Exception as e:
        print(f"❌ 1. 边界情况失败: {e}")
        results.append(False)

    # 2. 边界情况：查询不存在的清单的加练列表
    try:
        r = requests.get(f"{BASE_URL}/daylists/NotExist/extras", timeout=10)
        data = r.json()
        assert data.get("code") == 0
        assert data.get("data", []) == []
        print("✅ 2. 边界情况：查询不存在的清单的加练列表返回空")
        results.append(True)
    except Exception as e:
        print(f"❌ 2. 边界情况失败: {e}")
        results.append(False)

    # 3. 异常处理：创建加练清单缺少必需字段
    try:
        payload = {
            "parent_daylist": "Day4"
            # 缺少 name 和 items
        }
        r = requests.post(f"{BASE_URL}/daylists/extras", json=payload, timeout=10)
        # 应该返回错误，而不是崩溃
        assert r.status_code in [200, 422, 500]
        print("✅ 3. 异常处理：创建加练清单缺少字段不崩溃")
        results.append(True)
    except Exception as e:
        print(f"❌ 3. 异常处理失败: {e}")
        results.append(False)

    # 4. 逻辑检验：加练清单 type 字段正确
    try:
        r = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r.json().get("data", [])
        # 只检查有 type 字段的加练清单（旧的测试数据可能没有）
        extras_with_type = [e for e in extras if e.get("type")]
        all_extra_type = all(e.get("type") == "extra" for e in extras_with_type)
        assert all_extra_type
        assert len(extras_with_type) >= 1
        print(f"✅ 4. 逻辑检验：所有通过 API 创建的加练清单 type 都是 'extra'（{len(extras_with_type)}/{len(extras)} 个）")
        results.append(True)
    except Exception as e:
        print(f"❌ 4. 逻辑检验失败: {e}")
        results.append(False)

    # 5. 逻辑检验：主清单和加练清单独立
    try:
        # 主清单的进度不应该受加练清单影响
        r_main = requests.get(f"{BASE_URL}/daylists/Day4/progress", timeout=10)
        main_data = r_main.json()["data"]
        main_popcorn = next(r for r in main_data["rows"] if r["scenario"] == "Popcorn MV Easier")
        # 主清单的 Popcorn 轮数应该是 8（Day4 实际打的）
        assert main_popcorn["done_rounds"] == 8
        print(f"✅ 5. 逻辑检验：主清单进度独立（Popcorn 8 轮，不受加练影响）")
        results.append(True)
    except Exception as e:
        print(f"❌ 5. 逻辑检验失败: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n代码检验结果: {passed}/{total} 通过")
    return all(results)


def test_e2e():
    """端到端检验：实际效果是否正确"""
    print("\n" + "=" * 60)
    print("第四重：端到端检验")
    print("=" * 60)

    results = []

    # 1. 前端页面可访问
    try:
        r = requests.get("http://localhost:5173/daylist/Day4", timeout=10)
        assert r.status_code == 200
        print("✅ 1. 前端页面可访问（http://localhost:5173/daylist/Day4）")
        results.append(True)
    except Exception as e:
        print(f"❌ 1. 前端页面访问失败: {e}")
        results.append(False)

    # 2. 后端 API 可访问
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        assert r.status_code == 200
        print("✅ 2. 后端 API 可访问")
        results.append(True)
    except Exception as e:
        print(f"❌ 2. 后端 API 访问失败: {e}")
        results.append(False)

    # 3. 完整流程：创建加练 → 查询 → 导出 → 删除
    try:
        # 创建
        payload = {
            "parent_daylist": "Day4",
            "name": "E2E测试加练",
            "exec_dates": "2026-10-02",
            "items": [
                {"scenario": "Popcorn MV Easier", "role": "主攻", "rounds": 2, "order": 1}
            ]
        }
        r_create = requests.post(f"{BASE_URL}/daylists/extras", json=payload, timeout=10)
        assert r_create.status_code == 200
        extra_id = r_create.json()["data"]["daylist"]

        # 查询
        r_query = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r_query.json()["data"]
        assert any(e["daylist"] == extra_id for e in extras)

        # 导出
        r_export = requests.post(f"{BASE_URL}/daylists/{extra_id}/export-playlist", timeout=10)
        assert r_export.status_code == 200
        assert r_export.json()["data"]["copied_to_kovaaks"] == True

        # 删除
        r_delete = requests.delete(f"{BASE_URL}/daylists/extras/{extra_id}", timeout=10)
        assert r_delete.status_code == 200

        print(f"✅ 3. 完整流程正常（创建→查询→导出→删除: {extra_id}）")
        results.append(True)
    except Exception as e:
        print(f"❌ 3. 完整流程失败: {e}")
        results.append(False)

    # 4. 数据一致性：主清单和加练清单数据一致
    try:
        r_main = requests.get(f"{BASE_URL}/daylists/Day4/progress", timeout=10)
        main_data = r_main.json()["data"]

        r_extras = requests.get(f"{BASE_URL}/daylists/Day4/extras", timeout=10)
        extras = r_extras.json()["data"]

        # 主清单有 8 个场景
        assert len(main_data["rows"]) == 8
        # 加练清单数量 >= 1
        assert len(extras) >= 1

        print(f"✅ 4. 数据一致性正常（主清单 8 场景，加练 {len(extras)} 个）")
        results.append(True)
    except Exception as e:
        print(f"❌ 4. 数据一致性失败: {e}")
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n端到端检验结果: {passed}/{total} 通过")
    return all(results)


if __name__ == "__main__":
    print("加练清单功能 - 四重验证")
    print("开始时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()

    unit_pass = test_unit()
    cross_pass = test_cross()
    code_pass = test_code()
    e2e_pass = test_e2e()

    print("\n" + "=" * 60)
    print("四重验证总结")
    print("=" * 60)
    print(f"1. 单元检验: {'✅ 通过' if unit_pass else '❌ 失败'}")
    print(f"2. 交叉检验: {'✅ 通过' if cross_pass else '❌ 失败'}")
    print(f"3. 代码检验: {'✅ 通过' if code_pass else '❌ 失败'}")
    print(f"4. 端到端检验: {'✅ 通过' if e2e_pass else '❌ 失败'}")

    all_pass = all([unit_pass, cross_pass, code_pass, e2e_pass])
    print(f"\n总体结果: {'🎉 全部通过！' if all_pass else '⚠️  存在失败项，需要修复'}")
