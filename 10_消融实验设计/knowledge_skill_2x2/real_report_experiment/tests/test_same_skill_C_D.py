from .helpers import ROOT, group_hashes, read_csv


def test_c_and_d_read_identical_procedure_skill():
    for row in read_csv(ROOT / "manifests/pilot_manifest.csv"):
        hashes = group_hashes(row["question_id"])
        assert hashes["C"]["skill_hash"] == hashes["D"]["skill_hash"]
