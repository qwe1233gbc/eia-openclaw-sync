from __future__ import annotations

from collections import Counter

from pipeline_core import ROOT, TAXONOMY_JSONL, markdown_counter, read_jsonl


def main() -> None:
    rows = read_jsonl(TAXONOMY_JSONL)
    sections = ["# 210题分类分布", "", f"- 总题数：{len(rows)}", ""]
    for field, title in [
        ("audit_domain", "审核领域"),
        ("cognitive_level", "认知层级"),
        ("reasoning_type", "推理类型"),
        ("primary_functional_capability", "主要功能能力"),
        ("knowledge_dependency", "知识依赖"),
        ("workflow_dependency", "Workflow依赖"),
        ("evidence_span", "证据跨度"),
    ]:
        sections.extend([markdown_counter(title, Counter(row[field] for row in rows)), ""])
    pending = sum(row["taxonomy_review_required"] for row in rows)
    sections.extend(
        [
            "## 人工复核",
            "",
            f"- 模板默认分类：{sum(row['classification_status'] == 'auto_default' for row in rows)}",
            f"- 因源表金标状态而标记待复核：{pending}",
            "- 当前没有逐题人工覆盖；未来覆盖必须填写 `override_reason`。",
        ]
    )
    (ROOT / "taxonomy" / "taxonomy_distribution_report.md").write_text(
        "\n".join(sections) + "\n", encoding="utf-8"
    )

    final = f"""# 最终分类与GPT评价就绪报告

## 已完成

- 210题均已获得审核领域、认知层级、主推理类型和主要功能能力，并附知识依赖、
  Workflow依赖和证据跨度。
- 210个 `question_id` 均非空且唯一。
- 分类只依据源题目与7类模板，不读取A/B/C/D输出或得分。
- 18题趋势样本的题目ID与分类已冻结。
- 建立A/B/C/D统一的 `audit_output_v1` JSON Schema，`additionalProperties=false`。
- 建立盲化、评分包、结构化GPT评分验证、评审可靠性、分层统计、K/S/交互及
  科学问题方向脚本。
- GPT评分包不包含组别、RAG、Workflow、模型、run_id或依赖度标签。
- 总分由程序复算；依据型幻觉仅指虚构、不适用、过期或无支持依据。

## 待人工确认

- **{pending}** 题因源表人工判断为空、格式异常或“是否需要人工复核=是”而被标记；
  这些标记不代表分类错误，而是金标或题目状态仍需确认。
- 当前210题均采用模板默认分类，尚未进行逐题专家终审；任何后续覆盖必须写
  `override_reason` 并改为 `manual_override`。
- 18题趋势样本中有9题仍带源表人工复核标记，需要在实验运行前确认金标。

## GPT评分流程状态

- 工具链可运行到评分API之前，支持最小模式和正式多评审模式。
- 当前没有真实A/B/C/D统一JSON输出，没有评价API密钥，也没有冻结具体评价模型版本。
- 因此尚未执行144次趋势实验，没有生成或伪造任何模型分数、K/S主效应或交互趋势。
- 当前**尚未满足144次趋势实验的实际评分条件**；需要用户提供/生成四组输出、
  确认18题金标、冻结评价模型并配置API。

## 科学问题与论文结论边界

- 当前分类体系和分析工具足以预注册科学问题分析方法。
- 当前没有真实实验结果，不足以确定协同、独立或拮抗方向。
- 当前不足以形成正式论文效果结论；必须完成真实实验、人工复核、评审可靠性和
  敏感性分析。

## Skill完整性影响

- 仓库内16个审核技能的源文件结构基本完整。
- 当前Codex环境未完整安装全部审核skills，且 `audit-eia-knowledge-base` 为TODO模板。
- 本次分类与评价基础设施已完成；真实C/D组运行前应补齐并冻结实际Skill版本，
  否则不能声称Workflow/Skill条件已一致实现。
"""
    (ROOT / "reports" / "final_taxonomy_and_gpt_evaluation_readiness.md").write_text(
        final, encoding="utf-8"
    )


if __name__ == "__main__":
    main()
