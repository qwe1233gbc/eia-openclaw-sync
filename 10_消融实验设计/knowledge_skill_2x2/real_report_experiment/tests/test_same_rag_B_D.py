from .helpers import ROOT, group_hashes, read_csv


def test_b_and_d_read_identical_frozen_rag():
    for row in read_csv(ROOT / "manifests/pilot_manifest.csv"):
        hashes = group_hashes(row["question_id"])
        assert hashes["B"]["rag_context_hash"] == hashes["D"]["rag_context_hash"]
