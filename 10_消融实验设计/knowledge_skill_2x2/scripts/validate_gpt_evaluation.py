from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import ROOT, programmatic_total, read_jsonl
from validate_output_schema import validate_file

FUNCTIONAL_RULES = {
    "report_grounding": {
        "key_report_evidence_recall": 20,
        "evidence_conclusion_alignment": 20,
    },
    "basis_grounding": {
        "basis_authenticity_and_version": 15,
        "basis_applicability": 15,
        "clause_conclusion_alignment": 10,
    },
    "numerical_accuracy": {
        "formula_and_calculation": 20,
        "values_units_and_result": 20,
    },
    "procedural_reasoning": {
        "audit_step_coverage": 15,
        "sequence_and_cross_check": 15,
        "insufficient_evidence_escalation": 10,
    },
    "evidence_integration": {
        "multi_source_evidence_coverage": 15,
        "conflict_handling": 10,
        "synthesis_completeness": 15,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = validate_file(args.path, ROOT / "schemas" / "gpt_evaluation_v1.schema.json")
    for index, row in enumerate(read_jsonl(args.path), 1):
        rules = FUNCTIONAL_RULES[row["functional_module"]]
        if set(row["functional_scores"]) != set(rules):
            errors.append(f"{index}: 功能模块分项字段不匹配")
        for key, maximum in rules.items():
            if key in row["functional_scores"] and not 0 <= row["functional_scores"][key] <= maximum:
                errors.append(f"{index}: {key}超出0—{maximum}")
        if row["total_score"] != programmatic_total(row):
            errors.append(f"{index}: total_score不是程序分项和")
        if row["basis_hallucination"] != (row["basis_hallucination_type"] != "none"):
            errors.append(f"{index}: 依据型幻觉布尔值与类型不一致")
    if errors:
        raise SystemExit("\n".join(errors))
    print("evaluation valid")


if __name__ == "__main__":
    main()
