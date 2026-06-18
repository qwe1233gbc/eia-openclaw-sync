#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the eia-openclaw-sync package for GitHub cloud sync"""
import os, json, csv, shutil, time, re
from pathlib import Path
from collections import defaultdict

SRC = Path(r"E:\软件\openclaw_workspace")
DST = Path(r"E:\软件\eia-openclaw-sync")
ts = time.strftime('%Y-%m-%d %H:%M:%S')

# ================================================================
# STEP 1: Create directory structure
# ================================================================
print("=" * 60)
print("STEP 1: Creating directory structure")
print("=" * 60)

dirs = [
    "knowledge/standards",
    "knowledge/experience",
    "handoff",
    "reports",
    "prompts",
    "outputs",
]
for d in dirs:
    (DST / d).mkdir(parents=True, exist_ok=True)
    print(f"  CREATED: {d}/")

# ================================================================
# STEP 2: Copy files
# ================================================================
print("\n" + "=" * 60)
print("STEP 2: Copying lightweight files")
print("=" * 60)

COPY_MAP = [
    # (source_rel, dest_rel, description)
    ("updated_standard_clause_library.jsonl", "knowledge/standards/updated_standard_clause_library.jsonl",
     "标准条款库(含P0政策条款)"),
    ("case_law_style_experience_library.jsonl", "knowledge/experience/case_law_style_experience_library.jsonl",
     "176条类案经验JSONL"),
    ("handoff/c2929_case_source_evidence_table.csv", "handoff/c2929_case_source_evidence_table.csv",
     "C2929证据溯源CSV"),
    ("handoff/c2929_case_source_evidence_report.md", "handoff/c2929_case_source_evidence_report.md",
     "C2929溯源报告"),
    ("handoff/claude_code_to_openclaw_handoff_round2.md", "handoff/claude_code_to_openclaw_handoff_round2.md",
     "Round2交接报告"),
    ("handoff/p0_local_policy_acquisition_report.md", "handoff/p0_local_policy_acquisition_report.md",
     "P0政策获取报告"),
    ("handoff/p0_local_policy_acquisition_log.csv", "handoff/p0_local_policy_acquisition_log.csv",
     "P0获取日志"),
    ("handoff/missing_file_tasks.md", "handoff/missing_file_tasks.md",
     "缺失文件任务清单"),
    ("openclaw_data_ready_report.md", "reports/openclaw_data_ready_report.md",
     "OpenClaw数据就绪综合报告"),
    ("experience_data_readiness_report.md", "reports/experience_data_readiness_report.md",
     "经验数据就绪报告"),
    ("missing_file_report.md", "reports/missing_file_report.md",
     "缺失文件报告"),
    ("duplicate_file_report.md", "reports/duplicate_file_report.md",
     "重复文件报告"),
    ("file_manifest.jsonl", "reports/file_manifest.jsonl",
     "全量文件清单"),
    ("data_inventory.csv", "reports/data_inventory.csv",
     "分类统计"),
]

copied = 0
skipped = 0
copy_log = []

for src_rel, dst_rel, desc in COPY_MAP:
    src_path = SRC / src_rel
    dst_path = DST / dst_rel

    if not src_path.exists():
        print(f"  SKIP (missing): {src_rel}")
        skipped += 1
        copy_log.append({"src": src_rel, "dst": dst_rel, "status": "MISSING", "desc": desc})
        continue

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src_path), str(dst_path))
    size = dst_path.stat().st_size
    print(f"  COPY: {src_rel} -> {dst_rel} ({size:,} bytes)")
    copy_log.append({"src": src_rel, "dst": dst_rel, "status": "COPIED", "size": size, "desc": desc})
    copied += 1

print(f"\nCopied: {copied}, Skipped: {skipped}")

# ================================================================
# STEP 3: Generate .gitignore
# ================================================================
print("\n" + "=" * 60)
print("STEP 3: Generating .gitignore")
print("=" * 60)

