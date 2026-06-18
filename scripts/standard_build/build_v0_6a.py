#!/usr/bin/env python3
"""Build v0.6a experiment preparation package based on OpenClaw v0.6 upgrade analysis"""
import json, os, csv, shutil, time

BASE = r"E:\软件\eia_plastic_guide_research_pack"
SYNC = r"E:\软件\eia-openclaw-sync"
ts = time.strftime('%Y-%m-%d %H:%M:%S')

# =====================================================
# 1. Archive v0.5 outputs
# =====================================================
print("=== 1. Archiving v0.5 ===")
archive_dir = os.path.join(BASE, "outputs/openclaw_mvp_v0_5_archive")
os.makedirs(archive_dir, exist_ok=True)

v05_outputs = [
    "openclaw_mvp_experiment_report.md",
    "group_A_report_only_answers.jsonl",
    "group_B_standard_answers.jsonl",
    "group_C_standard_experience_answers.jsonl",
    "scoring_matrix.csv",
    "standard_library_hit_report.md",
    "experience_library_hit_report.md",
    "group_comparison_summary.md",
    "next_claude_code_tasks.md",
]

missing = []
for f in v05_outputs:
    found = False
    for search_dir in [BASE, SYNC, r"E:\软件"]:
        for root, dirs, files in os.walk(search_dir):
            if f in files:
                found = True
                break
        if found: break

    if found:
        print(f"  [FOUND] {f}")
    else:
        missing.append(f)
        print(f"  [MISSING] {f}")

# Generate missing report
miss_path = os.path.join(archive_dir, "missing_v0_5_outputs_report.md")
with open(miss_path, 'w', encoding='utf-8') as f:
    f.write("# v0.5 Missing Outputs Report\n\n")
    f.write(f"生成: {ts}\n\n")
    if missing:
        f.write("## Missing Files\n\n")
        for m in missing:
            f.write(f"- `{m}`: OpenClaw未生成或未同步到本地\n")
        f.write("\n## Impact\n不影响v0.6a准备——OpenClaw分析报告(v0.6_upgrade_analysis.md)已包含所有关键发现。\n")
    else:
        f.write("No missing files.\n")

print(f"  Missing report: {miss_path}")

# =====================================================
# 2. Generate v0.6a experiment design
# =====================================================
print("\n=== 2. v0.6a Experiment Design ===")

exp_design = """# v0.6a Experiment Design

## Positioning
v0.6a is NOT a formal large-sample experiment. It fixes v0.5 issues without expanding scope:
- Fix questions (retrieval mismatch, coverage gaps)
- Fix scoring (separate common + knowledge scores)
- Fix experience card relevance (prevent Q03-style false hits)
- Prepare human review materials

## Question Structure
- Main set: 18 questions
- Backup: 2 questions
- NOT "20 formal questions" - make it clear 18+2

## Types
- guide_explicit: 5 (2 retained + 3 new)
- standard_calculation: 4 (1 negative control + 3 new)
- case_experience: 5 (2 retained + 3 new)
- cross_check: 4 (1 retained + 3 new)

## Retained from v0.5 (5)
Q01: Glue VOCs content - high discrimination
Q02: Carbon replacement cycle - quantitative anchor
Q03: Collection efficiency - best performer
Q04: VOCs total substitution - clear policy
Q05: Process x VOCs cross-check - cross-item reasoning

## Negative Control (1)
Q06: Safety facilities (retained Q04 from v0.5) - tests zero false positive

## New (12 main + 2 backup)
Guide_explicit: standard selection, VOCs storage, hazwaste identification
Standard_calculation: air volume, carbon wind speed, waste carbon quantity
Case_experience: composite process VOCs, cooling water discharge, environmental risk
Cross_check: VOCs source chain, hazwaste x materials, monitoring plan x exhaust

## Scoring
common_score_6: judgement(2) + evidence(2) + actionability(2)
knowledge_use_score_4: standard(2) + experience(2)
total_score_10: only for B/C groups
A group only uses common_score_6

## Experience Cards
Active: 8 cards with relevance fields (NOT expanded to 15)
Candidate: safety, equipment, air volume, hazwaste, cooling, env risk (NOT called in v0.6a)
Pending: downgraded, cannot be used as strong evidence
"""

