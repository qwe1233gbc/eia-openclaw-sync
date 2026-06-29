#!/usr/bin/env python3
"""Build a local hybrid retrieval index for EIA audit knowledge.

This script is inspired by the Chen et al. (2026) dual-database design:
one semantic/vector index plus one full-text index. For this repository we
use SQLite only, so the workflow is reproducible without Pinecone or
OpenSearch.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import urllib.request
from pathlib import Path
from typing import Any, Iterable


TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".jsonl", ".yaml", ".yml"}


def load_config(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception:
        return load_minimal_yaml(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_minimal_yaml(path: Path) -> dict[str, Any]:
    """Small YAML subset parser for this config file when PyYAML is absent."""
    data: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, data)]
    current_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if line.startswith("- "):
            value = line[2:].strip()
            if isinstance(parent, list):
                if ":" in value:
                    k, v = value.split(":", 1)
                    obj = {k.strip(): parse_scalar(v.strip())}
                    parent.append(obj)
                    stack.append((indent, obj))
                else:
                    parent.append(parse_scalar(value))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                next_obj: Any = [] if key in {"sources", "glob"} else {}
                parent[key] = next_obj
                stack.append((indent, next_obj))
                current_key = key
            else:
                parent[key] = parse_scalar(value)
                current_key = key
    return data


def parse_scalar(value: str) -> Any:
    if value.isdigit():
        return int(value)
    return value.strip('"').strip("'")


def read_text(path: Path) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def cjk_search_text(text: str) -> str:
    chars: list[str] = []
    for ch in text.lower():
        if "\u4e00" <= ch <= "\u9fff":
            chars.extend([" ", ch, " "])
        else:
            chars.append(ch)
    return re.sub(r"\s+", " ", "".join(chars)).strip()


def chunk_text(text: str, chunk_chars: int, overlap_chars: int) -> Iterable[tuple[int, int, str]]:
    text = normalize_text(text)
    if not text:
        return
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_chars)
        chunk = text[start:end].strip()
        if chunk:
            yield start, end, chunk
        if end >= len(text):
            break
        start = max(0, end - overlap_chars)


def hash_embedding(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    tokens = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[idx] += sign
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [round(v / norm, 6) for v in vector]


def openai_embedding(text: str, model: str) -> list[float]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when embedding.mode=openai")
    payload = json.dumps({"model": model, "input": text}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["data"][0]["embedding"]


def embed(text: str, config: dict[str, Any]) -> list[float]:
    emb_cfg = config.get("embedding", {})
    mode = emb_cfg.get("mode", "hash")
    if mode == "openai":
        return openai_embedding(text, emb_cfg.get("openai_model", "text-embedding-3-small"))
    return hash_embedding(text, int(emb_cfg.get("dimensions", 384)))


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE chunks (
            chunk_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_path TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            char_start INTEGER NOT NULL,
            char_end INTEGER NOT NULL,
            content TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            embedding_json TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            chunk_id UNINDEXED,
            search_text,
            content,
            tokenize='unicode61'
        )
        """
    )
    return conn


def iter_source_files(repo_root: Path, source: dict[str, Any]) -> Iterable[Path]:
    root = repo_root / source["root"]
    for pattern in source.get("glob", ["**/*.md"]):
        yield from root.glob(pattern)


def build(config_path: Path, repo_root: Path) -> None:
    config_path = config_path.resolve()
    repo_root = repo_root.resolve()
    config = load_config(config_path)
    db_path = repo_root / config["index_path"]
    conn = init_db(db_path)
    chunk_chars = int(config.get("chunking", {}).get("chunk_chars", 1200))
    overlap_chars = int(config.get("chunking", {}).get("overlap_chars", 180))

    inserted = 0
    for source in config.get("sources", []):
        for path in sorted(set(iter_source_files(repo_root, source))):
            if not path.is_file():
                continue
            text = read_text(path)
            if not text:
                continue
            rel_path = path.relative_to(repo_root).as_posix()
            for idx, (start, end, content) in enumerate(chunk_text(text, chunk_chars, overlap_chars)):
                raw_id = f"{source['name']}::{rel_path}::{idx}::{start}:{end}"
                chunk_id = hashlib.sha1(raw_id.encode("utf-8")).hexdigest()
                metadata = {"config": str(config_path.relative_to(repo_root)), "file_suffix": path.suffix}
                vector = embed(content, config)
                conn.execute(
                    """
                    INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        source["name"],
                        rel_path,
                        source.get("evidence_type", "other"),
                        idx,
                        start,
                        end,
                        content,
                        json.dumps(metadata, ensure_ascii=False),
                        json.dumps(vector),
                    ),
                )
                conn.execute(
                    "INSERT INTO chunks_fts(chunk_id, search_text, content) VALUES (?, ?, ?)",
                    (chunk_id, cjk_search_text(content), content),
                )
                inserted += 1
    conn.commit()
    conn.close()
    print(json.dumps({"index_path": str(db_path), "chunks": inserted}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    repo_root = Path.cwd()
    build(args.config, repo_root)


if __name__ == "__main__":
    main()
