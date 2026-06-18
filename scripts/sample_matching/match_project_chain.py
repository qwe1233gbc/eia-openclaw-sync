import os, re, json, csv, dmPython

ai_dir = r"E:\openclaw_archive\workspace\agent\workspace\ai_packages_extracted\ai_packages"
conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
c = conn.cursor()

results = []

for proj in sorted(os.listdir(ai_dir)):
    pdir = os.path.join(ai_dir, proj)
    if not os.path.isdir(pdir) or proj.startswith('原始') or proj == 'data':
        continue

    # === STEP 1: Extract company name ===
    # Method A: From folder name (most reliable - contains full company name)
    # Pattern: "YYYYMMDDHHMMSSSSSS公司名项目类型"
    company_folder = ''
    m = re.search(r'\d{15,20}(.+?)(?:新建|扩建|迁建|改建|搬迁|修改|建设项目)', proj)
    if not m:
        # Try without date prefix
        m = re.search(r'^(.+?)(?:新建|扩建|迁建|改建|搬迁|修改)', proj)
    if m:
        company_folder = m.group(1).strip().rstrip('（').rstrip('(')
    if not company_folder:
        company_folder = proj[:30]

    # Method B: From manifest.json
    company_manifest = ''
    industry_manifest = ''
    mf_path = os.path.join(pdir, 'manifest.json')
    if os.path.exists(mf_path):
        with open(mf_path, 'r', encoding='utf-8') as f:
            mf = json.load(f)
        company_manifest = str(mf.get('apply_unit', mf.get('company', '')))[:60]
        industry_manifest = str(mf.get('industry_code', mf.get('industry', '')))[:20]

    # Use folder name as primary, manifest as secondary
    company_name = company_folder if len(company_folder) > 4 else company_manifest

    # === STEP 2: Check for body.md and comments ===
    body_path = os.path.join(pdir, 'body.md')
    comments_path = os.path.join(pdir, 'comments.jsonl')
    has_body = os.path.exists(body_path) and os.path.getsize(body_path) > 1000
    has_comments = os.path.exists(comments_path) and os.path.getsize(comments_path) > 100

    # Read body for glue keywords
    glue_kw = ['胶水','胶粘剂','涂胶','贴合','复合','熟化','涂布','淋膜','干法复合','湿法复合']
    is_glue = False
    glue_hits = {}
    if has_body:
        with open(body_path, 'r', encoding='utf-8') as f:
            body = f.read()
        for kw in glue_kw:
            cnt = body.count(kw)
            if cnt > 0:
                glue_hits[kw] = cnt
                if kw in ['胶水','胶粘剂','涂胶','贴合','复合','熟化','淋膜','干法复合'] and cnt >= 2:
                    is_glue = True

    # === STEP 3: Match in database ===
    # Extract core company name for DB search
    company_core = company_name
    for prefix in ['佛山市','顺德区','广东','佛山','顺德']:
        company_core = company_core.replace(prefix, '', 1)
    company_core = company_core.strip()[:10]

    db_unit_id = ''
    db_unit_name = ''
    db_sp_id = ''
    db_file_count = 0
    db_approval_count = 0
    db_tech_count = 0
    confidence = 0

    if len(company_core) >= 4:
        try:
            c.execute("SELECT id, unique_id, name FROM hycx_hb.hp_apply_unit WHERE name LIKE '%" + company_core[:6] + "%'")
            units = c.fetchall()

            # Find best match: name must contain the core
            best_unit = None
            for u in units:
                if company_core[:6] in str(u[2]):
                    # Check if this unit has actual projects
                    c.execute("SELECT COUNT(*) FROM hycx_hb.hp_main_info WHERE apply_unit_id = '" + str(u[1]) + "'")
                    if c.fetchone()[0] > 0:
                        best_unit = (u[0], u[1], u[2])
                        break

            if best_unit:
                db_unit_id = best_unit[1]
                db_unit_name = str(best_unit[2])[:80]
                confidence += 1

                # Find sp_id
                c.execute("SELECT sp_id FROM hycx_hb.hp_main_info WHERE apply_unit_id = '" + db_unit_id + "' AND rownum <= 3")
                sp_rows = c.fetchall()
                if sp_rows:
                    db_sp_id = str(sp_rows[0][0])[:50]
                    confidence += 1

                    # Count files
                    c.execute("SELECT COUNT(*), SUM(CASE WHEN file_type='hp_pf_file' THEN 1 ELSE 0 END), SUM(CASE WHEN file_type='hp_tech_file' THEN 1 ELSE 0 END) FROM hycx_hb.hp_file WHERE business_id LIKE '%" + db_sp_id + "%'")
                    row = c.fetchone()
                    if row:
                        db_file_count = row[0] or 0
                        db_approval_count = row[1] or 0
                        db_tech_count = row[2] or 0
                        if db_file_count > 0:
                            confidence += 1
        except Exception as e:
            pass

    # === STEP 4: Check disk PDFs ===
    disk_approval = ''
    disk_acceptance = ''
    disk_approval_dir = r"E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic"
    disk_accept_dir = r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched"

    if len(company_core) >= 4:
        for ddir, label in [(disk_approval_dir, 'approval'), (disk_accept_dir, 'acceptance')]:
            if os.path.exists(ddir):
                matches = [f for f in os.listdir(ddir) if f.endswith('.pdf') and company_core[:4] in f]
                if matches:
                    if label == 'approval':
                        disk_approval = matches[0][:100]
                        confidence += 1
                    else:
                        disk_acceptance = matches[0][:100]

    # Limit confidence to max 4
    confidence = min(confidence, 4)

    # === STEP 5: Determine grade ===
    if is_glue and confidence >= 3:
        grade = 'A'
        use = 'mvp_benchmark'
    elif is_glue and confidence >= 2:
        grade = 'B'
        use = 'experience_source'
    elif confidence >= 2:
        grade = 'C'
        use = 'reference_only'
    else:
        grade = 'D'
        use = 'discard'

    results.append({
        'project_folder': proj[:80],
        'company_name': company_name[:60],
        'company_core': company_core,
        'industry_code': industry_manifest,
        'is_glue': 'Y' if is_glue else 'N',
        'glue_kw': ', '.join(f'{k}({v})' for k,v in sorted(glue_hits.items(), key=lambda x:-x[1])[:5]),
        'db_unit_name': db_unit_name[:60],
        'db_sp_id': db_sp_id[:50],
        'db_file_count': db_file_count,
        'db_approval_count': db_approval_count,
        'has_body_md': 'Y' if has_body else 'N',
        'has_comments': 'Y' if has_comments else 'N',
        'disk_approval_match': 'Y' if disk_approval else 'N',
        'disk_acceptance_match': 'Y' if disk_acceptance else 'N',
        'confidence_score': confidence,
        'sample_grade': grade,
        'recommended_use': use,
    })

