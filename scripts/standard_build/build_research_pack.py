#!/usr/bin/env python3
"""Build eia_plastic_guide_research_pack"""
import os, json, csv, shutil, time
from pathlib import Path

BASE = Path(r"E:\软件\eia_plastic_guide_research_pack")
ts = time.strftime('%Y-%m-%d %H:%M:%S')
GUIDE_FULL = "佛山市塑胶行业建设项目环评文件编制技术参考指南（试行）"

# =====================================================
# CREATE DIRECTORIES
# =====================================================
dirs = [
    "00_先看这里_README",
    "01_塑胶指南原文与适用范围",
    "02_适用行业与样本筛选",
    "03_指南解析_明文标准库",
    "04_顺德类案经验库",
    "05_样本链_受理公告_终稿_批复_修改意见",
    "06_Benchmark最小实验",
    "07_OpenClaw交接材料",
    "08_进度与缺口报告",
    "99_原始文件路径索引",
]
for d in dirs:
    (BASE / d).mkdir(parents=True, exist_ok=True)
print(f"Created {len(dirs)} directories")

# =====================================================
# 00_README
# =====================================================
readme = f"""# 佛山市塑胶指南适用行业 研究材料包

> 生成时间: {ts}
> 定位: 不是全量资料仓库，是"塑胶指南适用行业研究材料包"

## 当前研究主线

**《{GUIDE_FULL}》的适用范围研究。**

核心行业方向不是普通 C2929 注塑，而是：
**C292 塑料制品业中涉胶水、涂胶、贴合/复合、熟化、塑料薄膜、塑料包装材料、塑塑复合、塑铝复合、涉 VOCs 治理的塑胶制造项目。**

## 为什么重点行业改了

盛之强实验发现：C2929 纯注塑项目不涉胶水，指南只能参照使用，不能作为主要审核依据。真正完全适用指南的项目是有胶水/复合工艺的塑胶项目。

## 标准库 vs 经验库

| 类型 | 是什么 | 作用 |
|------|--------|------|
| 标准库/明文依据库 | 来自国家报告表指南、佛山塑胶指南、排放标准和技术规范 | 告诉 AI：依据是什么、报告应提供哪些证据、公式/限值/参数是什么 |
| 经验库/类案经验库 | 来自顺德已审报告、修改意见、真实批注和同类项目 | 告诉 AI：类似项目经办人会追问什么、哪里容易出错、需要补什么证据 |

## 受理公告 / 终稿 / 批复 / 修改意见 分别怎么用

| 文件类型 | 角色 | 用途 |
|----------|------|------|
| 受理公告报告 | 待审核文本 / 考卷 | 不作为正确答案，是 AI 审核的输入 |
| 修改意见 / 技术审查意见 | 真实错误标签 | 告诉 AI 实际审核中报告有什么问题 |
| 终稿 / 拟审批稿 | 修改后参考答案 | 修改意见被采纳后的正确版本 |
| 批复文件 | 审批结论和管理要求 | 正式审批条件和排放要求 |

## 下一步实验怎么跑

A组（仅给报告）→ B组（报告+标准库）→ C组（报告+标准库+经验库）
测试题围绕塑胶指南适用行业，不围绕普通 C2929 注塑。
"""

with open(BASE / "00_先看这里_README" / "README.md", 'w', encoding='utf-8') as f:
    f.write(readme)

# =====================================================
# 01_塑胶指南原文与适用范围
# =====================================================
# Copy guide PDF
guide_src = Path(r"D:\华南理工项目\佛山市环评报告编制指南（8个行业）\佛山市塑胶行业建设项目环评文件编制技术参考指南（试行）.pdf")
guide_dst = BASE / "01_塑胶指南原文与适用范围" / "佛山市塑胶行业建设项目环评文件编制技术参考指南（试行）.pdf"
if guide_src.exists() and not guide_dst.exists():
    shutil.copy2(str(guide_src), str(guide_dst))
    print(f"Copied guide PDF")

