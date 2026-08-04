from core import make_manifests

pilot, formal = make_manifests()
print({"pilot": len(pilot), "formal_included": sum(r["include"] == "true" for r in formal)})
