from __future__ import annotations

import os
import subprocess
from pathlib import Path

from pipeline_core import ROOT, TAXONOMY_CSV


def main() -> None:
    node = os.environ.get(
        "CODEX_NODE_EXE",
        r"C:\Users\ylx\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe",
    )
    script = ROOT / "scripts" / "export_taxonomy_review_workbook.mjs"
    output = ROOT / "taxonomy" / "taxonomy_review_workbook.xlsx"
    subprocess.run(
        [node, str(script), str(TAXONOMY_CSV), str(output)],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
