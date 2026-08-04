# 正式RAG校验脚本

- `validate_formal_rag_sources.py`：来源白名单、路径、版本、重复内容和派生来源检查。
- `validate_rag_skill_isolation.py`：只扫描RAG正文，不扫描合法的路由元数据。
- `validate_snapshot_hashes.py`：验证A/B/C/D报告哈希、B/D RAG哈希和C/D Skill哈希。

任一脚本发现实质错误时返回非零退出码。
