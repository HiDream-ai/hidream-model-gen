#!/usr/bin/env python3
"""
图生图测试脚本 - Nano Banana 2
"""
import os
import sys

sys.path.insert(0, '/root/.openclaw/skills/vivago-ai/scripts')

from vivago_client import create_client
import json

def test_image_to_image():
    print("🎨 测试 Nano Banana 2 图生图功能")
    print("=" * 60)
    
    # 使用之前生成的图片UUID
    # 皮卡丘: p_302c9e53-ac49-459b-b034-c9c79ec9b50c
    # 绿头鸭: p_e77a6ca5-8da1-45cb-9d6d-e490617cc4ac
    
    image_uuids = [
        "p_302c9e53-ac49-459b-b034-c9c79ec9b50c",  # 皮卡丘
        "p_e77a6ca5-8da1-45cb-9d6d-e490617cc4ac"   # 绿头鸭
    ]
    
    prompt = "一只皮卡丘骑在绿头鸭背上，两个可爱的角色一起在水面上"
    
    print(f"\n📋 测试参数:")
    print(f"   Prompt: {prompt}")
    print(f"   图片数量: {len(image_uuids)}")
    print(f"   图片UUIDs: {image_uuids}")
    print(f"   比例: 16:9")
    print(f"   强度: 0.8")
    print(f"   权重: [0.9, 0.9]")
    print()
    
    try:
        client = create_client()
        
        print("⏳ 正在生成图生图...")
        print("   预计需要 1-2 分钟 (Nano Banana 2 较慢)")
        print()
        
        results = client.image_to_image(
            prompt=prompt,
            image_uuids=image_uuids,
            port="nano-banana",
            wh_ratio="16:9",
            strength=0.8,
            relevance=[0.9, 0.9]
        )
        
        print("\n" + "=" * 60)
        
        if results:
            print("✅ 生成成功!")
            print(f"\n📊 结果详情:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
            # 获取图片ID
            for i, result in enumerate(results):
                image_id = result.get('image')
                if image_id:
                    print(f"\n🖼️  生成的图片 {i+1}:")
                    print(f"   Image ID: {image_id}")
                    print(f"   下载链接: https://storage.vivago.ai/image/{image_id}.jpg")
                    
                    # 下载图片
                    print(f"\n📥 正在下载图片...")
                    download_path = f"/tmp/{image_id}.jpg"
                    downloaded = client.download_image(image_id, download_path)
                    
                    if downloaded and os.path.exists(downloaded):
                        size = os.path.getsize(downloaded)
                        print(f"   ✅ 已保存: {downloaded} ({size/1024:.1f} KB)")
                        
                        # 输出文件路径供飞书发送
                        with open('/tmp/img2img_output.txt', 'w') as f:
                            f.write(downloaded)
                    else:
                        print(f"   ⚠️  下载失败")
            
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
    success = test_image_to_image()
    sys.exit(0 if success else 1)
