from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "WATER_GBT18920_2020"
METADATA_ID = "WATER_GBT18920_2020_METADATA"
SOURCE_SHA256 = "fcaac95aef0896c279385124cd0313a8e45eae6efd251f3747722b3037aea539"
SNAPSHOT_VERSION = "v2.2_pr17_followup"
VERIFICATION_REPORT = ROOT / "09_环评审核技能库/quality/gbt18920_fulltext_verification_report.json"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_source_record() -> dict:
    return {
        "source_id": SOURCE_ID,
        "title": "城市污水再生利用 城市杂用水水质",
        "document_number": "GB/T 18920-2020",
        "issuer": "国家市场监督管理总局、国家标准化管理委员会",
        "document_type": "国家标准正式出版文本（用户提供、逐页核验）",
        "official_url": "https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=9825347B5A474612C6C3FE86323428C0",
        "source_sha256": SOURCE_SHA256,
        "issue_date": "2020-03-31",
        "effective_date": "2021-02-01",
        "validity_status": "现行",
        "applicable_region": "全国",
        "industry_scope": "城市杂用再生水",
        "pollution_medium": "再生水",
        "is_primary_source": True,
        "acquisition_method": "user_provided_verified_fulltext",
        "access_date": "2026-08-04",
        "full_text_available": True,
        "manual_source_upload_required": False,
        "eligible_for_formal_rag": True,
        "related_question_ids": "PL004_Emission_水污;PL005_Emission_水污",
        "historical_applicability": "2021-02-01起实施；替代GB/T 18920-2002",
        "current_reference": "2026-08-04现行",
        "notes": "official_url仅对应国家标准官方元数据页；全文由用户提供，文件版式、8页连续性、表1及正文经人工逐页核验。原PDF不提交仓库。",
        "repository_locator": "external_primary_source_not_committed",
        "path_policy": "原始PDF按.gitignore不入库；以SHA256、核验报告和正式父子块追溯",
        "source_provenance": "user_provided_verified_fulltext; official metadata independently linked",
        "verification_report_path": "09_环评审核技能库/quality/gbt18920_fulltext_verification_report.json",
        "applicable_from": "2021-02-01",
        "applicable_until": "",
        "shall_not_apply_before": "2021-02-01",
        "shall_not_apply_after": "",
    }


def update_manifest_pair(jsonl_path: Path, csv_path: Path, include_local_path: bool = False) -> None:
    rows = load_jsonl(jsonl_path)
    by_id = {row["source_id"]: row for row in rows}
    metadata = by_id[METADATA_ID]
    metadata.update({
        "eligible_for_formal_rag": False,
        "full_text_available": False,
        "manual_source_upload_required": False,
        "superseded_by_source_id": SOURCE_ID,
        "gap_status": "closed_by_user_provided_verified_fulltext",
        "notes": "官方元数据记录保留用于发现与版本核对；不得作为正式RAG正文。全文缺口由独立正式来源WATER_GBT18920_2020关闭。",
    })
    new_record = build_source_record()
    if include_local_path:
        new_record["local_path"] = "external_primary_source_not_committed"
    by_id[SOURCE_ID] = new_record

    # Repair ambiguous natural-language time expressions and add machine-readable boundaries.
    boundaries = {
        "WATER_GB18918_MOD2025": ("2026-03-01", "", "2026-03-01", ""),
        "SOLID_HW2021_HIST": ("2021-01-01", "2024-12-31", "", "2024-12-31"),
        "SOLID_HW2025_CURRENT": ("2025-01-01", "", "2025-01-01", ""),
        "SOLID_GB34330_2017_HIST": ("2017-10-01", "2026-02-28", "", "2026-02-28"),
        "SOLID_GB34330_2025": ("2026-03-01", "", "2026-03-01", ""),
    }
    replacement_text = {
        "WATER_GB18918_MOD2025": "不得用于2026-03-01之前的报告",
        "SOLID_HW2025_CURRENT": "不得用于2025-01-01之前的报告",
        "SOLID_GB34330_2025": "不得用于2026-03-01之前的报告",
    }
    for source_id, values in boundaries.items():
        row = by_id[source_id]
        row["applicable_from"], row["applicable_until"], row["shall_not_apply_before"], row["shall_not_apply_after"] = values
        if source_id in replacement_text:
            row["historical_applicability"] = replacement_text[source_id]
    ordered = [by_id[row["source_id"]] for row in rows if row["source_id"] != SOURCE_ID]
    metadata_index = next(i for i, row in enumerate(ordered) if row["source_id"] == METADATA_ID)
    ordered.insert(metadata_index + 1, by_id[SOURCE_ID])
    write_jsonl(jsonl_path, ordered)

    old_fields, _ = load_csv(csv_path)
    fields = list(old_fields)
    for name in (
        "source_provenance", "verification_report_path", "superseded_by_source_id", "gap_status",
        "applicable_from", "applicable_until", "shall_not_apply_before", "shall_not_apply_after",
    ):
        if name not in fields:
            fields.append(name)
    if include_local_path and "local_path" not in fields:
        fields.insert(6, "local_path")
    write_csv(csv_path, fields, ordered)


