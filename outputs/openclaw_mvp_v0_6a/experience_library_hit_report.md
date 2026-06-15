# 经验库命中报告 (Experience Library Hit Report)

## 经验库规模
- 总 active 经验卡：8条 (EXP_01 ~ EXP_08)
- 激活命中数：**8条全命中 (100%)**
- candidate 卡调用：0 (未调用，正确)

---

## 按证据等级命中分布

### Core 卡 (3条) — 极有价值

| 经验卡 | 命中次数 | 命中题目 (relevance) | 贡献 |
|--------|---------|---------------------|------|
| EXP_01 胶水VOCs超限值 | 2 HIGH | Q01 (HIGH), Q16 (HIGH) | 胶水限值+全链路双场景触发 |
| EXP_02 活性炭更换周期虚长 | 1 HIGH | Q02 (HIGH) | 更换周期唯一经验 |
| EXP_03 收集效率取95%但非全密闭 | 3 HIGH | Q03 (HIGH), Q05 (HIGH), Q16 (HIGH) | **最高频经验卡** — 收集效率核心风险 |

**Core 卡贡献**: 3条卡共6次HIGH命中，平均2.0次/卡

### Reference 卡 (2条) — 显著贡献

| 经验卡 | 命中次数 | 命中题目 (relevance) | 贡献 |
|--------|---------|---------------------|------|
| EXP_04 复合工艺VOCs遗漏 | 2 HIGH | Q05 (HIGH), Q13 (HIGH) | 跨题推理+工艺矛盾 |
| EXP_06 总量替代方案不实 | 1 HIGH | Q04 (HIGH) | 总量控制唯一经验 |

**Reference 卡贡献**: 2条卡共3次HIGH命中

### Pending 卡 (3条) — 有限贡献

| 经验卡 | 命中次数 | 命中题目 (relevance) | 说明 |
|--------|---------|---------------------|------|
| EXP_05 废活性炭产生量漏算 | 3 MEDIUM | Q09 (MEDIUM), Q12 (MEDIUM), Q17 (MEDIUM) | pending，仅辅助提示+1分 |
| EXP_07 注塑VOCs源强被低估 | 1 LOW→丢弃 | Q16 硬过滤 | 行业不匹配(注塑≠涂布)被正确丢弃 |
| EXP_08 冷却水排放路径不清 | 1 MEDIUM | Q14 (MEDIUM) | pending，仅辅助提示+1分 |

**Pending 卡贡献**: 2条产生4次MEDIUM命中(+1×4=+4分)，1条被正确丢弃

---

## 经验卡命中明细 (18题)

| 题目 | 预期经验 | 实际命中 | relevance | 评分影响 |
|------|---------|---------|-----------|---------|
| Q01 胶水VOCs超限值 | EXP_01 HIGH | EXP_01 HIGH | ✅ | +2 |
| Q02 活性炭更换周期 | EXP_02 HIGH | EXP_02 HIGH | ✅ | +2 |
| Q03 收集效率 | EXP_03 HIGH | EXP_03 HIGH | ✅ | +2 |
| Q04 总量替代 | EXP_06 HIGH | EXP_06 HIGH | ✅ | +2 |
| Q05 多源收集 | EXP_03+EXP_04 HIGH | EXP_03+EXP_04 HIGH | ✅ | +2 |
| Q06 安全设施 (negative) | 无 | 无 | ✅ 零误报 | 0 |
| Q07 标准适用层级 | 无 | 无 | ✅ | 0 |
| Q08 VOCs物料储存 | 无 | 无 | ✅ | 0 |
| Q09 危废识别 | EXP_05 MEDIUM | EXP_05 MEDIUM | ✅ pending仅提示 | +1 |
| Q10 风量核算 | 无 | 无 (EXP_01/06/08硬过滤) | ✅ relevance拦截 | 0 |
| Q11 过滤风速 | 无 | 无 | ✅ | 0 |
| Q12 废活性炭量 | EXP_05 MEDIUM | EXP_05 MEDIUM | ✅ pending仅提示 | +1 |
| Q13 复合工艺矛盾 | EXP_04 HIGH | EXP_04 HIGH | ✅ | +2 |
| Q14 冷却水隐性排放 | EXP_08 MEDIUM | EXP_08 MEDIUM | ✅ pending仅提示 | +1 |
| Q15 环境风险 | 无 | 无 | ✅ | 0 |
| Q16 VOCs全链路 | EXP_01+EXP_03 HIGH | EXP_01+EXP_03 HIGH | ✅ | +2 |
| Q17 危废×原辅料 | EXP_05 MEDIUM | EXP_05 MEDIUM | ✅ pending仅提示 | +1 |
| Q18 监测×排气筒 | 无 | 无 | ✅ | 0 |

**全部18题预期与实际命中100%一致** ✓

---

## Relevance 过滤成功案例

### 案例1: Q10 风量核算 — 硬过滤拦截

Q10 问题类型为 `standard_calculation`，涉及公式 Q=(10x²+F)Vx：

| 经验卡 | 过滤结果 | 原因 |
|--------|---------|------|
| EXP_01 | ❌ 丢弃 | not_applicable_task_types 含 `standard_calculation` |
| EXP_06 | ❌ 丢弃 | not_applicable_task_types 含 `standard_calculation` |
| EXP_08 | ❌ 丢弃 | not_applicable_task_types 含 `standard_calculation` |

**结论**: 3张经验卡因不适用于 standard_calculation 类型被正确硬过滤。v0.5 中可能出现的"胶水VOCs经验用于风量公式"的低关联误召回已被根除。

### 案例2: Q16 VOCs全链路 — 行业错配硬过滤

Q16 为涂布工序 VOCs 全链路核验 (cross_check)：

| 经验卡 | 过滤结果 | 原因 |
|--------|---------|------|
| EXP_07 注塑VOCs源强被低估 | ❌ 丢弃 | 行业不匹配 — 注塑工序经验不适用于涂布工序，且 not_modules 含"设备产能" |

**结论**: EXP_07 因"注塑工序"与"涂布工序"行业错配被硬过滤，正确丢弃。避免了跨行业经验误用。

### 案例3: Q06 negative_control — 零误报

Q06 安全设施审核 — 所有 EXP_01-08 均不涉及活性炭安全设施领域：
- 无经验卡被命中
- C组正确标注"未命中适用经验卡"
- **零误报验证通过**

---

## 与 v0.5 对比

| 维度 | v0.5 | v0.6a | 改善 |
|------|------|-------|------|
| 经验卡数量 | 20条 candidate | 8条 active (relevance过滤) | 质量>数量 |
| 误召回 (retrieval_mismatch) | Q03式低关联误召回存在 | ✅ 已根除 | relevance硬过滤 |
| pending卡使用 | 未区分 | MEDIUM分级，仅+1分 | 不将pending当strong basis |
| negative_control | 无 | Q06零误报验证 | ✅ 新增验证 |
| 覆盖率 | 2/8题无经验(25%) | 7/18题无经验(39%，因总题目增多) | 比例变化 |
