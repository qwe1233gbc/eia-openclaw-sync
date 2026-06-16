# Literature Matrix - Codex Draft 2026-06-16

## Scope Note

This matrix is built from the GitHub project hub and Zotero collections:

- GitHub hub: `eia-openclaw-sync`
- Zotero collections: `环评经验库` (13 items), `环评经验库相关论文` (11 items), `环评审核综述文章` (15 items)

Thesis boundary used here: the study is not about generic plastic manufacturing or pure C2929 injection molding. It focuses on Foshan plastic-sector EIA review scenarios involving glue, coating, lamination/composite processes, curing, plastic film/packaging, VOCs source accounting and VOCs governance.

## Core Literature Matrix

| Cluster | Paper | Scientific/problem focus | Method contribution | Relevance to this thesis | Boundary / caution |
|---|---|---|---|---|---|
| EIA LLM benchmark | Meyur et al. (2025), *Benchmarking LLMs for Environmental Review and Permitting* | Whether LLMs can reason over NEPA environmental review/permitting documents | NEPAQuAD benchmark, MAPLE evaluation pipeline, context-driven QA comparison | Supports building a task-specific benchmark from real EIA/permitting texts | Their setting is NEPA/EIS QA, not Chinese construction-project report-table review |
| EIA screening with GPT | Cilliers et al. (2025), *Large Language Model-assisted EIA screening* | Whether a customized GPT can assist list-based EIA screening | Iterative GPT screener tested on 20 South African cases | Supports context-specific, iterative refinement and human oversight | Screening differs from detailed technical review; do not claim full audit automation |
| AI and public scrutiny | Gimenez et al. (2025), *Facilitating public scrutiny of EIA reports with open data and AI* | How AI/open data can help scrutinize complex EIA reports | OD + AI + comparative analysis for uncertainty and expert-judgment appraisal | Supports the transparency and traceability framing of AI-assisted EIA review | Public scrutiny case; not a standard-card/experience-card controlled experiment |
| EIA ontology | Garrido & Requena (2011), *Proposal of ontology for EIA* | EIA terminology and methods vary across contexts, hindering reuse | EIA ontology and knowledge mobilization interface | Supports formal structuring of EIA terms, modules, and standard knowledge | Ontology is general; this thesis narrows to Foshan plastic-guide modules |
| Classic case-based reasoning | Watson & Marir (1994), *Case-based reasoning: a review* | How prior cases can support problem solving without fully eliciting rules | CBR cycle: retrieve, reuse/adapt, revise, retain | Theoretical basis for turning historical review comments into experience cards | CBR requires similarity control; hence relevance filtering is essential |
| LLM experiential learning | Zhao et al. (2023), *ExpeL* | How agents learn from experience without fine-tuning | Extract natural-language insights from training tasks and recall them at inference | Supports representing review experience as reusable natural-language heuristics | General agent tasks; environmental audit evidence binding remains thesis contribution |
| Reflective agent memory | Allard et al. (2026), *Experiential Reflective Learning* | Agents need task-relevant heuristics rather than dumping all experience | Generate heuristics from trajectories and retrieve top relevant heuristics | Strong support for `relevance` filtering before experience-card use | Do not cite ERL as evidence that this thesis system is self-improving |
| Agent memory survey | Du (2026), *Memory for Autonomous LLM Agents* | Memory architecture: write-manage-read; evaluation of decision-making memory | Taxonomy of temporal scope, substrate, and control policy | Frames the experience library as managed, selectively recalled memory | It is a survey and not EIA-specific |
| Knowledge graphs | Hogan et al. (2022), *Knowledge Graphs* | How graph models represent, query, validate, and extract knowledge | KG representation/extraction/query/validation overview | Supports standard library as structured, traceable knowledge rather than plain prompt text | This project currently uses cards/JSONL, not a full formal KG |
| KG in NLP | Schneider et al. (2022), *A decade of KGs in NLP* | How KGs support NLP tasks and what research streams exist | Survey of KG-related NLP tasks and maturity | Supports using structured domain knowledge in language tasks | Broad NLP survey; not EIA-specific |
| Regulatory NLP | Bommarito et al. (2018), *LexNLP* | Extracting structured data from legal and regulatory texts | Open-source legal/regulatory NLP extraction toolkit | Supports extracting clauses, dates, entities, quantities from standards/reports | Legal/regulatory domain adjacent, not environmental technical audit |
| Incomplete KB reasoning | Thai et al. (2022), *CBR-iKB* | QA over incomplete knowledge bases | Case-based reasoning over incomplete KBs with adaptive non-parametric reasoning | Helps justify case reasoning under incomplete experience coverage | Not an EIA audit method; only conceptual support |
| Human-AI collaboration evaluation | Fragiadakis et al. (2025), *Evaluating Human-AI Collaboration* | HAIC evaluation needs multidimensional metrics | Framework combining quantitative/qualitative and mode-specific metrics | Supports separating common review quality and knowledge-use scores | Framework is domain-agnostic; thesis still needs human-review validation |
| Public-sector AI bias | Alon-Barkat & Busuioc (2023), *Human-AI interactions in public sector decision making* | Automation bias and selective adherence in public decision making | Experiments with citizens/civil servants on algorithmic advice | Supports keeping human oversight and not claiming replacement of reviewers | Not environmental review; use for risk framing only |
| EIS quality review | Lee et al.; Kabir et al. | Quality review of environmental statements | Review package / EIS quality criteria | Supports using review criteria and real correction comments as evaluation anchors | Older and often general EIS quality work; not LLM-specific |
| Environmental report RAG | Garigliotti (2024), *SDG target detection in environmental reports using RAG with LLMs* | Detecting SDG target evidence in environmental reports | RAG evaluation for evidence identification/detection | Supports retrieval-based evidence grounding in environmental text | SDG target detection differs from compliance audit |

## Local Project Evidence Matrix

| Project component | Local source | Literature support | Thesis role |
|---|---|---|---|
| Standard card library | `03_指南解析_明文标准库` with 38 standard cards | Garrido & Requena; Hogan et al.; LexNLP | Turns dispersed clauses, formulas, limits and evidence requirements into traceable review knowledge |
| Experience card library | `04_顺德类案经验库`, 8 active + 5 candidate | Watson & Marir; Zhao et al.; Allard et al.; Du | Encodes historical review comments as reusable but bounded experience |
| Relevance filtering | `experience_relevance_schema_v0_6a` and v0.6a hit reports | Allard et al.; Du; Alon-Barkat & Busuioc | Controls when experience can be used and prevents cross-task/industry misuse |
| Benchmark | `06_Benchmark最小实验`, 18 main + 2 backup | Meyur et al.; Fragiadakis et al. | Converts review ability into testable question groups with explicit scoring |
| A/B/C experiment | `outputs/openclaw_mvp_v0_6a` | Meyur et al.; Cilliers et al. | Demonstrates the method chain: report only vs standard library vs standard+experience |

## Immediate Literature Gaps

1. Few studies connect EIA intelligent review with a dual knowledge base that separates explicit standards from local review experience.
2. Existing EIA-LLM work focuses on screening, public scrutiny, or QA; it rarely tests reviewer-style correction generation against real review comments.
3. Agent memory literature supports experience reuse, but does not solve administrative-domain evidence binding.
4. Public-sector AI literature warns against replacing human reviewers, supporting a thesis framing of assisted review rather than automated approval.
5. The v0.6a experiment is a small feasibility/chain-validation study, not a statistically valid effectiveness proof.
