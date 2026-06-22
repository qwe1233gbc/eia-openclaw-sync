# 样本筛选逻辑 — 行业代码优先 + 工艺验证 + 文件链完整性

> **替代文件**：`sample_filter_keywords.md`（旧关键词方案）
> **配套文件**：`target_industry_code_hierarchy.md`（行业代码层级定义）
>
> **核心变更**：旧方案 Tier1→Tier3 三级关键词 → 新方案 Code→Process→Chain 三级结构化筛选

---

## 筛选流程图

```
输入：一个项目（含行业代码 + 报告文本）
              │
              ▼
   ┌──────────────────────┐
   │ 一级：行业代码匹配      │
   │ 查 GB/T 4754 四位数代码 │
   └──────┬───────────────┘
          │
     ┌────┴────┐
     │  匹配?   │
     └────┬────┘
          │
    ┌─────┼─────┐
    │     │     │
    ▼     ▼     ▼
  Core  Edge  Excluded
  (C292 (C2641/   (C291/
   1-9) C2642/   橡胶类)
        C2319等)
    │     │     │
    │     │     └──→ 终止：不在目标范围
    │     │
    │     └──→ 需额外验证进入条件
    │
    ▼
   ┌──────────────────────┐
   │ 二级：工艺特征验证      │
   │ 必选项 + 加分项         │
   └──────┬───────────────┘
          │
     ┌────┴────┐
     │  通过?   │
     └────┬────┘
          │
    ┌─────┼─────┐
    │           │
    ▼           ▼
   是          否
    │           │
    │           └──→ 降级：仅作对照样本
    │                (approval_alignment)
    ▼
   ┌──────────────────────┐
   │ 三级：文件链完整性检查   │
   │ 受理公告/终稿/批复/修改意见│
   └──────┬───────────────┘
          │
     ┌────┴────┐
     │  分级    │
     └────┬────┘
          │
    ┌─────┼─────────┐
    ▼     ▼         ▼
   A级   B级       C级
   (全链) (部分链) (仅受理)
    │     │         │
    ▼     ▼         ▼
  mvp_   experience  reference
  bench  _source     _only
```

---

## 一级：行业代码匹配（Code Match）

### 匹配规则

```
IF project.industry_code IN CORE_CODES:
    level = "core"
ELIF project.industry_code IN EDGE_CODES:
    level = "edge"
    # Edge 行业必须在二级验证中同时满足至少一项必选工艺特征
ELIF project.industry_code IN EXCLUDED_CODES:
    level = "excluded"
    STOP
ELSE:
    level = "out_of_scope"
    STOP
```

### 代码集定义

```python
# 核心匹配：C292 塑料制品业全部 9 个子类
CORE_CODES = {
    "C2921", "C2922", "C2923", "C2924", "C2925",
    "C2926", "C2927", "C2928", "C2929"
}

# 边缘适用：VOCs/胶粘剂交叉行业
EDGE_CODES = {
    "C2641",  # 涂料制造
    "C2642",  # 油墨及类似产品制造
    "C2646",  # 密封用填料及类似品制造
    "C2319",  # 包装装潢及其他印刷
    "C2651",  # 初级形态塑料及合成树脂制造
    "C2652",  # 合成橡胶制造
}

# 排除：C29门类但不适用
EXCLUDED_CODES = {
    "C2911", "C2912", "C2913", "C2914",
    "C2915", "C2916", "C2919",  # 橡胶制品业各子类
}
```

### 行业代码获取方式

项目环评报告的第一页/封面页通常标注国民经济行业代码。优先从以下位置提取：
1. 报告封面/首页的"国民经济行业类别"字段
2. 建设项目建设内容表中的"行业类别及代码"
3. 若报告未标注，在顺德审批数据库 `hp_approve_info` 表的 `industry_code` 字段中查

---

## 二级：工艺特征验证（Process Verification）

### 必选项（MUST satisfy ≥1）

以下 5 项必须至少命中一项，从报告文本中**逐字段**检索而非全文关键词模糊命中：

| # | 工艺特征 | 检索位置 | 检索词 | 判据 |
|---|---------|---------|--------|------|
| P1 | 涉胶水/胶粘剂 | 原辅材料表 | 胶粘剂/胶水/粘合剂/热熔胶/水性胶/PU胶 | 表中至少一行含上述词且年用量>0 |
| P2 | 涉涂布/涂装 | 工艺流程文字描述 | 涂布/涂装/辊涂/喷涂/浸涂/淋涂 | 流程描述中含上述动词 |
| P3 | 涉复合/贴合 | 工艺流程文字描述 | 复合/贴合/干复/湿复/挤复 | 流程描述中含上述动词 |
| P4 | 涉印刷 | 工艺流程文字描述 | 印刷/凹印/柔印/丝印/胶印/印版 | 流程描述中含上述动词 |
| P5 | 涉熟化/固化/烘干 | 工艺流程文字描述 | 熟化/固化/烘干/烘箱/烘道/加热段 | 流程描述中含上述词 |

### 加分项（BONUS，不计入必须条件）

| # | 特征 | 检索位置 | 检索词 |
|---|------|---------|--------|
| B1 | 涉VOCs有组织排放 | 废气治理措施章节 | VOCs/非甲烷总烃 + 集气罩/收集/排气筒 |
| B2 | 涉活性炭吸附 | 废气治理措施章节 | 活性炭/颗粒炭/蜂窝炭/吸附 |
| B3 | 涉废活性炭 | 固废/危废章节 | 废活性炭/HW49 |

