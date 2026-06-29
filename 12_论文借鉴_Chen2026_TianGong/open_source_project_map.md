# Chen 2026 相关开源项目与复用清单

## 1. 论文补充材料

- 位置：https://acs.figshare.com/collections/Leveraging_LLMs_for_Environmental_Complexity_Structured_Fine-Tuning_Data_Sets_and_Deployment_Strategies/8226396
- 许可证：Figshare 页面标注 CC BY-NC 4.0。
- 内容：Supporting Information，包括教材覆盖、训练数据验证、测试数据、评价提示词、统计检验、模型响应对比、错误案例等。
- 本课题可借鉴：评价提示词、错误案例分析、人工/AI 混合评分流程。
- 注意：非商业许可；不直接复制长篇补充材料到本仓库。

## 2. TianGong_Env 数据集

- 位置：https://huggingface.co/datasets/chukeaa/TianGong_Env
- 许可证：MIT。
- 规模：Hugging Face 页面显示约 19.7k 行，含 train/test 两个 split。
- 字段：`question`、`answer`、`chain_of_thought`。
- 本课题可借鉴：中文环境问答数据结构、种子问题设计、问答字段组织。
- 注意：本课题不应把其通用环境问答直接作为环评审核金标；可作为写作参考和 schema 参考。

## 3. TianGong-AI-Unstructure

- 位置：https://github.com/linancn/TianGong-AI-Unstructure
- 许可证：MIT。
- 论文对应作用：文档解析、切块、embedding、Pinecone/OpenSearch 入库。
- 本课题可借鉴：
  - 文档解析后统一转为 chunk/pickle/结构化记录。
  - 一份文本同时进入向量库和全文库。
  - 标准、报告、ESG、教材等不同来源分别建索引。
- 本目录迁移实现：
  - `scripts/build_hybrid_index.py`
  - `schemas/corpus_chunk.schema.json`

## 4. tiangong-ai-langgraph-server

- 位置：https://github.com/linancn/tiangong-ai-langgraph-server
- 许可证：MIT。
- 论文对应作用：LangGraph agentic workflow，使用种子问题检索教材片段，再用结构化输出生成问答。
- 关键源码：`src/data_synthesize_agent.ts`。
- 本课题可借鉴：
  - `searchTextbooks`：先按问题召回 topK 片段并扩展上下文。
  - `routeChunks`：把多个 chunk 并行分发给分析节点。
  - `analyzeChunk`：用结构化 schema 生成 question/response/reasoning。
  - temperature=0：降低数据合成阶段随机性。
- 本目录迁移实现：
  - `scripts/hybrid_retrieve.py`
  - `prompts/eia_audit_data_synthesis_prompt.md`
  - `schemas/generated_qa.schema.json`

## 5. 本课题复用边界

建议复用“流程和接口”，不直接依赖其云服务栈：

- Pinecone -> 先用本地 SQLite 向量表，后续可替换。
- OpenSearch -> 先用 SQLite FTS5，后续可替换。
- LangGraph -> 先用 Dify 或 Python 脚本串联，后续可服务化。
- 教材 QA -> 改为环评审核 QA，包括标准依据、报告证据、类案经验和人工复核。
