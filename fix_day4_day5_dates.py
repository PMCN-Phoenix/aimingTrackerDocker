import requests
from datetime import datetime, timedelta

influx_url = 'http://127.0.0.1:8087'
token = 'aim-super-secret-token-2026'
org = 'aim-org'
bucket = 'aim'

def update_daylist_date(daylist, date_str):
    """更新某个清单的日期"""
    # Python 进程时区是北京时间，timestamp() 返回的就是正确的 UTC 时间戳
    first_date = datetime.strptime(date_str, '%Y-%m-%d')
    start_ts = int(first_date.timestamp())
    last_dt = first_date + timedelta(days=1) - timedelta(seconds=1)
    end_ts = int(last_dt.timestamp())
    
    print(f"{daylist} 新日期: {date_str}")
    print(f"  start_ts: {start_ts} ({datetime.utcfromtimestamp(start_ts)})")
    print(f"  end_ts: {end_ts} ({datetime.utcfromtimestamp(end_ts)})")
    
    # 删除旧的元数据
    delete_url = f'{influx_url}/api/v2/delete?org={org}&bucket={bucket}'
    delete_body = {
        "start": "1970-01-01T00:00:00Z",
        "stop": "2099-12-31T23:59:59Z",
        "predicate": f'_measurement="aim_daylist_meta" AND daylist="{daylist}"'
    }
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    response = requests.post(delete_url, headers=headers, json=delete_body)
    print(f"  删除旧元数据状态: {response.status_code}")
    
    # 写入新的元数据
    ts = start_ts
    meta_lines = f'''aim_daylist_meta,daylist={daylist} start_ts={start_ts} {ts}
aim_daylist_meta,daylist={daylist} end_ts={end_ts} {ts}
aim_daylist_meta,daylist={daylist} run_date="{date_str}" {ts}
aim_daylist_meta,daylist={daylist} exec_dates="{date_str}" {ts}
aim_daylist_meta,daylist={daylist} items=8 {ts}
aim_daylist_meta,daylist={daylist} rounds_total=29 {ts}'''
    
    if daylist == 'Day4':
        meta_lines += f'\naim_daylist_meta,daylist={daylist} label="Day4 攻Arm" {ts}'
    elif daylist == 'Day5':
        meta_lines += f'\naim_daylist_meta,daylist={daylist} label="Day5 攻Precision" {ts}'
    
    write_url = f'{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s'
    write_headers = {'Authorization': f'Token {token}', 'Content-Type': 'text/plain; charset=utf-8'}
    response = requests.post(write_url, headers=write_headers, data=meta_lines.encode('utf-8'))
    print(f"  写入新元数据状态: {response.status_code}")
    print()

# 更新 Day4 和 Day5 的日期
update_daylist_date('Day4', '2026-10-02')
update_daylist_date('Day5', '2026-10-03')

print("完成！Day4 和 Day5 的日期已修复")
