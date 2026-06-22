from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = (
    Path(__file__).resolve().parents[1]
    / "03_指南解析_明文标准库"
    / "Dify工作流知识库"
)


def canonicalize_industry_codes() -> tuple[int, list[str]]:
    json_path = ROOT / "national_economic_classification.json"
    jsonl_path = ROOT / "national_economic_classification.jsonl"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    changed = 0
    examples: list[str] = []
    for row in data:
        old = json.dumps(row, ensure_ascii=False, sort_keys=True)
        major = str(row.get("major") or "")
        middle = str(row.get("middle") or "")
        minor = str(row.get("minor") or "")
        if major:
            major = major.zfill(2)
        if middle:
            middle = middle.zfill(3)
        if minor:
            minor = minor.zfill(4)

        row["major"] = major
        row["middle"] = middle
        row["minor"] = minor

        industry_code = minor or middle or major or ""
        row["industry_code"] = industry_code
        row["standard_code"] = f"{row.get('door', '')}{industry_code}" if industry_code else row.get("door", "")

        new = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if old != new:
            changed += 1
            if len(examples) < 8:
                examples.append(f"{row.get('name','')}：{row['standard_code']}")

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return changed, examples


def clean_text(value: str) -> str:
    value = re.sub(r"[\u200b\u200c\u200d\ufeff\t]+", "", value or "")
    value = re.sub(r"<br\s*/?>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def write_emission_quick_reference() -> int:
    source = ROOT / "#9_塑料制品业产污系数_废气.json"
    data = json.loads(source.read_text(encoding="utf-8"))

    preferred_patterns = [
        ("2921", "塑料薄膜制造", "2.50"),
        ("2922", "塑料板、管、型材制造", "1.5"),
        ("2924", "泡沫塑料制造", "1.5"),
        ("2926", "塑料包装箱及容器制造", "2.70"),
        ("2926", "塑料包装箱及容器制造-吸塑/裁切", "1.9"),
        ("2929", "塑料零件及其他塑料制品制造-注塑/挤出", "2.70"),
        ("2929", "塑料零件及其他塑料制品制造-改性粒料造粒", "4.60"),
        ("广东省塑料制品与制造业", "广东省塑料制品成型工序", "2.368"),
        ("佛山市塑胶行业建设项目环评文件编制技术参考指南", "佛山市技术指南表22", "2.7"),
    ]

    rows = []
    used = set()
    for code_hint, label, coef_hint in preferred_patterns:
        for item in data:
            text = " ".join(clean_text(str(item.get(k, ""))) for k in ["标准文件", "表", "类型", "系数", "产品"])
            if code_hint in text and coef_hint in text:
                key = (label, coef_hint)
                if key in used:
                    continue
                used.add(key)
                rows.append(
                    {
                        "label": label,
                        "source": clean_text(str(item.get("标准文件", ""))),
                        "table": clean_text(str(item.get("表", ""))),
                        "type": clean_text(str(item.get("类型", ""))),
                        "coefficient": clean_text(str(item.get("系数", ""))),
                        "scope": clean_text(str(item.get("产品", "")))[:180],
                    }
                )
                break

    out = ROOT / "#9_塑料制品业产污系数_废气_速查.md"
    lines = [
        "# 塑料制品业产污系数_废气_速查",
        "",
        "本文件用于 Dify 检索时快速定位常用废气产污系数。完整抽取数据保留在 `#9_塑料制品业产污系数_废气.json`；正式核算仍应回查原始系数手册、佛山市技术指南或地方指南。",
        "",
        "| 场景 | 来源/表 | 类型 | 系数 | 适用边界提示 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        source_table = f"{row['source']}；{row['table']}"
        lines.append(
            f"| {row['label']} | {source_table} | {row['type']} | {row['coefficient']} | {row['scope']} |"
        )
    lines.extend(
        [
            "",
            "## 使用边界",
            "",
            "- 行业代码与系数手册适用工段不能机械等同，应结合项目产品、原料、工艺和核算口径判断。",
            "- `2929` 不能替代全部塑料项目；薄膜、板管型材、泡沫、包装容器、日用塑料等应优先按对应小类判断。",
            "- 涉胶黏剂复合、印刷、熟化、涂胶等工序，应同时核查佛山市塑胶指南、VOCs 无组织控制要求和项目原辅材料。",
        ]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def write_classification_note() -> None:
    text = """# 塑料/橡胶相关国民经济行业分类校验说明

本说明用于 Dify 工作流检索时约束塑料、橡胶及相邻行业代码的适用边界。完整分类数据见 `national_economic_classification.json` 与 `national_economic_classification.jsonl`。

## 已校正字段

- `major` 统一为 2 位大类代码，如 `29`。
- `middle` 统一为 3 位中类代码，如 `292`。
- `minor` 统一为 4 位小类代码，如 `2929`。
- `industry_code` 为当前记录对应的数字代码。
- `standard_code` 统一为“门类 + 数字代码”，如 `C2929`，不再使用 `C292922929` 这类错误拼接。

## 塑料制品业核心边界

| 代码 | 名称 | 适用边界 |
| --- | --- | --- |
| C292 | 塑料制品业 | 以合成树脂为主要原料，经挤塑、注塑、吹塑、压延、层压等工艺加工成型的塑料制品；不包括塑料鞋制造。 |
| C2921 | 塑料薄膜制造 | 农业覆盖、工业/商业/日用包装薄膜。 |
| C2922 | 塑料板、管、型材制造 | 塑料板、管、管件、棒材、薄片、PVC 异型材等。 |
| C2923 | 塑料丝、绳及编织品制造 | 塑料丝、绳、扁条、塑料袋、编织袋、编织布等。 |
| C2924 | 泡沫塑料制造 | 以合成树脂为主要原料，经发泡成型工艺形成内部微孔的塑料制品。 |
| C2925 | 塑料人造革、合成革制造 | 塑料人造革、塑料合成革。 |
| C2926 | 塑料包装箱及容器制造 | 吹塑、注塑等工艺制成的塑料包装箱、容器。 |
| C2927 | 日用塑料制品制造 | 餐厨用具、卫生洁具配件、日用装饰品等日用塑料制品。 |
| C2928 | 人造草坪制造 | 合成纤维植入基布、具备天然草运动性能的人造草。 |
| C2929 | 塑料零件及其他塑料制品制造 | 塑料绝缘零件、密封制品、紧固件、汽车/家具专用零配件，以及未列明的非日用塑料制品。 |

## 相邻行业边界

| 代码 | 名称 | 注意事项 |
| --- | --- | --- |
| C291 | 橡胶制品业 | 以天然橡胶或合成橡胶为原料制造橡胶制品，不应与 C292 塑料制品业混用。 |
| C2651 | 初级形态塑料及合成树脂制造 | 原状/初级形态塑料、合成树脂生产，不能简单归入 C2929。 |
| C2832 | 生物基、淀粉基新材料制造 | 生物基、淀粉基材料生产需与普通塑料制品加工区分。 |
| C4220 | 非金属废料和碎屑加工处理 | 从废料中回收、分类并使其适于进一步加工为新原料的活动，可能归入 C4220。 |

## 本项目使用建议

- 对普通注塑项目，不能默认全部写为 `C2929`；应先看最终产品是否属于薄膜、板管型材、泡沫、包装容器、日用塑料等更具体小类。
- 对涉胶水、涂胶、复合、熟化、印刷或 VOCs 治理项目，行业分类只解决产品/工艺大类，污染源判断还需结合佛山市塑胶指南、系数手册和报告原辅材料章节。
- 对废塑料、再生塑料颗粒、改性造粒项目，应区分“最终产品/半成品塑料制品”与“废料回收、分拣、再加工为新原料”的活动边界。
"""
    (ROOT / "plastic_rubber_industry_classification_checked.md").write_text(text, encoding="utf-8")


def write_index(changed_count: int, quick_rows: int) -> None:
    files = sorted(p.name for p in ROOT.iterdir() if p.is_file())
    groups = {
        "行业分类": [f for f in files if "classification" in f or "行业分类" in f],
        "三线一单": [f for f in files if "三线一单" in f],
        "环境质量与排放标准": [f for f in files if f.startswith(("DB44", "GB_", "HJ_", "#7_", "#8_"))],
        "产污系数": [f for f in files if "产污系数" in f],
        "环境状态公报": [f for f in files if "状态公报" in f],
    }

    lines = [
        "# Dify 工作流知识库文件索引",
        "",
        "本目录已按“结构化主文件 + 可读速查/说明 + 原始标准文本”整理。Dify 导入时优先使用本索引列出的主文件，避免重复导入旧版摘录。",
        "",
        "## 本次整理结果",
        "",
        f"- 已校正 `national_economic_classification.json/jsonl` 的代码字段：{changed_count} 条记录被规范化。",
        f"- 已生成 `#9_塑料制品业产污系数_废气_速查.md`，收录常用废气系数索引 {quick_rows} 条。",
        "- 已新增 `plastic_rubber_industry_classification_checked.md`，用于约束塑料/橡胶行业分类边界。",
        "- 已移除旧版重复摘录、错别字命名文件和被结构化文件覆盖的原始片段。",
        "",
        "## 推荐导入顺序",
        "",
        "1. `plastic_rubber_industry_classification_checked.md`",
        "2. `national_economic_classification.jsonl`",
        "3. `#9_塑料制品业产污系数_废气.json` 与 `#9_塑料制品业产污系数_废气_速查.md`",
        "4. `三线一单_顺德管控单元_完整.json` 与 `三线一单_顺德管控单元准入清单.md`",
        "5. DB44、GB、HJ 等标准文本",
        "",
    ]
    for group, names in groups.items():
        lines.append(f"## {group}")
        lines.append("")
        for name in names:
            lines.append(f"- `{name}`")
        lines.append("")
    (ROOT / "DIFY_KB_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    changed_count, examples = canonicalize_industry_codes()
    quick_rows = write_emission_quick_reference()
    write_classification_note()
    write_index(changed_count, quick_rows)
    print(json.dumps({"changed_count": changed_count, "examples": examples, "quick_rows": quick_rows}, ensure_ascii=False))


if __name__ == "__main__":
    main()
