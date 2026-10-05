"""
导入 Day7（2026-10-05）的 Kovaak's stats 数据到 InfluxDB
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
TARGET_DATE = "2026.10.05"  # Kovaak's 文件名中的日期格式

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

def write_to_influxdb(data):
    """写入数据到 InfluxDB"""
    # 构造 line protocol
    lines = []
    for d in data:
        # 转义场景名中的空格和逗号
        scenario = d['scenario'].replace(' ', '\\ ').replace(',', '\\,')
        line = (
            f"kovaak_score,scenario={scenario},list={LIST_NAME} "
            f"score={d['score']},accuracy={d['accuracy']},hits={d['hits']},misses={d['misses']} "
            f"{d['timestamp']}000000000"
        )
        lines.append(line)
    
    payload = '\n'.join(lines)
    
    headers = {
        'Authorization': f'Token {TOKEN}',
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    url = f"{INFLUX_URL}/api/v2/write?org={ORG}&bucket={BUCKET}&precision=ns"
    response = requests.post(url, data=payload.encode('utf-8'), headers=headers, timeout=30)
    
    if response.status_code == 204:
        return True
    else:
        print(f"  写入失败: {response.status_code} - {response.text}")
        return False

def main():
    print("=" * 80)
    print(f"导入 Day7 ({TARGET_DATE}) Kovaak's stats 数据")
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
    scenario_counts = {}
    for filepath in stats_files:
        data = parse_stats_file(filepath)
        if data:
            all_data.append(data)
            scenario = data['scenario']
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
    
    print(f"\n成功解析 {len(all_data)} 个文件")
    print("\n按场景统计:")
    for scenario, count in sorted(scenario_counts.items()):
        print(f"  {scenario}: {count} 次")
    
    # 显示每个场景的最高分
    print("\n各场景最高分:")
    scenario_scores = {}
    for d in all_data:
        s = d['scenario']
        if s not in scenario_scores or d['score'] > scenario_scores[s]['score']:
            scenario_scores[s] = d
    for scenario, d in sorted(scenario_scores.items()):
        print(f"  {scenario}: {d['score']:.0f} (命中率 {d['accuracy']*100:.1f}%)")
    
    # 写入 InfluxDB
    print(f"\n写入 {len(all_data)} 条数据到 InfluxDB...")
    success = write_to_influxdb(all_data)
    
    if success:
        print("✅ 数据导入成功！")
    else:
        print("❌ 数据导入失败！")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
