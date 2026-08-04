from core import ROOT, skill_purity_violations

errors = skill_purity_violations()
(ROOT / "reports" / "skill_purity_report.md").write_text(
    "# Skill去知识化检查\n\n"
    + ("通过：未发现标准号、明确限值、项目编号或答案式表达。\n" if not errors else f"失败：{errors}\n"),
    encoding="utf-8",
)
print({"violations": errors})
raise SystemExit(1 if errors else 0)
