#!/usr/bin/env python3
"""Deterministic, candidate-only governance pipeline for the 210 EIA QA items."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = ROOT / "gold_governance"
REPORTS = OUT / "reports"
SOURCE_CACHE = ROOT / ".cache" / "source_questions.json"
SOURCE_XLSX = REPO / "05_QA测试集" / "四大类问答对_最终版.xlsx"
TAXONOMY_JSONL = ROOT / "taxonomy" / "question_taxonomy_210.jsonl"
RECORDS_CSV = OUT / "gold_governance_records_v1.csv"
RECORDS_JSONL = OUT / "gold_governance_records_v1.jsonl"

ORIGINAL_FIELDS = [
    "date", "canonical_project_id", "version_round", "report_name", "project_name",
    "question_id", "audit_module", "question", "answer", "evidence", "source_basis",
    "scarcity_check", "verifiability_check", "manual_check", "人工判断", "人工备注",
    "润色后答案", "修改类型", "是否需要人工复核", "AI标注备注", "来源文件", "审核类别",
]
GOVERNANCE_FIELDS = [
    "raw_manual_judgement", "normalized_judgement_candidate",
    "normalized_judgement_final", "gold_review_status", "evidence_sufficiency",
    "item_quality_status", "basis_verification_status", "taxonomy_review_status",
    "experiment_inclusion", "review_queue_type", "reviewer_1", "reviewer_1_date",
    "reviewer_2", "reviewer_2_date", "adjudicator", "adjudication_note",
    "gold_version", "source_row_number", "auto_mapping_rule", "auto_flag_reason",
    "human_review_note",
]
TAXONOMY_FIELDS = [
    "audit_domain", "cognitive_level", "reasoning_type",
    "primary_functional_capability", "secondary_capabilities",
    "knowledge_dependency", "workflow_dependency", "evidence_span",
    "template_default_used", "taxonomy_source_override_reason",
    "classification_status", "taxonomy_version", "taxonomy_override_reason",
]
ALL_FIELDS = ORIGINAL_FIELDS + GOVERNANCE_FIELDS + TAXONOMY_FIELDS

EXPLICIT_MAP = {
    "正确": "无误", "无误": "无误", "存在错误": "存在错误",
    "存在缺漏": "存在缺漏", "需复核": "需人工复核",
    "不正确": "待判断", "需修正": "待判断", "无法判断": "待判断",
    "112": "待判断", "": "待判断",
}
ISSUE_LABELS = {"存在错误", "存在缺漏"}
INSUFFICIENCY_TERMS = (
    "未检索到", "无法核对", "证据不足", "材料缺失", "原文缺失", "未提供",
    "无法判断", "缺少关键", "信息不足", "未见", "无法确认",
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def ensure_dirs() -> None:
    for p in (OUT, REPORTS, OUT / "pilot", OUT / "formal", ROOT / ".cache"):
        p.mkdir(parents=True, exist_ok=True)


def read_source() -> tuple[list[str], list[dict[str, Any]]]:
    payload = json.loads(SOURCE_CACHE.read_text(encoding="utf-8"))
    return payload["headers"], payload["records"]


def read_taxonomy() -> dict[str, dict[str, Any]]:
    if not TAXONOMY_JSONL.exists():
        return {}
    rows = [json.loads(x) for x in TAXONOMY_JSONL.read_text(encoding="utf-8").splitlines() if x.strip()]
    return {r["question_id"]: r for r in rows}


def norm_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def candidate_mapping(raw: str) -> tuple[str, str, str]:
    if raw in EXPLICIT_MAP:
        reasons = {
            "": "人工判断为空：不得自动补填结论",
            "112": "数值112占用结论字段：疑似字段错位",
            "不正确": "需人工区分存在错误或存在缺漏",
            "需修正": "需人工区分实质问题或表达优化",
            "无法判断": "需人工区分证据不足、材料缺失或尚未审核",
            "需复核": "原结论明确要求人工复核",
        }
        return EXPLICIT_MAP[raw], f"MAP_{raw or 'BLANK'}", reasons.get(raw, "")
    if "无误" in raw or "正确" in raw:
        return "无误", "LONG_TEXT_CONTAINS_POSITIVE_CONCLUSION", "长说明占用结论字段；仅提取候选结论，必须人工确认"
    if "缺漏" in raw:
        return "存在缺漏", "LONG_TEXT_CONTAINS_OMISSION", "长说明占用结论字段；仅提取候选结论，必须人工确认"
    if "错误" in raw or "不正确" in raw:
        return "存在错误", "LONG_TEXT_CONTAINS_ERROR", "长说明占用结论字段；仅提取候选结论，必须人工确认"
    return "待判断", "UNRECOGNIZED_VALUE", "未识别的人工判断值，需人工复核"


def infer_quality(row: dict[str, Any], raw: str) -> tuple[str, str]:
    missing = [k for k in ("question", "answer", "evidence") if not norm_text(row.get(k))]
    if missing:
        return "原始材料缺失", f"缺少字段：{','.join(missing)}"
    if raw == "112" or (raw and raw not in EXPLICIT_MAP):
        return "字段错位", "人工判断字段出现数值或长说明"
    if not raw:
        return "待判断", "人工判断为空；结构完整但原因需人工确认"
    return "有效", ""


def infer_evidence(row: dict[str, Any]) -> tuple[str, str]:
    evidence = norm_text(row.get("evidence"))
    answer = norm_text(row.get("answer"))
    if not evidence:
        return "原始材料缺失", "证据字段为空"
    hit = [term for term in INSUFFICIENCY_TERMS if term in evidence or term in answer]
    if hit:
        return "不足", f"命中证据不足候选词：{'、'.join(hit[:3])}"
    return "部分充分", "存在报告证据，但尚未经人工逐项核验"


def infer_basis(row: dict[str, Any]) -> tuple[str, str]:
    if row.get("审核类别") == "环评投资概算":
        return "不需要外部依据", "投资复核主要依据报告内金额与算式"
    if norm_text(row.get("source_basis")):
        return "部分核验", "已列依据来源，但未在本阶段逐条核验"
    return "待判断", "未提供可核验依据"


def make_records() -> list[dict[str, Any]]:
    headers, source = read_source()
    if headers != ORIGINAL_FIELDS:
        raise ValueError(f"Source fields changed: {headers}")
    taxonomy = read_taxonomy()
    records: list[dict[str, Any]] = []
    for idx, src in enumerate(source, start=2):
        raw = norm_text(src.get("人工判断"))
        candidate, rule, map_reason = candidate_mapping(raw)
        quality, quality_reason = infer_quality(src, raw)
        evidence, evidence_reason = infer_evidence(src)
        basis, basis_reason = infer_basis(src)
        needs_review = norm_text(src.get("是否需要人工复核")) == "是"
        reasons = [x for x in (map_reason, quality_reason, evidence_reason, basis_reason) if x]
        if needs_review:
            if quality != "有效":
                queue = "C_题目或材料问题"
            elif raw in {"需复核", "无法判断"} or evidence in {"不足", "原始材料缺失"}:
                queue = "B_证据不足"
                if candidate in {"需人工复核", "待判断"} and evidence == "不足":
                    candidate = "证据不足"
                    rule += "+EVIDENCE_INSUFFICIENCY_SIGNAL"
            else:
                queue = "A_仅待终审"
        else:
            # “否”并不证明已经终审；异常仍分入C，其余留待分流。
            queue = "C_题目或材料问题" if quality != "有效" else "待分流"
        tax = taxonomy.get(src["question_id"], {})
        rec = {k: src.get(k, "") for k in ORIGINAL_FIELDS}
        rec.update({
            "raw_manual_judgement": raw,
            "normalized_judgement_candidate": candidate,
            "normalized_judgement_final": "",
            "gold_review_status": "未复核",
            "evidence_sufficiency": evidence,
            "item_quality_status": quality,
            "basis_verification_status": basis,
            "taxonomy_review_status": "自动默认",
            "experiment_inclusion": "候选池",
            "review_queue_type": queue,
            "reviewer_1": "", "reviewer_1_date": "", "reviewer_2": "",
            "reviewer_2_date": "", "adjudicator": "", "adjudication_note": "",
            "gold_version": "", "source_row_number": idx,
            "auto_mapping_rule": rule,
            "auto_flag_reason": "；".join(dict.fromkeys(reasons)),
            "human_review_note": "",
            "audit_domain": tax.get("audit_domain", ""),
            "cognitive_level": tax.get("cognitive_level", ""),
            "reasoning_type": tax.get("reasoning_type", ""),
            "primary_functional_capability": tax.get("primary_functional_capability", ""),
            "secondary_capabilities": "；".join(tax.get("secondary_capabilities", [])),
            "knowledge_dependency": tax.get("knowledge_dependency", ""),
            "workflow_dependency": tax.get("workflow_dependency", ""),
            "evidence_span": tax.get("evidence_span", ""),
            "template_default_used": tax.get("template_default_used", ""),
            "taxonomy_source_override_reason": tax.get("override_reason", ""),
            "classification_status": tax.get("classification_status", ""),
            "taxonomy_version": tax.get("taxonomy_version", ""),
            "taxonomy_override_reason": "",
        })
        records.append(rec)
    return records


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str] | None = None) -> None:
    rows = list(rows)
    fields = fields or (list(rows[0]) if rows else ALL_FIELDS)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def anomalies(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r["raw_manual_judgement"] == "" or r["raw_manual_judgement"] == "112"
            or (r["raw_manual_judgement"] not in EXPLICIT_MAP)]


def audit(records: list[dict[str, Any]]) -> None:
    _, source = read_source()
    raw_counts = Counter(norm_text(r["人工判断"]) or "(空白)" for r in source)
    cats = Counter(r["审核类别"] for r in source)
    manual = Counter(str(bool(r["manual_check"])).lower() for r in source)
    needs = Counter(norm_text(r["是否需要人工复核"]) or "(空白)" for r in source)
    field_rows = []
    for field, counts in (("人工判断", raw_counts), ("manual_check", manual), ("是否需要人工复核", needs), ("审核类别", cats)):
        field_rows += [{"field": field, "value": k, "count": v} for k, v in sorted(counts.items())]
    write_csv(REPORTS / "field_value_counts.csv", field_rows, ["field", "value", "count"])
    anom = anomalies(records)
    write_csv(REPORTS / "judgement_anomalies.csv", anom)
    conflicts = []
    for r in records:
        if (not bool(r["manual_check"]) and r["raw_manual_judgement"]) or (bool(r["manual_check"]) and not r["raw_manual_judgement"]):
            reason = ("manual_check=false但存在人工判断" if not bool(r["manual_check"])
                      else "manual_check=true但人工判断为空")
            x = dict(r); x["conflict_reason"] = reason; conflicts.append(x)
    write_csv(REPORTS / "review_status_conflicts.csv", conflicts, ALL_FIELDS + ["conflict_reason"])
    tax_counts = Counter(r["classification_status"] or "(缺失)" for r in records)
    write_csv(REPORTS / "taxonomy_default_distribution.csv",
              [{"classification_status": k, "count": v, "share": f"{v/len(records):.2%}"} for k, v in tax_counts.items()],
              ["classification_status", "count", "share"])
    pilot_ids = current_pilot_keys()
    current = [r for r in records if (r["canonical_project_id"], r["审核类别"]) in pilot_ids]
    current_unready = sum(r["gold_review_status"] != "已冻结" for r in current)
    sha = hashlib.sha256(SOURCE_XLSX.read_bytes()).hexdigest()
    lines = [
        "# 210题源数据审计",
        "",
        f"- 源文件：`{rel(SOURCE_XLSX)}`（只读）",
        f"- SHA-256：`{sha}`",
        f"- 总题数：{len(records)}；唯一 question_id：{len({r['question_id'] for r in records})}；项目数：{len({r['canonical_project_id'] for r in records})}",
        f"- 审核类别：{dict(cats)}",
        f"- 人工判断原值：{dict(raw_counts)}",
        f"- manual_check：{dict(manual)}",
        f"- 是否需要人工复核：{dict(needs)}",
        f"- 结论字段异常：{len(anom)}（空白 {raw_counts['(空白)']}；112 {raw_counts['112']}；长说明 {len(anom)-raw_counts['(空白)']-raw_counts['112']}）",
        f"- 状态冲突候选：{len(conflicts)}",
        f"- 四维分类状态：{dict(tax_counts)}；全部为 auto_default：{'是' if tax_counts == Counter({'auto_default': len(records)}) else '否'}",
        f"- 当前18题中未冻结：{current_unready}/{len(current)}；本阶段不自动冻结。",
        "",
        "自动判断均写入候选字段与日志字段；人工终值保持空白。",
    ]
    (REPORTS / "source_data_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / ".cache" / "source_workbook_sha256.txt").write_text(sha + "\n", encoding="ascii")


def current_pilot_keys() -> set[tuple[str, str]]:
    projects = {"PL001", "PL002", "PL003", "PL004", "PL020", "PL026"}
    cats = {"水污染物排放标准", "大气污染物排放标准", "噪声排放标准"}
    return {(p, c) for p in projects for c in cats}


def triage(records: list[dict[str, Any]]) -> None:
    queues = {
        "A": [r for r in records if r["review_queue_type"] == "A_仅待终审"],
        "B": [r for r in records if r["review_queue_type"] == "B_证据不足"],
        "C": [r for r in records if r["review_queue_type"] == "C_题目或材料问题"],
        "D": [r for r in records if r["review_queue_type"] == "D_无需复核候选"],
    }
    for key, rows in queues.items():
        write_csv(OUT / f"review_queue_{key}.csv", rows)
    target = [r for r in records if r["是否需要人工复核"] == "是"]
    target_counts = Counter(r["review_queue_type"] for r in target)
    all_counts = Counter(r["review_queue_type"] for r in records)
    text = [
        "# 人工复核队列汇总", "",
        f"- 原字段标记需复核：{len(target)}题；已全部分流：{sum(target_counts.values()) == len(target)}。",
        f"- 135题分流：{dict(target_counts)}",
        f"- 全部210题候选队列：{dict(all_counts)}",
        "- D类为0题：仅凭“是否需要人工复核=否”不足以证明已经人工终审。",
        "- 队列均为候选分流，不代表金标冻结或审核完成。",
    ]
    (REPORTS / "review_queue_summary.md").write_text("\n".join(text) + "\n", encoding="utf-8")


def selection_fields() -> list[str]:
    return ["selection_option", "selection_status", "priority", "blocker", "replaceable"] + ALL_FIELDS


def current_pilot(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = current_pilot_keys()
    rows = [r for r in records if (r["canonical_project_id"], r["审核类别"]) in keys]
    return sorted(rows, key=lambda r: (r["canonical_project_id"], r["审核类别"]))


def balanced_pilot(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    quotas = {"环评投资概算": 4, "噪声排放标准": 4, "水污染物排放标准": 5, "大气污染物排放标准": 5}
    # 投资题当前没有“存在错误/存在缺漏”的明确候选；由另外三类补足负例，
    # 使总计保持约9:9，同时不把“证据不足”冒充错误/缺漏。
    positive_targets = {"环评投资概算": 4, "噪声排放标准": 1, "水污染物排放标准": 2, "大气污染物排放标准": 2}
    selected: list[dict[str, Any]] = []
    used_projects: Counter[str] = Counter()
    for cat, quota in quotas.items():
        pool = [r for r in records if r["审核类别"] == cat and r["item_quality_status"] == "有效"
                and r["normalized_judgement_candidate"] in {"无误", "存在错误", "存在缺漏"}]
        # Alternate positive / issue while rewarding project diversity and evidence readiness.
        pos = [r for r in pool if r["normalized_judgement_candidate"] == "无误"]
        neg = [r for r in pool if r["normalized_judgement_candidate"] in ISSUE_LABELS]
        want_pos = positive_targets[cat]
        for bucket, want in ((pos, want_pos), (neg, quota - want_pos)):
            for _ in range(want):
                if not bucket:
                    break
                bucket.sort(key=lambda r: (
                    used_projects[r["canonical_project_id"]],
                    r["evidence_sufficiency"] != "部分充分",
                    r["basis_verification_status"] not in {"部分核验", "不需要外部依据"},
                    r["question_id"],
                ))
                pick = bucket.pop(0)
                selected.append(pick)
                used_projects[pick["canonical_project_id"]] += 1
        while sum(r["审核类别"] == cat for r in selected) < quota:
            remaining = [r for r in pool if r not in selected]
            remaining.sort(key=lambda r: (used_projects[r["canonical_project_id"]], r["question_id"]))
            if not remaining:
                break
            pick = remaining[0]; selected.append(pick); used_projects[pick["canonical_project_id"]] += 1
    return selected


def decorate_selection(rows: list[dict[str, Any]], option: str) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        blockers = []
        if r["gold_review_status"] != "已冻结": blockers.append("金标未冻结")
        if r["normalized_judgement_final"] == "": blockers.append("人工终值为空")
        if r["taxonomy_review_status"] == "自动默认": blockers.append("四维分类未人工确认")
        if r["evidence_sufficiency"] != "充分": blockers.append("证据充分性未确认")
        x = dict(r)
        x.update({
            "selection_option": option,
            "selection_status": "候选_未冻结",
            "priority": "优先人工核验" if r["审核类别"] == "环评投资概算" else "常规人工核验",
            "blocker": "；".join(blockers),
            "replaceable": "是",
            "experiment_inclusion": "趋势实验候选",
        })
        out.append(x)
    return out


def build_pilot(records: list[dict[str, Any]]) -> None:
    a = decorate_selection(current_pilot(records), "A_保留当前18题")
    b = decorate_selection(balanced_pilot(records), "B_平衡18题")
    write_csv(OUT / "pilot" / "pilot_current_18_readiness.csv", a, selection_fields())
    write_csv(OUT / "pilot" / "pilot_option_A_keep_current.csv", a, selection_fields())
    write_csv(OUT / "pilot" / "pilot_option_B_balanced.csv", b, selection_fields())
    priority = sorted(a + b, key=lambda r: (r["审核类别"] != "环评投资概算", r["question_id"]))
    write_csv(OUT / "pilot" / "pilot_priority_review_queue.csv", priority, selection_fields())
    def dist(rows: list[dict[str, Any]]) -> dict[str, int]:
        return dict(Counter(r["审核类别"] for r in rows))
    report = [
        "# 18题趋势实验候选方案", "",
        f"- 方案A：{len(a)}题，分布 {dist(a)}；已冻结 0 题。",
        f"- 方案B：{len(b)}题，分布 {dist(b)}；候选结论 {dict(Counter(r['normalized_judgement_candidate'] for r in b))}；已冻结 0 题。",
        "- 当前不能运行144次趋势实验：18题尚未完成终值、证据、依据与四维分类人工确认。",
        "- 投资题列为最高优先级；任何候选题均可在人工复核后替换。",
        "- 选择过程不读取任何模型得分或未来A/B/C/D结果。",
    ]
    (OUT / "pilot" / "pilot_selection_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def build_formal(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cats = [c for c in sorted({r["审核类别"] for r in records}) if c != "国民经济行业分类"]
    selected = []
    used: Counter[str] = Counter()
    for cat in cats:
        pool = [r for r in records if r["审核类别"] == cat and r["item_quality_status"] == "有效"
                and r["normalized_judgement_candidate"] in {"无误", "存在错误", "存在缺漏"}]
        pool.sort(key=lambda r: (
            used[r["canonical_project_id"]],
            r["evidence_sufficiency"] != "部分充分",
            r["basis_verification_status"] not in {"部分核验", "不需要外部依据"},
            r["normalized_judgement_candidate"] != "无误",
            r["question_id"],
        ))
        cat_selected = []
        while pool and len(cat_selected) < 8:
            # Prefer alternating positive and issue labels.
            desired_positive = len(cat_selected) % 2 == 0
            matches = [r for r in pool if (r["normalized_judgement_candidate"] == "无误") == desired_positive]
            pick_pool = matches or pool
            pick_pool.sort(key=lambda r: (used[r["canonical_project_id"]], r["question_id"]))
            pick = pick_pool[0]
            pool.remove(pick); cat_selected.append(pick); used[pick["canonical_project_id"]] += 1
        selected.extend(cat_selected)
    decorated = []
    for r in selected:
        x = dict(r)
        x.update({
            "selection_status": "正式实验候选_未冻结",
            "priority": "高" if r["knowledge_dependency"] == "high" and r["workflow_dependency"] == "high" else "常规",
            "blocker": "需填写人工终值、核验证据/依据、确认四维分类并完成审核",
            "experiment_inclusion": "正式实验候选",
        })
        decorated.append(x)
    fields = ["selection_status", "priority", "blocker"] + ALL_FIELDS
    write_csv(OUT / "formal" / "formal_candidate_pool.csv", decorated, fields)
    write_csv(OUT / "formal" / "formal_priority_review_queue.csv",
              sorted(decorated, key=lambda r: (r["priority"] != "高", r["审核类别"], r["question_id"])), fields)
    dist = Counter(r["审核类别"] for r in decorated)
    labels = Counter(r["normalized_judgement_candidate"] for r in decorated)
    text = [
        "# 正式实验候选池分布", "",
        f"- 候选总数：{len(decorated)}（未冻结）",
        f"- 审核任务分布：{dict(dist)}",
        f"- 候选结论分布：{dict(labels)}",
        "- 国民经济行业分类30题因结论字段异常，暂不纳入本候选池。",
        "",
        "> 本测试集采用按审核任务平衡抽样，用于比较模型条件，不代表真实业务中各类问题的发生频率。",
    ]
    (OUT / "formal" / "formal_candidate_distribution.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    return decorated


def protocol_and_final(records: list[dict[str, Any]], formal: list[dict[str, Any]]) -> None:
    protocol = """# 人工复核协议

