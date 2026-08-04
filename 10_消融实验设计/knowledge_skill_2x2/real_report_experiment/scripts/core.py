from __future__ import annotations

import csv
import difflib
import hashlib
import html
import json
import os
import random
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
K2 = ROOT.parent
REPO = K2.parents[1]
GOLD = K2 / "gold_governance" / "gold_governance_records_v1.csv"
SCHEMA = ROOT / "schemas" / "audit_output_v1.schema.json"
GROUPS = {
    "A": {"rag_enabled": False, "workflow_enabled": False},
    "B": {"rag_enabled": True, "workflow_enabled": False},
    "C": {"rag_enabled": False, "workflow_enabled": True},
    "D": {"rag_enabled": True, "workflow_enabled": True},
}
GROUP_CONFIGS = {
    "A": "group_A_llm_only.yaml",
    "B": "group_B_rag_only.yaml",
    "C": "group_C_workflow_only.yaml",
    "D": "group_D_rag_workflow.yaml",
}


def ensure_dirs() -> None:
    for rel in [
        "data/report_documents", "manifests", "snapshots", "workflow/procedure_only_skills",
        "runs", "reports", "rag", ".cache",
    ]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(canonical_json(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def norm(text: str) -> str:
    return re.sub(r"[\W_]+", "", text or "").lower()


def text_from_html(value: str) -> str:
    value = re.sub(r"</(p|tr|td|th|h[1-6]|li)>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def report_root(arg: str | None = None) -> Path:
    raw = arg or os.environ.get("EIA_REPORT_ROOT")
    if not raw:
        raise SystemExit("Missing --report-root and EIA_REPORT_ROOT")
    root = Path(raw).resolve()
    if not root.is_dir():
        raise SystemExit(f"Report root does not exist: {root}")
    return root


def gold_rows() -> list[dict[str, str]]:
    return read_csv(GOLD)


def eligible_for_formal(row: dict[str, str]) -> bool:
    return (
        row["gold_review_status"] == "已冻结"
        and row["item_quality_status"] == "有效"
        and bool(row["normalized_judgement_final"].strip())
        and row["taxonomy_review_status"] in {"人工确认", "人工覆盖"}
        and row["basis_verification_status"] in {"已核验", "不需要外部依据"}
        and row["experiment_inclusion"] in {"趋势实验冻结", "正式实验冻结"}
    )


def unique_tasks() -> list[dict[str, str]]:
    seen: set[str] = set()
    out = []
    for row in gold_rows():
        if row["question_id"] not in seen:
            seen.add(row["question_id"])
            out.append(row)
    return out


def discover_report_files(root: Path) -> list[Path]:
    allowed = {".docx", ".pdf", ".md", ".txt", ".html", ".json"}
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in allowed)


def pick_report_file(project_name: str, files: list[Path]) -> tuple[Path | None, float]:
    name = norm(project_name)
    best: tuple[Path | None, float] = (None, 0.0)
    for path in files:
        candidate = norm(path.stem)
        score = difflib.SequenceMatcher(None, name, candidate).ratio()
        if name and name in candidate:
            score = max(score, 0.98)
        if score > best[1]:
            best = (path, score)
    return best


def build_report_manifest(root: Path) -> list[dict[str, Any]]:
    ensure_dirs()
    files = discover_report_files(root)
    preferred: dict[str, Path] = {}
    for path in files:
        key = str(path.with_suffix(""))
        current = preferred.get(key)
        rank = {".json": 5, ".html": 4, ".md": 3, ".txt": 2, ".docx": 1, ".pdf": 0}
        if current is None or rank[path.suffix.lower()] > rank[current.suffix.lower()]:
            preferred[key] = path
    candidates = list(preferred.values())
    projects: dict[str, str] = {}
    for row in unique_tasks():
        projects.setdefault(row["canonical_project_id"], row["project_name"])
    rows = []
    for project_id, project_name in sorted(projects.items()):
        match, score = pick_report_file(project_name, candidates)
        available = bool(match and score >= 0.55)
        rows.append({
            "project_id": project_id,
            "project_name": project_name,
            "report_file_name": match.name if available else "",
            "report_file_type": match.suffix.lower() if available else "",
            "report_relative_identifier": match.relative_to(root).as_posix() if available else "",
            "report_sha256": sha_bytes(match.read_bytes()) if available else "",
            "report_version": "source_snapshot_v1",
            "parse_status": "pending" if available else "not_found",
            "section_index_status": "pending" if available else "not_found",
            "source_available": str(available).lower(),
            "notes": f"fuzzy_match={score:.4f}" if match else "no_candidate",
        })
    write_csv(ROOT / "data" / "report_manifest.csv", rows, list(rows[0]))
    (ROOT / ".cache" / "report_root.txt").write_text(str(root), encoding="utf-8")
    return rows


def source_path(row: dict[str, str], root: Path) -> Path:
    return root / Path(row["report_relative_identifier"])


def parse_source(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    raw_sections: list[tuple[str, str]] = []
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        items = payload if isinstance(payload, list) else payload.get("sections", [payload])
        for index, item in enumerate(items, 1):
            content = item.get("content") or item.get("text") or canonical_json(item)
            raw_sections.append((str(item.get("id") or index), text_from_html(str(content))))
    elif suffix in {".html", ".md", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="replace")
        raw_sections.append(("1", text_from_html(text) if suffix == ".html" else text))
    elif suffix == ".docx":
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in root.iter(f"{namespace}p"):
            text = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t"))
            if text.strip():
                paragraphs.append(text)
        raw_sections.append(("1", "\n".join(paragraphs)))
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            from PyPDF2 import PdfReader
        reader = PdfReader(str(path))
        for index, page in enumerate(reader.pages, 1):
            raw_sections.append((str(index), page.extract_text() or ""))
    else:
        raise ValueError(f"Unsupported source for neutral parser: {suffix}")
    sections = []
    for index, (source_id, text) in enumerate(raw_sections, 1):
        if not text.strip():
            continue
        sections.append({
            "section_id": f"S{index:03d}",
            "title": f"解析片段{source_id}",
            "section_path": f"报告/解析片段{source_id}",
            "text": text,
            "source_location": f"{path.name}#{source_id}",
            "content_sha256": sha_text(text),
        })
    return sections


def parse_reports(root: Path) -> list[dict[str, Any]]:
    manifest = read_csv(ROOT / "data" / "report_manifest.csv")
    logs, updated = [], []
    for row in manifest:
        status = row.copy()
        if row["source_available"] != "true":
            logs.append({"project_id": row["project_id"], "status": "not_found", "error": ""})
            updated.append(status)
            continue
        try:
            sections = parse_source(source_path(row, root))
            document = {
                "project_id": row["project_id"],
                "report_sha256": row["report_sha256"],
                "sections": sections,
            }
            (ROOT / "data" / "report_documents" / f"{row['project_id']}.json").write_text(
                json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            status["parse_status"] = "success"
            status["section_index_status"] = "success" if sections else "empty"
            logs.append({"project_id": row["project_id"], "status": "success", "error": ""})
        except Exception as exc:
            status["parse_status"] = "failed"
            status["section_index_status"] = "failed"
            logs.append({"project_id": row["project_id"], "status": "failed", "error": str(exc)})
        updated.append(status)
    write_csv(ROOT / "data" / "report_manifest.csv", updated, list(updated[0]))
    write_jsonl(ROOT / "reports" / "report_parse_log.jsonl", logs)
    return updated


def chunks_for_task(task: dict[str, str], top_k: int = 3) -> dict[str, Any] | None:
    doc_path = ROOT / "data" / "report_documents" / f"{task['canonical_project_id']}.json"
    if not doc_path.exists():
        return None
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    query_chars = set(norm(task["question"]))
    candidates = []
    for section in doc["sections"]:
        text = section["text"]
        window = text[:12000]
        score = len(query_chars & set(norm(window))) / max(1, len(query_chars))
        candidates.append((score, section, window))
    selected = sorted(candidates, key=lambda x: (-x[0], x[1]["section_id"]))[:top_k]
    chunks = []
    for rank, (_, section, text) in enumerate(selected, 1):
        chunks.append({
            "chunk_id": f"{task['question_id']}_R{rank}",
            "section_path": section["section_path"],
            "source_location": section["source_location"],
            "text": text,
            "content_sha256": sha_text(text),
            "rank": rank,
        })
    base = {
        "question_id": task["question_id"],
        "project_id": task["canonical_project_id"],
        "report_sha256": doc["report_sha256"],
        "context_mode": "frozen_chunks",
        "chunks": chunks,
    }
    base["context_sha256"] = sha_text(canonical_json(base))
    return base


def build_report_contexts() -> list[dict[str, Any]]:
    contexts = [x for task in unique_tasks() if (x := chunks_for_task(task))]
    write_jsonl(ROOT / "snapshots" / "report_contexts.jsonl", contexts)
    return contexts


def freeze_report_contexts() -> str:
    path = ROOT / "snapshots" / "report_contexts.jsonl"
    digest = sha_bytes(path.read_bytes())
    (ROOT / "snapshots" / "report_contexts.sha256").write_text(digest + "\n", encoding="ascii")
    return digest


def safe_knowledge_files() -> list[Path]:
    base = REPO / "03_指南解析_明文标准库"
    return sorted(
        p for p in base.rglob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".json", ".jsonl", ".csv", ".yaml"}
    )


def build_rag_corpus() -> list[dict[str, Any]]:
    whitelist, corpus = [], []
    for index, path in enumerate(safe_knowledge_files(), 1):
        rel = path.relative_to(REPO).as_posix()
        raw = path.read_text(encoding="utf-8", errors="replace")
        whitelist.append({
            "source_id": f"K{index:03d}",
            "relative_path": rel,
            "sha256": sha_bytes(path.read_bytes()),
            "allowed_scope": "国家/广东/佛山/顺德环评知识候选，需人工核验",
        })
        content = re.sub(r"\s+", " ", raw)[:6000]
        corpus.append({
            "chunk_id": f"K{index:03d}_C1",
            "source_name": path.name,
            "source_relative_path": rel,
            "standard_no": "",
            "clause_or_table": "",
            "content": content,
            "content_sha256": sha_text(content),
        })
    write_csv(ROOT / "rag" / "source_whitelist.csv", whitelist, list(whitelist[0]))
    write_jsonl(ROOT / "rag" / "corpus.jsonl", corpus)
    return corpus


def validate_rag_no_leakage() -> list[str]:
    bad = []
    forbidden = [
        "05_QA测试集/", "09_环评审核技能库/", "06_Dify工作流/",
        "10_消融实验设计/", "10_论文写作/", "人工答案", "GPT评分结果",
    ]
    for row in read_jsonl(ROOT / "rag" / "corpus.jsonl"):
        blob = f"{row.get('source_relative_path','')} {row.get('content','')}"
        if any(term in blob for term in forbidden):
            bad.append(row["chunk_id"])
    return bad


def freeze_rag_contexts(top_k: int = 3) -> list[dict[str, Any]]:
    corpus = read_jsonl(ROOT / "rag" / "corpus.jsonl")
    contexts = []
    retrieval_config_hash = sha_text(canonical_json({"algorithm": "char_overlap_v1", "top_k": top_k}))
    for task in unique_tasks():
        q = set(norm(task["question"]))
        scored = []
        for chunk in corpus:
            score = len(q & set(norm(chunk["content"]))) / max(1, len(q))
            scored.append((score, chunk))
        for rank, (score, chunk) in enumerate(sorted(scored, key=lambda x: (-x[0], x[1]["chunk_id"]))[:top_k], 1):
            contexts.append({
                "question_id": task["question_id"],
                "chunk_id": chunk["chunk_id"],
                "rank": rank,
                "source_name": chunk["source_name"],
                "standard_no": chunk["standard_no"],
                "clause_or_table": chunk["clause_or_table"],
                "content": chunk["content"],
                "content_sha256": chunk["content_sha256"],
                "retrieval_score": round(score, 6),
                "retrieval_config_hash": retrieval_config_hash,
            })
    write_jsonl(ROOT / "snapshots" / "rag_contexts.jsonl", contexts)
    return contexts


def procedure_skill(category: str) -> dict[str, Any]:
    rules = {
        "环评投资概算": ["提取总投资、环保投资和报告占比", "复算比例并核对单位与合计"],
        "固体废物控制标准": ["提取固体废物类型、贮存处置方式和报告所列依据", "检查不同废物类别是否均有依据"],
        "噪声排放标准": ["提取位置、功能区、厂界情景和报告所列限值", "核对昼夜、单位及适用边界"],
        "水污染物排放标准": ["提取排水路径、受纳设施、污染物和报告所列依据", "按企业排口与下游设施分层核对"],
        "大气污染物排放标准": ["提取工序、污染物、排放形式和报告所列依据", "检查排放源覆盖和适用条件"],
    }
    steps = rules.get(category, ["提取与问题有关的报告事实", "逐项检查证据充分性"])
    payload = {
        "skill_id": f"procedure_{sha_text(category)[:10]}",
        "task_name": category,
        "required_report_fields": ["项目事实", "报告所列依据", "数值及单位", "证据位置"],
        "procedure_steps": [
            "evidence_extraction", "task_planning", "calculation_or_cross_check",
            "basis_requirement_detection", "evidence_sufficiency_check", "final_synthesis",
        ] + steps,
        "calculation_rules": ["如涉及比例或合计，使用报告原始数值复算并保留计算式"],
        "cross_check_rules": ["跨章节核对同一事实、数值、单位和适用边界是否一致"],
        "insufficient_evidence_policy": "不得猜测；标记证据不足或需人工复核，并说明缺少的证据类型。",
        "output_mapping": {"result": "audit_output_v1"},
        "source_skill_path": "09_环评审核技能库（仅记录来源；实验文件已去知识化）",
    }
    payload["skill_sha256"] = sha_text(canonical_json(payload))
    return payload


def sanitize_skills() -> list[dict[str, Any]]:
    categories = sorted({row["审核类别"] for row in unique_tasks()})
    skills = [procedure_skill(category) for category in categories]
    for skill in skills:
        name = f"{skill['skill_id']}.json"
        (ROOT / "workflow" / "procedure_only_skills" / name).write_text(
            json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return skills


def skill_purity_violations() -> list[dict[str, str]]:
    pattern = re.compile(
        r"\b(?:GB|DB|HJ|PL)\s*\d+|(?:mg/m3|mg/L|dB\s*\(?A\)?|\d+\s*(?:毫克|分贝))|正确应为|应执行.{0,12}(?:标准|限值)",
        re.I,
    )
    violations = []
    for path in sorted((ROOT / "workflow" / "procedure_only_skills").glob("*.json")):
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            violations.append({"file": path.name, "match": match.group(0)})
    return violations


def skill_for(category: str) -> dict[str, Any]:
    for path in (ROOT / "workflow" / "procedure_only_skills").glob("*.json"):
        skill = json.loads(path.read_text(encoding="utf-8"))
        if skill["task_name"] == category:
            return skill
    raise KeyError(category)


def make_manifests() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    report_hash = {r["project_id"]: r["report_sha256"] for r in read_csv(ROOT / "data" / "report_manifest.csv")}
    candidate_ids = {r["question_id"] for r in read_jsonl(K2 / "gold_governance" / "codex_review_70" / "codex_review_70_v1.jsonl")}
    dry_candidates = [r for r in unique_tasks() if r["question_id"] in candidate_ids and report_hash.get(r["canonical_project_id"])]
    preferred = []
    for category in ["环评投资概算", "噪声排放标准", "水污染物排放标准", "大气污染物排放标准"]:
        match = next((r for r in dry_candidates if r["审核类别"] == category), None)
        if match:
            preferred.append(match)
    pilot_rows = []
    for task in preferred[:4]:
        pilot_rows.append({
            "question_id": task["question_id"],
            "project_id": task["canonical_project_id"],
            "audit_category": task["审核类别"],
            "gold_version": task["gold_version"],
            "gold_review_status": task["gold_review_status"],
            "experiment_inclusion": task["experiment_inclusion"],
            "report_sha256": report_hash[task["canonical_project_id"]],
            "include": "true",
            "exclusion_reason": "",
            "not_for_analysis": "true",
        })
    formal_rows = []
    for task in unique_tasks():
        eligible = eligible_for_formal(task) and bool(report_hash.get(task["canonical_project_id"]))
        reasons = []
        if not eligible_for_formal(task):
            reasons.append("not_human_frozen")
        if not report_hash.get(task["canonical_project_id"]):
            reasons.append("report_unavailable")
        formal_rows.append({
            "question_id": task["question_id"],
            "project_id": task["canonical_project_id"],
            "audit_category": task["审核类别"],
            "gold_version": task["gold_version"],
            "gold_review_status": task["gold_review_status"],
            "experiment_inclusion": task["experiment_inclusion"],
            "report_sha256": report_hash.get(task["canonical_project_id"], ""),
            "include": str(eligible).lower(),
            "exclusion_reason": ";".join(reasons),
            "not_for_analysis": "false",
        })
    fields = [
        "question_id", "project_id", "audit_category", "gold_version", "gold_review_status",
        "experiment_inclusion", "report_sha256", "include", "exclusion_reason", "not_for_analysis",
    ]
    write_csv(ROOT / "manifests" / "pilot_manifest.csv", pilot_rows, fields)
    write_csv(ROOT / "manifests" / "formal_manifest.csv", formal_rows, fields)
    return pilot_rows, formal_rows


def validate_manifest(path: Path, allow_dry_run: bool = False) -> list[str]:
    errors = []
    source = {r["question_id"]: r for r in unique_tasks()}
    for row in read_csv(path):
        if row["include"] != "true":
            continue
        gold = source[row["question_id"]]
        if allow_dry_run and row["not_for_analysis"] == "true":
            continue
        if not eligible_for_formal(gold):
            errors.append(f"{row['question_id']}: not human frozen")
    return errors


def group_hashes(question_id: str) -> dict[str, dict[str, Any]]:
    task = next(r for r in unique_tasks() if r["question_id"] == question_id)
    report = next(r for r in read_jsonl(ROOT / "snapshots" / "report_contexts.jsonl") if r["question_id"] == question_id)
    rag_rows = [r for r in read_jsonl(ROOT / "snapshots" / "rag_contexts.jsonl") if r["question_id"] == question_id]
    skill = skill_for(task["审核类别"])
    common_input = {"question_id": question_id, "question": task["question"], "project_id": task["canonical_project_id"]}
    common_hash = sha_text(canonical_json(common_input))
    rag_hash = sha_text(canonical_json(rag_rows))
    prompt_hash = sha_bytes((ROOT / "prompts" / "common_system_prompt.txt").read_bytes())
    schema_hash = sha_bytes(SCHEMA.read_bytes())
    model_hash = sha_bytes((ROOT / "configs" / "common_model.yaml").read_bytes())
    out = {}
    for group, switches in GROUPS.items():
        out[group] = {
            "common_input_hash": common_hash,
            "report_context_hash": report["context_sha256"],
            "rag_context_hash": rag_hash if switches["rag_enabled"] else None,
            "skill_hash": skill["skill_sha256"] if switches["workflow_enabled"] else None,
            "output_schema_hash": schema_hash,
            "model_config_hash": model_hash,
            "prompt_hash": prompt_hash,
            **switches,
        }
    return out


def validate_group_isolation(question_ids: list[str]) -> list[str]:
    errors = []
    if skill_purity_violations():
        errors.append("procedure-only skill contains forbidden knowledge")
    if validate_rag_no_leakage():
        errors.append("RAG corpus leakage detected")
    for qid in question_ids:
        h = group_hashes(qid)
        if len({h[g]["common_input_hash"] for g in GROUPS}) != 1:
            errors.append(f"{qid}: common input differs")
        if len({h[g]["report_context_hash"] for g in GROUPS}) != 1:
            errors.append(f"{qid}: report context differs")
        if h["B"]["rag_context_hash"] != h["D"]["rag_context_hash"]:
            errors.append(f"{qid}: B/D RAG differs")
        if h["C"]["skill_hash"] != h["D"]["skill_hash"]:
            errors.append(f"{qid}: C/D skill differs")
        if h["A"]["rag_context_hash"] or h["C"]["rag_context_hash"]:
            errors.append(f"{qid}: RAG leaked to A/C")
        if h["A"]["skill_hash"] or h["B"]["skill_hash"]:
            errors.append(f"{qid}: workflow leaked to A/B")
        if len({h[g]["output_schema_hash"] for g in GROUPS}) != 1:
            errors.append(f"{qid}: schema differs")
        if len({h[g]["model_config_hash"] for g in GROUPS}) != 1:
            errors.append(f"{qid}: model config differs")
    return errors


def build_run_matrix(stage: str = "dry_run") -> list[dict[str, Any]]:
    manifest = ROOT / "manifests" / ("pilot_manifest.csv" if stage == "dry_run" else "formal_manifest.csv")
    errors = validate_manifest(manifest, allow_dry_run=stage == "dry_run")
    if errors:
        raise SystemExit("\n".join(errors))
    repeats = 1 if stage == "dry_run" else 2
    included = [item for item in read_csv(manifest) if item["include"] == "true"]
    if stage == "formal" and len(included) < 18:
        raise SystemExit(
            f"Formal trend experiment blocked: requires at least 18 human-frozen items, got {len(included)}"
        )
    rows = []
    for item in included:
        for group in GROUPS:
            for repeat in range(1, repeats + 1):
                rows.append({
                    "experiment_id": f"{stage}_v1",
                    "run_id": f"{stage}_{item['question_id']}_{group}_r{repeat}",
                    "question_id": item["question_id"],
                    "project_id": item["project_id"],
                    "audit_category": item["audit_category"],
                    "group": group,
                    "repeat": repeat,
                    "not_for_analysis": item["not_for_analysis"],
                })
    write_jsonl(ROOT / "manifests" / f"{stage}_run_matrix.jsonl", rows)
    return rows


def validate_output(output: dict[str, Any]) -> list[str]:
    try:
        import jsonschema
        jsonschema.validate(output, json.loads(SCHEMA.read_text(encoding="utf-8")))
        return []
    except Exception as exc:
        return [str(exc)]


def mock_output(question_id: str, group: str, report: dict[str, Any]) -> dict[str, Any]:
    first = report["chunks"][0] if report["chunks"] else {"source_location": "", "text": ""}
    return {
        "schema_version": "audit_output_v1",
        "question_id": question_id,
        "judgement": "需人工复核",
        "judgement_confidence": 0.0,
        "report_evidence": [{
            "evidence_id": "E1",
            "source_location": first["source_location"],
            "evidence_text": first["text"][:160],
            "supports": "不确定性",
        }],
        "basis_status": "unavailable" if group in {"A", "C"} else "insufficient",
        "cited_bases": [],
        "identified_issues": [{
            "issue_id": "I1",
            "issue_type": "其他",
            "issue_description": "mock后端仅验证框架，未执行模型语义判断。",
            "linked_evidence_ids": ["E1"],
            "linked_basis_ids": [],
        }],
        "suggested_revision": "",
        "uncertainty_reason": "框架dry-run的mock输出，不可用于分析。",
        "abstain": True,
    }


def run_group(group: str, backend: str = "mock") -> list[dict[str, Any]]:
    if group not in GROUPS:
        raise SystemExit(f"Unknown group {group}")
    matrix_path = ROOT / "manifests" / "dry_run_run_matrix.jsonl"
    matrix = [r for r in read_jsonl(matrix_path) if r["group"] == group]
    if backend != "mock":
        raise SystemExit("No paid/API backend is configured; use --backend mock")
    contexts = {r["question_id"]: r for r in read_jsonl(ROOT / "snapshots" / "report_contexts.jsonl")}
    outputs = []
    for run in matrix:
        hashes = group_hashes(run["question_id"])[group]
        report = contexts[run["question_id"]]
        output = mock_output(run["question_id"], group, report)
        errors = validate_output(output)
        exp_dir = ROOT / "runs" / run["experiment_id"]
        for part in ["raw_outputs", "validated_outputs", "traces", "metadata"]:
            (exp_dir / part).mkdir(parents=True, exist_ok=True)
        raw_path = exp_dir / "raw_outputs" / f"{run['run_id']}.json"
        valid_path = exp_dir / "validated_outputs" / f"{run['run_id']}.json"
        raw_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        if not errors:
            valid_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        if GROUPS[group]["workflow_enabled"]:
            trace = {
                "run_id": run["run_id"],
                "nodes": [
                    "evidence_extraction", "task_planning", "calculation_or_cross_check",
                    "basis_requirement_detection", "evidence_sufficiency_check", "final_synthesis",
                ],
                "scored": False,
            }
            (exp_dir / "traces" / f"{run['run_id']}.json").write_text(
                json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        metadata = {
            **run,
            "model_name": "MOCK_NO_API",
            "model_version": "framework_only",
            **hashes,
            "question_hash": hashes["common_input_hash"],
            "report_sha256": report["report_sha256"],
            "input_tokens": 0,
            "output_tokens": 0,
            "schema_valid": not errors,
            "run_status": "success" if not errors else "invalid_json",
            "output_file": valid_path.relative_to(ROOT).as_posix() if not errors else "",
        }
        (exp_dir / "metadata" / f"{run['run_id']}.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        outputs.append(metadata)
    return outputs


def blind_outputs(seed: int = 20260729) -> list[dict[str, Any]]:
    exp_dir = ROOT / "runs" / "dry_run_v1"
    items = []
    for path in sorted((exp_dir / "validated_outputs").glob("*.json")):
        output = json.loads(path.read_text(encoding="utf-8"))
        run_id = path.stem
        metadata = json.loads((exp_dir / "metadata" / f"{run_id}.json").read_text(encoding="utf-8"))
        items.append({
            "blinded_output_id": "",
            "question_id": output["question_id"],
            "repeat": metadata["repeat"],
            "output": output,
            "not_for_analysis": metadata["not_for_analysis"],
        })
    random.Random(seed).shuffle(items)
    for index, item in enumerate(items, 1):
        item["blinded_output_id"] = f"BLIND{index:04d}"
    write_jsonl(ROOT / "runs" / "dry_run_v1" / "blinded_outputs.jsonl", items)
    return items


def build_scoring_packets() -> list[dict[str, Any]]:
    tasks = {r["question_id"]: r for r in unique_tasks()}
    contexts = {r["question_id"]: r for r in read_jsonl(ROOT / "snapshots" / "report_contexts.jsonl")}
    packets = []
    for item in read_jsonl(ROOT / "runs" / "dry_run_v1" / "blinded_outputs.jsonl"):
        task = tasks[item["question_id"]]
        packets.append({
            "blinded_output_id": item["blinded_output_id"],
            "question_id": item["question_id"],
            "question": task["question"],
            "frozen_report_context": contexts[item["question_id"]]["chunks"],
            "human_gold": {
                "judgement": task["normalized_judgement_final"],
                "answer": task["answer"],
                "basis": task["source_basis"],
                "gold_review_status": task["gold_review_status"],
            },
            "model_output": item["output"],
            "score_dimensions": {
                "judgement_accuracy": 30,
                "report_evidence": 25,
                "basis_accuracy_applicability": 25,
                "analysis_revision_completeness": 20,
            },
            "not_for_analysis": item["not_for_analysis"],
        })
    write_jsonl(ROOT / "runs" / "dry_run_v1" / "gpt_scoring_packets.jsonl", packets)
    return packets


def programmatic_total(score: dict[str, Any]) -> float:
    return sum(float(score[key]) for key in [
        "judgement_accuracy", "report_evidence",
        "basis_accuracy_applicability", "analysis_revision_completeness",
    ])


def interaction(a: float, b: float, c: float, d: float) -> float:
    return d - c - b + a


def readiness_report() -> str:
    manifest = read_csv(ROOT / "data" / "report_manifest.csv")
    pilot = read_csv(ROOT / "manifests" / "pilot_manifest.csv")
    formal = read_csv(ROOT / "manifests" / "formal_manifest.csv")
    parse_failures = [r["project_id"] for r in manifest if r["parse_status"] != "success"]
    frozen = sum(eligible_for_formal(r) for r in unique_tasks())
    isolation_errors = validate_group_isolation([r["question_id"] for r in pilot if r["include"] == "true"])
    dry_meta = list((ROOT / "runs" / "dry_run_v1" / "metadata").glob("*.json"))
    found = sum(r["source_available"] == "true" for r in manifest)
    lines = [
        "# 真实报告 A/B/C/D 实验就绪报告",
        "",
        "> 框架已完成不等于正式实验已完成；本报告未使用收费API、未生成论文实验结果。",
        "",
        f"- 真实项目标识数：{len(manifest)}；已定位报告：{found}",
        f"- 报告解析成功：{sum(r['parse_status']=='success' for r in manifest)}；失败或未找到：{len(parse_failures)}",
        f"- 解析失败/未找到项目：{', '.join(parse_failures) if parse_failures else '无'}",
        f"- A组基础输入：{'就绪' if pilot else '未就绪'}",
        f"- B组RAG泄漏检查：{'通过' if not validate_rag_no_leakage() else '失败'}",
        f"- C组Workflow去知识化：{'通过' if not skill_purity_violations() else '失败'}",
        f"- B/D RAG一致、C/D Skill一致、四组报告上下文一致：{'通过' if not isolation_errors else '失败'}",
        f"- 统一JSON Schema：{'可用' if SCHEMA.exists() else '缺失'}",
        f"- 当前满足人工冻结条件题数：{frozen}",
        f"- dry-run题数：{sum(r['include']=='true' for r in pilot)}；运行记录：{len(dry_meta)}",
        f"- 当前能否dry-run：{'能' if pilot and not isolation_errors else '不能'}",
        f"- 当前能否运行144次趋势实验：{'能' if frozen >= 18 else '不能'}",
        "",
        "## 阻塞项",
        "",
        f"- 人工冻结题不足18题（当前{frozen}题）。",
        f"- 正式清单可纳入题数：{sum(r['include']=='true' for r in formal)}。",
        "- common_model.yaml 尚未配置真实模型名称、版本和调用适配器。",
        "- RAG白名单条目仍需人工确认其正式性、现行性和地域适用性。",
        "",
        "## 必须由用户人工完成",
        "",
        "1. 完成至少18题双人复核/裁决并冻结金标与题目分类。",
        "2. 人工核验RAG法规来源和标准版本，确认允许进入正式索引。",
        "3. 指定同一模型版本与API配置，并授权小规模收费调用。",
        "4. 对GPT评分结果抽查；正式实验前再次运行全部隔离验证。",
        "",
        "本轮仅完成框架、单元测试、mock dry-run和就绪判断；未运行144次趋势实验。",
    ]
    text = "\n".join(lines) + "\n"
    (ROOT / "reports" / "final_real_report_experiment_readiness.md").write_text(text, encoding="utf-8")
    return text
