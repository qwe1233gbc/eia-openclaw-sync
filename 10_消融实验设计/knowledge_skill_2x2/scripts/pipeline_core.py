from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[2]
SOURCE_WORKBOOK = PROJECT_ROOT / "05_QA测试集" / "四大类问答对_最终版.xlsx"
SOURCE_JSON = ROOT / ".cache" / "source_questions.json"
TAXONOMY_CSV = ROOT / "taxonomy" / "question_taxonomy_210.csv"
TAXONOMY_JSONL = ROOT / "taxonomy" / "question_taxonomy_210.jsonl"

COGNITIVE_LEVELS = ["L1_understanding", "L2_application", "L3_analysis"]
AUDIT_DOMAINS = [
    "industry_classification",
    "environmental_investment",
    "environmental_quality_data",
    "water_emission_standard",
    "air_emission_standard",
    "noise_emission_standard",
    "solid_waste_standard",
]
REASONING_TYPES = [
    "factual_extraction",
    "quantitative_verification",
    "rule_applicability",
    "consistency_comparison",
    "multi_evidence_synthesis",
]
FUNCTIONAL_CAPABILITIES = [
    "report_grounding",
    "basis_grounding",
    "numerical_accuracy",
    "procedural_reasoning",
    "evidence_integration",
]
DEPENDENCY_LEVELS = ["low", "medium", "high"]
EVIDENCE_SPANS = [
    "single_field",
    "single_section",
    "cross_section",
    "report_plus_external",
]

TEMPLATE_DEFAULTS: dict[str, dict[str, Any]] = {
    "国民经济行业分类": {
        "audit_domain": "industry_classification",
        "cognitive_level": "L3_analysis",
        "reasoning_type": "multi_evidence_synthesis",
        "primary_functional_capability": "evidence_integration",
        "secondary_capabilities": ["report_grounding", "basis_grounding"],
        "knowledge_dependency": "high",
        "workflow_dependency": "high",
        "evidence_span": "cross_section",
    },
    "环评投资概算": {
        "audit_domain": "environmental_investment",
        "cognitive_level": "L2_application",
        "reasoning_type": "quantitative_verification",
        "primary_functional_capability": "numerical_accuracy",
        "secondary_capabilities": ["report_grounding", "procedural_reasoning"],
        "knowledge_dependency": "low",
        "workflow_dependency": "medium",
        "evidence_span": "cross_section",
    },
    "环境质量数据引用": {
        "audit_domain": "environmental_quality_data",
        "cognitive_level": "L3_analysis",
        "reasoning_type": "consistency_comparison",
        "primary_functional_capability": "evidence_integration",
        "secondary_capabilities": ["report_grounding", "basis_grounding"],
        "knowledge_dependency": "high",
        "workflow_dependency": "high",
        "evidence_span": "report_plus_external",
    },
    "水污染物排放标准": {
        "audit_domain": "water_emission_standard",
        "cognitive_level": "L3_analysis",
        "reasoning_type": "rule_applicability",
        "primary_functional_capability": "basis_grounding",
        "secondary_capabilities": ["report_grounding", "procedural_reasoning"],
        "knowledge_dependency": "high",
        "workflow_dependency": "high",
        "evidence_span": "report_plus_external",
    },
    "大气污染物排放标准": {
        "audit_domain": "air_emission_standard",
        "cognitive_level": "L3_analysis",
        "reasoning_type": "multi_evidence_synthesis",
        "primary_functional_capability": "basis_grounding",
        "secondary_capabilities": ["report_grounding", "evidence_integration"],
        "knowledge_dependency": "high",
        "workflow_dependency": "high",
        "evidence_span": "report_plus_external",
    },
    "噪声排放标准": {
        "audit_domain": "noise_emission_standard",
        "cognitive_level": "L2_application",
        "reasoning_type": "rule_applicability",
        "primary_functional_capability": "basis_grounding",
        "secondary_capabilities": ["report_grounding"],
        "knowledge_dependency": "high",
        "workflow_dependency": "medium",
        "evidence_span": "report_plus_external",
    },
    "固体废物控制标准": {
        "audit_domain": "solid_waste_standard",
        "cognitive_level": "L2_application",
        "reasoning_type": "rule_applicability",
        "primary_functional_capability": "basis_grounding",
        "secondary_capabilities": ["report_grounding"],
        "knowledge_dependency": "high",
        "workflow_dependency": "medium",
        "evidence_span": "report_plus_external",
    },
}