## 建议顺序

1. 30道异常题
2. 18道趋势实验候选
3. A类仅待终审题
4. 正式实验候选
5. 其余候选池

## 每题确认项

1. 题目是否有效；
2. 证据是否充分；
3. 正确结论是什么（填写 `normalized_judgement_final`）；
4. 依据是否准确；
5. 四维分类是否合理；覆盖时必须填写 `taxonomy_override_reason`；
6. 是否进入趋势或正式实验；
7. 是否冻结。

冻结前必须运行 `scripts/validate_gold_freeze.py`。候选映射、候选队列和候选样本均不等于金标。
"""
    (REPORTS / "manual_review_protocol.md").write_text(protocol, encoding="utf-8")
    anom = anomalies(records)
    needs = [r for r in records if r["是否需要人工复核"] == "是"]
    queue_counts = Counter(r["review_queue_type"] for r in needs)
    structurally_valid = sum(r["item_quality_status"] == "有效" for r in records)
    quick = sum(r["review_queue_type"] == "A_仅待终审" for r in records)
    current = current_pilot(records)
    frozen = sum(r["gold_review_status"] == "已冻结" for r in current)
    exclude = [r["question_id"] for r in records if r["item_quality_status"] in {"字段错位", "原始材料缺失", "题答不匹配", "排除"}]
    report = [
        "# 金标治理与实验就绪最终报告", "",
        "本报告描述的是候选治理状态，不代表金标已经完成。",
        "",
        f"1. 结构有效：{structurally_valid}/210题；其余需人工处理字段错位、空白结论原因或材料问题。",
        f"2. 30道结论字段异常：空白26题、`112` 3题、长说明1题；均保留原文且未写入人工终值。",
        f"3. 135道需复核题候选分流：{dict(queue_counts)}。",
        f"4. 可能较快冻结：A类候选{quick}题，但仍须人工核验证据、依据、分类和终值。",
        f"5. 当前18题真正就绪（已冻结）：{frozen}/18。",
        "6. 平衡18题须优先核验4道投资题，其后核验所有题的证据、依据和四维分类。",
        "7. 当前不可运行144次趋势实验。",
        "8. 阻挡项：人工终值为空、全部未冻结、证据仅为候选判断、四维分类仍为自动默认。",
        f"9. 已建设{len(formal)}道正式实验候选，但不能作为正式金标运行。",
        "10. 用户需填写/确认：题目质量、证据充分性、人工终值、依据核验、四维分类、两级审核/裁决、实验纳入状态、gold_version与冻结状态。",
        f"11. 建议暂不纳入实验：字段错位或材料异常题 {len(exclude)} 道；ID见 `judgement_anomalies.csv` 与C类队列。",
        "",
        "停止点：等待用户完成人工复核工作簿；未运行A/B/C/D，未运行GPT评分，未生成实验得分。",
    ]
    (REPORTS / "final_gold_governance_readiness.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def export(records: list[dict[str, Any]]) -> None:
    write_csv(RECORDS_CSV, records, ALL_FIELDS)
    write_jsonl(RECORDS_JSONL, records)


def build_all() -> None:
    ensure_dirs()
    records = make_records()
    export(records)
    audit(records)
    triage(records)
    build_pilot(records)
    formal = build_formal(records)
    protocol_and_final(records, formal)
    log = {
        "run_date": date.today().isoformat(),
        "pipeline": "candidate_only_gold_governance_v1",
        "source": rel(SOURCE_XLSX),
        "records": len(records),
        "automatic_rules": sorted({r["auto_mapping_rule"] for r in records}),
        "gold_review_status_written": sorted({r["gold_review_status"] for r in records}),
        "normalized_final_nonblank": sum(bool(r["normalized_judgement_final"]) for r in records),
        "experiment_execution": False,
        "model_scoring": False,
    }
    (REPORTS / "automation_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_all()
