#!/usr/bin/env python3
"""
快速验证 template_to_video 修复
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill')
sys.path.insert(0, '/root/.openclaw/workspace/skills/vivago-ai-skill/scripts')

# 验证函数签名
from scripts.vivago_client import VivagoClient
import inspect

sig = inspect.signature(VivagoClient.template_to_video)
params = list(sig.parameters.keys())

print("="*60)
print("template_to_video 函数签名验证")
print("="*60)
print(f"参数列表: {params}")
print()

# 检查关键参数
has_image_input = 'image_input' in params
has_image_uuid = 'image_uuid' in params

print("验证结果:")
print(f"  ✅ image_input 参数: {'存在' if has_image_input else '缺失'}")
print(f"  ✅ image_uuid 参数: {'存在' if has_image_uuid else '缺失'}")

# 检查默认值
image_input_param = sig.parameters.get('image_input')
image_uuid_param = sig.parameters.get('image_uuid')

if image_input_param:
    print(f"  📌 image_input 默认值: {image_input_param.default}")
if image_uuid_param:
    print(f"  📌 image_uuid 默认值: {image_uuid_param.default}")

print()
if has_image_input and has_image_uuid:
    print("🎉 修复验证成功！现在同时支持 image_input 和 image_uuid 参数")
else:
    print("❌ 修复未生效")

sys.exit(0 if (has_image_input and has_image_uuid) else 1)
