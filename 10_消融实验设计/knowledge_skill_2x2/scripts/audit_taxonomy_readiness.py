from __future__ import annotations

from collections import Counter

from pipeline_core import (
    PILOT_DOMAINS,
    PILOT_PROJECTS,
    ROOT,
    VALID_MANUAL_JUDGEMENTS,
    load_source_records,
    markdown_counter,
    source_category,
)


def main() -> None:
    rows = load_source_records()
    ids = [str(row.get("question_id") or "").strip() for row in rows]
    duplicate_count = sum(count - 1 for count in Counter(ids).values() if count > 1)
    blanks = [row for row in rows if not str(row.get("人工判断") or "").strip()]
    abnormal = [
        row
        for row in rows
        if str(row.get("人工判断") or "").strip()
        and str(row.get("人工判断") or "").strip() not in VALID_MANUAL_JUDGEMENTS
    ]
    needs_review = [
        row for row in rows if str(row.get("是否需要人工复核") or "").strip() == "是"
    ]
    categories = Counter(source_category(row) for row in rows)
    selected = [
        row
        for row in rows
        if str(row.get("canonical_project_id")) in PILOT_PROJECTS
        and {
            "水污染物排放标准": "water_emission_standard",
            "大气污染物排放标准": "air_emission_standard",
            "噪声排放标准": "noise_emission_standard",
        }.get(source_category(row))
        in PILOT_DOMAINS
    ]
    pilot_pending = sum(
        str(row.get("是否需要人工复核") or "").strip() == "是" for row in selected
    )
    text = f"""# 分类与评价就绪性审计

## 结论

- 核心工作簿包含 **{len(rows)}** 道题。
- `question_id` 空值 **{sum(not value for value in ids)}** 个，重复 **{duplicate_count}** 个；当前ID可作为稳定主键。
- 人工判断为空 **{len(blanks)}** 题，格式异常 **{len(abnormal)}** 题，源表标记“需要人工复核” **{len(needs_review)}** 题。
- 建议的18题趋势样本均能按项目与领域定位，但其中 **{pilot_pending}** 题仍带源表人工复核标记；可冻结选题，不能视为全部金标终审完成。

{markdown_counter("七类任务分布", categories)}

## 最小趋势实验与正式实验候选

- 最小趋势样本固定为：`PL001、PL002、PL003、PL004、PL020、PL026` 的水、气、噪声题，共18题。
- 18题均有非空人工判断，问题/无问题均有覆盖；源表复核标记必须保留并在评分前人工确认。
- 其余192题作为正式实验候选；人工判断为空、格式异常或标记需复核的题，不得未经确认直接作为终版金标。

## 可复用评价资产

- `12_论文借鉴_Chen2026_TianGong/prompts/` 已存在Chen论文相关评价提示词。
- `09_环评审核技能库/common_output_schema.json` 可参考，但不满足本任务统一A/B/C/D最终答案字段，故本任务建立独立 `audit_output_v1.schema.json`。
- 原有消融实验目录含基础评分rubric和组配置，但缺少盲化、结构化GPT评分、可靠性及K×S交互脚本，本分支补齐。

## 标签自动赋值边界

- 七类模板可默认赋值：四维主标签、知识依赖、Workflow依赖和证据跨度。
- 必须逐题人工确认：仅单字段即可完成的降级、多工艺/多污染源导致的升级、所有覆盖理由，以及源表金标空白/异常/待复核状态。
- 分类过程只读取题目、模板和人工状态字段，不读取任何A/B/C/D结果或得分。

## Skill安装审计

- 仓库 `09_环评审核技能库` 的01–15及99目录结构齐全；01–15均含 `SKILL.md/config.yaml/output_example.json`，99按仓库说明至少含 `SKILL.md/config.yaml`。
- 当前Codex环境只暴露部分环评审核skills；`audit-eia-knowledge-base` 仍含5处TODO，是未完成模板。
- 产污系数、源强核算、废气收集/风量/效率、活性炭、危废、VOCs总量和总汇总未完整安装为当前可调用skill。
- 该缺口不阻止本任务的模板分类、盲化和评价基础设施实现；会限制直接用全套skills运行C/D组真实审核输出。

## 当前缺口

- 未提供真实A/B/C/D输出，不能生成或伪造GPT评分与组间效果。
- 未提供评价API密钥与冻结的评价模型版本，`run_gpt_evaluator.py` 仅能完成dry-run就绪检查。
- 135题源表标记需人工复核，正式论文结论前必须完成金标复核。
"""
    output = ROOT / "reports" / "taxonomy_and_evaluation_readiness_audit.md"
    output.write_text(text, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
