# 环评审核技能库（细化版）

本包用于替换或增量更新仓库中的 `09_环评审核技能库`。核心改造是把 Dify 工作流中的“证据筛选—字段抽取—法规检索—单项判断”拆成可独立执行的 skill，并统一输出 JSON，便于后续 A/B/C/D 消融实验。

真正的分界点是：法规库回答“依据是什么”，技能库回答“怎么审、取哪些证据、怎么算、输出什么结构”。

## 文件结构

```text
09_环评审核技能库/
├── 01_国民经济行业类别审核/
│   ├── SKILL.md
│   ├── config.yaml
│   └── output_example.json
├── ...
├── 15_VOCs总量控制审核/
├── 99_总审核汇总/
├── common_output_schema.json
└── skill_registry.yaml
```

## 使用方式

1. 解压 zip 到仓库根目录。
2. 用本包内的 `09_环评审核技能库` 覆盖原目录，或先提交到新分支对比差异。
3. 让 Claude Code 按 `skill_registry.yaml` 检查每个 skill 是否存在 `SKILL.md / config.yaml / output_example.json`。
4. 后续 Dify 节点迁移时，优先把每个工作流的 code 节点逻辑写入对应 `config.yaml.keywords` 和 `SKILL.md` 的“证据提取策略”。

## 消融实验对应

- A：LLM only → 不读取 `law_cards`，不读取 skill，只用原始问题。
- B：LLM + 法规库 → 读取 `law_cards`，不读取 skill。
- C：LLM + 技能库 → 读取本目录 skill，不读取法规库。
- D：LLM + 法规库 + 技能库 → 读取本目录 skill 和法规库，这是目标组。
