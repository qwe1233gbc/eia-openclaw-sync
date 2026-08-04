from .helpers import ROOT, validate_manifest


def test_formal_manifest_has_no_nonfrozen_included_items():
    assert validate_manifest(ROOT / "manifests/formal_manifest.csv") == []


def test_dry_run_candidates_are_explicitly_not_for_analysis():
    import csv
    with (ROOT / "manifests/pilot_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert 2 <= len(rows) <= 4
    assert all(row["not_for_analysis"] == "true" for row in rows)


def test_formal_trend_matrix_is_blocked_below_18_frozen_items():
    import pytest
    from .helpers import build_run_matrix
    with pytest.raises(SystemExit, match="requires at least 18"):
        build_run_matrix("formal")
