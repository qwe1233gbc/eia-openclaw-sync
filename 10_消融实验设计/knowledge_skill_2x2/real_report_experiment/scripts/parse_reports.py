import argparse
from core import parse_reports, report_root

parser = argparse.ArgumentParser()
parser.add_argument("--report-root")
args = parser.parse_args()
rows = parse_reports(report_root(args.report_root))
print({"success": sum(r["parse_status"] == "success" for r in rows), "total": len(rows)})
