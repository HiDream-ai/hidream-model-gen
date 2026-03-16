#!/usr/bin/env python3
"""
验证新上传方式生成的图片 UUID 是否可用
使用图生视频功能进行验证
"""
import os
import sys
import time

sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

# 加载环境变量
with open('/root/.openclaw/workspace/skills/vivago-ai-skill/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from scripts.vivago_client import create_client

# 刚才上传成功的图片 UUID
TEST_IMAGE_UUID = "j_aaa28c3d-234e-4d6e-9f72-0342514ff2a8"

print("="*70)
print("验证新上传图片 UUID 可用性")
print("="*70)
print(f"\n测试图片 UUID: {TEST_IMAGE_UUID}")
print(f"上传方式: 新预签名 URL 方式 (v2)")

client = create_client()

print("\n" + "="*70)
print("测试: 图生视频 (Image-to-Video)")
print("="*70)
print(f"端口: v3L (360p)")
print(f"积分: 20")
print(f"\n⏳ 开始生成视频，请耐心等待...")
print(f"   提示: 视频生成可能需要 2-5 分钟\n")

try:
    result = client.image_to_video(
        prompt='camera slowly zooming out from the subject, gentle movement',
        image_uuid=TEST_IMAGE_UUID,
        port='v3L',
        duration=5,
        wh_ratio='1:1'
    )
    
    if result and len(result) > 0:
        video_info = result[0]
        print("\n" + "="*70)
        print("✅ 图生视频成功!")
        print("="*70)
        print(f"\n📊 结果详情:")
        print(f"   视频 UUID: {video_info.get('video', 'N/A')}")
        print(f"   任务状态: {video_info.get('task_status')}")
        print(f"   算法版本: {video_info.get('algo_version')}")
        print(f"   种子: {video_info.get('seed')}")
        
        video_url = f"https://media.vivago.ai/{video_info.get('video')}"
        print(f"\n🎬 视频地址:")
        print(f"   {video_url}")
        
        print("\n" + "="*70)
        print("✅ 验证结论")
        print("="*70)
        print("\n新上传方式生成的图片 UUID 完全可用!")
        print("  ✅ 图片上传成功")
        print("  ✅ UUID 可被 API 识别")
        print("  ✅ 图生视频功能正常")
        print("\n结论: 新上传方式可以正式替换旧实现")
        
    else:
        print("\n" + "="*70)
        print("❌ 图生视频失败: 无结果")
        print("="*70)
        
except Exception as e:
    print("\n" + "="*70)
    print("❌ 图生视频失败")
    print("="*70)
    print(f"\n错误信息: {e}")
    import traceback
    traceback.print_exc()
