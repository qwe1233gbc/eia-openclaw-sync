# 缺失文件与补采任务清单

> 生成时间：2026-06-14
> 来源：标准-经验校准过程 + C2929 Demo 审核过程中发现的缺失文件
> 交付给：Claude Code 后续补采执行

---

## 任务格式说明

每个任务采用以下格式：

```
TASK: <任务编号>
PRIORITY: P0(必须) / P1(重要) / P2(补充)
TYPE: file_fetch(文件获取) / file_parse(解析) / db_update(入库)
SOURCE: <缺失文件名称或来源>
REASON: <为何需要此文件>
DEPENDS_ON: <依赖的其他任务>
EXPECTED_OUTPUT: <预期的产出物路径>
NOTE: <补充说明>
```

---

## TASK 列表

---

```
TASK: T01
PRIORITY: P0
TYPE: file_fetch
SOURCE: 佛环函(2024)70号《佛山市生态环境局关于进一步规范活性炭吸附治理设施技术要求的通知》
REASON: EXP_C2929_AC_001 规则的核心标准依据。规则引用的碘值>=800mg/g、过滤风速<=0.6/0.4m/s、停留时间>=0.5s 等参数阈值均来源于此文件。当前标准库中无该文件的原文，所有参数判断均依赖规则自述，论文中引用存在证据链断裂风险。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/佛环函2024-70号_活性炭技术要求.txt
NOTE: 如无法获取原件，可从佛山市生态环境局官网公开文件页面下载。验证参数阈值的准确性，确认不同活性炭类型（煤质/木质/椰壳/蜂窝/柱状）是否有不同要求。
```

---

```
TASK: T02
PRIORITY: P0
TYPE: file_fetch
SOURCE: 顺环委办(2023)19号《顺德区挥发性有机物总量管理方案》（或等效文件）
REASON: EXP_C2929_AIR_002 规则的核心标准依据。规则引用的"不达标区VOCs削减替代"和"1:2替代比例"均来源于此文件。需核实文件名、文号、条款和具体的替代比例规定。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/顺环委办2023-19号_VOCs总量管理.txt
NOTE: 替代比例是否确实为1:2？是否区分不同行业？是否有其他等效或替代文件？需核实。
```

---

```
TASK: T03
PRIORITY: P0
TYPE: file_fetch + file_parse
SOURCE: 原辅材料表记录（缺失的原始审核批注）
REASON: 当前经验规则库中大部分规则缺少 source_comment（原始批注文字），无法验证规则是否来自真实审核批注。需从原始审核批注 csv/jsonl（如 qa_all_labeled.jsonl, 1312条）中提取20-30条C2929相关的 source_comment。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/experience/source_comments_c2929.jsonl
NOTE: 重点关注：（1）VOCs收集效率；（2）活性炭参数；（3）危废遗漏；（4）标准适用错误；（5）总量核算类批注。每条批注需标注来源文件、页码（如有）。
```

---

```
TASK: T04
PRIORITY: P1
TYPE: file_fetch + file_parse
SOURCE: 广东VOCs核算方法(2023修订版) 附录A 废气收集效率表
REASON: 收集效率取值（顶吸罩20-60%、侧吸罩20-40%、密闭罩80-95%等）是风量核算和源强判断的基础参数。当前标准库中有该文件记录但未见完整的收集效率表条款。需补充完整表格数据。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/广东VOCs核算方法2023_收集效率表.txt
NOTE: 同时验证"半密闭集气罩65%"是否在该文件的规定范围内。
```

---

```
TASK: T05
PRIORITY: P1
TYPE: file_fetch + file_parse
SOURCE: 292系数手册《排放源统计调查产排污核算方法和系数手册》塑料制品行业章节
REASON: 源强核算的核心依据。需确认：（1）注塑工艺的VOCs产污系数；（2）系数的单位（kg/t-原料 还是 kg/t-产品 还是 g/kg）；（3）是否区分不同塑料种类（PP/ABS/PA/PBT等）的系数；（4）回用料是否影响系数取值。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/292系数手册_塑料制品_C2929.txt
NOTE: 盛之强案例中报告引用了此系数手册，需核实产污系数 0.277t/a 的计算过程是否合理。
```

---

```
TASK: T06
PRIORITY: P1
TYPE: file_fetch + file_parse
SOURCE: 佛环(2024)20号《佛山市顺德区三线一单生态环境分区管控方案》
REASON: EXP_C2929_SPATIAL_001 规则的核心依据。需补充文件全文（特别是顺德区各管控单元的准入清单条款），以便在审核中检索具体条款（如1-3产业限制、1-4大气限制、3-7污染物排放管控等）。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/佛环2024-20号_顺德三线一单.txt
NOTE: 当前文件中可能已有三线一单清单的嵌入文本，需确认是否完整。
```

---

