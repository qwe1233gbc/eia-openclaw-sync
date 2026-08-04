from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

import yaml

from pipeline_core import ROOT, read_jsonl, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packets", type=Path)
    parser.add_argument(
        "--config", type=Path, default=ROOT / "configs" / "evaluator_minimal.yaml"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    packets = read_jsonl(args.packets)
    prompt_path = (args.config.parent / config["prompt"]).resolve()
    schema_path = (args.config.parent / config["schema"]).resolve()
    readiness = {
        "packet_count": len(packets),
        "model": config.get("model") or config.get("models"),
        "prompt_sha256": sha256(prompt_path),
        "schema_sha256": sha256(schema_path),
        "temperature": config["temperature"],
        "retry_count": config["retry_count"],
        "api_key_available": bool(os.getenv("OPENAI_API_KEY")),
    }
    print(readiness)
    if args.dry_run:
        return
    if not readiness["api_key_available"]:
        raise SystemExit("缺少OPENAI_API_KEY；未执行也未伪造任何GPT评分")
    if "USER_MUST_FREEZE" in str(readiness["model"]):
        raise SystemExit("必须先在评价配置中冻结具体模型版本")
    raise SystemExit(
        "实时API调用默认关闭：请在人工确认模型版本、费用预算和数据发送范围后实现/启用。"
    )


if __name__ == "__main__":
    main()
