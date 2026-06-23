import csv, json
from pathlib import Path

base = Path('04_顺德类案经验库')

active = []
with open(base / 'experience_cards_active_v0_6a.jsonl', encoding='utf-8') as f:
    for l in f:
        if l.strip(): active.append(json.loads(l))

judgments = {
    'EXP_01': ('部分明确', '胶水/涂胶工艺识别',
        '标准库有GB33372限值，经验库提示常见超限且须做低VOCs替代论证（非仅比对限值）',
        '高', '对照实验',
        'source_comment仅有简短引语，需补原始修改意见截图或全文'),
    'EXP_02': ('部分明确', '活性炭参数',
        '标准库有附件四公式，经验库提示实际操作中更换周期常虚高(填6-12月实际仅1-3月)，S取10%是高频错误点',
        '高', '对照实验',
        '来源仅一条简短引语，需补原始修改意见中关于更换周期的完整表述'),
    'EXP_03': ('部分明确', '废气收集效率',
        '标准库有收集效率表(95/80/60%分档)，经验库提示高频错误：半密闭或包围型写成全密闭取95%',
        '高', '对照实验',
        'source_comment有具体引语，来源相对最清晰，可用'),
    'EXP_04': ('部分明确', '复合/熟化工艺识别',
        '提示报告常遗漏复合/涂布工序的VOCs源强识别，标准库不会自动提示工序遗漏',
        '中', '案例展示',
        'source来自body.md工艺描述而非修改意见，属于研究者观察而非审批反馈；evidence_level=B'),
    'EXP_05': ('缺失', '废活性炭识别',
        '提示废活性炭年产生量常漏算，但标准库已含核算公式和危废代码，增量有限',
        '暂不使用', '暂不使用',
        'source_project/source_file/source_comment全部为空，无任何可追溯来源'),
    'EXP_06': ('部分明确', '总量控制',
        '标准库有粤环发[2019]2号总量要求，经验库提示顺德2:1削减替代+替代来源须具体不可写由区统筹',
        '中', '案例展示',
        '顺德区域政策特定性强，通用性有限；source仅三字，需补替代确认文件原文'),
    'EXP_07': ('缺失', '源强核算',
        '主要重复HJ1122标准产污系数(2.70kg/t)，增量作用有限',
        '暂不使用', '暂不使用',
        '来源全部为空；且产污系数已被标准库覆盖，经验库增量不显著'),
    'EXP_08': ('部分明确', '废水排放标准',
        '提示注塑项目冷却水常写不外排但实际有间歇排放，标准库不会提示此隐性排放',
        '中', '辅助提示',
        'evidence_level=C(pending)，source仅一句话，需确认为正式修改意见'),
}

# CSV
csv_path = base / 'experience_test_value_simple_v0_7.csv'
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['经验编号','经验名称','来源状态','对应审核点',
        '相对标准库的增量作用','测试价值等级','建议用途','人工复核备注'])
    for card in active:
        eid = card['id']
        j = judgments.get(eid, ('','','','','','','',''))
        writer.writerow([eid, card.get('name',''), j[0], j[1], j[2], j[3], j[4], j[5]])

print(f"CSV: {csv_path}")

# Field dictionary
dict_path = base / 'experience_test_value_field_dictionary_v0_7.md'
dict_path.write_text("""# 经验库测试价值判断 字段字典 v0.7

## 1. 经验编号
唯一标识每条类案经验，沿用原经验库编号（EXP_01~EXP_08）。

## 2. 经验名称
一句话概括该经验关注的问题，取自原经验库的 name 字段。

## 3. 来源状态
- **明确**: 能对应具体修改意见、报告批注或技术审查意见原始材料
- **部分明确**: 能找到相关项目或描述，但缺少完整原文或批注位置
- **缺失**: 目前找不到可靠来源，仅模型归纳或人工推测

## 4. 对应审核点
该经验主要对应的审核模块，每条仅填1-2个核心点。

## 5. 相对标准库的增量作用
一句话说明该经验相对于标准依据库多提供了什么。

## 6. 测试价值等级
- **高**: 适合进入对照实验，能体现经验库相对于标准库的增量
- **中**: 适合案例展示或辅助提示，暂不作为主要实验依据
- **低**: 内容较泛或与标准库重复
- **暂不使用**: 来源缺失、证据不足、范围不匹配

## 7. 建议用途
- **对照实验**: 可作为A/B/C知识条件对照中的经验库输入
- **案例展示**: 适合论文或汇报中解释经验库构建逻辑
- **辅助提示**: 可用于提示审核关注点，不能作为判断依据
- **暂不使用**: 暂时不进入当前研究使用范围

## 8. 人工复核备注
一句话说明为什么这样判断，或还需补充什么材料。
""", encoding='utf-8')
print(f"Dict: {dict_path}")