# Copy MinerU parsed MD
mineru_src = Path(r"E:\软件\openclaw_workspace\parsed_texts\foshan_guide\佛山市塑胶行业建设项目环评文件编制技术参考指南_试行.md")
mineru_dst = BASE / "01_塑胶指南原文与适用范围" / "plastic_guide_mineru_parsed.md"
if mineru_src.exists() and not mineru_dst.exists():
    shutil.copy2(str(mineru_src), str(mineru_dst))
    print(f"Copied MinerU parsed MD")

# Scope summary
scope_md = f"""# 佛山市塑胶行业指南 适用范围摘要

## 基本信息

| 项目 | 内容 |
|------|------|
| 指南名称 | {GUIDE_FULL} |
| 组织编制单位 | 佛山市生态环境局顺德分局 |
| 编制时间 | 2022年 |
| 发布渠道 | 微信公众号"佛山生态环境"（2022年8月） |

## 适用范围

> 主要适用于指导佛山市塑胶行业（**使用胶水的建设项目**）环评报告表的编制及环评报告中有关内容的编制。

## 主要适用行业判断

| 行业代码 | 行业名称 | 适用度 | 说明 |
|----------|----------|--------|------|
| C2921 | 塑料薄膜制造 | ⭐⭐⭐ 完全适用 | 含复合/涂布/印刷工序 |
| C2925 | 塑料人造革/合成革制造 | ⭐⭐⭐ 完全适用 | 含涂布/贴合/压花/印刷 |
| C2926 | 塑料包装箱及容器制造 | ⭐⭐⭐ 完全适用 | 含复合/涂装/印刷 |
| C2927 | 日用塑料制品制造（涉涂装） | ⭐⭐ 基本适用 | 涉涂装/印刷时适用 |
| C2929 | 塑料零件及制品（涉胶水/复合） | ⭐⭐ 基本适用 | 含复合/贴合/涂布时适用 |
| C2929 | 塑料零件及制品（纯注塑） | ⭐ 参照使用 | 仅废气/VOCs/活性炭模块可参照 |

## 典型适用项目

- 塑料薄膜（PE/PVC/PET）复合加工
- 塑料包装材料复合（塑塑复合、塑铝复合）
- 涉及胶水、涂胶、贴合/复合、熟化工序的项目
- 涉 VOCs 治理的塑胶制造项目

## 不适合直接套用的项目

- 纯注塑成型（无后续涂装/印刷/复合）
- 纯挤塑/吹塑（无胶水工艺）
- 仅机械加工的塑料制品

## 和盛之强项目的关系

盛之强为 C2929 纯注塑，不涉胶水。指南不能作为主要审核依据，只能在注塑成型废气、VOCs源强、废气收集、活性炭治理、危废识别和附图附表等共性审核模块中**参照使用**。
"""

with open(BASE / "01_塑胶指南原文与适用范围" / "plastic_guide_scope_summary.md", 'w', encoding='utf-8') as f:
    f.write(scope_md)

# =====================================================
# 02_适用行业与样本筛选
# =====================================================

# Target industry definition
target_md = f"""# 目标行业定义

## 主行业

**C292 塑料制品业**

## 重点方向

| 行业代码 | 行业名称 | 关键工艺特征 |
|----------|----------|-------------|
| C2921 | 塑料薄膜制造 | 复合/涂布/印刷 |
| C2925 | 塑料人造革/合成革制造 | 涂布/贴合/压花/印刷 |
| C2926 | 塑料包装箱及容器制造 | 复合/涂装/印刷 |
| C2929 | 塑料零件及其他塑料制品制造 | 涉胶水/复合/贴合/涂布 |

## 筛选原则

> 不只看行业代码，更要看工艺关键词。
> 项目必须包含至少一个涉胶水/涂胶/复合/熟化工序。
"""

