#!/usr/bin/env python3
"""Hybrid retrieval from the local SQLite index."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path


def cjk_search_text(text: str) -> str:
    chars: list[str] = []
    for ch in text.lower():
        if "\u4e00" <= ch <= "\u9fff":
            chars.extend([" ", ch, " "])
        else:
            chars.append(ch)
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def hash_embedding(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    tokens = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def vector_search(conn: sqlite3.Connection, query: str, limit: int, dimensions: int) -> list[tuple[str, float]]:
    q = hash_embedding(query, dimensions)
    rows = conn.execute("SELECT chunk_id, embedding_json FROM chunks").fetchall()
    scored = []
    for chunk_id, embedding_json in rows:
        scored.append((chunk_id, cosine(q, json.loads(embedding_json))))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def fts_search(conn: sqlite3.Connection, query: str, limit: int) -> list[tuple[str, float]]:
    search = cjk_search_text(query)
    try:
        rows = conn.execute(
            "SELECT chunk_id, bm25(chunks_fts) AS score FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?",
            (search, limit),
        ).fetchall()
        return [(chunk_id, -float(score)) for chunk_id, score in rows]
    except sqlite3.OperationalError:
        like = f"%{query}%"
        rows = conn.execute(
            "SELECT chunk_id, 1.0 FROM chunks_fts WHERE content LIKE ? LIMIT ?",
            (like, limit),
        ).fetchall()
        return [(chunk_id, float(score)) for chunk_id, score in rows]


def reciprocal_rank_fusion(*ranked_lists: list[tuple[str, float]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, (chunk_id, _score) in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def fetch_chunks(conn: sqlite3.Connection, ranked: list[tuple[str, float]], limit: int) -> list[dict]:
    out = []
    for chunk_id, score in ranked[:limit]:
        row = conn.execute(
            """
            SELECT chunk_id, source_name, source_path, evidence_type, chunk_index, char_start, char_end, content
            FROM chunks WHERE chunk_id = ?
            """,
            (chunk_id,),
        ).fetchone()
        if not row:
            continue
        out.append(
            {
                "score": round(score, 6),
                "chunk_id": row[0],
                "source_name": row[1],
                "source_path": row[2],
                "evidence_type": row[3],
                "chunk_index": row[4],
                "char_start": row[5],
                "char_end": row[6],
                "content": row[7][:1000],
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--candidate-k", type=int, default=30)
    parser.add_argument("--dimensions", type=int, default=384)
    args = parser.parse_args()

    conn = sqlite3.connect(args.index)
    v = vector_search(conn, args.query, args.candidate_k, args.dimensions)
    f = fts_search(conn, args.query, args.candidate_k)
    fused = reciprocal_rank_fusion(v, f)
    print(json.dumps(fetch_chunks(conn, fused, args.top_k), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

