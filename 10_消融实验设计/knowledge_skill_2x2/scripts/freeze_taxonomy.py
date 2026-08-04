from __future__ import annotations

from pipeline_core import ROOT, TAXONOMY_JSONL, read_jsonl, sha256, write_json


def main() -> None:
    rows = read_jsonl(TAXONOMY_JSONL)
    invalid_overrides = [
        row["question_id"]
        for row in rows
        if not row.get("template_default_used") and not str(row.get("override_reason") or "").strip()
    ]
    if len(rows) != 210 or invalid_overrides:
        raise SystemExit(f"无法冻结：题数={len(rows)}，无理由覆盖={invalid_overrides}")
    manifest = {
        "taxonomy_version": "v1",
        "question_count": len(rows),
        "taxonomy_jsonl_sha256": sha256(TAXONOMY_JSONL),
        "classification_uses_model_results": False,
        "pilot_selection": {
            "projects": ["PL001", "PL002", "PL003", "PL004", "PL020", "PL026"],
            "domains": [
                "water_emission_standard",
                "air_emission_standard",
                "noise_emission_standard",
            ],
            "expected_questions": 18,
        },
    }
    write_json(ROOT / "gold" / "taxonomy_freeze_manifest_v1.json", manifest)
    print("taxonomy frozen")


if __name__ == "__main__":
    main()
