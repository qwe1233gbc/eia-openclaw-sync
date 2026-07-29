# 210题金标治理工作区

本目录保存候选映射、人工复核队列、趋势/正式实验候选与治理工作簿。所有自动结论均为候选：

- `normalized_judgement_final` 全部留空；
- `gold_review_status` 全部为“未复核”；
- 不得将候选样本用于A/B/C/D实验，直至人工复核并通过冻结门槛；
- 运行 `../scripts/validate_gold_freeze.py` 校验拟冻结记录；
- 本阶段未调用付费模型、未运行GPT评分、未生成实验得分。

主入口为 `环评审核问答_金标治理工作簿_v1.xlsx`，人工复核顺序见
`reports/manual_review_protocol.md`。
