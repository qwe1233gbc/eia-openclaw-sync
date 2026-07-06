# Agent Skills 技能库理论素材

## 1. 收录文献

文件：

`A_Comprehensive_Survey_on_Agent_Skills_arXiv_2605_07358.pdf`

题名：

*A Comprehensive Survey on Agent Skills: Taxonomy, Techniques, and Applications*

作者：

Yingli Zhou, Wang Shu, Yaodong Su, Wenchuan Du, Yixiang Fang, Xuemin Lin

来源：

arXiv:2605.07358

原始链接：

https://arxiv.org/abs/2605.07358

配套资源：

https://github.com/JayLZhou/Awesome-Agent-Skills

## 2. 与本课题的关系

本课题中的“审核技能库”并不是模型微调数据，而是把地方塑胶行业环评技术审查中的可复用审核经验、标准适用步骤和证据核查流程整理为可调用的程序化知识。

该综述对本课题有三个直接参考价值：

1. 为“技能库”提供概念依据：Agent skill 可以理解为具有适用边界、操作步骤、辅助资源和调用条件的可复用过程性知识。
2. 为审核技能库设计提供结构参考：技能可由主说明文档、参考资料、模板、脚本、触发条件和适用范围组成。
3. 为后续论文方法章节提供理论支撑：本课题可将“标准依据库、审核技能库、样本链证据库”视为地方环评审查任务中的领域化技能资源，而大模型主要负责检索、抽取、比对、调用和辅助评分。

## 3. 可借鉴到本课题的内容

| Agent Skills 综述概念 | 本课题中的对应内容 |
|---|---|
| Skill representation | 审核技能条目、标准依据条目、工作流说明、核查表 |
| Skill acquisition | 从佛山市塑胶指南、真实报告、专家修改意见、评审评分表中抽取审核经验 |
| Skill retrieval and selection | 根据审核任务选择对应标准依据、审核步骤和样本链证据 |
| Skill execution | 按固定步骤完成行业分类、建设内容完整性、VOCs、危废、源强、治理措施等审查 |
| Skill evolution and governance | 通过人工复核、专家校准和真实样本链更新技能库 |

## 4. 在论文中的稳妥表述

可表述为：

本研究借鉴 Agent Skills 关于“过程性知识外部化、模块化组织和按需调用”的思想，将地方塑胶行业环评技术审查中的标准依据、审核经验和样本链证据整理为审核技能库。该技能库并非用于替代专家审查，而是为大模型辅助检索、证据定位、问题识别和评分评价提供结构化支撑，最终结果仍需人工复核和专家校准。

不建议表述为：

- 本研究构建了自动审核 Agent。
- 本研究通过技能库替代专家判断。
- 本研究证明大模型可独立完成环评审批。

