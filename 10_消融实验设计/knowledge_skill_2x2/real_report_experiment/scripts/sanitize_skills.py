from core import sanitize_skills

rows = sanitize_skills()
print({"procedure_only_skills": len(rows)})
