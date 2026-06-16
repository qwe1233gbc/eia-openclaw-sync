# Research Gap Storyline - Codex Draft 2026-06-16

## Proposed Thesis Title

面向环评智能审核的标准--经验双库构建与验证研究

副标题：以佛山市塑胶行业建设项目环评审核为例

## One-Sentence Story

Existing EIA-AI studies show that LLMs can support screening, public scrutiny, document QA, and environmental report analysis, but they do not yet provide a bounded method for combining explicit regulatory standards with evidence-graded local review experience; this thesis proposes a standard--experience dual-library method and uses a small Foshan plastic-guide benchmark to verify that the method chain is runnable, traceable, and less prone to experience misuse under relevance filtering.

## Background Logic

1. EIA review is knowledge-intensive. Reviewers must connect report statements, process routes, pollutant source accounting, standards, formulas, evidence requirements, and local approval experience.
2. Generic LLM use is risky in this setting because it may produce plausible but untraceable judgments.
3. Existing EIA-AI literature provides useful pieces:
   - EIA LLM benchmarks and QA show the need for domain-specific evaluation.
   - EIA screening studies show the value and limits of customized GPT workflows.
   - EIA ontology/KG work shows the need to structure environmental knowledge.
   - Case-based reasoning and agent memory literature show how prior experience can guide future decisions.
   - Human-AI collaboration literature warns against replacing public-sector experts.
4. The missing link is a practical review architecture that separates "what the standard explicitly says" from "what similar reviewed cases suggest reviewers often ask next."

## Research Gap

### Gap 1 - From EIA document QA to audit-oriented review

Prior EIA LLM work often asks whether models can answer questions from EIS/EIA documents. The thesis problem is different: whether an AI reviewer can identify missing evidence, questionable assumptions, and reviewer-style follow-up issues in a report-table audit context.

### Gap 2 - From generic RAG to traceable standard cards

RAG can retrieve context, but environmental review requires knowing the legal/technical status of each cited basis: guide clause, national standard, local policy, formula, limit, or evidence requirement. This motivates a standard card library rather than undifferentiated document chunks.

### Gap 3 - From raw historical cases to evidence-graded experience cards

Historical review comments are valuable but dangerous if reused without similarity control. This motivates active/candidate/pending experience cards, evidence binding, and rules that prevent candidate or pending cards from being treated as strong conclusions.

### Gap 4 - From memory retrieval to relevance filtering

Agent memory literature argues that experience must be selectively retrieved. The thesis operationalizes this through hard filters by task type, module, industry/process match, and negative-control tests.

### Gap 5 - From system demonstration to cautious validation

The current v0.6a results support feasibility and method-chain validation. They do not prove statistical effectiveness, replacement of reviewers, or full generalization across the plastic industry.

## Proposed Research Questions

1. How can explicit EIA standards, formulas, limits, and evidence requirements be transformed into a traceable standard library for intelligent review?
2. How can local historical review comments be transformed into evidence-graded experience cards without overgeneralizing across unrelated projects or modules?
3. Does adding the standard library improve the traceability and actionability of AI-generated review comments compared with report-only review?
4. Under relevance filtering, does adding the experience library provide reviewer-style follow-up increments in the subset of benchmark items where similar experience exists?
5. What modules remain uncovered by experience cards, and what does this imply for future library construction?

## Method Storyline

### Step 1 - Bound the scenario

The study scenario is Foshan plastic-sector EIA report review for projects involving glue, coating, lamination/composite processes, curing, plastic film/packaging, VOCs source accounting, and VOCs governance. Pure injection molding C2929 projects are only referential for common modules and should not define the core scenario.

### Step 2 - Build the standard library

Convert the Foshan plastic guide, national report-table guidance, VOCs standards, hazardous-waste rules, monitoring standards, and formulas into standard cards. Each card should state: source, clause/logic, applicable module, evidence required, and how the AI may use it.

### Step 3 - Build the experience library

Convert Shunde case review comments and corrected-report evidence into experience cards. Each card should state: trigger condition, reviewer concern, evidence basis, project/process scope, confidence level, and restrictions.

### Step 4 - Add relevance filtering

Before experience is used, filter by task type, module, process/industry match, and evidence status. Candidate cards are excluded from v0.6a. Pending cards can only provide weak/medium prompts and cannot support strong conclusions.

### Step 5 - Run A/B/C benchmark

Use the same 18 benchmark questions:

- A: report evidence only
- B: report evidence + standard cards
- C: report evidence + standard cards + active experience cards with relevance filtering

Use common_score_6 for all groups and knowledge_use_score_4 for B/C.

## What v0.6a Can Support

Safe claims:

- The standard library improves basis citation and traceability.
- The experience library provides reviewer-style increments in some questions.
- Relevance filtering helps reduce experience misuse.
- The OpenClaw v0.6a workflow shows that the method chain can run end to end.
- Negative control Q06 shows that irrelevant experience can be withheld in at least one designed test.

Claims to avoid:

- Do not claim statistical significance.
- Do not claim the system replaces human EIA reviewers.
- Do not claim 18 questions represent all Foshan plastic projects.
- Do not treat acceptance-announcement reports as gold answers.
- Do not treat approval documents as error labels.
- Do not treat candidate or pending experience cards as validated formal experience.

## Chapter-Level Narrative

### Chapter 1 - Introduction

Start from the practical problem: EIA report review depends on scattered standards and tacit local review experience. LLMs can read documents but need traceable, bounded knowledge support. Then narrow to Foshan plastic projects involving glue/composite/VOCs modules.

### Chapter 2 - Literature Review

Organize literature into five streams:

1. AI/LLM in EIA screening, permitting QA, and public scrutiny.
2. EIA knowledge organization, ontology, and structured environmental knowledge.
3. Knowledge graphs, regulatory NLP, and traceable retrieval.
4. Case-based reasoning and LLM agent experiential memory.
5. Human-AI collaboration and public-sector AI risk.

End with the gap: no existing work combines explicit standards and evidence-graded local experience into a relevance-filtered EIA review benchmark.

### Chapter 3 - Dual-Library Construction

Describe standard-card construction and experience-card construction separately. Emphasize different epistemic status: standard cards answer "what is required"; experience cards answer "what similar reviewers often question."

### Chapter 4 - Benchmark and Experiment

Describe the 18+2 v0.6a benchmark, A/B/C design, scoring rubric, negative control, and relevance filtering. Frame v0.6a as feasibility and chain validation.

### Chapter 5 - Results and Discussion

Discuss A to B as traceability improvement; B to C as partial reviewer-style increment; no-experience modules as library gaps; negative control as preliminary safety evidence.

### Chapter 6 - Limitations and Future Work

List sample size, single scenario, manual scoring, pending/candidate evidence gaps, lack of independent double scoring, and need for v0.7 expansion.

## Recommended Next Codex Work

1. Convert this draft into a formal `文献综述章节大纲`.
2. Expand `paper_story_cards` into 25-35 cards after Claude Code exports complete Zotero PDFs and indexes.
3. Build a `thesis_claim_guardrail.md` file mapping each planned thesis claim to permitted evidence.
4. Draft Chapter 2 with cautious language: "supports", "indicates", "provides preliminary evidence", not "proves".
