#!/usr/bin/env python3
"""
Phase 1 验证测试 - 测试 template_to_video 修复和轮询功能
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')

from scripts.vivago_client import create_client
from scripts.template_manager import get_template_manager
import requests
import json
import time
from datetime import datetime

# 配置
TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOiIyODg4Njc1NS0xOTA2LTRiY2YtODgzNC04MDFlNDM4OTliYWIiLCJ1c2VybmFtZSI6ImRpc2NvcmRfcUR6SVJvYiIsInBob25lbnVtIjoiMTIzNDU2Nzg5MTAiLCJlbWFpbCI6InpoYW9mYW5xaXVAZ21haWwuY29tIiwicm9sZSI6ImFwaSZlLWNvbW1lcmNlciZnZW5lcmFsIiwiZXhwIjo0ODY0ODc2MzM5fQ.pstbKg6H9I6KFG5fTPgpzkkrV6hd5YYoe0PbHV2YIYk"
BASE_URL = "https://vivago.ai/api/gw"

def test_template_to_video_fix():
    """测试 1: 验证 template_to_video 参数兼容性修复"""
    print("="*60)
    print("测试 1: template_to_video 参数兼容性")
    print("="*60)
    
    client = create_client()
    
    # 测试 1a: 使用 image_input 参数
    print("\n1a. 使用 image_input 参数调用...")
    try:
        result = client.template_to_video(
            image_input=TEST_IMAGE_UUID,
            template='ghibli',
            wh_ratio='1:1'
        )
        print("   ✅ image_input 参数正常工作")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 测试 1b: 使用 image_uuid 参数（修复前会失败）
    print("\n1b. 使用 image_uuid 参数调用...")
    try:
        result = client.template_to_video(
            image_uuid=TEST_IMAGE_UUID,
            template='ghibli',
            wh_ratio='1:1'
        )
        print("   ✅ image_uuid 参数正常工作（修复成功！）")
        return True
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

def test_1970s_template():
    """测试 2: 验证 1970s 模板轮询功能"""
    print("\n" + "="*60)
    print("测试 2: 1970s 模板轮询功能")
    print("="*60)
    
    client = create_client()
    
    print("\n提交 1970s 模板任务...")
    try:
        result = client.template_to_video(
            image_input=TEST_IMAGE_UUID,
            template='1970s',
            wh_ratio='1:1'
        )
        
        if result:
            print(f"✅ 1970s 模板测试成功！")
            print(f"   返回结果数: {len(result)}")
            if result:
                print(f"   第一个结果: {result[0].get('video', 'N/A')[:30]}...")
            return True
        else:
            print("❌ 返回结果为空")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数：运行 Phase 1 验证测试"""
    print("\n" + "="*60)
    print("Phase 1 验证测试")
    print("="*60)
    print("时间:", datetime.now().isoformat())
    
    results = {}
    
    # 测试 1
    results['template_to_video_fix'] = test_template_to_video_fix()
    
    # 测试 2
    results['1970s_template'] = test_1970s_template()
    
    # 汇总
    print("\n" + "="*60)
    print("Phase 1 测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 Phase 1 所有测试通过！")
    else:
        print("⚠️  部分测试失败，需要进一步调试")
    print("="*60)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
