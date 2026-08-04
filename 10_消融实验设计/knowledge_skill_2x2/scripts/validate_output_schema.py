from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from pipeline_core import ROOT, read_jsonl


def validate_file(path: Path, schema_path: Path) -> list[str]:
    validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    rows = read_jsonl(path) if path.suffix == ".jsonl" else [json.loads(path.read_text(encoding="utf-8"))]
    errors = []
    for index, row in enumerate(rows, 1):
        for error in validator.iter_errors(row):
            errors.append(f"{index}:{'/'.join(map(str, error.path))}: {error.message}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--schema", type=Path, default=ROOT / "schemas" / "audit_output_v1.schema.json"
    )
    args = parser.parse_args()
    errors = validate_file(args.path, args.schema)
    if errors:
        raise SystemExit("\n".join(errors))
    print("schema valid")


if __name__ == "__main__":
    main()
