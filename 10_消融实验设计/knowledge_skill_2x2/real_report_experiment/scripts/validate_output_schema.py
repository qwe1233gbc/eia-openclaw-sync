import argparse
import json
from pathlib import Path
from core import validate_output

parser = argparse.ArgumentParser()
parser.add_argument("output")
args = parser.parse_args()
errors = validate_output(json.loads(Path(args.output).read_text(encoding="utf-8")))
print({"errors": errors})
raise SystemExit(1 if errors else 0)
