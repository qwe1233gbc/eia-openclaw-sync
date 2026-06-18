#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all final outputs for the handoff round 2"""
import json, csv, os, time
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:\软件\openclaw_workspace")
HANDOFF = BASE / "handoff"
HANDOFF.mkdir(parents=True, exist_ok=True)
ts = time.strftime('%Y-%m-%d %H:%M:%S')

# ================================================================
# OUTPUT 1: p0_local_policy_acquisition_report.md
# ================================================================
print("1. p0_local_policy_acquisition_report.md")
with open(HANDOFF / "p0_local_policy_acquisition_report.md", 'w', encoding='utf-8') as f:
    f.write("# P0 本地政策文件获取报告\n\n")
    f.write(f"生成时间: {ts}\n\n")

    f.write("## 1. 佛环函(2024)70号\n\n")
    f.write("**文件名称**: 佛山市生态环境局关于加强活性炭吸附工艺规范化设计建设与运行管理的通知\n")
    f.write("**发布日期**: 2024-05-15\n")
    f.write("**状态**: 已下载 (嵌入版, 2个来源)\n\n")
    f.write("- v1: 19.3 MB (sthj.foshan.gov.cn PDF)\n")
    f.write("- v2: 34.9 MB (sthj.foshan.gov.cn PDF)\n")
    f.write("- 来源: http://sthj.foshan.gov.cn/attachment/0/566/566047/6788170.pdf\n")
    f.write("- 来源: http://sthj.foshan.gov.cn/attachment/0/566/566566/6798079.pdf\n\n")
    f.write("**关键条款**:\n")
    f.write("- 活性炭碘值: 颗粒 >=800mg/g, 蜂窝 >=650mg/g\n")
    f.write("- 气体流速: 颗粒 <0.6m/s, 蜂窝 <1.2m/s\n")
    f.write("- 停留时间: 0.5-1s\n")
    f.write("- 装填厚度: 颗粒 >=300mm, 蜂窝 >=600mm\n")
    f.write("- 温度监控: 进气 <=40C, 83C报警\n")
    f.write("- 压差计: 每个炭箱需安装\n\n")

    f.write("## 2. 顺环委办(2023)19号\n\n")
    f.write("**状态**: 未找到\n\n")
    f.write("**说明**: 该文号在公开渠道未检索到原文。同系列文件:\n")
    f.write("- 顺环委办(2024)3号: 顺德区重点行业VOCs总量指标管理工作方案(2024年修订)\n")
    f.write("- 顺环委办(2023)30号: 顺德区工业废水退出城镇生活污水处理系统工作推进方案(试行)\n")
    f.write("- 顺环委办(2020)44号: 关于对涉水排放的建设项目加强环境管理的通知\n\n")
    f.write("**替代文件已下载**:\n")
    f.write("- 顺环委办(2023)30号: 8.8 MB (污水处理方案)\n")
    f.write("- 顺环委办(2020)44号: 5.3 MB (涉水排放管理)\n\n")
    f.write("**建议**: 核实文号是否正确; 向顺德区生态环境保护委员会办公室申请政府信息公开\n\n")

    f.write("## 3. 顺德排水口径文件\n\n")
    f.write("**状态**: 未找到明确的单一文件\n\n")
    f.write("**可能相关文件**:\n")
    f.write("- 顺环委办(2023)30号: 工业废水退出城镇生活污水处理系统 (已下载)\n")
    f.write("- 顺环委办(2020)44号: 涉水排放建设项目环境管理 (已下载)\n")
    f.write("- 顺德区围内河涌管理实施办法 (shunde.gov.cn)\n\n")
    f.write("**建议**: 确认具体文件名称后再检索\n\n")

    f.write("## 4. 已下载文件清单\n\n")
    f.write("| 文件 | 大小 | 状态 |\n")
    f.write("|------|------|------|\n")
    f.write("| 佛环函(2024)70号 v1 | 19.3 MB | 嵌入版 |\n")
    f.write("| 佛环函(2024)70号 v2 | 34.9 MB | 嵌入版 |\n")
    f.write("| 顺环委办(2023)30号 | 8.8 MB | 嵌入版(替代) |\n")
    f.write("| 顺环委办(2020)44号 | 5.3 MB | 嵌入版(替代) |\n")

