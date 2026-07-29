from conftest import governance_rows

def test_112_flagged_as_field_misalignment():
    rows = [r for r in governance_rows() if r["raw_manual_judgement"] == "112"]
    assert len(rows) == 3
    assert all(r["item_quality_status"] == "字段错位" for r in rows)
    assert all(r["normalized_judgement_candidate"] == "待判断" for r in rows)
    assert all(r["normalized_judgement_final"] == "" for r in rows)
