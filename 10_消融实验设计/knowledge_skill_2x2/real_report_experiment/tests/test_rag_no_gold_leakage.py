from .helpers import validate_rag_no_leakage


def test_rag_corpus_excludes_gold_and_workflow_paths():
    assert validate_rag_no_leakage() == []
