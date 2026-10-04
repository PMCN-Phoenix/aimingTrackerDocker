import os
import csv
from collections import defaultdict

stats_path = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"

# 只读取今天（10/02）的文件
from datetime import datetime
today = datetime.now().date()

scenarios = defaultdict(lambda: {'best_score': 0, 'best_accuracy': 0, 'rounds': 0, 'scores': []})

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
    
    # 读取文件
    score = None
    accuracy = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 搜索 Score 和 Accuracy
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
        scenarios[scenario]['rounds'] += 1
        scenarios[scenario]['scores'].append(score)
        if score > scenarios[scenario]['best_score']:
            scenarios[scenario]['best_score'] = score
            scenarios[scenario]['best_accuracy'] = accuracy if accuracy else 0

# 输出结果
print("=== Day4 成绩汇总（10/02）===")
print()
for scenario in sorted(scenarios.keys()):
    data = scenarios[scenario]
    print(f"  - {scenario}:")
    print(f"    最佳分数: {data['best_score']}")
    print(f"    命中率: {data['best_accuracy']}%")
    print(f"    轮数: {data['rounds']}")
    print(f"    所有分数: {data['scores']}")
    print()
