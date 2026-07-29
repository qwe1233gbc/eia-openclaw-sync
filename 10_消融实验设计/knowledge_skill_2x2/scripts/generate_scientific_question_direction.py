from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import read_json, scientific_direction

TEXT = {
    "additive": "地方知识约束与模块化审核流程分别通过哪些审核环节改善大语言模型环评审核，其作用边界是否随任务类型变化？",
    "synergy": "地方知识与Agent Workflow/Skill如何协同减少环评审核中的依据错配与审核遗漏？（协同趋势待正式验证）",
    "antagonism": "地方知识与Agent Workflow/Skill组合时，是否会因知识—流程不一致产生错误传播、流程固化或信息冲突？（拮抗趋势待正式验证）",
    "knowledge_only": "地方审核知识能否减少大模型的依据型幻觉及其任务边界？",
    "workflow_only": "模块化审核流程能否提高长文本环评审核的证据完整性与结论一致性？",
    "neither": "当前无稳定改善，不包装为方法有效；优先检查金标、召回、Skill强度、任务难度、评分器区分度和分类质量。",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("effects", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    value = read_json(args.effects)
    key = scientific_direction(
        value["K_main_effect"], value["S_main_effect"], value["interaction"]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        f"# 科学问题方向\n\n- 结果模式：`{key}`\n- 建议：{TEXT[key]}\n\n"
        "本报告只描述趋势，不声称因果机制。\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
