from conftest import governance_rows

def test_candidate_mapping_does_not_overwrite_final():
    rows = governance_rows()
    assert any(r["normalized_judgement_candidate"] for r in rows)
    assert all(r["normalized_judgement_final"] == "" for r in rows)
    assert all(r["gold_review_status"] == "未复核" for r in rows)
