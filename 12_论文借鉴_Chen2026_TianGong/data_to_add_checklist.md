# 后续需要补充的数据清单

> 用途：基于 Chen 2026 技术路线和本仓库当前材料，列出本课题下一阶段最需要补充的数据。  
> 当前定位：本课题不做模型微调，数据补充服务于“标准依据库 + 审核技能库 + 样本链 + 人工复核 + A/B/C/D 知识条件对照实验”。

## 1. 总体结论

当前仓库已经具备阶段性基础：

- 标准依据库：已有 `standard_cards.jsonl` 约 37 条结构化标准卡，另有 v3 旧版标准条目约 71 条；
- 审核技能库：已有 15 个单项审核 skill 和 1 个汇总 skill；
- 样本链：已有 33 个按项目组织的目录，约 54 个 Markdown 材料文件；
- QA 候选池：已有 942 条种子问答，覆盖 151 个项目；
- 对照实验：已有 A/B/C/D 知识条件对照设计。

但目前最缺的不是“更多普通文本”，而是以下 5 类高质量数据：

1. 典型项目完整样本链；
2. 真实修改意见 / 批注 / 技术审查意见；
3. 经过校准的标准依据条目；
4. 可进入实验的人工复核评价题；
5. 对照实验评分记录和错误案例。

## 2. 优先级总表

| 优先级 | 需要增加的数据 | 最低建议数量 | 主要用途 | 当前问题 | 建议放置位置 |
| --- | --- | ---: | --- | --- | --- |
| P0 | 典型涉胶水/涂胶/复合/熟化/VOCs 项目完整样本链 | 3-5 个完整项目 | 构建真实案例、金标答案和错误标签 | 当前完整链不足 | `05_样本链（按项目组织）/` |
| P0 | 真实修改意见、批注或技术审查意见 | 每个核心项目至少 1 份 | 校准审核问题和修改建议 | 类案经验缺少真实绑定 | `05_样本链（按项目组织）/<项目>/04_修改意见_补正通知/` |
| P0 | 从 942 条 QA 中筛选出的正式评价题 | 30-50 题 | A/B/C/D 对照实验 | 现有 QA 只是种子池 | `10_消融实验设计/` 或 `outputs/evaluation_task_set_v1/` |
| P1 | 标准依据库人工校准记录 | 先校准 30-50 条 | 提升 RAG 和 skill 依据可靠性 | 表号、限值、适用条件需复核 | `03_指南解析_明文标准库/quality/` |
| P1 | 样本链 readiness 表 | 覆盖现有 33 个项目目录 | 判断哪些项目可进实验 | 样本完整度分散 | `05_样本链（按项目组织）/_元数据/` |
| P1 | skill 真实报告校准样本 | 每个核心 skill 2-3 例 | 验证技能库能否稳定输出 | skill 仍需真实样本验证 | `09_环评审核技能库/` 或 `outputs/skill_validation/` |
| P2 | A/B/C/D 四组实验输出 | 30-50 题 x 4 组 | 对照实验分析 | 尚无正式输出矩阵 | `outputs/ablation_experiment_v1/` |
| P2 | 人工评分记录 | 至少 2 名评分者，30-50 题 | 统计分析和一致性检验 | 缺少人工评分 | `outputs/ablation_experiment_v1/` |
| P2 | rejected log | 覆盖被剔除 QA/样本 | 错误分析和数据质量说明 | 剔除原因未系统记录 | `outputs/rejected_records/` |
| P3 | 更多参照样本 | 若干纯注塑/非核心项目 | 边界对照 | 容易混入核心实验 | `05_样本链（按项目组织）/EXCLUDED_*` 或单独元数据标注 |

## 3. P0：必须优先补充的数据

### 3.1 典型项目完整样本链

这是当前最重要的数据缺口。

建议优先补充以下类型项目：