VALID_MANUAL_JUDGEMENTS = {
    "无误",
    "存在错误",
    "存在缺漏",
    "需复核",
    "正确",
    "不正确",
    "需修正",
    "无法判断",
    "证据不足",
}
PILOT_PROJECTS = ["PL001", "PL002", "PL003", "PL004", "PL020", "PL026"]
PILOT_DOMAINS = {
    "water_emission_standard",
    "air_emission_standard",
    "noise_emission_standard",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            cooked = {
                key: json.dumps(value, ensure_ascii=False)
                if isinstance(value, (list, dict))
                else value
                for key, value in row.items()
            }
            writer.writerow(cooked)


def load_source_records() -> list[dict[str, Any]]:
    payload = read_json(SOURCE_JSON)
    return payload["records"]


def source_category(row: dict[str, Any]) -> str:
    category = str(row.get("审核类别") or "").strip()
    if category in TEMPLATE_DEFAULTS:
        return category
    module = str(row.get("audit_module") or "")
    checks = [
        ("国民经济行业", "国民经济行业分类"),
        ("投资", "环评投资概算"),
        ("环境质量", "环境质量数据引用"),
        ("水污染物", "水污染物排放标准"),
        ("大气污染物", "大气污染物排放标准"),
        ("噪声", "噪声排放标准"),
        ("固体废物", "固体废物控制标准"),
    ]
    for needle, fallback in checks:
        if needle in module:
            return fallback
    raise ValueError(f"无法映射审核类别: {row.get('question_id')} / {module!r}")


def classify_row(row: dict[str, Any]) -> dict[str, Any]:
    category = source_category(row)
    result = {
        "question_id": str(row.get("question_id") or "").strip(),
        "project_id": str(row.get("canonical_project_id") or "").strip(),
        **TEMPLATE_DEFAULTS[category],
        "template_default_used": True,
        "override_reason": "",
        "classification_status": "auto_default",
        "taxonomy_version": "v1",
        "source_category": category,
        "source_manual_check": bool(row.get("manual_check")),
        "source_manual_judgement": str(row.get("人工判断") or "").strip(),
        "source_needs_human_review": str(row.get("是否需要人工复核") or "").strip(),
    }
    manual = result["source_manual_judgement"]
    review_reasons: list[str] = []
    if not manual:
        review_reasons.append("人工判断为空")
    elif manual not in VALID_MANUAL_JUDGEMENTS:
        review_reasons.append("人工判断格式异常")
    if result["source_needs_human_review"] == "是":
        review_reasons.append("源工作簿标记需人工复核")
    result["taxonomy_review_required"] = bool(review_reasons)
    result["taxonomy_review_reason"] = "；".join(review_reasons)
    return result


def classify_all(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [classify_row(row) for row in records]
    ids = [row["question_id"] for row in rows]
    if len(rows) != 210:
        raise ValueError(f"预期210题，实际{len(rows)}题")
    if any(not value for value in ids):
        raise ValueError("question_id存在空值")
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"question_id重复: {duplicates}")
    return rows


def taxonomy_by_id() -> dict[str, dict[str, Any]]:
    return {row["question_id"]: row for row in read_jsonl(TAXONOMY_JSONL)}


def source_by_id() -> dict[str, dict[str, Any]]:
    return {str(row["question_id"]): row for row in load_source_records()}


def distribution(rows: list[dict[str, Any]], field: str) -> Counter:
    return Counter(str(row.get(field) or "") for row in rows)


def markdown_counter(title: str, counts: Counter) -> str:
    lines = [f"## {title}", "", "| 标签 | 题数 |", "|---|---:|"]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(counts.items()))
    return "\n".join(lines)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def programmatic_total(evaluation: dict[str, Any]) -> int:
    universal = sum(int(value) for value in evaluation["universal_scores"].values())
    functional = sum(int(value) for value in evaluation["functional_scores"].values())
    return universal + functional


