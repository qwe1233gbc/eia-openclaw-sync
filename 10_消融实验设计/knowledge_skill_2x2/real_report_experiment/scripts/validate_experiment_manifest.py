import argparse
from pathlib import Path
from core import ROOT, validate_manifest

parser = argparse.ArgumentParser()
parser.add_argument("--manifest", default="manifests/formal_manifest.csv")
parser.add_argument("--allow-dry-run", action="store_true")
args = parser.parse_args()
errors = validate_manifest(ROOT / Path(args.manifest), args.allow_dry_run)
print({"errors": errors})
raise SystemExit(1 if errors else 0)
