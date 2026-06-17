# OpenClaw 文献证据包复核报告

## 1. 复核基本信息

- **复核日期**：2026-06-17
- **GitHub commit hash**：e779cf8cc50662cadfc91143b7d832ea3b605dda（Add consolidated literature evidence pack on 2026-06-17）
- **复核执行环境**：OpenClaw 云端 Agent
- **实际读取文件**：

| 文件路径 | 格式 | 是否成功读取 |
|---|---|---|
| `outputs/literature_evidence_20260617/literature_support_pack_20260617.md` | Markdown | ✅ 读取 |
| `outputs/literature_evidence_20260617/literature_matrix_20260617.xlsx` | Excel 二进制 | ⚠️ 存在但无法直接读取内容，依赖 MD 版 `literature_matrix.md` 交叉验证 |
| `outputs/literature_evidence_20260617/references_20260617.bib` | BibTeX | ✅ 读取（18 条） |
| `outputs/codex_literature_2026_06_16/README_literature_evidence_20260617.md` | Markdown | ✅ 读取 |
| `outputs/codex_literature_2026_06_16/literature_evidence_quality_check_20260617.md` | Markdown | ✅ 读取 |
| `outputs/codex_literature_2026_06_16/related_work_high_level_draft.md` | Markdown | ✅ 读取 |
| `outputs/codex_literature_2026_06_16/literature_matrix.md` | Markdown | ✅ 读取 |
| `outputs/codex_literature_2026_06_16/paper_story_cards.md` | Markdown | ✅ 读取 |
| `outputs/codex_literature_2026_06_16/research_gap_storyline.md` | Markdown | ✅ 读取 |

> 注：`literature_matrix_20260617.xlsx` 为二进制 Excel 文件，OpenClaw 无直接读取 Excel 单元格的工具。本复核依赖同目录下的 `literature_matrix.md`（Codex 输出）和 `literature_support_pack_20260617.md`（Claude Code 整理版）交叉验证文献矩阵内容。

---

## 2. 总体判断

**文献证据包总体可用，可以支撑中期汇报和论文方法章节的初稿撰写，但需注意以下前提：**

1. **证据层次清晰**：文献被分为 7 个主张，每个主张有 1-4 篇核心文献支撑，且每篇都有"可用于论文的表述"段落，可直接引用入稿。
2. **表述克制**：全包大量出现"不能替代""不应视为""仍需""有限"等审慎措辞，经验库与标准库的边界清晰。
3. **bib 覆盖率有缺口**：`references_20260617.bib` 含 18 条文献，但 `related_work_high_level_draft.md` 中引用的 Cilliers 2025、Gimenez 2025、Schneider 2022、Allard 2026、Du 2026 等未纳入 bib，需补齐。
4. **文献验证未完成**：Chen 2026 标注"Full text to be checked"，多数文献未经过原文逐条核验。
5. **中文文献不足**：现有文献以英文为主，中国环评报告表质量审查和技术评估的中文文献极少，后续需补充。

**建议使用方式**：
- 中期汇报：可直接使用，但标注"文献尚在补充和核验中"；
- 论文方法章节：可用于撰写初稿，但需完成文献逐条核验、补齐 bib、补充中文文献后再定稿。

---

## 3. 对论文主张的支撑情况

### 主张 1：环评审核需要关注报告质量和证据充分性

**判断：支撑充分**

| 文献 | 贡献 |
|---|---|
| Lee1999ReviewingQuality | EIA 报告质量审查框架，覆盖基线、影响预测、替代方案、缓解措施、监测 |
| Bond2025ArtificialIntelligence | AI 应服务于具体评价任务、证据质量和治理边界 |

两条文献分别从传统 EIA 质量审查（Lee 1999，经典文献）和 AI 进入影响评价的当代边界（Bond 2025）两个角度支撑，形成时间纵深。表述将质量审查框架转化为"审核问题拆分为可复核的工作流模块"的逻辑清晰。

> 建议补充：中文环评报告表技术评估和质量审查文献（如《建设项目环境影响报告表编制技术指南》）以增强中国语境的支撑力度。

---

### 主张 2：普通问答不能代表环评审核能力

**判断：支撑充分**

| 文献 | 贡献 |
|---|---|
| Meyur2025BenchmarkingLLMs | NEPAQuAD benchmark + MAPLE 评估管线，环境审查需要专门题型、证据上下文 |
| Guo2025ELLE | 环境领域专门 QA benchmark，按领域/难度/题型组织 |
| Kornov2025LayingFoundation | 生成式 AI 需要先建立可复用的结构化数据基础 |

