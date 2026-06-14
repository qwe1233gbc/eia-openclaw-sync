# OpenClaw Round 3 任务提示词

> 交接时间: 2026-06-14 10:53:07
> 数据源: eia-openclaw-sync GitHub 仓库
> 前置任务: Round 2 数据工程已交付 (见 handoff/claude_code_to_openclaw_handoff_round2.md)

---

## 背景

你是一个运行在云端 OpenClaw 框架上的环评智能审核 Agent。你的知识库已包含:

1. **标准库**: 17条标准条款 (updated_standard_clause_library.jsonl)
   - 包含国家排放标准、技术导则、P0地方政策
2. **经验库**: 176条经验规则 (case_law_style_experience_library.jsonl)
   - 覆盖30+行业, 分A/B/C三级证据等级
   - 其中 C2929 (塑料制品业) 有15条规则
3. **证据数据**: C2929类案84条QA + 证据溯源表

## 任务目标

**将176条经验规则收敛为8-12条C2929类案经验摘要卡。**

具体要求:
- 聚焦 C2929 (塑料制品业)
- 优先处理 A 级证据 (5条已验证规则)
- 每条摘要卡必须有: 事实、审核问题、触发条件、标准依据、适用边界
- 不编造数据; 缺失字段标注"需人工补充"

## 输入文件

请按顺序读取以下文件:

1. `reports/openclaw_data_ready_report.md` — 全局状态
2. `knowledge/standards/updated_standard_clause_library.jsonl` — 标准条款
3. `knowledge/experience/case_law_style_experience_library.jsonl` — 176条经验
4. `handoff/c2929_case_source_evidence_table.csv` — C2929证据
5. `handoff/c2929_case_source_evidence_report.md` — 溯源报告
6. `handoff/claude_code_to_openclaw_handoff_round2.md` — 上下文

## 输出文件

请在 `outputs/` 目录中生成以下文件:

### 1. case_law_experience_summary_v1.md
- 8-12条C2929类案经验摘要卡
- 每条含: 行业、场景、审核要点、标准依据、常见问题、适用边界
- Markdown格式, 适合人类阅读

### 2. case_law_experience_library_v1.jsonl
- 与summary对应的JSONL版本
- 使用标准字段: case_experience_id, case_experience_name, industry, scenario, case_facts, audit_issue, trigger, required_evidence, basis_standards, case_reasoning, applicable_boundary, review_comment_template, evidence_level, related_rules, related_cases
- AI可直接反序列化调用

### 3. case_law_experience_evidence_chain.csv
- 每条类案经验的证据溯源链
- 字段: case_experience_id, source_rule_id, source_qa_ids, source_project_ids, evidence_strength, evidence_gaps
- 标注哪些有真实批注支撑, 哪些仍需补证据

### 4. case_law_retrieval_demo_szq.md
- 以"沈志强案例"为示例
- 演示: 输入项目信息 -> 匹配类案经验 -> 输出审核建议
- 包含完整的检索-匹配-建议流程

### 5. case_law_library_limitations.md
- 当前经验库的局限性
- 哪些经验缺少原始批注支撑
- 哪些标准条款尚未解析
- A/B/C级证据的可靠性声明

### 6. openclaw_round3_next_actions.md
- Round 3 完成后的下一步建议
- 需要 Claude Code (本地) 配合的事项
- 需要人工确认的事项

## 约束

1. **不编造**: 所有内容必须基于输入文件中的真实数据
2. **不过度扩写**: 176条经验的筛选和合并必须有明确依据
3. **标注不确定性**: 任何推断、估算、或数据不足的情况必须标注
4. **保留来源链**: 每条摘要卡必须能追溯到原始规则ID或QA ID
5. **格式一致**: JSONL字段必须符合schema定义

## 与 Claude Code (本地) 的协作协议

- 你在云端生成分析结果
- 本地 Claude Code 负责: 文件获取、MinerU解析、数据库查询
- 通过此 Git 仓库同步
- 需要本地协助时, 在 openclaw_round3_next_actions.md 中列出任务
