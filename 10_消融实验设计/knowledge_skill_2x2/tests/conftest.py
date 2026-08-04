import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

def governance_rows():
    with (ROOT / "gold_governance" / "gold_governance_records_v1.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))

def source_payload():
    return json.loads((ROOT / ".cache" / "source_questions.json").read_text(encoding="utf-8"))
