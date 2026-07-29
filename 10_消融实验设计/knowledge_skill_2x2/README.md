# 地方知识 × Workflow/Skill 2×2评价工具链

本目录实现210题预注册分类、A/B/C/D统一答案Schema、输出盲化、GPT结构化评分、
评审可靠性和K×S归因分析。不会修改原始问答工作簿，也不会在缺少真实输出/API时
生成虚构结果。

## 复现分类

在本目录运行：

```powershell
node scripts/extract_source_workbook.mjs
python scripts/audit_taxonomy_readiness.py
python scripts/classify_questions_from_templates.py
python scripts/freeze_taxonomy.py
python scripts/select_pilot_questions.py
python scripts/export_taxonomy_review_workbook.py
python scripts/generate_readiness_reports.py
pytest -q
```

工作簿脚本依赖Codex提供的 `@oai/artifact-tool`。本地复现时将依赖目录连接为本目录
的 `node_modules`，不要提交该连接。

## 实验顺序

1. 人工确认待复核金标及逐题分类覆盖。
2. 四组按同一 `audit_output_v1.schema.json` 生成真实答案。
3. 统一Schema验证与相同语法修复。
4. `blind_outputs.py` 生成盲化输出和私有映射。
5. `build_gpt_scoring_packets.py` 组装评分包。
6. 冻结评价模型、提示词哈希、Schema哈希和日期后运行评分。
7. 验证总分、计算可靠性、分层统计及K/S/交互趋势。

`private/blinding_key.json`、运行输出和API密钥不得提交。
