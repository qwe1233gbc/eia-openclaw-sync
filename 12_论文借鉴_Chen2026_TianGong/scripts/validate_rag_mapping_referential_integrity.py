from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml"
REGISTRY = ROOT / "09_环评审核技能库/formal_skill_registry.yaml"
MANIFEST = ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl"
RAG_CONTEXTS = [
    ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl",
    ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl",
]
RUN_MATRIX = ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv"
REPORT = ROOT / "09_环评审核技能库/quality/rag_mapping_referential_integrity_report.json"
VERIFICATION_REPORT = ROOT / "09_环评审核技能库/quality/gbt18920_fulltext_verification_report.json"
PARENT_CHUNKS = ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl"
FORMAL_GBT_SOURCE = "WATER_GBT18920_2020"
METADATA_GBT_SOURCE = "WATER_GBT18920_2020_METADATA"
GBT_QUESTIONS = {"PL004_Emission_水污", "PL005_Emission_水污"}

FORBIDDEN_SOURCE_MARKERS = (
    "05_QA测试集",
    "09_环评审核技能库",
    "06_Dify工作流",
    "10_消融实验设计",
    "人工答案",
    "人工金标",
    "标准卡",
    "Skill",
    "QA数据",
)
TIME_DIMENSIONS = {"valid_time", "policy_valid_time", "report_date", "data_year"}
def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def gbt_activation_ready(verification: dict, source: dict | None, table1_parents: list[dict]) -> bool:
    return bool(
        verification.get("pass") is True
        and source
        and source.get("eligible_for_formal_rag") is True
        and source.get("full_text_available") is True
        and table1_parents
    )


