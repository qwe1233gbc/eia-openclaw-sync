import csv
from pathlib import Path

from review_no_issue_70 import RESULT_CSV, load_records, select_70


def _results() -> list[dict[str, str]]:
    with Path(RESULT_CSV).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_exactly_70_source_marked_no_review_records_are_selected():
    selected = select_70(load_records())
    assert len(selected) == 70
    assert all(row["是否需要人工复核"] == "否" for row in selected)
    assert all(row["raw_manual_judgement"] in {"正确", "无误"} for row in selected)


def test_codex_review_never_authorizes_final_or_freeze():
    rows = _results()
    assert len(rows) == 70
    assert {row["codex_review_is_final"] for row in rows} == {"False"}
    assert {row["gold_freeze_authorized"] for row in rows} == {"False"}


def test_source_no_review_flag_is_not_automatically_accepted():
    rows = _results()
    assert sum(row["codex_review_status"] == "通过候选" for row in rows) == 10
    assert sum(row["codex_review_status"] != "通过候选" for row in rows) == 60


def test_all_nine_investment_items_recompute_as_pass_candidates():
    rows = [row for row in _results() if row["审核类别"] == "环评投资概算"]
    assert len(rows) == 9
    assert all(row["codex_review_status"] == "通过候选" for row in rows)
    assert all("÷" in row["calculation_detail"] and "报告=" in row["calculation_detail"] for row in rows)


def test_review_export_contains_no_absolute_windows_paths_or_model_scores():
    text = Path(RESULT_CSV).read_text(encoding="utf-8-sig")
    assert "E:\\" not in text
    assert "C:\\" not in text
    assert "model_score" not in text.lower()
    assert "A/B/C/D得分" not in text
