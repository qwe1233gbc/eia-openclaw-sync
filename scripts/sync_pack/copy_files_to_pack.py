import os, shutil

BASE = r"E:\软件\eia_plastic_guide_research_pack"

# 1. Copy 12 final approval PDFs
src = r"E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic"
dst = os.path.join(BASE, "05_样本链_受理公告_终稿_批复_修改意见", "批复文件_终稿")
if os.path.exists(src):
    shutil.copytree(src, dst, dirs_exist_ok=True)
    cnt = len([f for f in os.listdir(dst) if f.endswith('.pdf')])
    print(f"批复文件: {cnt} PDFs")

# 2. Copy acceptance PDFs (top 20 largest)
src2 = r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched"
dst2 = os.path.join(BASE, "05_样本链_受理公告_终稿_批复_修改意见", "受理公告_样本")
if os.path.exists(src2):
    os.makedirs(dst2, exist_ok=True)
    pdfs = [(f, os.path.getsize(os.path.join(src2, f))) for f in os.listdir(src2) if f.endswith('.pdf')]
    pdfs.sort(key=lambda x: -x[1])
    for fname, sz in pdfs[:20]:
        shutil.copy2(os.path.join(src2, fname), os.path.join(dst2, fname))
    print(f"受理公告样本: {min(20,len(pdfs))} PDFs")

# 3. Copy standard clause library
src3 = r"E:\软件\openclaw_workspace\updated_standard_clause_library.jsonl"
dst3 = os.path.join(BASE, "03_指南解析_明文标准库", "updated_standard_clause_library.jsonl")
if os.path.exists(src3):
    shutil.copy2(src3, dst3)
    print("标准条款库: OK")

# 4. Copy data inventory
src4 = r"E:\软件\openclaw_workspace\data_inventory.csv"
dst4 = os.path.join(BASE, "99_原始文件路径索引", "data_inventory.csv")
if os.path.exists(src4):
    shutil.copy2(src4, dst4)

# Summary
total = 0
total_size = 0
for root, dirs, files in os.walk(BASE):
    for f in files:
        fp = os.path.join(root, f)
        total += 1
        total_size += os.path.getsize(fp)

print(f"\nPack total: {total} files, {total_size/1024/1024:.1f} MB")

# Show structure
print("\n=== 文件结构 ===")
for root, dirs, files in os.walk(BASE):
    level = root.replace(BASE, "").count(os.sep)
    if level <= 3:
        indent = "  " * level
        folder = os.path.basename(root)
        if files:
            print(f"{indent}{folder}/ ({len(files)} files)")
            for f in sorted(files)[:5]:
                sz = os.path.getsize(os.path.join(root, f))
                print(f"{indent}  [{f.rsplit('.',1)[-1]}] {f[:70]} ({sz:,}b)")
