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
BLOCKED_METADATA_QUESTIONS = {"PL004_Emission_水污", "PL005_Emission_水污"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
            blob = json.dumps(source, ensure_ascii=False)
            if any(marker in blob for marker in FORBIDDEN_SOURCE_MARKERS):
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

    contexts = [row for path in RAG_CONTEXTS for row in load_jsonl(path)]
    for row in contexts:
        retrieved = set(row.get("retrieved_sources") or [])
        selected = row.get("selected_parent_chunks") or []
        body = str(row.get("rag_context", ""))
        for source_id in metadata_ids:
            if source_id in retrieved or any(str(chunk).startswith(source_id + "_") for chunk in selected) or source_id in body:
                errors.append({"question_id": row.get("question_id"), "source_id": source_id, "type": "metadata_source_in_formal_rag_body"})

    with RUN_MATRIX.open(encoding="utf-8-sig") as f:
        matrix = list(csv.DictReader(f))
    for row in matrix:
        if row.get("question_id") not in BLOCKED_METADATA_QUESTIONS:
            continue
        if row.get("status") != "blocked_primary_source_gap":
            errors.append({"run_id": row.get("run_id"), "type": "metadata_gap_not_blocked"})
        if row.get("basis_status") != "insufficient" or row.get("conclusion") != "无法判断" or row.get("manual_review_needed") != "true":
            errors.append({"run_id": row.get("run_id"), "type": "metadata_gap_unsafe_degradation"})

    report = {
        "scope": "skills_to_standard_mapping -> formal source manifest + frozen RAG contexts + v2 run matrix",
        "skills_checked": len(mapping.get("mappings", [])),
        "manifest_sources": len(manifest),
        "candidate_references_checked": candidate_count,
        "metadata_only_references_checked": metadata_count,
        "frozen_rag_contexts_checked": len(contexts),
        "errors": errors,
        "warnings": warnings,
        "pass": not errors,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