def main() -> int:
    mapping = yaml.safe_load(MAPPING.read_text(encoding="utf-8"))
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    registry_by_skill = {
        str(item["skill_id"]): item
        for item in registry.get("skills", [])
        if str(item.get("skill_id")) != "99"
    }
    manifest_rows = load_jsonl(MANIFEST)
    manifest = {row["source_id"]: row for row in manifest_rows}
    errors: list[dict] = []
    warnings: list[dict] = []
    candidate_count = 0
    metadata_count = 0

    metadata_ids: set[str] = set()
    for item in mapping.get("mappings", []):
        sid = str(item.get("skill_id", ""))
        registry_item = registry_by_skill.get(sid)
        if registry_item is None:
            errors.append({"skill_id": sid, "type": "formal_registry_entry_missing"})
        else:
            for key in ("candidate_source_ids", "metadata_only_source_ids", "query_template", "required_applicability_dimensions"):
                if (item.get(key) or []) != (registry_item.get(key) or []):
                    errors.append({"skill_id": sid, "field": key, "type": "mapping_registry_mismatch"})
        dimensions = set(item.get("required_applicability_dimensions") or [])
        candidates = item.get("candidate_source_ids") or []
        metadata_only = item.get("metadata_only_source_ids") or []
        candidate_count += len(candidates)
        metadata_count += len(metadata_only)
        metadata_ids.update(metadata_only)

        overlap = set(candidates) & set(metadata_only)
        for source_id in sorted(overlap):
            errors.append({"skill_id": sid, "source_id": source_id, "type": "metadata_source_in_candidate_list"})

        for source_id in candidates:
            source = manifest.get(source_id)
            if source is None:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "candidate_source_id_not_found"})
                continue
            if source.get("eligible_for_formal_rag") is not True:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "candidate_source_not_formal_rag_eligible"})
            if source.get("full_text_available") is not True:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "candidate_source_without_full_text"})
            origin_blob = " ".join(str(source.get(key, "")) for key in ("official_url", "repository_locator", "path_policy", "source_provenance", "acquisition_method"))
            if any(marker in origin_blob for marker in FORBIDDEN_SOURCE_MARKERS):
                errors.append({"skill_id": sid, "source_id": source_id, "type": "forbidden_non_normative_source"})
            validity = str(source.get("validity_status", ""))
            if "废止" in validity:
                if not source.get("historical_applicability"):
                    errors.append({"skill_id": sid, "source_id": source_id, "type": "retired_source_without_historical_scope"})
                elif not (dimensions & TIME_DIMENSIONS):
                    errors.append({"skill_id": sid, "source_id": source_id, "type": "retired_source_without_runtime_time_filter"})
                else:
                    warnings.append({"skill_id": sid, "source_id": source_id, "type": "historical_source_requires_report_time_filter"})

        for source_id in metadata_only:
            source = manifest.get(source_id)
            if source is None:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "metadata_source_id_not_found"})
                continue
            if source.get("eligible_for_formal_rag") is not False:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "metadata_source_unexpectedly_eligible"})
            if source.get("full_text_available") is not False:
                errors.append({"skill_id": sid, "source_id": source_id, "type": "metadata_source_has_full_text_flag"})

    formal_source = manifest.get(FORMAL_GBT_SOURCE)
    metadata_source = manifest.get(METADATA_GBT_SOURCE)
    if formal_source is None:
        errors.append({"source_id": FORMAL_GBT_SOURCE, "type": "formal_gbt18920_source_missing"})
    elif formal_source.get("eligible_for_formal_rag") is not True or formal_source.get("full_text_available") is not True:
        errors.append({"source_id": FORMAL_GBT_SOURCE, "type": "formal_gbt18920_source_not_active"})
    if metadata_source is None:
        errors.append({"source_id": METADATA_GBT_SOURCE, "type": "metadata_gbt18920_source_missing"})
    elif metadata_source.get("eligible_for_formal_rag") is not False or metadata_source.get("full_text_available") is not False:
        errors.append({"source_id": METADATA_GBT_SOURCE, "type": "metadata_gbt18920_source_unexpectedly_active"})

    all_candidates = {source_id for item in mapping.get("mappings", []) for source_id in item.get("candidate_source_ids", []) or []}
    all_metadata = {source_id for item in mapping.get("mappings", []) for source_id in item.get("metadata_only_source_ids", []) or []}
    if METADATA_GBT_SOURCE in all_candidates:
        errors.append({"source_id": METADATA_GBT_SOURCE, "type": "gbt_metadata_in_candidate_sources"})
    if FORMAL_GBT_SOURCE in all_metadata:
        errors.append({"source_id": FORMAL_GBT_SOURCE, "type": "gbt_formal_source_in_metadata_only_sources"})

    parent_chunks = {row["parent_id"]: row for row in load_jsonl(PARENT_CHUNKS)}
    table1_parents = [row for row in parent_chunks.values() if row.get("source_id") == FORMAL_GBT_SOURCE and row.get("table_number") == "表1"]
    if not table1_parents:
        errors.append({"source_id": FORMAL_GBT_SOURCE, "type": "gbt_table1_parent_missing"})
    elif any(not row.get("page_number") or "表1" not in row.get("content", "") for row in table1_parents):
        errors.append({"source_id": FORMAL_GBT_SOURCE, "type": "gbt_table1_parent_not_traceable"})

    contexts_by_path = [load_jsonl(path) for path in RAG_CONTEXTS]
    contexts = [row for rows in contexts_by_path for row in rows]
    for row in contexts:
        retrieved = set(row.get("retrieved_sources") or [])
        required = set(row.get("required_sources") or [])
        selected = row.get("selected_parent_chunks") or []
        body = str(row.get("rag_context", ""))
        for source_id in metadata_ids | {METADATA_GBT_SOURCE}:
            if source_id in retrieved or any(str(chunk).startswith(source_id + "_") for chunk in selected) or source_id in body:
                errors.append({"question_id": row.get("question_id"), "source_id": source_id, "type": "metadata_source_in_formal_rag_body"})
        if row.get("question_id") in GBT_QUESTIONS:
            if FORMAL_GBT_SOURCE not in required or FORMAL_GBT_SOURCE not in retrieved:
                errors.append({"question_id": row.get("question_id"), "type": "gbt_formal_source_not_required_and_retrieved"})
            if row.get("missing_required_sources"):
                errors.append({"question_id": row.get("question_id"), "type": "gbt_question_still_has_missing_source"})
            if not any(parent_chunks.get(parent_id, {}).get("table_number") == "表1" for parent_id in selected):
                errors.append({"question_id": row.get("question_id"), "type": "gbt_table1_not_selected"})
        elif FORMAL_GBT_SOURCE in required or FORMAL_GBT_SOURCE in retrieved or FORMAL_GBT_SOURCE in body:
            errors.append({"question_id": row.get("question_id"), "type": "gbt_formal_source_injected_into_unrelated_question"})

    left = {row["question_id"]: row for row in contexts_by_path[0]}
    right = {row["question_id"]: row for row in contexts_by_path[1]}
    for question_id in GBT_QUESTIONS:
        for key in ("required_sources", "retrieved_sources", "missing_required_sources", "selected_parent_chunks", "rag_context", "rag_context_sha256"):
            if left.get(question_id, {}).get(key) != right.get(question_id, {}).get(key):
                errors.append({"question_id": question_id, "field": key, "type": "frozen_snapshot_mismatch"})

    verification = json.loads(VERIFICATION_REPORT.read_text(encoding="utf-8")) if VERIFICATION_REPORT.exists() else {}
    activation_ready = gbt_activation_ready(verification, formal_source, table1_parents)

    with RUN_MATRIX.open(encoding="utf-8-sig") as f:
        matrix = list(csv.DictReader(f))
    for row in matrix:
        if row.get("question_id") not in GBT_QUESTIONS:
            continue
        if activation_ready:
            if row.get("status") != "ready_input_freeze":
                errors.append({"run_id": row.get("run_id"), "type": "verified_fulltext_run_not_unblocked"})
            if row.get("basis_status") or row.get("conclusion") or row.get("manual_review_needed"):
                errors.append({"run_id": row.get("run_id"), "type": "unblocked_run_contains_prefilled_conclusion"})
        elif row.get("status") != "blocked_primary_source_gap":
            errors.append({"run_id": row.get("run_id"), "type": "run_unblocked_without_complete_verification"})

    report = {
        "scope": "skills_to_standard_mapping -> formal source manifest + frozen RAG contexts + v2 run matrix",
        "skills_checked": len(mapping.get("mappings", [])),
        "manifest_sources": len(manifest),
        "candidate_references_checked": candidate_count,
        "metadata_only_references_checked": metadata_count,
        "frozen_rag_contexts_checked": len(contexts),
        "gbt18920_formal_source_activated": activation_ready,
        "gbt18920_table1_parent_chunks": len(table1_parents),
        "errors": errors,
        "warnings": warnings,
        "pass": not errors,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
