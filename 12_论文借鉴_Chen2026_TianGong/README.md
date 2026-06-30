# Chen 2026 / TianGong 可借鉴模块整理（不微调版）

本目录整理 Chen 等（2026）《Leveraging LLMs for Environmental Complexity: Structured Fine-Tuning Datasets and Deployment Strategies》及其开源项目中可复用的研究思路，并给出适配本仓库“塑胶行业环评审核技能库”课题的轻量化实现模板。

本课题当前明确不走模型微调路线。这里借鉴的核心不是 fine-tuning 本身，而是：如何组织权威材料、如何构建可追溯的候选问答、如何进行专家复核、如何评价不同知识条件下的审核输出。

一句话定位：

> 本目录用于把 Chen 2026 的“结构化知识构建、混合检索、工作流部署、专家验证和分层评价”迁移到塑胶行业环评审核场景；不把 TianGong 数据集作为本课题训练集，不把微调作为当前研究主线。

## 1. 论文核心启发

Chen 等（2026）对本课题最有价值的启发包括：

1. 稳定、标准化、法规/验证类任务适合沉淀为结构化知识、规则和可复用工作流。
2. 动态、跨材料、需要计算或工具辅助的任务更适合采用通用模型 + 检索增强 + 工具 + 人工复核。
3. 数据集构建不应停留在“生成问答”，而应包含证据绑定、专家验证、剔除记录和错误分析。
4. 有效性评价不应只看主观印象，应设计题型分类、评分量规、统计验证和典型错误案例。

对应到本课题，推荐路线是：

`标准依据库 + 审核技能库 + 检索增强 + 样本链证据 + 人工复核 + 知识条件对照实验`

当前项目数据能否对应 Chen 2026，建议先读：

- `data_correspondence_no_finetune.md`：逐项说明本项目标准库、样本链、QA、技能库和实验设计如何对应 Chen 2026，以及哪些部分不能对应。

## 2. SI 补充材料细化

已结合 Chen 等（2026）Supporting Information 进一步补充以下材料：

- `SI_详细方法映射.md`：整理 SI 中教材覆盖、训练数据验证、测试集分类、评分提示词、统计验证、错误案例和 Fleiss' kappa 的可迁移方法。
- `SI_评价验证框架_环评审核迁移.md`：将 SI 的评价设计转化为本课题可用的审核任务分类、人工复核、拒收规则、评分量规和 A/B/C/D 知识条件对照方案。
- `prompts/eia_audit_evaluation_prompt_from_si.md`：基于 SI 评分提示词改写的环评审核输出评分模板。
- `schemas/evaluation_record.schema.json`：用于记录人工评分、错误标签、知识条件组别和复核结论的结构化 schema。

SI 中最值得迁移的细节包括：

- 训练数据生成后需要专家复核，SI 中 19,739 条生成记录经验证后保留 19,532 条、剔除 207 条；
- 被剔除数据主要包括空泛来源、来源-问题不匹配、无依据数值或概念；
- 测试集按认知层级、环境领域、推理类型、功能能力四维分类；
- 评分采用 10-100 分分档，并关注事实正确性、逻辑推理、计算过程和完整性；
- 统计验证包括正态性检验、Bootstrap 置信区间、配对检验、Wilcoxon、FDR 校正和效应量；
- 错误案例区分幻觉/事实漂移、上下文误读、推理链错误和数值传播错误；
- Fleiss' kappa 结果提示多评审者一致性需要先校准。

## 3. 开源项目与数据

- 论文补充材料：Figshare / ACS Supporting Information，说明实验设计、测试集、评分提示词、统计验证和错误案例。
- 数据集：Hugging Face `chukeaa/TianGong_Env`，MIT License，约 19.7k 条中文环境问答数据，字段包括 `question`、`answer`、`chain_of_thought`。
- 非结构化处理项目：`linancn/TianGong-AI-Unstructure`，包含文档解析、切块、向量库/全文库入库等脚本思路。
- LangGraph 工作流项目：`linancn/tiangong-ai-langgraph-server`，包含教材检索、chunk 分发、结构化输出生成和评价工作流代码。

使用边界：

- 可复用流程、接口、schema 和评价思路；
- 不直接复制外部长篇材料；
- 不把 TianGong 的通用环境 QA 当作本课题金标；
- 不把论文中的模型性能结论直接迁移到环评审核场景。

## 4. 本目录提供的可复用模块

- `paper_method_notes.md`：论文思路、可借鉴模块与本课题迁移方案。
- `data_correspondence_no_finetune.md`：本项目数据与 Chen 2026 方法的对应关系，强调不微调路线。
- `technical_route_comparison_chen2026_eia.md`：Chen 2026 技术路线与本课题现有数据、技术路线、缺口和后续任务的完整对照。
- `open_source_project_map.md`：开源项目、许可证、可复用点和谨慎事项。
- `SI_详细方法映射.md`：Supporting Information 的详细方法抽取。
- `SI_评价验证框架_环评审核迁移.md`：面向本课题的评价与验证框架。
- `configs/eia_plastic_hybrid_index.yaml`：本课题知识库构建配置模板。
- `schemas/corpus_chunk.schema.json`：切块后的知识片段 schema。
- `schemas/generated_qa.schema.json`：生成问答/审核任务的结构化 schema。
- `schemas/evaluation_record.schema.json`：人工评分和错误分析 schema。
- `scripts/build_hybrid_index.py`：本地 SQLite FTS5 + 向量表的混合索引构建脚本。
- `scripts/hybrid_retrieve.py`：向量检索 + 全文检索 + RRF 合并的检索脚本。
- `prompts/eia_audit_data_synthesis_prompt.md`：把检索片段转成审核问答/审核任务的提示词模板。
- `prompts/eia_audit_evaluation_prompt_from_si.md`：把候选答案转成评分记录的评价提示词模板。
- `examples/seed_queries_eia_plastic.txt`：可作为种子问题的环评审核题。

## 5. 推荐使用方式

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

后续评价候选输出时，可使用：

```text
12_论文借鉴_Chen2026_TianGong/prompts/eia_audit_evaluation_prompt_from_si.md
```

默认使用 `hash` 向量模式，便于无 API key 时本地复现流程。后续如需服务化，可替换为 OpenAI embedding、FAISS、Chroma、Pinecone 或 OpenSearch。
