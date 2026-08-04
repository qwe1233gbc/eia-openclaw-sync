from .helpers import ROOT, read_csv


def test_report_manifest_has_required_fields_and_no_absolute_paths():
    rows = read_csv(ROOT / "data/report_manifest.csv")
    assert len(rows) == 41
    assert all(row["source_available"] == "true" for row in rows)
    required = {
        "project_id", "project_name", "report_file_name", "report_file_type",
        "report_relative_identifier", "report_sha256", "report_version",
        "parse_status", "section_index_status", "source_available", "notes",
    }
    assert required <= set(rows[0])
    assert not any(":\\" in row["report_relative_identifier"] for row in rows)
