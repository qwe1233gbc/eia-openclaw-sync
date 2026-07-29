#!/usr/bin/env python3
"""Reject any purported frozen gold item that does not pass every freeze gate."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from governance_core import RECORDS_CSV


def validation_errors(row: dict[str, Any]) -> list[str]:
    if row.get("gold_review_status") != "已冻结":
        return []
    errors = []
    final = str(row.get("normalized_judgement_final", "")).strip()
    if not final: errors.append("最终结论为空")
    if final == "待判断": errors.append("最终结论仍为待判断")
    if row.get("item_quality_status") != "有效": errors.append("题目质量不是有效")
    if row.get("evidence_sufficiency") != "充分":
        errors.append("证据充分性未达到充分")
    if row.get("basis_verification_status") not in {"已核验", "不需要外部依据"}:
        errors.append("依据未核验")
    if row.get("taxonomy_review_status") not in {"人工确认", "人工覆盖"}:
        errors.append("四维分类尚未人工确认")
    if row.get("taxonomy_review_status") == "人工覆盖" and not str(row.get("taxonomy_override_reason", "")).strip():
        errors.append("分类覆盖缺少原因")
    if str(row.get("auto_flag_reason", "")).strip():
        errors.append("仍存在未解决自动异常标记")
    if not str(row.get("reviewer_1", "")).strip():
        errors.append("一审审核者为空")
    if not str(row.get("gold_version", "")).strip():
        errors.append("gold_version为空")
    return errors


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for row in rows:
        errors = validation_errors(row)
        if errors:
            failures.append({"question_id": row.get("question_id", ""), "errors": errors})
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path, default=RECORDS_CSV)
    args = parser.parse_args()
    failures = validate(load_rows(args.path))
    if failures:
        print(json.dumps(failures, ensure_ascii=False, indent=2))
        return 1
    print("PASS: no invalid frozen gold records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
