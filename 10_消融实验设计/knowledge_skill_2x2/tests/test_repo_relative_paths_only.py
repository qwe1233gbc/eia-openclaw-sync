import re
from conftest import ROOT

def test_repo_relative_paths_only():
    suffixes = {".md", ".csv", ".json", ".jsonl"}
    for path in (ROOT / "gold_governance").rglob("*"):
        if path.is_file() and path.suffix.lower() in suffixes:
            text = path.read_text(encoding="utf-8-sig")
            assert not re.search(r"(?i)(?:^|[\"'`\\s])[A-Z]:[\\\\/]", text), path
