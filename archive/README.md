# 项目归档说明

归档日期：2026-03-11

## 归档内容

### 1. 测试结果文件 (archive/test_results/)
- `test_result.json` - 早期测试结果
- `test_results.json` - 综合测试结果
- `phase2_test_results.json` - 第二阶段测试结果

### 2. 模板测试脚本 (archive/test_templates/tier5_templates/)
14个单模板测试文件，已整合到统一的测试体系中：
- test_template_angel_wings.py
- test_template_iron_man.py
- test_template_gta_star.py
- test_template_ash_out.py
- test_template_ghibli.py
- test_template_turkey_chasing.py
- test_template_1930s_vintage_style.py
- test_template_glasses_display.py
- test_template_romantic_kiss.py
- test_template_phoenix_wings.py
- test_template_apt.py
- test_template_barbie.py
- test_template_magic_reveal_ravenclaw.py
- run_all.sh

### 3. 测试缓存 (archive/cache/)
- `test_history.json` - 历史测试记录

### 4. 文档归档 (docs/archive/)
- `changelogs/CHANGELOG_20260311.md` - 版本变更日志
- `history/VERSION_HISTORY_20260311.md` - 版本历史记录

## 保留的核心文件

### 测试框架
- `conftest.py` - Pytest配置
- `test_suite.py` - 主测试套件
- `run_tests.py` - 测试运行器
- `run_optimized_tests.py` - 优化版测试运行器
- `smart_test_optimizer.py` - 智能测试优化器
- `test_history_manager.py` - 测试历史管理
- `generate_tier5_tests.py` - 测试生成器

### 层级测试文件
- `tier1_quick.py` - 快速冒烟测试
- `tier3_image.py` - 图片功能测试
- `tier3_phase2_video.py` - 视频功能测试
- `tier4_image_ports.py` - 图片端口测试
- `tier4_video_v3l.py` / `tier4_video_kling.py` - 视频端口测试
- `tier5_ten_templates.py` - 模板批量测试
- `tier5_selected.py` - 精选模板测试
- `tier6_10_templates.py` - 扩展模板测试

### 实用脚本
- `video_*.py` - 视频功能独立脚本
- `test_nano_txt2img.py` - Nano模型测试
- `test_template_fix.py` - 模板修复验证

## 新一轮测试准备状态

✅ 已清理临时文件和缓存
✅ 已归档历史测试结果
✅ 已整合分散的模板测试
✅ 核心测试框架保留完整
✅ 项目结构已优化

项目已准备好进行新一轮测试。
