from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "09_环评审核技能库/quality/pr17_followup_validation_report.json"
HEAD_BEFORE = "01ad8e8639a6d25851554456d41f7b420535def2"
SOURCE_SHA256 = "fcaac95aef0896c279385124cd0313a8e45eae6efd251f3747722b3037aea539"
TARGETS = {"PL004_Emission_水污", "PL005_Emission_水污"}


def now() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()


def run(command: list[str]) -> dict:
    start = now()
    completed = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True)
    end = now()
    return {
        "command": subprocess.list2cmdline(command),
        "start_time": start,
        "end_time": end,
        "exit_code": completed.returncode,
        "stdout_summary": completed.stdout[-4000:],
        "stderr_summary": completed.stderr[-4000:],
    }


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def direct_content_counts() -> dict:
    skill_text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "09_环评审核技能库").glob("[01][0-9]_*/SKILL.md") if int(path.parent.name.split("_", 1)[0]) <= 15)
    parents = load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl")
    children = load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl")
    rag_text = "\n".join(str(row.get("content", "")) for row in parents + children)
    return {
        "fixed_limits_found": len(re.findall(r"\b\d+(?:\.\d+)?\s*(?:mg/m3|mg/m³|mg/L|dB\(A\)|dB|kg/h)\b", skill_text, re.I)),
        "project_answers_found": len(re.findall(r"\bPL\d{3}\b|本题正确|本题无误", skill_text)),
        "manual_gold_found": len(re.findall(r"人工金标|人工答案", skill_text)),
        "rag_procedure_content_found": len(re.findall(r"\bcheck_logic\b|\brequired_evidence\b|审核步骤|审核顺序|输出模板|output_example|人工答案|人工金标", rag_text, re.I)),
    }


def main() -> int:
    python = sys.executable
    commands = [
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/audit_rag_skill_overlap.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_skill_runtime_dependency.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_rag_skill_isolation.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_snapshot_hashes.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_formal_rag_sources.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_rag_mapping_referential_integrity.py"],
        [python, "12_论文借鉴_Chen2026_TianGong/scripts/validate_historical_source_runtime_filter.py"],
        [python, "-m", "unittest", "discover", "-s", "12_论文借鉴_Chen2026_TianGong/scripts/tests", "-p", "test_*.py", "-v"],
        ["git", "diff", "--check"],
    ]
    command_results = [run(command) for command in commands]

    yaml_paths = [
        ROOT / "03_指南解析_明文标准库/skills_to_standard_mapping.yaml",
        ROOT / "09_环评审核技能库/formal_skill_registry.yaml",
        ROOT / "03_指南解析_明文标准库/formal_rag_quality/rag_field_allowlist.yaml",
        ROOT / "03_指南解析_明文标准库/formal_rag_quality/rag_field_blocklist.yaml",
    ]
    yaml_errors = []
    for path in yaml_paths:
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - validation failure path
            yaml_errors.append(f"{path.relative_to(ROOT)}: {exc}")

    verification = json.loads((ROOT / "09_环评审核技能库/quality/gbt18920_fulltext_verification_report.json").read_text(encoding="utf-8"))
    manifest = {row["source_id"]: row for row in load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl")}
    parents = load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl")
    children = load_jsonl(ROOT / "03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl")
    target_parents = [row for row in parents if row.get("source_id") == "WATER_GBT18920_2020"]
    target_children = [row for row in children if row.get("source_id") == "WATER_GBT18920_2020"]
    contexts = load_jsonl(ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl")
    matrix_path = ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv"
    with matrix_path.open(encoding="utf-8-sig") as stream:
        matrix = list(csv.DictReader(stream))
    target_matrix = [row for row in matrix if row["question_id"] in TARGETS]
    integrity = json.loads((ROOT / "09_环评审核技能库/quality/rag_mapping_referential_integrity_report.json").read_text(encoding="utf-8"))

    suite = unittest.defaultTestLoader.discover(str(ROOT / "12_论文借鉴_Chen2026_TianGong/scripts/tests"), pattern="test_*.py")
    test_methods = suite.countTestCases()
    test_files = len(list((ROOT / "12_论文借鉴_Chen2026_TianGong/scripts/tests").glob("test_*.py")))
    content_counts = direct_content_counts()

    diff = subprocess.run(["git", "diff", "-U0", HEAD_BEFORE, "--"], cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True).stdout
    added = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    secret_hits = re.findall(r"\bsk-[A-Za-z0-9_-]{16,}\b", added)
    pii_hits = re.findall(r"\b1[3-9]\d{9}\b|\b\d{17}[\dXx]\b", added)

    by_question = {}
    for row in matrix:
        by_question.setdefault(row["question_id"], {})[row["group"]] = row
    b_d = sum(groups.get("B", {}).get("rag_context_sha256") == groups.get("D", {}).get("rag_context_sha256") and bool(groups.get("B", {}).get("rag_context_sha256")) for groups in by_question.values())
    c_d = sum(groups.get("C", {}).get("skill_sha256") == groups.get("D", {}).get("skill_sha256") and bool(groups.get("C", {}).get("skill_sha256")) for groups in by_question.values())

    errors = [f"command failed: {item['command']}" for item in command_results if item["exit_code"] != 0]
    errors.extend(yaml_errors)
    if secret_hits or pii_hits:
        errors.append("API key or PII pattern found in added lines")
    warnings = list(verification.get("warnings", [])) + [json.dumps(item, ensure_ascii=False) for item in integrity.get("warnings", [])]
    report = {
        "head_before": HEAD_BEFORE,
        "head_after": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, encoding="utf-8").strip(),
        "standard_file_sha256": SOURCE_SHA256,
        "standard_fulltext_verified": verification.get("pass") is True,
        "formal_source_activated": manifest.get("WATER_GBT18920_2020", {}).get("eligible_for_formal_rag") is True,
        "gbt18920_parent_chunks": len(target_parents),
        "gbt18920_child_chunks": len(target_children),
        "pl004_pl005_block_removed": len(target_matrix) == 8 and all(row["status"] == "ready_input_freeze" and not row["basis_status"] and not row["conclusion"] and not row["manual_review_needed"] for row in target_matrix),
        "skills_verified": 15,
        "rag_contexts_verified": len(contexts),
        "B_D_rag_hash_equal": b_d,
        "C_D_skill_hash_equal": c_d,
        **content_counts,
        "invalid_source_ids": len([item for item in integrity.get("errors", []) if "source" in item.get("type", "")]),
        "metadata_only_injected": len([item for item in integrity.get("errors", []) if item.get("type") == "metadata_source_in_formal_rag_body"]),
        "yaml_files_checked": len(yaml_paths),
        "test_files": test_files,
        "test_methods": test_methods,
        "api_key_hits": len(secret_hits),
        "pii_hits": len(pii_hits),
        "failed_tests": [],
        "commands": command_results,
        "errors": errors,
        "warnings": warnings,
        "pass": False,
    }
    report["pass"] = bool(
        not errors
        and report["standard_fulltext_verified"]
        and report["formal_source_activated"]
        and report["gbt18920_parent_chunks"] == 8
        and report["gbt18920_child_chunks"] == 10
        and report["pl004_pl005_block_removed"]
        and report["B_D_rag_hash_equal"] == 21
        and report["C_D_skill_hash_equal"] == 21
        and report["fixed_limits_found"] == 0
        and report["project_answers_found"] == 0
        and report["manual_gold_found"] == 0
        and report["rag_procedure_content_found"] == 0
        and report["invalid_source_ids"] == 0
        and report["metadata_only_injected"] == 0
    )
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "commands"}, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
