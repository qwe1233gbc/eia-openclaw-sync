# OpenClaw Skill Card — 环评智能审核 v0.6a

## 1. Skill 目标

面向建设项目环境影响报告表审核，基于**明文标准库 + 类案经验库 + relevance 过滤机制**，辅助识别环评报告中需要核实、补充或退改的关键问题。

## 2. 适用行业与场景

- **优先行业**: C2929 塑料零件及其他塑料制品制造 (注塑、挤出、造粒、涂布)
- **地区**: 佛山市顺德区
- **报告类型**: 建设项目环境影响报告表
- **审核模块**: VOCs源强、废气收集效率、活性炭参数、危废识别与核算、总量控制、工艺一致性、冷却水平衡、环境风险、监测计划

## 3. 输入

- `evidence_package`: 环评报告关键证据 (原辅材料、设备、工艺、产污、治理设施、标准引用、核算数据)
- `standard_clause_library`: 38条标准卡 (法规、导则、标准、系数手册、地方政策)
- `experience_rules_active`: 8条 active 经验卡 (经标准校准、含 task_type/module/evidence_level)

## 4. 知识库构成

### 4.1 标准库 (38条)

详见 `standard_clause_library.jsonl`，覆盖：排放标准、VOCs源强、废气收集效率、活性炭参数、危废识别、冷却水、复合工艺、总量控制、安全设施、监测计划、环境风险等。

### 4.2 经验库 (8条 active)

| 经验卡ID | 名称 | 证据等级 | 适用任务类型 |
|----------|------|---------|-------------|
| EXP_01 | 胶水VOCs超限值 | core | guide_explicit, case_experience |
| EXP_02 | 活性炭更换周期虚长 | core | guide_explicit, standard_calculation, case_experience |
| EXP_03 | 收集效率取95%但非全密闭 | core | case_experience, cross_check, guide_explicit |
| EXP_04 | 复合工艺VOCs遗漏 | reference | case_experience, cross_check |
| EXP_05 | 废活性炭产生量漏算 | pending | case_experience, cross_check, guide_explicit |
| EXP_06 | 总量替代方案不实 | reference | case_experience, guide_explicit |
| EXP_07 | 注塑VOCs源强被低估 | pending | case_experience |
| EXP_08 | 冷却水排放路径不清 | pending | case_experience, cross_check |

## 5. 工作流

```text
1. 接收 evidence_package + 题目
   ├── 识别 question_type: guide_explicit / standard_calculation / case_experience / cross_check / negative_control
   └── 识别审核模块: VOCs源强 / 废气收集 / 活性炭 / 危废 / 工艺 / 冷却水 / 环境风险 / 监测 / 总量 / 安全

2. 标准库检索
   ├── 按模块匹配 standard_clause_library → 返回相关 STD_XX
   └── 提取条款位置、限值、公式、表格

3. 经验库检索 (含 relevance 过滤)
   ├── Step1 硬过滤:
   │   ├── task_type ∈ card.not_applicable_task_types → 丢弃
   │   ├── module ∈ card.not_applicable_modules → 丢弃
   │   ├── pending → 标记 MEDIUM (不能强判断)
   │   └── 行业不匹配 → 降级/丢弃
   ├── Step2 软分级:
   │   ├── HIGH = task匹配 + module匹配 + 行业匹配 + evidence_status core/reference
   │   ├── MEDIUM = module/task匹配但evidence链不完整 (pending)
   │   └── LOW = 仅关键词匹配 → 丢弃
   └── Step3 使用:
       ├── HIGH → 可进入审核判断 → +2 experience_basis_score
       ├── MEDIUM → 辅助提示 + 标注人工复核 → +1
       └── LOW → 丢弃

4. 报告证据核验
   ├── 对照 report_evidence_used 验证标准条款匹配性
   ├── 执行计算核验 (standard_calculation)
   └── 执行交叉核验 (cross_check)

5. 形成审核判断
   ├── audit_judgement: 判断结论
   ├── judgement_level: needs_revision / needs_supplement / needs_expert_confirm
   ├── identified_issues: 问题清单
   └── recommended_review_comment: 可执行的退改意见

6. 自反思评分 (4维40分)
   ├── coherence_score (0-10): 判断逻辑一致性
   ├── evidence_consistency_score (0-10): 证据支撑一致性
   ├── calculation_correctness_score (0-10): 计算正确性
   └── relevance_check_score (0-10): 经验卡相关性过滤正确性
   └── total_score_40
```

## 6. 输出格式

每行一个 JSON 对象，字段：
- `item_id, group, question_type, project_name`
- `audit_judgement, judgement_level`
- `report_evidence_used`
- `standard_cards_used[]` (standard_card_id, standard_card_title, matched_requirement, source_type, manual_check_needed)
- `experience_cards_used[]` (experience_card_id, experience_card_title, evidence_level, applicable_task_types, relevance_level)
- `experience_relevance_results[]` (experience_card_id, relevance_level, relevance_reason, evidence_status, can_support_judgement)
- `calculation_check[]`, `cross_check_logic`, `cross_item_impacts[]`
- `identified_issues[]`, `recommended_review_comment`
- `confidence, manual_check_needed, limitations[]`
- `self_reflection { coherence_score, evidence_consistency_score, calculation_correctness_score, relevance_check_score, total_score_40, revision_needed, revision_reason }`

## 7. 自反思评分细则 (4维40分)

| 维度 | 满分 | 评分标准 |
|------|------|---------|
| 逻辑一致性 (coherence) | 10 | 审核判断-证据-结论是否逻辑自洽 |
| 证据一致性 (evidence) | 10 | 标准条款/经验/报告证据是否相互支撑 |
| 计算正确性 (calculation) | 10 | 公式应用、数值计算是否准确 |
| 相关性过滤 (relevance) | 10 | 经验卡relevance分级是否正确 |

## 8. 当前限制

1. **经验卡覆盖盲区**: 7/18题无经验卡覆盖 (安全设施/标准适用/储存/风量/过滤风速/环境风险/监测计划)
2. **Pending 卡信息量不足**: 3张 pending 卡 (EXP_05/07/08) 仅能提供辅助提示
3. **行业限定**: C2929 注塑/涂布场景，未见跨行业验证
4. **地区限定**: 佛山市顺德区政策和标准为上下文
5. **不做自动审批**: 输出为退改意见草稿，需人工确认

## 9. 不适用场景

- 非 C2929 行业的环评审核
- 跨地区 (非顺德/广东省) 的政策适用
- 生态、地下水、土壤等非 VOCs/危废模块
- 施工期、清洁生产、碳排放等专项审核
- 行政审批结论生成

## 10. 改进方向

| 方向 | 优先级 | 说明 |
|------|--------|------|
| 补齐经验卡覆盖盲区 | 高 | 安全设施/监测计划/环境风险模块 |
| 升级 pending 卡 | 高 | 收集更多证据将 EXP_05/07/08 升级为 core/reference |
| 扩展行业覆盖 | 中 | 从 C2929 扩展到其他制造业代码 |
| 跨地区适配 | 中 | 非顺德地区的标准/政策本地化 |
| 端到端自动化 | 低 | 从 PDF 解析 → 审核 → 意见生成全链路 |
