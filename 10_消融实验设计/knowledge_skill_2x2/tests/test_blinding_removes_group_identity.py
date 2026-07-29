from blind_outputs import FORBIDDEN, blind


def test_blinding_removes_identity_fields():
    records = [{
        "question_id": "Q1",
        "group": "D",
        "run_id": "D-run-1",
        "rag_enabled": True,
        "workflow_enabled": True,
        "model_answer": {"judgement": "无误"},
    }]
    blinded, key = blind(records)
    assert FORBIDDEN.isdisjoint(blinded[0])
    assert blinded[0]["blinded_output_id"] in key["mapping"]
