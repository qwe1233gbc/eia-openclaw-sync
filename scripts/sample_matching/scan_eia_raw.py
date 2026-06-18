import os

root = r"E:\软件\环评原始数据"

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
    level = dirpath.replace(root, '').count(os.sep)

    if level <= 3 and filenames:
        exts = {}
        for f in filenames:
            ext = f.rsplit('.', 1)[-1] if '.' in f else 'no_ext'
            exts[ext] = exts.get(ext, 0) + 1
        rel = dirpath[len(root)+1:]
        total = sum(exts.values())
        top5 = sorted(exts.items(), key=lambda x: -x[1])[:5]
        ext_str = ' | '.join(f"{e}:{c}" for e,c in top5)
        print(f"{rel}/  [{total} files] {ext_str}")

        # Show sample filenames
        for f in sorted(filenames)[:3]:
            print(f"    - {f[:100]}")

    if level > 3:
        break
