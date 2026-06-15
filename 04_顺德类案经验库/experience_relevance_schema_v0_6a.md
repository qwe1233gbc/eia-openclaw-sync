# Experience Relevance Schema v0.6a

## Hard Filter (Step 1)
1. task_type in not_applicable_task_types → DISCARD
2. module in not_applicable_modules → DISCARD
3. evidence_status = pending → NO strong conclusion
4. No report evidence supporting trigger → DISCARD

## Soft Classification (Step 2)
- HIGH: task_type match + module match + industry match + evidence status core/reference
- MEDIUM: module/task match but evidence chain incomplete
- LOW: only keyword match or task mismatch

## Usage Rules (Step 3)
- HIGH: can enter review judgment
- MEDIUM: auxiliary hint only, mark for human review
- LOW: discard, do not cite
