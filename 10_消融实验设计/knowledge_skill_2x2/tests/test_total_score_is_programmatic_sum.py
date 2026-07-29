from pipeline_core import programmatic_total


def test_programmatic_total():
    value = {
        "universal_scores": {
            "judgement_correctness": 20,
            "report_evidence_quality": 15,
            "key_issue_completeness": 15,
            "logical_consistency_and_uncertainty": 10,
        },
        "functional_scores": {"a": 20, "b": 20},
    }
    assert programmatic_total(value) == 100
