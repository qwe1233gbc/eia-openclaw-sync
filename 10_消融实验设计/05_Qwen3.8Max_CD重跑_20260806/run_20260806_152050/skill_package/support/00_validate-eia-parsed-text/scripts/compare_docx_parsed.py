#!/usr/bin/env python3
"""Compare an EIA DOCX with a lightweight parsed-text artifact.

The script uses only the Python standard library and emits a compact JSON
precheck. It is intentionally conservative: automatic metrics surface risks;
the skill workflow still samples audit-critical evidence before final release.
"""

from __future__ import annotations

import argparse
import collections
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = "{" + W_NS + "}"

MAIN_SECTIONS = [
    "一、建设项目基本情况",
    "二、建设项目工程分析",
    "三、区域环境质量现状、环境保护目标及评价标准",
    "四、主要环境影响和保护措施",
    "五、环境保护措施监督检查清单",
    "六、结论",
]

CONTENT_KEYS = (
    "content",
    "text",
    "page_content",
    "markdown",
    "html",
    "body",
)

CRITICAL_TABLE_TERMS = (
    "产品",
    "原辅材料",
    "设备",
    "工艺",
    "产污",
    "废气",
    "废水",
    "源强",
    "排放",
    "收集效率",
    "处理效率",
    "活性炭",
    "危险废物",
    "固体废物",
    "总量",
    "环境保护措施",
    "执行标准",
)

UNIT_PATTERN = (
    r"%|t/a|kg/a|g/a|mg/m(?:3|³)|mg/l|μg/m(?:3|³)|m(?:3|³)/h|"
    r"m(?:2|²)|m(?:3|³)|kg|mg|g|t|kw|kW|h|d|a|℃|吨|千克|公斤|"
    r"平方米|立方米|小时|天|年"
)

NUMBER_UNIT_RE = re.compile(
    rf"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?(?:\s*(?:{UNIT_PATTERN}))?",
    re.IGNORECASE,
)


