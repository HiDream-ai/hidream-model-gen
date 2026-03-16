#!/usr/bin/env python3
"""
视频首尾帧测试脚本 - Keyframe-to-Video
"""
import os
import sys

sys.path.insert(0, '/root/.openclaw/skills/vivago-ai/scripts')

from vivago_client import create_client
import json

def test_keyframe_to_video():
    print("🎬 测试视频首尾帧功能 (Keyframe-to-Video)")
    print("=" * 60)
    
    # 使用之前生成的图片UUID
    # 皮卡丘: p_a78df93d-7af6-4927-a793-197e790761e6
    # 柯基: p_302c9e53-ac49-459b-b034-c9c79ec9b50c
    
    start_image = "p_a78df93d-7af6-4927-a793-197e790761e6"  # 皮卡丘
    end_image = "p_302c9e53-ac49-459b-b034-c9c79ec9b50c"     # 柯基
    
    prompt = "皮卡丘变成了一只柯基"
    
    print(f"\n📋 测试参数:")
    print(f"   Prompt: {prompt}")
    print(f"   起始帧: {start_image}")
    print(f"   结束帧: {end_image}")
    print(f"   模型: v3L (Vivago.ai 2.0 360p)")
    print(f"   比例: keep")
    print(f"   时长: 5秒")
    print(f"   预计需要 2-3 分钟...")
    print()
    
    try:
        client = create_client()
        
        results = client.keyframe_to_video(
            prompt=prompt,
            start_image_uuid=start_image,
            end_image_uuid=end_image,
            port='v3L',
            wh_ratio='keep',
            duration=5,
            mode='Fast',
            fast_mode=True
        )
        
        print("\n" + "=" * 60)
        
        if results:
            print("✅ 生成成功!")
            print(f"\n📊 结果详情:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
            # 获取视频信息
            for i, result in enumerate(results):
                video_id = result.get('video')
                if video_id:
                    video_url = f"https://media.vivago.ai/{video_id}"
                    print(f"\n🎥 生成的视频 {i+1}:")
                    print(f"   Video ID: {video_id}")
                    print(f"   视频链接: {video_url}")
                    
                    # 保存视频信息
                    with open('/tmp/keyframe_video_info.txt', 'w') as f:
                        f.write(f"{video_id}\n{video_url}")
                    
                    # 飞书消息格式
                    print(f"\n📱 飞书消息格式:")
                    print(f"   🎬 视频首尾帧生成完成！")
                    print(f"   📹 {video_url}")
                    print(f"   📋 皮卡丘 → 柯基的变身视频")
            
            return True
        else:
            print("❌ 生成失败: 未返回结果")
            return False
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_keyframe_to_video()
    sys.exit(0 if success else 1)
