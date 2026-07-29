from __future__ import annotations

from collections import Counter

from pipeline_core import (
    PILOT_DOMAINS,
    PILOT_PROJECTS,
    ROOT,
    source_by_id,
    taxonomy_by_id,
    write_jsonl,
)


def main() -> None:
    source = source_by_id()
    taxonomy = taxonomy_by_id()
    selected = [
        item
        for item in taxonomy.values()
        if item["project_id"] in PILOT_PROJECTS and item["audit_domain"] in PILOT_DOMAINS
    ]
    selected.sort(key=lambda row: (PILOT_PROJECTS.index(row["project_id"]), row["audit_domain"]))
    if len(selected) != 18:
        raise SystemExit(f"预期18题，实际{len(selected)}题")
    output = []
    for item in selected:
        raw = source[item["question_id"]]
        output.append(
            {
                "question_id": item["question_id"],
                "project_id": item["project_id"],
                "question": raw.get("question"),
                "report_evidence": raw.get("evidence"),
                "reference_answer": raw.get("润色后答案") or raw.get("answer"),
                "reference_basis": raw.get("source_basis"),
                "manual_judgement": raw.get("人工判断"),
                "gold_confirmation_status": (
                    "pending_human_confirmation"
                    if str(raw.get("是否需要人工复核") or "") == "是"
                    else "source_marked_no_review"
                ),
                "taxonomy": {
                    key: item[key]
                    for key in (
                        "audit_domain",
                        "cognitive_level",
                        "reasoning_type",
                        "primary_functional_capability",
                        "knowledge_dependency",
                        "workflow_dependency",
                        "evidence_span",
                    )
                },
                "sample_selection_frozen": True,
            }
        )
    write_jsonl(ROOT / "gold" / "pilot_questions_18.jsonl", output)
    domains = Counter(row["taxonomy"]["audit_domain"] for row in output)
    judgements = Counter(str(row["manual_judgement"]) for row in output)
    pending = sum(row["gold_confirmation_status"] == "pending_human_confirmation" for row in output)
    report = [
        "# 18题趋势样本分类分布",
        "",
        f"- 项目：{', '.join(PILOT_PROJECTS)}",
        f"- 题数：{len(output)}",
        f"- 待人工确认金标：{pending}",
        "",
        "## 审核领域",
        "",
        *[f"- `{key}`：{value}" for key, value in sorted(domains.items())],
        "",
        "## 人工判断",
        "",
        *[f"- `{key}`：{value}" for key, value in sorted(judgements.items())],
        "",
        "选题ID已冻结；待人工确认仅影响金标终审，不得据模型结果反向改题或改分类。",
    ]
    (ROOT / "reports" / "pilot_sample_taxonomy_distribution.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
