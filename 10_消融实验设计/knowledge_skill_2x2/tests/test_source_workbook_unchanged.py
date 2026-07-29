import hashlib
import re
from conftest import ROOT, REPO

def test_source_workbook_unchanged():
    report = (ROOT / "gold_governance/reports/source_data_audit.md").read_text(encoding="utf-8")
    expected = re.search(r"SHA-256：`([0-9a-f]{64})`", report).group(1)
    source = REPO / "05_QA测试集/四大类问答对_最终版.xlsx"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
