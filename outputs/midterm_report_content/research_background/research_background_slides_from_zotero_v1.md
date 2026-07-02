# 研究背景页设计：基于 Zotero 文献库

> 用途：用于中期汇报 PPT 的“研究背景”部分，可直接拆成 2-3 页。
>
> 检索范围：Zotero 主库 `libraryID=1`。
>
> 图源说明：下列图片均从 Zotero 本地论文 PDF 页面渲染后裁剪，仅用于汇报中说明研究背景和文献依据。正式论文写作时建议使用“改绘示意图 + 文献引用”的方式，PPT 中可保留截图并标注文献来源。

## 推荐使用的 3 页结构

### 第 1 页：环评文件资料复杂，传统审核依赖人工经验

页面大标题：

```text
环评文件资料复杂，审核知识难以直接复用
```

现状问题：

```text
建设项目环评文件通常包含项目概况、工艺流程、污染源强、治理设施、标准适用、总量控制和审批要求等多类信息。不同项目报告在格式、章节、术语和证据完整性上存在差异，真实审核经验也往往分散在修改意见、批复和专家判断中，难以直接转化为可检索、可复用的知识。
```

推荐插图：

```text
outputs/midterm_report_content/research_background/figures/slide_bg_01_garigliotti2023_dreamskg_clean.png
```

图注建议：

```text
EA 报告知识图谱化示意：将项目活动、环境影响和受体关系组织为机器可读知识。
来源：Garigliotti et al., 2023, WWW Companion, DOI: 10.1145/3543873.3587590。
```

PPT 页面要点：

```text
- 环评报告是典型长文本、多章节、多证据材料。
- 报告、修改意见、批复和专家经验之间缺少统一组织。
- 审核知识具有强场景性，直接依赖通用问答容易丢失依据。
- 因此需要将标准、报告和审查经验组织为可追溯知识库。
```

讲稿提示：

```text
首先，从环评文件自身特点看，它不是普通的文本问答材料。一个项目报告中同时包含建设内容、原辅料、工艺流程、污染物产生、治理设施、排放标准和管理要求等内容，而且不同编制单位的表达并不完全一致。Garigliotti 等关于环境评价知识图谱的研究也指出，环境评价报告中活动、影响和受体之间存在复杂关系，传统上很多信息只能依赖人工阅读和经验判断。

对应到本课题，佛山市塑胶行业环评文件中还涉及胶水、涂胶、复合、熟化和 VOCs 治理等具体工艺。如果不先把标准依据、报告证据和历史修改意见整理成知识库，大模型很容易只给出泛泛判断，难以支撑技术审查。
```

---

### 第 2 页：大模型可辅助环境审查，但需要任务化评价和证据约束

页面大标题：

```text
大模型具备辅助潜力，但专业审查任务仍需证据和评价框架
```

现状问题：

```text
已有研究开始将 LLM 用于环境审查和许可文档问答，但研究也显示，环境审查任务具有法规语义复杂、文档篇幅长、问题类型多样等特点。模型输出质量不仅取决于模型本身，也取决于是否提供正确上下文、是否采用 RAG、是否有专家参与构建和评价。
```

推荐插图：

```text
outputs/midterm_report_content/research_background/figures/slide_bg_02_meyur2025_maple_clean.png
```

图注建议：

```text
MAPLE 评价流程：比较无上下文、RAG、全文 PDF 和金标准片段等不同知识条件下的模型表现。
来源：Meyur et al., 2025, Benchmarking LLMs for Environmental Review and Permitting, DOI: 10.48550/arXiv.2407.07321。
```

PPT 页面要点：

```text
- 环境审查类任务已出现 LLM 评价数据集和流程。
- LLM 在专业法规/长文档任务中不能只依赖通用知识。
- 不同知识输入条件会影响输出质量。
- 本课题可借鉴“知识条件对照 + 专家评价”的思路。
```

讲稿提示：

```text
第二个背景是大模型在环境审查中的应用已经开始出现，但它并不是简单把报告丢给模型就可以完成审查。Meyur 等构建了 NEPAQuAD 和 MAPLE，用真实环境影响声明文件形成问答任务，并比较无上下文、RAG、PDF 全文和金标准片段等不同知识条件。

这对本课题有两个启发。第一，环评审查任务需要拆成可评价的问题，而不是只看模型能否生成一段看似合理的话。第二，不同知识条件会显著影响模型输出，因此我后续设计 A/B/C/D 对照实验，比较仅报告片段、加入标准依据库、加入审核技能库、再加入样本链和修改意见后的差异。
```

---

### 第 3 页：环境领域大模型应用需要结构化知识和流程化工具

页面大标题：

```text
环境领域大模型应用需要结构化知识与流程化工具支撑
```

现状问题：

