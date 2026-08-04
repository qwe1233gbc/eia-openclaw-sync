from build_gpt_scoring_packets import build


def test_packet_contains_reference_and_limited_taxonomy():
    packet = build([{
        "question_id": "PL001_Emission_水污",
        "blinded_output_id": "BO-test",
        "model_answer": {"judgement": "无误"},
    }])[0]
    assert packet["reference_answer"]
    assert packet["reference_basis"]
    assert set(packet["question_taxonomy_for_rubric"]) == {
        "audit_domain",
        "cognitive_level",
        "reasoning_type",
        "primary_functional_capability",
    }
