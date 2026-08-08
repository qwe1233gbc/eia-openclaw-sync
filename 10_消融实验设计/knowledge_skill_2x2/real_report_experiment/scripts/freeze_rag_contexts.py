from core import freeze_rag_contexts

rows = freeze_rag_contexts()
print({"frozen_rag_rows": len(rows)})