# Summary
high = [(c, judgments[c['id']]) for c in active if judgments.get(c['id'],('','','','','','','',''))[3]=='高']
mid  = [(c, judgments[c['id']]) for c in active if judgments.get(c['id'],('','','','','','','',''))[3]=='中']
low  = [(c, judgments[c['id']]) for c in active if judgments.get(c['id'],('','','','','','','',''))[3]=='低']
unused = [(c, judgments[c['id']]) for c in active if judgments.get(c['id'],('','','','','','','',''))[3]=='暂不使用']

summary_path = base / 'experience_test_value_summary_v0_7.md'
lines = [
    "# 类案经验库测试价值简要判断 v0.7\n",
    "## 1. 总体判断\n",
    "当前经验库（8条active）**尚不适合直接进入知识条件对照实验**。",
    "主要原因是8条中仅3条达到高测试价值等级，且所有经验的来源均为部分明确（无一达到明确），",
    "source_comment字段仅有2-5字简短引语，缺少完整原始修改意见文本。",
    "建议先补全来源证据链后，以3条高价值经验为核心开展小规模预实验。\n",
    f"## 2. 可进入对照实验的经验（高: {len(high)}条）\n",
]
for c, j in high:
    lines.append(f"- **{c['id']} {c['name']}**: {j[2][:100]}")
    lines.append(f"  审核点: {j[1]} | 来源: {c.get('source_project','')} {c.get('source_file','')}\n")

lines.append(f"## 3. 适合案例展示的经验（中: {len(mid)}条）\n")
for c, j in mid:
    lines.append(f"- **{c['id']} {c['name']}**: {j[5][:100]}\n")

lines.append(f"## 4. 暂不使用的经验（暂不使用: {len(unused)}条, 低: {len(low)}条）\n")
for c, j in unused:
    lines.append(f"- **{c['id']} {c['name']}**: {j[5][:100]}\n")

lines.extend([
    "## 5. 最需要补充的材料\n",
    "1. 康明新材料厂完整修改意见原文: 当前8条中7条来自该项目，source_comment仅2-5字",
    "2. 第二条独立来源项目: 所有经验均来自同一项目，缺乏跨项目验证",
    "3. EXP_05/07的来源材料: 这两条source字段全部为空",
    "4. 审批意见原文: approval_match全部为none",
    "5. 终稿修改响应: 需形成完整的问题-退改-响应闭环\n",
    "## 6. 最终结论\n",
    "当前类案经验库无法直接支撑完整对照实验。",
    "3条(EXP_01/02/03)达到高测试价值，可进入预实验；",
    "3条(EXP_04/06/08)仅适合案例展示或辅助提示；",
    "2条(EXP_05/07)因来源缺失应暂不使用。",
    "适合小规模预实验的模块: 胶水VOCs含量、活性炭更换周期、废气收集效率。",
    "经验库核心短板不是数量(8条够了)，而是溯源链不完整: 所有经验仅来自一个项目，",
    "source_comment过于简短，缺少跨项目验证。",
])

summary_path.write_text('\n'.join(lines), encoding='utf-8')
print(f"Summary: {summary_path}")

print(f"\n高:{len(high)} 中:{len(mid)} 低:{len(low)} 暂不使用:{len(unused)}")
