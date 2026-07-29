#!/usr/bin/env python3
"""Build the 13-sheet governance workbook through the bundled artifact-tool runtime."""
from __future__ import annotations

import os
import subprocess
import csv
import json
from pathlib import Path

from governance_core import OUT, ROOT, build_all

HERE = Path(__file__).resolve().parent
node = Path(os.environ.get("CODEX_BUNDLED_NODE", r"C:\Users\ylx\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"))
build_all()

def csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

payload = {
    "records": csv_rows(OUT / "gold_governance_records_v1.csv"),
    "anomalies": csv_rows(OUT / "reports" / "judgement_anomalies.csv"),
    "A": csv_rows(OUT / "review_queue_A.csv"),
    "B": csv_rows(OUT / "review_queue_B.csv"),
    "C": csv_rows(OUT / "review_queue_C.csv"),
    "D": csv_rows(OUT / "review_queue_D.csv"),
    "pilot": csv_rows(OUT / "pilot" / "pilot_option_B_balanced.csv"),
    "formal": csv_rows(OUT / "formal" / "formal_candidate_pool.csv"),
}
(ROOT / ".cache" / "workbook_inputs.json").write_text(
    json.dumps(payload, ensure_ascii=False), encoding="utf-8"
)
raise SystemExit(subprocess.call([str(node), str(HERE / "create_gold_governance_workbook.mjs")]))
