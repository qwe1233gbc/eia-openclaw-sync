from __future__ import annotations

from pipeline_core import (
    ROOT,
    TAXONOMY_CSV,
    TAXONOMY_JSONL,
    TEMPLATE_DEFAULTS,
    classify_all,
    load_source_records,
    write_csv,
    write_jsonl,
)


def main() -> None:
    rows = classify_all(load_source_records())
    fields = [
        "question_id",
        "project_id",
        "audit_domain",
        "cognitive_level",
        "reasoning_type",
        "primary_functional_capability",
        "secondary_capabilities",
        "knowledge_dependency",
        "workflow_dependency",
        "evidence_span",
        "template_default_used",
        "override_reason",
        "classification_status",
        "taxonomy_version",
        "source_category",
        "source_manual_check",
        "source_manual_judgement",
        "source_needs_human_review",
        "taxonomy_review_required",
        "taxonomy_review_reason",
    ]
    write_csv(TAXONOMY_CSV, rows, fields)
    write_jsonl(TAXONOMY_JSONL, rows)
    defaults = []
    for category, values in TEMPLATE_DEFAULTS.items():
        defaults.append(
            {
                "source_category": category,
                **{key: value for key, value in values.items() if key != "secondary_capabilities"},
                "secondary_capabilities": values["secondary_capabilities"],
            }
        )
    write_csv(ROOT / "taxonomy" / "template_default_mapping.csv", defaults)
    print(f"已分类 {len(rows)} 题")


if __name__ == "__main__":
    main()
