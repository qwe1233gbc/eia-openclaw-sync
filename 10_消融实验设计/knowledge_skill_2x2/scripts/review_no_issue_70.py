#!/usr/bin/env python3
"""Codex candidate review of the 70 source-marked no-review/positive QA pairs.

This never writes normalized_judgement_final or gold_review_status.  It reviews
the evidence package using the repository prompt principles and the applicable
EIA skills, and emits a separate, auditable candidate opinion.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from governance_core import OUT, RECORDS_CSV, ROOT, write_csv, write_jsonl

REVIEW_DIR = OUT / "codex_review_70"
RESULT_CSV = REVIEW_DIR / "codex_review_70_v1.csv"
RESULT_JSONL = REVIEW_DIR / "codex_review_70_v1.jsonl"

OFFICIAL_BASIS = {
    "噪声排放标准": [
        "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/wlhj/hjzspfbz/200809/t20080918_128936.htm",
    ],
    "固体废物控制标准": [
        "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/gthw/gtfwwrkzbz/202302/t20230224_1017500.shtml",
        "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/gthw/gtfwwrkzbz/202012/t20201218_813927.shtml",
        "https://www.mee.gov.cn/xxgk2018/xxgk/xxgk02/202411/t20241129_1097685.html",
    ],
    "水污染物排放标准": [
        "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/shjbh/swrwpfbz/200307/t20030701_66529.shtml",
        "https://www.mee.gov.cn/xxgk2018/xxgk/xxgk01/202512/W020251209362803739215.pdf",
    ],
    "大气污染物排放标准": [
        "https://gdee.gd.gov.cn/attachment/0/493/493201/3964836.pdf",
        "https://www.mee.gov.cn/hdjl/cjwt/202509/t20250915_1130206.shtml",
    ],
    "环评投资概算": [],
}

RESULT_FIELDS = [
    "question_id", "canonical_project_id", "project_name", "审核类别",
    "question", "answer", "evidence", "source_basis",
    "source_manual_judgement", "source_needs_human_review",
    "codex_review_status", "recommended_gold_candidate",
    "question_validity", "answer_evidence_alignment",
    "standard_or_calculation_check", "basis_verification_candidate",
    "issue_tags", "codex_review_note", "calculation_detail",
    "source_report_folder", "source_report_match_score",
    "full_report_context_check", "official_basis_urls",
    "codex_review_is_final", "gold_freeze_authorized",
]


def load_records() -> list[dict[str, str]]:
    with RECORDS_CSV.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def select_70(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = [
        r for r in rows
        if r["raw_manual_judgement"] in {"正确", "无误"}
        and r["是否需要人工复核"] == "否"
        and r["item_quality_status"] == "有效"
        and r["evidence_sufficiency"] in {"充分", "部分充分"}
        and r["basis_verification_status"] in {"已核验", "部分核验", "不需要外部依据"}
    ]
    if len(selected) != 70:
        raise ValueError(f"Expected 70 selected records, got {len(selected)}")
    return selected


def plain_report_text(folder: Path) -> str:
    parts = []
    for path in folder.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, list):
            for chunk in payload:
                if isinstance(chunk, dict):
                    parts.append(str(chunk.get("content", "")))
    text = html.unescape(" ".join(parts))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def report_match(project: str, report_root: Path | None) -> tuple[str, str, str]:
    if not report_root or not report_root.exists():
        return "", "", "未提供完整报告目录；仅审核QA证据包"
    folders = [p for p in report_root.iterdir() if p.is_dir()]
    if not folders:
        return "", "", "完整报告目录为空"
    scored = []
    for folder in folders:
        clean = re.sub(r"^\d+_", "", folder.name).split("_01_")[0]
        score = difflib.SequenceMatcher(None, project, clean).ratio()
        scored.append((score, folder))
    score, folder = max(scored, key=lambda x: x[0])
    if score < 0.96:
        return "", f"{score:.3f}", "未可靠匹配完整报告"
    return folder.name, f"{score:.3f}", plain_report_text(folder)


def investment_review(row: dict[str, str]) -> dict[str, str]:
    text = f"{row['answer']} {row['evidence']}"
    patterns = {
        "total": r"总投资(?:为)?\s*(\d+(?:\.\d+)?)\s*万元",
        "environmental": r"环保投资(?:为)?\s*(\d+(?:\.\d+)?)\s*万元",
        "reported": r"环保投资占比(?:为)?\s*(\d+(?:\.\d+)?)\s*%",
        "sum": r"分项投资合计(?:为)?\s*(\d+(?:\.\d+)?)\s*万元",
    }
    values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        values[key] = float(match.group(1)) if match else None
    if None in values.values() or not values["total"]:
        return {
            "codex_review_status": "证据包不足",
            "recommended_gold_candidate": "证据不足",
            "question_validity": "有效",
            "answer_evidence_alignment": "部分一致",
            "standard_or_calculation_check": "待人工复核",
            "basis_verification_candidate": "不需要外部依据",
            "issue_tags": "missing_numeric_evidence",
            "codex_review_note": "总投资、环保投资、填报占比或分项合计未能从证据包完整提取。",
            "calculation_detail": json.dumps(values, ensure_ascii=False),
        }
    calculated = values["environmental"] / values["total"] * 100
    ratio_ok = abs(calculated - values["reported"]) <= 0.01
    sum_ok = abs(values["environmental"] - values["sum"]) <= 1e-9
    status = "通过候选" if ratio_ok and sum_ok else "存在错误"
    candidate = "无误" if status == "通过候选" else "存在错误"
    return {
        "codex_review_status": status,
        "recommended_gold_candidate": candidate,
        "question_validity": "有效",
        "answer_evidence_alignment": "一致" if status == "通过候选" else "不一致",
        "standard_or_calculation_check": "计算正确" if status == "通过候选" else "计算错误",
        "basis_verification_candidate": "不需要外部依据",
        "issue_tags": "" if status == "通过候选" else "numeric_mismatch",
        "codex_review_note": "总投资、环保投资、填报占比和分项合计均由证据包支持，并完成独立复算。" if status == "通过候选"
        else "复算占比或分项合计与报告填报值不一致。",
        "calculation_detail": (
            f"{values['environmental']:g}÷{values['total']:g}×100%={calculated:.6f}%；"
            f"报告={values['reported']:g}%；分项合计={values['sum']:g}万元"
        ),
    }


def noise_review(row: dict[str, str], full_text: str) -> dict[str, str]:
    evidence = row["evidence"]
    qid = row["question_id"]
    answer = row["answer"]
    zone_in_evidence = bool(
        re.search(r"(声环境功能区划|属于\s*[234]\s*类(?:声环境)?(?:功能区|区域)|\d{4}.+工业区片区)", evidence)
    )
    limit_match = re.search(r"([234])类.*?昼间[≤小于等于]*\s*(\d+).*?夜间[≤小于等于]*\s*(\d+)", evidence)
    expected = {"2": ("60", "50"), "3": ("65", "55"), "4": ("70", "55")}
    limits_ok = bool(limit_match and expected.get(limit_match.group(1)) == (limit_match.group(2), limit_match.group(3)))
    report_context = bool(
        full_text and re.search(r"(属于|执行).{0,20}[234]\s*类.{0,20}(声环境功能区|区域)", full_text)
    )
    if qid == "PL004_Emission_噪声" and zone_in_evidence and limits_ok:
        status, candidate = "通过候选", "无误"
        alignment, check = "一致", "标准类别与昼夜限值正确"
        tags = ""
        note = "证据包同时给出佛山市声环境功能区划、项目片区、3类厂界标准及65/55 dB(A)限值。"
    else:
        status, candidate = "证据包不足", "证据不足"
        alignment, check = "部分一致", "限值可核对，但功能区适用依据不足"
        tags = "missing_function_zone_evidence"
        note = (
            "证据包主要复述报告采用的GB12348类别，未提供足以独立确认该类别的声功能区划依据；"
            "因此不能仅凭同一句报告表述确认“选取正确”。"
        )
        if not limits_ok:
            tags += ";missing_limit_evidence"
            note += " 昼夜限值也未在证据包中完整出现。"
    return {
        "codex_review_status": status,
        "recommended_gold_candidate": candidate,
        "question_validity": "有效",
        "answer_evidence_alignment": alignment,
        "standard_or_calculation_check": check,
        "basis_verification_candidate": "已核验标准文本；项目功能区待核验" if status != "通过候选" else "部分核验",
        "issue_tags": tags,
        "codex_review_note": note,
        "calculation_detail": "",
        "_full_report_context": "完整报告中检出声功能区上下文" if report_context else "完整报告中未自动检出声功能区上下文",
    }


def water_review(row: dict[str, str]) -> dict[str, str]:
    qid = row["question_id"]
    evidence = row["evidence"]
    answer = row["answer"]
    ids = set(re.findall(r"(?:DB|GB)[A-Za-z]?\s*\d*/?\d*(?:-\d+)?", evidence, re.I))
    if qid == "PL003_Emission_水污":
        status, candidate = "待人工复核", "需人工复核"
        tags = "rural_treatment_facility_applicability;external_mapping_unverified"
        note = "农村生活污水处理站是否适用GB18918一级B及其现行尾水要求，不能仅由报告自述确定。"
    else:
        status, candidate = "基本通过_需补外部依据", "需人工复核"
        tags = "wwtp_mapping_unverified;basis_version_scope"
        note = (
            "企业排口—污水处理厂—尾水标准的层次与证据包基本一致；"
            "但污水处理厂纳管范围、尾水受纳关系及GB18918现行修改单尚缺逐项目官方依据。"
        )
    if qid in {"PL004_Emission_水污", "PL005_Emission_水污", "PL011_Emission_水污"}:
        tags += ";answer_adds_claim_outside_evidence"
        note += " 答案还加入冷却水/回用处理判断，但当前证据字段未提供相应原文。"
    if qid in {"PL008_Emission_水污", "PL009_Emission_水污"}:
        tags += ";standard_name_or_number_typo"
        note += " 报告标准名称或编号存在可辨识的书写瑕疵，答案已指出但仍需修订报告。"
    return {
        "codex_review_status": status,
        "recommended_gold_candidate": candidate,
        "question_validity": "有效",
        "answer_evidence_alignment": "基本一致",
        "standard_or_calculation_check": "标准层次基本合理，外部适用关系未闭环",
        "basis_verification_candidate": "部分核验",
        "issue_tags": tags,
        "codex_review_note": note,
        "calculation_detail": f"证据中识别标准：{'、'.join(sorted(ids))}",
    }


def air_review(row: dict[str, str]) -> dict[str, str]:
    qid = row["question_id"]
    if qid == "PL002_Emission_大气":
        status, candidate = "证据包不足", "证据不足"
        tags = "pollution_source_coverage_not_evidenced"
        note = "证据仅给出挤出/抽检非甲烷总烃标准，不能支撑答案对粉尘、臭气和厂区内VOCs“全部覆盖”的结论。"
    elif qid in {"PL028_Emission_大气", "PL029_Emission_大气"}:
        status, candidate = "证据包不足", "证据不足"
        tags = "answer_adds_pollutants_limits_and_stack_height"
        note = "答案加入特征污染物、具体限值和24m排气筒折算等关键信息，但当前证据字段未完整提供这些事实。"
    else:
        status, candidate = "基本通过_需补外部依据", "需人工复核"
        tags = "some_external_limits_not_officially_linked"
        note = (
            "工序—污染物—排放形式—标准的对应关系与证据包基本一致；"
            "但部分DB44/27限值、行业标准表格或项目污染源完整性仍需正式文本/完整工程分析闭环。"
        )
    return {
        "codex_review_status": status,
        "recommended_gold_candidate": candidate,
        "question_validity": "有效",
        "answer_evidence_alignment": "部分一致" if status == "证据包不足" else "基本一致",
        "standard_or_calculation_check": "部分核验",
        "basis_verification_candidate": "部分核验",
        "issue_tags": tags,
        "codex_review_note": note,
        "calculation_detail": "",
    }


def solid_review(row: dict[str, str]) -> dict[str, str]:
    evidence = row["evidence"]
    missing_terms = ("未检出", "未发现", "未引用", "仅在工程分析", "仅在政策相符性")
    codes = set(re.findall(r"(?:GB|HJ)[A-Za-z /]*\d+(?:-\d+)?", evidence, re.I))
    if any(term in evidence for term in missing_terms) or not codes:
        status, candidate = "存在缺漏", "存在缺漏"
        tags = "missing_solid_waste_standard"
        note = "证据明确未检出/未引用固废控制标准，或仅描述暂存处置措施；原答案却统一声称标准编制完整。"
    elif "GB18597-2001" in evidence.replace(" ", ""):
        status, candidate = "存在错误", "存在错误"
        tags = "obsolete_GB18597_2001"
        note = "报告仍引用GB18597-2001及2013修改单；GB18597-2023自2023-07-01实施并替代旧版。"
    elif "2021" in evidence:
        status, candidate = "存在错误", "存在错误"
        tags = "obsolete_hazardous_waste_catalog_2021"
        note = "证据引用《国家危险废物名录（2021年版）》；2025年版自2025-01-01施行并同时废止2021年版。"
    elif "GB18597-2023" in evidence.replace(" ", "") and "GB18599-2020" in evidence.replace(" ", ""):
        status, candidate = "基本通过_需轻微修正", "需人工复核"
        tags = "standard_title_or_scope_needs_correction"
        note = "危险废物与一般工业固废标准均有依据，但报告/答案对GB18599-2020名称或适用范围表述需按正式文本修订。"
    elif "GB18597-2023" in evidence.replace(" ", ""):
        status, candidate = "基本通过_需轻微修正", "需人工复核"
        tags = "answer_overstates_general_solid_waste_basis"
        note = "危险废物贮存标准有证据；答案关于一般固废依据或GB18599“已引用”的表述超出当前证据，不能直接判定完整。"
    else:
        status, candidate = "存在缺漏", "存在缺漏"
        tags = "incomplete_current_solid_waste_basis"
        note = "固废依据未形成现行危险废物与一般工业固废管理要求的完整证据链。"
    return {
        "codex_review_status": status,
        "recommended_gold_candidate": candidate,
        "question_validity": "有效",
        "answer_evidence_alignment": "不一致" if status in {"存在错误", "存在缺漏"} else "部分一致",
        "standard_or_calculation_check": "不通过" if status in {"存在错误", "存在缺漏"} else "部分通过",
        "basis_verification_candidate": "已核验版本关系；项目适用范围待确认",
        "issue_tags": tags,
        "codex_review_note": note,
        "calculation_detail": f"证据中识别依据：{'、'.join(sorted(codes))}",
    }


def review_row(row: dict[str, str], report_root: Path | None) -> dict[str, Any]:
    folder, score, report_text_or_note = report_match(row["project_name"], report_root)
    full_text = report_text_or_note if folder else ""
    category = row["审核类别"]
    if category == "环评投资概算":
        review = investment_review(row)
    elif category == "噪声排放标准":
        review = noise_review(row, full_text)
    elif category == "水污染物排放标准":
        review = water_review(row)
    elif category == "大气污染物排放标准":
        review = air_review(row)
    elif category == "固体废物控制标准":
        review = solid_review(row)
    else:
        raise ValueError(category)
    context = review.pop("_full_report_context", "已匹配完整报告，仅用于辅助定位" if folder else report_text_or_note)
    return {
        "question_id": row["question_id"],
        "canonical_project_id": row["canonical_project_id"],
        "project_name": row["project_name"],
        "审核类别": category,
        "question": row["question"],
        "answer": row["answer"],
        "evidence": row["evidence"],
        "source_basis": row["source_basis"],
        "source_manual_judgement": row["raw_manual_judgement"],
        "source_needs_human_review": row["是否需要人工复核"],
        **review,
        "source_report_folder": folder,
        "source_report_match_score": score,
        "full_report_context_check": context,
        "official_basis_urls": "；".join(OFFICIAL_BASIS.get(category, [])),
        "codex_review_is_final": False,
        "gold_freeze_authorized": False,
    }


def write_summary(results: list[dict[str, Any]]) -> None:
    status = Counter(r["codex_review_status"] for r in results)
    category_status: dict[str, Counter] = {}
    for row in results:
        category_status.setdefault(row["审核类别"], Counter())[row["codex_review_status"]] += 1
    changed = [r for r in results if r["recommended_gold_candidate"] != "无误"]
    lines = [
        "# 70道“候选无误题”Codex复核报告", "",
        "本轮依据仓库Codex提示词、QA证据包、可匹配的完整报告解析文本及现行官方标准进行候选复核。",
        "结果不是人工终值，不授权金标冻结，也未运行A/B/C/D实验或模型评分。",
        "",
        f"- 复核题数：{len(results)}",
        f"- 状态分布：{dict(status)}",
        f"- 仍可保留“无误”候选：{sum(r['recommended_gold_candidate'] == '无误' for r in results)}",
        f"- 需要改判或补证：{len(changed)}",
        "",
        "## 分类别结果", "",
    ]
    for category, counts in category_status.items():
        lines.append(f"- {category}：{dict(counts)}")
    lines += [
        "",
        "## 对科学问题的影响", "",
        "- 原字段“无需人工复核”不能作为金标质量的替代变量。",
        "- 大量固废题使用同一模板答案，但证据显示标准缺失、版本过期或与答案不一致。",
        "- 多数噪声题只能证明报告填写了某类标准，不能独立证明声功能区类别适用。",
        "- 水和大气题主要阻挡项是外部标准/污水厂关系未闭环或答案加入证据外事实。",
        "- 投资核算题的报告内数值证据最完整，适合作为低知识依赖对照任务。",
        "",
        "## 建议", "",
        "科学问题可继续研究RAG与Workflow/Skill的交互效应，但实验前必须把“原人工标记”",
        "替换为经证据、依据和版本核验后的金标；本轮结果应进入人工复核，不得直接冻结。",
    ]
    (REVIEW_DIR / "codex_review_70_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-root", type=Path, default=None)
    args = parser.parse_args()
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    selected = select_70(load_records())
    results = [review_row(row, args.report_root) for row in selected]
    write_csv(RESULT_CSV, results, RESULT_FIELDS)
    write_jsonl(RESULT_JSONL, results)
    write_summary(results)
    print(json.dumps({
        "records": len(results),
        "status": dict(Counter(r["codex_review_status"] for r in results)),
        "recommended": dict(Counter(r["recommended_gold_candidate"] for r in results)),
        "output": str(RESULT_CSV.relative_to(ROOT)),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
