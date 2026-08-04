import csv
from conftest import ROOT

def test_pilot_selection_no_model_score_leakage():
    for name in ("pilot_option_A_keep_current.csv", "pilot_option_B_balanced.csv"):
        path = ROOT / "gold_governance/pilot" / name
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
            headers = f.seek(0) or []
        assert len(rows) == 18
        forbidden = {"score", "model_score", "a_score", "b_score", "c_score", "d_score"}
        assert not forbidden.intersection({k.lower() for k in rows[0]})
        assert all(r["selection_status"] == "候选_未冻结" for r in rows)
