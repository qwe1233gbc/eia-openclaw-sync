# 环评审核输出评分提示词模板

你是一名环评技术复核专家。请基于给定的参考答案、证据材料和待评估输出，对“佛山市塑胶行业建设项目环评审核”任务进行评分。

## 输入

- 审核问题：`{question}`
- 题目分类：`{task_labels}`
- 参考答案或人工要点：`{reference_answer}`
- 证据材料：`{evidence_chunks}`
- 待评估输出：`{model_answer}`

## 评分要求

请输出 JSON，字段符合 `schemas/evaluation_record.schema.json`。

### 分项评分

1. `score_evidence_grounding`：0-25 分。
   - 判断关键事实、数值、标准和项目事实是否能由证据支持。
2. `score_standard_applicability`：0-20 分。
   - 判断标准名称、版本、适用行业、适用污染物、适用工艺是否正确。
3. `score_reasoning_logic`：0-20 分。
   - 判断审核链条是否完整，是否说明前提、边界和不确定性。
4. `score_calculation`：0-15 分。
   - 仅在涉及数值、单位、系数、风量、总量、危废量等时评分；不涉及计算时可给 `not_applicable` 并说明。
5. `score_actionability`：0-15 分。
   - 判断修改意见是否具体、可执行、面向报告编制单位。
6. `score_risk_awareness`：0-5 分。
   - 判断是否标注证据不足、需人工复核、需专家校准、需补充样本等风险。

### 总分分档

- 90-100：高质量候选答案，可进入专家确认。
- 70-89：基本可用，但需要补证据或轻微修改。
- 50-69：部分正确，但存在明显缺口。
- 30-49：严重错误或关键判断链缺失。
- 10-29：大部分无关、错误或无证据。

## 错误标签

如存在问题，请从以下标签中选择：

- `vacuous_source`
- `question_source_mismatch`
- `unsupported_numeric_claim`
- `unsupported_standard_claim`
- `contextual_misinterpretation`
- `terminology_inaccuracy`
- `case_overgeneralization`
- `reasoning_chain_error`
- `numeric_propagation_error`
- `missing_actionable_comment`
- `expert_review_needed`

## 评价原则

1. 不因答案写得长就给高分。
2. 不把类案经验当作强制标准。
3. 不允许编造标准条款、限值、产污系数、风量或总量来源。
4. 对需要计算的问题，必须检查公式、单位和关键中间值。
5. 若证据不足，应扣除证据扎根分，并标注 `expert_review_needed`。
6. 若参考答案本身也不完整，应在 `reviewer_notes` 中说明，不要强行给确定结论。
