# Codex任务：将21题C组Skill重整版接入实验分支

## 目标

使用本包的4个主Skill覆盖21道题，减少因外部RAG为空而产生的无效整题拒答，同时避免测试项目案例和人工批注泄漏。

## 1. Skill路由

- 国民经济行业分类 → Skill 01
- 环保投资 → Skill 02
- 环境质量数据引用 → Skill 05
- 水/气/噪声/固废排放控制标准 → Skill 07

删除重复的`review-eia-industry-classification`路由。

## 2. 输入清洗

对每份DOCX生成实验上下文前：

- 删除comments、commentRangeStart、commentRangeEnd；
- 接受或移除修订痕迹；
- 删除人工修改意见；
- 删除联系人、电话、身份证和附件个人信息；
- 保留正文、表格、公式和章节位置。

生成`input_sanitization_report.json`，记录批注数、修订数和PII清理结果。

## 3. 双层输出

所有Skill统一使用：

```text
report_internal_result
external_validation_result
final_answer
```

外部资料为空时：

- 继续完成报告内部证据抽取、算术和一致性检查；
- `external_validation_result.status=not_performed`；
- 不得把整道题简化为“无法判断”。

## 4. 实验定位

如果只运行C组，在报告中标记：

```text
experiment_type = skill_executability
causal_comparison = false
```

不得生成“Skill提升了多少”的因果结论。

## 5. 防泄漏检查

提交前扫描全部Skill和输入：

- `PL001`
- `亮正`
- Question ID
- 人工答案
- `Comment by`
- 固定项目数值

除输入报告中的项目名外，Skill文件命中数量必须为0。

## 6. 产物

- 重整后Skill目录；
- 路由表；
- Skill SHA256；
- 输入清洗报告；
- 21题C组输出；
- 逐题执行状态；
- 报告内部完成率；
- 外部资料未提供率；
- 无依据强答率；
- 待人工复核清单。

禁止自动合并主分支。