def five_band(score: float) -> int:
    if score >= 90:
        return 5
    if score >= 70:
        return 4
    if score >= 50:
        return 3
    if score >= 30:
        return 2
    return 1


def cohen_kappa(a: list[Any], b: list[Any], weighted: bool = False) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("评分向量必须等长且非空")
    labels = sorted(set(a) | set(b))
    n = len(a)
    ia = {label: idx for idx, label in enumerate(labels)}
    matrix = [[0.0 for _ in labels] for _ in labels]
    for x, y in zip(a, b):
        matrix[ia[x]][ia[y]] += 1
    row = [sum(values) for values in matrix]
    col = [sum(matrix[i][j] for i in range(len(labels))) for j in range(len(labels))]
    if weighted:
        denominator = max(1, len(labels) - 1) ** 2
        weights = [
            [((i - j) ** 2) / denominator for j in range(len(labels))]
            for i in range(len(labels))
        ]
        observed = sum(weights[i][j] * matrix[i][j] for i in range(len(labels)) for j in range(len(labels))) / n
        expected = sum(
            weights[i][j] * row[i] * col[j]
            for i in range(len(labels))
            for j in range(len(labels))
        ) / (n * n)
        return 1.0 if expected == 0 else 1 - observed / expected
    observed = sum(matrix[i][i] for i in range(len(labels))) / n
    expected = sum(row[i] * col[i] for i in range(len(labels))) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def fleiss_kappa(ratings: list[list[Any]]) -> float:
    if not ratings or not ratings[0]:
        raise ValueError("评分矩阵不能为空")
    n_raters = len(ratings[0])
    if n_raters < 2 or any(len(row) != n_raters for row in ratings):
        raise ValueError("每题必须具有相同且至少2个评分")
    labels = sorted({value for row in ratings for value in row})
    counts = [[row.count(label) for label in labels] for row in ratings]
    p_i = [
        (sum(value * value for value in row) - n_raters)
        / (n_raters * (n_raters - 1))
        for row in counts
    ]
    p_bar = statistics.mean(p_i)
    totals = [sum(row[j] for row in counts) for j in range(len(labels))]
    denom = len(ratings) * n_raters
    p_e = sum((value / denom) ** 2 for value in totals)
    return 1.0 if p_e == 1 else (p_bar - p_e) / (1 - p_e)


def pearson(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or len(a) < 2:
        raise ValueError("至少需要两个配对分数")
    ma, mb = statistics.mean(a), statistics.mean(b)
    numerator = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    denominator = math.sqrt(
        sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)
    )
    return 0.0 if denominator == 0 else numerator / denominator


def effect_components(a: float, b: float, c: float, d: float) -> dict[str, float]:
    return {
        "K_main_effect": ((b - a) + (d - c)) / 2,
        "S_main_effect": ((c - a) + (d - b)) / 2,
        "interaction": d - c - b + a,
    }


def bootstrap_mean_ci(values: list[float], seed: int = 20260729, repeats: int = 5000) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = [
        statistics.mean(rng.choices(values, k=len(values))) for _ in range(repeats)
    ]
    means.sort()
    return means[int(repeats * 0.025)], means[int(repeats * 0.975)]


def scientific_direction(k: float, s: float, interaction: float, tolerance: float = 1.0) -> str:
    k_effective = k > tolerance
    s_effective = s > tolerance
    if k_effective and s_effective and interaction > tolerance:
        return "synergy"
    if k_effective and s_effective and interaction < -tolerance:
        return "antagonism"
    if k_effective and s_effective:
        return "additive"
    if k_effective:
        return "knowledge_only"
    if s_effective:
        return "workflow_only"
    return "neither"
