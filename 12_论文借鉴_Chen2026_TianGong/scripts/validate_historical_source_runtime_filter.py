from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl"


def load_manifest(path: Path = MANIFEST) -> dict[str, dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["source_id"]: row for row in rows}


def parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def evaluate_source(report_date: str | None, source: dict, competing_versions_exist: bool = False) -> dict:
    selected_source_id = source["source_id"]
    effective = parse_date(source.get("applicable_from") or source.get("effective_date"))
    expiry = parse_date(source.get("applicable_until"))
    result = {
        "report_date": report_date,
        "effective_date": effective.isoformat() if effective else "",
        "expiry_or_repeal_date": expiry.isoformat() if expiry else "",
        "historical_applicability": source.get("historical_applicability", ""),
        "selected_source_id": selected_source_id,
        "applicability_result": "",
        "manual_review_needed": False,
    }
    if not report_date:
        if competing_versions_exist:
            result.update(applicability_result="manual_review_required_missing_report_date", manual_review_needed=True)
        else:
            result["applicability_result"] = "indeterminate_missing_report_date"
        return result
    when = parse_date(report_date)
    if effective and when < effective:
        result["applicability_result"] = "not_yet_effective"
    elif expiry and when > expiry:
        result["applicability_result"] = "expired_or_repealed"
    else:
        result["applicability_result"] = "applicable"
    return result


def main() -> int:
    manifest = load_manifest()
    errors: list[dict] = []
    required_fields = ("applicable_from", "applicable_until", "historical_applicability")
    historical_ids = ("SOLID_HW2021_HIST", "SOLID_HW2025_CURRENT", "SOLID_GB34330_2017_HIST", "SOLID_GB34330_2025")
    for source_id in historical_ids:
        source = manifest.get(source_id)
        if not source:
            errors.append({"source_id": source_id, "type": "source_missing"})
            continue
        for field in required_fields:
            if field not in source:
                errors.append({"source_id": source_id, "field": field, "type": "runtime_boundary_field_missing"})

    scenarios = [
        ("2024-06-30", "SOLID_HW2025_CURRENT", "not_yet_effective"),
        ("2025-06-30", "SOLID_HW2021_HIST", "expired_or_repealed"),
        ("2026-02-28", "SOLID_GB34330_2025", "not_yet_effective"),
        ("2026-03-01", "SOLID_GB34330_2017_HIST", "expired_or_repealed"),
    ]
    results = []
    for report_date, source_id, expected in scenarios:
        result = evaluate_source(report_date, manifest[source_id], competing_versions_exist=True)
        results.append(result)
        if result["applicability_result"] != expected:
            errors.append({"source_id": source_id, "report_date": report_date, "expected": expected, "actual": result["applicability_result"], "type": "negative_runtime_filter_failed"})
    missing_date = evaluate_source(None, manifest["SOLID_HW2021_HIST"], competing_versions_exist=True)
    results.append(missing_date)
    if missing_date["applicability_result"] != "manual_review_required_missing_report_date" or not missing_date["manual_review_needed"]:
        errors.append({"type": "missing_report_date_did_not_require_manual_review"})

    report = {"sources_checked": len(historical_ids), "scenarios_checked": len(results), "results": results, "errors": errors, "pass": not errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
