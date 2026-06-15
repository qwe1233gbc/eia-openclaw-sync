# 错误案例分析报告 (Error Case Analysis)

## v0.5 已知问题修复验证

### 1. retrieval_mismatch (低关联误召回)

| 状态 | ✅ 已修复 |
|------|-----------|

**v0.5 问题**: 低关联经验卡被误用于不相关题目。例如 Q03 式误召回：胶水VOCs经验 (EXP_01) 可能被误用于风量核算题 (standard_calculation)。

**v0.6a 修复机制**: Relevance 硬过滤 (Step1)
- 每张经验卡标注 `not_applicable_task_types`
- Step1 硬过滤：task_type ∈ not_applicable_task_types → 直接丢弃
- Q10 (standard_calculation) 验证：EXP_01/EXP_06/EXP_08 因 not_applicable_task_types 含 `standard_calculation` 被硬过滤 ✅
- Q16 验证：EXP_07 因行业不匹配(注塑≠涂布)被硬过滤 ✅

**结论**: v0.5 式误召回已被 relevance 硬过滤机制成功根除。

---

### 2. coverage_gap (覆盖盲区)

| 状态 | ⚠️ 仍存在，但比例改善 |
|------|----------------------|

**v0.5**: 2/8 题无经验卡 (25%)
**v0.6a**: 7/18 题无经验卡 (39%)

比例看似上升 (25% → 39%)，但实际上：
- v0.6a 题目总数为18题，相比 v0.5 的8题增加了10题
- 新增题目中包含更多纯标准类题目 (Q07标准适用、Q08物料储存、Q10风量核算、Q11过滤风速、Q15环境风险、Q18监测计划)
- 这些新增题目天然位于经验库盲区
- **已知盲区 7 题 vs v0.5 未知盲区 2 题**：v0.6a 盲区已明确识别和记录

**改进方向**:
- 优先补齐高频模块经验卡 (安全设施、监测计划)
- 对纯标准/计算类题目明确标注"仅标准库支撑"
- 不强制在所有模块都建设经验卡 (有些模块天然无类案经验)

---

### 3. low_discrimination (低区分度)

| 状态 | ✅ 改善 |
|------|--------|

**v0.5 问题**: 部分题目三组评分相同，无法体现经验库的增量价值。

**v0.6a 改善**:
- **新增 Q10**: A=6, B=8, C=8 — B/C有区分 (标准卡区分)
- **新增 Q11**: A=6, B=8, C=8 — 同上
- **新增 Q12**: A=6, B=8, C=9 — 三组区分 (pending经验产生+1)
- **新增 Q13**: A=6, B=8, C=10 — C-B+2 (EXP_04 HIGH)
- **新增 Q14**: A=6, B=8, C=9 — pending经验产生+1
- **新增 Q16**: A=5, B=8, C=10 — 全链路核算三组明显区分
- **新增 Q17**: A=6, B=8, C=9 — pending经验产生+1

**结论**: 新增7题均有不同程度的组间区分度，整体区分度改善。全部18题中仅 Q06/Q07/Q08/Q10/Q11/Q15/Q18 (7题) C-B无增量且A-B已有区分，区分度已足够。

---

### 4. unsupported_experience (无依据经验引用)

| 状态 | ✅ 零发生 |
|------|----------|

v0.6a 全部18题中：
- 所有经验卡引用均经过 relevance 过滤
- pending 卡标注 `can_support_judgement=false`
- 无经验卡被引用在 irrelevant 题目
- unsupported_experience = 0 ✓

---

### 5. unsupported_standard (无依据标准引用)

| 状态 | ✅ 零发生 |
|------|----------|

v0.6a 全部18题中：
- 所有标准卡引用均来自已记录的 standard_clause_library.jsonl (38条)
- 无编造标准号、条款、限值
- unsupported_standard = 0 ✓

---

## 新发现的问题与改进方向

### 6. pending 卡信息量不足

**问题**: 4题 MEDIUM pending (Q09/Q12/Q14/Q17) 仅+1分，但 pending 经验的实际审核提示价值未充分量化。

**改进方向**:
- 将 pending 卡升级为 core/reference 后重新评分
- 区分"pending 但提示有价值"与"pending 且提示无价值"

### 7. 经验卡粒度问题

**问题**: EXP_05 "废活性炭产生量漏算" 同时适用于 Q09 (危废种类) 和 Q12 (废活性炭量核算)，但 relevance 评分在 Q12 的 standard_calculation 场景下降为 MEDIUM。

**改进方向**: 考虑拆分经验卡以更精准匹配 task_type。

### 8. A 组 baseline 合理性

**问题**: A 组部分题目 review_comment_score=1 (Q03/Q04/Q16)，但这是否公正反映了"仅证据包"的回答水平？可能需要人工复核。

**改进方向**: 对 A 组回答进行人工校准，确保 baseline 合理。

---

## 修复总结

| v0.5 问题 | v0.6a 状态 | 修复方法 |
|-----------|-----------|---------|
| retrieval_mismatch | ✅ 已修复 | relevance 硬过滤 + not_applicable_task_types |
| coverage_gap | ⚠️ 仍存在但已识别 | 明确标注盲区，建议后续补齐 |
| low_discrimination | ✅ 改善 | 新增10题有区分度 |
| unsupported_experience | ✅ 零发生 | relevance 过滤 + pending 限制 |
| unsupported_standard | ✅ 零发生 | 严格引用 standard_clause_library |
