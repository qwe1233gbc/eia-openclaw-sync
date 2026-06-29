# Claude Code 上传与集成提示词

请把本压缩包中的 `03_标准库_从Dify知识库解析/` 上传到 GitHub 仓库：

`qwe1233gbc/eia-openclaw-sync`

建议目标路径：

`03_法规库_明文依据/parsed_from_dify_kb_standard_cards/`

执行要求：

1. 保留 `standard_cards.jsonl`、`standard_cards.json`、`skills_to_standard_mapping.yaml`、`cards_by_skill/`、`quality/`。
2. 更新仓库根 README 或 `03_法规库_明文依据/README.md`，增加“Dify 知识库解析版标准卡”的说明。
3. 检查 `09_环评审核技能库` 中 01–15 每个 skill 的 `config.yaml`，增加标准库引用：

```yaml
standard_library:
  source: "03_法规库_明文依据/parsed_from_dify_kb_standard_cards/standard_cards.jsonl"
  mapping: "03_法规库_明文依据/parsed_from_dify_kb_standard_cards/skills_to_standard_mapping.yaml"
  retrieval_fields:
    - skill_ids
    - retrieval_tags
    - trigger_keywords
    - source_basis
```

4. 不要删除原始 Dify 知识库；本目录是解析后的标准卡层，用于给技能库调用。
5. 重点注意 `quality/QUALITY_CHECK.md` 中的两个问题：
   - GB3096 夜间限值以本标准卡修正值为准；
   - 环保投资 5% 是经验阈值，不要写成硬性违法判断。
