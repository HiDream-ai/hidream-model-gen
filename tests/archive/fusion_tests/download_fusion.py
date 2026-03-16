#!/usr/bin/env python3
"""
下载融合宝可梦图片
"""
import sys
import os
import requests

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

TOKEN = os.environ.get('HIDREAM_TOKEN')

# 融合图片的UUID
image_uuid = 'p_fdcc4f96-4182-4627-a66f-581b2d0724ad'

print(f'🎨 下载融合宝可梦图片: {image_uuid}')
print()

# 使用 storage URL 格式下载
urls_to_try = [
    f"https://storage.vivago.ai/image/{image_uuid}.jpg",
    f"https://storage.vivago.ai/image/{image_uuid}.png",
]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-accept-language": "en"
}

output_path = '/tmp/fusion_pokemon.jpg'

for url in urls_to_try:
    print(f'尝试: {url}')
    try:
        resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f'  状态码: {resp.status_code}')
        print(f'  内容长度: {len(resp.content)} bytes')
        
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            print(f'✅ 图片下载成功: {output_path}')
            print(f'📁 文件大小: {len(resp.content)} bytes')
            break
        else:
            print(f'  尝试下一个URL...')
    except Exception as e:
        print(f'  错误: {e}')
        continue

# 检查文件
if os.path.exists(output_path):
    size = os.path.getsize(output_path)
    print()
    print('='*60)
    print(f'✅ 图片已准备好: {output_path}')
    print(f'📊 文件大小: {size} bytes')
    print('='*60)
else:
    print('❌ 下载失败')
