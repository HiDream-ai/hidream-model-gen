# Test Version History

## v0.2.0 (2026-03-05)

### Architecture Update
- ✅ 重构层级架构：一级功能 -> 二级端口
- ✅ 添加 API 端口配置系统 (`api_ports.json`)
- ✅ 支持动态端口选择和扩展
- ✅ 更新 README 功能状态表格

### New Features
- 🧪 图生视频功能 (v3Pro/v3L/kling-video)
- ✅ 端口列表查询 (`list_categories`, `list_ports`)

### Test Status
| Date | Suite ID | Category | Port | Status | Notes |
|------|----------|----------|------|--------|-------|
| 2026-03-05 | 168e69b8 | text_to_image | kling-image | ✅ PASSED | Successfully generated images |
| 2026-03-05 | TBD | image_to_video | v3Pro | 🧪 TESTING | Long processing time (2-3 min) |

### Known Issues
- Video generation requires 2-3 minutes
- Need to avoid frequent video API calls

---

## v0.1.0 (2026-03-05)

### Initial Release
- Basic test framework
- Test cases:
  - txt2img_basic: Basic text-to-image
  - txt2img_batch: Batch generation
  - txt2img_ratios: Multiple aspect ratios
  - api_error_handling: Error handling
- Report generation
- Configurable test suite

### Bug Fixes
- Fixed result endpoint URL from `/v3/image/image/async/results` to `/v3/image/txt2img/async/results`

### Test Results
| Date | Suite ID | Status | Notes |
|------|----------|--------|-------|
| 2026-03-05 | 168e69b8 | ✅ PASSED | Successfully generated image with kling-image-o1 |
| 2026-03-05 | TBD | ❌ FAILED | API endpoint issue (fixed in v0.1.1) |
