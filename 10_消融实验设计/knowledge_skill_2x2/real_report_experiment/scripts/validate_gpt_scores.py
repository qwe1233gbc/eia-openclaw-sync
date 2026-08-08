import argparse
import json
from pathlib import Path
from core import programmatic_total

parser = argparse.ArgumentParser()
parser.add_argument("scores")
args = parser.parse_args()
errors = []
for line in Path(args.scores).read_text(encoding="utf-8").splitlines():
    if not line:
        continue
    row = json.loads(line)
    computed = programmatic_total(row)
    if float(row.get("total_score", computed)) != computed:
        errors.append(row.get("blinded_output_id", "unknown"))
print({"total_score_mismatches": errors})
raise SystemExit(1 if errors else 0)
