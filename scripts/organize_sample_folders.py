"""
统一整理样本链文件夹
将分散在多个子目录的受理公告/终稿/批复/修改意见等文件，
按项目重组到统一结构
"""
import os
import shutil
from pathlib import Path

# ============================================================
# 配置
# ============================================================

# 旧目录（源）
OLD_BASE = Path("05_样本链_受理公告_终稿_批复_修改意见")

# 新目录（目标）
NEW_BASE = Path("05_样本链（按项目组织）")

# 项目列表（从 candidate_project_inventory.csv 获取）
PROJECTS = {
    "SH_001": "某塑胶包装项目",
    "SH_002": "顺德利兴塑料包装",
    "SH_003": "某注塑项目",
    "SH_004": "顺德区百洛涂料",
    "SH_005": "某塑胶制品项目",
    "SH_006": "某注塑加工项目",
    "SH_007": "某注塑件项目",
    "SH_008": "某塑料零件项目",
    "SH_009": "某塑胶复合项目",
    "SH_010": "某塑料制品项目",
    "SH_011": "某塑料配件项目",
    "SH_012": "某塑胶材料项目",
    "AI_001": "AI包项目1",
    "AI_002": "AI包项目2",
}

# 子目录结构
SUBDIRS = [
    "01_受理公告",
    "02_终稿_拟审批稿",
    "03_批复",
    "04_修改意见_补正通知",
    "05_专家意见",
    "06_提取产物",
]


# ============================================================
# Step 1: 创建文件夹骨架
# ============================================================

def create_folder_skeleton():
    """创建全部的项目文件夹和子目录"""
    NEW_BASE.mkdir(exist_ok=True)

    # 全局元数据目录
    meta_dir = NEW_BASE / "_元数据"
    meta_dir.mkdir(exist_ok=True)

    # 归档目录
    archive_dir = NEW_BASE / "_归档_旧结构"
    archive_dir.mkdir(exist_ok=True)

    for pid, pname in PROJECTS.items():
        proj_dir = NEW_BASE / pid
        for sub in SUBDIRS:
            (proj_dir / sub).mkdir(parents=True, exist_ok=True)

        # 创建项目信息文件
        info_path = proj_dir / "_项目信息.md"
        if not info_path.exists():
            info_path.write_text(f"""# {pid} — {pname}

## 基本信息
- 项目名称：{pname}
- 建设单位：待填写
- 建设地点：佛山市顺德区
- 行业类别及代码：待填写
- 行业代码层级：待填写

## 审批链状态
- [ ] 受理公告报告
- [ ] 终稿/拟审批稿
- [ ] 批复
- [ ] 修改意见/补正通知
- [ ] 专家意见

## 工艺特征
- [ ] P1 涉胶水/胶粘剂
- [ ] P2 涉涂布/涂装
- [ ] P3 涉复合/贴合
- [ ] P4 涉印刷
- [ ] P5 涉熟化/固化/烘干

## 审核要素
- [ ] B1 涉 VOCs 有组织排放
- [ ] B2 涉活性炭吸附
- [ ] B3 涉废活性炭

## 指南适用性
- 塑料指南适用性：待判定
- 推荐用途：待判定
- 备注：
""", encoding="utf-8")

    print(f"[Done] 创建 {len(PROJECTS)} 个项目文件夹")
    print(f"  目标路径: {NEW_BASE.absolute()}")


# ============================================================
# Step 2: 文件分类器
# ============================================================

def classify_file(filename: str) -> str | None:
    """根据文件名判断文件类型，返回目标子目录名"""
    name_lower = filename.lower()

    # 受理公告
    if any(kw in filename for kw in ["受理公告", "受理通知书", "acceptance"]):
        return "01_受理公告"

    # 终稿/拟审批稿
    if any(kw in filename for kw in ["终稿", "报批稿", "拟审批", "拟批准", "final"]):
        return "02_终稿_拟审批稿"

    # 批复
    if any(kw in filename for kw in ["批复", "审批意见", "approval"]):
        # 但排除"修改意见"、"审查意见"
        if "修改" not in filename and "审查意见" not in filename:
            return "03_批复"

    # 修改意见/补正通知
    if any(kw in filename for kw in ["修改意见", "补正通知", "审查意见", "补充通知", "review"]):
        return "04_修改意见_补正通知"

    # 专家意见
    if any(kw in filename for kw in ["专家意见", "评审意见", "expert"]):
        return "05_专家意见"

    # MinerU 解析结果
    if name_lower.endswith("_mineru.md") or "mineru" in name_lower:
        # 根据对应的原始文件类型归类
        for kw, subdir in [
            ("受理公告", "01_受理公告"),
            ("终稿", "02_终稿_拟审批稿"),
            ("拟审批", "02_终稿_拟审批稿"),
            ("批复", "03_批复"),
            ("修改", "04_修改意见_补正通知"),
            ("补正", "04_修改意见_补正通知"),
        ]:
            if kw in filename:
                return subdir
        return None  # 无法判断，手动处理

    # 提取产物
    if any(kw in name_lower for kw in ["证据单元", "标准依据", "审核任务", "提取", "extract"]):
        return "06_提取产物"

    return None  # 无法分类


