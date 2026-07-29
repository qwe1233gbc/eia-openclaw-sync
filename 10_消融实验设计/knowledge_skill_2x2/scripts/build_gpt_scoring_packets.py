from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import ROOT, read_jsonl, source_by_id, taxonomy_by_id, write_jsonl


def build(records: list[dict]) -> list[dict]:
    source = source_by_id()
    taxonomy = taxonomy_by_id()
    packets = []
    for row in records:
        question_id = row["question_id"]
        raw, tax = source[question_id], taxonomy[question_id]
        packets.append(
            {
                "blinded_output_id": row["blinded_output_id"],
                "question_id": question_id,
                "question": raw.get("question"),
                "question_taxonomy_for_rubric": {
                    key: tax[key]
                    for key in (
                        "audit_domain",
                        "cognitive_level",
                        "reasoning_type",
                        "primary_functional_capability",
                    )
                },
                "report_evidence": raw.get("evidence"),
                "reference_answer": raw.get("润色后答案") or raw.get("answer"),
                "reference_basis": raw.get("source_basis"),
                "model_answer": row.get("model_answer", row.get("answer")),
            }
        )
    return packets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "runs" / "blinded_packets" / "scoring_packets.jsonl"
    )
    args = parser.parse_args()
    packets = build(read_jsonl(args.input))
    write_jsonl(args.output, packets)
    print(f"built {len(packets)} packets")


if __name__ == "__main__":
    main()
