"""
导入 Day6（2026-10-04）的 Kovaak's stats 数据到 InfluxDB
"""
import os
import re
import requests
from datetime import datetime

# 配置
INFLUX_URL = "http://127.0.0.1:8087"
TOKEN = "aim-super-secret-token-2026"
ORG = "aim-org"
BUCKET = "aim"
LIST_NAME = "viscose-s2-easier"

STATS_DIR = r"D:\1_game\1_steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
TARGET_DATE = "2026.10.04"  # Kovaak's 文件名中的日期格式

def parse_stats_file(filepath):
    """解析单个 Kovaak's stats CSV 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取分数
        score_match = re.search(r'Score:,\s*([\d.]+)', content)
        score = float(score_match.group(1)) if score_match else 0
        
        # 提取命中数和未命中数
        hit_match = re.search(r'Hit Count:,\s*(\d+)', content)
        miss_match = re.search(r'Miss Count:,\s*(\d+)', content)
        hits = int(hit_match.group(1)) if hit_match else 0
        misses = int(miss_match.group(1)) if miss_match else 0
        accuracy = hits / (hits + misses) if (hits + misses) > 0 else 0
        
        # 提取场景名
        scenario_match = re.search(r'Scenario:,\s*(.+)', content)
        scenario = scenario_match.group(1).strip() if scenario_match else ""
        
        # 从文件名提取时间
        filename = os.path.basename(filepath)
        time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})-(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            date_str = time_match.group(1).replace('.', '-')
            time_str = time_match.group(2).replace('.', ':')
            datetime_str = f"{date_str} {time_str}"
            timestamp = int(datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp())
        else:
            timestamp = int(os.path.getmtime(filepath))
        
        return {
            'scenario': scenario,
            'score': score,
            'accuracy': accuracy,
            'timestamp': timestamp,
            'hits': hits,
            'misses': misses
        }
    except Exception as e:
        print(f"  解析失败 {filepath}: {e}")
        return None

def main():
    print("=" * 80)
    print(f"导入 Day6 ({TARGET_DATE}) Kovaak's stats 数据")
    print("=" * 80)
    
    # 扫描今天的 stats 文件
    stats_files = []
    for f in os.listdir(STATS_DIR):
        if f.endswith('.csv') and TARGET_DATE in f:
            stats_files.append(os.path.join(STATS_DIR, f))
    
    stats_files.sort(key=lambda x: os.path.getmtime(x))
    print(f"\n找到 {len(stats_files)} 个今天的 stats 文件")
    
    # 解析所有文件
    all_data = []
    for filepath in stats_files:
        data = parse_stats_file(filepath)
        if data:
            all_data.append(data)
            print(f"  ✓ {data['scenario']}: 分数 {data['score']:.0f}, 命中率 {data['accuracy']*100:.1f}%")
    
    print(f"\n共解析 {len(all_data)} 轮数据")
    
    # 按场景分组统计
    from collections import defaultdict
    by_scenario = defaultdict(list)
    for d in all_data:
        by_scenario[d['scenario']].append(d)
    
    print("\n按场景统计:")
    for scn, rounds in by_scenario.items():
        scores = [r['score'] for r in rounds]
        print(f"  {scn}: {len(rounds)}轮, 平均 {sum(scores)/len(scores):.1f}, 最高 {max(scores):.0f}")
    
    # 写入 InfluxDB
    print("\n" + "=" * 80)
    print("写入 InfluxDB")
    print("=" * 80)
    
    lines = []
    for d in all_data:
        # tag 值里的空格和逗号要转义
        scenario_tag = d['scenario'].replace(' ', '\\ ').replace(',', '\\,')
        ts = d['timestamp']
        
        # 写入 score（纳秒级时间戳）
        line1 = f'aim_scenario,scenario={scenario_tag},list={LIST_NAME} score={d["score"]} {ts * 1000000000}'
        lines.append(line1)
        
        # 写入 accuracy
        line2 = f'aim_scenario,scenario={scenario_tag},list={LIST_NAME} accuracy={d["accuracy"]} {ts * 1000000000}'
        lines.append(line2)
    
    # 分批写入
    batch_size = 100
    write_url = f'{INFLUX_URL}/api/v2/write?org={ORG}&bucket={BUCKET}'
    write_headers = {'Authorization': f'Token {TOKEN}', 'Content-Type': 'text/plain; charset=utf-8'}
    
    success = 0
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i+batch_size]
        body = '\n'.join(batch)
        response = requests.post(write_url, headers=write_headers, data=body.encode('utf-8'))
        if response.status_code == 204:
            success += len(batch)
            print(f"  批次 {i//batch_size + 1}: ✅ 写入 {len(batch)} 条")
        else:
            print(f"  批次 {i//batch_size + 1}: ❌ 失败 {response.status_code} - {response.text}")
    
    print(f"\n完成！共写入 {success} 条数据（{len(all_data)} 轮 × 2 字段）")
    
    # 保存临时数据供后续分析
    temp_data = {
        'date': TARGET_DATE,
        'total_rounds': len(all_data),
        'scenarios': {}
    }
    for scn, rounds in by_scenario.items():
        temp_data['scenarios'][scn] = [
            {'score': r['score'], 'accuracy': r['accuracy'], 'timestamp': r['timestamp']}
            for r in rounds
        ]
    
    with open(r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\day6_scores_temp.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(temp_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n临时数据已保存到 day6_scores_temp.json")

if __name__ == "__main__":
    main()
