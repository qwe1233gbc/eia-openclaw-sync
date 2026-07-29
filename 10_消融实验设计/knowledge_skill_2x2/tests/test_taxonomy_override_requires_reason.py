from validate_gold_freeze import validation_errors

def test_taxonomy_override_requires_reason():
    row = {
        "gold_review_status": "已冻结", "normalized_judgement_final": "无误",
        "item_quality_status": "有效", "evidence_sufficiency": "充分",
        "basis_verification_status": "已核验", "taxonomy_review_status": "人工覆盖",
        "taxonomy_override_reason": "", "auto_flag_reason": "", "reviewer_1": "A",
        "gold_version": "gold_v1.0",
    }
    assert "分类覆盖缺少原因" in validation_errors(row)
    row["taxonomy_override_reason"] = "报告证据支持调整"
    assert validation_errors(row) == []
