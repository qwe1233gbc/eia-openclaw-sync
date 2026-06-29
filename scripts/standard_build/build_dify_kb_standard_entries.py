import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STD_DIR = ROOT / "03_指南解析_明文标准库"
KB_DIR = STD_DIR / "Dify工作流知识库"
BASE_JSONL = STD_DIR / "plastic_guide_standard_library_v4_skill_aligned_pilot.jsonl"

OUT_JSONL = STD_DIR / "dify_kb_standard_entries_pilot.jsonl"
OUT_MD = STD_DIR / "dify_kb_standard_entries_pilot.md"
OUT_REPORT = STD_DIR / "dify_kb_standard_entries_parse_report.md"


SKILL_MAP = {
    "industry": ("01", "国民经济行业类别审核"),
    "investment": ("02", "环评投资核算审核"),
    "three_lines": ("03", "三线一单符合性审核"),
    "construction": ("04", "建设内容完整性审核"),
    "quality_status": ("05", "环境质量现状数据审核"),
    "quality_standard": ("06", "环境质量执行标准审核"),
    "emission_standard": ("07", "污染物排放标准审核"),
    "coefficient": ("08", "产污系数适用性审核"),
    "source_strength": ("09", "源强定量核算审核"),
    "collection_form": ("10", "废气收集形式审核"),
    "air_volume": ("11", "废气设计风量审核"),
    "collection_efficiency": ("12", "废气收集效率审核"),
    "carbon": ("13", "活性炭参数审核"),
    "waste": ("14", "危险废物识别审核"),
    "voc_total": ("15", "VOCs总量控制审核"),
}


def clean_text(value):
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"<br\s*/?>", "；", text, flags=re.I)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def short(text, limit=180):
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def std_refs_from_text(text):
    pattern = re.compile(
        r"(GB/T\s*\d{3,5}(?:[-—]\d{2,4})?|GB\s*\d{3,5}(?:[-—]\d{2,4})?|"
        r"HJ\s*\d{2,4}(?:[-—]\d{2,4})?|DB44/?\s*\d{2,4}(?:[-—]\d{2,4})?|"
        r"AQ/T\s*\d{2,4}|环办环评\[\d{4}\]\d+号|生态环境部公告\s*\d{4}年第\d+号)"
    )
    refs = []
    seen = set()
    for match in pattern.findall(text or ""):
        std = clean_text(match).replace("—", "-")
        std = re.sub(r"\s+", " ", std)
        if std not in seen:
            refs.append({"std": std, "clause": "", "text": short(text, 120)})
            seen.add(std)
    return refs


def make_entry(
    module,
    source_file,
    source_section,
    skill_key,
    trigger,
    requirement,
    evidence,
    refs=None,
    notes="",
    source_type="dify_kb",
    page_or_table="",
):
    skill_id, skill_name = SKILL_MAP[skill_key]
    return {
        "module": module,
        "source_type": source_type,
        "source_file": source_file,
        "source_section": source_section,
        "source_page_or_table": page_or_table,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "trigger": trigger if isinstance(trigger, list) else [trigger],
        "requirement": clean_text(requirement),
        "check_evidence": evidence if isinstance(evidence, list) else [evidence],
        "notes": clean_text(notes),
        "standard_refs": refs if refs is not None else std_refs_from_text(requirement),
        "review_status": "manual_check_needed",
        "entry_origin": "dify_kb_parse_pilot",
    }


def load_existing_keys():
    keys = set()
    max_id = 0
    if not BASE_JSONL.exists():
        return keys, max_id
    for line in BASE_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        match = re.match(r"STD_(\d+)", item.get("id", ""))
        if match:
            max_id = max(max_id, int(match.group(1)))
        keys.add(
            (
                clean_text(item.get("source_file")),
                clean_text(item.get("source_section")),
                clean_text(item.get("requirement")),
            )
        )
    return keys, max_id


