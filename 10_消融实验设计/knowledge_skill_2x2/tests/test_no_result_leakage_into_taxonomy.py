from pipeline_core import TAXONOMY_JSONL, read_jsonl


def test_taxonomy_has_no_experiment_results():
    forbidden = {"group", "model_answer", "model_score", "rag_enabled", "workflow_enabled"}
    for row in read_jsonl(TAXONOMY_JSONL):
        assert forbidden.isdisjoint(row)
