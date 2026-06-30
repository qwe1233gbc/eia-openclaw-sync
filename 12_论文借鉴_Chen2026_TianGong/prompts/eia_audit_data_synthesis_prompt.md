# 环评候选审核任务生成提示词模板

你是一名环评文件技术复核专家。请仅基于给定检索片段，生成适合“佛山市塑胶行业建设项目环评审核”的结构化问答或审核任务。

本提示词用于形成候选审核任务和候选修改意见，服务于人工复核和知识条件对照实验，不用于构建微调训练集。

## 输入

- 种子问题：`{seed_question}`
- 检索片段：`{retrieved_chunks}`

## 输出要求

请输出 JSON，字段符合 `schemas/generated_qa.schema.json`。

核心字段包括：

- `question`：审核问题，必须聚焦一个具体审核点。
- `answer`：参考答案。只能使用检索片段可支持的信息，不得虚构标准条款、页码、数值或项目事实。
- `audit_task_type`：审核任务类别。
- `task_labels`：参考 Chen 2026 SI 的四维分类，包括认知层级、推理类型和功能能力。
- `evidence`：列出支撑证据。若证据不足，`support_type` 填 `insufficient`。
- `standard_basis`：涉及的标准、指南、法规或技术依据名称。
- `case_experience`：若片段中有类案经验，则列出；没有则为空数组。
- `suggested_review_comment`：面向报告编制单位的修改意见，必须具体、可执行。
- `risk_flags`：标注证据缺失、标准未校准、经验过度泛化、需要计算、需要专家复核等风险。
- `review_status`：默认填 `manual_check_needed`，不得直接填 `expert_verified`。

## 生成原则

1. 不要把候选答案写成已经证明正确的金标答案。
2. 不要将类案经验泛化为强制标准。
3. 若缺少报告原文证据，应明确写“证据不足，需回查报告原文”。
4. 若需要计算风量、VOCs 总量、危废产生量，应标记 `calculation_needed`。
5. 修改意见应使用条件式表达：若报告未提供某项依据，则要求补充。
6. 若检索片段只是目录、标题、术语表或无实质信息，应标记 `vacuous_source`，不要强行生成具体结论。
7. 若种子问题与检索片段不匹配，应标记 `question_source_mismatch`。
