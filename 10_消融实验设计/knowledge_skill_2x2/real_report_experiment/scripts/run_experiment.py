import argparse
from core import run_group

parser = argparse.ArgumentParser()
parser.add_argument("--group", choices=["A", "B", "C", "D"], required=True)
parser.add_argument("--backend", default="mock")
args = parser.parse_args()
rows = run_group(args.group, args.backend)
print({"group": args.group, "runs": len(rows), "backend": args.backend, "not_for_analysis": True})
