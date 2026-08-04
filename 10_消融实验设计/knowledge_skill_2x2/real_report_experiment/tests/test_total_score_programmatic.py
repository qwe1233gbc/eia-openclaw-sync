from .helpers import programmatic_total


def test_total_score_is_programmatic_sum():
    score = {
        "judgement_accuracy": 30,
        "report_evidence": 20,
        "basis_accuracy_applicability": 15,
        "analysis_revision_completeness": 10,
        "total_score": 99,
    }
    assert programmatic_total(score) == 75
