# v0.6a Experiment Design

## Positioning
v0.6a is NOT a formal large-sample experiment. It fixes v0.5 issues without expanding scope:
- Fix questions (retrieval mismatch, coverage gaps)
- Fix scoring (separate common + knowledge scores)
- Fix experience card relevance (prevent Q03-style false hits)
- Prepare human review materials

## Question Structure
- Main set: 18 questions
- Backup: 2 questions
- NOT "20 formal questions" - make it clear 18+2

## Types
- guide_explicit: 5 (2 retained + 3 new)
- standard_calculation: 4 (1 negative control + 3 new)
- case_experience: 5 (2 retained + 3 new)
- cross_check: 4 (1 retained + 3 new)

## Retained from v0.5 (5)
Q01: Glue VOCs content - high discrimination
Q02: Carbon replacement cycle - quantitative anchor
Q03: Collection efficiency - best performer
Q04: VOCs total substitution - clear policy
Q05: Process x VOCs cross-check - cross-item reasoning

## Negative Control (1)
Q06: Safety facilities (retained Q04 from v0.5) - tests zero false positive

## New (12 main + 2 backup)
Guide_explicit: standard selection, VOCs storage, hazwaste identification
Standard_calculation: air volume, carbon wind speed, waste carbon quantity
Case_experience: composite process VOCs, cooling water discharge, environmental risk
Cross_check: VOCs source chain, hazwaste x materials, monitoring plan x exhaust

## Scoring
common_score_6: judgement(2) + evidence(2) + actionability(2)
knowledge_use_score_4: standard(2) + experience(2)
total_score_10: only for B/C groups
A group only uses common_score_6

## Experience Cards
Active: 8 cards with relevance fields (NOT expanded to 15)
Candidate: safety, equipment, air volume, hazwaste, cooling, env risk (NOT called in v0.6a)
Pending: downgraded, cannot be used as strong evidence
