# 正式RAG与旧混合检索原型

旧原型`build_hybrid_index.py`、`hybrid_retrieve.py`和`eia_plastic_hybrid_index.yaml`原样保留，标记为`legacy_local_hybrid_retrieval_prototype`：SQLite＋FTS5、hash embedding、RRF，且旧配置同时包含标准库、QA、实验设计和Skill，因此不作为正式B/D组RAG。

正式RAG只接收白名单权威来源，标准卡仅用于路由，问题级上下文在模型调用前冻结，并验证B/D哈希一致。