def add_entries(out, entries):
    seen = {
        (
            clean_text(item.get("source_file")),
            clean_text(item.get("source_section")),
            clean_text(item.get("requirement")),
        )
        for item in out
    }
    for item in entries:
        key = (
            clean_text(item.get("source_file")),
            clean_text(item.get("source_section")),
            clean_text(item.get("requirement")),
        )
        if key in seen or not item.get("requirement"):
            continue
        out.append(item)
        seen.add(key)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv_dicts(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_industry_entries():
    path = KB_DIR / "national_economic_classification.jsonl"
    if not path.exists():
        return []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    keep_codes = {
        "C2651",
        "C291",
        "C2911",
        "C2912",
        "C2913",
        "C2914",
        "C2915",
        "C2916",
        "C2919",
        "C4220",
    }
    entries = []
    for row in rows:
        code = clean_text(row.get("standard_code"))
        if code not in keep_codes:
            continue
        name = clean_text(row.get("name"))
        desc = clean_text(row.get("description"))
        entries.append(
            make_entry(
                "国民经济行业分类",
                "national_economic_classification.jsonl",
                code,
                "industry",
                f"项目可能与{name}或塑料制品业边界混淆",
                f"审核国民经济行业类别时，应核对 {code} {name} 的定义边界。{desc or '如项目产品、原料或工艺与该小类更匹配，应避免简单归入 C2929。'}",
                ["产品方案", "主要原辅材料", "生产工艺", "行业类别说明"],
                [{"std": "GB/T 4754-2017", "clause": code, "text": f"{code} {name}"}],
                notes="从 Dify 知识库行业分类 JSONL 抽取；是否纳入正式库需人工复核。",
            )
        )
    return entries


def parse_pollutant_standard_csv():
    path = KB_DIR / "#8_塑料制品业典型污染源及执行标准.csv"
    entries = []
    for row in read_csv_dicts(path):
        process = clean_text(row.get("工序/污染源"))
        pollutant = clean_text(row.get("主要污染因子"))
        emission_form = clean_text(row.get("排放形式"))
        standard = clean_text(row.get("对应执行标准"))
        limit = clean_text(row.get("排放限值"))
        if not standard:
            continue
        entries.append(
            make_entry(
                "污染物排放标准适用性",
                path.name,
                f"{pollutant}/{emission_form}",
                "emission_standard",
                f"{process or '塑料制品业工序'}产生{pollutant}且为{emission_form}排放",
                f"{process or '塑料制品业相关工序'}产生的{pollutant}采用{emission_form}排放时，应核对执行标准：{standard}；排放限值：{limit or '需结合标准表号进一步核实'}。",
                ["工艺流程", "污染因子识别表", "排放形式", "排放标准章节", "限值表"],
                std_refs_from_text(standard),
                notes="由塑料制品业典型污染源及执行标准 CSV 抽取，表号和限值需人工核对原标准。",
                page_or_table="塑料制品业典型污染源及执行标准",
            )
        )
    return entries


def parse_surface_water_csv():
    path = KB_DIR / "#7_收纳水体地表水执行标准.csv"
    entries = []
    for row in read_csv_dicts(path):
        plant = clean_text(row.get("城镇污水厂简称"))
        outlet = clean_text(row.get("排污口名称"))
        water = clean_text(row.get("受纳水体名称") or row.get("排入水体"))
        quality_class = clean_text(row.get("地表水评价标准"))
        water_standard = clean_text(row.get("地表水执行标准"))
        tailwater_standard = clean_text(row.get("尾水污染物排放标准"))
        if not plant or not water_standard:
            continue
        entries.append(
            make_entry(
                "地表水执行标准",
                path.name,
                f"{plant}/{water}",
                "quality_standard",
                f"项目废水经{plant}或相关污水处理系统排放",
                f"涉及{plant}排口或其受纳水体{water}时，应核对地表水评价类别为{quality_class or '待核实'}；{water_standard}。尾水排放标准应核对：{tailwater_standard or '需结合排水去向进一步核实'}。",
                ["排水去向", "纳污水体", "污水处理厂名称", "地表水功能类别", "尾水排放标准"],
                std_refs_from_text(water_standard + " " + tailwater_standard),
                notes=f"排污口：{outlet}。由顺德收纳水体执行标准 CSV 抽取，需结合项目实际排水去向复核。",
                page_or_table="顺德区污水处理厂受纳水体执行标准",
            )
        )
    return entries


def parse_coefficient_json():
    path = KB_DIR / "#9_塑料制品业产污系数_废气.json"
    entries = []
    seen = set()
    include_terms = (
        "塑料",
        "塑胶",
        "树脂",
        "注塑",
        "挤出",
        "吹塑",
        "吹膜",
        "发泡",
        "造粒",
        "成型",
        "VOCs",
        "挥发性有机",
        "非甲烷",
        "有机废气",
    )
    fuel_only_terms = ("锅炉", "燃烧", "天然气", "液化石油气", "柴油", "NOx", "二氧化硫")
    for row in read_json(path):
        source = clean_text(row.get("标准文件"))
        table = clean_text(row.get("表"))
        typ = clean_text(row.get("类型"))
        coefficient = clean_text(row.get("系数"))
        product = clean_text(row.get("产品"))
        report = clean_text(row.get("环评文件名"))
        all_text = " ".join([source, table, typ, product, report])
        if not any(term in all_text for term in include_terms):
            continue
        if any(term in all_text for term in fuel_only_terms) and not any(
            term in all_text for term in ("塑料", "塑胶", "树脂", "注塑", "挤出", "吹塑", "发泡", "造粒")
        ):
            continue
        key = (source, table, typ, coefficient, short(product, 100))
        if key in seen or not coefficient:
            continue
        seen.add(key)
        entries.append(
            make_entry(
                "产污系数适用性",
                path.name,
                table or typ,
                "coefficient",
                "报告采用塑料制品业废气产污系数进行 VOCs/非甲烷总烃核算",
                f"选用{typ or '废气产污系数'}时，应核对来源文件、行业小类、工艺、活动水平和系数单位是否匹配。候选系数为：{coefficient}；适用说明：{product}",
                ["行业小类", "产品产量或原料用量", "生产工艺", "产污系数来源", "源强核算表"],
                std_refs_from_text(source),
                notes=f"样本来源报告：{report}。该条为样本中出现的系数候选，需回到正式系数手册或指南复核。",
                page_or_table=table,
            )
        )
    return entries


def parse_short_guides():
    entries = []
    entries.extend(
        [
            make_entry(
                "环评投资核算",
                "#2_环评投资核算指南.md",
                "审核要点",
                "investment",
                "报告仅列总投资或环保投资比例异常",
                "总投资额应与项目规模、产能匹配；环保投资应覆盖废气、废水、噪声、固废等治理设施，且费用明细应能与治理工程对应。",
                ["总投资", "环保投资明细", "治理设施清单", "项目规模与产能"],
                [{"std": "环办环评[2020]33号", "clause": "附件2", "text": "建设项目环境影响报告表编制技术要求"}],
            ),
            make_entry(
                "建设内容完整性",
                "#5_建设内容编制完整性指南.md",
                "审核要点",
                "construction",
                "建设内容章节缺少工程组成或改扩建依托关系",
                "建设内容应完整列明主体工程、辅助工程、公用工程、环保工程、储运工程及依托工程；改扩建项目应说明与现有工程的依托关系。",
                ["工程组成表", "平面布置图", "现有工程说明", "依托工程说明"],
                std_refs_from_text("环办环评[2020]33号 附件2; HJ 884"),
            ),
            make_entry(
                "源强定量核算",
                "#10_产污系数定量核算指南.md",
                "核算公式",
                "source_strength",
                "VOCs源强核算缺少公式、活动水平或系数来源",
                "产污系数选用应与行业类别、产品类型和生产工艺匹配；核算公式应完整说明 E=sum(产污系数 x 产量)，并列明活动水平、单位换算和系数来源。",
                ["行业类别", "产品类型", "产量或原料用量", "系数来源", "源强核算过程"],
                std_refs_from_text("HJ 1122-2020 表22; 广东省工业源VOCs减排量核算方法(2023修订版)"),
            ),
        ]
    )

    common_coefficients = [
        ("塑料薄膜(配料-挤出)", "2.50 kg/t"),
        ("塑料包装容器", "2.70 kg/t"),
        ("日用塑料制品", "2.70 kg/t"),
        ("泡沫塑料(模塑发泡)", "30 kg/t"),
    ]
    for product, coefficient in common_coefficients:
        entries.append(
            make_entry(
                "产污系数适用性",
                "#10_产污系数定量核算指南.md",
                product,
                "coefficient",
                f"报告采用{product}相关 VOCs 产污系数",
                f"{product}常见 VOCs/废气产污系数候选值为 {coefficient}。使用时应核对行业小类、工艺路线和活动水平，不能仅按“塑料制品”笼统套用。",
                ["行业小类", "产品名称", "工艺路线", "产量", "系数来源"],
                std_refs_from_text("HJ 1122-2020 表22; 广东省工业源VOCs减排量核算方法(2023修订版)"),
                notes="该数值来自 Dify 速查指南，需与正式手册或指南原表复核。",
            )
        )
    return entries


def parse_collection_guides():
    entries = []
    collection_rows = [
        ("密闭负压", "设备/车间密闭，负压收集", "控制风速不作要求"),
        ("包围式集气罩", "三面围挡，一面开口", "开口面控制风速≥0.5m/s"),
        ("外部集气罩", "顶吸/侧吸", "控制风速≥0.3m/s"),
    ]
    for method, desc, requirement in collection_rows:
        entries.append(
            make_entry(
                "废气收集形式",
                "#17_废气收集形式及排气量计算指南.md",
                method,
                "collection_form",
                f"项目采用{method}收集 VOCs 废气",
                f"{method}的适用说明为：{desc}；控制要求为：{requirement}。审核时应判断收集方式是否与设备布局、开口面和污染源位置匹配。",
                ["设备布局", "收集罩形式", "控制风速", "车间密闭情况", "平面布置图"],
                std_refs_from_text("HJ 2026-2013 6.2; GB 37822-2019"),
            )
        )
    entries.append(
        make_entry(
            "废气设计风量",
            "#17_废气收集形式及排气量计算指南.md",
            "排气量计算",
            "air_volume",
            "报告给出设计风量但缺少罩口面积或控制风速",
            "排气量可按 Q = 3600 x F x v 进行核算，其中 F 为罩口面积，v 为控制风速；多罩口并联时还应核对支路阻力平衡。",
            ["罩口面积", "控制风速", "罩口数量", "并联系统阻力", "设计风量计算表"],
            std_refs_from_text("HJ 2026-2013 6.2; GB 37822-2019"),
        )
    )

    speed_rows = [("支管", "8-12 m/s"), ("主管", "10-15 m/s"), ("排气筒出口", "15-20 m/s")]
    for pipe, speed in speed_rows:
        entries.append(
            make_entry(
                "废气设计风量",
                "#18_废气收集风量与设计风量核算指南.md",
                pipe,
                "air_volume",
                f"废气收集系统涉及{pipe}风速核算",
                f"{pipe}风速候选控制范围为 {speed}；设计风量应覆盖所有收集点，并与风机风量、风压和系统阻力匹配。",
                ["管道类型", "设计风速", "设计风量", "风机参数", "系统阻力"],
                std_refs_from_text("HJ 2026-2013 6.2; 广东省工业源VOCs减排量核算方法(2023修订版)"),
                notes="风速范围来自 Dify 速查指南，需结合正式规范和工程设计复核。",
            )
        )
    entries.append(
        make_entry(
            "废气设计风量",
            "#18_废气收集风量与设计风量核算指南.md",
            "排气筒高度",
            "air_volume",
            "报告设置有组织废气排气筒",
            "有组织废气排气筒高度候选审核要求为不低于 15 m；实际适用时应结合排放标准、周边建筑物和地方要求进一步核实。",
            ["排气筒高度", "周边建筑物", "排放标准", "平面布置图"],
            std_refs_from_text("HJ 2026-2013 6.2"),
            notes="该条为速查规则，正式审查需回到排放标准及地方要求。",
        )
    )

    efficiency_rows = [
        ("单层密闭负压", "95%"),
        ("单层密闭正压", "85%"),
        ("双层密闭空间", "99%"),
        ("设备排气口直连", "95%"),
        ("包围式(风速≥0.5m/s)", "80%"),
        ("包围式(风速0.3-0.5m/s)", "60%"),
        ("外部式(风速≥0.5m/s)", "40%"),
        ("外部式(风速0.3-0.5m/s)", "20-40%"),
        ("无收集设施", "0%"),
    ]
    for method, efficiency in efficiency_rows:
        entries.append(
            make_entry(
                "废气收集效率",
                "#19_废气收集效率判定指南.md",
                method,
                "collection_efficiency",
                f"报告按{method}取废气收集效率",
                f"{method}对应的收集效率候选值为 {efficiency}。审核时应核对收集形式、密闭负压证据、控制风速计算和取值是否超过对应方式上限。",
                ["收集形式", "密闭条件", "控制风速", "效率取值依据", "源强核算表"],
                std_refs_from_text("广东省工业源VOCs减排量核算方法(2023修订版) 表23"),
                notes="效率值来自 Dify 速查指南，需与正式核算方法表格复核。",
            )
        )
    return entries


def strip_table_fragment(raw):
    parts = [clean_text(part) for part in raw.strip().strip("|").split("|")]
    parts = [part for part in parts if part]
    return " ".join(parts)


def split_three_line_requirements(rows):
    requirements = []
    current = []
    for raw in rows:
        text = strip_table_fragment(raw)
        if not text:
            continue
        starts = [m.start() for m in re.finditer(r"\d+(?:-\d+)?\.", text)]
        if starts:
            if current:
                requirements.append(clean_text("".join(current)))
                current = []
            for index, start in enumerate(starts):
                end = starts[index + 1] if index + 1 < len(starts) else len(text)
                segment = text[start:end]
                if index + 1 < len(starts):
                    requirements.append(clean_text(segment))
                else:
                    current = [segment]
        elif current:
            current.append(text)
    if current:
        requirements.append(clean_text("".join(current)))
    return requirements


def parse_three_lines_entries():
    path = KB_DIR / "三线一单_顺德管控单元_完整.json"
    if not path.exists():
        return []
    data = read_json(path)
    keywords = ("挥发性有机物", "VOCs", "低VOCs", "无组织排放", "高挥发性", "粉尘", "氮氧化物")
    entries = []
    seen_req = set()
    for block in data:
        rows = block.get("rows", [])
        unit_code = ""
        unit_name = ""
        for raw in rows:
            text = strip_table_fragment(raw)
            if text.startswith("ZH"):
                parts = [clean_text(p) for p in raw.strip("|").split("|")]
                unit_code = parts[0] if parts else ""
                unit_name = parts[5] if len(parts) > 5 else ""
        for text in split_three_line_requirements(rows):
            if not any(k in text for k in keywords):
                continue
            text = re.sub(r"^\d+\.", "", text)
            if text in seen_req:
                continue
            seen_req.add(text)
            entries.append(
                make_entry(
                    "三线一单符合性",
                    path.name,
                    unit_code or "顺德区管控单元",
                    "three_lines",
                    "项目位于顺德区管控单元且涉及 VOCs、粉尘或大气污染物排放",
                    f"三线一单符合性分析应核对管控单元{unit_name or '名称'}及其准入要求：{text}",
                    ["项目位置", "管控单元编码", "管控单元名称", "准入清单对照表", "VOCs或大气污染物排放说明"],
                    [],
                    notes="从顺德管控单元完整 JSON 中按 VOCs/大气相关关键词抽取，需结合项目具体位置和最新管控成果复核。",
                )
            )
    return entries


def assign_ids(entries, start):
    for i, item in enumerate(entries, start + 1):
        item["id"] = f"STD_{i:03d}"
    return entries


def write_jsonl(entries):
    with OUT_JSONL.open("w", encoding="utf-8") as f:
        for item in entries:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_md(entries):
    by_skill = defaultdict(list)
    by_source = Counter()
    for item in entries:
        by_skill[item["skill_name"]].append(item)
        by_source[item["source_file"]] += 1

    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Dify 工作流知识库解析标准库条目（候选）\n\n")
        f.write("> 说明：本文件由 `scripts/standard_build/build_dify_kb_standard_entries.py` 从 `Dify工作流知识库` 中的结构化文件、速查表和指南片段自动解析生成。所有条目均为候选条目，默认标记为 `manual_check_needed`，需人工核对标准原文、表号、限值和适用边界后再并入正式标准库。\n\n")
        f.write(f"- 候选条目数：{len(entries)}\n")
        f.write("- 条目用途：支撑塑胶项目环评审核中的行业分类、建设内容、源强核算、排放标准、废气收集、三线一单和水环境标准核对。\n")
        f.write("- 使用边界：本文件不等同于正式标准文本，也不构成最终金标答案。\n\n")

        f.write("## 按审核技能分布\n\n")
        f.write("| 审核技能 | 条目数 |\n| --- | ---: |\n")
        for skill, items in sorted(by_skill.items()):
            f.write(f"| {skill} | {len(items)} |\n")

        f.write("\n## 按来源文件分布\n\n")
        f.write("| 来源文件 | 条目数 |\n| --- | ---: |\n")
        for source, count in by_source.most_common():
            f.write(f"| {source} | {count} |\n")

        f.write("\n## 候选条目\n\n")
        for item in entries:
            f.write(f"### {item['id']} — {item['module']}\n\n")
            f.write(f"- skill: {item['skill_id']} {item['skill_name']}\n")
            f.write(f"- 来源: {item['source_file']}；章节/条款: {item['source_section']}\n")
            if item.get("source_page_or_table"):
                f.write(f"- 页码/表格: {item['source_page_or_table']}\n")
            f.write(f"- 复核状态: {item['review_status']}\n")
            f.write(f"- 触发场景: {'；'.join(item['trigger'])}\n")
            f.write(f"- 审核要求: {item['requirement']}\n")
            f.write(f"- 所需证据: {'；'.join(item['check_evidence'])}\n")
            if item.get("standard_refs"):
                refs = []
                for ref in item["standard_refs"]:
                    parts = [clean_text(ref.get("std")), clean_text(ref.get("clause"))]
                    refs.append(" ".join([p for p in parts if p]))
                f.write(f"- 标准引用: {'；'.join(refs)}\n")
            if item.get("notes"):
                f.write(f"- 备注: {item['notes']}\n")
            f.write("\n")


def write_report(entries):
    by_skill = Counter(item["skill_name"] for item in entries)
    by_source = Counter(item["source_file"] for item in entries)
    with OUT_REPORT.open("w", encoding="utf-8") as f:
        f.write("# Dify 知识库标准条目解析报告\n\n")
        f.write("## 解析范围\n\n")
        f.write("- 行业分类：`national_economic_classification.jsonl` 中与塑料、橡胶、合成树脂、废塑料边界相关的类别。\n")
        f.write("- 排放标准：`#8_塑料制品业典型污染源及执行标准.csv`。\n")
        f.write("- 水环境标准：`#7_收纳水体地表水执行标准.csv`。\n")
        f.write("- 产污系数：`#9_塑料制品业产污系数_废气.json`。\n")
        f.write("- 审核指南：环评投资、建设内容、产污系数、废气收集形式、设计风量、收集效率等速查文件。\n")
        f.write("- 三线一单：`三线一单_顺德管控单元_完整.json` 中 VOCs/大气污染相关要求。\n\n")
        f.write("## 生成结果\n\n")
        f.write(f"- 生成候选条目：{len(entries)} 条\n")
        f.write(f"- JSONL：`{OUT_JSONL.relative_to(ROOT).as_posix()}`\n")
        f.write(f"- Markdown：`{OUT_MD.relative_to(ROOT).as_posix()}`\n\n")
        f.write("## 按技能统计\n\n")
        for skill, count in sorted(by_skill.items()):
            f.write(f"- {skill}: {count} 条\n")
        f.write("\n## 按来源统计\n\n")
        for source, count in by_source.most_common():
            f.write(f"- {source}: {count} 条\n")
        f.write("\n## 人工复核建议\n\n")
        f.write("1. 优先复核排放限值类条目，核对标准名称、表号、污染因子和限值单位。\n")
        f.write("2. 对产污系数类条目，应回到正式系数手册或地方指南，确认行业小类、工艺路线和活动水平。\n")
        f.write("3. 对三线一单条目，应结合项目地理位置和最新管控单元成果，避免把区域通用要求误用到具体项目。\n")
        f.write("4. 对水环境条目，应结合项目实际排水去向和纳污水体，而不是仅按污水厂名称套用。\n")
        f.write("5. 本次输出仅作为标准库扩充候选，不作为最终金标或自动审核结论。\n")


def main():
    _, max_id = load_existing_keys()
    entries = []
    add_entries(entries, parse_industry_entries())
    add_entries(entries, parse_short_guides())
    add_entries(entries, parse_collection_guides())
    add_entries(entries, parse_pollutant_standard_csv())
    add_entries(entries, parse_surface_water_csv())
    add_entries(entries, parse_coefficient_json())
    add_entries(entries, parse_three_lines_entries())
    entries = assign_ids(entries, max_id)
    write_jsonl(entries)
    write_md(entries)
    write_report(entries)
    print(
        json.dumps(
            {
                "entries": len(entries),
                "start_after_existing_std_id": max_id,
                "outputs": [
                    OUT_JSONL.relative_to(ROOT).as_posix(),
                    OUT_MD.relative_to(ROOT).as_posix(),
                    OUT_REPORT.relative_to(ROOT).as_posix(),
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
