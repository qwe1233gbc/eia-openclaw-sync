from validate_gold_freeze import validation_errors

def base():
    return {
        "gold_review_status": "已冻结",
        "normalized_judgement_final": "无误",
        "item_quality_status": "有效",
        "evidence_sufficiency": "充分",
        "basis_verification_status": "已核验",
        "taxonomy_review_status": "人工确认",
        "taxonomy_override_reason": "",
        "auto_flag_reason": "",
        "reviewer_1": "审核员",
        "gold_version": "gold_v1.0",
    }

def test_gold_freeze_gate():
    assert validation_errors(base()) == []
    for field, bad in [
        ("normalized_judgement_final", ""), ("item_quality_status", "字段错位"),
        ("evidence_sufficiency", "不足"), ("basis_verification_status", "未核验"),
        ("taxonomy_review_status", "自动默认"), ("reviewer_1", ""), ("gold_version", ""),
    ]:
        row = base(); row[field] = bad
        assert validation_errors(row), field
