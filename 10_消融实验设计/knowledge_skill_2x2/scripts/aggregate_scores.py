from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from pipeline_core import bootstrap_mean_ci


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
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["group"]].append(float(row["total_score"]))
    output = []
    for group, values in sorted(grouped.items()):
        low, high = bootstrap_mean_ci(values)
        output.append(
            {
                "group": group,
                "n": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "bootstrap_ci_low": low,
                "bootstrap_ci_high": high,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]) if output else ["group"])
        writer.writeheader()
        writer.writerows(output)


if __name__ == "__main__":
    main()
