# Zhou 2026 RAG方法映射

## 可借鉴

权威来源过滤、法规版本优先级、父子块、BM25＋Dense Embedding＋Reranker、检索条款显式进入Prompt、检索Embedding与评价Embedding分离、专家盲评。

## 不照搬

LoRA微调、3954条训练QA、五折交叉验证、固定4000/500 token参数、Dify唯一实现、以ROUGE/BLEU作为主指标。

## 本研究扩展

地方适用性过滤、行业和工艺适用性、污染介质和排放去向、RAG与Skill严格隔离、报告证据与外部依据双证据链、问题级离线冻结、B/D哈希一致。
