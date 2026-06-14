# experiment_v0_1 完成报告

> 生成时间: 2026-06-14 22:36:48

## 产出物清单

| 文件 | 内容 | 数量 |
|------|------|------|
| standard_cards_mvp.jsonl/md | 标准审核依据卡 | 32条,12模块 |
| experience_cards_mvp.jsonl/md | 类案经验卡 | 8条 |
| benchmark_items_mvp.jsonl/md | Benchmark测试题 | 12道,4种题型 |
| prompts/A,B,C/ | 三组提示词 | 36个(12×3) |
| scoring_template.csv | 评分模板 | 36行×12列 |
| scoring_guide.md | 评分指南 | 含5维评分标准 |
| experiment_design_mvp.md | 实验设计说明 | 含方法论和局限性 |

## 数据来源

- 标准卡: 报告表编制指南 + 佛山塑胶行业指南 + standard_clause_library
- 经验卡: case_law_style_experience_library.jsonl → 筛选C2929注塑相关
- 测试题证据包: 基于盛之强项目虚构的合理场景
- 金标答案: 基于指南公式计算 + 类案经验推断

## 待人工检查

- [ ] 标准卡32条是否全部覆盖C2929审核要点
- [ ] 经验卡8条是否与盛之强项目场景关联紧密
- [ ] Q04-Q06的计算题金标答案数值是否准确
- [ ] cross_check题是否真正体现了多证据交叉
- [ ] 三组prompt的信息量差异是否足够明显
- [ ] scoring_template的金标答案需要真实经办人验证

## Git同步状态

- ⬜ 尚未推送到GitHub (需手动执行)
