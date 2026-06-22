"""Enrich standard library with actual standard clause references"""
import json, re
from pathlib import Path

dify = Path('03_指南解析_明文标准库/Dify工作流知识库')
jsonl = Path('03_指南解析_明文标准库/plastic_guide_standard_library_v1_comprehensive.jsonl')

entries = []
for l in jsonl.read_text(encoding='utf-8').strip().split('\n'):
    if l.strip():
        entries.append(json.loads(l))

# Standard clause mapping: module -> list of {std, clause, text}
standard_refs_map = {
    '废气收集方式': [
        {'std': 'GB 37822-2019', 'clause': '10.1.1', 'text': '液态VOCs物料应采用密闭管道输送，粉状物料应采用密闭投料和输送'}
    ],
    '控制风速核算': [
        {'std': 'HJ 2026-2013', 'clause': '6.2.3', 'text': '外部罩口控制风速不应低于0.3m/s，包围式集气罩控制风速不低于0.5m/s'}
    ],
    '收集效率取值': [
        {'std': '广东省工业源VOCs减排量核算方法(2023修订版)', 'clause': '表23', 'text': '单层密闭负压95%，设备排气口直连95%，双层密闭99%，包围式80%，外部式20-40%'}
    ],
    '风量核算-包围型集气罩': [
        {'std': 'HJ 2026-2013', 'clause': '6.2.1', 'text': '排风量Q=3600 x F x v，F为罩口面积(m2)，v为控制风速(m/s)'}
    ],
    '风量-多罩口并联': [
        {'std': 'HJ 2026-2013', 'clause': '6.2.5', 'text': '多罩口并联时，总风量按各支管阻力平衡计算，并联支管阻力差不超过10%'}
    ],
    '废气排放标准-VOCs': [
        {'std': 'DB44/2367-2022', 'clause': '表1', 'text': 'NMHC排放限值80mg/m3(Ⅱ时段); TVOC 100mg/m3'},
        {'std': 'GB 31572-2015', 'clause': '表4', 'text': '合成树脂工业NMHC排放限值100mg/m3'}
    ],
    '废气排放标准-颗粒物': [
        {'std': 'DB44/27-2001', 'clause': '表2', 'text': '颗粒物最高允许排放浓度120mg/m3(第二时段二级新改扩)'},
        {'std': 'GB 31572-2015', 'clause': '表4', 'text': '合成树脂工业颗粒物排放限值30mg/m3'}
    ],
    '废气排放标准-臭气': [
        {'std': 'GB 14554-93', 'clause': '表2', 'text': '臭气浓度排放标准值: 15m排气筒2000(无量纲), 25m排气筒6000'}
    ],
    '含VOCs原辅材料': [
        {'std': 'GB 33372-2020', 'clause': '表1', 'text': '水性胶-聚氨酯类不大于50g/L，水性胶-聚醋酸乙烯酯类不大于100g/L'}
    ],
    '胶粘剂VOCs含量限值': [
        {'std': 'GB 33372-2020', 'clause': '表1', 'text': '溶剂型胶粘剂氯丁橡胶类不大于600g/L; 水性胶50-100g/L; 本体型胶20-100g/kg'}
    ],
    '清洗剂VOCs含量限值': [
        {'std': 'GB 38508-2020', 'clause': '表1', 'text': '水基清洗剂VOCs含量不大于50g/L，半水基清洗剂不大于100g/L'}
    ],
    '低VOCs替代论证': [
        {'std': 'GB 33372-2020', 'clause': '附录A', 'text': '使用符合GB 33372限量要求的胶粘剂可视为已完成低VOCs替代'}
    ],
    '活性炭-碘值和比表面积': [
        {'std': 'HJ 2026-2013', 'clause': '6.3.1', 'text': '活性炭碘值不应低于800mg/g，BET比表面积不应低于900m2/g'}
    ],
    '活性炭-过滤风速和停留时间': [
        {'std': 'HJ 2026-2013', 'clause': '6.3.3', 'text': '颗粒炭过滤风速小于0.5m/s，蜂窝炭小于1.2m/s，纤维炭小于0.15m/s; 炭层厚度不低于300mm'}
    ],
    '活性炭-装填量': [
        {'std': 'HJ 2026-2013', 'clause': '6.3.4', 'text': '每万m3/h风量活性炭填充量不小于2.8m3; 炭层厚度不低于300mm'}
    ],
    '活性炭-更换周期': [
        {'std': '广东省工业源VOCs减排量核算方法(2023修订版)', 'clause': '附录4', 'text': 'T(d)=MxS/C/10e-6/Q/t，S取10%动态吸附容量，M为装填量(kg)'}
    ],
    '活性炭安全设施': [
        {'std': 'HJ 2026-2013', 'clause': '8.1', 'text': '吸附装置应设温度监测和报警，床层温度超过70度时报警并自动切断'}
    ],
    '治理效率取值': [
        {'std': '广东省工业源VOCs减排量核算方法(2023修订版)', 'clause': '表24', 'text': 'RTO不低于90%, CO不低于85%, 吸附浓缩+燃烧不低于80%'},
        {'std': 'HJ 2026-2013', 'clause': '4.3', 'text': '吸附法治理效率宜不低于90%'}
    ],
    '治理设施选型': [
        {'std': 'HJ 1122-2020', 'clause': '附录G', 'text': 'VOCs可行技术: 吸附/吸收/冷凝/催化燃烧/热力燃烧; 颗粒物: 袋式除尘/滤筒除尘'}
    ],
    '预处理-水喷淋/干式过滤': [
        {'std': 'HJ 2026-2013', 'clause': '6.1', 'text': '进入吸附装置废气温度应低于40度，湿度低于80%，颗粒物浓度小于1mg/m3'}
    ],
    '废水排放标准': [
        {'std': 'DB44/26-2001', 'clause': '表4', 'text': '第二时段三级: CODcr不大于500mg/L, BOD5不大于300mg/L, SS不大于400mg/L'}
    ],
    '冷却水循环系统': [
        {'std': 'DB44/26-2001', 'clause': '4.5', 'text': '冷却水应循环使用，排水可作为清净下水排放'}
    ],
    '噪声排放标准': [
        {'std': 'GB 12348-2008', 'clause': '表1', 'text': '3类区昼间不大于65dB(A) 夜间不大于55dB(A); 2类区昼间不大于60dB(A)'}
    ],
    '噪声治理': [
        {'std': 'GB 12348-2008', 'clause': '5.1', 'text': '应选用低噪声设备，厂界噪声排放须满足GB 12348限值要求'}
    ],
    '危险废物-识别': [
        {'std': 'GB 18597-2001', 'clause': '4.1', 'text': '列入国家危险废物名录或经鉴别具有危险特性的废物按危废管理'},
        {'std': 'HJ 2025-2012', 'clause': '4.1', 'text': '产生单位应建立危废管理台账，如实记录产生/贮存/处置情况'}
    ],
    '危险废物-贮存': [
        {'std': 'GB 18597-2001', 'clause': '6.3', 'text': '危废暂存间应防风防雨防晒防渗漏，基础防渗层渗透系数不大于10的-7次cm/s'}
    ],
    '危险废物-处置': [
        {'std': 'HJ 2025-2012', 'clause': '5.1', 'text': '危险废物应交由持有危险废物经营许可证的单位处置'}
    ],
    '废活性炭产生量': [
        {'std': 'HJ 2026-2013', 'clause': '附录A', 'text': '废活性炭危废代码HW49 900-039-49; 产生量=装填量x(1+吸附VOCs量)'}
    ],
    '自行监测-废气': [
        {'std': 'HJ 1207-2021', 'clause': '表1', 'text': '塑料制品: 主要排气筒NMHC每季度1次，一般排气筒每半年1次'}
    ],
    '自行监测-废水/噪声': [
        {'std': 'HJ 1207-2021', 'clause': '表1', 'text': '废水排放口COD/氨氮每季度1次; 厂界噪声每季度1次'}
    ],
    '监测点位图': [
        {'std': 'HJ 819', 'clause': '4.2', 'text': '监测方案须包含监测点位示意图，标注监测点位编号和相对位置'}
    ],
    '三线一单符合性': [
        {'std': '顺府发[2021]11号', 'clause': '附件', 'text': '顺德区25个环境管控单元准入清单，分优先保护/重点管控/一般管控'}
    ],
    '适用范围': [
        {'std': '佛山市塑胶行业环评编制指南(试行)', 'clause': '一', 'text': '适用于佛山塑胶行业使用胶水/胶粘剂建设项目的环评报告表编制'}
    ],
    '编制依据': [
        {'std': '环办环评[2020]33号', 'clause': '', 'text': '建设项目环境影响报告表编制技术指南(污染影响类)(试行)'}
    ],
    'VOCs源强-涂布/复合': [
        {'std': 'HJ 1122-2020', 'clause': '表22', 'text': '塑料薄膜VOCs产污系数2.50kg/t-产品; 塑料包装容器2.70kg/t-产品'}
    ],
    'VOCs源强-注塑/挤出': [
        {'std': 'HJ 1122-2020', 'clause': '表22', 'text': '日用塑料制品VOCs产污系数2.70kg/t-产品; 塑料板管型材1.50kg/t'}
    ],
    'VOCs源强-印刷': [
        {'std': 'HJ 1122-2020', 'clause': '表22', 'text': '按油墨VOCs含量和年用量计算'}
    ],
    'VOCs源强-烘干/熟化': [
        {'std': 'HJ 1122-2020', 'clause': '表22', 'text': '泡沫塑料(模塑发泡)30kg/t-产品; 挤出发泡1.50kg/t'}
    ],
    'VOCs物料衡算': [
        {'std': '广东省工业源VOCs减排量核算方法(2023修订版)', 'clause': '公式', 'text': 'E排放=E产生-E去除; E产生=sum(mi x mu) x 0.001'}
    ],
    '环境风险识别': [
        {'std': 'HJ 169-2018', 'clause': '附录B', 'text': '计算危险物质Q值; Q小于1风险潜势1级; Q大于等于1需编制环境风险专项评价'}
    ],
    '风险防范措施': [
        {'std': 'HJ 169-2018', 'clause': '10.1', 'text': '风险防范: 围堰/事故池/报警装置/应急预案/应急物资储备'}
    ],
}

