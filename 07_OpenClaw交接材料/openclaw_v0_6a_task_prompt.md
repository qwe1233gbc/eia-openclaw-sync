# OpenClaw v0.6a Task Prompt

## Load Materials
1. benchmark: `06_Benchmark最小实验/benchmark_items_mvp_v0_6a.jsonl` (18 main + 2 backup)
2. standards: `03_指南解析_明文标准库/plastic_guide_standard_cards_v0_4_checked.jsonl` (38 cards)
3. experience ACTIVE: `04_顺德类案经验库/experience_cards_active_v0_6a.jsonl` (8 cards)
4. experience CANDIDATE: DO NOT LOAD for v0.6a
5. relevance schema: `04_顺德类案经验库/experience_relevance_schema_v0_6a.json`

## Key Rules
- Q06 is negative control: NO experience card may be used
- Use hard filter + soft classification for relevance
- Pending cards cannot be strong evidence
- Score: common_6 + knowledge_4 = total_10 (B/C only)
- 18 main questions, NOT 20
- Do NOT expand experience library to 15 cards