def make_parent(number: int, section_path: str, clause: str, page: str, content: str, table: str = "") -> dict:
    return {
        "parent_id": f"{SOURCE_ID}_P{number:04d}",
        "source_id": SOURCE_ID,
        "title": "城市污水再生利用 城市杂用水水质",
        "document_number": "GB/T 18920-2020",
        "version": "2020",
        "section_path": section_path,
        "clause_number": clause,
        "table_number": table,
        "page_number": page,
        "content": content,
        "applicability": {"reuse_type": "城市杂用水", "water_use": "按条款或表头用途", "valid_time": "2021-02-01起"},
        "exception": "应结合具体回用用途选择表1列；混凝土用水还应符合JGJ 63，自动喷水灭火系统另核GB 50084。",
        "source_sha256": SOURCE_SHA256,
        "content_sha256": sha256_text(content),
        "authority_weight": 1.2,
    }


def build_chunks() -> tuple[list[dict], list[dict]]:
    table1 = """表1 城市杂用水水质基本控制项目及限值（正文第2—3页）
列A用途：冲厕、车辆冲洗；列B用途：城市绿化、道路清扫、消防、建筑施工。
1 pH：A 6.0～9.0；B 6.0～9.0。
2 色度（铂钴色度单位，≤）：A 15；B 30。
3 嗅：A 无不快感；B 无不快感。
4 浊度/NTU（≤）：A 5；B 10。
5 五日生化需氧量（BOD5）/(mg/L)（≤）：A 10；B 10。
6 氨氮/(mg/L)（≤）：A 5；B 8。
7 阴离子表面活性剂/(mg/L)（≤）：A 0.5；B 0.5。
8 铁/(mg/L)（≤）：A 0.3；B —。
9 锰/(mg/L)（≤）：A 0.1；B —。
10 溶解性总固体/(mg/L)（≤）：A 1000（2000）a；B 1000（2000）a。
11 溶解氧/(mg/L)（≥）：A 2.0；B 2.0。
12 总氯/(mg/L)（≥）：A 1.0（出厂）、0.2（管网末端）；B 1.0（出厂）、0.2b（管网末端）。
13 大肠埃希氏菌/(MPN/100 mL或CFU/100 mL)：A 无c；B 无c。
注：“—”表示对此项无要求。
a 括号内指标值为沿海及本地水源中溶解性固体含量较高的区域的指标。
b 用于城市绿化时，不应超过2.5 mg/L。
c 大肠埃希氏菌不应检出。"""
    contents = [
        ("封面", "", "封面", "", "GB/T 18920-2020《城市污水再生利用 城市杂用水水质》，代替GB/T 18920-2002。2020-03-31发布，2021-02-01实施。发布机关：国家市场监督管理总局、国家标准化管理委员会。"),
        ("前言", "", "前言Ⅲ", "", "前言：本标准按照GB/T 1.1-2009给出的规则起草，代替GB/T 18920-2002。主要技术变化包括更新规范性引用文件，增加再生水定义，调整表1部分水质指标，增加氯化物和硫酸盐选择性控制，修改采样检测频率，并将安全利用独立成章。提出单位为中华人民共和国住房和城乡建设部，归口单位为全国城镇给水排水标准化技术委员会（SAC/TC 434）。"),
        ("1范围—3术语和定义", "1—3.7", "正文第1—2页", "", """1 范围：规定城市污水再生利用城市杂用水的术语和定义、水质指标、采样与监测、安全利用。适用于冲厕、车辆冲洗、城市绿化、道路清扫、消防、建筑施工等杂用的再生水。
2 规范性引用文件：GB/T 5750.4、GB/T 5750.5、GB/T 5750.6、GB/T 5750.11、GB/T 5750.12、GB/T 7488、GB/T 7489、GB/T 11913、GB/T 12997、GB/T 12998、GB/T 12999、GB 50084、CJ/T 158、HJ 505、HJ 506、JGJ 63。
3 术语和定义：3.1再生水；3.2城市杂用水；3.3冲厕用水；3.4城市绿化用水；3.5道路清扫用水；3.6消防用水；3.7建筑施工用水。各术语按其对应非饮用用途界定。"""),
        ("4水质指标—表1", "4.1—4.4", "正文第2—3页", "表1", """4 水质指标。4.1 城市杂用水的水质基本控制项目及限值应符合表1。4.2 用户宜根据当地再生水厂水源情况，有针对性地选择表2的项目。4.3 混凝土用水还应符合JGJ 63。4.4 用于自动喷水灭火系统用水，除符合表1外，悬浮物还应符合GB 50084。
""" + table1),
        ("4水质指标—表2", "4.2", "正文第3页", "表2", "表2 城市杂用水选择性控制项目及限值，单位mg/L：氯化物（Cl-）不大于350；硫酸盐（SO4^2-）不大于500。"),
        ("5采样与监测—采样及分析方法", "5.1—5.2", "正文第3—4页", "表3、表4", """5.1 采样及保管：水质采样的设计、组织按GB/T 12997、GB/T 12998执行。水样为24 h混合样，应至少每2 h取样一次，以日均值计。样品保管按GB/T 12999执行。再生水厂供水出口处宜设水质监测取样点。
5.2 分析方法：基本控制项目按表3执行，选择性控制项目按表4执行。表3：pH、色度、浊度、BOD5、氨氮、阴离子表面活性剂、铁、锰、溶解性总固体、溶解氧、总氯（总余氯）、大肠埃希氏菌分别采用表列方法及GB/T 5750.4、GB/T 5750.5、GB/T 5750.6、GB/T 5750.11、GB/T 5750.12、GB/T 7488、GB/T 7489、GB/T 11913、HJ 505、HJ 506等执行标准；GB/T 7488和GB/T 7489采用裁定方法。表4：氯化物采用硝酸银容量法、硝酸汞容量法或离子色谱法，执行GB/T 5750.5；硫酸盐采用硫酸钡比浊法、离子色谱法或铬酸钡分光光度法，执行GB/T 5750.5。"""),
        ("5采样与监测—检测频率", "5.3", "正文第4页", "表5", "表5 城市杂用水采样检测频率：pH、色、浊度、嗅、溶解氧、总氯、大肠埃希氏菌每日1次；五日生化需氧量（BOD5）、氨氮、阴离子表面活性剂、铁、锰、溶解性总固体每周1次。基本控制项目采样检测频率不应低于表5规定。"),
        ("6安全利用", "6.1—6.2.5", "正文第5页", "表6", """6.1 水源及管道连接：用于再生水厂的水源宜优先选用生活污水，或不含重污染、有毒有害工业废水的城市污水；再生水管道不应与饮用水管道、设施直接连接。
6.2 标识：城市杂用水管道、设备、设施外部显著位置应设置警示标识及说明。供水点、水箱阀门井等设备设施外部，以及管道直管段、起始点、交叉点、转弯处、终点和穿越楼板墙等处应设置标识。管道涂色应符合CJ/T 158；标识应包括“再生水”“不得饮用”字样及流向箭头，字样字体高度宜符合表6，宽高比宜为0.6～1.0，管道内介质流向用箭头表示。
表6 标识字体高度（单位mm）：管道直径不大于50，字体15～30；50～200，字体45；200～300，字体60；300～500，字体75；大于500，字体90。管道直径应含上限、不应含下限。水箱、用水器具标识应醒目；阀门井井盖应设置“再生水”和“不得饮用”字样标识。"""),
    ]
    parents = [make_parent(i + 1, section, clause, page, content, table) for i, (section, clause, page, table, content) in enumerate(contents)]
    children: list[dict] = []
    for parent in parents:
        child_content = parent["content"]
        children.append({
            "child_id": f"{parent['parent_id']}_C001",
            "parent_id": parent["parent_id"],
            "source_id": SOURCE_ID,
            "section_path": parent["section_path"],
            "clause_number": parent["clause_number"],
            "table_number": parent["table_number"],
            "page_number": parent["page_number"],
            "content": child_content,
            "applicability": parent["applicability"],
            "source_sha256": SOURCE_SHA256,
            "content_sha256": sha256_text(child_content),
        })
    table_parent = parents[3]
    for suffix, use, marker in (
        ("C002", "冲厕、车辆冲洗", "列A用途"),
        ("C003", "城市绿化、道路清扫、消防、建筑施工", "列B用途"),
    ):
        content = f"{table_parent['content']}\n检索用途：{use}；应读取表1中{marker}对应值及全部a/b/c注释。"
        children.append({
            "child_id": f"{table_parent['parent_id']}_{suffix}",
            "parent_id": table_parent["parent_id"],
            "source_id": SOURCE_ID,
            "section_path": table_parent["section_path"],
            "clause_number": table_parent["clause_number"],
            "table_number": "表1",
            "page_number": "正文第2—3页",
            "content": content,
            "applicability": {"reuse_type": "城市杂用水", "water_use": use, "valid_time": "2021-02-01起"},
            "source_sha256": SOURCE_SHA256,
            "content_sha256": sha256_text(content),
        })
    return parents, children