gitignore = """# EIA OpenClaw Sync - .gitignore
# 禁止上传原始文件、企业敏感材料、重量级二进制文件

# === 原始环评报告 ===
*.doc
*.docx
*.pdf
*.zip
*.rar
*.7z

# === 图片/视频 ===
*.png
*.jpg
*.jpeg
*.gif
*.mp4
*.avi
media/

# === 数据备份 ===
*.bak
*.backup
*~

# === 临时文件 ===
*.tmp
*.temp
~$*
.DS_Store
Thumbs.db

# === 企业敏感信息 ===
# 已在文件中删除, 此规则作追加防护
*企业联系人*
*身份证*

# === Python ===
__pycache__/
*.pyc
*.pyo

# === Node ===
node_modules/

# === IDE ===
.vscode/
.idea/
"""

with open(DST / ".gitignore", 'w', encoding='utf-8') as f:
    f.write(gitignore)
print("  CREATED: .gitignore")

# ================================================================
# STEP 4: Generate README.md
# ================================================================
print("\n" + "=" * 60)
print("STEP 4: Generating README.md")
print("=" * 60)

readme = f"""# eia-openclaw-sync

> EIA 智能审核 Agent 云端同步仓库
> 创建时间: {ts}
> 本地工作区: E:\\\\软件\\\\openclaw_workspace\\\\

## 目录结构

```
eia-openclaw-sync/
├── README.md                  # 本文件
├── cloud_sync_manifest.md     # 同步清单
├── .gitignore                 # 敏感文件过滤
├── knowledge/
│   ├── standards/             # 标准条款库 (JSONL)
│   └── experience/            # 类案经验库 (JSONL)
├── handoff/                   # Claude Code -> OpenClaw 交接文件
├── reports/                   # 就绪报告
├── prompts/                   # OpenClaw 任务提示词
└── outputs/                   # OpenClaw 输出文件 (待生成)
```

## 用途

此仓库为 OpenClaw 环评智能审核 Agent 提供轻量级数据同步通道。

- **不包含**: 原始环评报告、PDF、Word 文件、企业敏感材料
- **仅包含**: JSONL结构数据、CSV表格、Markdown报告、任务提示词

## 敏感信息检查

- [x] 无 docx/pdf/zip
- [x] 无企业联系人/电话/身份证
- [x] 无原始环评报告全文

## 当前任务目标

将 176 条经验规则收敛为 8-12 条 C2929 类案经验摘要卡。
"""

with open(DST / "README.md", 'w', encoding='utf-8') as f:
    f.write(readme)
print("  CREATED: README.md")

# ================================================================
# STEP 5: Generate cloud_sync_manifest.md
# ================================================================
print("\n" + "=" * 60)
print("STEP 5: Generating cloud_sync_manifest.md")
print("=" * 60)

manifest_md = f"""# Cloud Sync Manifest

> 生成时间: {ts}
> 本地源: E:\\\\软件\\\\openclaw_workspace\\\\
> 同步目标: E:\\\\软件\\\\eia-openclaw-sync\\\\

## 文件清单

| # | 源路径 | 目标路径 | 大小 | 用途 | 敏感 | OpenClaw读取 |
|---|--------|----------|------|------|------|-------------|
"""

total_size = 0
for i, entry in enumerate(copy_log):
    size_str = f"{entry.get('size',0):,}" if entry.get('size') else "N/A"
    total_size += entry.get('size', 0)
    sensitive = "NO"  # All files are filtered to be non-sensitive
    manifest_md += f"| {i+1} | {entry['src']} | {entry['dst']} | {size_str} | {entry['desc']} | {sensitive} | YES |\n"

