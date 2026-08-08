from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable


TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-_/][A-Za-z0-9]+)*|\d+(?:\.\d+)*|[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text or "")]


def bm25_rank(query: str, documents: list[dict], top_k: int = 20) -> list[dict]:
    """Deterministic BM25 retrieval for the provisional, non-hybrid validation index."""
    doc_tokens = [tokenize(d.get("content", "")) for d in documents]
    avgdl = sum(map(len, doc_tokens)) / max(len(doc_tokens), 1)
    dfs: Counter[str] = Counter()
    for toks in doc_tokens:
        dfs.update(set(toks))
    q = tokenize(query)
    qset = set(q)
    n = len(documents)
    ranked = []
    for doc, toks in zip(documents, doc_tokens):
        tf = Counter(toks)
        score = 0.0
        for term in q:
            if not tf[term]:
                continue
            idf = math.log(1 + (n - dfs[term] + 0.5) / (dfs[term] + 0.5))
            denom = tf[term] + 1.2 * (1 - 0.75 + 0.75 * len(toks) / max(avgdl, 1))
            score += idf * (tf[term] * 2.2) / denom
        exact = sum(1 for term in qset if len(term) >= 4 and term in doc.get("content", "").lower())
        authority = float(doc.get("authority_weight", 1.0))
        score = score * authority + exact * 0.75
        ranked.append({**doc, "retrieval_score": round(score, 6)})
    return sorted(ranked, key=lambda x: (-x["retrieval_score"], x.get("parent_id", "")))[:top_k]


def select_required_sources(
    ranked: Iterable[dict], required_source_ids: Iterable[str], final_parent_k: int = 8,
    fill_with_non_required: bool = False,
) -> list[dict]:
    """Fixed reranking: exact required source IDs first, then BM25 order."""
    required = list(dict.fromkeys(required_source_ids))
    ranked = list(ranked)
    selected: list[dict] = []
    matches_by_source = {
        source_id: [d for d in ranked if d.get("source_id") == source_id]
        for source_id in required
    }
    level = 0
    while len(selected) < final_parent_k:
        added = False
        for source_id in required:
            matches = matches_by_source[source_id]
            if level < len(matches):
                selected.append(matches[level])
                added = True
                if len(selected) >= final_parent_k:
                    break
        if not added:
            break
        level += 1
    if fill_with_non_required:
        for doc in ranked:
            if doc.get("parent_id") not in {d.get("parent_id") for d in selected}:
                selected.append(doc)
            if len(selected) >= final_parent_k:
                break
    return selected[:final_parent_k]