| 类型 | 典型特征 | 为什么需要 |
| --- | --- | --- |
| 涉胶水项目 | 使用水性胶、溶剂型胶、粘合剂、复合胶 | 对应指南适用边界和 VOCs 核算 |
| 涂胶 / 贴合项目 | 有涂布、上胶、贴合、覆膜、复合工序 | 可验证废气收集、风量、收集效率 |
| 塑塑复合项目 | 薄膜、包装材料、复合膜、软包装 | 与普通注塑区别明显，适合作为核心案例 |
| 塑铝复合项目 | 铝塑膜、塑铝复合、包装复合材料 | 适合验证行业分类和排放标准适用 |
| 熟化项目 | 复合后熟化、烘干、固化、老化房 | 适合验证 VOCs 产生和治理链条 |
| VOCs 治理完整项目 | 集气罩/密闭空间 + 活性炭/催化燃烧/其他治理 | 可验证治理设施、活性炭参数和总量控制 |

每个完整样本链建议至少包含：

| 材料 | 是否必需 | 用途 |
| --- | --- | --- |
| 受理公告报告 / 送审稿 | 必需 | 作为模型审核输入 |
| 修改意见 / 技术审查意见 / 专家批注 | 必需 | 作为真实问题标签 |
| 终稿 / 拟审批稿 | 强烈建议 | 用于观察问题是否修正 |
| 批复文件 | 强烈建议 | 用于校准管理要求和最终结论 |
| 项目信息表 | 必需 | 记录行业代码、工艺、原辅料、治理设施、样本等级 |

建议新增或补全位置：

```text
05_样本链（按项目组织）/<项目ID>/
├── _项目信息.md
├── 01_受理公告/
├── 02_终稿_拟审批稿/
├── 03_批复文件/
└── 04_修改意见_补正通知/
```

### 3.2 真实修改意见、批注或技术审查意见

真实修改意见是本课题区别于普通 RAG 问答的关键数据。

建议收集内容：

- 生态环境部门修改意见；
- 专家技术审查意见；
- 报告 Word/PDF 批注；
- 编制单位修改说明；
- 前后版本对照中能够体现“问题已修正”的片段。

每条修改意见后续应拆解为：

| 字段 | 说明 |
| --- | --- |
| project_id | 对应项目 |
| original_report_evidence | 原报告中存在问题的片段 |
| review_comment | 真实修改意见原文或摘要 |
| issue_type | 问题类型，如行业分类、废气收集、活性炭、危废等 |
| standard_basis | 涉及的标准或指南依据 |
| final_revision_evidence | 终稿或拟审批稿中是否修正 |
| usable_for_evaluation | 是否可作为正式评价题 |
| manual_review_status | retain / revise_needed / reject |

### 3.3 正式评价题数据

当前 942 条 QA 只能作为种子问答池，不能直接作为正式测试集。

建议先整理一版小规模正式评价题：

- 数量：30-50 题；
- 来源：优先来自完整样本链和真实修改意见；
- 覆盖：至少覆盖 8-10 个核心审核模块；
- 每题必须具备证据链；
- 每题必须标注人工复核状态。

建议评价题字段：

| 字段 | 说明 |
| --- | --- |
| task_id | 评价题编号 |
| project_id | 项目编号 |
| audit_module | 审核模块 |
| question | 审核问题 |
| report_evidence | 报告原文证据 |
| standard_basis | 标准依据 |
| real_review_comment | 真实修改意见或参考意见 |
| reference_answer | 人工校准参考答案 |
| cognitive_level | L1 / L2 / L3 |
| reasoning_type | factual / quantitative / comparative / cross_document |
| manual_review_status | retain / revise_needed / reject |

建议输出位置：

```text
outputs/evaluation_task_set_v1/
├── evaluation_task_set_v1.md
├── evaluation_task_set_v1.csv
└── rejected_task_log_v1.csv
```

## 4. P1：支撑实验可靠性的数据

### 4.1 标准依据库校准记录

需要优先校准的标准/依据类型：

