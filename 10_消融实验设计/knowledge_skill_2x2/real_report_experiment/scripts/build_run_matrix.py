import argparse
from core import build_run_matrix

parser = argparse.ArgumentParser()
parser.add_argument("--stage", choices=["dry_run", "formal"], default="dry_run")
args = parser.parse_args()
rows = build_run_matrix(args.stage)
print({"runs": len(rows), "stage": args.stage})
