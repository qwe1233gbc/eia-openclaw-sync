import os, re
from PyPDF2 import PdfReader

root = r"E:\软件\环评原始数据"
dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]

# Find the one with most files (should be 顺德顺德 with 3194)
target_dir = None
max_files = 0
for d in dirs:
    dpath = os.path.join(root, d)
    pdf_count = len([f for f in os.listdir(dpath) if f.endswith('.pdf')])
    print(f"{d}: {pdf_count} PDFs")
    if pdf_count > max_files:
        max_files = pdf_count
        target_dir = dpath

print(f"\nTarget: {target_dir}")

# Sample 3 files
files = sorted([f for f in os.listdir(target_dir) if f.endswith('.pdf')])
for fname in files[:5]:
    path = os.path.join(target_dir, fname)
    try:
        reader = PdfReader(path)
        text = ''
        for page in reader.pages[:1]:
            text += page.extract_text() or ''
        clean = re.sub(r'\s+', ' ', text)[:400]
        print(f'\n=== {fname[:60]} ===')
        print(clean)
    except Exception as e:
        print(f'ERR: {fname[:40]} - {e}')

# Now search for plastic industry in this directory
print(f'\n\n=== Searching for plastic industry 批复 ===')
plastic_kw = ['塑胶','塑料','注塑','挤塑','吹塑','发泡','涂装','涂料','油墨',
              '胶粘','胶水','复合','贴合','印刷','包装','薄膜','新材料','树脂']
found = 0
for fname in files:
    path = os.path.join(target_dir, fname)
    try:
        reader = PdfReader(path)
        text = ''
        for page in reader.pages[:2]:
            text += page.extract_text() or ''
        score = sum(1 for kw in plastic_kw if kw in text)
        if score >= 2:
            # Extract document number
            doc_num = ''
            m = re.search(r'(?:顺管|环|佛环)[^号]*号', text)
            if m: doc_num = m.group(0)
            print(f'[{score}] {fname[:80]} | {doc_num}')
            found += 1
    except:
        pass

print(f'\nPlastic industry 批复 total: {found}')
