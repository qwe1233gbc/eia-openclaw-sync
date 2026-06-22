"""
样本筛选逻辑 — 行业代码优先 + 工艺验证 + 文件链完整性
替代旧 sample_filter_keywords.md 中的三维关键词方案
"""
import json
from pathlib import Path
from typing import Optional

# ============================================================
# 一级：行业代码集（基于 GB/T 4754-2017）
# ============================================================

CORE_CODES: set[str] = {
    "C2921", "C2922", "C2923", "C2924", "C2925",
    "C2926", "C2927", "C2928", "C2929",
}

EDGE_CODES: set[str] = {
    "C2641",   # 涂料制造
    "C2642",   # 油墨及类似产品制造
    "C2646",   # 密封用填料及类似品制造
    "C2319",   # 包装装潢及其他印刷
    "C2651",   # 初级形态塑料及合成树脂制造
    "C2652",   # 合成橡胶制造
}

EXCLUDED_CODES: set[str] = {
    "C2911", "C2912", "C2913", "C2914",
    "C2915", "C2916", "C2919",
}

# ============================================================
# 二级：工艺特征检索定义
# ============================================================

PROCESS_FEATURES: dict[str, dict] = {
    "p1_glue": {
        "label": "涉胶水/胶粘剂",
        "search_in": ["原辅材料表", "主要原辅材料"],
        "patterns": ["胶粘剂", "胶水", "粘合剂", "热熔胶", "水性胶", "PU胶", "聚氨酯胶"],
        "criterion": "表中至少一行含检索词且年用量>0",
    },
    "p2_coating": {
        "label": "涉涂布/涂装",
        "search_in": ["工艺流程", "生产工艺", "工程分析"],
        "patterns": ["涂布", "涂装", "辊涂", "喷涂", "浸涂", "淋涂"],
        "criterion": "流程描述中含上述动词",
    },
    "p3_composite": {
        "label": "涉复合/贴合",
        "search_in": ["工艺流程", "生产工艺", "工程分析"],
        "patterns": ["复合", "贴合", "干复", "湿复", "挤复", "无溶剂复合"],
        "criterion": "流程描述中含上述动词",
    },
    "p4_printing": {
        "label": "涉印刷",
        "search_in": ["工艺流程", "生产工艺", "工程分析"],
        "patterns": ["印刷", "凹印", "柔印", "丝印", "胶印", "印版", "印品"],
        "criterion": "流程描述中含上述动词",
    },
    "p5_curing": {
        "label": "涉熟化/固化/烘干",
        "search_in": ["工艺流程", "生产工艺", "工程分析"],
        "patterns": ["熟化", "固化", "烘干", "烘箱", "烘道", "加热段", "干燥"],
        "criterion": "流程描述中含上述词",
    },
}

BONUS_FEATURES: dict[str, dict] = {
    "b1_vocs": {
        "label": "涉VOCs有组织排放",
        "search_in": ["废气治理", "污染防治措施", "废气"],
        "patterns": ["VOCs", "非甲烷总烃", "挥发性有机物", "NMHC"],
    },
    "b2_carbon": {
        "label": "涉活性炭吸附",
        "search_in": ["废气治理", "污染防治措施", "废气"],
        "patterns": ["活性炭", "颗粒炭", "蜂窝炭", "纤维炭", "吸附"],
    },
    "b3_waste_carbon": {
        "label": "涉废活性炭",
        "search_in": ["固废", "危废", "固体废物", "危险废物"],
        "patterns": ["废活性炭", "HW49", "900-039-49", "900-041-49"],
    },
}

# ============================================================
# 匹配函数
# ============================================================