三条文献分别从 benchmark 构建（Meyur）、领域数据集（Guo）和数据基础（Kornov）三个角度支撑"专门 evaluation 而非泛化问答"的主张。表述中将审核任务拆为"法规标准—报告证据—工程分析逻辑—结论可追溯性"四要素，与文献论点一致。

---

### 主张 3：环境审查类任务需要专门 benchmark

**判断：基本支撑**

（与主张 2 共享核心文献）

此主张与主张 2 高度重叠。Meyur 2025 和 Guo 2025 直接支撑"环境领域需要专门 benchmark"，但当前证据包未将这一主张作为单独条目展开。`research_gap_storyline.md` 中 Gap 1 有较清晰的论述："From EIA document QA to audit-oriented review"。

> 建议：如果论文需要将此作为独立主张，可从 Meyur 2025 的 MAPLE pipeline 和 Guo 2025 的 ELLE dataset 中提取更具体的支持论据。

---

### 主张 4：标准库/RAG 适合支撑法规、标准、导则等强依据任务

**判断：支撑充分**

| 文献 | 贡献 |
|---|---|
| Garrido2011OntologyEIA | EIA 本体构建，结构化知识组织 |
| Hogan2022KnowledgeGraphs | 知识图谱表示、查询、验证和推理框架 |
| Garigliotti2024SDGRAG | RAG 在环境报告目标识别中的实证价值 |
| Bommarito2018LexNLP | 法律/监管文本需要结构化抽取 |

四条文献形成"EIA 知识组织→通用 KG→RAG 实证→监管 NLP"的完整支撑链。表述中提出"标准卡"（standard card）作为中间表示，比完整知识图谱更实用，也未过度拔高。

> 注意：Garigliotti 2024 研究的是 SDG 目标检测而非 VOCs 合规审核，应在引用时注明场景差异。

---

### 主张 5：经验库可以由案例推理、类案经验和专家经验复用理论支撑

**判断：基本支撑**

| 文献 | 贡献 |
|---|---|
| Aamodt1994CaseBased | CBR 经典流程：检索、复用、修正、保留 |
| Watson1994CaseBasedReview | 历史案例在新旧问题相似但不完全相同时的参考价值 |
| Thai2022CBRiKB | CBR 辅助不完整知识库问答推理 |
| Zhao2023ExpeL | LLM agent 从历史任务轨迹抽取可复用经验 |

四条文献从经典 CBR 到 LLM agent 经验学习形成理论链，支撑"经验可结构化复用"。但注意：

- 经典 CBR 文献（1994 年）距当前 LLM 时代较远，需要在论文中说明"借鉴 CBR 思想而非直接实现 CBR 系统"；
- Zhao 2023 ExpeL 是 agent 自生成经验，而本研究经验来自真实批注，差异需明确说明；
- 缺少"行政审核场景下历史意见复用"的直接文献。

> 建议：在论文中增加一段，说明"本文不实现 CBR 的完整四步循环，而是借鉴其知识组织思想，将审核经验封装为可检索、可触发的经验卡"。

---

### 主张 6：AI 生成的候选问答需要专家验证

**判断：支撑充分**

| 文献 | 贡献 |
|---|---|
| AlonBarkat2023HumanAI | 公共部门决策中 automation bias 和 selective adherence 风险 |
| Fragiadakis2025EvaluatingHAIC | 人机协同评价需要多维指标 |
| Magesh2025HallucinationFree | 高风险文本推理工具仍可能产生幻觉 |

三条文献从公共部门 AI 风险、评价框架和幻觉问题三个角度支撑"AI 生成内容需人工核验"主张。表述中将 seed QA 定位为"候选材料"而非"gold answer"，并规定需经环评工程师判断"保留/修改/降级/剔除"，表述恰当。

---

### 主张 7：评价体系需要关注可靠性和一致性

**判断：基本支撑**

| 文献 | 贡献 |
|---|---|
| Li2024LLMasJudges | LLM-as-judge 存在偏差、稳定性和可靠性问题 |
| Fragiadakis2025EvaluatingHAIC | 不应只看单一平均分 |
| Meyur2025BenchmarkingLLMs | 透明评估管线和多策略对比 |

文献支撑了"需要可靠性检验"的必要性论证，但尚未提供 Cohen's Kappa / Fleiss' Kappa / bootstrap CI 在 EIA 审核场景中的具体操作方案。`literature_support_pack_20260617.md` 中已标注"具体操作论文还可继续检索"，且 `research_gap_storyline.md` 明确说明 v0.6a 尚未完成独立双评，表述诚实。

