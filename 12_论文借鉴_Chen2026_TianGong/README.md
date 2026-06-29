# Chen 2026 / TianGong 可借鉴模块整理

本目录整理 Chen 等（2026）《Leveraging LLMs for Environmental Complexity: Structured Fine-Tuning Data Sets and Deployment Strategies》及其公开项目中可复用的研究思路，并给出适配本仓库“环评审核技能库”课题的轻量实现模板。

## 论文核心启发

Chen 等（2026）对本课题最有价值的启发，不是训练模型本身，而是环境领域知识如何被结构化、检索化并嵌入工作流：

1. 稳定、标准化、法规/验证类任务：适合沉淀为结构化知识、规则和可复用审核 skill。
2. 动态、跨学科、需要工具和计算的任务：适合用通用模型 + agentic workflow + 检索/计算工具。
3. 数据集构建阶段：用教材/标准库等权威材料，经混合检索、去重、结构化问答生成、人工复核，形成可评测、可复核的数据。

对应到本课题，塑胶行业环评审核采用“法规/标准依据库 + 审核技能库 + 检索增强 + 人工复核”的路线。Chen 论文中的结构化数据构建部分仅作为方法背景，本仓库以技能库和工作流复用为目标。

## 开源项目与数据

- 论文补充材料：Figshare / ACS Supporting Information，说明实验设计、测试集、评分提示词和错误案例。
- 数据集：Hugging Face `chukeaa/TianGong_Env`，MIT License，约 19.7k 条中文环境问答数据，字段包括 `question`、`answer`、`chain_of_thought`。
- 非结构化处理项目：`linancn/TianGong-AI-Unstructure`，包含文档解析、切块、向量库/全文库入库等脚本思路。
- LangGraph 工作流项目：`linancn/tiangong-ai-langgraph-server`，包含教材检索、chunk 分发、结构化输出生成等 agentic workflow 代码。

## 本目录提供的可复用模块

- `paper_method_notes.md`：论文思路、可借鉴模块与本课题迁移方案。
- `open_source_project_map.md`：开源项目、许可证、可复用点和谨慎事项。
- `configs/eia_plastic_hybrid_index.yaml`：本课题知识库构建配置模板。
- `schemas/corpus_chunk.schema.json`：切块后的知识片段 schema。
- `schemas/generated_qa.schema.json`：生成问答/审核任务的结构化 schema。
- `scripts/build_hybrid_index.py`：本地 SQLite FTS5 + 向量表的混合索引构建脚本。
- `scripts/hybrid_retrieve.py`：向量检索 + 全文检索 + RRF 合并的检索脚本。
- `prompts/eia_audit_data_synthesis_prompt.md`：把检索片段转成审核问答/审核任务的提示词模板。
- `examples/seed_queries_eia_plastic.txt`：可作为“种子问题”的环评审核题。

## 推荐使用方式

先构建本地混合索引：

```bash
python 12_论文借鉴_Chen2026_TianGong/scripts/build_hybrid_index.py ^
  --config 12_论文借鉴_Chen2026_TianGong/configs/eia_plastic_hybrid_index.yaml
```

再进行检索测试：

```bash
python 12_论文借鉴_Chen2026_TianGong/scripts/hybrid_retrieve.py ^
  --index outputs/chen2026_hybrid_index/eia_plastic_hybrid.sqlite ^
  --query "报告中活性炭更换周期缺失时应如何审核？" ^
  --top-k 8
```

默认使用 `hash` 向量模式，便于无 API key 时本地复现流程。若后续需要贴近论文，可切换到 OpenAI embedding 或 Pinecone/OpenSearch。
