import requests
import json

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'
list_name = 'viscose-s2-easier'

# 读取保存的成绩数据
with open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\day5_scores_temp.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

scenarios = data['scenarios']

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

total_rounds = sum(len(v) for v in scenarios.values())
print(f"开始导入 Day5 成绩数据：{len(scenarios)} 个场景，{total_rounds} 轮")

for i in range(0, len(lines), batch_size):
    batch = lines[i:i+batch_size]
    body = '\n'.join(batch)
    response = requests.post(write_url, headers=write_headers, data=body.encode('utf-8'))
    print(f"  写入批次 {i//batch_size + 1}: 状态 {response.status_code}")

print(f"\n完成！共导入 {len(scenarios)} 个场景，{total_rounds} 轮数据")
