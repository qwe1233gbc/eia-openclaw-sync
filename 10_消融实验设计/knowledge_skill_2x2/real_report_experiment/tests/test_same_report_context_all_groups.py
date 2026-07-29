from .helpers import ROOT, group_hashes, read_csv


def test_same_frozen_report_context_for_abcd():
    for row in read_csv(ROOT / "manifests/pilot_manifest.csv"):
        hashes = group_hashes(row["question_id"])
        assert len({item["report_context_hash"] for item in hashes.values()}) == 1
