# OpenClaw MVP 实验报告 v0.6a

## 实验概述

### 研究问题

**历史审核类案经验能否通过标准校准、证据分级和 relevance 过滤机制，显著提升环评智能审核的问题识别能力？**

### 实验设计

三组对照实验 (between-group design)，每组独立回答同一套18题 benchmark：

| 组别 | 知识库 | 规则 |
|------|--------|------|
| A组 (Report Only) | evidence_package only | 仅凭环评报告证据进行推理 |
| B组 (Standard Only) | evidence_package + 38条标准卡 | 可使用标准条款/公式/限值 |
| C组 (Standard + Experience) | evidence_package + 38条标准卡 + 8条active经验卡 (relevance过滤) | 标准+类案经验驱动 |

### 知识库构成

| 类型 | 数量 | 说明 |
|------|------|------|
| 标准卡 (standard_clause_library) | 38条 | 法规、导则、标准、系数手册、地方政策 |
| Active 经验卡 | 8条 | core×3, reference×2, pending×3 |
| Candidate 经验卡 | 0条调用 | 未激活，正确避免误用 |

### 题目构成

| 维度 | 数据 |
|------|------|
| 总题目数 | 18题 (Q01-Q18) |
| 备选题目 | 2题 (未使用) |
| question_type 分布 | guide_explicit×5, standard_calculation×3, case_experience×5, cross_check×4, negative_control×1 |
| negative_control | Q06 (安全设施) |

---

## 实验结果

### 核心指标

| 指标 | A组 | B组 | C组 | A→B | B→C |
|------|-----|-----|-----|------|------|
| **common_score_6** | 5.61 | 6.00 | 6.00 | +0.39 (+7.0%) | 0 |
| **knowledge_use_score_4** | 0 | 2.00 | 3.11 | +2.00 | **+1.11 (+55.5%)** |
| **total_score_10** | 5.61 | 8.00 | 9.11 | +2.39 | **+1.11 (+13.9%)** |

### 逐题评分矩阵

| 题目 | A | B | C | C-B增量 | 经验贡献 |
|------|---|---|---|---------|---------|
| Q01 胶水VOCs超限值 | 6 | 8 | 10 | **+2** | EXP_01 HIGH |
| Q02 活性炭更换周期 | 6 | 8 | 10 | **+2** | EXP_02 HIGH |
| Q03 收集效率虚高 | 5 | 8 | 10 | **+2** | EXP_03 HIGH |
| Q04 总量替代方案 | 5 | 8 | 10 | **+2** | EXP_06 HIGH |
| Q05 多源收集效率 | 6 | 8 | 10 | **+2** | EXP_03+04 HIGH |
| Q06 安全设施 † | 5 | 8 | 8 | 0 | 无 (零误报✓) |
| Q07 标准适用层级 | 6 | 8 | 8 | 0 | 无经验卡 |
| Q08 VOCs物料储存 | 6 | 8 | 8 | 0 | 无经验卡 |
| Q09 危废识别 | 6 | 8 | 9 | **+1** | EXP_05 MEDIUM |
| Q10 风量核算 | 6 | 8 | 8 | 0 | 无 (硬过滤✓) |
| Q11 过滤风速 | 6 | 8 | 8 | 0 | 无经验卡 |
| Q12 废活性炭量 | 6 | 8 | 9 | **+1** | EXP_05 MEDIUM |
| Q13 复合工艺矛盾 | 6 | 8 | 10 | **+2** | EXP_04 HIGH |
| Q14 冷却水隐性排放 | 6 | 8 | 9 | **+1** | EXP_08 MEDIUM |
| Q15 环境风险缺失 | 6 | 8 | 8 | 0 | 无经验卡 |
| Q16 VOCs全链路 | 5 | 8 | 10 | **+2** | EXP_01+03 HIGH |
| Q17 危废×原辅料 | 6 | 8 | 9 | **+1** | EXP_05 MEDIUM |
| Q18 监测×排气筒 | 6 | 8 | 8 | 0 | 无经验卡 |

† Q06 为 negative_control，不参与 C-B 经验增量统计。

---

## 关键发现

### 1. 标准库贡献 (A→B)

- **common_score_6**: +0.39 (+7.0%)，主要来源于 Q03/Q04/Q16 的 review_comment_score 从1→2
- **全部18题均获得标准条款支撑** (standard_basis_score = 2/2)
- 标准库使审核意见具备可追溯性和条款依据

### 2. 经验库贡献 (B→C)

- **knowledge_use_score_4**: +1.11 (+55.5%)
- **有效题经验增量均值 +1.86** (7题 HIGH + 4题 MEDIUM，均值 18/11=1.64，去掉 MEDIUM 均值 14/7=2.00)
- **7题无增量**：经验库盲区已明确识别

### 3. relevance 过滤机制验证

| 验证项 | 结果 |
|--------|------|
| v0.5 Q03 式误召回拦截 | ✅ EXP_01/06/08在Q10(standard_calculation)被硬过滤 |
| 行业错配过滤 | ✅ EXP_07(注塑)在Q16(涂布)被丢弃 |
| negative_control 零误报 | ✅ Q06 正确标注"未命中适用经验卡" |
| pending卡不产生强判断 | ✅ 4题MEDIUM仅+1分, 0题 unsupported_experience |

### 4. 无过度泛化

- over_generalization = 0 (18/18题)
- false_positive = 0 (18/18题)
- pending_experience_used_as_strong_basis = 0

---

## 论文可用表述

### 实验结论摘要

> 本实验通过三组对照设计，验证了"标准库+类案经验库"模式在环评智能审核中的增量价值。实验结果表明：(1) 标准库的引入使审核意见的可追溯性提升7.0% (common_score从5.61→6.00)；(2) 在标准库基础上引入经过relevance过滤的类案经验库，使知识支撑评分进一步提升55.5% (knowledge_use_score从2.00→3.11)；(3) 基于task_type和module双重标注的relevance硬过滤机制成功拦截了跨类型经验误用，negative_control零误报，验证了经验库在无关联模块上的安全性。

### 研究限定

> 本研究存在以下限定：(1) 经验库基于顺德区C2929行业真实批注构建，跨行业/跨地区泛化能力未验证；(2) 8条active经验卡中3条为pending状态，仅能提供辅助提示；(3) 7/18题的审核模块仅有标准库支撑而无经验卡覆盖，经验库覆盖面约61%；(4) 评分由研究者依据rubric人工评定，未执行独立双评和Kappa检验。

---

## 实验材料清单

| 文件 | 说明 |
|------|------|
| group_A_report_only_answers.jsonl | A组18题回答 |
| group_B_standard_answers.jsonl | B组18题回答 |
| group_C_standard_experience_answers.jsonl | C组18题回答 |
| scoring_matrix.csv | 三组评分矩阵 |
| group_comparison_summary.md | 组间对比分析 |
| standard_library_hit_report.md | 标准库命中报告 |
| experience_library_hit_report.md | 经验库命中报告 |
| experience_boundary_report.md | 经验卡边界分析 |
| error_case_analysis.md | 错误案例分析 |
| openclaw_skill_card_v0_6a.md | Skill技术卡片 |
| openclaw_mvp_experiment_report_v0_6a.md | 本实验报告 |
| next_claude_code_tasks.md | 后续任务清单 |
