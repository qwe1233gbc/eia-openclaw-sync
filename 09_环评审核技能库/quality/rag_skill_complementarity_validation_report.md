# RAG—Skill去重互补重构验证报告

验证日期：2026-08-04
基线：`origin/main@0155d3690f93f3906bb83a73eed7464062fd2f1f`

## 重构结果

- 已审计并重构01—15共15个单题Skill；`99_总审核汇总`仅做汇总边界扫描，不参与单题生成。
- 预重构重叠审计共32条：高风险0条、中风险1条、低风险31条。
- 中风险项是Skill 01固定写入具体标准版本，已改为运行时RAG查询和适用性核验。
- 15/15 Skill声明统一`rag_evidence`输入、`basis_status`输出、无RAG安全降级和人工复核条件。
- Skill正文中的固定法规限值、项目题号和人工金标命中均为0。
- RAG字段白名单只允许路由元数据参与查询；程序字段和整张标准卡不得注入B组正文。
- 旧版快照未覆盖；PR #17合并前修复使用`v2.1_pr17_acceptance`更新v2快照、哈希、路由和运行矩阵。

## PR #17合并前修复

- 15个Skill均改为任务特异性`required_applicability_dimensions`，映射、注册表、查询模板、`rag_evidence.applicability`输入契约和Skill第9节保持一致。
- 环保投资及源强内部算术复核可使用`basis_status=not_required`，不会因缺少无关的污染介质或排放形式而错误降级。
- GB 18918-2002修改单的错误来源别名已清除，统一使用清单中的`WATER_GB18918_MOD2025`。
- `WATER_GBT18920_2020_METADATA`已从正式候选来源移入`metadata_only_source_ids`，只允许提示正文缺口，不得进入`rag_evidence`或支撑匹配/不匹配。
- `PL004_Emission_水污`和`PL005_Emission_水污`的8个A/B/C/D运行均显式记录`basis_status=insufficient`、`conclusion=无法判断`、`manual_review_needed=true`。

## 自动验证

- RAG—Skill重叠扫描：通过，Skill命中0、RAG命中0。
- Skill运行时依赖检查：通过，15个Skill、错误0。
- RAG/Skill隔离检查：通过，错误0。
- v2快照与运行矩阵：通过，15个Skill文件哈希一致；21/21题B/D RAG哈希相同；21/21题C/D Skill哈希相同。
- A/B/C/D输入组合：通过，D只包含B的RAG输入与C的Skill输入。
- 单元测试：13个测试文件、15个测试方法全部通过。
- YAML：映射、注册表、RAG字段白名单和黑名单共4个文件全部可解析。
- 正式RAG来源清单：26项，错误0、警告0。
- mapping—manifest引用完整性：15个Skill、44个正式候选引用、1个metadata-only引用；错误0，4条历史来源时点过滤提醒。
- metadata-only来源隔离：两套冻结快照共42个RAG上下文正文注入0；不合格正式候选0；PL004/PL005安全降级8/8。

## 逐Skill适用性与人工专业复核

- 01—15映射均使用各自任务所需字段，不再共用地区、行业、工艺、污染介质、排放形式和有效时点六维模板。
- Skill 05—15已逐项人工复核，多介质路由、计算边界、版本时点、无RAG降级及`risk_hints`边界均通过。
- Skill 09补齐多级治理、回流循环、重复削减及质量—体积—时间口径；Skill 11补齐罩型、面积、控制风速、换气次数、并发、漏风和余量；Skill 14补齐历史版本和不得凭名称认定要求。

## 当前实验结论

本轮“RAG知识层—Skill程序层互补性重构”已通过，可继续用于补齐材料和执行未阻断的最小趋势管线。完整正式混合标签ABCD实验仍不可启动：`PL004_Emission_水污`与`PL005_Emission_水污`缺少可离线核验的GB/T 18920-2020正式全文，Dense Embedding与神经重排序器尚未配置，混合标签正式实验集也尚未冻结。

## 人工复核

自动高风险阻断项为0。`manual_review_queue.md`已更新为Skill 05—15合并前人工专业复核记录；复核已完成，历史来源仍须在每次运行时按报告日期过滤。