```text
环境领域任务既有稳定、规则驱动的标准适用问题，也有需要跨材料整合和专业判断的问题。已有研究认为，结构化领域知识、检索增强、工具调用、可靠性评价和专家验证，是环境大模型可靠应用的重要条件。
```

推荐插图 A：

```text
outputs/midterm_report_content/research_background/figures/slide_bg_03_chen2026_llm_pipeline_clean.png
```

图注建议：

```text
环境领域 LLM 管线：结构化知识、工作流工具调用、模型评价和可靠性评估。
来源：Chen et al., 2026, Environmental Science & Technology, DOI: 10.1021/acs.est.5c09526。
```

推荐插图 B（如果页面想更简洁，可替代 A）：

```text
outputs/midterm_report_content/research_background/figures/slide_bg_03_kornov2025_eahub_progression_clean.png
```

图注建议：

```text
EA Hub 到 AI 应用的递进：从受控数据源到信息检索、单功能智能体和多智能体系统。
来源：Kørnøv et al., 2025, Impact Assessment and Project Appraisal, DOI: 10.1080/14615517.2025.2532919。
```

PPT 页面要点：

```text
- 环境 AI 应用依赖高质量、领域化、可更新的数据基础。
- 结构化知识库可降低依据不可追溯和模型幻觉风险。
- 工作流/技能库可把复杂审核过程拆解为可检查步骤。
- 本课题聚焦佛山市塑胶行业，构建标准依据库、审核技能库和样本链。
```

讲稿提示：

```text
第三个背景是，环境领域大模型应用需要领域知识和流程工具支撑。Chen 等的环境领域 LLM 研究表明，结构化语料、工作流工具调用、模型评价和可靠性评估需要结合起来。Kørnøv 等也强调，环境评价中的生成式 AI 和智能体应用，首先依赖受控、可维护、符合法规和程序要求的数据基础。

因此，本课题没有把目标设定为自动审批，也不做模型微调，而是把大模型作为知识库构建、审核任务生成和评分评价的辅助工具。具体来说，就是面向佛山市塑胶行业环评技术审查，构建标准依据库、审核技能库和样本链，再通过知识条件对照实验评价这些知识输入是否有助于提高审核辅助输出的可追溯性和可复核性。
```

## 如果只放 2 页，建议合并方式

### 方案 A：更稳妥

```text
第 1 页：环评文件资料复杂，审核知识难以直接复用
使用 Garigliotti 2023 或 Kørnøv 2025 图。

第 2 页：大模型辅助审查需要结构化知识、证据约束和评价框架
使用 Meyur 2025 + Chen 2026 两张图中的一张，重点讲 RAG、知识条件对照和专家复核。
```

### 方案 B：更突出大模型

```text
第 1 页：环境审查已进入 LLM 辅助探索阶段
使用 Meyur 2025 MAPLE 图。

第 2 页：本课题切入点是地方行业知识库与审核技能库
使用 Chen 2026 或 Kørnøv 2025 图。
```

## 文献引用清单

1. Garigliotti, D., Bjerva, J., Nielsen, F. A., Butzbach, A., Lyhne, I., Kørnøv, L., & Hose, K. (2023). Do bridges dream of water pollutants? Towards DreamsKG, a knowledge graph to make digital access for sustainable environmental assessment come true. WWW Companion. DOI: 10.1145/3543873.3587590.
2. Meyur, R., Phan, H., Hayashi, K., et al. (2025). Benchmarking LLMs for environmental review and permitting. arXiv. DOI: 10.48550/arXiv.2407.07321.
3. Chen, C., Li, N., Qi, J., et al. (2026). Leveraging LLMs for environmental complexity: structured fine-tuning data sets and deployment strategies. Environmental Science & Technology, 60(1), 497-509. DOI: 10.1021/acs.est.5c09526.
4. Kørnøv, L., Lyhne, I., & Sveding, K. R. (2025). Laying the foundation for generative AI and multi-agent systems in environmental assessment: building a curated dataset from the Danish EA Hub. Impact Assessment and Project Appraisal, 43(4), 253-266. DOI: 10.1080/14615517.2025.2532919.

## 与本课题的衔接话术

```text
综合已有研究可以看出，环评文件智能化处理并不是单纯的文本生成问题，而是一个需要标准依据、样本证据、审核流程和人工复核共同支撑的知识组织问题。已有研究为本课题提供了三个基础判断：第一，环评报告和审查材料需要结构化组织；第二，大模型在环境审查中具有辅助潜力，但必须进行任务化评价；第三，环境领域大模型应用需要受控数据、检索增强、工具流程和专家校准。

因此，本课题以佛山市塑胶行业环评文件为案例场景，研究大模型辅助下的标准依据库、审核技能库和样本链构建，并进一步通过知识条件对照实验评价其对审核辅助质量的影响。
```