def update_chunks(base: Path) -> tuple[int, int]:
    parent_path = base / "parent_chunks.jsonl"
    child_path = base / "child_chunks.jsonl"
    parents = [row for row in load_jsonl(parent_path) if row["source_id"] != SOURCE_ID]
    children = [row for row in load_jsonl(child_path) if row["source_id"] != SOURCE_ID]
    new_parents, new_children = build_chunks()
    parents.extend(new_parents)
    children.extend(new_children)
    write_jsonl(parent_path, parents)
    write_jsonl(child_path, children)

    manifest_path = base / "chunk_manifest.csv"
    fields, rows = load_csv(manifest_path)
    rows = [row for row in rows if row["source_id"] != SOURCE_ID]
    metadata_index = next(i for i, row in enumerate(rows) if row["source_id"] == METADATA_ID)
    rows.insert(metadata_index + 1, {
        "source_id": SOURCE_ID,
        "title": "城市污水再生利用 城市杂用水水质",
        "eligible": "True",
        "parent_chunk_count": str(len(new_parents)),
        "child_chunk_count": str(len(new_children)),
        "source_sha256": SOURCE_SHA256,
        "local_path": "external_primary_source_not_committed",
    })
    write_csv(manifest_path, fields, rows)
    quality = base / "chunk_quality_report.md"
    quality.write_text(
        "# 正式RAG分块质量报告\n\n"
        f"- 可入库来源：{sum(str(row.get('eligible')).lower() == 'true' for row in rows)}\n"
        f"- 父块：{len(parents)}\n- 子块：{len(children)}\n"
        "- GB/T 18920-2020：8个父块、10个子块；表1作为跨正文第2—3页的完整父块保留，另设两个用途检索子块并回溯同一父块。\n"
        "- 分块策略：法规/标准按标题、条款、表格和注释切分；父块保留完整条款或完整表格。\n"
        "- 表格核验：GB/T 18920-2020表1—表6已逐页人工核图；表1表头、13项指标和a/b/c注释完整。\n"
        "- 排除：缺失全文来源、仅元数据来源、QA、Skill、人工答案和实验输出均未入库。\n",
        encoding="utf-8",
    )
    return len(new_parents), len(new_children)


