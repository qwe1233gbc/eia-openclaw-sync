from __future__ import annotations
import csv, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "03_指南解析_明文标准库/formal_rag/source_manifest.jsonl"
ALLOWED = ("法律", "法规", "条例", "标准", "官方", "正式", "技术规范", "指南", "公报", "区划", "结构化转录")
FORBIDDEN = ("05_QA测试集", "09_环评审核技能库", "06_Dify工作流", "10_消融实验设计")
rows = [json.loads(x) for x in MANIFEST.read_text(encoding="utf-8").splitlines() if x.strip()]
errors, warnings = [], []
sha_counts = Counter(r.get("source_sha256", "") for r in rows if r.get("source_sha256"))
for r in rows:
    label = f"{r.get('source_id')}: {r.get('title')}"
    if r.get("eligible_for_formal_rag") and not any(x in str(r.get("document_type", "")) for x in ALLOWED): errors.append(label + " document_type不在白名单")
    blob = json.dumps(r, ensure_ascii=False)
    if any(x in blob for x in FORBIDDEN): errors.append(label + " 指向禁止目录")
    if r.get("eligible_for_formal_rag") and not r.get("source_sha256"): errors.append(label + " 缺少SHA256")
    if not r.get("validity_status"): warnings.append(label + " 版本状态未知")
    if r.get("is_primary_source") is False and r.get("eligible_for_formal_rag"): warnings.append(label + " 派生来源仅可作元数据")
for sha, n in sha_counts.items():
    if n > 1: warnings.append(f"SHA256重复 {sha}: {n}条")
print(json.dumps({"scope":"formal source manifest only","source_count":len(rows),"errors":errors,"warnings":warnings,"pass":not errors}, ensure_ascii=False, indent=2))
sys.exit(1 if errors else 0)
