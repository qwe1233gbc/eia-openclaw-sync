# 07_污染物排放标准审核

## 0. Skill定位

本Skill是环境专业审核程序，不是法规知识副本。它负责报告证据抽取、RAG查询构造、适用性比较、内部复算、异常处理和结构化输出。具体标准、条款、限值、版本和固定适用结论必须由运行时`rag_evidence`提供。

来源工作流：`06_Dify工作流/8-污染物排放标准内容判断.yml`。旧Dify工作流仅作历史平台实现，不直接作为C/D组Skill输入。

## 1. 审核目标

按污染源、污染因子、排放方式、去向、地区和有效时点，核验废气、废水、噪声、一般固废和危险废物控制依据的完整性与适用性。

## 2. 触发条件

1. 报告列示污染物排放或固废控制标准
2. 污染源—污染因子—排放形式需要匹配
3. 纳管、回用、外排、有组织或无组织边界需要判断

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
    "pollutant": "",
    "pollution_medium": "",
    "emission_mode": "",
    "discharge_destination": "",
    "valid_time": ""
  },
  "effective_date": "",
  "validity_status": "",
  "source_sha256": ""
}
```

`case_hints`只允许`source_type=expert_heuristic`或`case_experience`，只能形成风险提示，不能单独支撑最终正确/错误结论。

适用性字段允许使用`not_applicable`明确表示当前污染介质不需要该维度；`not_applicable`不等于缺失。只有当前介质真正必要的字段为`null`、空值或无法从报告证据确定时，才可据此判定`basis_status=insufficient`。

## 4. 报告证据字段

| 字段 | 要求 |
|---|---|
| `pollution_source` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `process` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `pollutant` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `pollution_medium` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `emission_mode` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `discharge_destination` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `treatment_facility` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `reported_standard` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `reported_limit` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `stack_or_outlet_parameters` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |
| `report_date` | 从报告原文抽取；缺失填`null`并进入`missing_evidence` |

每个使用的字段必须绑定`evidence_id + source_section + source_location + quote`；报告证据与外部依据必须分开保存。

## 5. 报告证据抽取顺序

1. 工艺和产污环节
2. 污染因子
3. 治理设施
4. 有组织/无组织/厂区内
5. 纳管/回用/外排去向
6. 报告标准表及限值
7. 固废类别与贮存方式

抽取时保留相互冲突的全部位置，不得只选择支持预设结论的片段。

## 6. RAG查询构造

查询只使用报告事实和审核类别，不使用外部评判标签、题号、评分或Skill预设结论。组合以下维度：

- 地区
- 行业
- 工艺
- 污染介质
- 污染因子
- 排放形式
- 排放去向
- 报告引用标准
- 报告日期

统一查询模板：`{audit_category} {region} {industry} {process} {pollutant} {pollution_medium} {emission_mode} {discharge_destination} {valid_time}`。

按介质条件化构造查询：废气重点填充`pollutant`、`emission_mode`及排放口/厂界条件；废水重点填充`pollutant`、`discharge_destination`及纳管、外排或回用条件；噪声重点填充厂界、功能区、时段和边界条件，`discharge_destination=not_applicable`不构成缺失；固体废物重点填充废物类别、贮存方式、利用处置去向和有效版本，`emission_mode=not_applicable`不构成缺失。

## 7. 审核程序

1. 建立工序—污染物—治理—排放形式清单
2. 按介质和去向分别查询RAG
3. 依据RAG返回的适用范围、例外和版本筛选候选标准
4. 逐项比较报告标准、条款和限值
5. 核对污染源覆盖是否完整
6. 固废与危废只用RAG返回的法律、名录、鉴别和贮存条款判断

不得根据模型记忆补充法规、限值、版本或适用结论。

## 8. 计算与内部一致性复核

1. 执行单位、基准条件和排放速率换算时记录参数来源
2. 不得在Skill中预置具体标准号、类别限值或固定适用结论

纯算术和报告内部一致性不依赖RAG；外部规范参数必须标注`source_id`和条款来源。

## 9. 外部依据比较

仅当`rag_evidence`存在且来源、版本、有效时点及本Skill的必要适用性维度足以判断时，才逐项比较报告值与RAG值。本Skill的通用维度为`region`、`industry`、`process`、`pollutant`、`pollution_medium`、`emission_mode`、`discharge_destination`、`valid_time`，但应按介质解释：废气核对污染物、排放形式和排放口/厂界；废水核对污染物、去向和纳管/外排/回用；噪声核对厂界、功能区、时段和边界；固废核对类别、贮存、利用处置去向和版本。明确的`not_applicable`应视为已判定不适用，不得作为缺失门槛；真正必要维度未知时才不得输出确定的外部依据结论。`metadata_only_source_ids`只能提示标准存在和正文缺口，不得放入`rag_evidence`或支撑匹配/不匹配；若结论依赖该正文，必须输出`basis_status=insufficient`、`conclusion=无法判断`、`manual_review_needed=true`。

## 10. 证据不足与降级规则

- `rag_evidence`充分且可适用：`basis_status=available`。
- 本任务不需要外部规范常量，只做报告内部算术或一致性：`basis_status=not_required`。
- 需要外部依据但RAG为空、版本未知、条款不适用或来源不可追溯：`basis_status=insufficient`，结论降级为`无法判断`或仅报告内部问题。
- 字段为`not_applicable`时先按污染介质核实其确实不适用；经核实后不得仅因该字段判定`insufficient`。废气、废水、噪声、固废分别按第6节的条件化必要字段判断。
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

本Skill核验控制标准；污染源定量核算、危险废物识别和环境质量标准分别由09、14和06 Skill处理。
