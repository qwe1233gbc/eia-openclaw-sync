from conftest import governance_rows

def test_review_queue_separation():
    rows = [r for r in governance_rows() if r["是否需要人工复核"] == "是"]
    assert len(rows) == 135
    assert all(r["review_queue_type"] in {"A_仅待终审", "B_证据不足", "C_题目或材料问题"} for r in rows)
    ids = [r["question_id"] for r in rows]
    assert len(ids) == len(set(ids))
