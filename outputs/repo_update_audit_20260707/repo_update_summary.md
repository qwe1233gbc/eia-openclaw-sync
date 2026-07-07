# 仓库信息更新记录

> 日期：2026-07-07  
> 目的：检查仓库中与当前研究数据状态不一致的说明文档，并同步到最新口径。

## 1. 本次发现的主要未更新信息

本次遍历后，发现以下信息存在旧口径：

1. 部分文档更新时间仍停留在 2026-06-29。
2. 仍使用“942 条 QA”作为当前主口径。
3. 仍写作“从 942 条 QA 中筛选 30-50 题”。
4. 部分文档未体现 95 条样本链 QA、60 道正式评价候选题和 240 行 A/B/C/D 实验运行表。
5. 部分文档未体现“60 道候选题还不是金标题，需人工复核”的最新判断。
6. 部分文档未体现数据库候选样本链的最新口径：49 个候选项目、196 条 URL。

## 2. 已统一更新的当前口径

当前统一口径如下：

```text
标准库：37 条主标准卡、71 条旧版深度条目、124 条 skill 对齐候选条目
技能库：15 个单项审核 skill + 1 个总审核 skill
QA 主工作簿：seed_qa 主表 1037 行
样本链 QA：95 条
正式评价候选题：60 道
A/B/C/D 实验运行表：240 行
数据库候选样本链：49 个近三年 C292 候选项目、196 条 URL
当前关键任务：补齐 60 道候选题的人工金标证据链
```

## 3. 已更新文件

| 文件 | 更新内容 |
|---|---|
| `00_先看这里_README/README.md` | 增加 2026-07-07 最新状态，补充 95 条样本链 QA、60 道候选题、240 行实验表等信息 |
| `08_进度与缺口报告/current_progress_dashboard.md` | 重写当前进度面板，更新模块状态和下一步任务 |
| `08_进度与缺口报告/missing_materials_and_next_steps.md` | 重写缺口清单，明确最大缺口是人工金标证据链 |
| `13_数据准备_简化版/README.md` | 更新数据准备总览，统一 1037 行 QA、95 条样本链 QA、60 道候选题口径 |
| `13_数据准备_简化版/data_readiness_update_20260706.md` | 修正旧的 942 题表述 |
| `13_数据准备_简化版/missing_and_fix_plan.md` | 修正 QA 分层和金标题建设计划 |
| `13_数据准备_简化版/next_data_preparation_tasks.md` | 将“从 942 条 QA 中筛题”更新为“从 60 道候选题中复核金标题” |
| `12_论文借鉴_Chen2026_TianGong/README.md` | 增加最新 Chen 对标数据状态 |
| `12_论文借鉴_Chen2026_TianGong/data_correspondence_no_finetune.md` | 更新 QA 主版本和正式评价候选题口径 |
| `12_论文借鉴_Chen2026_TianGong/project_data_flow_against_chen2026.md` | 更新数据流中 QA、样本链 QA、verified gold 的对应关系 |
| `12_论文借鉴_Chen2026_TianGong/technical_route_comparison_chen2026_eia.md` | 更新技术路线中的 QA 数量、候选题和 verified gold 计划 |
| `12_论文借鉴_Chen2026_TianGong/data_to_add_checklist.md` | 更新下一步补充数据清单 |

## 4. 保留不改的内容

以下表述虽然包含“自动审批”等关键词，但属于研究边界说明或禁止性表述，应该保留：

- 不做自动审批；
- 不替代人工审批；
- 不评价自动审批能力；
- 不把候选 QA 当作正式 Benchmark。

## 5. 下一步建议

1. 优先填写 `outputs/next_execution_plan_20260706/gold_manual_review_template_60.csv`。
2. 先完成 10-15 道人工复核样例。
3. 对样本链目录做 A/B/C 分级。
4. 将 60 道候选题绑定到主 skill 和标准依据。
5. 完成 40-60 道 verified gold 后再运行 A/B/C/D 实验。