> 建议：在论文方法章节中先定位为"评价设计中应包含可靠性检验"的必要性论证，而非已完成的操作方案。

---

### 主张 8：Chen 等环境 LLM 论文的方法范式可以迁移到本研究，但不能照搬微调路线

**判断：需人工核查**

| 文献 | 贡献 |
|---|---|
| Chen2026LeveragingLLMs | 结构化微调数据集和部署策略 |

**核心风险**：Chen 2026 在 bib 中标注"Full text to be checked"，全文内容尚未核验。基于单一未验证文献声称"方法范式可以迁移"存在以下隐患：
1. 无法确认 Chen 论文的实际方法范式与本研究路径的一致性；
2. 无法排除该文献本身存在本研究不应采用的方法假设；
3. 单篇支撑力度偏弱。

> 建议：在中期汇报中降级为"可借鉴环境 LLM 领域关于结构化数据—专门评价—部署边界的总体研究方向（如 Chen 2026 等），但具体范式迁移有待全文核验后确认"。

---

## 4. 经验库理论引入是否稳妥

### 4.1 风险表述扫描结果

对所有文件进行关键词扫描，结果如下：

| 风险表述 | 是否出现 | 说明 |
|---|---|---|
| 某国是案例法 | ❌ 未出现 | — |
| 某国只看案例 | ❌ 未出现 | — |
| 中国只看标准 | ❌ 未出现 | — |
| 历史修改意见等同于判例 | ❌ 未出现 | — |
| 环评审核可以照搬域外判例法 | ❌ 未出现 | — |
| 经验库可以替代标准库 | ❌ 未出现 | 多处明确反向表述 |
| 单个修改意见可以直接作为强规则 | ❌ 未出现 | 证据分级机制贯穿全文 |
| 具体国名展开法律制度比较 | ⚠️ 部分出现 | "南非""美国"仅用于标注研究地理来源（Cilliers 南非筛查案例、Meyur NEPA 场景），未做制度比较。`literature_evidence_quality_check_20260617.md` 已确认此项 PASS |

### 4.2 审慎表述密度统计

全包中出现的关键审慎措辞：

| 措辞 | 出现位置 |
|---|---|
| "经验库不能替代标准库" | `literature_support_pack_20260617.md` §2 主张 4；`related_work_high_level_draft.md` §2.3 |
| "不把历史审核意见视为正式规则" | `literature_support_pack_20260617.md` §2 主张 4 |
| "经验库只用于辅助发现问题和提示核查方向" | 同上 |
| "借鉴……思想" / "不将……等同于" | `related_work_high_level_draft.md` §2.3 |
| "不能表述为系统已被统计证明有效" | `research_gap_storyline.md` §What v0.6a Can Support |
| "candidate/pending cards cannot support strong conclusions" | `research_gap_storyline.md` §Step 4 |
| "relevance 过滤"机制 | 多处 |

### 4.3 总体评估

**经验库理论引入稳妥。** 全包对经验库的定位一致且克制：定位为"类案经验参照"而非"强制规则"，强调证据分级（A/B/C）、relevance 过滤、禁止无条件注入。核心表述"借鉴'明文规则约束 + 类案经验参照'的知识组织思想"可以直接用于论文。

唯一需要关注的细微点是：CBR 经典文献（Aamodt 1994、Watson 1994）的理论框架与当前 LLM agent 经验学习的衔接需要清晰说明，避免被误解为"本研究实现了一个 CBR 系统"。

---

## 5. 主要问题

1. **Chen 2026 文献未验证**：bib 标注"Full text to be checked"，但证据包已将其置于核心论证位置（主张 7、research_gap_storyline 多处引用）。需优先完成全文核验，再决定引用强度。

2. **bib 覆盖不全**：`references_20260617.bib`（18 条）缺少 `related_work_high_level_draft.md` 中引用的 Cilliers 2025、Gimenez 2025、Schneider 2022、Allard 2026、Du 2026 等至少 5 条文献。建议将 bib 补齐至 23+ 条。

3. **主张 2 和主张 3 重叠**：证据包将"普通问答不能代表环评审核能力"和"环境审查类任务需要专门 benchmark"合并论述。如果论文需要两者独立支撑，建议拆分引用。

4. **中文文献严重不足**：18 条文献中无一条是中文环评报告表质量审查或技术评估文献。中国建设项目环评表审核制度特征的研究无法仅用英文文献支撑。

