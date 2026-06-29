# 99_总审核汇总

## 0. Skill 定位

`总审核汇总 skill = 汇总器，不是裁判员`。它只接收 01–15 单项 skill 的 JSON 输出，负责合并问题、排序风险、生成经办人审核意见清单；不得替代单项 skill 重做判断，也不得把“无法判断”改写成“匹配”。

## 1. 输入契约

| 字段 | 类型 | 说明 |
|---|---|---|
| `skill_results` | array | 01–15 单项 skill 输出，必须符合 `common_output_schema.json`。 |
| `project_metadata` | object | 项目名称、报告版本、样本编号、解析时间。 |
| `review_mode` | string | `full_review`、`ablation_llm_only`、`ablation_law_only`、`workflow_only`、`law_plus_workflow`。 |

## 2. 汇总主线

`单项结论 → 风险分级 → 证据缺口归并 → 修改意见生成 → 消融实验标签输出`。

## 3. 风险分级

- 一级风险：结论为“不匹配”，且涉及行业类别、三线一单、排放标准、源强核算、废气治理、危废识别、总量控制。
- 二级风险：结论为“部分匹配”，或计算可复核但存在参数缺失。
- 三级风险：结论为“无法判断”，但仅因页码、表名、附件缺失导致。
- 不列风险：结论为“匹配”或“不适用”，但仍保留证据索引用于追溯。

## 4. 去重规则

同一证据缺口被多个 skill 命中时，只生成一条综合修改意见。例如“缺少胶水 MSDS”可能同时影响 08 产污系数、09 源强核算、14 危废识别，应归并为：`补充胶水 MSDS，并同步修正 VOCs 含量、源强核算和危废识别依据`。

## 5. 输出 JSON

```json
{
  "project_id": "",
  "review_mode": "law_plus_workflow",
  "overall_conclusion": "建议退回修改 | 建议补正后通过 | 基本可通过 | 无法形成总评",
  "risk_summary": {
    "level_1": [],
    "level_2": [],
    "level_3": []
  },
  "merged_review_comments": [],
  "missing_evidence_index": [],
  "law_basis_index": [],
  "skill_result_index": [],
  "ablation_tags": {
    "uses_llm": true,
    "uses_law_library": true,
    "uses_skill_workflow": true,
    "uses_case_memory": false
  }
}
```

## 6. 总评规则

- 任一一级风险未解决 → `建议退回修改`。
- 无一级风险，但存在二级风险 → `建议补正后通过`。
- 仅存在三级风险且不影响实质判断 → `基本可通过`。
- 多个核心 skill 为“无法判断” → `无法形成总评`。

## 7. 给经办人的汇总意见格式

按“问题位置 → 问题性质 → 修改动作 → 关联 skill”输出，不按 skill 机械罗列。每条意见必须包含至少一个证据位置或明确写“证据位置缺失，需人工定位”。
