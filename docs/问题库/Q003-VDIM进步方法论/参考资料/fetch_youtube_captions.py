import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7892'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7892'

import requests
import re
import json
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

video_id = 'XMxIHLXJhY8'
out_dir = r'D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\VDIM进步调研'

# 1. 获取视频页面
print('Fetching video page...')
r = requests.get(f'https://www.youtube.com/watch?v={video_id}', headers=headers, timeout=30)
print(f'Page status: {r.status_code}, length: {len(r.text)}')

# 2. 提取字幕 baseUrl
match = re.search(r'"captionTracks":\[(.*?)\]', r.text)
if not match:
    print('No captionTracks found')
    exit(1)

caption_data = match.group(1)
url_match = re.search(r'"baseUrl":"([^"]+)"', caption_data)
if not url_match:
    print('No baseUrl found')
    exit(1)

raw_url = url_match.group(1)
caption_url = raw_url.replace('\\u0026', '&')
print(f'Caption URL found, length: {len(caption_url)}')

# 3. 访问字幕 URL
print('Fetching captions...')
r2 = requests.get(caption_url, headers=headers, timeout=30)
print(f'Caption status: {r2.status_code}, length: {len(r2.content)}, content-type: {r2.headers.get("Content-Type")}')

if len(r2.content) == 0:
    print('Empty content, trying with fmt parameter...')
    # 试试加 fmt 参数
    fmt_url = caption_url + '&fmt=srv3'
    r3 = requests.get(fmt_url, headers=headers, timeout=30)
    print(f'fmt=srv3 status: {r3.status_code}, length: {len(r3.content)}')
    if len(r3.content) > 0:
        r2 = r3
    else:
        print('Still empty. Trying json3...')
        fmt_url2 = caption_url + '&fmt=json3'
        r4 = requests.get(fmt_url2, headers=headers, timeout=30)
        print(f'fmt=json3 status: {r4.status_code}, length: {len(r4.content)}')
        if len(r4.content) > 0:
            r2 = r4

if len(r2.content) == 0:
    print('FAILED: All caption requests returned empty content')
    exit(1)

# 保存原始内容
with open(os.path.join(out_dir, 'lg56_vdim_main_raw.txt'), 'w', encoding='utf-8') as f:
    f.write(r2.text)
print(f'Saved raw content, first 300 chars: {r2.text[:300]}')

# 尝试解析
text = ''
try:
    # 尝试 XML 解析
    root = ET.fromstring(r2.content)
    texts = [elem.text for elem in root.iter() if elem.text]
    text = ' '.join(texts)
    print(f'XML parsed, {len(texts)} text elements')
except Exception as e:
    print(f'XML parse failed: {e}')
    try:
        # 尝试 JSON 解析
        data = r2.json()
        if 'events' in data:
            texts = []
            for event in data['events']:
                if 'segs' in event:
                    for seg in event['segs']:
                        if 'utf8' in seg:
                            texts.append(seg['utf8'])
            text = ' '.join(texts)
            print(f'JSON parsed, {len(texts)} segments')
    except Exception as e2:
        print(f'JSON parse also failed: {e2}')
        text = r2.text

print(f'Final text length: {len(text)}')
print(f'First 500 chars: {text[:500]}')

# 保存纯文本
with open(os.path.join(out_dir, 'lg56_vdim_main.txt'), 'w', encoding='utf-8') as f:
    f.write(text)
print('Saved lg56_vdim_main.txt')
