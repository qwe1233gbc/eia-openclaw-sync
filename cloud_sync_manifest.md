# Cloud Sync Manifest

> 生成时间: 2026-06-14 10:53:07
> 本地源: E:\\软件\\openclaw_workspace\\
> 同步目标: E:\\软件\\eia-openclaw-sync\\

## 文件清单

| # | 源路径 | 目标路径 | 大小 | 用途 | 敏感 | OpenClaw读取 |
|---|--------|----------|------|------|------|-------------|
| 1 | updated_standard_clause_library.jsonl | knowledge/standards/updated_standard_clause_library.jsonl | 7,357 | 标准条款库(含P0政策条款) | NO | YES |
| 2 | case_law_style_experience_library.jsonl | knowledge/experience/case_law_style_experience_library.jsonl | 268,699 | 176条类案经验JSONL | NO | YES |
| 3 | handoff/c2929_case_source_evidence_table.csv | handoff/c2929_case_source_evidence_table.csv | 28,391 | C2929证据溯源CSV | NO | YES |
| 4 | handoff/c2929_case_source_evidence_report.md | handoff/c2929_case_source_evidence_report.md | 851 | C2929溯源报告 | NO | YES |
| 5 | handoff/claude_code_to_openclaw_handoff_round2.md | handoff/claude_code_to_openclaw_handoff_round2.md | 2,525 | Round2交接报告 | NO | YES |
| 6 | handoff/p0_local_policy_acquisition_report.md | handoff/p0_local_policy_acquisition_report.md | 2,188 | P0政策获取报告 | NO | YES |
| 7 | handoff/p0_local_policy_acquisition_log.csv | handoff/p0_local_policy_acquisition_log.csv | 1,421 | P0获取日志 | NO | YES |
| 8 | handoff/missing_file_tasks.md | handoff/missing_file_tasks.md | 14,182 | 缺失文件任务清单 | NO | YES |
| 9 | openclaw_data_ready_report.md | reports/openclaw_data_ready_report.md | 2,929 | OpenClaw数据就绪综合报告 | NO | YES |
| 10 | experience_data_readiness_report.md | reports/experience_data_readiness_report.md | 654 | 经验数据就绪报告 | NO | YES |
| 11 | missing_file_report.md | reports/missing_file_report.md | 431 | 缺失文件报告 | NO | YES |
| 12 | duplicate_file_report.md | reports/duplicate_file_report.md | 20,389 | 重复文件报告 | NO | YES |
| 13 | file_manifest.jsonl | reports/file_manifest.jsonl | 299,629 | 全量文件清单 | NO | YES |
| 14 | data_inventory.csv | reports/data_inventory.csv | 1,142 | 分类统计 | NO | YES |

**总大小**: 650,788 bytes (0.6 MB)

## 安全声明

所有文件已经过过滤:
- 不含 docx/pdf/zip 原始文件
- 不含企业敏感信息
- 仅含结构化数据(JSONL/CSV)和报告(Markdown)

## 建议 OpenClaw 读取顺序

1. **首先**: `reports/openclaw_data_ready_report.md` — 了解全局数据状态
2. **其次**: `knowledge/standards/updated_standard_clause_library.jsonl` — 加载标准库
3. **核心**: `knowledge/experience/case_law_style_experience_library.jsonl` — 176条经验规则
4. **溯源**: `handoff/c2929_case_source_evidence_table.csv` — C2929证据
5. **任务**: `prompts/openclaw_round3_prompt.md` — Round 3 工作指令
6. **交接**: `handoff/claude_code_to_openclaw_handoff_round2.md` — 上下文交接

## 当前任务目标

将 176 条经验规则收敛为 **8-12 条 C2929 类案经验摘要卡**，格式为:
- AI可直接调用
- 有证据溯源
- 有适用边界
- 可嵌入审核工作流
