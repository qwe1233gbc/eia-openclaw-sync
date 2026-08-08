# C组实验Skill清单

## 主Skill

| 编号 | Skill目录 | 覆盖问题 | 是否需要外部资料 |
|---|---|---|---|
| 01 | `01_manual-audit-national-economic-industry-classification` | 国民经济行业分类4题 | 已保留分类注释参考；必须删除测试项目案例 |
| 02 | `02_review-eia-environmental-investment` | 环保投资1题 | 不需要 |
| 05 | `05_review-eia-environmental-quality-data` | 环境质量3题 | 内部核验不需要；官方一致性需要公报 |
| 07 | `07_review-eia-pollutant-discharge-standards` | 水3题、气1题、噪声4题、固废5题 | 内部核验不需要；正式适用性需要标准资料 |

## 支持模块

| 模块 | 作用 | 是否计入实验Skill |
|---|---|---|
| `00_validate-eia-parsed-text` | 检查报告解析质量、批注泄漏和表格保真 | 否 |
| `retrieve-eia-discharge-standard-knowledge` | 对用户提供的正式标准资料进行结构化和匹配 | 否 |

## 删除项

- 删除重复的`review-eia-industry-classification`；
- 删除`liangzheng-case.md`；
- 不新增“行业分类报告内版”；
- 不将种子样本适宜性并入环境专业审核Skill。
