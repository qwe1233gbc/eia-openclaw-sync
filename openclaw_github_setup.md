# OpenClaw GitHub 访问配置

> 发给 OpenClaw Agent 的仓库访问信息
> 生成时间: 2026-06-14

---

## 一、GitHub 账号

| 项目 | 值 |
|------|-----|
| 用户名 | `qwe1233gbc` |
| 显示名 | Yang Long Xiang |

## 二、目标仓库

| 项目 | 值 |
|------|-----|
| 仓库 | `qwe1233gbc/eia-openclaw-sync` |
| 可见性 | Private |
| 默认分支 | `main` |
| HTTPS Clone | `https://github.com/qwe1233gbc/eia-openclaw-sync.git` |
| SSH Clone | `git@github.com:qwe1233gbc/eia-openclaw-sync.git` |
| Web URL | `https://github.com/qwe1233gbc/eia-openclaw-sync` |

## 三、访问令牌 (Personal Access Token)

```
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
```

**权限范围**: Contents Read & Write（仅限此仓库）

## 四、环境变量配置

请在你的运行环境中设置：

```bash
export GITHUB_TOKEN="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"
export GITHUB_REPO="qwe1233gbc/eia-openclaw-sync"
export GITHUB_USER="qwe1233gbc"
```

## 五、Git 操作命令

### 克隆仓库

```bash
git clone https://oauth2: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@github.com/qwe1233gbc/eia-openclaw-sync.git
```

### 拉取最新

```bash
cd eia-openclaw-sync
git pull origin main
```

### 提交并推送

```bash
cd eia-openclaw-sync
git add outputs/
git commit -m "round3: 类案经验摘要卡 + 证据链"
git push origin main
```

## 六、仓库目录结构

```
eia-openclaw-sync/
├── README.md
├── cloud_sync_manifest.md          # 同步清单（读取顺序）
├── .gitignore                       # 已排除PDF/docx/zip
├── knowledge/
│   ├── standards/
│   │   └── updated_standard_clause_library.jsonl   # 17条标准条款
│   └── experience/
│       └── case_law_style_experience_library.jsonl  # 176条经验规则
├── handoff/
│   ├── claude_code_to_openclaw_handoff_round2.md    # Round2 交接
│   ├── c2929_case_source_evidence_table.csv          # C2929证据
│   ├── c2929_case_source_evidence_report.md
│   ├── p0_local_policy_acquisition_report.md
│   └── missing_file_tasks.md
├── reports/
│   ├── openclaw_data_ready_report.md                # 全局状态
│   └── experience_data_readiness_report.md
├── prompts/
│   └── openclaw_round3_prompt.md                    # Round3 任务指令
└── outputs/                                          # 你的输出目录
    ├── (待生成) case_law_experience_summary_v1.md
    ├── (待生成) case_law_experience_library_v1.jsonl
    ├── (待生成) case_law_experience_evidence_chain.csv
    ├── (待生成) case_law_retrieval_demo_szq.md
    ├── (待生成) case_law_library_limitations.md
    └── (待生成) openclaw_round3_next_actions.md
```

## 七、你的 Round 3 任务

详细指令见 `prompts/openclaw_round3_prompt.md`。

核心目标：将 176 条经验规则收敛为 **8—12 条 C2929 类案经验摘要卡**。

建议读取顺序：
1. `reports/openclaw_data_ready_report.md` — 了解全局
2. `knowledge/standards/updated_standard_clause_library.jsonl` — 加载标准库
3. `knowledge/experience/case_law_style_experience_library.jsonl` — 加载经验
4. `handoff/c2929_case_source_evidence_table.csv` — 证据溯源
5. `prompts/openclaw_round3_prompt.md` — 执行任务

完成后的输出请放到 `outputs/` 目录，然后 git commit + push。
