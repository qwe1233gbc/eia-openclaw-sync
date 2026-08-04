from .helpers import ROOT, read_jsonl


def test_blinded_packets_do_not_reveal_group_or_factors():
    for row in read_jsonl(ROOT / "runs/dry_run_v1/blinded_outputs.jsonl"):
        blob = __import__("json").dumps(row, ensure_ascii=False)
        assert '"group"' not in blob
        assert "rag_enabled" not in blob
        assert "workflow_enabled" not in blob
        assert "run_id" not in blob
