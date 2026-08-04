from __future__ import annotations
import csv, hashlib, json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "10_消融实验设计/06_运行矩阵/run_matrix_v2.csv"
HASH_LISTS = [
    ROOT / "09_环评审核技能库/skill_hashes_v2.csv",
    ROOT / "10_消融实验设计/03_Skill冻结快照/skill_hashes_v2.csv",
]
SNAPSHOTS = [
    ROOT / "09_环评审核技能库/formal_skill_snapshots_v2.jsonl",
    ROOT / "10_消融实验设计/03_Skill冻结快照/skill_snapshots_v2.jsonl",
]
rows=list(csv.DictReader(MATRIX.open(encoding="utf-8-sig")))
byq=defaultdict(dict)
for r in rows: byq[r["question_id"]][r["group"]]=r
errors=[]
hash_sets=[]
for path in HASH_LISTS:
    with path.open(encoding="utf-8-sig") as f:
        hash_sets.append({row["skill_id"]: row for row in csv.DictReader(f)})
if {sid: row["skill_sha256"] for sid, row in hash_sets[0].items()} != {sid: row["skill_sha256"] for sid, row in hash_sets[1].items()}:
    errors.append("09目录与10目录v2哈希清单不一致")
hash_rows=list(hash_sets[0].values())
for row in hash_rows:
    skill_path = ROOT / row["path"]
    # Hash canonical UTF-8 text so checkout-level CRLF/LF conversion does not
    # change a frozen Skill identity.
    actual = hashlib.sha256(skill_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    if actual != row["skill_sha256"]:
        errors.append(f"Skill {row['skill_id']}: v2清单哈希与文件不一致")
snapshot_sets=[]
for path in SNAPSHOTS:
    snapshot_sets.append({row["skill_id"]: row for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())})
for sid, expected in hash_sets[0].items():
    left=snapshot_sets[0].get(sid)
    right=snapshot_sets[1].get(sid)
    if not left or not right:
        errors.append(f"Skill {sid}: v2快照记录缺失")
        continue
    if left["content"] != right["content"]:
        errors.append(f"Skill {sid}: 09目录与10目录v2快照正文不一致")
    snapshot_hash=hashlib.sha256(left["content"].encode("utf-8")).hexdigest()
    if snapshot_hash != expected["skill_sha256"] or left["skill_sha256"] != expected["skill_sha256"] or right["skill_sha256"] != expected["skill_sha256"]:
        errors.append(f"Skill {sid}: 源文件、快照正文与声明哈希不一致")
for qid, g in byq.items():
    if set(g) != set("ABCD"): errors.append(f"{qid}: 缺少组别") ; continue
    reports={g[x]["report_context_sha256"] for x in "ABCD"}
    if len(reports)!=1 or not next(iter(reports)): errors.append(f"{qid}: A/B/C/D报告哈希不一致或为空")
    if g["B"]["rag_context_sha256"] != g["D"]["rag_context_sha256"] or not g["B"]["rag_context_sha256"]: errors.append(f"{qid}: B/D RAG哈希不一致或为空")
    if g["C"]["skill_sha256"] != g["D"]["skill_sha256"] or not g["C"]["skill_sha256"]: errors.append(f"{qid}: C/D Skill哈希不一致或为空")
    if g["A"]["rag_context_sha256"] or g["C"]["rag_context_sha256"]: errors.append(f"{qid}: A/C意外包含RAG")
    if g["A"]["skill_sha256"] or g["B"]["skill_sha256"]: errors.append(f"{qid}: A/B意外包含Skill")
print(json.dumps({"scope":"positive_control_21_questions_v2","question_count":len(byq),"skill_files_verified":len(hash_rows),"snapshot_records_verified":len(snapshot_sets[0]),"B_D_hash_equal":sum(g.get('B',{}).get('rag_context_sha256')==g.get('D',{}).get('rag_context_sha256') and bool(g.get('B',{}).get('rag_context_sha256')) for g in byq.values()),"C_D_hash_equal":sum(g.get('C',{}).get('skill_sha256')==g.get('D',{}).get('skill_sha256') and bool(g.get('C',{}).get('skill_sha256')) for g in byq.values()),"errors":errors,"pass":not errors}, ensure_ascii=False, indent=2))
sys.exit(1 if errors else 0)
