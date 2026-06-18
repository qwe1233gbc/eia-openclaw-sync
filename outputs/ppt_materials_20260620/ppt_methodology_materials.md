# 中期汇报PPT素材：方法链各步骤资料整理

> 生成日期: 2026-06-20

## 1_公开资料与内部样本收集

**从佛山市生态环境局官网、微信公众号、顺德审批数据库、内部文件系统收集环评相关材料**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 8行业指南原件 | D:\华南理工项目\佛山市环评报告编制指南（8个行业）\ | 8份PDF |
| [MISS] 525份批复PDF | E:\软件\eia-openclaw-sync\05_样本链_受理公告_终稿_批复_修改意见\批复文件_全量PDF | 525 PDF |
| [MISS] 91份受理公告PDF | E:\软件\eia-openclaw-sync\05_样本链_受理公告_终稿_批复_修改意见\受理公告_全量PDF | 91 PDF |
| [OK] 27个ai_package项目 | E:\openclaw_archive\workspace\agent\workspace\ai_packages_ex | body.md+comments.jsonl |
| [OK] 顺德数据库DM8 | 172.16.168.163:5236 hycx_hb | 11万条审批记录 |
| [OK] 微信公众号文章 | 8行业指南发布文章(2022.08) | 佛山生态环境公众号 |

## 2_塑胶行业涉VOCs样本筛选

**从全量数据中筛选涉胶水/涂布/复合工艺的塑胶行业项目**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 行业关键词表 | E:\软件\eia-openclaw-sync\02_适用行业与样本筛选\sample_filter_keywords. | 30+关键词 |
| [OK] 候选项目清单 | E:\软件\eia-openclaw-sync\02_适用行业与样本筛选\candidate_project_inven | 12项目 |
| [OK] 塑胶指南适用范围 | E:\软件\eia-openclaw-sync\01_塑胶指南原文与适用范围\plastic_guide_scope_s | 适用行业判断表 |
| [OK] 工艺特征检测 | 从27个body.md中检测胶水关键词 | 27个强匹配项目 |

## 3_样本来源分级与证据可追溯性核验

**ABC三级分级管理，不同等级承担不同用途。当前数据集无A类完整链。**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 方法链说明 | E:\软件\eia-openclaw-sync\00_先看这里_README\methodology_chain_v06 | ABC三级定义 |
| [OK] 样本分级CSV | E:\软件\eia-openclaw-sync\05_样本链_受理公告_终稿_批复_修改意见\plastic_proje | 含completeness_level字段 |
| [OK] 经验卡证据映射 | E:\软件\eia-openclaw-sync\outputs\experience_source_file_mappi | 8active+5candidate源文件映射 |

## 4_报告文本解析与证据片段抽取

**MinerU解析PDF报告，提取关键审核段落；ai_package提供结构化报告全文**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 康明新材料厂body.md | 165KB报告全文 | Markdown格式 |
| [OK] 19条原始修改意见 | comments.jsonl | 审核人Word批注提取 |
| [OK] MinerU解析的受理公告 | E:\软件\eia-openclaw-sync\05_样本链_受理公告_终稿_批复_修改意见\受理公告_MinerU解析 | 91份MD |
| [OK] 275条AI升级批注 | E:\软件\eia-openclaw-sync\05_样本链_受理公告_终稿_批复_修改意见\升级修改意见_全量 | 28个项目 |
| [OK] 17份Word原件 | E:\软件\塑胶行业环评报告_Word版_17份.zip | 363MB |

## 5_明文标准库构建(核心)

**从佛山塑胶行业指南51页+16个引用标准中逐章抽取审核要点，每条卡可追溯到具体页码或标准条款**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 综合标准库JSONL | E:\软件\eia-openclaw-sync\03_指南解析_明文标准库\plastic_guide_standard | 71条标准卡 |
| [OK] 标准库MD表格 | E:\软件\eia-openclaw-sync\03_指南解析_明文标准库\plastic_guide_standard | 人读版 |
| [OK] 指南MinerU解析 | E:\软件\eia-openclaw-sync\01_塑胶指南原文与适用范围\plastic_guide_mineru_ | 46个HTML表格 |
| [OK] 来源分布 | guide:57 + standard:12 + local_policy:2 | 17个审核模块 |

## 6_审核工作流规则整理

**Dify工作流实现11条审核规则的自动化，16个yml文件**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 16个Dify工作流 | E:\软件\eia-openclaw-sync\06_Dify工作流 | 16个yml |
| [OK] 工作流知识库 | E:\软件\eia-openclaw-sync\Dify工作流_标准库 | 31个文件 |
| [OK] 合并版工作流 | 环评智能审核_合并版_不迭代.yml | 11条规则全串联 |

## 7_类案经验卡抽取与relevance过滤

