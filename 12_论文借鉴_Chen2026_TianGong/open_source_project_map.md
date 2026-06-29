# Chen 2026 相关开源项目与复用清单

## 1. 论文补充材料

- 位置：https://acs.figshare.com/collections/Leveraging_LLMs_for_Environmental_Complexity_Structured_Fine-Tuning_Data_Sets_and_Deployment_Strategies/8226396
- 许可证：Figshare 页面标注 CC BY-NC 4.0。
- 内容：Supporting Information，包括教材覆盖、训练数据验证、测试数据、评价提示词、统计检验、模型响应对比、错误案例等。

本课题可借鉴：

- 专家参与的数据验证流程：每条生成记录绑定问题、答案、推理痕迹和检索片段；
- 失败样本剔除规则：空泛来源、来源-问题不匹配、无依据数值或概念；
- 328 题测试集的四维分类：认知层级、环境领域、推理类型、功能能力；
- 10-100 分评分量规：事实正确性、逻辑推理、计算过程、完整性；
- 统计验证路线：正态性检验、Bootstrap CI、配对检验、Wilcoxon、FDR、效应量；
- 错误案例分析：幻觉、事实漂移、上下文误读、推理链错误、数值传播错误；
- 多评审者一致性提醒：Fleiss' kappa 结果显示评分口径需要校准。

注意：

- 不直接复制长篇 SI 内容；
- 不把 SI 中模型性能结论直接外推到本课题；
- 不把 AI 评价替代专家复核。

## 2. TianGong_Env 数据集

- 位置：https://huggingface.co/datasets/chukeaa/TianGong_Env
- 许可证：MIT。
- 规模：Hugging Face 页面显示约 19.7k 行，包含 train/test split。
- 字段：`question`、`answer`、`chain_of_thought`。

本课题可借鉴：

- 中文环境问答数据结构；
- 问题、答案、推理痕迹分字段保存；
- 训练/测试拆分意识；
- 生成数据需要人工验证的处理方式。

谨慎事项：

- 该数据集是通用环境教材问答，不是环评审核金标；
- 本课题不直接复用其问答内容；
- 可参考其 schema 和数据组织方式。

## 3. TianGong-AI-Unstructure

- 位置：https://github.com/linancn/TianGong-AI-Unstructure
- 许可证：MIT。
- 论文对应作用：文档解析、切块、embedding、Pinecone/OpenSearch 入库。

本课题可借鉴：

- 文档解析后统一转为 chunk / pickle / 结构化记录；
- 一份文本同时进入向量库和全文库；
- 标准、报告、ESG、教材等不同来源分别建索引；
- 保留来源路径、页码、章节和 metadata。

本目录迁移实现：

- `scripts/build_hybrid_index.py`
- `schemas/corpus_chunk.schema.json`
- `configs/eia_plastic_hybrid_index.yaml`

## 4. tiangong-ai-langgraph-server

- 位置：https://github.com/linancn/tiangong-ai-langgraph-server
- 许可证：MIT。
- 论文对应作用：LangGraph agentic workflow，使用种子问题检索教材片段，再用结构化输出生成问答和评价结果。

本课题可借鉴：

- `searchTextbooks`：先按问题召回 topK 片段并扩展上下文；
- `routeChunks`：把多个 chunk 并行分发给分析节点；
- `analyzeChunk`：用结构化 schema 生成 question / response / reasoning；
- evaluation workflow：用统一评分提示词评估输出质量；
- temperature=0：降低数据合成阶段随机性。

本目录迁移实现：

- `scripts/hybrid_retrieve.py`
- `prompts/eia_audit_data_synthesis_prompt.md`
- `prompts/eia_audit_evaluation_prompt_from_si.md`
- `schemas/generated_qa.schema.json`
- `schemas/evaluation_record.schema.json`

## 5. 本课题复用边界

建议复用“流程和接口”，不直接依赖其云服务栈：

- Pinecone -> 先用本地 SQLite 向量表，后续可替换为 FAISS / Chroma / Pinecone；
- OpenSearch -> 先用 SQLite FTS5，后续可替换；
- LangGraph -> 先用 Dify 或 Python 脚本串联，后续可服务化；
- 教材 QA -> 改为环评审核 QA，包括标准依据、报告证据、类案经验和人工复核。

## 6. 对论文写作的类比关系

| Chen 2026 | 本课题 |
| --- | --- |
| 环境教材语料 | 佛山塑胶指南、法规标准、Dify 知识库、样本链、修改意见 |
| 教材 chunk | 标准条目、报告片段、修改意见片段、技能库步骤 |
| 种子问题 | 审核任务问题 |
| 生成问答 | 候选审核问答和修改意见 |
| 专家验证 | 人工复核与专家校准 |
| 测试集四维分类 | 审核任务四维分类 |
| 模型/agent 对比 | A/B/C/D 知识条件对照 |
| 统计验证 | 小样本人工评分 + 置信区间 + 成对检验 + 错误分析 |
