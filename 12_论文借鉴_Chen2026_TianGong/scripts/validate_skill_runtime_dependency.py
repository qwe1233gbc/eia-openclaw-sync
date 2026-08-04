from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SKILLS=ROOT/'09_环评审核技能库'
required=['rag_evidence','basis_status','证据不足与降级规则','不得根据模型记忆','report_evidence_used','rag_basis_used','risk_hints','manual_review_needed']
errors=[]
for p in sorted(SKILLS.glob('[01][0-9]_*/SKILL.md')):
    sid=p.parent.name.split('_',1)[0]
    if sid=='99' or int(sid)>15: continue
    text=p.read_text(encoding='utf-8')
    for token in required:
        if token not in text: errors.append({'skill_id':sid,'missing':token})
    if re.search(r'\bPL\d{3}\b|人工金标|人工答案|本题正确|本题无误',text): errors.append({'skill_id':sid,'forbidden':'project_or_gold'})
print(json.dumps({'skills_checked':15,'errors':errors,'pass':not errors},ensure_ascii=False,indent=2)); sys.exit(1 if errors else 0)