class VisibleHTMLText(HTMLParser):
    """Extract readable text while retaining table boundaries."""

    BREAK_TAGS = {
        "p",
        "div",
        "br",
        "li",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "tr",
        "table",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        tag = tag.lower()
        if tag in self.BREAK_TAGS:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.BREAK_TAGS:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" | ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return clean_text("".join(self.parts))


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n+ *", "\n", text)
    return text.strip()


def compact(text: str) -> str:
    return re.sub(r"\s+", "", html.unescape(text))


def normalize(text: str) -> str:
    text = compact(text)
    text = text.replace("VOCs", "VOCS").replace("VOCₛ", "VOCS")
    text = text.replace("m²", "m2").replace("m³", "m3")
    text = re.sub(r"[，。；：、“”‘’（）()《》〈〉【】\[\]—–－|｜-]", "", text)
    return text.lower()


def ngram_coverage(source: str, target: str, n: int = 7) -> float:
    source_n = normalize(source)
    target_n = normalize(target)
    if not source_n:
        return 1.0
    if len(source_n) < n:
        return 1.0 if source_n in target_n else 0.0
    source_set = {source_n[i : i + n] for i in range(len(source_n) - n + 1)}
    target_set = {target_n[i : i + n] for i in range(max(0, len(target_n) - n + 1))}
    return len(source_set & target_set) / len(source_set)


def element_text(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return clean_text("".join(parts))


def table_text(table: ET.Element) -> str:
    rows: list[str] = []
    for row in table.findall("./" + W + "tr"):
        cells = [element_text(cell) for cell in row.findall("./" + W + "tc")]
        cells = [cell for cell in cells if cell]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def read_docx(path: Path) -> dict:
    try:
        archive = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, FileNotFoundError) as exc:
        raise ValueError(f"无法打开DOCX：{exc}") from exc

    with archive:
        try:
            root = ET.fromstring(archive.read("word/document.xml"))
        except KeyError as exc:
            raise ValueError("DOCX缺少word/document.xml") from exc

        body = root.find(".//" + W + "body")
        if body is None:
            raise ValueError("DOCX正文结构不可读取")

        blocks: list[str] = []
        for child in body:
            if child.tag == W + "p":
                text = element_text(child)
            elif child.tag == W + "tbl":
                text = table_text(child)
            else:
                continue
            if text:
                blocks.append(text)

        all_tables = [
            text
            for text in (table_text(table) for table in root.findall(".//" + W + "tbl"))
            if text
        ]

        page_count = None
        if "docProps/app.xml" in archive.namelist():
            try:
                app_root = ET.fromstring(archive.read("docProps/app.xml"))
                for node in app_root.iter():
                    if node.tag.rsplit("}", 1)[-1] == "Pages" and node.text:
                        page_count = int(node.text)
                        break
            except (ET.ParseError, ValueError):
                page_count = None

        media = [name for name in archive.namelist() if name.startswith("word/media/")]
        embeds = [name for name in archive.namelist() if name.startswith("word/embeddings/")]

    text = "\n".join(blocks)
    return {
        "text": text,
        "tables": all_tables,
        "table_count": len(all_tables),
        "drawings": len(root.findall(".//" + W + "drawing")),
        "media_files": len(media),
        "embedded_objects": len(embeds),
        "page_count": page_count,
    }


def choose_content(record) -> str:  # noqa: ANN001
    if isinstance(record, str):
        return record
    if isinstance(record, dict):
        for key in CONTENT_KEYS:
            value = record.get(key)
            if isinstance(value, str):
                return value
        strings = [value for value in record.values() if isinstance(value, str)]
        return max(strings, key=len) if strings else ""
    return ""


def read_json_or_jsonl(path: Path) -> tuple[list[str], list[str]]:
    if path.suffix.lower() == ".jsonl":
        records = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    else:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            for key in ("chunks", "items", "data", "documents", "pages"):
                if isinstance(data.get(key), list):
                    records = data[key]
                    break
            else:
                records = [data]
        else:
            records = [data]

    chunks: list[str] = []
    ids: list[str] = []
    for index, record in enumerate(records):
        content = choose_content(record)
        if content:
            chunks.append(content)
            if isinstance(record, dict) and record.get("id") is not None:
                ids.append(str(record["id"]))
            else:
                ids.append(str(index))
    return chunks, ids


def read_parsed(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        chunks, ids = read_json_or_jsonl(path)
    else:
        chunks = [path.read_text(encoding="utf-8-sig")]
        ids = ["0"]

    raw = "\n".join(chunks)
    if re.search(r"<\s*(?:html|body|table|p|div|tr|td|h[1-6])\b", raw, re.IGNORECASE):
        parser = VisibleHTMLText()
        parser.feed(raw)
        plain = parser.text()
    else:
        plain = clean_text(raw)

    return {"raw": raw, "text": plain, "chunks": chunks, "ids": ids}


def section_map(text: str) -> tuple[dict[str, str], bool]:
    text_c = compact(text)
    positions = [(heading, text_c.find(compact(heading))) for heading in MAIN_SECTIONS]
    present = [(heading, pos) for heading, pos in positions if pos >= 0]
    ordered = [pos for _, pos in present] == sorted(pos for _, pos in present)
    result: dict[str, str] = {}
    for index, (heading, pos) in enumerate(positions):
        if pos < 0:
            continue
        next_positions = [p for _, p in positions[index + 1 :] if p > pos]
        end = min(next_positions) if next_positions else len(text_c)
        if heading == "六、结论":
            for marker in ("附表", "附图", "附件1", "附件一"):
                marker_pos = text_c.find(marker, pos + len(compact(heading)))
                if marker_pos >= 0:
                    end = min(end, marker_pos)
        result[heading] = text_c[pos:end]
    return result, ordered


def number_unit_tokens(text: str) -> list[str]:
    tokens = []
    for token in NUMBER_UNIT_RE.findall(text):
        normalized = re.sub(r"\s+", "", token).lower()
        normalized = normalized.replace("m²", "m2").replace("m³", "m3")
        tokens.append(normalized)
    return tokens


def multiset_coverage(source: list[str], target: list[str]) -> float:
    if not source:
        return 1.0
    source_count = collections.Counter(source)
    target_count = collections.Counter(target)
    matched = sum(min(count, target_count[token]) for token, count in source_count.items())
    return matched / len(source)


def numeric_id_diagnostics(ids: list[str]) -> dict:
    numeric = []
    for value in ids:
        if re.fullmatch(r"\d+", value.strip()):
            numeric.append(int(value))
    duplicates = sorted(value for value, count in collections.Counter(ids).items() if count > 1)
    gaps: list[int] = []
    if len(numeric) == len(ids) and numeric:
        unique = sorted(set(numeric))
        gaps = [value for value in range(unique[0], unique[-1] + 1) if value not in unique]
    return {
        "ids": ids,
        "duplicates": duplicates,
        "numeric_gaps": gaps,
        "in_input_order": numeric == sorted(numeric) if len(numeric) == len(ids) else None,
    }


def anomaly_diagnostics(raw: str) -> list[dict]:
    findings: list[dict] = []
    patterns = [
        ("serialized_record", r"\{\s*['\"]id['\"]\s*:\s*['\"]"),
        ("object_object", r"\[object Object\]"),
        ("traceback", r"Traceback \(most recent call last\)"),
        ("none_type", r"NoneType"),
        ("replacement_character", "�"),
    ]
    for code, pattern in patterns:
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            excerpt = clean_text(raw[max(0, match.start() - 35) : match.end() + 45])[:120]
            findings.append({"code": code, "excerpt": excerpt})

    for tag in ("table", "tr", "td"):
        opened = len(re.findall(rf"<{tag}\b", raw, re.IGNORECASE))
        closed = len(re.findall(rf"</{tag}\s*>", raw, re.IGNORECASE))
        if opened != closed:
            findings.append(
                {"code": f"unbalanced_{tag}", "opened": opened, "closed": closed}
            )
    return findings


def add_issue(container: list[dict], code: str, message: str, evidence=None) -> None:  # noqa: ANN001
    item = {"code": code, "message": message}
    if evidence is not None:
        item["evidence"] = evidence
    container.append(item)


def compare(docx: Path, parsed: Path, max_findings: int, min_table_chars: int) -> dict:
    source = read_docx(docx)
    target = read_parsed(parsed)
    source_sections, _ = section_map(source["text"])
    target_sections, target_ordered = section_map(target["text"])

    section_results = []
    for heading in MAIN_SECTIONS:
        if heading not in source_sections:
            continue
        coverage = (
            ngram_coverage(source_sections[heading], target_sections.get(heading, ""))
            if heading in target_sections
            else 0.0
        )
        section_results.append(
            {
                "section": heading,
                "present": heading in target_sections,
                "coverage": round(coverage, 4),
                "source_chars": len(source_sections[heading]),
                "parsed_chars": len(target_sections.get(heading, "")),
            }
        )

    source_body = "\n".join(source_sections.values()) or source["text"]
    target_body = "\n".join(
        target_sections.get(heading, "") for heading in source_sections
    ) or target["text"]
    body_coverage = ngram_coverage(source_body, target_body)
    number_coverage = multiset_coverage(
        number_unit_tokens(source_body), number_unit_tokens(target_body)
    )

    table_results = []
    for index, text in enumerate(source["tables"], start=1):
        if len(compact(text)) < min_table_chars:
            continue
        coverage = ngram_coverage(text, target["text"])
        critical = any(term in text for term in CRITICAL_TABLE_TERMS)
        table_results.append(
            {
                "table": f"word_table_{index}",
                "coverage": round(coverage, 4),
                "critical": critical,
                "source_chars": len(compact(text)),
                "signature": clean_text(text)[:100],
            }
        )
    low_tables = sorted(table_results, key=lambda item: item["coverage"])[:max_findings]

    chunk_info = numeric_id_diagnostics(target["ids"])
    anomalies = anomaly_diagnostics(target["raw"])
    blockers: list[dict] = []
    warnings: list[dict] = []

    missing_sections = [item["section"] for item in section_results if not item["present"]]
    if missing_sections:
        add_issue(blockers, "missing_main_section", "解析结果缺少原Word主章节", missing_sections)
    if not target_ordered:
        add_issue(blockers, "section_order_error", "解析结果主章节顺序异常")

    for item in section_results:
        if not item["present"]:
            continue
        if item["coverage"] < 0.75 and item["source_chars"] >= 300:
            add_issue(
                blockers,
                "low_section_coverage",
                f"核心章节覆盖过低：{item['section']}",
                item,
            )
        elif item["coverage"] < 0.90 and item["source_chars"] >= 300:
            add_issue(
                warnings,
                "section_needs_review",
                f"章节覆盖需要人工确认：{item['section']}",
                item,
            )

    if body_coverage < 0.80:
        add_issue(blockers, "low_body_coverage", "主体正文覆盖率低于80%", round(body_coverage, 4))
    elif body_coverage < 0.90:
        add_issue(warnings, "body_needs_review", "主体正文覆盖率低于90%", round(body_coverage, 4))

    if number_coverage < 0.90:
        add_issue(blockers, "low_number_unit_coverage", "数值及单位出现次数覆盖率低于90%", round(number_coverage, 4))
    elif number_coverage < 0.95:
        add_issue(warnings, "number_unit_needs_review", "数值及单位覆盖率低于95%", round(number_coverage, 4))

    severe_tables = [item for item in table_results if item["critical"] and item["coverage"] < 0.50]
    review_tables = [item for item in table_results if item["critical"] and 0.50 <= item["coverage"] < 0.85]
    if severe_tables:
        add_issue(
            blockers,
            "critical_table_loss",
            "至少一个审核关键表格覆盖低于50%",
            sorted(severe_tables, key=lambda item: item["coverage"])[:max_findings],
        )
    if review_tables:
        add_issue(
            warnings,
            "critical_table_needs_review",
            "部分审核关键表格覆盖低于85%",
            sorted(review_tables, key=lambda item: item["coverage"])[:max_findings],
        )

    blocker_anomaly_codes = {"serialized_record", "object_object", "traceback", "none_type"}
    if any(item["code"] in blocker_anomaly_codes for item in anomalies):
        add_issue(blockers, "parser_artifact", "解析文本混入序列化对象或异常信息", anomalies)
    elif anomalies:
        add_issue(warnings, "text_or_markup_anomaly", "解析文本存在乱码或标签不平衡", anomalies)

    if chunk_info["duplicates"]:
        add_issue(warnings, "duplicate_chunk_id", "解析分块ID重复", chunk_info["duplicates"])
    if chunk_info["numeric_gaps"]:
        add_issue(warnings, "chunk_id_gap", "解析分块ID存在缺号，需核对是否漏块", chunk_info["numeric_gaps"])
    if chunk_info["in_input_order"] is False:
        add_issue(warnings, "chunk_order_risk", "数值型分块ID未按顺序排列")

    if blockers:
        verdict = "不可用"
    elif warnings:
        verdict = "修复后可用"
    else:
        verdict = "自动预检通过，待关键证据抽查"

    html_tables = len(re.findall(r"<table\b", target["raw"], re.IGNORECASE))
    html_rows = len(re.findall(r"<tr\b", target["raw"], re.IGNORECASE))
    return {
        "verdict": verdict,
        "note": "最终放行仍需按技能要求抽查8–12个审核关键证据点。",
        "files": {
            "docx": str(docx),
            "parsed": str(parsed),
            "docx_bytes": docx.stat().st_size,
            "parsed_bytes": parsed.stat().st_size,
        },
        "metrics": {
            "docx_pages_from_properties": source["page_count"],
            "source_visible_chars": len(compact(source["text"])),
            "parsed_plain_chars": len(compact(target["text"])),
            "plain_text_length_ratio": round(
                len(compact(target["text"])) / max(1, len(compact(source["text"]))), 4
            ),
            "audit_body_7gram_coverage": round(body_coverage, 4),
            "number_unit_occurrence_coverage": round(number_coverage, 4),
            "source_tables": source["table_count"],
            "parsed_html_tables": html_tables,
            "parsed_html_rows": html_rows,
            "source_drawings": source["drawings"],
            "source_media_files": source["media_files"],
            "source_embedded_objects": source["embedded_objects"],
        },
        "sections": section_results,
        "chunks": chunk_info,
        "anomalies": anomalies,
        "lowest_coverage_tables": low_tables,
        "blockers": blockers,
        "warnings": warnings,
        "manual_checks": [
            "抽查8–12个审核关键证据点，优先第四章、复杂表格和定量核算。",
            "确认工艺流程图、平面关系图、公式和图片表格存在等价文字替代。",
            "确认表格线性化后字段、数值、单位与对象的对应关系未改变。",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare an original EIA DOCX with parsed JSON/HTML/Markdown/TXT."
    )
    parser.add_argument("--docx", required=True, type=Path, help="Original .docx file")
    parser.add_argument("--parsed", required=True, type=Path, help="Parsed text artifact")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    parser.add_argument("--max-findings", type=int, default=5)
    parser.add_argument("--min-table-chars", type=int, default=80)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = compare(
            args.docx.resolve(),
            args.parsed.resolve(),
            max(1, args.max_findings),
            max(20, args.min_table_chars),
        )
    except (OSError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
        print(json.dumps({"verdict": "不可用", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if result["verdict"] == "不可用" else 0


if __name__ == "__main__":
    raise SystemExit(main())
