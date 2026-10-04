"""
验证 Day7 playlist 场景名，并写入游戏目录
"""
import json
import shutil
import os

# 路径
benchmark_path = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists\Viscose Benchmark S2 - Easier.json"
day7_backup_path = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\清单\viscose训练提升清单日期推进\Viscose基准-Day7游玩清单.playlist.json"
game_playlist_dir = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists"
game_day7_path = os.path.join(game_playlist_dir, "Viscose Day7 - 攻Wrist.json")

# 读取 Benchmark playlist
with open(benchmark_path, "r", encoding="utf-8") as f:
    benchmark = json.load(f)

benchmark_scenarios = set(s["scenario_name"] for s in benchmark["scenarioList"])
print(f"Benchmark 场景数: {len(benchmark_scenarios)}")

# 读取 Day7 playlist
with open(day7_backup_path, "r", encoding="utf-8") as f:
    day7 = json.load(f)

day7_scenarios = list(s["scenario_name"] for s in day7["scenarioList"])
day7_unique_scenarios = set(day7_scenarios)
total_rounds = sum(s["play_Count"] for s in day7["scenarioList"])

print(f"\n=== 场景名验证 ===")
all_match = True
for s in sorted(day7_unique_scenarios):
    if s in benchmark_scenarios:
        print(f"✅ {s}")
    else:
        print(f"❌ {s} - 不在 Benchmark 中！")
        all_match = False

print(f"\n=== 统计 ===")
print(f"Day7 场景条目数: {len(day7['scenarioList'])}")
print(f"Day7 唯一场景数: {len(day7_unique_scenarios)}")
print(f"Day7 总轮数: {total_rounds}")

if all_match:
    print(f"\n✅ 所有场景名验证通过！")
    
    # 写入游戏目录
    print(f"\n=== 写入游戏目录 ===")
    print(f"目标: {game_day7_path}")
    
    # 检查是否已存在
    if os.path.exists(game_day7_path):
        print(f"⚠️  文件已存在，将覆盖")
        # 备份旧文件
        backup_path = game_day7_path + ".bak"
        shutil.copy2(game_day7_path, backup_path)
        print(f"已备份到: {backup_path}")
    
    # 复制文件
    shutil.copy2(day7_backup_path, game_day7_path)
    print(f"✅ 已写入游戏目录")
    
    # 回读验证
    with open(game_day7_path, "r", encoding="utf-8") as f:
        verify = json.load(f)
    
    verify_rounds = sum(s["play_Count"] for s in verify["scenarioList"])
    print(f"\n=== 回读验证 ===")
    print(f"playlistName: {verify['playlistName']}")
    print(f"场景条目数: {len(verify['scenarioList'])}")
    print(f"总轮数: {verify_rounds}")
    
    if verify_rounds == total_rounds and verify["playlistName"] == "Viscose Day7 - 攻Wrist":
        print(f"✅ 回读验证通过！")
    else:
        print(f"❌ 回读验证失败！")
    
else:
    print(f"\n❌ 有场景名不匹配，未写入游戏目录！")
