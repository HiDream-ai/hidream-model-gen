#!/usr/bin/env python3
"""
使用 vivago_client.template_to_video 测试 1970s
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

from vivago_client import create_client
import time
from datetime import datetime

client = create_client()

print("="*60)
print("使用 template_to_video 方法测试 1970s")
print("="*60)
print(f"开始: {datetime.now().isoformat()}")

start = time.time()
try:
    result = client.template_to_video(
        image_input='j_daeef3b0-9cd7-4741-87e8-31fab45f89c1',
        template='1970s',
        wh_ratio='1:1'
    )
    elapsed = time.time() - start
    print(f"\n完成: {datetime.now().isoformat()}")
    print(f"耗时: {elapsed:.1f}秒")
    print(f"结果: {result}")
    
except Exception as e:
    elapsed = time.time() - start
    print(f"\n错误 ({elapsed:.1f}秒): {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