| 类型 | 重点校准内容 |
| --- | --- |
| GB 31572 | 是否适用于塑料制品相关废气；污染物、限值、表号 |
| GB 37822 | VOCs 无组织控制、收集治理、台账和运行管理 |
| DB44/2367 | 广东地方 VOCs 排放控制要求及适用边界 |
| 产污系数 | 行业、工艺、污染物、单位、适用条件 |
| 三线一单 | 管控单元、准入清单、项目地址匹配 |
| 国民经济行业分类 | C2921-C2929 及相邻行业边界 |
| 活性炭相关依据 | 碘值、填装量、更换周期、吸附设施管理要求 |
| 危废识别依据 | 废活性炭、废胶桶、废过滤棉等代码和管理要求 |

建议为每条标准卡增加或校准：

```text
review_status: unreviewed / checked / needs_expert_review / deprecated
hard_law: true / false
applicability_notes:
source_verified:
verified_by:
verified_date:
```

### 4.2 样本链 readiness 表

建议对现有 33 个项目目录做一次完整盘点，形成 readiness 表。

建议字段：

| 字段 | 说明 |
| --- | --- |
| project_id | 项目编号 |
| project_name | 项目名称 |
| industry_code | 行业代码 |
| core_or_reference | core / reference / excluded |
| has_acceptance_report | 是否有受理公告或送审稿 |
| has_review_comment | 是否有修改意见 |
| has_final_report | 是否有终稿或拟审批稿 |
| has_approval | 是否有批复 |
| has_vocs_process | 是否涉及 VOCs 关键工艺 |
| has_glue_or_composite | 是否涉胶水/复合 |
| sample_chain_level | A_complete / B_partial / C_single |
| recommended_use | formal_eval / case_experience / retrieval_only / excluded |

建议输出位置：

```text
05_样本链（按项目组织）/_元数据/sample_chain_readiness_table.md
05_样本链（按项目组织）/_元数据/sample_chain_readiness_table.csv
```

### 4.3 skill 真实样本校准数据

每个核心 skill 至少需要 2-3 个真实报告样本进行校准。

优先校准以下 skill：

| skill | 为什么优先 |
| --- | --- |
| 01 国民经济行业类别审核 | 研究边界和样本筛选基础 |
| 07 污染物排放标准审核 | 容易出现标准适用错误 |
| 08 产污系数适用性审核 | 关系到源强核算可靠性 |
| 09 源强定量核算审核 | 涉及计算和单位，错误风险高 |
| 10 废气收集形式审核 | 影响收集效率和治理判断 |
| 11 废气设计风量审核 | 典型定量审核点 |
| 12 废气收集效率审核 | 容易过度套用经验值 |
| 13 活性炭参数审核 | 当前标准卡仍需补强 |
| 14 危险废物识别审核 | 依赖原辅料、治理设施和危废名录 |
| 15 VOCs总量控制审核 | 需要跨章节汇总 |

建议输出：

```text
outputs/skill_validation/
├── skill_validation_cases_v1.csv
├── skill_validation_findings_v1.md
└── skill_revision_suggestions_v1.md
```

## 5. P2：用于正式评价和论文结果的数据

### 5.1 A/B/C/D 对照实验输出

需要为同一批评价题生成四组输出：

| 组别 | 输入条件 | 需要保存的数据 |
| --- | --- | --- |
| A | 仅报告片段或审核问题 | 模型原始输出 |
| B | A + 标准依据库 | 检索到的标准片段 + 输出 |
| C | B + 审核技能库步骤 | 使用的 skill 步骤 + 输出 |
| D | C + 样本链/修改意见/类案经验 | 引用的经验片段 + 输出 |

每条输出建议保存：

- task_id；
- group_id；
- input_context；
- retrieved_evidence；
- model_output；
- used_skill；
- used_standard_cards；
- risk_flags；
- generation_time；
- manual_review_required。

### 5.2 人工评分记录

评分记录是后续能否写出“实验结果”的关键。

建议至少 2 名评分者，先评分 30-50 题。每条记录包括：

| 字段 | 说明 |
| --- | --- |
| task_id | 题目编号 |
| group_id | A/B/C/D |
| reviewer_id | 评分者编号 |
| score_correctness | 判断正确性 |
| score_evidence | 证据使用 |
| score_standard | 标准适用 |
| score_logic | 审核逻辑 |
| score_calculation | 数值/计算 |
| score_actionability | 修改意见可执行性 |
| score_false_positive_control | 误报控制 |
| error_tags | 错误标签 |
| reviewer_comment | 人工备注 |

