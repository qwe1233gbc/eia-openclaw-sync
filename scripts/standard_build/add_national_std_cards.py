import json, os, csv, time

ts = time.strftime('%Y-%m-%d %H:%M:%S')
BASE = r"E:\软件\eia_plastic_guide_research_pack\03_指南解析_明文标准库"

# Load existing 25 cards
existing_path = os.path.join(BASE, "plastic_guide_standard_cards_v0_4_checked.jsonl")
existing = []
with open(existing_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip(): existing.append(json.loads(line))

# New national standard cards - focus on hard limits AI must cite
national_cards = [
    # === DB44/2367-2022 固定污染源VOCs ===
    {"id":"STD_N01","module":"排放标准-VOCs限值","source_type":"standard","source_file":"DB44/2367-2022","source_section":"表3 固定污染源挥发性有机物综合排放标准","source_page_or_table":"表3","trigger":["报告未引用DB44/2367-2022","VOCs排放限值取值错误"],"requirement":"NMHC有组织排放限值: 60mg/m3(表3特别排放限值)。厂区内无组织: 1h平均<=6mg/m3, 任意一次<=20mg/m3。厂界无组织: 4.0mg/m3","check_evidence":["排放标准适用性分析","排气筒监测数据","厂界/厂区监测点位图"]},
    {"id":"STD_N02","module":"排放标准-VOCs物料储存","source_type":"standard","source_file":"GB37822-2019","source_section":"挥发性有机物无组织排放控制标准","source_page_or_table":"全文","trigger":["含VOCs物料敞口存放","胶水桶/溶剂桶未密闭"],"requirement":"含VOCs物料应储存于密闭容器/储罐中;盛装VOCs物料的容器在非取用状态时应加盖/封口/保持密闭","check_evidence":["原料储存现场照片","VOCs物料台账","容器密闭性说明"]},

    # === GB31572-2015 合成树脂 ===
    {"id":"STD_N03","module":"排放标准-合成树脂VOCs","source_type":"standard","source_file":"GB31572-2015","source_section":"表5 合成树脂工业污染物排放标准","source_page_or_table":"表5/表9 2024年修改单","trigger":["报告引用GB31572标准时未采用2024年修改单限值"],"requirement":"合成树脂工业NMHC有组织排放: 60mg/m3(表5特别排放限值)。厂界无组织NMHC: 4.0mg/m3。2024年修改单取消了非甲烷总烃去除效率>=97%的豁免条件","check_evidence":["2024年修改单版本确认","排放限值对应表","排气筒监测数据"]},
    {"id":"STD_N04","module":"排放标准-颗粒物","source_type":"standard","source_file":"DB44/27-2001","source_section":"广东省大气污染物排放限值","source_page_or_table":"表2","trigger":["颗粒物排放限值未引用或错误"],"requirement":"颗粒物有组织排放: 120mg/m3(第二时段二级标准)。厂界无组织颗粒物: 1.0mg/m3","check_evidence":["颗粒物排放核算","排气筒参数","厂界监测数据"]},

    # === DB44/26-2001 水污染物 ===
    {"id":"STD_N05","module":"排放标准-水污染物","source_type":"standard","source_file":"DB44/26-2001","source_section":"广东省水污染物排放限值","source_page_or_table":"表4 第二时段三级标准","trigger":["废水排放标准引用错误","COD/氨氮限值未明确"],"requirement":"生活污水排入城镇污水处理厂执行DB44/26-2001第二时段三级标准: COD<=500mg/L, BOD5<=300mg/L, SS<=400mg/L, 氨氮--","check_evidence":["废水水质检测报告","纳管协议","污水处理厂接纳证明"]},

    # === GB12348-2008 噪声 ===
    {"id":"STD_N06","module":"排放标准-噪声","source_type":"standard","source_file":"GB12348-2008","source_section":"工业企业厂界环境噪声排放标准","source_page_or_table":"表1 3类标准","trigger":["噪声排放标准未明确昼间/夜间限值"],"requirement":"厂界噪声3类标准: 昼间<=65dB(A), 夜间<=55dB(A)。具体分区须依据顺德区声环境功能区划确定","check_evidence":["厂界噪声监测报告","声功能区划文件","厂区平面布置图"]},

    # === GB18597-2023 危废贮存 ===
    {"id":"STD_N07","module":"危废贮存标准","source_type":"standard","source_file":"GB18597-2023","source_section":"危险废物贮存污染控制标准","source_page_or_table":"全文","trigger":["危废暂存间设计不规范","危废分区/标识缺失"],"requirement":"危废贮存设施须防风/防雨/防晒/防渗漏。液态危废贮存区须设围堰或导流沟。不同种类危废分区存放,设置危废识别标志","check_evidence":["危废贮存场所照片","防渗设计说明","危废识别标志照片"]},

    # === HJ1207-2021 自行监测 ===
    {"id":"STD_N08","module":"监测-频次要求","source_type":"standard","source_file":"HJ1207-2021","source_section":"自行监测技术指南-橡胶和塑料制品","source_page_or_table":"表1","trigger":["监测频次不符合HJ1207要求","缺少厂区/厂界监测"],"requirement":"有组织NMHC: 1次/半年; 厂界NMHC+颗粒物+臭气: 1次/年; 厂区内NMHC: 1次/年; 废水间接排放: 1次/半年","check_evidence":["监测计划表","自行监测方案","监测报告"]},
]

# Append
all_cards = existing + national_cards
for i, c in enumerate(all_cards, 1):
    c['id'] = f'STD_{i:02d}'

print(f"Existing: {len(existing)} + National: {len(national_cards)} = {len(all_cards)}")

# Save
with open(existing_path, 'w', encoding='utf-8') as f:
    for c in all_cards:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

# Also save separate national-only file
nat_path = existing_path.replace('.jsonl', '_national_only.jsonl')
with open(nat_path, 'w', encoding='utf-8') as f:
    for c in national_cards:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

# Update MD
md_path = existing_path.replace('.jsonl', '.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# 塑胶指南标准库 v0.4 (含国家标准限值)\n\n")
    f.write(f"共 {len(all_cards)} 条 | 塑胶指南{len(existing)}条 + 国家标准{len(national_cards)}条 | 生成: {ts}\n\n")
    f.write("> 国家标准卡提供硬性限值,塑胶指南卡提供审核流程依据,地方政策标注独立来源\n\n")
    for mod in sorted(set(c['module'] for c in all_cards)):
        cs = [c for c in all_cards if c['module']==mod]
        f.write(f"## {mod} ({len(cs)}条)\n\n")
        f.write("| ID | 来源 | 触发 | 要求 | 证据 |\n|----|------|------|------|------|\n")
        for c in cs:
            src_short = c['source_file'][:25]
            f.write(f"| {c['id']} | {src_short} | {'; '.join(c['trigger'][:1])[:40]} | {c['requirement'][:80]} | {'; '.join(c['check_evidence'][:2])[:50]} |\n")
        f.write("\n")

# Also update the old v0.4 jsonl in sync repo
sync_path = r"E:\软件\eia-openclaw-sync\03_指南解析_明文标准库\plastic_guide_standard_cards_v0_4_checked.jsonl"
import shutil
shutil.copy2(existing_path, sync_path)
shutil.copy2(md_path, sync_path.replace('.jsonl', '.md'))

print(f"Updated sync repo")
print(f"\nNew national cards:")
for c in national_cards:
    print(f"  {c['id']}: {c['module']} ({c['source_file']})")
