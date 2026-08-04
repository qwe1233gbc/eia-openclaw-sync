from __future__ import annotations
import csv, hashlib, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv"
HASHES = ROOT / "10_消融实验设计/03_Skill冻结快照/skill_hashes_v2.csv"
rows=list(csv.DictReader(MATRIX.open(encoding="utf-8-sig")))
byq=defaultdict(dict)
for r in rows: byq[r["question_id"]][r["group"]]=r
errors=[]
hash_rows=list(csv.DictReader(HASHES.open(encoding="utf-8-sig")))
for row in hash_rows:
    skill_path = ROOT / row["path"]
    # Hash canonical UTF-8 text so checkout-level CRLF/LF conversion does not
    # change a frozen Skill identity.
    actual = hashlib.sha256(skill_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    if actual != row["skill_sha256"]:
        errors.append(f"Skill {row['skill_id']}: v2清单哈希与文件不一致")
for qid, g in byq.items():
    if set(g) != set("ABCD"): errors.append(f"{qid}: 缺少组别") ; continue
    reports={g[x]["report_context_sha256"] for x in "ABCD"}
    if len(reports)!=1 or not next(iter(reports)): errors.append(f"{qid}: A/B/C/D报告哈希不一致或为空")
    if g["B"]["rag_context_sha256"] != g["D"]["rag_context_sha256"] or not g["B"]["rag_context_sha256"]: errors.append(f"{qid}: B/D RAG哈希不一致或为空")
    if g["C"]["skill_sha256"] != g["D"]["skill_sha256"] or not g["C"]["skill_sha256"]: errors.append(f"{qid}: C/D Skill哈希不一致或为空")
    if g["A"]["rag_context_sha256"] or g["C"]["rag_context_sha256"]: errors.append(f"{qid}: A/C意外包含RAG")
    if g["A"]["skill_sha256"] or g["B"]["skill_sha256"]: errors.append(f"{qid}: A/B意外包含Skill")
print(json.dumps({"scope":"positive_control_21_questions_v2","question_count":len(byq),"skill_files_verified":len(hash_rows),"B_D_hash_equal":sum(g.get('B',{}).get('rag_context_sha256')==g.get('D',{}).get('rag_context_sha256') and bool(g.get('B',{}).get('rag_context_sha256')) for g in byq.values()),"C_D_hash_equal":sum(g.get('C',{}).get('skill_sha256')==g.get('D',{}).get('skill_sha256') and bool(g.get('C',{}).get('skill_sha256')) for g in byq.values()),"errors":errors,"pass":not errors}, ensure_ascii=False, indent=2))
sys.exit(1 if errors else 0)