建议输出位置：

```text
outputs/ablation_experiment_v1/
├── model_outputs_abcd_v1.csv
├── manual_scores_v1.csv
├── error_tags_v1.csv
└── ablation_result_summary_v1.md
```

### 5.3 rejected log

借鉴 Chen 2026 的数据剔除思路，本项目也应保留被剔除样本的原因。

建议错误类型：

- `vacuous_source`：证据片段空泛；
- `question_source_mismatch`：问题和证据不匹配；
- `unsupported_numeric_claim`：数值无来源；
- `unsupported_standard_claim`：标准适用性无依据；
- `case_overgeneralization`：类案经验过度泛化；
- `contextual_misinterpretation`：误读行业、工艺、原辅料或治理设施；
- `calculation_chain_error`：计算链错误；
- `not_in_scope`：不属于当前研究边界。

## 6. P3：可后续扩展的数据

### 6.1 参照样本和排除样本

建议保留但不要混入核心实验：

- 普通纯注塑项目；
- 电子电器项目；
- 五金喷涂项目；
- 涂料生产项目；
- 其他非塑胶指南核心适用范围项目。

用途：

- 说明研究边界；
- 测试模型是否误把非核心项目纳入指南适用范围；
- 支撑论文中的适用范围讨论。

### 6.2 更多标准原文和地方政策

后续可补充：

- 最新版国家标准和地方标准原文；
- 佛山、顺德相关生态环境管理文件；
- 排污许可、VOCs 治理、危废管理相关政策；
- 典型行业技术规范或指南。

补充原则：

- 优先补与当前 skill 直接相关的标准；
- 每份材料必须记录来源、版本、发布日期、适用范围；
- 不建议无目的堆大量政策文本。

## 7. 建议的下一步执行顺序

### 第一批：先补能让实验跑起来的数据

1. 盘点 33 个项目目录，形成 `sample_chain_readiness_table`；
2. 从中挑出 3-5 个最典型、证据链最完整的核心项目；
3. 从 942 条种子 QA 中筛选 30-50 条候选正式评价题；
4. 补齐每题的报告证据、标准依据和真实修改意见；
5. 建立 rejected log。

### 第二批：补能让结果可信的数据

1. 校准 30-50 条标准卡或标准条目；
2. 用真实样本校准 10 个优先 skill；
3. 完成 30-50 题 A/B/C/D 输出；
4. 完成至少 2 名评分者的人工评分；
5. 汇总错误类型和评分分歧。

### 第三批：补能让论文更完整的数据

1. 增加参照样本和排除样本；
2. 补充更多政策和标准来源；
3. 扩展评价题数量；
4. 加入多评审者一致性分析；
5. 形成方法章节和案例章节材料。

## 8. 可以直接安排给我的任务

你可以按下面的任务顺序继续安排我执行：

1. **样本链 readiness 盘点**：我来扫描 `05_样本链（按项目组织）/`，输出每个项目缺哪些材料。
2. **QA 题库清理**：我来修复乱码字段，统一 942 条 QA 的字段名和复核状态。
3. **正式评价题筛选**：我从 942 条 QA 中筛 30-50 条最适合实验的题。
4. **标准库校准清单**：我把 37 条标准卡和 71 条旧版条目合并去重，列出优先人工审查项。
5. **skill 校准样本表**：我按 15 个 skill 找对应真实样本，标注哪些 skill 缺样本。
6. **A/B/C/D 实验数据模板**：我生成实验输入、输出、评分和错误标签 CSV 模板。

## 9. 当前最建议先做的一件事

最建议先做：

> 先对 `05_样本链（按项目组织）/` 做 readiness 盘点，并从 942 条 QA 中筛出 30-50 条证据链完整的正式评价题。

原因是：只有先确定哪些项目和题目能作为正式评价材料，后面的标准库校准、skill 校准和 A/B/C/D 实验才不会悬空。
