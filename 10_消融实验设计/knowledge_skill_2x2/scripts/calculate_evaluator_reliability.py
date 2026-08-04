from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

from pipeline_core import cohen_kappa, five_band, fleiss_kappa, pearson, write_json


def calculate(rows: list[dict]) -> dict:
    by_id: dict[str, dict[str, float]] = defaultdict(dict)
    for row in rows:
        by_id[row["blinded_output_id"]][row["evaluator_id"]] = float(row["total_score"])
    evaluators = sorted({name for values in by_id.values() for name in values})
    pairwise = []
    for i, left in enumerate(evaluators):
        for right in evaluators[i + 1 :]:
            pairs = [
                (values[left], values[right])
                for values in by_id.values()
                if left in values and right in values
            ]
            if len(pairs) < 2:
                continue
            a, b = map(list, zip(*pairs))
            bands_a, bands_b = [five_band(x) for x in a], [five_band(x) for x in b]
            pairwise.append(
                {
                    "left": left,
                    "right": right,
                    "n": len(pairs),
                    "pearson": pearson(a, b),
                    "cohen_kappa": cohen_kappa(bands_a, bands_b),
                    "weighted_kappa": cohen_kappa(bands_a, bands_b, weighted=True),
                    "mean_absolute_difference": statistics.mean(
                        abs(x - y) for x, y in pairs
                    ),
                }
            )
    complete = [
        [five_band(values[evaluator]) for evaluator in evaluators]
        for values in by_id.values()
        if all(evaluator in values for evaluator in evaluators)
    ]
    return {
        "evaluators": evaluators,
        "pairwise": pairwise,
        "fleiss_kappa": fleiss_kappa(complete) if complete and len(evaluators) > 2 else None,
        "complete_case_count": len(complete),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = [
        json.loads(line)
        for line in args.input.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    write_json(args.output, calculate(rows))


if __name__ == "__main__":
    main()
