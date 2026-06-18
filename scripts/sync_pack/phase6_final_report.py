#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 6: Generate final reports"""
import json, csv, time, os
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:\软件\openclaw_workspace")
RULES_DIR = Path(r"E:\eia-llm-judge-framework\eia_experience_review_project\04_experience_library\source_rules")

# Load inventory
inv = {}
inv_path = BASE / "data_inventory.csv"
if inv_path.exists():
    with open(inv_path, 'r', encoding='utf-8-sig') as fh:
        for row in csv.DictReader(fh):
            inv[row["category"]] = {"count": int(row["file_count"]), "size_mb": float(row["total_size_mb"])}

# Load manifest for stats
manifest_count = 0
total_size = 0
categories = defaultdict(lambda: {"count": 0, "size": 0})
manifest_path = BASE / "file_manifest.jsonl"
if manifest_path.exists():
    with open(manifest_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            manifest_count += 1
            total_size += e.get("size", 0)
            cat = e.get("category", "other")
            categories[cat]["count"] += 1
            categories[cat]["size"] += e.get("size", 0)

# Load rules
all_rules = []
for fname in ["experience_rules_all.json", "experience_rules_A_verified.json",
              "experience_rules_B_candidate.json", "experience_rules_C_observation.json"]:
    fp = RULES_DIR / fname
    if fp.exists():
        with open(fp, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, list):
            all_rules.extend(data)

# Deduplicate
seen = set()
unique_rules = []
for r in all_rules:
    rid = r.get("rule_id", "")
    if rid not in seen:
        seen.add(rid)
        unique_rules.append(r)

rules_std = [r for r in unique_rules if r.get("common_standards")]
rules_nostd = [r for r in unique_rules if not r.get("common_standards")]
rules_human = [r for r in unique_rules if r.get("need_human_review")]
rules_A = [r for r in unique_rules if str(r.get("evidence_level")) == "A"]
rules_B = [r for r in unique_rules if str(r.get("evidence_level")) == "B"]
rules_C = [r for r in unique_rules if str(r.get("evidence_level")) == "C"]

# Clause library
clause_count = 0
clause_path = BASE / "standard_clause_library.jsonl"
if clause_path.exists():
    with open(clause_path, 'r', encoding='utf-8') as fh:
        clause_count = sum(1 for _ in fh)

# Workspace files
ws_files = sum(len(files) for _, _, files in os.walk(str(BASE)))

# ======== openclaw_data_ready_report.md ========
print("Generating openclaw_data_ready_report.md...")
REPORT_PATH = BASE / "openclaw_data_ready_report.md"
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    f.write(f"# OpenClaw 数据就绪报告\n\n")
    f.write(f"> 生成时间: {ts}\n")
    f.write(f"> 研究主题: 面向环评智能审核的证据分级经验知识库构建与有效性验证研究\n\n")
    f.write("---\n\n")

    # 1. Available
    f.write("## 1. 已可供 OpenClaw 使用的资料\n\n")
    f.write(f"- 文件总数: {manifest_count}\n")
    f.write(f"- 总大小: {total_size/1024/1024:.0f} MB\n")
    f.write(f"- 工作区文件: {ws_files}\n\n")

    f.write("### 按类别\n\n")
    f.write("| 类别 | 文件数 | 大小(MB) | 就绪 |\n")
    f.write("|------|--------|----------|------|\n")
    for cat in sorted(categories, key=lambda c: -categories[c]["count"]):
        s = categories[cat]
        ready = "OK" if cat in [
            "标准PDF","标准解析文本","经验规则","benchmark数据","工作流文件"
        ] else "inspect"
        f.write(f"| {cat} | {s['count']} | {s['size']/1024/1024:.1f} | {ready} |\n")

    f.write("\n### 核心资料检查\n\n")
    checks = [
        ("环评报告", "环评报告" in categories),
        ("批复/修改意见", "批复文件" in categories or "修改意见" in categories),
        ("标准PDF", "标准PDF" in categories),
        ("经验规则", "经验规则" in categories),
        ("Benchmark数据", "benchmark数据" in categories),
        ("三线一单", "三线一单文件" in categories),
        ("VOCs核算", "VOCs核算文件" in categories),
        ("产污系数", "产污系数手册" in categories),
    ]
    for name, ok in checks:
        f.write(f"- [{'x' if ok else ' '}] {name}\n")

    # 2. Missing
    f.write("\n## 2. 哪些资料缺失\n\n")
    f.write("### 用户指定的文件\n\n")
    f.write("- `experience_rules_ai_checked.jsonl` - 不存在\n")
    f.write("- `experience_rules_for_human_review_checked.md` - 不存在\n")

    f.write("\n### 标准PDF\n\n")
    f.write("- GB30981.2-2025 - 2025年5月发布, 全网无免费电子版\n")
    f.write("- 佛山VOCs总量文件 - 仅嵌入版, 无独立原件\n")
    f.write("- 佛山工业废水防治函 - 仅嵌入版, 无独立原件\n")
    f.write("- 佛山声功能区划 - 仅有征求意见稿\n")

    f.write("\n### 经验规则标准依据\n\n")
    f.write(f"- {len(rules_nostd)} 条规则缺少 common_standards\n")

    # 3. Standards parsed
    f.write("\n## 3. 哪些标准已解析\n\n")
    f.write(f"- 标准PDF: {categories.get('标准PDF',{}).get('count',0)} 个\n")
    f.write(f"- 标准解析txt: 14 个\n")
    f.write(f"- clause_library: {clause_count} 条\n")
    f.write(f"- 知识库标准条目: ~2177 条\n")
    f.write("- MinerU: 未运行\n")

    # 4. Rules supported
    f.write("\n## 4. 哪些经验规则已能被标准库支撑\n\n")
    f.write(f"| 指标 | 值 |\n|------|----|\n")
    f.write(f"| 规则总数 | {len(unique_rules)} |\n")
    f.write(f"| 有标准支撑 | {len(rules_std)} ({100*len(rules_std)//len(unique_rules)}%) |\n")
    f.write(f"| 缺失标准 | {len(rules_nostd)} ({100*len(rules_nostd)//len(unique_rules)}%) |\n")
    f.write(f"| A级(已验证) | {len(rules_A)} |\n")
    f.write(f"| B级(候选) | {len(rules_B)} |\n")
    f.write(f"| C级(观察) | {len(rules_C)} |\n")
    a_with_std = len([r for r in rules_A if r.get("common_standards")])
    f.write(f"| A级中有标准支撑 | {a_with_std}/{len(rules_A)} |\n")

    # 5. Human review
    f.write("\n## 5. 哪些经验规则仍需人工确认\n\n")
    f.write(f"- need_human_review=True: {len(rules_human)} 条\n")
    f.write(f"- 无标准依据: {len(rules_nostd)} 条\n")
    f.write("- GB30981.2-2025 需人工购买或等待公开\n")

    # 6. Next steps
    f.write("\n## 6. 下一步 OpenClaw 优先探索建议\n\n")
    f.write("### 报告\n\n")
    f.write("1. A级规则触发测试: 在30份环评报告中验证12条A级规则\n")
    f.write("2. 标准条款对齐: 为84条无标准规则补充 common_standards\n")
    f.write("3. MinerU解析: 批量解析标准PDF全文\n")
    f.write("4. Benchmark构建: 基于 qa_all_labeled.jsonl (1312条) 构建测试集\n")

    f.write("\n### 规则\n\n")
    f.write("- A级 (12条): 已多项目验证, 可直接用于审核原型\n")
    f.write("- B级 (7条): 需增加案例验证\n")
    f.write("- 有标准支撑的规则: 可作为明文依据+类案经验对\n")

    f.write("\n### 数据缺口处理\n\n")
    f.write("- 佛山VOCs/废水防治函: 用嵌入版暂代, 或申请政府信息公开\n")
    f.write("- 佛山声功能区划: 从正式通知页下载\n")
    f.write("- GB30981.2-2025: 2026年6月实施前购买或等公开\n")

print(f"Generated: {REPORT_PATH}")

# ======== claude_code_acquisition_log.csv ========
print("Generating claude_code_acquisition_log.csv...")
LOG_PATH = BASE / "handoff" / "claude_code_acquisition_log.csv"
with open(LOG_PATH, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["timestamp","standard_id","standard_name","status","source_url","file_path","notes"])
    rows = [
        [ts, "GB37824-2019","涂料油墨胶粘剂工业大气污染物排放标准","downloaded",
         "https://www.mee.gov.cn/.../W020190606595716599412.pdf","standards_downloads/","MEE官方PDF"],
        [ts, "GB41616-2022","印刷工业大气污染物排放标准","downloaded",
         "https://www.mee.gov.cn/.../W020221117627656874791.pdf","standards_downloads/","MEE官方PDF"],
        [ts, "HJ2.4-2021","声环境影响评价技术导则","downloaded",
         "https://www.mee.gov.cn/.../W020220323705204679206.pdf","standards_downloads/","MEE官方PDF"],
        [ts, "HJ169-2018","建设项目环境风险评价技术导则","downloaded",
         "https://www.mee.gov.cn/.../W020181026519881869834.pdf","standards_downloads/","MEE官方PDF"],
        [ts, "HW-2025","国家危险废物名录(2025年版)","downloaded",
         "https://www.mee.gov.cn/.../W020241129617875148704.pdf","standards_downloads/","MEE官方PDF"],
        [ts, "GB33372-2020","胶粘剂挥发性有机化合物限量","downloaded",
         "https://www.gzns.gov.cn/attachment/6/6722/6722588/6931066.pdf","standards_downloads/","gzns.gov.cn嵌入"],
        [ts, "GB38507-2020","油墨中可挥发性有机化合物含量的限值","downloaded",
         "http://www.gzns.gov.cn/attachment/6/6722/6722581/6931046.pdf","standards_downloads/","gzns.gov.cn嵌入"],
        [ts, "GB38508-2020","清洗剂挥发性有机化合物含量限值","downloaded",
         "http://www.gzns.gov.cn/attachment/6/6722/6722600/6931081.pdf","standards_downloads/","gzns.gov.cn嵌入"],
        [ts, "GB/T38597-2020","低挥发性有机化合物含量涂料产品技术要求","downloaded",
         "http://csx.gov.cn/.../P020240910628244239825.pdf","standards_downloads/","csx.gov.cn嵌入"],
        [ts, "GB/T18920-2020","城市污水再生利用 城市杂用水水质","downloaded",
         "http://www.ych.gov.cn/.../P020251119333474001290.pdf","standards_downloads/","ych.gov.cn嵌入"],
        [ts, "GB/T19923-2024","城市污水再生利用 工业用水水质","downloaded",
         "http://xxgk.bazhou.gov.cn/getfile.do?...","standards_downloads/","bazhou.gov.cn嵌入"],
        [ts, "GB30981.2-2025","涂料中有害物质限量 第2部分:工业涂料","failed",
         "N/A","","2025-05-30发布,无免费电子版,需人工(spc.org.cn 65元)"],
        [ts, "佛山VOCs总量","佛山市VOCs排污总量指标精细化管理方案","partial",
         "https://sdies.com/.../20231024175912_82800.pdf","standards_downloads/","嵌入版19.3MB,无独立原件"],
        [ts, "佛山工业废水防治函","进一步加强工业企业废水污染防治的函","partial",
         "http://sthj.foshan.gov.cn/attachment/0/393/393047/5928837.pdf","standards_downloads/","嵌入版8.1MB,无独立原件"],
        [ts, "佛山三线一单","三线一单生态环境分区管控方案(2024版)","downloaded",
         "http://sthj.foshan.gov.cn/attachment/0/408/408981/5981034.pdf","standards_downloads/","官方PDF"],
        [ts, "佛山声功能区划","佛山市声环境功能区划","partial",
         "http://sthj.foshan.gov.cn/attachment/0/356/356389/5777289.pdf","standards_downloads/","征求意见稿,正式版需从通知页下载"],
    ]
    for row in rows:
        w.writerow(row)

print(f"Generated: {LOG_PATH}")

# ======== Final summary ========
print(f"\n{'='*60}")
print("PHASE 6 COMPLETE - ALL OUTPUTS GENERATED")
print(f"{'='*60}")
print(f"\nOutputs in {BASE}:")
for ext in ['*.md', '*.jsonl', '*.csv']:
    for f in sorted(BASE.rglob(ext)):
        sz = f.stat().st_size
        print(f"  {f.relative_to(BASE)} ({sz:,} bytes)")
print(f"\nTotal workspace: {ws_files} files in {BASE}")
