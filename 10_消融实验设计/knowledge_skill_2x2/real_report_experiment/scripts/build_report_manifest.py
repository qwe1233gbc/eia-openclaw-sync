import argparse
from core import build_report_manifest, report_root

parser = argparse.ArgumentParser()
parser.add_argument("--report-root")
args = parser.parse_args()
rows = build_report_manifest(report_root(args.report_root))
print({"projects": len(rows), "found": sum(r["source_available"] == "true" for r in rows)})
