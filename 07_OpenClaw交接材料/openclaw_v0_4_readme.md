# OpenClaw v0.4 README

## Quick Start

1. Read `00_先看这里_README/README.md` for research overview
2. Load standard cards: `03_指南解析_明文标准库/plastic_guide_standard_cards_v0_4_checked.jsonl` (38 cards)
3. Load experience cards: `04_顺德类案经验库/plastic_case_experience_cards_v0_4_checked.jsonl` (8 cards, 3 core)
4. Review benchmark: `06_Benchmark最小实验/benchmark_items_mvp_v0_4.jsonl` (8 questions)
5. Execute MVP experiment using A/B/C group design

## Current Status

- Standard library: MVP-ready (38 cards with source tracing)
- Experience library: Candidate-ready (3 core cards usable, need evidence binding for formal use)
- Sample chains: Partial (2 B-level chains for benchmark)
- Benchmark: 8 questions based on 康明新材料厂 (coating+adhesive project)

## Key Limitations

- Experience cards NOT verified by real inspectors
- Small sample size
- Gold answers NOT validated
- Results NOT for formal paper conclusions

## Next Steps for OpenClaw

1. Run A/B/C experiment on 8 benchmark questions
2. Compare group scores: B-A (standard contribution), C-B (experience increment)
3. Report which standard cards were most frequently referenced
4. Report which experience cards triggered novel review insights
5. Flag any gold answer discrepancies for human review
