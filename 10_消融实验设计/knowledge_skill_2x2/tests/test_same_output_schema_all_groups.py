from pipeline_core import ROOT, sha256


def test_one_frozen_schema_is_used_for_all_groups():
    schema = ROOT / "schemas" / "audit_output_v1.schema.json"
    digest = sha256(schema)
    assert len(digest) == 64
    assert not any((ROOT / "schemas").glob("audit_output_[ABCD]*.schema.json"))
