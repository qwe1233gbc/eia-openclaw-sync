# 11_废气设计风量审核

## 0. Skill定位

本Skill是环境专业审核程序，不是法规知识副本。它负责报告证据抽取、RAG查询构造、适用性比较、内部复算、异常处理和结构化输出。具体标准、条款、限值、版本和固定适用结论必须由运行时`rag_evidence`提供。

来源工作流：`06_Dify工作流/18-废气收集风量与设计风量核算.yml`。旧Dify工作流仅作历史平台实现，不直接作为C/D组Skill输入。

## 1. 审核目标

根据罩型、开口面积、控制风速、距离、同时运行设备和系统阻力复算理论风量，并与设计风量比较。

## 2. 触发条件

1. 报告给出集气罩或密闭空间风量
2. 存在多个支路或同时运行设备
3. 理论风量、设计风量和风机参数需要核对

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
    "pollution_medium": "",
    "emission_mode": "",
    "valid_time": ""
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
| `hood_type` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `opening_dimensions` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `source_distance` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `control_velocity` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `simultaneous_sources` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `room_volume` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `air_changes` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `duct_loss` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `theoretical_airflow` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `design_airflow` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `fan_rating` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |

每个使用的字段必须绑定`evidence_id + source_section + source_location + quote`；报告证据与外部依据必须分开保存。

## 5. 报告证据抽取顺序

1. 收集形式和罩型
2. 几何尺寸
3. 控制风速或换气次数
4. 同时运行数量
5. 支路与系统损失
6. 理论风量
7. 设计风量和风机参数

抽取时保留相互冲突的全部位置，不得只选择支持预设结论的片段。

## 6. RAG查询构造

查询只使用报告事实和审核类别，不使用外部评判标签、题号、评分或Skill预设结论。组合以下维度：

- 罩型
- 污染源几何
- 控制风速参数
- 换气次数
- 设计规范
- 工况

统一查询模板：`{audit_category} {region} {industry} {process} {pollution_medium} {emission_mode} {report_cited_standard} {report_date}`。

## 7. 审核程序

1. 选择与收集形式匹配的计算方法
2. 核对每个参数来源
3. 复算单点和总系统风量
4. 检查同时运行、漏风和余量是否重复
5. 规范参数缺少RAG时只复核报告内部算术

不得根据模型记忆补充法规、限值、版本或适用结论。

## 8. 计算与内部一致性复核

1. 局部收集按报告采用的面积—速度或罩型公式复算
2. 整体换风按空间体积和换气次数复算
3. 单位统一后比较理论风量、设计风量和风机额定值

纯算术和报告内部一致性不依赖RAG；外部规范参数必须标注`source_id`和条款来源。

## 9. 外部依据比较

仅当`rag_evidence`存在且来源、版本、有效时点及适用性维度足以判断时，才逐项比较报告值与RAG值。比较至少记录地区、行业、工艺、污染介质、排放形式和有效时点；任一关键维度未知时不得输出确定的外部依据结论。

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

只审核风量计算；收集形式合理性和收集效率由10、12 Skill处理。
