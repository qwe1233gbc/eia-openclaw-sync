# 环评审核问答分类定义 v1

分类在查看A/B/C/D结果前冻结。主标签均为单选，辅助能力可多选。

## 认知层级

- `L1_understanding`：提取单一事实，识别字段、编号或概念。
- `L2_application`：把公式、标准或规则应用到具体项目，通常核对2—3项证据。
- `L3_analysis`：跨章节或内外部来源综合判断，识别遗漏、冲突及适用性。

## 审核领域

`industry_classification`、`environmental_investment`、`environmental_quality_data`、
`water_emission_standard`、`air_emission_standard`、`noise_emission_standard`、
`solid_waste_standard`。

## 推理类型

- `factual_extraction`：单一事实提取。
- `quantitative_verification`：比例、合计、单位、限值或公式复算。
- `rule_applicability`：按地区、行业、工艺、污染物、排放形式、版本及时效匹配规则。
- `consistency_comparison`：报告内部、报告与外部资料或事实与结论之间比较。
- `multi_evidence_synthesis`：整合多项项目事实和依据形成结论。

## 功能能力

- `report_grounding`：报告证据扎根。
- `basis_grounding`：法规、标准、公报或分类依据扎根。
- `numerical_accuracy`：公式、数值和单位准确。
- `procedural_reasoning`：多步骤审核顺序和升级处理。
- `evidence_integration`：跨章节、跨来源证据整合。

## 归因标签

- `knowledge_dependency`、`workflow_dependency`：`low|medium|high`。
- `evidence_span`：`single_field|single_section|cross_section|report_plus_external`。

## 冻结与覆盖

模板默认值不等于人工终审。逐题覆盖必须填写 `override_reason`，并把
`classification_status` 改为 `manual_override`。分类不得读取任何模型结果或得分。