def detect_project(filename: str, filepath: str) -> str | None:
    """根据文件名或路径检测属于哪个项目"""
    # 检查是否包含项目编号
    for pid in PROJECTS:
        if pid in filename or pid in filepath:
            return pid
    return None


# ============================================================
# Step 3: 迁移文件
# ============================================================

def scan_and_migrate(dry_run: bool = True):
    """扫描旧目录，迁移文件到新结构"""
    if not OLD_BASE.exists():
        print(f"[WARN] 旧目录不存在: {OLD_BASE}")
        return

    migrations: list[dict] = []
    unclassified: list[dict] = []

    # 遍历旧目录所有文件
    for old_path in OLD_BASE.rglob("*"):
        if not old_path.is_file():
            continue
        if old_path.suffix in [".csv", ".md"] and old_path.parent == OLD_BASE:
            continue  # 根级CSV/MD归入元数据，不按项目迁移

        filename = old_path.name
        rel_path = str(old_path.relative_to(OLD_BASE))

        file_type = classify_file(filename)
        project = detect_project(filename, rel_path)

        if project and file_type:
            migrations.append({
                "project": project,
                "file_type": file_type,
                "filename": filename,
                "source": str(old_path),
                "source_rel": rel_path,
            })
        else:
            unclassified.append({
                "filename": filename,
                "source": str(old_path),
                "reason": "no_project" if not project else "no_type",
            })

    # 执行迁移
    if dry_run:
        print(f"\n[Dry Run] 将迁移 {len(migrations)} 个文件:")
        for m in migrations[:20]:
            print(f"  {m['project']}/{m['file_type']}/ ← {m['filename']}")
        if len(migrations) > 20:
            print(f"  ... 及其他 {len(migrations)-20} 个文件")
        print(f"\n无法分类: {len(unclassified)} 个文件")
        if unclassified:
            for u in unclassified[:10]:
                print(f"  ? {u['filename']} ({u['reason']})")
    else:
        count = 0
        for m in migrations:
            dest_dir = NEW_BASE / m["project"] / m["file_type"]
            dest_path = dest_dir / m["filename"]
            shutil.copy2(m["source"], dest_path)
            count += 1

        print(f"[Done] 迁移了 {count} 个文件")

        # 迁移元数据CSV/MD
        for meta_file in OLD_BASE.glob("*.csv"):
            shutil.copy2(meta_file, NEW_BASE / "_元数据" / meta_file.name)
        for meta_file in OLD_BASE.glob("*.md"):
            shutil.copy2(meta_file, NEW_BASE / "_元数据" / meta_file.name)

        # 旧目录移入归档
        archive_dest = NEW_BASE / "_归档_旧结构" / OLD_BASE.name
        if not archive_dest.exists():
            shutil.move(str(OLD_BASE), str(archive_dest))
            print(f"[Done] 旧目录已归档至 {archive_dest}")


# ============================================================
# Step 4: 生成文件清单
# ============================================================

def generate_inventory():
    """生成项目文件清单 CSV"""
    import csv

    rows = []
    for pid in PROJECTS:
        proj_dir = NEW_BASE / pid
        if not proj_dir.exists():
            continue
        for file_path in proj_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("_"):
                rel = file_path.relative_to(proj_dir)
                rows.append({
                    "project": pid,
                    "subdir": str(rel.parent),
                    "filename": file_path.name,
                    "size_kb": round(file_path.stat().st_size / 1024, 1),
                })

    csv_path = NEW_BASE / "_元数据" / "sample_chain_inventory_v2.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["project", "subdir", "filename", "size_kb"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[Done] 清单已生成: {csv_path}")
    print(f"  共 {len(rows)} 个文件")


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    import sys

    dry_run = "--execute" not in sys.argv

    print("=" * 60)
    print("样本链文件夹统一整理")
    print(f"模式: {'Dry Run (预览)' if dry_run else '执行迁移'}")
    print("=" * 60)

    create_folder_skeleton()
    scan_and_migrate(dry_run=dry_run)

    if not dry_run:
        generate_inventory()

    print(f"\n{'[预览完成] 加 --execute 执行实际迁移' if dry_run else '[迁移完成]'}")