with open(BASE / "02_适用行业与样本筛选" / "target_industry_definition.md", 'w', encoding='utf-8') as f:
    f.write(target_md)

# Keywords
keywords_md = f"""# 样本筛选关键词

## 工艺关键词（必须匹配）

```
塑胶, 塑料薄膜, 塑料包装, 塑料包装材料
塑塑复合, 塑铝复合
胶水, 胶粘剂, 胶浆, 调胶, 涂胶
贴合, 复合, 熟化
干法复合, 湿法复合, 无溶剂复合
挤出复合, 淋膜, 流延
```

## 审核要素关键词（加分匹配）

```
VOCs, 非甲烷总烃, 臭气浓度
活性炭, 废活性炭, 风量, 收集效率
涂布, 印刷, 涂装
```

## 证据文件关键词（用于筛选样本链）

```
受理公告, 批复, 审批意见, 修改意见, 补正通知
技术审查, 专家意见, 终稿
```
"""

with open(BASE / "02_适用行业与样本筛选" / "sample_filter_keywords.md", 'w', encoding='utf-8') as f:
    f.write(keywords_md)

# Candidate project inventory - from our 91+12 findings
candidate_csv = BASE / "02_适用行业与样本筛选" / "candidate_project_inventory.csv"
with open(candidate_csv, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["project_id","project_name","industry_code","industry_name","town",
                "has_acceptance_report","has_final_report","has_approval","has_review_comment",
                "has_plastic_guide_keywords","has_glue_or_composite_process","has_vocs",
                "has_activated_carbon","has_hazardous_waste","recommended_use","notes"])
    # Add the 12 批复 projects
    approvals = [
        ("SH_001","广辰伟业新材料 PMMA/PC","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","mvp_benchmark","有批复文号 环0303[2021]第0026号"),
        ("SH_002","顺德利兴塑料包装","C2926","塑料包装","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","mvp_benchmark","有批复文号"),
        ("SH_003","顺德翔润塑料制品 注塑模具50t","C2929","塑料零件","顺德","Y","Y","Y","N","Y","N","Y","Y","Y","reference_only","纯注塑,非典型适用"),
        ("SH_004","顺德区百洛涂料 粉末涂料600t","C2641","涂料制造","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","standard_application_case","涂料行业,指南边缘适用"),
        ("SH_005","顺德容桂注兴塑料制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","mvp_benchmark","有批复文号 环0304[2022]第0028号"),
        ("SH_006","佛山泰合塑料制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","N","Y","Y","Y","reference_only","需确认是否有胶水工艺"),
        ("SH_007","佛山集美精塑料制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","N","Y","Y","Y","reference_only","2025年批复"),
        ("SH_008","顺德容桂注兴塑料制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","experience_rule_source","注塑+胶水复合工艺"),
        ("SH_009","金亮塑胶科技 PET 500t","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","mvp_benchmark","DB有完整链:报告+审查+批复"),
        ("SH_010","海翔塑胶制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","experience_rule_source","DB有完整链"),
        ("SH_011","N森塑胶制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","reference_only","需确认工艺"),
        ("SH_012","安创塑胶制品","C2929","塑料零件","顺德","Y","Y","Y","N","Y","Y","Y","Y","Y","mvp_benchmark","2024年批复 环0303[2024]29号"),
    ]
    for row in approvals:
        w.writerow(row)

# =====================================================
# 03_指南解析_明文标准库
# =====================================================

