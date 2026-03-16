#!/usr/bin/env python3
"""
视频模板测试脚本 - Template-to-Video
Renovation of Old Photos（老照片修复）特效
"""
import os
import sys

sys.path.insert(0, '/root/.openclaw/skills/vivago-ai/scripts')

from vivago_client import create_client
import json

def test_template_to_video():
    print("🎬 测试视频模板功能 (Template-to-Video)")
    print("=" * 60)
    print("特效: Renovation of Old Photos（老照片修复上色）")
    print()
    
    # 使用之前上传的图片UUID（皮卡丘或柯基的黑白照片）
    # 这里用皮卡丘的UUID作为示例
    image_uuid = "p_a78df93d-7af6-4927-a793-197e790761e6"  # 皮卡丘
    
    print(f"📋 测试参数:")
    print(f"   模板: renovation_old_photos")
    print(f"   图片UUID: {image_uuid}")
    print(f"   比例: 4:3")
    print(f"   模式: Fast")
    print(f"   预计需要 2-3 分钟...")
    print()
    
    try:
        client = create_client()
        
        results = client.template_to_video(
            image_uuid=image_uuid,
            template='renovation_old_photos',
            wh_ratio='4:3',
            mode='Fast',
            duration=5
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
                    with open('/tmp/template_video_info.txt', 'w') as f:
                        f.write(f"{video_id}\n{video_url}")
                    
                    # 飞书消息格式
                    print(f"\n📱 飞书消息格式:")
                    print(f"   🎬 老照片修复特效生成完成！")
                    print(f"   📹 {video_url}")
                    print(f"   📋 Renovation of Old Photos 特效")
            
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
    success = test_template_to_video()
    sys.exit(0 if success else 1)
