import os, csv, dmPython, re

# Read the existing CSV
csv_path = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\plastic_project_chain_v1.csv"
rows = []
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Disk PDF directories
disk_dirs = {
    'approval': r"E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic",
    'acceptance': r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched",
}
# Also check the raw data dirs
raw_dirs = [
    r"E:\软件\环评原始数据\顺德顺德",
    r"E:\软件\环评原始数据\顺德区受理报告",
]

# Build disk filename index
disk_index = {}
for label, ddir in disk_dirs.items():
    if os.path.exists(ddir):
        for f in os.listdir(ddir):
            if f.endswith('.pdf'):
                disk_index[f] = {'dir': label, 'path': os.path.join(ddir, f)}
for ddir in raw_dirs:
    if os.path.exists(ddir):
        for f in os.listdir(ddir):
            if f.endswith('.pdf'):
                disk_index[f] = {'dir': 'raw', 'path': os.path.join(ddir, f)}

print(f"Disk PDF index: {len(disk_index)} files")

conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
c = conn.cursor()

updated = 0
for row in rows:
    if row['sample_grade'] not in ['A', 'B']:
        continue
    if row['disk_approval_match'] == 'Y':
        continue  # Already matched

    sp_id = row['db_sp_id']
    if not sp_id or len(sp_id) < 5:
        continue

    # Get ALL file names for this sp_id
    try:
        c.execute("SELECT file_name, file_type, file_path_zh FROM hycx_hb.hp_file WHERE business_id LIKE '%" + sp_id + "%' AND file_name IS NOT NULL AND LENGTH(file_name) > 3")
        db_files = c.fetchall()
    except:
        continue

    if not db_files:
        continue

    approval_matches = []
    acceptance_matches = []
    all_matches = []

    for fname, ftype, fpath in db_files:
        fname_str = str(fname) if fname else ''
        # Try to match against disk PDFs
        # Strategy 1: exact filename match
        if fname_str in disk_index:
            all_matches.append((fname_str, disk_index[fname_str]['dir'], ftype))
            continue

        # Strategy 2: extract core keywords from DB filename and search disk
        core_from_db = fname_str[:30]
        if len(core_from_db) < 5:
            continue

        for disk_name, disk_info in disk_index.items():
            if core_from_db[:15] in disk_name or disk_name[:15] in core_from_db:
                all_matches.append((disk_name, disk_info['dir'], ftype))
                if disk_info['dir'] == 'approval':
                    approval_matches.append(disk_name)
                elif disk_info['dir'] == 'acceptance':
                    acceptance_matches.append(disk_name)
                break

    # Update row
    if approval_matches:
        row['disk_approval_match'] = 'Y'
        row['confidence_score'] = str(int(row['confidence_score']) + 1)
    if acceptance_matches:
        row['disk_acceptance_match'] = 'Y'

    updated += 1
    if all_matches:
        print(f"[{row['company_core'][:15]}] {len(all_matches)} disk matches: {all_matches[0][1]}/{all_matches[0][0][:60]}")

c.close()
conn.close()

# Save updated CSV
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    headers = rows[0].keys()
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row[h] for h in headers])

# Summary
a_count = sum(1 for r in rows if r['sample_grade'] == 'A')
a_full = sum(1 for r in rows if r['sample_grade'] == 'A' and r['confidence_score'] == '4')
print(f"\nUpdated: {updated} rows")
print(f"A-grade with full chain (C4): {a_full}/{a_count}")
print(f"Saved: {csv_path}")