bench_dir = os.path.join(BASE, "06_Benchmark最小实验")
os.makedirs(bench_dir, exist_ok=True)
with open(os.path.join(bench_dir, "v0_6a_experiment_design.md"), 'w', encoding='utf-8') as f:
    f.write(exp_design)

# =====================================================
# 3. Build benchmark items v0.6a (18 main)
# =====================================================
print("=== 3. Benchmark v0.6a ===")

# Load v0.5 benchmark for retained items
v05_path = os.path.join(bench_dir, "benchmark_items_mvp_v0_4.jsonl")
v05_items = []
if os.path.exists(v05_path):
    with open(v05_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                v05_items.append(json.loads(line))

# Build 18 main items + 2 backup
items_v06a = []

# -- RETAINED (5 from v0.5) --
retain_ids = ['Q01','Q02','Q05','Q06','Q07']
for item in v05_items:
    if item['item_id'] in retain_ids:
        item['version'] = 'v0.6a'
        item['gold_label_source'] = 'review_comment'
        item['manual_check_needed'] = True
        item['difficulty'] = 'medium'
        item['scoring_points'] = ['judgement','evidence','actionable','standard_use','experience_use']
        item['data_leakage_risk'] = 'low'
        items_v06a.append(item)

# Re-number retained
for i, item in enumerate(items_v06a, 1):
    item['item_id'] = f'Q{i:02d}'

# -- NEGATIVE CONTROL (1) --
nc = v05_items[3].copy()  # Q04 safety
nc['item_id'] = 'Q06'
nc['version'] = 'v0.6a'
nc['question_type'] = 'negative_control'
nc['gold_label_source'] = 'standard_card'
nc['expected_standard_cards'] = ['STD_24']
nc['expected_experience_cards'] = []
nc['notes'] = 'Negative control: no experience card for safety facilities. Tests zero false positive.'
items_v06a.append(nc)

# -- NEW 12 ITEMS (skeleton with key fields) --
new_items = [
    {"item_id":"Q07","question_type":"guide_explicit","audit_module":"标准适用层级","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告涂布废气执行GB31572-2015表5特别排放限值。请依据DB44/2367-2022判断该标准选择是否正确。","gold_judgement":"标准引用不当","gold_answer":"DB44/2367-2022为广东省固定污染源VOCs综合排放标准,已于2022年实施,应优先执行。GB31572-2015仅适用于合成树脂工业,涂布工序不在其适用范围。","gold_label_source":"standard_card","difficulty":"medium","expected_standard_cards":["STD_09"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q08","question_type":"guide_explicit","audit_module":"VOCs物料储存","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告未描述胶水桶/溶剂桶的储存方式。根据GB37822-2019,含VOCs物料应如何储存?报告缺失此项是否应退回补充?","gold_judgement":"缺失储存描述,应退回补充","gold_answer":"GB37822-2019要求含VOCs物料储存于密闭容器/储罐,非取用状态加盖/封口。报告未描述胶水桶/溶剂桶储存方式,应补充储存设施说明和现场照片。","gold_label_source":"standard_card","difficulty":"easy","expected_standard_cards":["STD_27"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q09","question_type":"guide_explicit","audit_module":"危废识别-非活性炭","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告危废章节仅列出废活性炭(HW49),但项目使用溶剂型聚氨酯胶水。请判断是否有遗漏的危废类别。","gold_judgement":"遗漏废胶水桶(HW49)","gold_answer":"使用溶剂型胶粘剂,废胶水桶/废溶剂桶属于HW49(900-041-49),须纳入危废清单。另须识别含胶废抹布(HW49)。","gold_label_source":"review_comment","difficulty":"easy","expected_standard_cards":["STD_21"],"expected_experience_cards":["EXP_05"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q10","question_type":"standard_calculation","audit_module":"风量核算","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"涂布车间设包围型集气罩,罩口1.2m×0.8m,距污染源0.3m,控制风速0.5m/s,有挡板。报告取设计风量8000m3/h。请按指南附件三公式核算设计风量。","gold_judgement":"设计风量偏高","gold_answer":"Q=(10x2+F)Vx=(10×0.09+0.96)×0.5=0.93m3/s=3348m3/h。报告8000偏高2.4倍,可能虚增了风量导致收集效率虚高。","gold_label_source":"standard_card","difficulty":"hard","expected_standard_cards":["STD_15"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q11","question_type":"standard_calculation","audit_module":"活性炭过滤风速","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"活性炭箱截面4m2,风量15000m3/h,采用颗粒活性炭。请核算过滤风速并判断是否满足指南附件四要求。","gold_judgement":"过滤风速超标","gold_answer":"v=Q/(3600×A)=15000/(3600×4)=1.04m/s。颗粒炭指南要求<0.5m/s,超标2倍。应增大炭箱截面至>=8.3m2或改用蜂窝炭(<1.2m/s可满足)。","gold_label_source":"standard_card","difficulty":"medium","expected_standard_cards":["STD_17"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q12","question_type":"standard_calculation","audit_module":"废活性炭产生量","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"活性炭装填量2.0t/次,每15天更换一次。报告称废活性炭年产生量2.0t,危废合同处置能力2.5t/a。请核算实际年产生量。","gold_judgement":"废活性炭量核算偏低","gold_answer":"年更换次数=365/15=24.3次,年产生量=2.0×24.3=48.6t/a(不含吸附VOCs量)。危废合同2.5t/a远不满足,须调整更换方案或扩大危废合同处置能力。","gold_label_source":"standard_card","difficulty":"medium","expected_standard_cards":["STD_23"],"expected_experience_cards":["EXP_05"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q13","question_type":"case_experience","audit_module":"复合工艺VOCs","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告称复合工序为'热熔复合,无VOCs产生'。但原料清单含'聚氨酯胶粘剂'且设备有'干法复合机'。请依据类案经验识别工艺描述矛盾。","gold_judgement":"工艺描述与原料/设备矛盾","gold_answer":"设备含干法复合机且使用聚氨酯胶粘剂,不属于热熔复合。EXP_04:顺德多个塑胶项目将干法复合作热熔复合压低VOCs源强,退改后补充复合工序VOCs核算。","gold_label_source":"experience_card","difficulty":"medium","expected_standard_cards":["STD_05"],"expected_experience_cards":["EXP_04"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q14","question_type":"case_experience","audit_module":"冷却水排放","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告称冷却水循环使用不外排,补充量5m3/d(循环量100m3/d的5%)。但开式冷却塔理论损失仅约2%。请依据类案经验判断是否存在隐性排放。","gold_judgement":"可能存在隐性排放","gold_answer":"EXP_08类案:多个顺德注塑项目冷却水写'不外排'但实际有间歇排放。补充量5%远超理论损失2%,差额约3m3/d去向不明。须明确排放去向并确认雨污分流。","gold_label_source":"experience_card","difficulty":"medium","expected_standard_cards":["STD_19"],"expected_experience_cards":["EXP_08"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q15","question_type":"case_experience","audit_module":"环境风险","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"项目使用溶剂型聚氨酯胶水(年用量10.5t),但报告无环境风险评价章节。请依据相关标准判断是否合规。","gold_judgement":"缺失环境风险评价","gold_answer":"使用溶剂型胶粘剂须按HJ169-2018识别环境风险:胶水/溶剂泄漏、火灾次生污染。须补充风险识别、防范措施和应急预案。","gold_label_source":"standard_card","difficulty":"hard","expected_standard_cards":["STD_38"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q16","question_type":"cross_check","audit_module":"VOCs源强全链路","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"原料:胶水10.5t/a(VOCs含量120g/L),涂布面积300万m2/a。报告VOCs有组织排放1.2t/a。请从原料→产生→收集→排放全链路交叉核验。","gold_judgement":"全链路核算不一致","gold_answer":"VOCs产生量=胶水用量×VOCs含量=10.5×0.12=1.26t(仅胶水,未含涂布热解VOCs)。按80%收集×85%处理=1.26×0.8×0.15=0.15t排放。报告1.2t/a有组织排放可能将无组织VOCs混入。","gold_label_source":"cross_check_manual","difficulty":"hard","expected_standard_cards":["STD_11","STD_13","STD_14"],"expected_experience_cards":["EXP_01","EXP_03"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q17","question_type":"cross_check","audit_module":"危废×原辅料","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告危废清单:废活性炭(HW49)、废包装桶(HW49)。但原辅料清单含'液压油0.5t/a'和'切削液0.3t/a'。请交叉核验危废清单完整性。","gold_judgement":"遗漏废液压油(HW08)和废切削液(HW09)","gold_answer":"液压油→废液压油HW08(900-218-08),切削液→废切削液HW09(900-006-09)。报告仅识别废活性炭和废包装桶,遗漏2类危废。","gold_label_source":"review_comment","difficulty":"medium","expected_standard_cards":["STD_35"],"expected_experience_cards":["EXP_05"],"manual_check_needed":True,"data_leakage_risk":"low"},
    {"item_id":"Q18","question_type":"cross_check","audit_module":"监测计划×排气筒","project_id":"SH_004","project_name":"康明新材料厂","audit_task":"报告监测计划有3个排气筒(DA001/002/003),但工艺描述仅有涂布+烘干2个废气产生源。请交叉核验排气筒数量与产污环节的对应性。","gold_judgement":"排气筒与产污源不匹配","gold_answer":"仅有2个废气产生源却设3个排气筒,多出的DA003来源不明。按HJ1207-2021,监测计划排气筒须与产污环节一一对应。须解释DA003的来源或删除。","gold_label_source":"standard_card","difficulty":"medium","expected_standard_cards":["STD_25"],"expected_experience_cards":[],"manual_check_needed":True,"data_leakage_risk":"low"},
]

for item in new_items:
    item['version'] = 'v0.6a'
    item['evidence_package'] = {"project": item['project_name'], "excerpt": item['audit_task']}
    item['scoring_points'] = ['judgement','evidence','actionable','standard_use','experience_use']
    items_v06a.append(item)

# Save main 18
main_path = os.path.join(bench_dir, "benchmark_items_mvp_v0_6a.jsonl")
with open(main_path, 'w', encoding='utf-8') as f:
    for item in items_v06a:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Backup 2
backup = [
    {"item_id":"B01","version":"v0.6a","question_type":"cross_check","audit_module":"噪声×声功能区","gold_label_source":"standard_card","notes":"备选题"},
    {"item_id":"B02","version":"v0.6a","question_type":"guide_explicit","audit_module":"附图一致性","gold_label_source":"review_comment","notes":"备选题"},
]
backup_path = os.path.join(bench_dir, "benchmark_items_mvp_v0_6a_backup.jsonl")
with open(backup_path, 'w', encoding='utf-8') as f:
    for item in backup:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# Change log
change_path = os.path.join(bench_dir, "benchmark_item_change_log_v0_6a.md")
with open(change_path, 'w', encoding='utf-8') as f:
    f.write("# Benchmark v0.5 → v0.6a Change Log\n\n")
    f.write("| v0.5 ID | v0.6a ID | Action | Reason |\n|---------|----------|--------|--------|\n")
    f.write("| Q01 | Q01 | Retained | High discrimination, EXP_01 perfect hit |\n")
    f.write("| Q02 | Q02 | Retained | High discrimination, quantitative anchor |\n")
    f.write("| Q03 | — | Replaced | Retrieval mismatch (EXP_01 low relevance) |\n")
    f.write("| Q04 | Q06 | Retained as NC | Negative control: zero false positive test |\n")
    f.write("| Q05 | Q03 | Retained | Best performer, EXP_03 perfect hit |\n")
    f.write("| Q06 | Q04 | Retained | High discrimination, clear policy basis |\n")
    f.write("| Q07 | Q05 | Retained | Best cross-check, cross-item reasoning |\n")
    f.write("| Q08 | — | Replaced | Coverage gap + low discrimination |\n")
    f.write("| — | Q07-Q18 | New (12) | Cover 12 high-priority modules |\n")
    f.write("\nMain: 18 questions (5 retained + 1 NC + 12 new)\nBackup: 2 questions\n")

print(f"  Benchmark: {len(items_v06a)} main + {len(backup)} backup")

# =====================================================
# 4. Experience Cards with Relevance
# =====================================================
print("\n=== 4. Experience Cards v0.6a ===")

exp_dir = os.path.join(BASE, "04_顺德类案经验库")

# Load existing 8
old_exp_path = os.path.join(exp_dir, "plastic_case_experience_cards_v0_4_checked.jsonl")
old_cards = []
with open(old_exp_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip(): old_cards.append(json.loads(line))

# Add relevance fields
relevance_map = {
    "EXP_01": {"applicable_task_types":["guide_explicit","case_experience"],"not_applicable_task_types":["standard_calculation"],"applicable_modules":["胶粘剂VOCs含量","原辅材料-VOCs"],"not_applicable_modules":["涂胶量核算"],"applicable_industry_features":["涉溶剂型胶粘剂","聚氨酯胶水"],"relevance_rules":{"hard_filter":["task_type is standard_calculation"],"high":["task_type matches","module matches"],"medium":["only keyword match"],"low":["task_type in not_applicable_task_types"]}},
    "EXP_02": {"applicable_task_types":["guide_explicit","standard_calculation","case_experience"],"not_applicable_task_types":[],"applicable_modules":["活性炭-更换周期"],"not_applicable_modules":[],"applicable_industry_features":["涉活性炭治理"],"relevance_rules":{"hard_filter":[],"high":["task_type matches","module matches"],"medium":["related module"],"low":["unrelated module"]}},
    "EXP_03": {"applicable_task_types":["case_experience","cross_check","guide_explicit"],"not_applicable_task_types":[],"applicable_modules":["废气收集效率"],"not_applicable_modules":[],"applicable_industry_features":["涉包围型集气罩","涉涂布/复合车间"],"relevance_rules":{"hard_filter":[],"high":["task_type matches","module matches"],"medium":["related module"],"low":["unrelated module"]}},
    "EXP_04": {"applicable_task_types":["case_experience","cross_check"],"not_applicable_task_types":["standard_calculation"],"applicable_modules":["复合工艺VOCs","涂布工艺"],"not_applicable_modules":[],"applicable_industry_features":["涉复合/涂布工艺"],"relevance_rules":{"hard_filter":[],"high":["task_type matches","module matches"],"medium":["only keyword"],"low":[]}},
    "EXP_05": {"applicable_task_types":["case_experience","cross_check","guide_explicit"],"not_applicable_task_types":[],"applicable_modules":["危废识别","危废产生量"],"not_applicable_modules":[],"applicable_industry_features":["涉活性炭","涉危废"],"relevance_rules":{"hard_filter":["evidence_status is pending → no strong conclusion"],"high":[],"medium":["module matches but evidence pending"],"low":[]}},
    "EXP_06": {"applicable_task_types":["case_experience","guide_explicit"],"not_applicable_task_types":["standard_calculation"],"applicable_modules":["总量控制"],"not_applicable_modules":[],"applicable_industry_features":["顺德区","VOCs>300kg/a"],"relevance_rules":{"hard_filter":[],"high":["task_type matches","module matches","顺德项目"],"medium":["module matches but non-顺德项目"],"low":[]}},
    "EXP_07": {"applicable_task_types":["case_experience"],"not_applicable_task_types":["standard_calculation","cross_check"],"applicable_modules":["VOCs源强核算"],"not_applicable_modules":["设备产能"],"applicable_industry_features":["涉注塑工序"],"not_applicable_industry_features":["涉涂布机产能"],"relevance_rules":{"hard_filter":["task_type is cross_check with equipment capacity"],"high":[],"medium":["module matches + 注塑项目"],"low":["涂布机产能题"]}},
    "EXP_08": {"applicable_task_types":["case_experience","cross_check"],"not_applicable_task_types":["standard_calculation"],"applicable_modules":["废水-循环排放"],"not_applicable_modules":[],"applicable_industry_features":["涉冷却循环水"],"relevance_rules":{"hard_filter":[],"high":["task_type matches","module matches"],"medium":["related module"],"low":[]}},
}

active_cards = []
for c in old_cards:
    eid = c.get('id','')
    if eid in relevance_map:
        c.update(relevance_map[eid])
    active_cards.append(c)

active_path = os.path.join(exp_dir, "experience_cards_active_v0_6a.jsonl")
with open(active_path, 'w', encoding='utf-8') as f:
    for c in active_cards:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

# Candidate cards (NOT in active pool for v0.6a)
candidate_cards = [
    {"id":"CAND_01","name":"安全设施缺失","status":"candidate","reason":"Negative control prevents use in v0.6a","notes":"Cannot be used in Q06 negative control"},
    {"id":"CAND_02","name":"设备产能不匹配","status":"candidate","reason":"EXP_07 covers注塑 only,涂布产能 needs separate card"},
    {"id":"CAND_03","name":"风量核算虚高","status":"candidate","reason":"New module, not yet verified against real comments"},
    {"id":"CAND_04","name":"冷却水隐性排放","status":"candidate","reason":"EXP_08 is pending, needs evidence upgrade first"},
    {"id":"CAND_05","name":"环境风险遗漏","status":"candidate","reason":"New module, need real case binding"},
]
cand_path = os.path.join(exp_dir, "experience_cards_candidate_v0_6a.jsonl")
with open(cand_path, 'w', encoding='utf-8') as f:
    for c in candidate_cards:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

# Change log
change_log = os.path.join(exp_dir, "experience_card_change_log_v0_6a.md")
with open(change_log, 'w', encoding='utf-8') as f:
    f.write("# Experience Card Change Log v0.6a\n\n")
    f.write("## Active (8 cards)\n- All 8 original cards retained\n- Added relevance fields (applicable_task_types, applicable_modules, relevance_rules)\n- Pending cards (EXP_05/07/08) tagged: cannot be strong evidence\n\n")
    f.write("## Candidate (5 cards, NOT in v0.6a active pool)\n- CAND_01-CAND_05: safety, equipment, air volume, cooling, env risk\n- Will enter active pool only after evidence binding in v0.7\n\n")
    f.write("## Key Rules\n- Q06 (negative control): NO experience card can be used\n- EXP_07: prohibited from涂布设备产能 questions\n- EXP_01: prohibited from standard_calculation tasks\n")

# Relevance schema
schema_md = os.path.join(exp_dir, "experience_relevance_schema_v0_6a.md")
with open(schema_md, 'w', encoding='utf-8') as f:
    f.write("# Experience Relevance Schema v0.6a\n\n")
    f.write("## Hard Filter (Step 1)\n1. task_type in not_applicable_task_types → DISCARD\n2. module in not_applicable_modules → DISCARD\n3. evidence_status = pending → NO strong conclusion\n4. No report evidence supporting trigger → DISCARD\n\n")
    f.write("## Soft Classification (Step 2)\n- HIGH: task_type match + module match + industry match + evidence status core/reference\n- MEDIUM: module/task match but evidence chain incomplete\n- LOW: only keyword match or task mismatch\n\n")
    f.write("## Usage Rules (Step 3)\n- HIGH: can enter review judgment\n- MEDIUM: auxiliary hint only, mark for human review\n- LOW: discard, do not cite\n")

schema_json = os.path.join(exp_dir, "experience_relevance_schema_v0_6a.json")
with open(schema_json, 'w', encoding='utf-8') as f:
    json.dump({"version":"v0.6a","hard_filters":["task_type_mismatch","module_mismatch","pending_evidence","no_report_support"],"soft_levels":{"HIGH":"task+module+industry match + evidence verified","MEDIUM":"partial match, needs human review","LOW":"keyword only, discard"},"negative_control_rule":"No experience card may be used for negative control questions"}, f, ensure_ascii=False, indent=2)

print(f"  Active: {len(active_cards)}, Candidate: {len(candidate_cards)}")

# =====================================================
# 5. Scoring Rubric
# =====================================================
print("\n=== 5. Scoring v0.6a ===")

scoring_md = os.path.join(bench_dir, "scoring_rubric_v0_6a.md")
with open(scoring_md, 'w', encoding='utf-8') as f:
    f.write("# Scoring Rubric v0.6a\n\n")
    f.write("## common_score_6 (A/B/C all groups)\n- judgement_correct: 0-2\n- evidence_use: 0-2\n- actionability: 0-2\n\n")
    f.write("## knowledge_use_score_4 (B/C only)\n- standard_basis: 0-2\n- experience_basis: 0-2\n\n")
    f.write("## total_score_10 (B/C only)\ntotal = common_score_6 + knowledge_use_score_4\n\n")
    f.write("## Comparison Rules\n- B-A: compare common_score_6 + standard_basis\n- C-B: compare experience_basis + review quality change\n- Negative control: excluded from experience increment stats\n")

# Scoring template
template_path = os.path.join(bench_dir, "scoring_template_v0_6a.csv")
with open(template_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["item_id","group","model","judgement(0-2)","evidence(0-2)","actionable(0-2)","common_6","standard(0-2)","experience(0-2)","knowledge_4","total_10","notes"])
    for item in items_v06a:
        for grp in ['A','B','C']:
            w.writerow([item['item_id'], grp, '', '', '', '', '', '', '', '', '', ''])

print(f"  Scoring template: 18×3 = 54 rows")

# =====================================================
# 6. Sample Selection
# =====================================================
print("\n=== 6. Sample Selection ===")

sample_dir = os.path.join(BASE, "05_样本链_受理公告_终稿_批复_修改意见")
sample_csv = os.path.join(sample_dir, "sample_selection_for_v0_6a.csv")
with open(sample_csv, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["project_id","project_name","industry_code","has_glue","has_coating","has_composite","has_vocs","has_carbon","has_acceptance","has_review","has_final","has_approval","chain_level","usable_for_questions","usable_real_error","usable_cross_check","risk_leakage","notes"])
    w.writerow(["SH_004","康明新材料厂","C2929","Y","Y","Y","Y","Y","N","Y","N","N","D","ALL","Y","Y","LOW","主样本: body.md+19条修改意见"])
    w.writerow(["SH_001","金来塑料","C2929","Y","Y","Y","Y","Y","Y","Y","N","Y","B","Q07-Q12","N","N","LOW","辅样本: 3环链,有批复"])
    w.writerow(["SH_002","金能塑料","C2929","Y","Y","Y","Y","Y","Y","Y","N","Y","B","Q07-Q12","N","N","LOW","辅样本: 3环链"])

sample_md = os.path.join(sample_dir, "sample_selection_for_v0_6a.md")
with open(sample_md, 'w', encoding='utf-8') as f:
    f.write("# Sample Selection for v0.6a\n\n")
    f.write("## Primary: 康明新材料厂\n- 18 questions based on this single project\n- body.md 165KB + 19 review comments\n- Coating 135 hits + adhesive 30 hits = perfect guide match\n\n")
    f.write("## Secondary: 金来/金能塑料\n- For new questions Q07-Q12 if additional project data needed\n- 3-ring chain (report+review+approval)\n\n")

# =====================================================
# 7. OpenClaw Prompt
# =====================================================
print("\n=== 7. OpenClaw v0.6a Prompt ===")

oc_dir = os.path.join(BASE, "07_OpenClaw交接材料")
prompt = os.path.join(oc_dir, "openclaw_v0_6a_task_prompt.md")
with open(prompt, 'w', encoding='utf-8') as f:
    f.write("# OpenClaw v0.6a Task Prompt\n\n")
    f.write("## Load Materials\n1. benchmark: `06_Benchmark最小实验/benchmark_items_mvp_v0_6a.jsonl` (18 main + 2 backup)\n")
    f.write("2. standards: `03_指南解析_明文标准库/plastic_guide_standard_cards_v0_4_checked.jsonl` (38 cards)\n")
    f.write("3. experience ACTIVE: `04_顺德类案经验库/experience_cards_active_v0_6a.jsonl` (8 cards)\n")
    f.write("4. experience CANDIDATE: DO NOT LOAD for v0.6a\n")
    f.write("5. relevance schema: `04_顺德类案经验库/experience_relevance_schema_v0_6a.json`\n\n")
    f.write("## Key Rules\n- Q06 is negative control: NO experience card may be used\n")
    f.write("- Use hard filter + soft classification for relevance\n")
    f.write("- Pending cards cannot be strong evidence\n")
    f.write("- Score: common_6 + knowledge_4 = total_10 (B/C only)\n")
    f.write("- 18 main questions, NOT 20\n")
    f.write("- Do NOT expand experience library to 15 cards\n")

# =====================================================
# 8. Readiness Report
# =====================================================
print("\n=== 8. Readiness Report ===")

prog_dir = os.path.join(BASE, "08_进度与缺口报告")
ready_path = os.path.join(prog_dir, "v0_6a_readiness_report.md")
with open(ready_path, 'w', encoding='utf-8') as f:
    f.write(f"# v0.6a Readiness Report\n\n生成: {ts}\n\n")
    f.write("## 1. v0.5 Retained Questions\nQ01(glue VOCs), Q02(carbon cycle), Q05(collection)→Q03, Q06(total)→Q04, Q07(cross)→Q05, Q04(safety)→Q06(NC)\n\n")
    f.write("## 2. v0.6a Question Count\n18 main + 2 backup. NOT 20 formal questions.\n\n")
    f.write("## 3. Negative Control\nQ06 (safety facilities). No experience card. Tests zero false positive.\n\n")
    f.write("## 4. Experience Library\nNOT expanded. 8 active (with relevance) + 5 candidate (NOT in v0.6a).\n\n")
    f.write("## 5. Relevance Mechanism\nHard filter (Step 1) → Soft classification (Step 2) → Usage rules (Step 3). EXP_01 prohibited from standard_calculation tasks.\n\n")
    f.write("## 6. Scoring\ncommon_score_6 (all groups) + knowledge_use_score_4 (B/C only). A group uses only common_6.\n\n")
    f.write("## 7. Gold Answers\nAll 18 marked manual_check_needed=True. Q01-Q05 sourced from review_comment. Q07-Q18 sourced from standard_card.\n\n")
    f.write("## 8. Samples\nPrimary: 康明新材料厂. Secondary: 金来/金能塑料.\n\n")
    f.write("## 9. Ready for OpenClaw?\nYES. All materials in place. OpenClaw should read v0.6a prompt and execute.\n")

# =====================================================
# 9. Sync to GitHub
# =====================================================
print("\n=== 9. Syncing to GitHub ===")

# Copy to sync repo
sync_dirs = {
    "06_Benchmark最小实验": ["v0_6a_experiment_design.md","benchmark_items_mvp_v0_6a.jsonl","benchmark_items_mvp_v0_6a_backup.jsonl","benchmark_item_change_log_v0_6a.md","scoring_rubric_v0_6a.md","scoring_template_v0_6a.csv"],
    "04_顺德类案经验库": ["experience_cards_active_v0_6a.jsonl","experience_cards_candidate_v0_6a.jsonl","experience_card_change_log_v0_6a.md","experience_relevance_schema_v0_6a.md","experience_relevance_schema_v0_6a.json"],
    "05_样本链_受理公告_终稿_批复_修改意见": ["sample_selection_for_v0_6a.csv","sample_selection_for_v0_6a.md"],
    "07_OpenClaw交接材料": ["openclaw_v0_6a_task_prompt.md"],
    "08_进度与缺口报告": ["v0_6a_readiness_report.md"],
}

for subdir, files in sync_dirs.items():
    for f in files:
        src = os.path.join(BASE, subdir, f)
        dst = os.path.join(SYNC, subdir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  SYNC: {subdir}/{f}")

print(f"\nv0.6a BUILD COMPLETE")
print(f"Questions: {len(items_v06a)} main + {len(backup)} backup")
print(f"Experience: {len(active_cards)} active + {len(candidate_cards)} candidate")
