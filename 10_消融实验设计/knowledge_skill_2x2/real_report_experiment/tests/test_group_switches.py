from .helpers import GROUPS


def test_only_the_two_experimental_factors_change():
    assert GROUPS == {
        "A": {"rag_enabled": False, "workflow_enabled": False},
        "B": {"rag_enabled": True, "workflow_enabled": False},
        "C": {"rag_enabled": False, "workflow_enabled": True},
        "D": {"rag_enabled": True, "workflow_enabled": True},
    }
