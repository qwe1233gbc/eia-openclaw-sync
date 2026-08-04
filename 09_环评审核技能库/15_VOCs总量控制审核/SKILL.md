# 15_VOCs总量控制审核

## 0. Skill定位

本Skill是环境专业审核程序，不是法规知识副本。它负责报告证据抽取、RAG查询构造、适用性比较、内部复算、异常处理和结构化输出。具体标准、条款、限值、版本和固定适用结论必须由运行时`rag_evidence`提供。

来源工作流：`无独立Dify工作流；汇总源强核算、排放标准与总量控制章节证据`。旧Dify工作流仅作历史平台实现，不直接作为C/D组Skill输入。

## 1. 审核目标

核对VOCs产生、收集、处理、有组织/无组织排放、以新带老和总量申请之间的口径与算术闭合，并比较RAG返回的有效管理要求。

## 2. 触发条件

1. 项目产生或排放VOCs
2. 报告提出总量控制指标、替代或削减来源
3. 总量章节与源强表存在口径差异

未触发时输出`不适用`，不得为完成任务而创造项目事实。

## 3. 输入契约

```json
{
  "question": "",
  "audit_category": "",
  "report_evidence": [],
  "rag_evidence": [],
  "project_metadata": {},
  "case_hints": []
}
```

`report_evidence`单元：

```json
{
  "evidence_id": "",
  "field": "",
  "value": "",
  "unit": "",
  "source_section": "",
  "source_location": "",
  "quote": "",
  "chunk_id": ""
}
```

`rag_evidence`单元：

```json
{
  "source_id": "",
  "document_title": "",
  "document_number": "",
  "clause_number": "",
  "content": "",
  "applicability": {
    "region": "",
    "industry": "",
    "process": "",
    "VOCs_scope": "",
    "calculation_period": "",
    "policy_valid_time": ""
  },
  "effective_date": "",
  "validity_status": "",
  "source_sha256": ""
}
```

`case_hints`只允许`source_type=expert_heuristic`或`case_experience`，只能形成风险提示，不能单独支撑最终正确/错误结论。

## 4. 报告证据字段

| 字段 | 要求 |
|---|---|
| `vocs_generation` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `organized_emission` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `unorganized_emission` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `treatment_reduction` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `existing_project_emission` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `replacement_reduction` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `reported_total` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `requested_total` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `management_basis` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `report_date` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |

每个使用的字段必须绑定`evidence_id + source_section + source_location + quote`；报告证据与外部依据必须分开保存。

## 5. 报告证据抽取顺序

1. VOCs物料和工艺
2. 源强核算
3. 有组织和无组织排放
4. 治理削减
5. 现有工程与以新带老
6. 总量章节
7. 申请和替代依据

抽取时保留相互冲突的全部位置，不得只选择支持预设结论的片段。

## 6. RAG查询构造

查询只使用报告事实和审核类别，不使用外部评判标签、题号、评分或Skill预设结论。组合以下维度：

- 地区
- 行业
- 项目性质
- 污染物口径
- 总量管理文件
- 报告日期

统一查询模板：`{audit_category} {region} {industry} {process} {VOCs_scope} {calculation_period} {policy_valid_time}`。

## 7. 审核程序

1. 统一VOCs统计口径和单位
2. 汇总有组织与无组织排放
3. 核对削减量是否重复
4. 比较源强、总量表和申请值
5. 根据RAG返回的管理要求判断适用性
6. 没有RAG时只评价内部算术和口径一致

不得根据模型记忆补充法规、限值、版本或适用结论。

## 8. 计算与内部一致性复核

1. total_emission = organized_emission + unorganized_emission
2. net_increment = proposed_emission - verified_existing_reduction
3. 所有削减和替代参数必须绑定证据

纯算术和报告内部一致性不依赖RAG；外部规范参数必须标注`source_id`和条款来源。

## 9. 外部依据比较

仅当`rag_evidence`存在且来源、版本、有效时点及本Skill的必要适用性维度足以判断时，才逐项比较报告值与RAG值。本Skill必须核对：`region`、`industry`、`process`、`VOCs_scope`、`calculation_period`、`policy_valid_time`。不相关字段不得作为强制门槛；任一必要维度未知时，不得输出确定的外部依据结论。

## 10. 证据不足与降级规则

- `rag_evidence`充分且可适用：`basis_status=available`。
- 本任务不需要外部规范常量，只做报告内部算术或一致性：`basis_status=not_required`。
- 需要外部依据但RAG为空、版本未知、条款不适用或来源不可追溯：`basis_status=insufficient`，结论降级为`无法判断`或仅报告内部问题。
- C组没有RAG时仍完成证据抽取和可独立复算，但不得给出法规限值、固定标准适用结论，也不得把“缺少RAG”误判为“报告错误”。

## 11. 结论分级

- `匹配`：报告证据充分，所需RAG依据可追溯且适用，比较或复算无冲突。
- `不匹配`：报告证据明确，且内部复算或适用RAG依据显示实质冲突。
- `部分匹配`：主体成立，但存在非核心缺漏或局部不一致。
- `无法判断`：关键报告证据或外部依据不足。
- `不适用`：项目事实未触发本审核条目。

## 12. 输出契约

```json
{
  "skill_id": "",
  "conclusion": "",
  "report_evidence_used": [],
  "rag_basis_used": [],
  "basis_status": "available | insufficient | not_required",
  "applicability_check": [],
  "calculation_trace": [],
  "missing_evidence": [],
  "risk_hints": [],
  "manual_review_needed": false,
  "review_comment": ""
}
```

输出必须为合法JSON。`review_comment`应明确“报告事实—外部依据—比较过程—建议修改”，不得输出未提供的项目事实。

## 13. 人工复核规则

出现以下任一情况时`manual_review_needed=true`：关键证据位置缺失；报告前后冲突；RAG版本或适用性不明；结论为不匹配、部分匹配或无法判断；计算参数缺少来源；经验提示与正式依据冲突。

## 14. 非规范经验提示

常见错误和类案只能写入`risk_hints`，必须带`source_type`、适用场景和局限性。经验阈值、历史修改意见或同类项目惯例不得冒充法条，不能单独支撑最终判断。

## 15. 与其他Skill边界

只审核VOCs总量口径；源强、收集、治理参数和排放标准由09—13及07 Skill提供。
