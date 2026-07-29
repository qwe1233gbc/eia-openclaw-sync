from conftest import governance_rows

def test_blank_judgement_not_auto_filled():
    rows = [r for r in governance_rows() if r["raw_manual_judgement"] == ""]
    assert len(rows) == 26
    assert all(r["normalized_judgement_candidate"] == "待判断" for r in rows)
    assert all(r["normalized_judgement_final"] == "" for r in rows)
    assert all(r["gold_review_status"] == "未复核" for r in rows)
