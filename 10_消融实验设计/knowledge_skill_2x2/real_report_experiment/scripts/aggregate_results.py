import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from core import ROOT, programmatic_total

parser = argparse.ArgumentParser()
parser.add_argument("--scores", default="runs/scores.jsonl")
args = parser.parse_args()
path = ROOT / args.scores
if not path.exists():
    raise SystemExit("No GPT scores exist; aggregation was not fabricated.")
groups = defaultdict(list)
for line in path.read_text(encoding="utf-8").splitlines():
    if line:
        row = json.loads(line)
        groups[row["group"]].append(programmatic_total(row))
summary = [{"group": group, "mean_total": sum(values) / len(values), "n": len(values)} for group, values in sorted(groups.items())]
with (ROOT / "reports" / "aggregate_results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["group", "mean_total", "n"])
    writer.writeheader(); writer.writerows(summary)
print(summary)