print("   done")

# ================================================================
# OUTPUT 2: p0_local_policy_acquisition_log.csv
# ================================================================
print("2. p0_local_policy_acquisition_log.csv")
with open(HANDOFF / "p0_local_policy_acquisition_log.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["timestamp","doc_id","doc_name","status","source_url","file_path","file_size_mb","notes"])
    w.writerow([ts,"佛环函(2024)70号","活性炭吸附工艺规范化设计建设与运行管理通知","downloaded_embedded",
                "http://sthj.foshan.gov.cn/attachment/0/566/566047/6788170.pdf",
                "p0_policies/佛环函2024_70号_嵌入版_1.pdf","19.3","嵌入在大型PDF中,非独立原件"])
    w.writerow([ts,"佛环函(2024)70号","活性炭吸附工艺规范化设计建设与运行管理通知","downloaded_embedded",
                "http://sthj.foshan.gov.cn/attachment/0/566/566566/6798079.pdf",
                "p0_policies/佛环函2024_70号_嵌入版_2.pdf","34.9","嵌入在大型PDF中"])
    w.writerow([ts,"顺环委办(2023)19号","(未知文件名)","not_found",
                "N/A","","","文号未检索到原文,已下载(2023)30号和(2020)44号作为替代"])
    w.writerow([ts,"顺环委办(2023)30号","工业废水退出城镇生活污水处理系统工作推进方案","downloaded_embedded",
                "http://www.shunde.gov.cn/attachment/0/486/486291/6187853.pdf",
                "p0_policies/顺环委办2023_30号_嵌入版.pdf","8.8","替代(2023)19号"])
    w.writerow([ts,"顺环委办(2020)44号","涉水排放建设项目环境管理通知","downloaded_embedded",
                "http://www.shunde.gov.cn/attachment/0/423/423500/6064150.pdf",
                "p0_policies/顺环委办2020_44号_嵌入版.pdf","5.3","替代(2023)19号"])
    w.writerow([ts,"顺德排水口径","(待确认)","not_found",
                "N/A","","","文件名称不明确,无法检索;顺环委办30号和44号可能相关"])

print("   done")

# ================================================================
# OUTPUT 3: updated_standard_clause_library.jsonl (add P0 clauses)
# ================================================================
print("3. updated_standard_clause_library.jsonl")
# Read existing library
existing = []
lib_path = BASE / "standard_clause_library.jsonl"
if lib_path.exists():
    with open(lib_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                existing.append(json.loads(line))

# Add new clauses from P0 policies
new_clauses = [
    {
        "source": "p0_local_policy",
        "standard_id": "佛环函(2024)70号",
        "standard_name": "佛山市生态环境局关于加强活性炭吸附工艺规范化设计建设与运行管理的通知",
        "scope": "佛山市VOCs4+2企业活性炭吸附工艺",
        "key_tables": [
            {"name": "活性炭参数要求", "rows": [
                {"param": "碘吸附值(颗粒)", "value": ">=800 mg/g"},
                {"param": "碘吸附值(蜂窝)", "value": ">=650 mg/g"},
                {"param": "比表面积(颗粒)", "value": ">=850 m2/g"},
                {"param": "比表面积(蜂窝)", "value": ">=750 m2/g"},
                {"param": "气体流速(颗粒)", "value": "<0.6 m/s"},
                {"param": "气体流速(蜂窝)", "value": "<1.2 m/s"},
                {"param": "停留时间", "value": "0.5-1 s"},
                {"param": "装填厚度(颗粒)", "value": ">=300 mm"},
                {"param": "装填厚度(蜂窝)", "value": ">=600 mm"},
            ]}
        ],
        "limits": [
            "适用条件: 间歇式生产、单体风量<30000m3/h、VOCs进口浓度约300mg/m3(不超过600mg/m3)",
            "进气颗粒物<1mg/m3, 温度<40C",
            "不含低沸点、易溶于水等物质组分"
        ],
        "requirements": [
            "环评应明确: 废气预处理工序、活性炭箱体体积、填装数量/质量、更换周期",
            "排污许可证应载明: 活性炭品质要求、设计风量、类型、填装量、更换周期、碘值",
            "每个炭箱安装压差计和温度传感器",
            "进风风管安装防火阀(65-80C自动关闭)",
            "温度达83C报警",
        ],
        "status": "parsed_from_embedded_pdf",
        "parser_notes": "嵌入版PDF, 非独立原件, 条款提取自环评报告引用"
    },
    {
        "source": "p0_local_policy",
        "standard_id": "顺环委办(2023)30号",
        "standard_name": "顺德区工业废水退出城镇生活污水处理系统工作推进方案(试行)",
        "scope": "顺德区工业废水排放管理",
        "key_tables": [],
        "limits": [],
        "requirements": ["工业废水分类管理", "退出城镇生活污水处理系统的条件和程序"],
        "status": "parsed_from_embedded_pdf",
        "parser_notes": "替代顺环委办(2023)19号; 嵌入版PDF"
    },
    {
        "source": "p0_local_policy",
        "standard_id": "顺环委办(2020)44号",
        "standard_name": "关于对涉水排放的建设项目加强环境管理的通知",
        "scope": "顺德区涉水排放建设项目",
        "key_tables": [],
        "limits": [],
        "requirements": ["涉水排放项目环境管理要求"],
        "status": "parsed_from_embedded_pdf",
        "parser_notes": "替代顺环委办(2023)19号; 嵌入版PDF"
    },
]

for nc in new_clauses:
    existing.append(nc)

with open(BASE / "updated_standard_clause_library.jsonl", 'w', encoding='utf-8') as f:
    for e in existing:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')

print(f"   {len(existing)} total entries (+{len(new_clauses)} new)")

# ================================================================
# OUTPUT 4: case_law_style_experience_library.jsonl
# ================================================================
print("4. case_law_style_experience_library.jsonl")
# case_law files not found on disk - generate from rules
RULES_DIR = Path(r"E:\eia-llm-judge-framework\eia_experience_review_project\04_experience_library\source_rules")
all_rules = []
for fname in ["experience_rules_all.json"]:
    fp = RULES_DIR / fname
    if fp.exists():
        with open(fp, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        if isinstance(data, list):
            all_rules.extend(data)

case_library = []
for r in all_rules:
    entry = {
        "case_experience_id": r.get("rule_id", ""),
        "case_experience_name": "",
        "industry": r.get("industry_code", ""),
        "scenario": r.get("project_type", ""),
        "case_facts": "需人工补充",
        "audit_issue": r.get("trigger_condition", ""),
        "trigger": r.get("review_checkpoints", []) if isinstance(r.get("review_checkpoints"), list) else [],
        "required_evidence": [],
        "basis_standards": r.get("common_standards", []),
        "case_reasoning": r.get("common_approval_requirement", ""),
        "applicable_boundary": r.get("limitations", ""),
        "review_comment_template": r.get("expected_report_content", ""),
        "evidence_level": r.get("evidence_level", ""),
        "related_rules": [],
        "related_cases": r.get("source_project_ids", []) if isinstance(r.get("source_project_ids"), list) else [],
    }

    # Build name
    entry["case_experience_name"] = (
        f"{r.get('industry_code','?')}_{r.get('element','?')}_"
        f"{r.get('project_type','?')}_{r.get('rule_type','?')}"
    )

    # Build required evidence from checkpoints
    cps = r.get("review_checkpoints", [])
    if isinstance(cps, list):
        entry["required_evidence"] = [f"check: {cp}" for cp in cps[:5]]

    # Build trigger from conditions
    tc = r.get("trigger_condition", "")
    if tc:
        entry["trigger"] = [tc]

    # Mark empty fields
    for key in entry:
        if entry[key] == "" or entry[key] == []:
            if key not in ["related_rules", "required_evidence"]:
                entry[key] = "需人工补充" if isinstance(entry[key], str) else entry[key]

    case_library.append(entry)

with open(BASE / "case_law_style_experience_library.jsonl", 'w', encoding='utf-8') as f:
    for e in case_library:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')

print(f"   {len(case_library)} entries (source: experience_rules_all.json)")

# ================================================================
# OUTPUT 5 & 6: c2929 evidence files (already partially done, enhance)
# ================================================================
print("5/6. Enhancing C2929 evidence files...")

# Load existing evidence
evidence_path = HANDOFF / "c2929_case_source_evidence_table.csv"
evidence_rows = []
if evidence_path.exists():
    with open(evidence_path, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            evidence_rows.append(row)

# Enhance with original comments from ai_packages
AI_PKG = Path(r"E:\openclaw_archive\workspace\agent\workspace\ai_packages_extracted\ai_packages")
original_comments = []
for proj_dir in sorted(AI_PKG.iterdir()):
    if not proj_dir.is_dir() or proj_dir.name.startswith("原始") or proj_dir.name == "data":
        continue
    comments_file = proj_dir / "comments.jsonl"
    if not comments_file.exists():
        continue
    with open(comments_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
                text = c.get("comment_text", c.get("text", str(c)))
                original_comments.append({
                    "project": proj_dir.name,
                    "text": str(text)[:500],
                    "file": str(comments_file),
                })
            except:
                pass

# Regenerate evidence CSV with more data
with open(HANDOFF / "c2929_case_source_evidence_table.csv", 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(["case_id","project_name","industry_code","original_comment","audit_module",
                "related_case_experience_id","source_file","manual_check_needed"])
    for i, row in enumerate(evidence_rows):
        w.writerow([row.get(k, "") for k in ["case_id","project_name","industry_code",
                     "original_comment","audit_module","related_case_experience_id","source_file","manual_check_needed"]])
    # Add original comment samples
    for i, c in enumerate(original_comments[:50]):
        w.writerow([
            f"ORIG_{i+1}", c["project"][:80], "C2929", c["text"][:300],
            "", "", c["file"], "Y"
        ])

# Generate evidence report
with open(HANDOFF / "c2929_case_source_evidence_report.md", 'w', encoding='utf-8') as f:
    f.write("# C2929 类案证据溯源报告\n\n")
    f.write(f"生成时间: {ts}\n\n")
    f.write("## 数据源\n\n")
    f.write(f"- qa_all_labeled.jsonl: 1312 QA条目, 其中C2929: 84条\n")
    f.write(f"- C2929经验规则: 15条 (A级5条, C级10条)\n")
    f.write(f"- ai_packages原始批注: {len(original_comments)}条\n\n")
    f.write("## 溯源状态\n\n")
    f.write("| 项目 | 状态 |\n")
    f.write("|------|------|\n")
    f.write(f"| C2929 QA条目 | 84条已提取 |\n")
    f.write(f"| 经验规则匹配 | 待逐条对齐 |\n")
    f.write(f"| 原始批注 | {len(original_comments)}条, 作者信息为空 |\n")
    f.write("| 真实意见原文 | 未找到直接映射 |\n\n")
    f.write("## 问题\n\n")
    f.write("1. comments.jsonl 中 author 字段为空, 无法区分审核人员\n")
    f.write("2. 原始docx批注作者为'审核人'(通用署名), 无法定位到具体审核员\n")
    f.write("3. C2929的经验规则与QA条目的对应关系需人工标注\n\n")
    f.write("## 建议\n\n")
    f.write("- 从数据库中提取 hp_approve_tech.REPLY_NOTE 获取实名技术审查意见\n")
    f.write("- 对84条C2929 QA进行逐条行业标注验证\n")

print("   done")

# ================================================================
# OUTPUT 7: claude_code_to_openclaw_handoff_round2.md
# ================================================================
print("7. claude_code_to_openclaw_handoff_round2.md")

with open(HANDOFF / "claude_code_to_openclaw_handoff_round2.md", 'w', encoding='utf-8') as f:
    f.write("# Claude Code -> OpenClaw Handoff Round 2\n\n")
    f.write(f"交接时间: {ts}\n")
    f.write(f"执行环境: Claude Code (本地 Windows)\n")
    f.write(f"目标: OpenClaw 环评智能审核 Agent\n\n")
    f.write("---\n\n")

    f.write("## 一、P0 地方文件补齐状态\n\n")
    f.write("| 文件 | 状态 | 备注 |\n")
    f.write("|------|------|------|\n")
    f.write("| 佛环函(2024)70号 | 已下载(嵌入版) | 2个来源PDF, 关键条款已提取 |\n")
    f.write("| 顺环委办(2023)19号 | 未找到 | 已下载(2023)30号和(2020)44号替代 |\n")
    f.write("| 顺德排水口径文件 | 未找到 | 文件名不明确, 顺环委办30号可能相关 |\n\n")

    f.write("### 仍需人工获取\n\n")
    f.write("- 顺环委办(2023)19号原件 — 需核实文号或申请政府信息公开\n")
    f.write("- 顺德排水口径文件 — 需先确认具体文件名称\n")
    f.write("- 佛环函(2024)70号独立原件 — 当前仅有嵌入版\n\n")

    f.write("## 二、类案经验 JSONL 转换\n\n")
    f.write(f"- 已转换 {len(case_library)} 条\n")
    f.write("- 来源: experience_rules_all.json (经验规则全量)\n")
    f.write("- 注意: OpenClaw的 case_law_style_experience_summary.md 文件在本地不可用\n")
    f.write("  (OpenClaw云端实例已不可达, 类案经验摘要文件无法获取)\n")
    f.write("- 当前JSONL基于本地经验规则文件生成, 字段已按规范结构化\n\n")

    f.write("## 三、C2929 类案证据溯源\n\n")
    f.write(f"- qa_all_labeled.jsonl: 84条C2929 QA\n")
    f.write(f"- C2929经验规则: 15条 (A:5, C:10)\n")
    f.write(f"- 原始批注: {len(original_comments)}条从ai_packages提取\n")
    f.write("- 真实批注原文: 未找到直接映射关系\n\n")

    f.write("### 问题\n\n")
    f.write("- comments.jsonl 中 author 字段为空, 无法溯源审核员身份\n")
    f.write("- 经验规则与QA条目的对应关系需人工标注\n")
    f.write("- 仍缺原始批注: 84条C2929 QA中大部分未能匹配到真实修改意见原文\n\n")

    f.write("## 四、本次输出文件\n\n")
    f.write("| 文件 | 路径 |\n")
    f.write("|------|------|\n")
    f.write("| p0_local_policy_acquisition_report.md | handoff/ |\n")
    f.write("| p0_local_policy_acquisition_log.csv | handoff/ |\n")
    f.write("| updated_standard_clause_library.jsonl | workspace root |\n")
    f.write("| case_law_style_experience_library.jsonl | workspace root |\n")
    f.write("| c2929_case_source_evidence_table.csv | handoff/ |\n")
    f.write("| c2929_case_source_evidence_report.md | handoff/ |\n")
    f.write("| claude_code_to_openclaw_handoff_round2.md | handoff/ (本文件) |\n\n")

    f.write("## 五、下一步 OpenClaw 建议\n\n")
    f.write("1. 确认顺环委办(2023)19号文号是否正确; 如不正确, 提供正确文号后重新检索\n")
    f.write("2. 如能恢复 OpenClaw 云端, 请提供 case_law_style_experience_summary.md, 重新生成JSONL\n")
    f.write("3. 从数据库 hp_approve_tech.REPLY_NOTE 提取实名技术审查意见, 与C2929类案匹配\n")
    f.write("4. 将 updated_standard_clause_library.jsonl 中的P0政策条款导入标准库\n")
    f.write("5. 对15条C2929经验规则逐条标注QA对应关系\n")

print("   done")

# ================================================================
# FINAL SUMMARY
# ================================================================
print(f"\n{'='*60}")
print("ALL OUTPUTS GENERATED")
print(f"{'='*60}")
for f in sorted(HANDOFF.rglob("*")):
    if f.is_file():
        print(f"  handoff/{f.name} ({f.stat().st_size:,} bytes)")
for f in sorted(BASE.glob("*.jsonl")):
    print(f"  {f.name} ({f.stat().st_size:,} bytes)")
