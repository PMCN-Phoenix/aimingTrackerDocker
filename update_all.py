#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
练枪看板 · 一键更新脚本
========================
按依赖顺序执行完整更新链路：
  0. 数据导入        Kovaak's stats → /import-aim；Aim Lab → aimlab_import.py；节拍 → tempo_sync.py
  1. sync_lists.py --build   生成/更新 scenario_lists.json（唯一事实来源）
  2. sync_lists.py            按清单更新 Node-RED flows.json（需先停 aim-nodered）
  3. bench_rows.py            物化 aim_bench_row + aim_bench_meta（最佳分口径 + 实时子类档位）
  4. daylist_sync.py          同步今日清单（aim_daylist + aim_daylist_meta）
  5. build_dashboard.py       生成全部看板 JSON（provisioning 30s 自动重载）

用法:
  python update_all.py              # 完整更新（步骤 0→5）——打完枪跑这一条即可
  python update_all.py --data-only  # 只导入数据，不重建看板（最快）
  python update_all.py --skip-nodered  # 跳过步骤 2（Node-RED 未停时）
  python update_all.py --check      # 只做一致性检查，不写任何数据
"""
import sys
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))

def run(script, *args, desc=""):
    """运行一个 Python 脚本，返回 (success, output)"""
    cmd = [sys.executable, os.path.join(BASE, script)] + list(args)
    print(f"\n{'='*60}")
    print(f"  {desc or script}")
    print(f"  $ python {script} {' '.join(args)}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=BASE)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  ⚠ 超时（120s）")
        return False
    except Exception as e:
        print(f"  ✗ 异常: {e}")
        return False

def http_post(path, timeout=300):
    """调用 Node-RED HTTP 接口（数据导入 / 分析）"""
    import urllib.request, urllib.error
    url = "http://127.0.0.1:1881" + path
    print(f"\n{'='*60}")
    print(f"  POST {url}")
    print(f"{'='*60}")
    try:
        req = urllib.request.Request(url, data=b"", method="POST")
        body = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        print("  " + body[:600])
        return True
    except Exception as e:
        print(f"  ✗ 失败: {e}（Node-RED 未启动？先跑 docker compose up -d）")
        return False


def import_data():
    """步骤 0：把新数据拉进库（Kovaak's → Aim Lab → 节拍）"""
    ok_a = http_post("/import-aim")
    ok_b = run("aimlab_import.py", desc="步骤 0b/6: 导入 Aim Lab Replay")
    ok_c = run("tempo_sync.py", desc="步骤 0c/6: 同步节拍 BPM")
    return ok_a and ok_b and ok_c


def main():
    skip_nodered = "--skip-nodered" in sys.argv
    check_only = "--check" in sys.argv
    data_only = "--data-only" in sys.argv

    if check_only:
        print("🔍 检查模式（不写数据）")
        ok1 = run("sync_lists.py", "--check", desc="步骤 1: 清单一致性检查")
        ok3 = run("bench_rows.py", "--show", desc="步骤 3: 档位物化状态")
        ok4 = run("daylist_sync.py", "--list", desc="步骤 4: 今日清单状态")
        print(f"\n{'='*60}")
        print(f"  检查完成: 清单={'✅' if ok1 else '❌'} 档位={'✅' if ok3 else '❌'} 清单={'✅' if ok4 else '❌'}")
        return

    print("🚀 练枪看板 · 一键更新")

    # 步骤 0: 数据导入（Kovaak's / Aim Lab / 节拍）
    ok0 = import_data()
    if not ok0:
        print("  ⚠ 步骤 0 有失败项，继续后续步骤（已有数据仍会刷新）")

    if data_only:
        print(f"\n{'='*60}")
        print(f"  ✅ 数据导入完成（--data-only 模式，未重建看板）")
        print(f"{'='*60}")
        return

    if skip_nodered:
        print("  (跳过 Node-RED flows 更新)")

    # 步骤 1: 生成 scenario_lists.json
    ok1 = run("sync_lists.py", "--build", desc="步骤 1/6: 生成 scenario_lists.json")
    if not ok1:
        print("  ✗ 步骤 1 失败，终止")
        sys.exit(1)

    # 步骤 2: 更新 Node-RED flows（可选）
    if not skip_nodered:
        ok2 = run("sync_lists.py", desc="步骤 2/6: 更新 Node-RED flows.json")
        if not ok2:
            print("  ⚠ 步骤 2 失败（可能 Node-RED 未停），继续后续步骤")
    else:
        print("\n  步骤 2/6: 跳过 Node-RED flows 更新")

    # 步骤 3: 物化档位数据
    ok3 = run("bench_rows.py", desc="步骤 3/6: 物化 aim_bench_row + aim_bench_meta")
    if not ok3:
        print("  ✗ 步骤 3 失败，终止")
        sys.exit(1)

    # 步骤 4: 同步今日清单
    ok4 = run("daylist_sync.py", desc="步骤 4/6: 同步今日清单 aim_daylist")
    if not ok4:
        print("  ⚠ 步骤 4 失败（可能无今日清单），继续后续步骤")

    # 步骤 5: 生成看板 JSON
    ok5 = run("build_dashboard.py", desc="步骤 5/6: 生成全部看板 JSON")
    if not ok5:
        print("  ✗ 步骤 5 失败")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  ✅ 更新完成！Grafana provisioning 将在 30 秒内自动重载看板")
    print(f"  看板地址: http://127.0.0.1:3001")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