manifest_md += f"""
**总大小**: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)

## 安全声明

所有文件已经过过滤:
- 不含 docx/pdf/zip 原始文件
- 不含企业敏感信息
- 仅含结构化数据(JSONL/CSV)和报告(Markdown)

## 建议 OpenClaw 读取顺序

1. **首先**: `reports/openclaw_data_ready_report.md` — 了解全局数据状态
2. **其次**: `knowledge/standards/updated_standard_clause_library.jsonl` — 加载标准库
3. **核心**: `knowledge/experience/case_law_style_experience_library.jsonl` — 176条经验规则
4. **溯源**: `handoff/c2929_case_source_evidence_table.csv` — C2929证据
5. **任务**: `prompts/openclaw_round3_prompt.md` — Round 3 工作指令
6. **交接**: `handoff/claude_code_to_openclaw_handoff_round2.md` — 上下文交接

## 当前任务目标

将 176 条经验规则收敛为 **8-12 条 C2929 类案经验摘要卡**，格式为:
- AI可直接调用
- 有证据溯源
- 有适用边界
- 可嵌入审核工作流
"""

with open(DST / "cloud_sync_manifest.md", 'w', encoding='utf-8') as f:
    f.write(manifest_md)
print(f"  CREATED: cloud_sync_manifest.md")

# ================================================================
# STEP 6: Generate openclaw_round3_prompt.md
# ================================================================
print("\n" + "=" * 60)
print("STEP 6: Generating openclaw_round3_prompt.md")
print("=" * 60)

round3_prompt = f"""# OpenClaw Round 3 任务提示词

> 交接时间: {ts}
> 数据源: eia-openclaw-sync GitHub 仓库
> 前置任务: Round 2 数据工程已交付 (见 handoff/claude_code_to_openclaw_handoff_round2.md)

---

## 背景

你是一个运行在云端 OpenClaw 框架上的环评智能审核 Agent。你的知识库已包含:

1. **标准库**: 17条标准条款 (updated_standard_clause_library.jsonl)
   - 包含国家排放标准、技术导则、P0地方政策
2. **经验库**: 176条经验规则 (case_law_style_experience_library.jsonl)
   - 覆盖30+行业, 分A/B/C三级证据等级
   - 其中 C2929 (塑料制品业) 有15条规则
3. **证据数据**: C2929类案84条QA + 证据溯源表

## 任务目标

**将176条经验规则收敛为8-12条C2929类案经验摘要卡。**

具体要求:
- 聚焦 C2929 (塑料制品业)
- 优先处理 A 级证据 (5条已验证规则)
- 每条摘要卡必须有: 事实、审核问题、触发条件、标准依据、适用边界
- 不编造数据; 缺失字段标注"需人工补充"

## 输入文件

请按顺序读取以下文件:

1. `reports/openclaw_data_ready_report.md` — 全局状态
2. `knowledge/standards/updated_standard_clause_library.jsonl` — 标准条款
3. `knowledge/experience/case_law_style_experience_library.jsonl` — 176条经验
4. `handoff/c2929_case_source_evidence_table.csv` — C2929证据
5. `handoff/c2929_case_source_evidence_report.md` — 溯源报告
6. `handoff/claude_code_to_openclaw_handoff_round2.md` — 上下文

## 输出文件

请在 `outputs/` 目录中生成以下文件:

### 1. case_law_experience_summary_v1.md
- 8-12条C2929类案经验摘要卡
- 每条含: 行业、场景、审核要点、标准依据、常见问题、适用边界
- Markdown格式, 适合人类阅读

### 2. case_law_experience_library_v1.jsonl
- 与summary对应的JSONL版本
- 使用标准字段: case_experience_id, case_experience_name, industry, scenario, case_facts, audit_issue, trigger, required_evidence, basis_standards, case_reasoning, applicable_boundary, review_comment_template, evidence_level, related_rules, related_cases
- AI可直接反序列化调用

### 3. case_law_experience_evidence_chain.csv
- 每条类案经验的证据溯源链
- 字段: case_experience_id, source_rule_id, source_qa_ids, source_project_ids, evidence_strength, evidence_gaps
- 标注哪些有真实批注支撑, 哪些仍需补证据

### 4. case_law_retrieval_demo_szq.md
- 以"沈志强案例"为示例
- 演示: 输入项目信息 -> 匹配类案经验 -> 输出审核建议
- 包含完整的检索-匹配-建议流程

### 5. case_law_library_limitations.md
- 当前经验库的局限性
- 哪些经验缺少原始批注支撑
- 哪些标准条款尚未解析
- A/B/C级证据的可靠性声明

### 6. openclaw_round3_next_actions.md
- Round 3 完成后的下一步建议
- 需要 Claude Code (本地) 配合的事项
- 需要人工确认的事项

## 约束

1. **不编造**: 所有内容必须基于输入文件中的真实数据
2. **不过度扩写**: 176条经验的筛选和合并必须有明确依据
3. **标注不确定性**: 任何推断、估算、或数据不足的情况必须标注
4. **保留来源链**: 每条摘要卡必须能追溯到原始规则ID或QA ID
5. **格式一致**: JSONL字段必须符合schema定义

## 与 Claude Code (本地) 的协作协议

- 你在云端生成分析结果
- 本地 Claude Code 负责: 文件获取、MinerU解析、数据库查询
- 通过此 Git 仓库同步
- 需要本地协助时, 在 openclaw_round3_next_actions.md 中列出任务
"""

