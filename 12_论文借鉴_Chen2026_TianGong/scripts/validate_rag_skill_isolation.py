from __future__ import annotations
import csv, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
errors=[]
rag_files=[ROOT/'03_指南解析_明文标准库/formal_rag_chunks/parent_chunks.jsonl',ROOT/'03_指南解析_明文标准库/formal_rag_chunks/child_chunks.jsonl']
rag_rules={'skill_id':r'\bskill_id\b','check_logic':r'\bcheck_logic\b','required_evidence':r'\brequired_evidence\b','审核步骤':r'审核步骤|审核顺序','输出模板':r'输出模板|output_example','人工答案':r'人工答案|人工金标|润色后答案'}
for path in rag_files:
    for no,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        row=json.loads(line); content=str(row.get('content',''))
        for name,pat in rag_rules.items():
            if re.search(pat,content,re.I): errors.append({'scope':'rag_content','file':path.name,'line':no,'type':name})
snap=ROOT/'10_消融实验设计/03_Skill冻结快照/skill_snapshots_v2.jsonl'
limit=re.compile(r'\b\d+(?:\.\d+)?\s*(?:mg/m3|mg/m³|mg/L|dB\(A\)|dB|kg/h)\b',re.I)
for no,line in enumerate(snap.read_text(encoding='utf-8').splitlines(),1):
    row=json.loads(line); content=row.get('content','')
    if limit.search(content): errors.append({'scope':'skill_snapshot','skill_id':row.get('skill_id'),'type':'fixed_limit'})
    if re.search(r'\bPL\d{3}\b|人工金标|人工答案|本题正确|本题无误',content): errors.append({'scope':'skill_snapshot','skill_id':row.get('skill_id'),'type':'project_or_gold'})
for p in (ROOT/'10_消融实验设计/05_Prompt模板').glob('*'):
    if p.is_file() and re.search(r'人工金标|人工答案|本题正确|本题无误',p.read_text(encoding='utf-8')): errors.append({'scope':'prompt','file':p.name,'type':'gold'})
matrix=list(csv.DictReader((ROOT/'10_消融实验设计/06_运行矩阵/run_matrix_v2.csv').open(encoding='utf-8-sig')))
for row in matrix:
    if row['group'] in ('A','B') and row.get('skill_sha256'): errors.append({'scope':'run_matrix','run_id':row['run_id'],'type':'skill_in_A_B'})
    if row['group'] in ('A','C') and row.get('rag_context_sha256'): errors.append({'scope':'run_matrix','run_id':row['run_id'],'type':'rag_in_A_C'})
print(json.dumps({'scope':'formal RAG content + v2 skill snapshots + prompts + v2 run matrix','errors':errors,'pass':not errors,'metadata_exclusions':['related_skill_ids','question_id routing metadata']},ensure_ascii=False,indent=2)); sys.exit(1 if errors else 0)
