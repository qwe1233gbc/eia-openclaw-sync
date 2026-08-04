from pipeline_core import scientific_direction


def test_direction_rules():
    assert scientific_direction(5, 6, 0) == "additive"
    assert scientific_direction(5, 6, 3) == "synergy"
    assert scientific_direction(5, 6, -3) == "antagonism"
    assert scientific_direction(5, 0, 0) == "knowledge_only"
    assert scientific_direction(0, 5, 0) == "workflow_only"
    assert scientific_direction(0, 0, 0) == "neither"
