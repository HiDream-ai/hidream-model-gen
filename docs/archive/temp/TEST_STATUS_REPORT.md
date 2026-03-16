# Vivago AI 模板测试状态报告

**生成时间**: 2026-03-06  
**总模板数**: 181  
**测试进度**: 24/181 (13.3%)

---

## 📊 测试结果汇总

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 已测试 | 24 | 13.3% |
| ⏳ 未测试 | 157 | 86.7% |

### 按结果类型分布

| 结果类型 | 数量 | 模板示例 |
|----------|------|----------|
| 🖼️ 图片 (静态特效) | 17 | Motorcycle Boy, Nine Grid Pet, Dinner Party... |
| 🎬 视频 (动态特效) | 7 | Mystic Traveler, Autumn Feast, Moving Figure... |
| ❓ 未知 | 0 | - |

### 按端口类型分布

| 端口类型 | 总数量 | 已测试 | 结果类型 |
|----------|--------|--------|----------|
| image_edit_gen | 17 | 17 | 🖼️ 图片 |
| proto_transformer | 58 | 12 | 🎬 视频 |
| video_diffusion_img2vid | 53 | 0 | 待测试 |
| avatar_transformer | 15 | 0 | 待测试 |
| outfit_transformer | 10 | 0 | 待测试 |
| 其他 | 28 | 0 | 待测试 |

---

## ✅ 已测试模板详情

### 🖼️ 图片结果模板 (17个)

第一批测试完成 (image_edit_gen 端口):

1. ✅ Motorcycle Boy
2. ✅ Nine Grid Pet
3. ✅ Dinner Party
4. ✅ Midnight Neon
5. ✅ Domineering CEO
6. ✅ White Sweater
7. ✅ Elegant Gentle
8. ✅ Costume Change
9. ✅ Lens Heartbeat
10. ✅ Darkroom Flash
11. ✅ Noble Person
12. ✅ Night Chat
13. ✅ Polaroid
14. ✅ Black Rose
15. ✅ Advanced Image
16. ✅ Cool Boss
17. ✅ Three Frames

### 🎬 视频结果模板 (7个)

第二批测试完成 (proto_transformer 端口):

1. ✅ Mystic Traveler
2. ✅ Autumn Feast
3. ✅ Moving Figure
4. ✅ 1960s Elegant
5. ✅ Doodle Alive
6. ✅ 1970s
7. ✅ A Family

---

## 🚫 违规/敏感内容模板

| 模板名称 | 端口 | 违规原因 | 建议 |
|----------|------|----------|------|
| 2000s_y2k | proto_transformer | 可能触发内容审核 | 更换成年女性/男性样本重试 |

---

## ⚠️ 已知问题

### 1. Prompt 乱码问题

以下7个模板存在中文prompt乱码（UTF-8编码错误），需要重新提供配置文件：

| 模板名称 | UUID | 严重程度 |
|----------|------|----------|
| Turkey Chasing | bfbf99a7-e76a-4c78-8f16-68c8ca4e4d4f.mp4 | 🔴 严重 |
| Turkey Away | fdc290e5-4832-48b3-b6a0-1a84545bb849.mp4 | 🔴 严重 |
| Glam Cat | ae5e1f9c-0411-4960-9b74-3d4251c6523b.mp4 | 🔴 严重 |
| Little Turkey | 9b2c5c17-7abe-4ffe-b66a-f402e7e7c7a6.mp4 | 🔴 严重 |
| Heavenly Hug | 82482327-dddd-4133-a105-b7aefc877c98.mp4 | 🔴 严重 |
| Fighting Giant | 23524908-5565-461b-a489-fd3f959d8a0e.mp4 | 🔴 严重 |
| Kiss Hand | e2830f9d-01b7-4ed5-9451-ab26121002c4.mp4 | 🔴 严重 |

**影响评估**:
- ✅ 模板调用：不受影响（使用template_id）
- ❌ 生成质量：可能受影响

---

## 📋 后续测试计划

### 优先级1：重试失败的模板
- 第二批剩余：renovation_of_old_photos, 1930s_vintage_style, animal_cooking, 1940s_suit_portrait, color_the_lines, 1970s_disco, 1990s_punk_rock, me_in_hand, music_box, turkey_chasing
- 魔法系列：magic_reveal_gryffindor (修复括号问题后)

### 优先级2：未测试端口
- video_diffusion_img2vid (53个模板)
- avatar_transformer (15个模板)
- outfit_transformer (10个模板)
- 其他端口 (28个模板)

### 优先级3：处理乱码模板
- 等待新的配置文件后重新测试

---

## 🔧 修复记录

| 时间 | 修复内容 | 状态 |
|------|----------|------|
| 2026-03-06 | 修复magic_reveal模板括号查找问题 | ✅ 完成 |
| 2026-03-06 | 识别模板结果类型(image/video) | ✅ 完成 |
| 2026-03-06 | 更新模板状态到api_ports.json | ✅ 完成 |

---

## 📁 相关文件

- `api_ports.json` - API端口配置
- `templates_data.json` - 模板数据
- `template_manager.py` - 模板管理器

---

*报告由测试脚本自动生成*