### 验证结果判定

```
IF MUST_COUNT >= 1:
    IF level == "core":
        result = "full_match"      # → 进入三级文件链检查
    IF level == "edge":
        result = "edge_match"      # → 进入三级，标注"边缘适用"
ELSE:
    IF level == "core":
        result = "process_mismatch"  # → 降级为对照样本
    IF level == "edge":
        result = "out_of_scope"      # → 终止
```

---

## 三级：文件链完整性检查（Chain Completeness）

### 文件清单

| 文件类型 | 字段 | 典型文件名模式 |
|---------|------|--------------|
| 受理公告报告 | acceptance_announcement_report | `*受理公告*` / `*受理通知书*` |
| 终稿/拟审批稿 | final_report | `*报批稿*` / `*拟审批稿*` / `*终稿*` |
| 批复 | approval | `*批复*` / `*审批意见*` |
| 修改意见/补正通知 | review_comment | `*修改意见*` / `*补正通知*` / `*审查意见*` |

### 分级规则

```python
def classify_sample_grade(has_acceptance, has_final, has_approval, has_review):
    chain_score = sum([has_acceptance, has_final, has_approval])
    
    if chain_score >= 3 and has_review:
        return "A", "mvp_benchmark"  # 完整四件套：可用于金标Benchmark
    elif chain_score >= 2:
        return "B", "experience_source"  # 两件以上：可用于经验提取
    elif has_acceptance:
        return "C", "reference_only"  # 仅有受理公告：仅作参考
    else:
        return "D", "incomplete"  # 无核心文件：不可用
```

### 特殊文件类型处理

| 文件标记 | 含义 | 处理方式 |
|---------|------|---------|
| 受理公告报告 (acceptance_announcement_report) | 建设单位提交环评后被受理的公告 | 确认项目进入审批流程 |
| 拟审批稿 (pre_final_report) | 通过技术审查后拟批准的版本 | 可作为"终稿"的替代 |
| 修改意见 (review_comment) | 技术审查中指出的问题 | **经验库提取的核心来源** |
| 补正通知 (supplement_notice) | 要求补充材料的通知 | 等价于修改意见，可合并处理 |
| 专家意见 (expert_opinion) | 专家评审会意见 | 可选，有则加分 |

---

## 四、输出：候选项目清单字段规范

每个候选项目输出以下结构化字段（替换旧 CSV 的自由文本备注）：

```csv
sample_id,project_name,industry_code,industry_code_level,
process_feature_p1_glue,p2_coating,p3_composite,p4_printing,p5_curing,
bonus_b1_vocs,b2_carbon,b3_waste_carbon,
has_acceptance,has_final,has_approval,has_review,
sample_grade,recommended_use,notes
```

| 字段 | 类型 | 说明 |
|------|------|------|
| industry_code_level | enum | `core` / `edge` / `excluded` |
| process_feature_p1-p5 | bool | 5 项工艺特征逐项判定的 0/1 |
| bonus_b1-b3 | bool | 3 项加分特征逐项判定的 0/1 |
| sample_grade | enum | `A` / `B` / `C` / `D` |
| recommended_use | enum | `mvp_benchmark` / `experience_source` / `reference_only` / `approval_alignment` / `excluded` |

---

## 五、实现说明

### 5.1 行业代码映射函数

```python
def match_industry_level(code: str) -> tuple[str, str]:
    """返回 (level, label)"""
    code_4digit = code[:5] if len(code) >= 5 else code
    
    if code_4digit in CORE_CODES:
        return "core", "塑料制品业-核心"
    elif code_4digit in EDGE_CODES:
        return "edge", "边缘交叉行业"
    elif code_4digit in EXCLUDED_CODES:
        return "excluded", "C29橡胶类-排除"
    else:
        # 模糊匹配: 只要前4位是 C292 就纳入核心
        if code.startswith("C292") and len(code) >= 4:
            return "core", "塑料制品业-模糊匹配"
        return "out_of_scope", "不在目标范围"
```

### 5.2 工艺特征提取函数

```python
# 不再用全文关键词模糊匹配
# 改为：逐章节/逐表定位检索
def verify_process_feature(report_sections: dict, feature: str) -> bool:
    """在指定章节中检索工艺特征"""
    section_targets = {
        "p1_glue": ["原辅材料表", "主要原辅材料"],
        "p2_coating": ["工艺流程", "生产工艺"],
        "p3_composite": ["工艺流程", "生产工艺"],
        "p4_printing": ["工艺流程", "生产工艺"],
        "p5_curing": ["工艺流程", "生产工艺"],
    }
    # 仅在目标章节中检索，避免全文误匹配
    ...
```

### 5.3 旧关键词与新代码体系的对照

旧方案关键词的作用被重新分配：
- "塑料薄膜/塑料包装/胶水/复合/熟化" → 工艺特征 P1-P5
- "VOCs/非甲烷总烃/活性炭/收集效率/涂布/印刷" → 加分项 B1-B3 + 工艺特征 P2/P4
- "受理公告/批复/修改意见/补正通知/终稿" → 三级文件链完整性检查
