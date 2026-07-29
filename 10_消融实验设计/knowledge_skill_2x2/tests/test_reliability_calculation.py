from pipeline_core import cohen_kappa, fleiss_kappa


def test_perfect_reliability():
    assert cohen_kappa([1, 2, 3], [1, 2, 3]) == 1
    assert fleiss_kappa([[1, 1, 1], [2, 2, 2], [3, 3, 3]]) == 1
