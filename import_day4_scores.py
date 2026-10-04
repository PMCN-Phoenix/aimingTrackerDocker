import os
import csv
import requests
from datetime import datetime
from collections import defaultdict

stats_path = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'
list_name = 'viscose-s2-easier'

# 只读取今天（10/02）的文件
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
    
    # 读取文件，提取 Score 和时间戳
    score = None
    accuracy = None
    timestamp = None
    
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
    
    # 用文件修改时间作为时间戳
    timestamp = int(file_time.timestamp())
    
    if score is not None:
        scenarios[scenario].append({
            'score': score,
            'accuracy': accuracy if accuracy else 0,
            'timestamp': timestamp
        })

# 构建 Line Protocol 并写入
lines = []
for scenario, rounds in scenarios.items():
    # tag 值里的空格和逗号要转义
    scenario_tag = scenario.replace(' ', '\\ ').replace(',', '\\,')
    
    for round_data in rounds:
        ts = round_data['timestamp']
        score = round_data['score']
        accuracy = round_data['accuracy']
        
        # 写入 score
        line1 = f'aim_scenario,scenario={scenario_tag},list={list_name} score={score} {ts}'
        lines.append(line1)
        
        # 写入 accuracy
        line2 = f'aim_scenario,scenario={scenario_tag},list={list_name} accuracy={accuracy} {ts}'
        lines.append(line2)

# 分批写入（每批 100 行）
batch_size = 100
write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}

for i in range(0, len(lines), batch_size):
    batch = lines[i:i+batch_size]
    body = '\n'.join(batch)
    response = requests.post(write_url, headers=write_headers, data=body.encode('utf-8'))
    print(f"写入批次 {i//batch_size + 1}: 状态 {response.status_code}")

print(f"\n完成！共导入 {len(scenarios)} 个场景，{sum(len(v) for v in scenarios.values())} 轮数据")
