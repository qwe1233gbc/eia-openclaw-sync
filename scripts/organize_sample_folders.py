"""
统一整理样本链文件夹 V2
- 从目录名/文件名提取项目名，按项目归并
- 自动检测文件类型（受理公告/批复/修改意见等）
- 匹配 candidate_project_inventory.csv 中已有的项目ID
"""
import os, re, csv, shutil
from pathlib import Path
from collections import defaultdict

OLD_BASE = Path("05_样本链_受理公告_终稿_批复_修改意见")
NEW_BASE = Path("05_样本链（按项目组织）")
SUBDIRS = ["01_受理公告", "02_终稿_拟审批稿", "03_批复", "04_修改意见_补正通知", "05_专家意见", "06_提取产物"]

def load_project_mapping():
    """从CSV加载 project_id -> project_name 映射"""
    mapping = {}
    csv_path = Path("02_适用行业与样本筛选/candidate_project_inventory.csv")
    if csv_path.exists():
        with open(csv_path, encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                pid = row.get('project_id','').strip()
                pname = row.get('project_name','').strip()
                if pid and pname:
                    mapping[pid] = pname
    return mapping

def extract_key_name(dirname: str) -> str:
    """从目录名中提取核心关键词（公司名简称）"""
    name = re.sub(r'^[\d]+\.?\s*', '', dirname)
    name = re.sub(r'^（[^）]*）', '', name)
    name = re.sub(r'^\[[^\]]*\]\s*', '', name)
    name = re.sub(r'\s*修改意见.*$', '', name)
    name = re.sub(r'\s*迁扩建项目.*$', '', name)
    name = re.sub(r'\s*迁建项目.*$', '', name)
    name = re.sub(r'\s*新建项目.*$', '', name)
    name = re.sub(r'\s*搬迁项目.*$', '', name)
    name = re.sub(r'（修$', '', name)
    name = re.sub(r'（全本$', '', name)
    name = re.sub(r'-$', '', name)
    name = re.sub(r'\.$', '', name)
    return name.strip()

def match_to_inventory(key_name: str, mapping: dict) -> str | None:
    """将公司名匹配到已知 project_id"""
    for pid, pname in mapping.items():
        pname_short = pname.replace('佛山市顺德区','').replace('佛山市','').replace('有限公司','').replace('新建项目','').strip()
        if pname_short and pname_short in key_name:
            return pid
        if key_name and key_name in pname:
            return pid
    return None

def classify_file(filename: str, parent_dir_name: str = "") -> str | None:
    """判断文件类型，返回目标子目录名"""
    full = filename + parent_dir_name

    if any(kw in full for kw in ['批复', '审批意见']):
        if '修改' not in filename and '审查意见' not in filename:
            return "03_批复"

    if any(kw in full for kw in ['修改意见', '补正通知', '审查意见', '补充通知']):
        return "04_修改意见_补正通知"

    if filename.endswith('.jsonl') and 'enriched' in filename.lower():
        return "04_修改意见_补正通知"

    if filename.endswith('.md') and '受理公告' in filename:
        return "01_受理公告"

    if any(kw in filename for kw in ['报批稿', '终稿', '拟审批', '拟批准', '送审稿']):
        return "02_终稿_拟审批稿"

    return None

def scan_and_migrate(dry_run=True):
    if not OLD_BASE.exists():
        print(f"[WARN] 旧目录不存在: {OLD_BASE}")
        return

    mapping = load_project_mapping()
    print(f"已加载 {len(mapping)} 个项目映射")

    project_files = defaultdict(list)
    unclassified = []

    for old_path in OLD_BASE.rglob("*"):
        if not old_path.is_file():
            continue
        if old_path.suffix in ['.csv', '.md'] and old_path.parent == OLD_BASE:
            continue

        filename = old_path.name
        parent_dir = old_path.parent.name if old_path.parent != OLD_BASE else ""

        file_type = classify_file(filename, parent_dir)

        project_id = None
        for pid in mapping:
            if pid in filename or pid in str(old_path):
                project_id = pid
                break

        if not project_id:
            search_text = parent_dir if parent_dir else filename
            key_name = extract_key_name(search_text)
            project_id = match_to_inventory(key_name, mapping)

        if not project_id:
            project_id = extract_key_name(parent_dir or filename)[:60]

        if project_id:
            project_files[project_id].append((old_path, file_type or "06_提取产物"))
        else:
            unclassified.append((old_path, "no_project"))

    print(f"\n识别到 {len(project_files)} 个项目组")
    for pid, files in sorted(project_files.items()):
        types = defaultdict(int)
        for _, ft in files:
            types[ft] += 1
        print(f"  {pid}: {len(files)} 文件 ({dict(types)})")

    if dry_run:
        total = sum(len(fs) for fs in project_files.values())
        print(f"\n[Dry Run] 共 {total} 文件将迁移到 {len(project_files)} 个项目文件夹")
        if unclassified:
            print(f"  无法归类: {len(unclassified)} 个")
    else:
        count = 0
        for pid, files in project_files.items():
            proj_dir = NEW_BASE / pid
            for sub in SUBDIRS:
                (proj_dir / sub).mkdir(parents=True, exist_ok=True)
            for old_path, file_type in files:
                dest = proj_dir / file_type / old_path.name
                if not dest.exists():
                    shutil.copy2(old_path, dest)
                    count += 1
        print(f"\n[Done] 实际迁移 {count} 个文件")

        # 迁移根级CSV/MD到元数据
        meta = NEW_BASE / "_元数据"
        meta.mkdir(exist_ok=True)
        for f in OLD_BASE.glob("*.csv"):
            shutil.copy2(f, meta / f.name)
        for f in OLD_BASE.glob("*.md"):
            if any(kw in f.name.lower() for kw in ['sample_chain','sample_selection','explanation']):
                shutil.copy2(f, meta / f.name)

        # 归档旧目录
        archive = NEW_BASE / "_归档_旧结构"
        archive.mkdir(exist_ok=True)
        old_dest = archive / OLD_BASE.name
        if not old_dest.exists():
            shutil.move(str(OLD_BASE), str(old_dest))
            print(f"[Done] 旧目录已归档至 {old_dest}")

if __name__ == "__main__":
    import sys
    dry_run = "--execute" not in sys.argv
    print("=" * 60)
    print(f"样本链文件夹统一整理 V2 | {'预览' if dry_run else '执行迁移'}")
    print("=" * 60)
    scan_and_migrate(dry_run=dry_run)
    if dry_run:
        print("\n[预览完成] 加 --execute 执行实际迁移")
