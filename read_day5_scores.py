import os
import csv
import json
from collections import defaultdict
from datetime import datetime

stats_path = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"

# 只读取今天（10/03）的文件
today = datetime.now().date()

scenarios = defaultdict(list)

for filename in os.listdir(stats_path):
    if not filename.endswith('.csv'):
        continue

    filepath = os.path.join(stats_path, filename)
    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))

    # 只处理今天的文件
    if file_time.date() != today:
        continue

    # 提取场景名
    scenario = filename.split(' - Challenge - ')[0]

    # 读取文件，提取 Score
    score = None
    accuracy = None

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('Score:,'):
            try:
                score = float(line.strip().split(',')[1])
            except:
                pass
        elif line.startswith('Accuracy:,'):
            try:
                accuracy = float(line.strip().split(',')[1])
            except:
                pass

    if score is not None:
        scenarios[scenario].append({
            'score': score,
            'accuracy': accuracy if accuracy else 0,
            'timestamp': int(file_time.timestamp())
        })

# 输出结果
print("=== Day5 成绩汇总（10/03）===")
print()
for scenario in sorted(scenarios.keys()):
    rounds = scenarios[scenario]
    best_score = max(r['score'] for r in rounds)
    best_acc = max(r['accuracy'] for r in rounds)
    print(f"  - {scenario}:")
    print(f"    最佳分数: {best_score}")
    print(f"    命中率: {best_acc}%")
    print(f"    轮数: {len(rounds)}")
    print(f"    所有分数: {[r['score'] for r in rounds]}")
    print()

# 保存到 JSON 文件，等 InfluxDB 启动后再导入
output_data = {
    'date': '2026-10-03',
    'scenarios': dict(scenarios)
}

with open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\day5_scores_temp.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("成绩数据已保存到 day5_scores_temp.json，等 InfluxDB 启动后再导入")
