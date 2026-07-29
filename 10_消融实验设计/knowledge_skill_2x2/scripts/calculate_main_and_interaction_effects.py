from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

from pipeline_core import effect_components, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--lower-is-better", action="store_true")
    args = parser.parse_args()
    rows = list(csv.DictReader(args.input.open(encoding="utf-8-sig")))
    grouped = defaultdict(list)
    for row in rows:
        value = float(row["value"])
        grouped[row["group"]].append(1 - value if args.lower_is_better else value)
    means = {group: statistics.mean(values) for group, values in grouped.items()}
    missing = set("ABCD") - means.keys()
    if missing:
        raise SystemExit(f"缺少实验组: {sorted(missing)}")
    write_json(args.output, {"group_means": means, **effect_components(**{k.lower(): means[k] for k in "ABCD"})})


if __name__ == "__main__":
    main()
