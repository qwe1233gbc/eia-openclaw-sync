# Dify 知识库解析版标准库

生成日期：2026-06-29

这个包把仓库中的 `03_指南解析_明文标准库/Dify工作流知识库` 解析成技能库可调用的结构化标准卡。核心产物是：

- `standard_cards.jsonl`：主标准库，适合 RAG / 向量库 / 脚本读取。
- `standard_cards.json`：同内容 JSON 数组，方便调试。
- `skills_to_standard_mapping.yaml`：每个审核 skill 应调用哪些标准卡。
- `cards_by_skill/`：按技能拆分后的标准卡。
- `DIFY_KB_SOURCE_MANIFEST.csv`：Dify 知识库源文件到 skill 的使用关系。
- `quality/QUALITY_CHECK.md`：解析时发现的风险和需要人工确认的点。

## 调用逻辑

报告证据片段 → skill_id → `skills_to_standard_mapping.yaml` 找标准卡 → 用 `retrieval_tags/trigger_keywords` 召回 → 按 `normative_requirements + thresholds + formulas + check_logic` 输出审核结论。

## 标准卡字段

`standard_id` 是唯一编号；`skill_ids` 是可调用该卡的技能；`source_files` 是 Dify 知识库源文件；`evidence_fields` 是技能需要从报告中提取的证据；`thresholds/formulas` 是可计算规则；`manual_review` 是触发人工复核的边界条件。

## 已覆盖技能

01 国民经济行业类别、02 环保投资、03 三线一单、04 建设内容、05 环境质量现状数据、06 环境质量执行标准、07 污染物排放标准、08 产污系数合理性、09 产污系数定量核算、10 废气收集形式及排气量、11 废气收集风量与设计风量、12 废气收集效率、13 活性炭参数、14 危险废物识别、15 VOCs总量控制。

## 上传建议

把本目录放到：

`03_指南解析_明文标准库/`

然后在 `09_环评审核技能库` 的每个 `config.yaml` 中增加标准库引用。
