# 99_总审核汇总

## 定位

总审核汇总不重新审核报告原文，只汇总各单项 skill 的输出结果。

## 输入

各单项 skill 的 JSON 输出结果（01-15）。

## 输出

1. **总体审核结论**：汇总各 skill 的结论，标注通过/不通过/需复核的比例
2. **主要问题列表**：按严重程度排序（不匹配 > 部分匹配 > 无法判断）
3. **需优先退改的问题**：conclusion="不匹配" 的条目
4. **证据不足的问题**：conclusion="无法判断" 的条目
5. **各 skill 结果汇总表**：skill_id | conclusion | key_findings
6. **人工复核清单**：所有 manual_review_needed=true 的条目

## 约束

- 不得覆盖单项 skill 的结论
- 若各 skill 之间存在冲突，标注：存在结论冲突，需人工复核
- 不得自动做出审批结论（通过/不通过）

## 输出格式

```json
{
  "summary_id": "SUMMARY_YYYYMMDD",
  "report_name": "",
  "total_skills": 15,
  "skills_executed": 0,
  "results": {
    "匹配": 0,
    "不匹配": 0,
    "部分匹配": 0,
    "无法判断": 0
  },
  "priority_issues": [],
  "evidence_gaps": [],
  "skill_results_table": [],
  "conflicts": [],
  "human_review_checklist": [],
  "overall_conclusion": "需人工确认"
}
```
