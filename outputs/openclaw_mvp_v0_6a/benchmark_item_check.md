# Benchmark 题目核查报告 v0.6a

## 1. 读取情况
- 主实验题：**18 道** (Q01-Q18)
- 备选题：**2 道** (B01-B02，不进入主评分)
- 文件格式：JSONL 全部合法

## 2. 逐题信息

| item_id | question_type | audit_module | negative_control | 预期标准卡 | 预期经验卡 | gold_label_source | difficulty |
|---------|--------------|-------------|------------------|-----------|-----------|-------------------|------------|
| Q01 | guide_explicit | 胶粘剂VOCs含量 | N | STD_07 | EXP_01 | review_comment | medium |
| Q02 | guide_explicit | 活性炭更换周期 | N | STD_18, STD_17 | EXP_02 | review_comment | medium |
| Q03 | case_experience | 收集效率取值 | N | STD_14 | EXP_03 | review_comment | medium |
| Q04 | case_experience | VOCs总量替代 | N | STD_22 | EXP_06 | review_comment | medium |
| Q05 | cross_check | 工艺×VOCs | N | STD_14, STD_10 | EXP_03, EXP_04 | review_comment | medium |
| Q06 | negative_control | 活性炭安全设施 | **Y** | STD_24 | 无 | standard_card | — |
| Q07 | guide_explicit | 标准适用层级 | N | STD_09 | 无 | standard_card | medium |
| Q08 | guide_explicit | VOCs物料储存 | N | STD_27 | 无 | standard_card | easy |
| Q09 | guide_explicit | 危废识别-非活性炭 | N | STD_21 | EXP_05 | review_comment | easy |
| Q10 | standard_calculation | 风量核算 | N | STD_15 | 无 | standard_card | hard |
| Q11 | standard_calculation | 活性炭过滤风速 | N | STD_17 | 无 | standard_card | medium |
| Q12 | standard_calculation | 废活性炭产生量 | N | STD_23 | EXP_05 | standard_card | medium |
| Q13 | case_experience | 复合工艺VOCs | N | STD_05 | EXP_04 | experience_card | medium |
| Q14 | case_experience | 冷却水排放 | N | STD_19 | EXP_08 | experience_card | medium |
| Q15 | case_experience | 环境风险 | N | STD_38 | 无 | standard_card | hard |
| Q16 | cross_check | VOCs源强全链路 | N | STD_11, STD_13, STD_14 | EXP_01, EXP_03 | cross_check_manual | hard |
| Q17 | cross_check | 危废×原辅料 | N | STD_35 | EXP_05 | review_comment | medium |
| Q18 | cross_check | 监测计划×排气筒 | N | STD_25 | 无 | standard_card | medium |

## 3. 类型分布
- guide_explicit: 5题 (Q01, Q02, Q07, Q08, Q09)
- standard_calculation: 4题 (Q10, Q11, Q12, Q06[negative_control])
- case_experience: 5题 (Q03, Q04, Q13, Q14, Q15)
- cross_check: 4题 (Q05, Q16, Q17, Q18)

## 4. 经验卡预期命中（仅C组）
- HIGH: Q01(EXP_01), Q02(EXP_02), Q03(EXP_03), Q04(EXP_06), Q05(EXP_03+04), Q13(EXP_04), Q16(EXP_01+03)
- MEDIUM(pending): Q09(EXP_05), Q12(EXP_05), Q14(EXP_08), Q17(EXP_05)
- 无命中: Q06, Q07, Q08, Q10, Q11, Q15, Q18

## 5. Negative control (Q06)
- 作用：验证C组在无经验卡时是否误用经验或编造类案
- 预期标准卡：STD_24
- 预期经验卡：无
- 不参与C-B经验增量统计

## 6. 备选题
- B01: cross_check / 噪声×声功能区
- B02: guide_explicit / 附图一致性
- 状态：不进入主评分，仅在主实验题无法解析时使用

## 7. manual_check_needed 汇总
全部 18 题均标记 manual_check_needed=true（gold answer 未经过经办人验证）