5. **CBR 文献年代跨度大**：Aamodt 1994 / Watson 1994 距今 32 年，与当前 LLM 研究范式有代差。建议补充近年 CBR+LLM 结合的研究（如 2022-2025 年文献），避免评审人质疑理论过时。

6. **Kappa/一致性检验文献仅为方向性提及**：Li 2024 和 Fragiadakis 2025 支撑了"需要可靠性检验"的论点，但未提供 EIA 审核 benchmark 中如何操作 Kappa / Fleiss' Kappa 的具体方案。`literature_support_pack_20260617.md` 虽已标注"可继续检索"，但中期汇报如提出此要求，需要至少 1-2 篇操作层面文献。

7. **xlsx 文件无法直接复核**：`literature_matrix_20260617.xlsx` 为二进制格式，OpenClaw 无法直接读取单元格内容。本复核依赖 `literature_matrix.md` 交叉验证。如果 xlsx 包含额外信息（如评分、状态标记），无法确认。

8. **文献观点与原文一致性未核验**：全包中文献的观点描述由 AI（Codex/Claude Code）生成，是否与原文一致尚未经人工逐条核验。需在论文定稿前完成此项工作。

---

## 6. 建议修改表述

以下为可直接替换到中期汇报或论文中的表述建议：

### 6.1 经验库定位（论文方法章节可用）

> 本文引入"类案经验库"并不将历史审核批注等同于正式规则或司法判例，而是借鉴案例推理（Case-Based Reasoning）中"相似案例可辅助新问题判断"的知识组织思想，将同类项目中反复出现的审核争点、证据缺口和经办人式追问结构化为可检索、可触发、可人工验证的经验知识单元。经验库仅用于辅助发现潜在问题和提示核查方向，不替代标准库中的明文依据，不构成独立于标准的判断规则。

### 6.2 标准库定位（论文方法章节可用）

> 标准库将分散在法规、导则、排放标准和地方管理文件中的条款、限值、公式和证据要求，转化为带有来源标识、适用模块、审核要点和证据指引的标准卡。与通用 RAG 文档片段不同，标准卡强调依据身份（标准号/条款位置/版本）和审核用途（该条款在审核中回答"报告应满足什么要求"），从而提升回答的可追溯性和可复核性。

### 6.3 环境 LLM 研究范式迁移（中期汇报可用，Chen 2026 核验后使用）

> 本研究不进行模型微调，而是借鉴环境 LLM 领域关于"结构化领域数据→专门评价框架→部署边界分析"的研究方向（如 Chen 等, 2026; Meyur 等, 2025），将研究对象收束在佛山市塑胶行业建设项目环评报告表审核场景，通过标准库和经验库的分层构建与对照实验，验证知识资源对审核质量的影响。

### 6.4 Benchmark 验证边界（中期汇报/论文实验章节可用）

> 当前 v0.6a benchmark 仅包含 18 道正式题，样本集中于佛山市塑胶行业指南适用场景，评分由单一研究者完成且未进行独立双评。因此，实验结果只能支持"方法链路可运行""标准库提升依据可追溯性""经验库在部分题目中带来经办人式追问增量"等有限结论，不应表述为系统已被统计证明有效或可以替代人工审核。

---

## 7. 最终结论

**谨慎结论：文献证据包可以支撑中期汇报和论文方法章节初稿，但不可直接用于最终定稿。**

具体判断：

1. **可立即用于中期汇报**（标注"文献尚在补充核验中"）：主张 1（报告质量）、主张 2（普通问答不足）、主张 4（标准库/RAG）、主张 5（CBR 理论）、主张 6（专家验证）均有充分或基本充分的文献支撑，表述克制、边界清晰。

2. **需核验后使用**：主张 8（Chen 范式迁移）依赖未核验文献，建议中期汇报中降级表述。

3. **需补充文献**：主张 7（评价可靠性）需要补充 1-2 篇 Kappa / 一致性检验的操作层面文献；全部主张均需补充中文环评审核制度文献。

4. **bib 需补齐**：当前缺少 Cilliers 2025、Gimenez 2025、Schneider 2022、Allard 2026、Du 2026 等至少 5 条文献的 bib 条目。

5. **经验库引入稳妥**：未发现"经验库等同于判例""经验替代标准"等风险表述，审慎措辞覆盖充分。

---

## 附录：文件清单

| 文件名 | 用途 |
|---|---|
| `openclaw_literature_review_20260617.md` | 本复核报告 |
| `openclaw_literature_review_table_20260617.csv` | 结构化复核表 |
