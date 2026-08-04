import argparse
import csv
from pathlib import Path
from core import ROOT, interaction

parser = argparse.ArgumentParser()
parser.add_argument("--aggregate", default="reports/aggregate_results.csv")
args = parser.parse_args()
path = ROOT / args.aggregate
if not path.exists():
    raise SystemExit("No aggregate results exist; effects were not fabricated.")
values = {r["group"]: float(r["mean_total"]) for r in csv.DictReader(path.open(encoding="utf-8-sig"))}
if set(values) != {"A", "B", "C", "D"}:
    raise SystemExit("A/B/C/D are all required")
effects = {
    "B-A": values["B"] - values["A"],
    "C-A": values["C"] - values["A"],
    "D-A": values["D"] - values["A"],
    "D-B": values["D"] - values["B"],
    "D-C": values["D"] - values["C"],
    "interaction_trend": interaction(values["A"], values["B"], values["C"], values["D"]),
}
(ROOT / "reports" / "abcd_effects.json").write_text(__import__("json").dumps(effects, ensure_ascii=False, indent=2), encoding="utf-8")
print(effects)