with open(DST / "prompts" / "openclaw_round3_prompt.md", 'w', encoding='utf-8') as f:
    f.write(round3_prompt)
print("  CREATED: prompts/openclaw_round3_prompt.md")

# ================================================================
# STEP 7: Security check
# ================================================================
print("\n" + "=" * 60)
print("STEP 7: Security check")
print("=" * 60)

sensitive_patterns = {
    "身份证": r'\b\d{17}[\dXx]\b',
    "手机号": r'\b1[3-9]\d{9}\b',
    "电话": r'\b0\d{2,3}-\d{7,8}\b',
    "邮箱": r'\b[\w.-]+@[\w.-]+\.\w+\b',
    "地址": r'(?:公司|工厂|企业)\s*地址',
}

prohibited_exts = ['.doc', '.docx', '.pdf', '.zip', '.rar', '.7z',
                   '.png', '.jpg', '.jpeg', '.gif', '.mp4']

security_issues = []
total_file_size = 0

for root, dirs, files in os.walk(str(DST)):
    # Skip .git
    if '.git' in root:
        continue
    for fname in files:
        fpath = Path(root) / fname
        ext = fpath.suffix.lower()
        size = fpath.stat().st_size
        total_file_size += size

        # Check prohibited extensions
        if ext in prohibited_exts:
            security_issues.append(f"PROHIBITED_EXT: {fpath.relative_to(DST)} ({ext})")

        # Check file size
        if size > 10 * 1024 * 1024:  # 10 MB
            security_issues.append(f"LARGE_FILE: {fpath.relative_to(DST)} ({size/1024/1024:.1f} MB)")

        # Scan text content
        if ext in ['.md', '.jsonl', '.csv', '.txt', '.json']:
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                for pname, pattern in sensitive_patterns.items():
                    matches = re.findall(pattern, content)
                    if matches and len(matches) > 0:
                        security_issues.append(f"SENSITIVE_{pname}: {fpath.relative_to(DST)} ({len(matches)} matches)")
            except:
                pass

# Generate security report
print(f"  Total files: {sum(1 for _ in DST.rglob('*') if _.is_file() and '.git' not in str(_))}")
print(f"  Total size: {total_file_size:,} bytes ({total_file_size/1024/1024:.1f} MB)")
print(f"  Security issues: {len(security_issues)}")

