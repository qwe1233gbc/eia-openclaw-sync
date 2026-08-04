from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [ROOT / "03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl", ROOT / "03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl"]
RULES = {"skill_id":r"\bskill_id\b", "check_logic":r"\bcheck_logic\b", "required_evidence":r"\brequired_evidence\b", "审核步骤":r"审核步骤", "人工答案":r"人工答案", "gold":r"\bgold(?:en)?_?answer\b", "润色后答案":r"润色后答案"}
hits=[]
for path in FILES:
    for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        row=json.loads(line); content=str(row.get("content", ""))
        for name, pat in RULES.items():
            if re.search(pat, content, re.I): hits.append({"file":path.name,"line":no,"id":row.get("parent_id") or row.get("child_id"),"rule":name})
print(json.dumps({"scope":"content field only; related_skill_ids and routing metadata excluded","files":[p.name for p in FILES],"hits":hits,"pass":not hits}, ensure_ascii=False, indent=2))
sys.exit(1 if hits else 0)
