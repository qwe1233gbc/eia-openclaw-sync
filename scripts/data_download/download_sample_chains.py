import dmPython, requests, urllib3, os, re, json, shutil
urllib3.disable_warnings()

conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
c = conn.cursor()
BASE_URL = 'http://10.8.0.152:8082/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Plastic keywords
PLASTIC_KW = ['塑胶','塑料','注塑','涂装','涂料','包装','印刷','复合','薄膜','新材料','树脂','胶粘','胶水','涂布','淋膜','贴合','熟化']

# Load already-matched approval files from disk
fin_dir = r'E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic'
fin_files = [f for f in os.listdir(fin_dir) if f.endswith('.pdf')]

# Filter: only plastic-related approval files
plastic_approvals = []
for fname in fin_files:
    score = sum(1 for kw in PLASTIC_KW if kw in fname)
    if score >= 1:
        plastic_approvals.append(fname)

print(f'Plastic-related approvals on disk: {len(plastic_approvals)}/{len(fin_files)}')
print()

# For each plastic approval, trace full chain through DB
dst = r'E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\完整样本链_已下载'
os.makedirs(dst, exist_ok=True)

chains = []
downloaded_count = 0

for fname in plastic_approvals[:30]:  # Process top 30
    # Extract company from filename
    m = re.search(r'关于(.+?)(?:新建|扩建|迁建|改建|项目)', fname)
    if not m: continue
    company_hint = m.group(1)[:12]
    if len(company_hint) < 4: continue

    # Step 1: Find company in DB
    try:
        c.execute(f"SELECT unique_id, name FROM hycx_hb.hp_apply_unit WHERE name LIKE '%{company_hint[:6]}%' AND rownum <= 3")
        units = c.fetchall()
    except: continue

    for unit in units:
        uid = str(unit[0])
        uname = str(unit[1])

        # Step 2: Get sp_id
        c.execute(f"SELECT sp_id FROM hycx_hb.hp_main_info WHERE apply_unit_id = '{uid}' AND rownum <= 1")
        sp = c.fetchone()
        if not sp: continue
        sp_id = str(sp[0])

        # Step 3: Get ALL files for this sp_id
        c.execute(f"SELECT file_type, file_name, file_path_zh FROM hycx_hb.hp_file WHERE business_id LIKE '%{sp_id}%' AND file_name IS NOT NULL AND LENGTH(file_name) > 3")
        db_files = c.fetchall()

        proj_files = [f for f in db_files if str(f[0]) == 'proj_file']
        tech_files = [f for f in db_files if str(f[0]) == 'hp_tech_file']
        pf_files = [f for f in db_files if str(f[0]) == 'hp_pf_file']

        has_proj = len(proj_files) > 0
        has_tech = len(tech_files) > 0
        has_pf = len(pf_files) > 0

        if not has_pf: continue  # Must have approval

        # Step 4: Check if plastic-related
        all_text = ' '.join([str(f[1]) for f in db_files])
        plastic_score = sum(1 for kw in PLASTIC_KW if kw in all_text)
        is_plastic = plastic_score >= 1

        if not is_plastic: continue

        # Step 5: Check disk approval match
        disk_approval = fname
        disk_approval_path = os.path.join(fin_dir, fname)

        # Step 6: Build chain info
        chain_links = []
        if has_proj: chain_links.append('report')
        if has_tech: chain_links.append('tech_review')
        if has_pf: chain_links.append('approval')
        chain_grade = len(chain_links)

        # Step 7: Download files from server
        proj_dir = os.path.join(dst, uname[:40].replace('/', '_'))
        os.makedirs(proj_dir, exist_ok=True)

        # Copy the approval from disk
        dst_approval = os.path.join(proj_dir, fname)
        if not os.path.exists(dst_approval):
            shutil.copy2(disk_approval_path, dst_approval)

        # Download report files from server
        downloaded = 0
        for f in proj_files[:3] + pf_files[:2]:
            ftype = str(f[0])
            fpath_zh = str(f[2]) if f[2] else ''
            if not fpath_zh: continue

            relative = fpath_zh.replace('\\', '/').lstrip('../').lstrip('./')
            url = BASE_URL + relative
            fname_clean = str(f[1])[:100].replace('/', '_').replace('\\', '_')

            dst_file = os.path.join(proj_dir, f'[{ftype}]_{fname_clean}')
            if os.path.exists(dst_file): continue

            try:
                resp = requests.get(url, headers=HEADERS, timeout=30, verify=False)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(dst_file, 'wb') as fout:
                        fout.write(resp.content)
                    downloaded += 1
            except:
                pass

        downloaded_count += downloaded

        chain_info = {
            'company': uname[:60],
            'sp_id': sp_id[:40],
            'approval_file': fname[:80],
            'chain_links': '+'.join(chain_links),
            'chain_grade': chain_grade,
            'plastic_score': plastic_score,
            'proj_files': len(proj_files),
            'tech_files': len(tech_files),
            'pf_files': len(pf_files),
            'downloaded': downloaded,
        }
        chains.append(chain_info)

        print(f'[{chain_grade}环] {uname[:40]}')
        print(f'  链: {chain_links}')
        print(f'  文件: proj={len(proj_files)} tech={len(tech_files)} pf={len(pf_files)}')
        print(f'  下载: {downloaded} files')
        if pf_files:
            print(f'  批复: {str(pf_files[0][1])[:80]}')
        print()

        break  # One match per company

    if len(chains) >= 15:
        break

# Save manifest
with open(os.path.join(dst, 'chains_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(chains, f, ensure_ascii=False, indent=2)

# Summary
print(f'=== SUMMARY ===')
print(f'Total chains: {len(chains)}')
for g in range(1, 4):
    cnt = sum(1 for c in chains if c['chain_grade'] == g)
    print(f'  {g}环链: {cnt}')
print(f'Downloads: {downloaded_count} files')
print(f'Saved to: {dst}')

c.close()
conn.close()