c.close()
conn.close()

# Sort by grade then confidence
results.sort(key=lambda x: (['A','B','C','D'].index(x['sample_grade']), -x['confidence_score']))

# Save
csv_path = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\plastic_project_chain_v1.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    headers = ['project_folder','company_name','company_core','industry_code',
               'is_glue','glue_kw','db_unit_name','db_sp_id',
               'db_file_count','db_approval_count','has_body_md','has_comments',
               'disk_approval_match','disk_acceptance_match',
               'confidence_score','sample_grade','recommended_use']
    w.writerow(headers)
    for r in results:
        w.writerow([r[h] for h in headers])

# Summary
print(f'Total projects: {len(results)}')
for g in ['A','B','C','D']:
    cnt = sum(1 for r in results if r['sample_grade']==g)
    glue = sum(1 for r in results if r['sample_grade']==g and r['is_glue']=='Y')
    print(f'  {g}: {cnt} ({glue} glue)')

# Show A/B grade projects
print(f'\n=== 可用于benchmark的项目 ===')
for r in results:
    if r['sample_grade'] in ['A','B']:
        print(f"[{r['sample_grade']}|C{r['confidence_score']}] {r['company_name'][:40]}")
        print(f"  胶水: {r['is_glue']} | DB: {r['db_file_count']}文件({r['db_approval_count']}批复) | 磁盘: 批复={r['disk_approval_match']} 受理={r['disk_acceptance_match']}")

print(f'\nSaved: {csv_path}')
