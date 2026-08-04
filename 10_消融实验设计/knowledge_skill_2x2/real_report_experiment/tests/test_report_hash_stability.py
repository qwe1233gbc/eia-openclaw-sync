import json
from .helpers import ROOT, sha_text


def test_parsed_section_hashes_are_reproducible():
    for path in (ROOT / "data/report_documents").glob("*.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["sections"]
        assert all(section["content_sha256"] == sha_text(section["text"]) for section in doc["sections"])
