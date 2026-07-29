from core import validate_rag_no_leakage

errors = validate_rag_no_leakage()
print({"leakage_chunks": errors})
raise SystemExit(1 if errors else 0)
