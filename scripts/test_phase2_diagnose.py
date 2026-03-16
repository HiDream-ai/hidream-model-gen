#!/usr/bin/env python3
"""
Phase 2 深度诊断测试
精确定位问题所在阶段
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

from scripts.vivago_client import create_client
from scripts.template_manager import get_template_manager
import requests
import json
import time
from datetime import datetime

TEST_IMAGE_UUID = 'j_daeef3b0-9cd7-4741-87e8-31fab45f89c1'
client = create_client()
manager = get_template_manager()

def diagnose_template(template_id):
    """详细诊断单个模板"""
    print(f"\n{'='*60}")
    print(f"诊断: {template_id}")
    print(f"{'='*60}")
    
    template = manager.get_template(template_id)
    if not template:
        print("❌ 模板不存在")
        return
    
    print(f"模板名称: {template.get('name')}")
    print(f"算法: {template.get('algo_type')}")
    print(f"端点: {template.get('endpoint')}")
    print(f"结果端点: {template.get('result_endpoint')}")
    
    # 1. 检查模板配置
    print("\n【步骤 1】检查模板配置...")
    print(f"  Module: {template.get('module')}")
    print(f"  Version: {template.get('version')}")
    print(f"  Template ID: {template.get('template_id')}")
    
    # 2. 构建请求数据
    print("\n【步骤 2】构建请求数据...")
    try:
        data = manager.build_request_data(template_id, TEST_IMAGE_UUID, wh_ratio='1:1')
        print(f"  ✅ 请求数据构建成功")
        print(f"  请求体大小: {len(json.dumps(data))} 字节")
        print(f"  Prompt 长度: {len(data.get('params', {}).get('custom_params', {}).get('prompts', [''])[0])} 字符")
        
        # 检查关键字段
        if 'params' in data and 'custom_params' in data['params']:
            custom = data['params']['custom_params']
            print(f"  包含 prompts: {'prompts' in custom}")
            print(f"  包含 master_template_id: {'master_template_id' in custom}")
            print(f"  包含 wh_ratio: {'wh_ratio' in custom}")
    except Exception as e:
        print(f"  ❌ 构建失败: {e}")
        return
    
    # 3. 发送请求（带详细计时）
    print("\n【步骤 3】发送 POST 请求...")
    url = f"{client.base_url}{template['endpoint']}"
    headers_post = {**client.headers, 'Content-Type': 'application/json'}
    
    start_time = time.time()
    try:
        print(f"  URL: {url}")
        print(f"  开始时间: {datetime.now().isoformat()}")
        print(f"  超时设置: 20秒")
        
        resp = requests.post(url, json=data, headers=headers_post, timeout=20)
        
        elapsed = time.time() - start_time
        print(f"  响应时间: {elapsed:.2f}秒")
        print(f"  HTTP 状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  API Code: {result.get('code')}")
            print(f"  API Message: {result.get('message')}")
            
            if result.get('code') == 0:
                task_id = result.get('result', {}).get('task_id')
                print(f"  ✅ 提交成功! TaskID: {task_id}")
                return {'stage': 'submit_success', 'task_id': task_id}
            else:
                print(f"  ❌ API 返回错误: {result.get('message')}")
                return {'stage': 'submit_api_error', 'error': result.get('message')}
        else:
            print(f"  ❌ HTTP 错误: {resp.status_code}")
            print(f"  响应内容: {resp.text[:200]}")
            return {'stage': 'submit_http_error', 'status': resp.status_code}
            
    except requests.exceptions.ConnectTimeout:
        elapsed = time.time() - start_time
        print(f"  ❌ 连接超时 ({elapsed:.2f}秒)")
        print(f"  问题: 无法建立到服务器的连接")
        return {'stage': 'connect_timeout', 'duration': elapsed}
    except requests.exceptions.ReadTimeout:
        elapsed = time.time() - start_time
        print(f"  ❌ 读取超时 ({elapsed:.2f}秒)")
        print(f"  问题: 连接建立但服务器响应超时")
        return {'stage': 'read_timeout', 'duration': elapsed}
    except requests.exceptions.ConnectionError as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 连接错误 ({elapsed:.2f}秒)")
        print(f"  错误详情: {e}")
        return {'stage': 'connection_error', 'error': str(e)}
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 其他错误 ({elapsed:.2f}秒): {type(e).__name__}: {e}")
        return {'stage': 'other_error', 'error': str(e)}

def main():
    """诊断所有失败模板"""
    print("\n" + "="*60)
    print("Phase 2 深度诊断")
    print("="*60)
    print(f"时间: {datetime.now().isoformat()}")
    print()
    
    # 诊断失败的模板
    failed_templates = ['1970s', 'couple_kissing', 'hold_deceased', 'photo_restore']
    
    results = {}
    for template_id in failed_templates:
        result = diagnose_template(template_id)
        results[template_id] = result
        
        # 如果成功了，不再继续测试（节省积分）
        if result and result.get('stage') == 'submit_success':
            print(f"\n✅ {template_id} 提交成功，跳过其他测试以节省积分")
            break
    
    # 诊断报告
    print("\n\n" + "="*60)
    print("诊断报告")
    print("="*60)
    
    for tid, result in results.items():
        if not result:
            continue
        stage = result.get('stage', 'unknown')
        print(f"\n{tid}:")
        print(f"  阶段: {stage}")
        
        if stage == 'submit_success':
            print(f"  状态: ✅ 提交成功")
        elif stage == 'connect_timeout':
            print(f"  状态: ❌ 连接超时")
            print(f"  分析: 网络连接问题或服务器无响应")
        elif stage == 'read_timeout':
            print(f"  状态: ❌ 读取超时")
            print(f"  分析: 连接成功但服务器处理慢（请求体过大或服务端处理慢）")
            print(f"  持续时间: {result.get('duration', 'N/A'):.2f}秒")
        elif stage == 'connection_error':
            print(f"  状态: ❌ 连接错误")
            print(f"  分析: DNS、网络或服务器问题")
        elif stage == 'submit_api_error':
            print(f"  状态: ❌ API 返回错误")
            print(f"  错误: {result.get('error')}")
    
    print("\n" + "="*60)
    print("问题分析")
    print("="*60)
    
    # 统计问题类型
    connect_timeouts = [t for t, r in results.items() if r and r.get('stage') == 'connect_timeout']
    read_timeouts = [t for t, r in results.items() if r and r.get('stage') == 'read_timeout']
    connection_errors = [t for t, r in results.items() if r and r.get('stage') == 'connection_error']
    
    if read_timeouts:
        print(f"\n🔍 读取超时模板 ({len(read_timeouts)}个): {', '.join(read_timeouts)}")
        print("  可能原因:")
        print("    1. 请求体过大（某些模板 prompt 很长）")
        print("    2. 服务端处理时间较长")
        print("    3. 当前超时设置 20 秒可能过短")
        print("  建议:")
        print("    - 增加超时时间到 60-120 秒")
        print("    - 检查这些模板的 prompt 长度")
    
    if connect_timeouts:
        print(f"\n🔍 连接超时模板 ({len(connect_timeouts)}个): {', '.join(connect_timeouts)}")
        print("  可能原因: 网络连接问题")
    
    if connection_errors:
        print(f"\n🔍 连接错误模板 ({len(connection_errors)}个): {', '.join(connection_errors)}")
        print("  可能原因: DNS 或网络不稳定")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
