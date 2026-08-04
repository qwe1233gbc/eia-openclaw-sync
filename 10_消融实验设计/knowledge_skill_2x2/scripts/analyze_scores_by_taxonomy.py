from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

from pipeline_core import taxonomy_by_id

FIELDS = [
    "cognitive_level",
    "audit_domain",
    "reasoning_type",
    "primary_functional_capability",
    "knowledge_dependency",
    "workflow_dependency",
    "evidence_span",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    taxonomy = taxonomy_by_id()
    rows = list(csv.DictReader(args.input.open(encoding="utf-8-sig")))
    grouped = defaultdict(list)
    for row in rows:
        tax = taxonomy[row["question_id"]]
        for field in FIELDS:
            grouped[(field, tax[field], row["group"])].append(float(row["total_score"]))
    output = [
        {
            "dimension": field,
            "label": label,
            "group": group,
            "n": len(values),
            "mean_score": statistics.mean(values),
        }
        for (field, label, group), values in sorted(grouped.items())
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]) if output else ["dimension"])
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    main()
