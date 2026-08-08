from .helpers import interaction


def test_interaction_is_d_minus_c_minus_b_plus_a():
    assert interaction(10, 13, 14, 20) == 3
