from core import build_rag_corpus

rows = build_rag_corpus()
print({"rag_chunks": len(rows)})
