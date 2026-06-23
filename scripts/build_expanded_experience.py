"""Build expanded experience library from 649+ QAs, strict QAs, and classified experience."""
import json
from pathlib import Path
from collections import defaultdict

# Sources
qa_base = []
with open('E:/eia-llm-judge-framework/data/historical_db/qa_experience_base.jsonl', encoding='utf-8') as f:
    for l in f:
        if l.strip(): qa_base.append(json.loads(l))
qa_tech = []
with open('E:/eia-llm-judge-framework/data/historical_db/qa_tech_review.jsonl', encoding='utf-8') as f:
    for l in f:
        if l.strip(): qa_tech.append(json.loads(l))
qa_strict = []
with open('E:/eia-llm-judge-framework/data/qa_strict/qa_strict_all.jsonl', encoding='utf-8') as f:
    for l in f:
        if l.strip(): qa_strict.append(json.loads(l))

all_sources = qa_base + qa_tech + qa_strict
print(f"Total source QAs: {len(all_sources)}")

# Define new experience cards extracted from real QAs
new_cards = [
    # === 废气收集效率 ===
    {
        "id": "EXP_09", "name": "半密闭车间收集效率虚高至95%",
        "applicable_scope": "使用局部集气罩(非全密闭)的塑胶项目",
        "when_triggered": "收集效率取95%但实际为包围型或外部集气罩",
        "what_to_check": ["核实车间/设备是否真正全密闭负压", "若为包围型集气罩，控制风速是否>=0.5m/s（否则降至60%）", "多个产生源是否分别核算收集效率而非统一取最大值"],
        "case_reasoning": "顺德多个塑胶项目将半密闭车间或包围型集气罩取95%收集效率，退改后按实际收集方式调整。源自审批经验库中'收集效率取值依据不足'类问题的反复出现。",
        "review_comment": "收集效率95%仅适用于全密闭负压空间。当前为包围型集气罩，应按实际控制风速取值：>=0.5m/s取80%，0.3-0.5m/s取60%。",
        "evidence_level": "A",
        "source_project": "顺德审批数据库(多条)",
        "source_file": "qa_experience_base.jsonl + qa_strict_all.jsonl",
        "source_comment": "649条QA中收集效率相关审核点为高频触发点；来源于顺德历年审批意见汇总",
        "approval_match": "pending",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "core",
    },
    {
        "id": "EXP_10", "name": "生产工位与收集设施不匹配",
        "applicable_scope": "大型容器(如100L桶)操作的塑胶项目",
        "when_triggered": "报告称在通风橱内操作但设备尺寸明显超出通风橱容量",
        "what_to_check": ["现场核实生产工位位置和配套收集设施", "100L以上容器操作是否可能完全在通风橱内完成", "若工位相距较远，集中收集管道阻力是否导致效率下降"],
        "case_reasoning": "技术审查发现某项目使用100L桶称在通风橱内操作但实际不可能，退改后补充现场核实和收集方案调整。",
        "review_comment": "须现场核实生产工位与收集设施匹配性。大型容器(>50L)操作不应简单描述为通风橱内进行。",
        "evidence_level": "B",
        "source_project": "顺德技术审查案例",
        "source_file": "qa_tech_review.jsonl",
        "source_comment": "技术审查意见: 100L桶不可能在通风橱内进行",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    # === 活性炭参数 ===
    {
        "id": "EXP_11", "name": "活性炭碘值不满足800mg/g最低要求",
        "applicable_scope": "使用活性炭治理VOCs的塑胶项目",
        "when_triggered": "报告仅写'设置活性炭吸附装置'但未提供碘值、比表面积等关键参数",
        "what_to_check": ["活性炭碘值是否>=800mg/g", "BET比表面积是否>=900m2/g", "是否提供活性炭质量检验报告", "是否明确活性炭类型(颗粒/蜂窝/纤维)及对应设计参数"],
        "case_reasoning": "多个顺德塑胶项目不提供活性炭具体参数，审批要求补充碘值和比表面积证明，部分项目使用的活性炭碘值实测仅400-600mg/g。",
        "review_comment": "须提供活性炭碘值(>=800mg/g)和比表面积(>=900m2/g)的检验报告，并明确活性炭类型和设计参数符合HJ 2026-2013要求。",
        "evidence_level": "A",
        "source_project": "顺德审批数据库(多条)",
        "source_file": "qa_experience_base.jsonl",
        "source_comment": "审批中反复追问活性炭参数，649条QA中活性炭相关为高频审核点",
        "approval_match": "pending",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "core",
    },
    # === 危废识别 ===
    {
        "id": "EXP_12", "name": "擦拭胶粘剂废抹布遗漏于危废清单",
        "applicable_scope": "使用胶粘剂/油墨/清洗剂的塑胶项目",
        "when_triggered": "危废清单仅列废活性炭、废包装桶但遗漏擦拭废抹布",
        "what_to_check": ["是否识别擦拭胶粘剂/油墨的废抹布为危废(HW49 900-041-49)", "废抹布产生量是否按使用量和更换频次估算", "是否纳入危废台账和处置合同"],
        "case_reasoning": "技术审查发现多个项目遗漏擦拭废抹布为危废，退改后补充危废代码(HW49)和完善处置方案。",
        "review_comment": "补充擦拭胶粘剂废抹布为危险废物(HW49 900-041-49)，明确产生量、收集方式和处置去向。",
        "evidence_level": "B",
        "source_project": "顺德技术审查案例",
        "source_file": "qa_tech_review.jsonl",
        "source_comment": "技术审查意见: 危险废物遗漏擦拭胶粘剂废抹布",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    # === VOCs物料识别 ===
    {
        "id": "EXP_13", "name": "油性油墨/稀释剂以效果为由规避低VOCs替代",
        "applicable_scope": "使用油性油墨/稀释剂/溶剂型胶粘剂的塑胶项目",
        "when_triggered": "报告以'印刷效果好'/'黏结强度高'为由拒绝低VOCs替代但缺少技术经济论证",
        "what_to_check": ["是否进行低VOCs替代技术经济论证(非仅效果描述)", "是否列出至少2种低VOCs替代方案及不可行原因", "是否符合佛山市三线一单中'严格限制溶剂型原辅材料'要求"],
        "case_reasoning": "技术审查发现某项目使用油性油墨仅以'印刷效果好'作为不可替代理由，退改要求提供完整的技术经济论证或更换水性油墨。",
        "review_comment": "油性油墨的'效果好'不能作为不可替代论证。须提供至少2种低VOCs替代方案的对比分析或证明技术不可行，否则应更换为水性油墨。",
        "evidence_level": "B",
        "source_project": "顺德技术审查案例",
        "source_file": "qa_tech_review.jsonl",
        "source_comment": "技术审查: 油性油墨印刷效果好不可作为不可替代说明",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    {
        "id": "EXP_14", "name": "稀释剂/清洗剂未按VOCs物料识别",
        "applicable_scope": "使用稀释剂/清洗剂/溶剂的塑胶项目",
        "when_triggered": "原辅材料表列稀释剂但未说明其VOCs含量和是否属于有机溶剂清洗剂",
        "what_to_check": ["稀释剂VOCs含量是否超过GB38508限值(水基<=50g/L,半水基<=100g/L)", "是否根据MSDS判断稀释剂属于有机溶剂清洗剂", "稀释剂年用量和VOCs产生量是否纳入源强核算"],
        "case_reasoning": "多个顺德项目用稀释剂但未纳入VOCs物料核算，退改后补充MSDS和VOCs含量分析。",
        "review_comment": "稀释剂须按GB38508判断是否属于有机溶剂清洗剂，提供MSDS和VOCs含量数据，纳入废气源强核算。",
        "evidence_level": "B",
        "source_project": "顺德审批数据库",
        "source_file": "qa_experience_base.jsonl",
        "source_comment": "审批追问: 核实稀释剂是否属于有机溶剂清洗剂",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    # === 源强核算 ===
    {
        "id": "EXP_15", "name": "产污系数选用不当导致VOCs源强偏低",
        "applicable_scope": "涉注塑/挤出/涂布工序的塑胶项目",
        "when_triggered": "VOCs产生量明显偏低(如注塑<2.0 kg/t-产品)且未说明系数来源",
        "what_to_check": ["产污系数是否来自HJ1122-2020表22或广东省核算方法", "产品类型与系数是否匹配(注塑2.70,薄膜2.50,泡沫30kg/t)", "是否遗漏脱模剂/润滑剂/清洗剂等辅助物料的VOCs贡献"],
        "case_reasoning": "顺德多个注塑企业VOCs量估算偏低30-50%，退改后调整系数并补充遗漏的辅助物料VOCs。",
        "review_comment": "注塑工序VOCs产污系数应取HJ1122-2020表22中2.70kg/t-产品。须核实产品类型与系数匹配性，并补充脱模剂等辅助物料的VOCs贡献。",
        "evidence_level": "B",
        "source_project": "顺德审批数据库(多条)",
        "source_file": "qa_experience_base.jsonl",
        "source_comment": "审批中反复要求核实VOCs产生量，注塑系数的选用为高频问题",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "core",
    },
    # === 废气收集方式 ===
    {
        "id": "EXP_16", "name": "收集点位布置不合理导致风量虚算",
        "applicable_scope": "多工位集中收集的塑胶项目",
        "when_triggered": "多个相距较远工位采用同一套收集系统但未分析管道阻力平衡",
        "what_to_check": ["平面布置图是否标注各工位收集点位", "相距较远工位集中收集是否分析管道阻力平衡", "风量核算是否考虑支管阻力差(不超过10%)", "收集效率取值是否因管道过长而降效"],
        "case_reasoning": "技术审查发现项目开料和打磨工位相距较远但统一收集，未分析可行性和风量平衡，退改后分设系统。",
        "review_comment": "相距较远工位集中收集时须分析管道阻力平衡和总风量，若支管阻力差>10%应分设收集系统或加大风机选型。",
        "evidence_level": "B",
        "source_project": "顺德技术审查案例",
        "source_file": "qa_tech_review.jsonl",
        "source_comment": "技术审查: 结合平面布置图明确收集点位，分析集中收集可行性",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    # === 废水 ===
    {
        "id": "EXP_17", "name": "冷却水'不外排'声明与实际情况矛盾",
        "applicable_scope": "涉冷却循环水的注塑/挤出项目",
        "when_triggered": "报告写冷却水'循环使用不外排'但实际运营中有间歇排放",
        "what_to_check": ["冷却塔排污水/定期更换水是否有排放", "若排放，去向是否为雨水管网(需确认为清净下水)", "是否有雨污分流条件", "是否取得污水处理厂接纳同意"],
        "case_reasoning": "顺德多个注塑项目冷却水实际有间歇排放但报告写'不外排'，退改后补充排放去向论证和雨污分流确认。",
        "review_comment": "须明确冷却水实际是否排放。若有排放须说明去向：排入雨水管网须论证为清净下水并确认雨污分流；排入污水管网须取得污水处理厂同意。",
        "evidence_level": "B",
        "source_project": "顺德审批数据库(多条)",
        "source_file": "qa_experience_base.jsonl",
        "source_comment": "审批意见: 是否单纯冷却水; 冷却水排放路径核实",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
    # === 总量控制 ===
    {
        "id": "EXP_18", "name": "VOCs总量替代方案缺少确认文件",
        "applicable_scope": "顺德区VOCs排放>300kg/年的塑胶项目",
        "when_triggered": "总量替代方案仅写'由区统筹'无具体来源",
        "what_to_check": ["替代来源是否已由生态环境分局确认(书面文件)", "替代比例是否满足顺德2:1削减要求", "替代来源是否与项目同区域"],
        "case_reasoning": "顺德多个项目VOCs替代方案模糊，仅写'由区统筹分配'无正式确认文件，退改后补充替代来源确认函。",
        "review_comment": "VOCs总量>300kg/年须提供顺德区2:1替代的具体来源确认文件(分局盖章)，不得仅写'由区统筹'。",
        "evidence_level": "B",
        "source_project": "顺德审批数据库",
        "source_file": "qa_experience_base.jsonl",
        "source_comment": "审批追问: 替代来源是否已确认(非仅承诺)",
        "approval_match": "none",
        "evidence_status": "partially_supported",
        "manual_check_needed": True,
        "classification": "reference",
    },
]

print(f"New cards: {len(new_cards)}")

# Load existing active cards
existing = []
active_path = Path('04_顺德类案经验库/experience_cards_active_v0_6a.jsonl')
for l in active_path.read_text(encoding='utf-8').strip().split('\n'):
    if l.strip(): existing.append(json.loads(l))

# Merge: keep existing + add new
all_cards = existing + new_cards
print(f"Total cards: {len(all_cards)} (existing: {len(existing)}, new: {len(new_cards)})")

# Write expanded library
out_path = Path('04_顺德类案经验库/experience_cards_active_v0_7_expanded.jsonl')
with open(out_path, 'w', encoding='utf-8') as f:
    for card in all_cards:
        f.write(json.dumps(card, ensure_ascii=False) + '\n')

print(f"Saved: {out_path}")

# Summary
modules = defaultdict(int)
for c in all_cards:
    mod = c.get('name','')[:20]
    src = 'new' if c['id'] in [nc['id'] for nc in new_cards] else 'existing'
    modules[f"{src}/{c.get('classification','?')}"] += 1
print(f"\nBy source/class: {dict(modules)}")
print(f"Evidence level: A={sum(1 for c in all_cards if c.get('evidence_level')=='A')}, B={sum(1 for c in all_cards if c.get('evidence_level')=='B')}, C={sum(1 for c in all_cards if c.get('evidence_level')=='C')}")
print(f"Source types: {len(set(c.get('source_project','') for c in all_cards))} unique source projects")
