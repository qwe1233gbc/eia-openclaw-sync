from core import ROOT, read_csv, validate_group_isolation

pilot = read_csv(ROOT / "manifests" / "pilot_manifest.csv")
errors = validate_group_isolation([r["question_id"] for r in pilot if r["include"] == "true"])
print({"errors": errors})
raise SystemExit(1 if errors else 0)
