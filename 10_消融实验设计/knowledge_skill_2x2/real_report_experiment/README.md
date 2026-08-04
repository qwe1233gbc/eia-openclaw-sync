# 基于真实环评报告的知识 RAG × Workflow/Skill 四组实验

本目录实现 A（LLM）、B（RAG）、C（程序型 Workflow）和 D（RAG+Workflow）
的统一实验框架。正式运行只接受人工冻结金标；候选题仅可用于
`not_for_analysis=true` 的框架 dry-run。

## 快速检查

```powershell
$env:EIA_REPORT_ROOT="<仓库外真实报告解析目录>"
python scripts/build_report_manifest.py
python scripts/parse_reports.py
python scripts/build_report_contexts.py
python scripts/build_rag_corpus.py
python scripts/freeze_rag_contexts.py
python scripts/sanitize_skills.py
python scripts/build_run_matrix.py --stage dry_run
python scripts/run_experiment.py --group A --backend mock
python scripts/validate_group_isolation.py
pytest -q
```

`mock` 后端只验证数据流、隔离和 JSON Schema，不产生可用于论文分析的模型结果。
正式模型适配器需由用户配置后才能运行；框架不会自动调用收费 API。

报告全文解析、冻结报告片段、RAG语料快照和逐次运行包均在本地生成并被
`.gitignore` 排除；仓库只提交相对标识、哈希、清单、代码和汇总，避免把
仓库外的完整环评报告带入 Git。