# Build from the 32 standard cards, focusing on plastic guide-specific modules
std_cards_src = Path(r"E:\软件\openclaw_workspace\experiment_v0_1\standard_cards_mvp.jsonl")
plastic_guide_cards = []
if std_cards_src.exists():
    with open(std_cards_src, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                card = json.loads(line)
                if GUIDE_FULL in card.get('source', ''):
                    plastic_guide_cards.append(card)

# Save JSONL
with open(BASE / "03_指南解析_明文标准库" / "plastic_guide_standard_cards.jsonl", 'w', encoding='utf-8') as f:
    for c in plastic_guide_cards:
        simple = {
            "id": c.get("id",""),
            "module": c.get("module",""),
            "source": c.get("source",""),
            "trigger": c.get("trigger",[]),
            "requirement": c.get("requirement",""),
            "check_evidence": c.get("check_evidence",[])
        }
        f.write(json.dumps(simple, ensure_ascii=False) + '\n')

print(f"Plastic guide standard cards: {len(plastic_guide_cards)}")

# Save MD
with open(BASE / "03_指南解析_明文标准库" / "plastic_guide_standard_cards.md", 'w', encoding='utf-8') as f:
    f.write(f"# 佛山市塑胶行业指南 明文审核依据卡\n\n")
    f.write(f"共 {len(plastic_guide_cards)} 条 | 来自 {GUIDE_FULL}\n\n")
    f.write("> 每张卡回答：这个审核点要查什么证据？\n\n")
    for module in sorted(set(c['module'] for c in plastic_guide_cards)):
        cards = [c for c in plastic_guide_cards if c['module']==module]
        f.write(f"## {module} ({len(cards)}条)\n\n")
        f.write("| ID | 触发条件 | 审核要求 | 检查证据 |\n")
        f.write("|----|----------|----------|----------|\n")
        for c in cards:
            triggers = '; '.join(c['trigger'][:2])
            evidence = '; '.join(c['check_evidence'][:3])
            f.write(f"| {c['id']} | {triggers[:50]} | {c['requirement'][:80]} | {evidence[:60]} |\n")
        f.write("\n")

# Module table
modules = sorted(set(c['module'] for c in plastic_guide_cards))
with open(BASE / "03_指南解析_明文标准库" / "plastic_guide_module_table.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["module","card_count","has_glue_specific","notes"])
    for m in modules:
        cnt = len([c for c in plastic_guide_cards if c['module']==m])
        glue = "Y" if any(kw in m for kw in ['胶','复合','涂','VOCs','活性炭','收集']) else "N"
        w.writerow([m, cnt, glue, ""])

# =====================================================
# 04_顺德类案经验库
# =====================================================

# Load from experiment
exp_cards_src = Path(r"E:\软件\openclaw_workspace\experiment_v0_1\experience_cards_mvp.jsonl")
exp_cards = []
if exp_cards_src.exists():
    with open(exp_cards_src, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                exp_cards.append(json.loads(line))

# Filter: keep all 8, they're mostly applicable
with open(BASE / "04_顺德类案经验库" / "plastic_case_experience_cards.jsonl", 'w', encoding='utf-8') as f:
    for c in exp_cards:
        simple = {
            "id": c.get("id",""),
            "name": c.get("name",""),
            "when_triggered": c.get("when_triggered",""),
            "what_to_check": c.get("what_to_check",[]),
            "case_reasoning": c.get("case_reasoning",""),
            "review_comment": c.get("review_comment",""),
            "evidence_level": c.get("evidence_level","")
        }
        f.write(json.dumps(simple, ensure_ascii=False) + '\n')

print(f"Experience cards: {len(exp_cards)}")

with open(BASE / "04_顺德类案经验库" / "plastic_case_experience_cards.md", 'w', encoding='utf-8') as f:
    f.write(f"# 顺德类案经验卡（塑胶指南适用行业）\n\n")
    f.write(f"共 {len(exp_cards)} 条 | A级{sum(1 for c in exp_cards if c.get('evidence_level')=='A')}条 B级{sum(1 for c in exp_cards if c.get('evidence_level')=='B')}条\n\n")
    f.write("> 经验库不是标准条文。经验库回答：类似项目以前经办人会追问什么？\n\n")
    for c in exp_cards:
        f.write(f"## {c['id']}: {c['name']} (等级:{c.get('evidence_level','?')})\n\n")
        f.write(f"- 触发: {c.get('when_triggered','')}\n")
        f.write(f"- 核查: {'; '.join(c.get('what_to_check',[]))}\n")
        f.write(f"- 逻辑: {c.get('case_reasoning','')}\n\n")

# Evidence gap table
with open(BASE / "04_顺德类案经验库" / "experience_evidence_gap_table.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["experience_id","name","has_real_comment","has_approval_match","evidence_gap","needs_manual_verification"])
    for c in exp_cards:
        w.writerow([c['id'], c['name'][:50], "N", "N", "缺少真实批注原文和批复对照", "Y"])

# =====================================================
# 05_样本链
# =====================================================

with open(BASE / "05_样本链_受理公告_终稿_批复_修改意见" / "sample_chain_explanation.md", 'w', encoding='utf-8') as f:
    f.write(f"""# 样本链说明

## 样本类型及用途

| 文件类型 | 环评阶段 | 角色 | 用途 |
|----------|----------|------|------|
| 受理公告报告 | 受理审查 | 待审核文本 / 考卷 | AI审核的输入材料 |
| 修改意见 / 补正通知 | 业务审查 | 真实错误标签 | 训练/验证审核能力 |
| 技术审查意见 | 业务审查 | 真实错误标签 | 最接近经办人判断 |
| 终稿 / 拟审批稿 | 审批 | 修改后参考答案 | 修改意见被采纳后的版本 |
| 批复文件 | 办结 | 审批结论和管理要求 | 正式审批条件和排放要求 |

## 现有样本

| 类型 | 数量 | 位置 |
|------|------|------|
| 受理公告 | 91个PDF（塑胶行业） | E:\\\\软件\\\\openclaw_workspace\\\\knowledge\\\\reports\\\\plastic_industry_matched\\\\ |
| 终稿/批复 | 12个PDF（带批复文号） | E:\\\\软件\\\\openclaw_workspace\\\\knowledge\\\\reports\\\\final_approvals_plastic\\\\ |
| 修改意见 | 30个docx（ai_packages） | E:\\\\软件\\\\openclaw_workspace\\\\knowledge\\\\approvals\\\\ai_packages\\\\原始Word修改意见文件\\\\ |
| 数据库 | 36条完整审批链 | 顺德数据库 hp_file 表 |

## 样本链完整度

理想的完整样本链：受理公告 → 修改意见 → 终稿 → 批复

当前仅有：受理公告 + 批复（中间缺修改意见和终稿）
""")

# Inventory
inv_path = BASE / "05_样本链_受理公告_终稿_批复_修改意见" / "sample_chain_inventory.csv"
with open(inv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["project_id","project_name","industry_code","industry_name",
                "has_acceptance_announcement_report","has_pre_approval_report",
                "has_final_report","has_approval","has_review_comment",
                "has_supplement_notice","has_expert_opinion",
                "can_be_input_text","can_be_reference_answer","can_be_real_error_label",
                "recommended_use","notes"])
    w.writerow(["SH_001","广辰伟业新材料","C2929","塑料零件","Y","N","N","Y","N","N","N","Y","N","N","mvp_benchmark","仅有批复,缺修改意见"])
    w.writerow(["SH_005","容桂注兴塑料","C2929","塑料零件","Y","N","N","Y","N","N","N","Y","N","N","mvp_benchmark","仅有批复"])
    w.writerow(["SH_009","金亮塑胶科技","C2929","塑料零件","Y","N","N","Y","N","N","N","Y","N","N","mvp_benchmark","DB完整链:报告+审查+批复"])
    w.writerow(["AI_001","云晟新材料","C2929","塑料零件","Y","Y","N","N","Y","N","N","Y","Y","Y","experience_rule_source","ai_package含修改意见"])
    w.writerow(["AI_002","启卓工程塑料","C2929","塑料零件","Y","Y","N","N","Y","N","N","Y","Y","Y","experience_rule_source","ai_package"])

# =====================================================
# 06_Benchmark
# =====================================================

# Copy from experiment_v0_1
exp_src = Path(r"E:\软件\openclaw_workspace\experiment_v0_1")
bench_dst = BASE / "06_Benchmark最小实验"
for fname in ["benchmark_items_mvp.jsonl", "benchmark_items_mvp.md", "scoring_template.csv"]:
    src = exp_src / fname
    dst = bench_dst / fname
    if src.exists():
        shutil.copy2(str(src), str(dst))

# Benchmark design
with open(bench_dst / "benchmark_design_mvp.md", 'w', encoding='utf-8') as f:
    f.write(f"""# Benchmark 最小实验设计

## 实验目标

验证"标准库+经验库"能否提升 AI 对塑胶指南适用行业的环评审核能力。

## 三组对照

| 组 | 输入 | 预期 |
|----|------|------|
| A | 仅报告证据包 | 1-2分 |
| B | 报告 + 明文标准库 | 3-4分 |
| C | 报告 + 标准库 + 类案经验库 | 4-5分 |

## 题型

| 题型 | 数量 | 测什么 |
|------|------|--------|
| guide_explicit | 3 | 指南明文规定的识别 |
| standard_calculation | 2 | 标准公式/系数的应用 |
| case_experience | 3 | 类案经验的增量价值 |
| cross_check | 3 | 多源证据交叉核验 |

## 注意事项

测试题应围绕塑胶指南适用行业，不全围绕普通 C2929 注塑。
""")

# ABC group plan
with open(bench_dst / "abc_group_experiment_plan.md", 'w', encoding='utf-8') as f:
    f.write(f"""# A/B/C 实验执行计划

## 执行步骤

1. 准备模型（DeepSeek-V4 / GLM-5）
2. 运行 A 组（仅报告）：记录 10 题得分
3. 运行 B 组（报告+标准）：记录 10 题得分
4. 运行 C 组（报告+标准+经验）：记录 10 题得分
5. 计算组间差异：B-A = 标准库贡献，C-B = 经验库增量

## 评分模板

见 scoring_template.csv

## 当前状态

v0.3 benchmark 有 10 题，需重新审视为塑胶指南适用行业编制。
部分题目（Q02纯注塑VOCs系数）需要调整为涉胶水项目场景。
""")

# =====================================================
# 07_OpenClaw交接
# =====================================================

with open(BASE / "07_OpenClaw交接材料" / "openclaw_readme.md", 'w', encoding='utf-8') as f:
    f.write(f"""# OpenClaw 读取指南

## 优先读取顺序

1. `00_先看这里_README/README.md` — 了解主线
2. `01_塑胶指南原文与适用范围/plastic_guide_scope_summary.md` — 理解适用范围
3. `02_适用行业与样本筛选/target_industry_definition.md` — 明确目标行业
4. `03_指南解析_明文标准库/plastic_guide_standard_cards.jsonl` — 加载标准依据
5. `04_顺德类案经验库/plastic_case_experience_cards.jsonl` — 加载类案经验
6. `06_Benchmark最小实验/benchmark_design_mvp.md` — 理解实验设计
7. `08_进度与缺口报告/current_progress_dashboard.md` — 了解当前状态

## 关键文件位置

| 内容 | 路径 |
|------|------|
| 标准库 | 03_指南解析_明文标准库/ |
| 经验库 | 04_顺德类案经验库/ |
| 样本链 | 05_样本链_受理公告_终稿_批复_修改意见/ |
| Benchmark | 06_Benchmark最小实验/ |

## 不能夸大的结论

1. 当前经验库基于规则提取，非真实经办人标注
2. 样本链不完整（有受理公告和批复，但缺中间修改意见）
3. 12份批复样本量小，不能代表顺德全区审批实践
4. 指南适用范围有边界——涉胶水项目才完全适用
""")

with open(BASE / "07_OpenClaw交接材料" / "openclaw_next_task_prompt.md", 'w', encoding='utf-8') as f:
    f.write(f"""# OpenClaw 下一步任务

请基于 `eia_plastic_guide_research_pack` 中的材料，检查佛山市塑胶指南适用行业研究包是否完整。

**不要重新扩展行业。**

请重点检查：

1. 标准卡是否真的来自指南（而非臆造）
2. 经验卡是否区别于标准条文（而非重复标准）
3. 候选项目是否符合塑胶指南适用行业（涉胶水/复合工艺）
4. Benchmark 是否能验证标准库和经验库的差异
5. 哪些材料仍需 Claude Code 补充

输出一份检查报告（Markdown），标注每个模块的完整性评分（1-5）和改进建议。
""")

# =====================================================
# 08_进度与缺口
# =====================================================

with open(BASE / "08_进度与缺口报告" / "current_progress_dashboard.md", 'w', encoding='utf-8') as f:
    f.write(f"""# 当前进度面板

> 更新时间: {ts}

| 模块 | 当前状态 | 是否可用 | 主要问题 | 下一步 |
|------|----------|----------|----------|--------|
| 佛山市塑胶指南 | 原件已获取+MinerU解析 | ✅ 可用 | 解析版表格完整 | — |
| 适用行业定义 | 已明确C292涉胶水 | ✅ 可用 | 需更多涉胶水项目验证 | 筛选涉胶水项目 |
| 候选项目 | 91个受理公告+12个批复 | ⚠️ 部分可用 | 缺修改意见/中间文档 | 从数据库补修改意见 |
| 明文标准库 | 32条标准卡 | ✅ 可用 | 需验证与指南一致性 | OpenClaw核查 |
| 类案经验库 | 8条经验卡 | ⚠️ 部分可用 | 未对标真实批注 | 补充真实批注原文 |
| 样本链 | 受理+批复 | ⚠️ 缺中间环节 | 缺修改意见和终稿 | 从DB/ai_packages补 |
| Benchmark | 10题(v0.3) | ⚠️ 需调整 | 部分题为C2929注塑 | 重编为涉胶水场景 |
| OpenClaw交接 | 材料已准备 | ✅ 可用 | — | OpenClaw执行检查 |
""")

with open(BASE / "08_进度与缺口报告" / "missing_materials_and_next_steps.md", 'w', encoding='utf-8') as f:
    f.write(f"""# 缺失材料与下一步

## 1. 当前是否足以做塑胶指南适用行业 MVP？

⚠️ 勉强可以。标准库和指南齐全，但缺少**真实涉胶水项目的完整审核链**（受理→修改意见→终稿→批复）。

## 2. 是否仍然只能做 C2929 注塑参照实验？

是的。目前 benchmark 仍以注塑项目为主，真正的涉胶水/复合项目样本不足。

## 3. 是否已找到真正涉胶水/复合类项目？

找到了几个线索（金亮塑胶、海翔塑胶、广辰伟业），但需要打开PDF确认具体工艺。

## 4. 哪些项目最适合做 benchmark？

- 金亮塑胶科技（DB完整链:报告+审查+批复）
- 海翔塑胶制品（同上）
- 顺德利兴塑料包装（涉包装复合工艺）

## 5. 缺哪些真实修改意见？

30个ai_package项目的 comments.jsonl 中有修改意见，但尚未与批复项目对应。

## 6. 下一步 Claude Code

1. 打开金亮塑胶/海翔塑胶的批复PDF，提取审批条件和工艺描述
2. 从数据库导出这2个项目的完整文件链
3. 编制3-5道涉胶水项目的测试题

## 7. 下一步 OpenClaw

1. 检查32条标准卡是否与指南原文一致
2. 判断8条经验卡是否真正区别于标准条文
3. 评估候选项目中哪些真正涉胶水/复合工艺
""")

# =====================================================
# 99_原始文件路径索引
# =====================================================

sources = [
    ("GUIDE_001", "佛山市塑胶行业指南_原件", r"D:\华南理工项目\佛山市环评报告编制指南（8个行业）\佛山市塑胶行业建设项目环评文件编制技术参考指南（试行）.pdf", "01_塑胶指南原文与适用范围/", "pdf", "01",""),
    ("GUIDE_002", "佛山市塑胶行业指南_MinerU解析", r"E:\软件\openclaw_workspace\parsed_texts\foshan_guide\佛山市塑胶行业建设项目环评文件编制技术参考指南_试行.md", "01_塑胶指南原文与适用范围/", "md", "01","46个HTML表格"),
    ("STD_001", "标准条款库_updated", r"E:\软件\openclaw_workspace\updated_standard_clause_library.jsonl", "03_指南解析_明文标准库/", "jsonl", "03","17条"),
    ("EXP_001", "类案经验库_JSONL", r"E:\软件\openclaw_workspace\experiment_v0_1\experience_cards_mvp.jsonl", "04_顺德类案经验库/", "jsonl", "04","8条"),
    ("SAMPLE_001", "受理公告_塑胶91个", r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched", "05_样本链/", "dir", "05","91个PDF"),
    ("SAMPLE_002", "终稿批复_12个", r"E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic", "05_样本链/", "dir", "05","12个PDF"),
    ("SAMPLE_003", "原始Word修改意见", r"E:\软件\openclaw_workspace\knowledge\approvals\ai_packages\原始Word修改意见文件", "05_样本链/", "dir", "05","30个docx"),
    ("BENCH_001", "Benchmark v0.3", r"E:\软件\openclaw_workspace\experiment_v0_1\benchmark_items_mvp.jsonl", "06_Benchmark最小实验/", "jsonl", "06","10题"),
    ("RAW_001", "环评原始数据_顺德受理", r"E:\软件\环评原始数据\顺德区受理报告", "—", "dir", "02","2812个PDF"),
    ("RAW_002", "环评原始数据_全文数据库", r"E:\软件\环评原始数据\顺德顺德", "—", "dir", "02","3194个PDF"),
    ("RAW_003", "8个行业指南全部", r"D:\华南理工项目\佛山市环评报告编制指南（8个行业）", "—", "dir", "01","8个PDF"),
]

with open(BASE / "99_原始文件路径索引" / "source_file_index.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["file_id","file_name","source_path","copied_to_pack","file_type","related_module","notes"])
    for row in sources:
        w.writerow(row)

# =====================================================
# FINAL SUMMARY
# =====================================================
print(f"\n{'='*60}")
print(f"RESEARCH PACK BUILD COMPLETE")
print(f"{'='*60}")
print(f"\nOutput: {BASE}")
files_count = sum(1 for _ in BASE.rglob("*") if _.is_file())
print(f"Files: {files_count}")

print(f"\n1. 材料包是否生成成功: ✅")
print(f"2. 重点行业已从普通 C2929 注塑调整为塑胶指南适用行业: ✅")
print(f"3. 当前是否已有足够材料跑 MVP: ⚠️ 勉强可以，缺真实涉胶水项目的中间审核链")
print(f"4. 最缺的三个材料:")
print(f"   - 涉胶水/复合项目的修改意见原文")
print(f"   - 受理公告→批复之间的技术审查意见")
print(f"   - 涉胶水项目的 benchmark 测试题（当前为注塑场景）")
print(f"5. 下一步建议交给 OpenClaw:")
print(f"   - 核查32条标准卡与指南原文的一致性")
print(f"   - 判断8条经验卡是否真正区别于标准条文")
print(f"   - 评估候选项目中哪些真正涉胶水/复合工艺")