```
TASK: T07
PRIORITY: P1
TYPE: db_update
SOURCE: standard_clause_library.jsonl
REASON: 当前标准条款库的14条记录为从报告"执行标准"章节自动抽取，缺少标准原文中的表格数据、公式和适用范围条款。需补充至少以下标准的完整条款级记录：GB31572-2015（表4/表5）、DB44/2367-2022（表1-表3：收集效率附录）、GB18597-2023（危废贮存技术要求）、GB14554-93（表1/表2）。
DEPENDS_ON: T01, T02, T04, T05, T06（需先获取原文才能抽取条款）
EXPECTED_OUTPUT: knowledge/standards/standard_clause_library_checked.jsonl（增量补充）
NOTE: 逐条记录需包含：standard_id, clause_number, clause_text, clause_type（限值/公式/表格/适用范围）, applicable_scenario, source_page。
```

---

```
TASK: T08
PRIORITY: P1
TYPE: file_fetch
SOURCE: 顺德区排水许可证管理口径文件（或等效地方管理文件）
REASON: EXP_C2929_WW_001 规则的依赖文件。间接冷却水排雨水管网是否符合顺德区现行口径，需要地方正式文件支撑。如无正式文件，需确认经办人的通行做法并记录为经验规则。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/顺德排水管理口径.txt
NOTE: 如无正式文件，可从历史审核批注中抽取关于"冷却水排雨水"的处理口径，作为经验记录而非标准条款。
```

---

```
TASK: T09
PRIORITY: P2
TYPE: file_fetch
SOURCE: GB30981.2-2025《工业防护涂料中有害物质限量 第2部分：塑料制品用涂料》
REASON: 虽然盛之强案例不涉及涂装，但此标准是C2929相关标准之一。2025年新发布，2026年6月实施。当前全网无免费电子版。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/GB30981_2-2025.txt（2026年6月后）
NOTE: 2026年6月实施后可能公开。如研究时间紧迫，可先标注为"待实施后补充"。
```

---

```
TASK: T10
PRIORITY: P2
TYPE: file_parse
SOURCE: 佛山声功能区划正式文件
REASON: 噪声审核依赖该文件确认项目所在区域的声环境功能区类别（3类是否正确）。
DEPENDS_ON: none
EXPECTED_OUTPUT: knowledge/standards/parsed_texts/佛山声功能区划.txt
NOTE: 当前仅有征求意见稿。如正式版已发布，建议获取正式版。
```

---

```
TASK: T11
PRIORITY: P2
TYPE: db_update
SOURCE: 盛之强案例完整审核记录
REASON: 当前的 review_workflow_annotation.md 已经完成了20个步骤的模拟经办人审核流程标注，可以作为 benchmark 的 gold answer 来使用。需将其结构化为标准 benchmark 条目格式。
DEPENDS_ON: none
EXPECTED_OUTPUT: benchmark/benchmark_items_shengzhiqiang.jsonl
NOTE: 按 benchmark_items.jsonl 格式结构化每条审核发现，标注 source（标准库/经验库）、gold_answer、scoring_rubric。
```

---

```
TASK: T12
PRIORITY: P2
TYPE: db_update
SOURCE: 经验规则缺失字段补充
REASON: C级157条规则中42条无 common_standards，需要为标准库中搜索相关标准并补充关联。但此任务的ROI取决于这些模板化规则是否真的被使用。
DEPENDS_ON: T07（需先完善标准库）
EXPECTED_OUTPUT: knowledge/experience/experience_rules_all_supplemented.json
NOTE: 建议只在明确会用到某条规则时才补充其标准关联，不需要批量处理157条。
```

---

## 任务依赖图

```text
T01(佛环函70号) ────┐
T02(顺环委办19号) ───┤
T04(VOCs核算方法) ───┼──→ T07(完善标准条款库)
T05(292系数手册) ───┤
T06(三线一单方案) ───┘

T03(原始批注) ──→ 独立的经验规则补采

T08(排水口径) ──→ 独立的经验依赖

T07(完善标准库) ──→ T12(补充经验规则标准关联) [可选]

T11(benchmark结构化) ──→ 独立任务

T09(GB30981.2) ──→ P2 低优先级
T10(声功能区划) ──→ P2 低优先级
```

---

## 执行建议

1. **第一批（P0，必须）**：T01、T02、T03 —— 这3个任务直接关系到3条A级核心规则是否有标准原文支撑，也是论文中的证据链关键节点
2. **第二批（P1，重要）**：T04、T05、T06、T07、T08 —— 完善标准条款库和补齐依赖文件
3. **第三批（P2，补充）**：T09、T10、T11、T12 —— 锦上添花

**预期产出时间**：第一批3个任务预计各需Claude Code 15-30分钟（主要为文件搜索+解析+入库）。建议在下次Claude Code会话中优先完成T01-T03。

---

*本清单由 EIA Case-Standard Reviewer 生成，基于标准-经验校准过程中发现的文件缺口。*
