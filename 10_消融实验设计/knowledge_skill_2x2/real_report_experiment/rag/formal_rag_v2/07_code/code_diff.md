# 代码变更说明

## v2 (2026-08-09): DashScope 混合 RAG

- 新增 `dashscope_rag.py`：DashScope text-embedding-v3 + qwen3-rerank 集成模块
- 更新 `build_or_update_formal_rag.py`：三阶段混合检索（BM25+Dense→RRF→Neural Rerank）
- 新增 `doc_embeddings_cache.json`：预计算向量缓存
- 冻结快照新增字段：`rrf_k`, `hybrid_trace`, `embedding_model`, `reranker_model`
- 更新 `retrieval_mode`: `hybrid_bm25_dense_rrf_neural_rerank`
- 更新 `formal_hybrid_rag`: `True`
- 更新 `requirements.txt`：新增 `dashscope>=1.20.0`

### 三阶段检索策略

| 阶段 | 模块 | 说明 |
|------|------|------|
| Stage 1a | BM25 | 词汇检索，召回 top-40 |
| Stage 1b | text-embedding-v3 | 稠密检索，召回 top-40 |
| Stage 1c | RRF (k=60) | 融合 BM25 + Dense 结果 |
| Stage 2 | qwen3-rerank | 神经重排序，输出 top-8 |
| Stage 3 | required_source_ids | 保底机制，确保关键法规不被淘汰 |

### API Key 配置

通过环境变量 `DASHSCOPE_API_KEY` 传入。脚本内置默认开发密钥作为回退。

## v1 (2026-08-04): BM25 临时验证

- BM25 + fixed_source_priority 临时验证模式（已被 v2 替代）
