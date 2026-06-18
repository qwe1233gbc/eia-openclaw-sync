import os, re, shutil

# Find the correct directory
root_options = [
    r"E:\软件\环评原始数据\顺德区受理报告",
    r"E:\软件\环评原始数据\顺德非顺德",
    r"E:\软件\环评原始数据\顺德顺德",
]
root = None
for r in root_options:
    if os.path.exists(r):
        root = r
        print(f"Found: {r}")
        break

if not root:
    print("No directory found!")
    exit()

files = sorted(os.listdir(root))

# Keywords for plastic/rubber/coating/packaging/printing
# Matching the scope of the Foshan plastic industry guide (C292, glue-related, composite, coating)
plastic_kw = [
    '塑料', '塑胶', '注塑', '橡胶', '包装', '涂料', '涂装', '新材料',
    '合成', '树脂', '化工', '印刷', '复合', '薄膜', '胶粘', '胶水',
    '发泡', '挤塑', '吹塑', '模塑', '弹性体', '聚氨酯', '聚氯乙烯',
    'PVC', 'PE', 'PP', 'ABS', 'EVA', '制罐', '制袋', '标签'
]

found = []
for f in files:
    if not f.endswith('.pdf'):
        continue
    score = sum(1 for kw in plastic_kw if kw.lower() in f.lower())
    if score > 0:
        size = os.path.getsize(os.path.join(root, f))
        found.append((score, f, size))

found.sort(key=lambda x: -x[0])

print(f"\nTotal PDFs: {len(files)}")
print(f"Plastic/rubber/coating industry matches: {len(found)}")

# Print top matches
print(f"\n=== Top matches (score >= 2) ===\n")
high = [(s, f, sz) for s, f, sz in found if s >= 2]
print(f"High confidence: {len(high)} reports\n")
for score, fname, size in high:
    print(f"[{score}] {fname[:150]} ({size/1024/1024:.1f}MB)")

# Print all matches
print(f"\n=== All matches ===\n")
for score, fname, size in found:
    print(f"[{score}] {fname[:150]} ({size/1024/1024:.1f}MB)")

# Copy high-confidence matches to target folder
dst = r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched"
os.makedirs(dst, exist_ok=True)
copied = 0
for score, fname, size in high:
    src = os.path.join(root, fname)
    dst_path = os.path.join(dst, fname)
    if not os.path.exists(dst_path):
        shutil.copy2(src, dst_path)
        copied += 1

print(f"\nCopied {copied} high-confidence reports to: {dst}")