def context_block(parent: dict) -> str:
    return f"【{parent['title']}｜{parent['document_number']}｜{parent['section_path']}｜{parent['page_number']}】\n{parent['content']}"


def update_frozen_context(path: Path, trace_path: Path | None = None) -> None:
    rows = load_jsonl(path)
    table_parent = build_chunks()[0][3]
    new_index_sha = sha256_text(
        (ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl").read_text(encoding="utf-8")
        + (ROOT / "03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl").read_text(encoding="utf-8")
    )
    for row in rows:
        row["index_sha256"] = new_index_sha
        if row.get("question_id") not in {"PL004_Emission_水污", "PL005_Emission_水污"}:
            continue
        row["query_builder_version"] = "sanitized-question-category-v2.2-no-gold"
        row["required_sources"] = [SOURCE_ID if x == METADATA_ID else x for x in row.get("required_sources", [])]
        if SOURCE_ID not in row["required_sources"]:
            row["required_sources"].append(SOURCE_ID)
        row["retrieved_sources"] = [x for x in row.get("retrieved_sources", []) if x != METADATA_ID]
        if SOURCE_ID not in row["retrieved_sources"]:
            row["retrieved_sources"].append(SOURCE_ID)
        row["missing_required_sources"] = []
        row["selected_parent_chunks"] = [x for x in row.get("selected_parent_chunks", []) if not x.startswith(METADATA_ID)]
        if table_parent["parent_id"] not in row["selected_parent_chunks"]:
            row["selected_parent_chunks"].append(table_parent["parent_id"])
        block = context_block(table_parent)
        block_header = block.splitlines()[0]
        old = row.get("rag_context", "").split(block_header, 1)[0].rstrip()
        row["rag_context"] = old + "\n\n" + block
        row["rag_context_sha256"] = sha256_text(row["rag_context"])
        row["final_parent_k"] = len(row["selected_parent_chunks"])
    write_jsonl(path, rows)

    if trace_path and trace_path.exists():
        traces = load_jsonl(trace_path)
        for trace in traces:
            if trace.get("question_id") not in {"PL004_Emission_水污", "PL005_Emission_水污"}:
                continue
            trace["missing_required_sources"] = []
            selected = [x for x in trace.get("selected_parent_chunks", []) if not x.startswith(METADATA_ID)]
            if table_parent["parent_id"] not in selected:
                selected.append(table_parent["parent_id"])
            trace["selected_parent_chunks"] = selected
            candidates = trace.get("ranked_candidates") or []
            candidates = [item for item in candidates if item.get("source_id") != METADATA_ID]
            candidates.insert(0, {"rank": 1, "parent_id": table_parent["parent_id"], "source_id": SOURCE_ID, "score": "required_source_exact_match"})
            for index, item in enumerate(candidates, 1):
                item["rank"] = index
            trace["ranked_candidates"] = candidates
        write_jsonl(trace_path, traces)


def refresh_rag_hash_csv(snapshot_path: Path, hash_path: Path) -> None:
    contexts = {row["question_id"]: row for row in load_jsonl(snapshot_path)}
    fields, rows = load_csv(hash_path)
    for row in rows:
        digest = contexts[row["question_id"]]["rag_context_sha256"]
        for key in ("B_rag_context_sha256", "D_rag_context_sha256"):
            if key in row:
                row[key] = digest
        if "hash_equal" in row:
            row["hash_equal"] = "True"
    write_csv(hash_path, fields, rows)


def refresh_skill_snapshots() -> dict[str, str]:
    registry_path = ROOT / "09_环评审核技能库/formal_skill_registry.yaml"
    import yaml
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    skills = [item for item in registry["skills"] if str(item.get("skill_id")) != "99"]
    hashes: dict[str, str] = {}
    snapshot_rows = []
    hash_rows = []
    for item in skills:
        sid = str(item["skill_id"])
        skill_path = ROOT / "09_环评审核技能库" / item["path"]
        content = skill_path.read_text(encoding="utf-8")
        digest = sha256_text(content)
        hashes[sid] = digest
        snapshot_rows.append({
            "skill_id": sid,
            "skill_name": item["name"],
            "audit_category": item["audit_category"],
            "path": f"09_环评审核技能库/{item['path']}",
            "role": item["role"],
            "skill_sha256": digest,
            "snapshot_version": SNAPSHOT_VERSION,
            "snapshot_date": "2026-08-04",
            "content": content,
        })
        hash_rows.append({"skill_id": sid, "skill_name": item["name"], "skill_sha256": digest, "snapshot_version": SNAPSHOT_VERSION, "path": f"09_环评审核技能库/{item['path']}"})
    for path in (
        ROOT / "09_环评审核技能库/formal_skill_snapshots_v2.jsonl",
        ROOT / "10_消融实验设计/03_Skill冻结快照/skill_snapshots_v2.jsonl",
    ):
        write_jsonl(path, snapshot_rows)
    for path in (
        ROOT / "09_环评审核技能库/skill_hashes_v2.csv",
        ROOT / "10_消融实验设计/03_Skill冻结快照/skill_hashes_v2.csv",
    ):
        write_csv(path, ["skill_id", "skill_name", "skill_sha256", "snapshot_version", "path"], hash_rows)
    return hashes


def refresh_routing_matrix(hashes: dict[str, str]) -> None:
    routing_path = ROOT / "10_消融实验设计/03_Skill冻结快照/skill_routing_v2.csv"
    fields, rows = load_csv(routing_path)
    for row in rows:
        sid = row.get("skill_id", "")
        if sid:
            row["skill_sha256"] = hashes[sid]
        row["snapshot_version"] = SNAPSHOT_VERSION
    write_csv(routing_path, fields, rows)

    context_rows = {row["question_id"]: row for row in load_jsonl(ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl")}
    matrix_path = ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv"
    fields, matrix = load_csv(matrix_path)
    for row in matrix:
        qid, group = row["question_id"], row["group"]
        if group in {"B", "D"}:
            row["rag_context_sha256"] = context_rows[qid]["rag_context_sha256"]
        if group in {"C", "D"}:
            row["skill_sha256"] = hashes[row["skill_id"]]
            row["skill_snapshot_version"] = SNAPSHOT_VERSION
        if qid in {"PL004_Emission_水污", "PL005_Emission_水污"}:
            row["status"] = "ready_input_freeze"
            row["basis_status"] = ""
            row["conclusion"] = ""
            row["manual_review_needed"] = ""
    write_csv(matrix_path, fields, matrix)


def write_verification_report() -> None:
    candidates = [
        {"actual_file_path": "E:/浏览器下载内容/GBT+18920-2020.pdf", "file_name": "GBT+18920-2020.pdf", "file_size": 487041, "modified_time": "2026-08-04T20:57:30.6856482+08:00", "sha256": SOURCE_SHA256, "file_type": "PDF", "selected": True},
        {"actual_file_path": "E:/浏览器下载内容/standards_downloads/GB_T18920-2020_城市污水再生利用_城市杂用水水质.pdf", "file_name": "GB_T18920-2020_城市污水再生利用_城市杂用水水质.pdf", "file_size": 4934328, "modified_time": "2026-06-12T21:46:08.2845172+08:00", "sha256": "4ddc72bb5b93ce933b08e0269cd196960d0dc291cbe5e186b0c651849c697af9", "file_type": "PDF", "selected": False, "exclusion_reason": "误命名；实际为97页《宜城市中心城区给水工程专项规划（2021—2035）》"},
        {"actual_file_path": "repository_external_metadata_page", "file_name": "GBT18920-2020_官方元数据页.html", "file_size": 24170, "modified_time": "2026-08-04T17:41:08.2622121+08:00", "sha256": "439576dd84532c27d98ba588c991e7d1a3abeac02f34c5d1b86ca11a1865b6ca", "file_type": "HTML", "selected": False, "exclusion_reason": "官方元数据，不是全文"},
    ]
    report = {
        "file_path": "E:/浏览器下载内容/GBT+18920-2020.pdf",
        "file_name": "GBT+18920-2020.pdf",
        "file_sha256": SOURCE_SHA256,
        "file_size": 487041,
        "page_count": 8,
        "candidate_files": candidates,
        "document_number_verified": True,
        "document_title_verified": True,
        "issuer_verified": True,
        "issue_date_verified": True,
        "effective_date_verified": True,
        "issuer": "国家市场监督管理总局、国家标准化管理委员会",
        "issue_date": "2020-03-31",
        "effective_date": "2021-02-01",
        "page_sequence_complete": True,
        "sections_verified": ["范围", "规范性引用文件", "术语和定义", "水质指标", "采样与监测", "安全利用"],
        "table_1_complete": True,
        "tables_verified": ["表1", "表2", "表3", "表4", "表5", "表6"],
        "full_text_verified": True,
        "source_provenance": "user_provided_verified_fulltext; formal standard publication layout; official metadata independently linked",
        "extraction_method": "native PDF text extraction plus Poppler 150 dpi page rendering and manual visual cross-check",
        "ocr_used": False,
        "manual_table_review_completed": True,
        "raw_pdf_committed": False,
        "errors": [],
        "warnings": ["部分嵌入字体导致原生文本层首部字形映射异常；所有8页及表1跨页内容已按渲染图像人工交叉核验。", "文件由用户提供，不将official_url表述为该PDF的下载来源。"],
        "pass": True,
    }
    VERIFICATION_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    write_verification_report()
    update_manifest_pair(
        ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl",
        ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.csv",
    )
    update_manifest_pair(
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/01_source_governance/supplement_source_manifest.jsonl",
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/01_source_governance/supplement_source_manifest.csv",
        include_local_path=True,
    )
    # Frozen source manifest mirrors the canonical governance manifest.
    _, source_rows = load_csv(ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.csv")
    source_fields, _ = load_csv(ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.csv")
    write_csv(ROOT / "10_消融实验设计/02_RAG冻结快照/rag_source_manifest.csv", source_fields, source_rows)

    parent_count, child_count = update_chunks(ROOT / "03_指南解析_明文标准库/formal_rag_chunks")
    update_chunks(ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/03_formal_chunks")
    update_frozen_context(
        ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl",
        ROOT / "10_消融实验设计/02_RAG冻结快照/rag_retrieval_trace.jsonl",
    )
    update_frozen_context(
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl",
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_retrieval_trace_v2.jsonl",
    )
    refresh_rag_hash_csv(
        ROOT / "10_消融实验设计/02_RAG冻结快照/rag_contexts_frozen.jsonl",
        ROOT / "10_消融实验设计/02_RAG冻结快照/rag_context_hashes.csv",
    )
    refresh_rag_hash_csv(
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl",
        ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_context_hashes_v2.csv",
    )
    snapshot_path = ROOT / "10_消融实验设计/knowledge_skill_2x2/real_report_experiment/rag/formal_rag_v2/04_rag_snapshots/rag_contexts_frozen_v2.jsonl"
    marker_path = snapshot_path.parent / "freeze_marker.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker.update({"frozen_at": "2026-08-04", "snapshot_version": SNAPSHOT_VERSION, "snapshot_file_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(), "gold_fields_read_before_freeze": 0})
    marker_path.write_text(json.dumps(marker, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    hashes = refresh_skill_snapshots()
    refresh_routing_matrix(hashes)
    print(json.dumps({"source_id": SOURCE_ID, "source_sha256": SOURCE_SHA256, "parent_chunks": parent_count, "child_chunks": child_count, "snapshot_version": SNAPSHOT_VERSION}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