def match_industry_code(code: str) -> dict:
    """一级匹配：返回行业代码层级"""
    code = code.strip().upper()
    code_4 = code[:5] if len(code) >= 5 else code

    if code_4 in CORE_CODES:
        return {"level": "core", "label": "塑料制品业-核心", "action": "continue"}
    if code_4 in EDGE_CODES:
        return {"level": "edge", "label": "边缘交叉行业", "action": "continue"}
    if code_4 in EXCLUDED_CODES:
        return {"level": "excluded", "label": "C29橡胶类-排除", "action": "stop"}

    # 模糊匹配: 前4位 C292
    if code.startswith("C292") and len(code) >= 4:
        return {"level": "core", "label": "塑料制品业-模糊匹配(C292*)", "action": "continue"}

    return {"level": "out_of_scope", "label": "不在目标范围", "action": "stop"}


def verify_process_features(sections: dict[str, str]) -> dict:
    """二级匹配：在指定章节中检索工艺特征（非全文关键词模糊匹配）"""
    must_hits: list[str] = []
    bonus_hits: list[str] = []

    for feat_key, feat_def in PROCESS_FEATURES.items():
        search_text = ""
        for section_name in feat_def["search_in"]:
            for actual_name, content in sections.items():
                if section_name in actual_name:
                    search_text += content + " "

        for pattern in feat_def["patterns"]:
            if pattern in search_text:
                must_hits.append(feat_key)
                break

    for feat_key, feat_def in BONUS_FEATURES.items():
        search_text = ""
        for section_name in feat_def["search_in"]:
            for actual_name, content in sections.items():
                if section_name in actual_name:
                    search_text += content + " "

        for pattern in feat_def["patterns"]:
            if pattern in search_text:
                bonus_hits.append(feat_key)
                break

    must_count = len(must_hits)
    bonus_count = len(bonus_hits)

    # 判定
    if must_count >= 1:
        verdict = "process_pass"
    else:
        verdict = "process_fail"

    return {
        "verdict": verdict,
        "must_hits": must_hits,
        "bonus_hits": bonus_hits,
        "must_count": must_count,
        "bonus_count": bonus_count,
    }


def classify_chain_completeness(
    has_acceptance: bool,
    has_final: bool,
    has_approval: bool,
    has_review: bool,
) -> dict:
    """三级：文件链完整性分级"""
    chain_score = sum([has_acceptance, has_final, has_approval])

    if chain_score >= 3 and has_review:
        return {"grade": "A", "use": "mvp_benchmark", "desc": "完整四件套：可用于金标Benchmark"}
    elif chain_score >= 2:
        return {"grade": "B", "use": "experience_source", "desc": "两件以上：可用于经验提取和对照实验"}
    elif has_acceptance:
        return {"grade": "C", "use": "reference_only", "desc": "仅有受理公告：仅作参考"}
    else:
        return {"grade": "D", "use": "incomplete", "desc": "无核心文件：不可用"}


def filter_sample(
    industry_code: str,
    sections: dict[str, str],
    file_flags: dict[str, bool],
) -> dict:
    """综合筛选：行业代码 → 工艺验证 → 文件链，返回完整判定结果"""
    # 一级
    level = match_industry_code(industry_code)
    if level["action"] == "stop":
        return {"status": "rejected", "reason": level["label"], "level": level}

    # 二级
    process = verify_process_features(sections)
    if process["verdict"] == "process_fail":
        if level["level"] == "core":
            return {
                "status": "downgraded",
                "reason": "C292核心行业但工艺特征不匹配→降级为对照样本",
                "level": level,
                "process": process,
                "use": "approval_alignment",
            }
        else:
            return {
                "status": "rejected",
                "reason": "边缘行业且工艺特征不匹配",
                "level": level,
                "process": process,
            }

    # 三级
    chain = classify_chain_completeness(
        has_acceptance=file_flags.get("has_acceptance", False),
        has_final=file_flags.get("has_final", False),
        has_approval=file_flags.get("has_approval", False),
        has_review=file_flags.get("has_review", False),
    )

    return {
        "status": "accepted",
        "level": level,
        "process": process,
        "chain": chain,
        "recommended_use": chain["use"],
    }
