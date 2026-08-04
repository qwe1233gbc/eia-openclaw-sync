from .helpers import ROOT, group_hashes, read_csv


def test_output_schema_hash_is_same_for_all_groups():
    question_id = read_csv(ROOT / "manifests/pilot_manifest.csv")[0]["question_id"]
    hashes = group_hashes(question_id)
    assert len({item["output_schema_hash"] for item in hashes.values()}) == 1