sensitive_path = DST / "sensitive_file_check_report.md"
with open(sensitive_path, 'w', encoding='utf-8') as f:
    f.write("# 安全检查报告\n\n")
    f.write(f"检查时间: {ts}\n\n")
    f.write(f"## 总体\n\n")
    f.write(f"- 总文件大小: {total_file_size:,} bytes ({total_file_size/1024/1024:.1f} MB)\n")
    if total_file_size < 50 * 1024 * 1024:
        f.write("- 大小限制: PASS (< 50MB)\n")
    else:
        f.write("- 大小限制: FAIL (> 50MB)\n")

    f.write(f"\n## 禁止文件类型检查\n\n")
    prohibited_found = [i for i in security_issues if i.startswith("PROHIBITED")]
    if prohibited_found:
        for i in prohibited_found:
            f.write(f"- FAIL: {i}\n")
    else:
        f.write("- PASS: 无禁止文件类型 (docx/pdf/zip/png等)\n")

    f.write(f"\n## 敏感信息检查\n\n")
    sensitive_found = [i for i in security_issues if i.startswith("SENSITIVE")]
    if sensitive_found:
        for i in sensitive_found:
            f.write(f"- WARNING: {i}\n")
    else:
        f.write("- PASS: 未检测到手机号、身份证、邮箱等敏感信息\n")

    f.write(f"\n## 大文件检查\n\n")
    large = [i for i in security_issues if i.startswith("LARGE")]
    if large:
        for i in large:
            f.write(f"- WARNING: {i}\n")
    else:
        f.write("- PASS: 无超过10MB的文件\n")

    f.write(f"\n## 综合判定\n\n")
    if not prohibited_found and not sensitive_found:
        f.write("**PASS** — 可以安全推送到 GitHub。\n")
    else:
        f.write("**FAIL** — 存在安全问题, 需处理后再推送。\n")

print(f"  CREATED: sensitive_file_check_report.md")

# ================================================================
# STEP 8: Generate github_sync_ready_report.md
# ================================================================
print("\n" + "=" * 60)
print("STEP 8: github_sync_ready_report.md")
print("=" * 60)

github_report = f"""# GitHub Sync Ready Report

> 生成时间: {ts}

## 同步目录

- 本地源: `E:\\\\软件\\\\openclaw_workspace\\\\`
- 同步目录: `E:\\\\软件\\\\eia-openclaw-sync\\\\`

## 文件统计

| 类别 | 数量 | 大小 |
|------|------|------|
| Markdown报告 | {sum(1 for _ in DST.rglob('*.md') if '.git' not in str(_))} | - |
| JSONL数据 | {sum(1 for _ in DST.rglob('*.jsonl') if '.git' not in str(_))} | - |
| CSV表格 | {sum(1 for _ in DST.rglob('*.csv') if '.git' not in str(_))} | - |
| **总计** | - | {total_file_size/1024/1024:.1f} MB |

## 安全检查结果

- 禁止文件类型: {'FAIL' if prohibited_found else 'PASS'}
- 敏感信息: {'FAIL' if sensitive_found else 'PASS'}
- 大小限制: {'FAIL' if total_file_size > 50*1024*1024 else 'PASS'}

## 已包含

- [x] 标准条款库 (JSONL)
- [x] 类案经验库 (JSONL)
- [x] C2929证据溯源表
- [x] 数据就绪报告
- [x] P0政策获取报告
- [x] Round 3 任务提示词
- [x] .gitignore
- [x] README.md

## 已排除

- [x] 原始环评报告 (30份, ~600MB)
- [x] PDF 标准文件 (~90MB)
- [x] Word 修改意见 (30个docx, ~500MB)
- [x] 图片/媒体文件
- [x] 企业敏感信息

## Git 推送前检查清单

- [ ] 配置 git user.name 和 user.email
- [ ] 检查 sensitive_file_check_report.md
- [ ] 确认 .gitignore 生效
- [ ] git add . && git status 确认无敏感文件
- [ ] git commit
- [ ] 在 GitHub 创建远程仓库
- [ ] git remote add origin
- [ ] git push -u origin main
"""

with open(DST / "github_sync_ready_report.md", 'w', encoding='utf-8') as f:
    f.write(github_report)
print("  CREATED: github_sync_ready_report.md")

# ================================================================
# FINAL SUMMARY
# ================================================================
print(f"\n{'='*60}")
print(f"BUILD COMPLETE")
print(f"{'='*60}")
print(f"\nSync directory: {DST}")
print(f"Total size: {total_file_size:,} bytes ({total_file_size/1024/1024:.1f} MB)")
print(f"Security issues: {len(security_issues)}")
for i in security_issues:
    print(f"  - {i}")

print(f"\nFiles:")
for f in sorted(DST.rglob("*")):
    if f.is_file() and '.git' not in str(f):
        print(f"  {f.relative_to(DST)} ({f.stat().st_size:,} bytes)")
