from __future__ import annotations

import argparse
import hashlib
import secrets
from pathlib import Path

from pipeline_core import ROOT, read_jsonl, write_json, write_jsonl

FORBIDDEN = {
    "group",
    "experiment_group",
    "rag_enabled",
    "workflow_enabled",
    "prompt",
    "rag_context",
    "workflow_trace",
    "model",
    "model_name",
    "run_id",
    "knowledge_dependency",
    "workflow_dependency",
}


def remove_identity(value):
    if isinstance(value, dict):
        return {key: remove_identity(item) for key, item in value.items() if key not in FORBIDDEN}
    if isinstance(value, list):
        return [remove_identity(item) for item in value]
    return value


def blind(records: list[dict], seed: int = 20260729) -> tuple[list[dict], dict]:
    salt = secrets.token_hex(16)
    blinded, mapping = [], {}
    for index, row in enumerate(records):
        identity = f"{row.get('question_id')}|{row.get('group')}|{row.get('run_id')}|{index}"
        blind_id = "BO-" + hashlib.sha256((salt + identity).encode()).hexdigest()[:16]
        clean = remove_identity(row)
        clean["blinded_output_id"] = blind_id
        blinded.append(clean)
        mapping[blind_id] = {
            "question_id": row.get("question_id"),
            "group": row.get("group"),
            "run_id": row.get("run_id"),
        }
    import random

    random.Random(seed).shuffle(blinded)
    return blinded, {"salt": salt, "mapping": mapping, "shuffle_seed": seed}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "runs" / "blinded_packets" / "blinded_outputs.jsonl"
    )
    parser.add_argument(
        "--key", type=Path, default=ROOT / "private" / "blinding_key.json"
    )
    args = parser.parse_args()
    blinded, key = blind(read_jsonl(args.input))
    write_jsonl(args.output, blinded)
    write_json(args.key, key)
    print(f"blinded {len(blinded)} outputs")


if __name__ == "__main__":
    main()
