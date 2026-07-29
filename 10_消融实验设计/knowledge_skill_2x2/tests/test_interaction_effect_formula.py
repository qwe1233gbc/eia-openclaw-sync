from pipeline_core import effect_components


def test_interaction_formula():
    result = effect_components(50, 60, 65, 80)
    assert result["K_main_effect"] == 12.5
    assert result["S_main_effect"] == 17.5
    assert result["interaction"] == 5