**从真实修改意见中提取8条类案经验+5条候选，每条标注适用边界和证据状态**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] Active经验卡 | E:\软件\eia-openclaw-sync\04_顺德类案经验库\experience_cards_active_v | 8条(含relevance字段) |
| [OK] Candidate经验卡 | E:\软件\eia-openclaw-sync\04_顺德类案经验库\experience_cards_candidat | 5条 |
| [OK] Relevance机制 | E:\软件\eia-openclaw-sync\04_顺德类案经验库\experience_relevance_sche | 硬过滤+软分级 |
| [OK] 证据绑定表 | E:\软件\eia-openclaw-sync\04_顺德类案经验库\experience_evidence_bindi | 逐条证据状态标注 |

## 8_seed QA / benchmark构建

**18题主实验+2题备选，基于康明新材料厂（涂布+胶粘剂，完全匹配塑胶指南）**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] v0.6a Benchmark JSONL | E:\软件\eia-openclaw-sync\06_Benchmark最小实验\benchmark_items_mvp | 18+2题 |
| [OK] 评分rubric | E:\软件\eia-openclaw-sync\06_Benchmark最小实验\scoring_rubric_v0_6 | common_6+knowledge_4 |
| [OK] 实验设计文档 | E:\软件\eia-openclaw-sync\06_Benchmark最小实验\v0_6a_experiment_de | ABC三组对照 |
| [OK] 785条人工标注QA | E:\软件\eia-openclaw-sync\05_QA测试集\qa_tasks_for_labeling.json | Label Studio标注 |

## 9_证据链审计与人工复核

**逐条核验标准卡/经验卡/benchmark的证据来源，标注过期标准和处理状态**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] 标准卡修正日志 | E:\软件\eia-openclaw-sync\03_指南解析_明文标准库\standard_card_correcti | 6条修正记录 |
| [OK] 经验卡缺口表 | E:\软件\eia-openclaw-sync\04_顺德类案经验库\experience_evidence_gap_t | 逐条证据缺口 |
| [OK] 过期标准清理 | 806->785条QA, 删除21条引用DB44/814/815的过期标准 |  |

## 10_ABC对照实验验证(核心)

**OpenClaw v0.6a执行18题×3组对照实验，验证标准库和经验库的增量价值**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] A组答案(仅报告) | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\group_A_r | 18条 |
| [OK] B组答案(+标准) | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\group_B_s | 18条 |
| [OK] C组答案(+经验) | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\group_C_s | 18条 |
| [OK] 评分矩阵CSV | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\scoring_m | 55行评分 |
| [OK] 实验总报告 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\openclaw_ |  |
| [OK] 组间对比摘要 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\group_com |  |
| [OK] 标准库命中报告 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\standard_ |  |
| [OK] 经验库命中报告 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\experienc |  |
| [OK] 错误案例分析 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\error_cas | 4类错误 |
| [OK] 经验边界报告 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\experienc |  |
| [OK] 论文关键表格 | E:\软件\eia-openclaw-sync\outputs\openclaw_mvp_v0_6a\v0_6a_key | Group_Deltas等3张表 |

## 11_标准经验双库迭代更新

**根据实验结果和文献支撑，更新标准库/经验库/benchmark，准备下一轮迭代**

| 素材 | 位置 | 规模 |
|------|------|------|
| [OK] v0.5->v0.6升级分析 | E:\软件\eia-openclaw-sync\07_OpenClaw交接材料\v0.6_upgrade_analysi | OpenClaw输出 |
| [OK] v0.6a实验准备包 | 16个文件 | benchmark+relevance+scoring |
| [OK] Codex文献证据包 | E:\软件\eia-openclaw-sync\outputs\codex_literature_2026_06_16 | 4个文献文件 |
| [OK] Codex文献证据包v2 | E:\软件\eia-openclaw-sync\outputs\literature_evidence_20260617 | MD+xlsx+bib |
| [OK] Claude Code脚本库 | E:\软件\eia-openclaw-sync\scripts | 34个脚本,8个分类 |
| [OK] 四智能体协作协议 | E:\软件\eia-openclaw-sync\00_先看这里_README\agent_collaboration_p | GPT+Claude+Codex+OpenClaw |

## PPT制作建议

### 核心slides（5-8页）

1. **封面+研究问题**: 环评智能审核中，标准知识如何结构化？类案经验能否提升审核质量？
2. **方法链总图**: 用流程图展示11步方法链，标注当前进度
3. **标准库**: 71条卡×17模块，展示一条卡的结构(id/module/trigger/requirement/check_evidence)
4. **经验库**: 8条active+5条candidate，展示EXP_03(relevance机制)和EXP_05(pending状态)
5. **Benchmark**: 18题×3组, 展示A/B/C三组的评分差异，标注B-A和C-B增量
6. **实验结果**: 评分矩阵+组间对比摘要+标准库/经验库命中率
7. **证据链审计**: ABC三级分级，当前无A类完整链，诚实标注
8. **下一步**: v0.7计划 + 四智能体协作架构

### 可选slides

- 康明新材料厂案例走查（body.md片段+对应的标准卡+修改意见对照）
- Dify工作流截图
- 文献支撑（Codex文献矩阵）
- 数据规模一览（525批复+91受理+785人工QA）
