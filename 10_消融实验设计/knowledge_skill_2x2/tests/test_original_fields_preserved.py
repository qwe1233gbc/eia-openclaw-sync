from conftest import governance_rows, source_payload
from governance_core import ORIGINAL_FIELDS

def test_original_fields_preserved():
    source = source_payload()["records"]
    governed = governance_rows()
    assert len(source) == len(governed) == 210
    for before, after in zip(source, governed):
        for field in ORIGINAL_FIELDS:
            left = "" if before.get(field) is None else str(before.get(field)).lower()
            right = "" if after.get(field) is None else str(after.get(field)).lower()
            assert left == right
