# eia-openclaw-sync

> EIA 智能审核 Agent 云端同步仓库
> 创建时间: 2026-06-14 10:53:07
> 本地工作区: E:\\软件\\openclaw_workspace\\

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
