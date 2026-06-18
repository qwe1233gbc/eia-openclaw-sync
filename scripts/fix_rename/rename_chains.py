import os, json

dst = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\完整样本链_已下载"

# Load manifest
manifest_path = os.path.join(dst, "chains_manifest.json")
chain_info = {}
if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
        for c in json.load(f):
            chain_info[c["company"][:30]] = c

for d in sorted(os.listdir(dst)):
    dpath = os.path.join(dst, d)
    if not os.path.isdir(dpath):
        continue

    files = [f for f in os.listdir(dpath) if not f.startswith(".")]
    if not files:
        os.rmdir(dpath)
        print("DEL empty: " + d[:50])
        continue

    # Find matching chain info
    info = None
    for key, val in chain_info.items():
        if key[:8] in d:
            info = val
            break

    if not info:
        # Not in manifest, keep but mark
        new_name = "[?环] " + d[:60].replace("/", "_")
        new_path = os.path.join(dst, new_name)
        if new_path != dpath:
            os.rename(dpath, new_path)
            print("MARK: " + new_name[:80])
        continue
    grade = str(info["chain_grade"])
    has_tech = "_有审查" if info["tech_files"] > 0 else ""
    new_name = "[" + grade + "环" + has_tech + "] " + d[:60].replace("/", "_").replace("\\", "_")
    new_path = os.path.join(dst, new_name)

    if new_path != dpath:
        os.rename(dpath, new_path)
        print("OK: " + new_name[:80])

# Rename parent
parent = os.path.dirname(dst)
new_parent = os.path.join(parent, "样本链_已下载")
os.rename(dst, new_parent)
print("\nParent: 完整样本链_已下载 -> 样本链_已下载")

# Final listing
print("\n=== 最终结构 ===")
for d in sorted(os.listdir(new_parent)):
    dpath = os.path.join(new_parent, d)
    if os.path.isdir(dpath):
        files = [f for f in os.listdir(dpath) if not f.startswith(".")]
        print(d[:70] + " (" + str(len(files)) + " files)")