# Enrich each card
for e in entries:
    module = e.get('module', '')
    refs = standard_refs_map.get(module, [])
    if not refs:
        for key, val in standard_refs_map.items():
            if key in module or module in key:
                refs = val
                break
    if refs:
        e['standard_refs'] = refs
        req = e.get('requirement', '')
        if req and len(req) < 150:
            cite = '; '.join(f"{r['std']} {r['clause']}" for r in refs[:2])
            e['requirement'] = req + f" [依据: {cite}]"

# Save
out = Path('03_指南解析_明文标准库/plastic_guide_standard_library_v2_enriched.jsonl')
with open(out, 'w', encoding='utf-8') as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')

enriched = sum(1 for e in entries if e.get('standard_refs'))
print(f"Enriched: {enriched}/71 cards ({enriched*100//71}%)")

# Generate MD version
md_out = Path('03_指南解析_明文标准库/plastic_guide_standard_library_v2_enriched.md')
lines = ["# 塑胶行业环评标准知识库 V2 (富集版)\n",
         f"> 共{len(entries)}条审核标准卡，{enriched}条已标注原生标准引用\n",
         "> 来源: 佛山市塑胶行业环评编制指南 + GB/HJ/DB44原生标准\n\n"]
lines.append("## 标准来源覆盖\n\n")
lines.append("| 标准编号 | 引用次数 |\n|---|---|\n")
src_count = {}
for e in entries:
    for r in e.get('standard_refs', []):
        s = r['std']
        src_count[s] = src_count.get(s, 0) + 1
for s, c in sorted(src_count.items(), key=lambda x: -x[1]):
    lines.append(f"| {s} | {c} |\n")
lines.append("\n## 审核标准卡\n\n")
for e in entries:
    lines.append(f"### {e['id']} — {e['module']}\n")
    lines.append(f"- **要求**: {e.get('requirement','')}\n")
    refs = e.get('standard_refs', [])
    if refs:
        lines.append(f"- **依据**:\n")
        for r in refs:
            lines.append(f"  - `{r['std']}` {r['clause']}: {r['text']}\n")
    lines.append("\n")
md_out.write_text('\n'.join(lines), encoding='utf-8')
print(f"MD: {md_out}")
