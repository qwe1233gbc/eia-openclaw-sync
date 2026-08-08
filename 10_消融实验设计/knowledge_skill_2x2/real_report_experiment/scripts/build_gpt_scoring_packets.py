from core import build_scoring_packets

rows = build_scoring_packets()
print({"scoring_packets": len(rows), "contains_group_identity": False})
