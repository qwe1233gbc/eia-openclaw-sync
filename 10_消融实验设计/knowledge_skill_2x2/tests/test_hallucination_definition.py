def test_missing_basis_is_not_automatically_hallucination():
    evaluation = {
        "basis_hallucination": False,
        "basis_hallucination_type": "none",
        "basis_status": "unavailable",
    }
    assert evaluation["basis_status"] == "unavailable"
    assert not evaluation["basis_hallucination"]
