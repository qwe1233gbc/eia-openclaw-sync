#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Dify 工作流知识库文件解析为标准卡的最小脚本骨架。
当前压缩包已内置解析结果；后续新增 Dify KB 文件时，可按本脚本扩展。
"""
from pathlib import Path
import json
import re

DIFY_KB_DIR = Path("03_指南解析_明文标准库/Dify工作流知识库")
OUT = Path("03_法规库_明文依据/parsed_from_dify_kb_standard_cards/standard_cards.jsonl")

def infer_skill_id(filename: str) -> list[str]:
    mapping = {
        "#2_": ["02_环保投资"],
        "#5_": ["04_建设内容"],
        "#6_": ["05_环境质量现状数据"],
        "#7_": ["06_环境质量执行标准", "07_污染物排放标准"],
        "#8_": ["07_污染物排放标准"],
        "#9_": ["08_产污系数合理性"],
        "#10_": ["09_产污系数定量核算"],
        "#17_": ["10_废气收集形式及排气量"],
        "#18_": ["11_废气收集风量与设计风量"],
        "#19_": ["12_废气收集效率"],
        "national_economic": ["01_国民经济行业类别"],
        "plastic_rubber": ["01_国民经济行业类别"],
        "三线一单": ["03_三线一单"],
        "GB_18597": ["14_危险废物识别"],
        "GB_18599": ["14_危险废物识别"],
    }
    hits = []
    for k, v in mapping.items():
        if filename.startswith(k) or k in filename:
            hits.extend(v)
    return sorted(set(hits)) or ["99_待人工归类"]

def simple_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    title_match = re.search(r"^#\s*(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else path.stem
    return {
        "standard_id": "AUTO-" + re.sub(r"[^0-9A-Za-z\u4e00-\u9fa5]+", "-", path.stem).strip("-"),
        "title": title,
        "skill_ids": infer_skill_id(path.name),
        "source_files": [str(path)],
        "trigger_keywords": list(sorted(set(re.findall(r"[A-Za-z]{2,}\s*\d{2,4}|\bGB\s*\d+|\bHJ\s*\d+|DB44/?\d+|VOCs|非甲烷总烃|三线一单|活性炭|危险废物", text))))[:30],
        "raw_excerpt": text[:500],
    }

def main():
    cards = []
    for path in DIFY_KB_DIR.iterdir():
        if path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".jsonl"}:
            cards.append(simple_card(path))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
