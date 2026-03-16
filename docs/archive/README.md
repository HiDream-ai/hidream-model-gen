# 文档归档目录

此目录包含项目开发过程中的历史文档和临时文档。

## 目录结构

```
docs/archive/
├── history/          # 历史文档（已完成的阶段报告）
├── temp/             # 临时文档（不再需要的中间报告）
└── reports/          # 历史测试报告（可选归档）
```

## history/ - 历史阶段报告

包含项目各阶段完成后的总结报告，供参考但不再维护。

| 文档 | 阶段 | 日期 | 说明 |
|------|------|------|------|
| CODE_REVIEW_REPORT.md | Code Review | 2026-03-06 | 原始代码审查报告 |
| OPTIMIZATION_REVIEW.md | P0-P2优化确认 | 2026-03-06 | 优化结果确认 |
| OPTIMIZATION_SUMMARY.md | 优化总结 | 2026-03-06 | 完整优化总结 |
| P1_IMPROVEMENTS_REPORT.md | P1优化 | 2026-03-06 | P1改进报告 |
| P2_IMPROVEMENTS_REPORT.md | P2优化 | 2026-03-06 | P2改进报告 |

## temp/ - 临时中间报告

开发过程中生成的临时报告，内容已过时或已合并到正式文档中。

| 文档 | 类型 | 日期 | 说明 |
|------|------|------|------|
| TEMPLATE_CATEGORIES.md | 分类草稿 | 2026-03-05 | 模板分类草稿，已整合 |
| TEMPLATE_TEST_REPORT.md | 测试记录 | 2026-03-06 | 早期模板测试记录 |
| TEST_STATUS_REPORT.md | 状态报告 | 2026-03-06 | 临时测试状态，已过时 |
| TESTING_STRATEGY.md | 策略草稿 | 2026-03-07 | 旧版测试策略，已被优化版替代 |

## 如何查看归档文档

如需查看历史文档：

```bash
# 查看历史阶段报告
ls docs/archive/history/
cat docs/archive/history/CODE_REVIEW_REPORT.md

# 查看临时文档
ls docs/archive/temp/
```

## 注意事项

- 归档文档仅供历史参考，**不保证内容最新**
- 最新信息请查看项目根目录和 docs/ 下的正式文档
- 如需恢复某个文档，可从归档目录复制到上级目录

---

*归档整理时间: 2026-03-07*
