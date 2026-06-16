# Agent Collaboration Protocol

> 四智能体 + GitHub 信息中枢 协作架构

## 角色分工

| 智能体 | 角色 | 职责 |
|--------|------|------|
| **GPT** | 指挥官 | 统筹研究全局、分配任务、审阅输出 |
| **Claude Code** | 本地资料工程 | 文件处理、标准库构建、样本链管理、数据工程 |
| **Codex** | 文献综述与论文叙事 | 论文阅读、文献综述、方法论分析、论文写作 |
| **OpenClaw** | 实验执行与Skill验证 | 运行benchmark、验证标准库/经验库有效性、输出评分报告 |

## 信息中枢

| 平台 | 用途 |
|------|------|
| **GitHub** (`qwe1233gbc/eia-openclaw-sync`) | 四个智能体的共享信息中枢，所有结构化数据、报告、benchmark结果的交换站 |
| **飞书** (cc-connect) | 实时消息通信，Claude Code 和 OpenClaw 的消息入口 |

## 协作流程

```
GPT (指挥官)
  │ 任务分配
  ├─→ Claude Code: 整理标准库、下载政策文件、构建样本链
  ├─→ Codex: 阅读论文、撰写文献综述、方法论章节
  └─→ OpenClaw: 执行benchmark实验、输出评分报告
  │
  ▼
GitHub (信息中枢)
  │ 所有输出汇聚
  ▼
GPT (指挥官)
  │ 审阅、整合、指导下一轮
```

## 当前工作目录

- Claude Code: `E:\软件\eia_plastic_guide_research_pack\`
- GitHub 中枢: `https://github.com/qwe1233gbc/eia-openclaw-sync`
- 飞书通道: `eia-research` + `home-claude`
