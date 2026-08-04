from __future__ import annotations
import csv, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SKILLS=ROOT/'09_环评审核技能库'
RAG=ROOT/'03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl'
OUT=SKILLS/'quality/rag_skill_overlap_runtime_report.json'
fixed_limit=re.compile(r"\b\d+(?:\.\d+)?\s*(?:mg/m3|mg/m³|mg/L|dB\(A\)|dB|kg/h)\b", re.I)
standard=re.compile(r"(?:GB(?:/T)?|DB44/?|HJ)\s*\d+", re.I)
fixed_conclusion=re.compile(r"(?:必须|一律|固定|一定).{0,60}(?:执行|适用|限值|标准)")
project=re.compile(r"\bPL\d{3}\b|人工金标|人工答案|本题正确|本题无误")
skill_hits=[]
for p in sorted(SKILLS.glob('[01][0-9]_*/SKILL.md')):
    text=p.read_text(encoding='utf-8')
    for no,line in enumerate(text.splitlines(),1):
        if fixed_limit.search(line): skill_hits.append({'file':str(p.relative_to(ROOT)),'line':no,'type':'fixed_limit_in_skill'})
        if standard.search(line) and fixed_conclusion.search(line): skill_hits.append({'file':str(p.relative_to(ROOT)),'line':no,'type':'fixed_standard_applicability'})
        if project.search(line): skill_hits.append({'file':str(p.relative_to(ROOT)),'line':no,'type':'project_specific_leakage'})
rag_rules={'check_logic':r'\bcheck_logic\b','required_evidence':r'\brequired_evidence\b','审核顺序':r'审核顺序','输出模板':r'输出模板|output_example','人工答案':r'人工答案|人工金标'}
rag_hits=[]
for no,line in enumerate(RAG.read_text(encoding='utf-8').splitlines(),1):
    row=json.loads(line); content=str(row.get('content',''))
    for name,pat in rag_rules.items():
        if re.search(pat,content,re.I): rag_hits.append({'parent_id':row.get('parent_id'),'line':no,'type':name})
result={'scope':'01-15 skill bodies and formal RAG content only','skill_hits':skill_hits,'rag_hits':rag_hits,'pass':not skill_hits and not rag_hits,'note':'standard numbers used only as query labels are allowed; related_skill_ids metadata is excluded'}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2)); sys.exit(1 if not result['pass'] else 0)
