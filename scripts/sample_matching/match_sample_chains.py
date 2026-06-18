import dmPython, json, os, re, csv
from PyPDF2 import PdfReader

# ====== SOURCE 1: 91 acceptance PDFs ======
pdf_dir = r"E:\软件\openclaw_workspace\knowledge\reports\plastic_industry_matched"
acceptance = []
for fname in os.listdir(pdf_dir):
    if not fname.endswith('.pdf'): continue
    path = os.path.join(pdf_dir, fname)
    try:
        reader = PdfReader(path)
        text = ''
        for page in reader.pages[:2]:
            text += page.extract_text() or ''
        company = ''
        project = ''
        m = re.search(r'(?:建设单位|申请单位)[：:\s]+(.{4,40}?)(?:有限公司|有限责任公司)', text)
        if m: company = m.group(0).replace('建设单位：','').replace('建设单位:','').strip()[:40]
        m = re.search(r'项目名称[：:\s]+(.{5,60})', text)
        if m: project = m.group(1).strip()[:60]
        if company:
            acceptance.append({'company': company, 'project': project, 'file': fname[:60]})
    except: pass

print(f'Acceptance PDFs with company names: {len(acceptance)}')

# ====== SOURCE 2: 12 final approvals ======
final_dir = r"E:\软件\openclaw_workspace\knowledge\reports\final_approvals_plastic"
finals = []
for fname in os.listdir(final_dir):
    if not fname.endswith('.pdf'): continue
    path = os.path.join(final_dir, fname)
    try:
        reader = PdfReader(path)
        text = ''
        for page in reader.pages[:2]:
            text += page.extract_text() or ''
        company = ''
        doc_num = ''
        m = re.search(r'(?:建设单位|申请单位)[：:\s]+(.{4,40}?)(?:有限公司|有限责任公司)', text)
        if m: company = m.group(0).replace('建设单位：','').replace('建设单位:','').strip()[:40]
        m = re.search(r'[\[（]?\d{4}[\]）]?\S{0,5}号', fname)
        if m: doc_num = m.group(0)
        m = re.search(r'(20\d{2})', fname)
        year = m.group(1) if m else ''
        # Fallback: extract from fname itself
        if not company:
            m2 = re.search(r'关于(.+?)(?:新建|扩建|迁建|改建|项目)', fname)
            if m2: company = m2.group(1)[:40]
        if company:
            finals.append({'company': company, 'doc_num': doc_num, 'year': year, 'file': fname[:60]})
    except: pass

print(f'Final approvals with company names: {len(finals)}')

# ====== SOURCE 3: 30 ai_package ======
ai_dir = r"E:\openclaw_archive\workspace\agent\workspace\ai_packages_extracted\ai_packages"
comments_data = []
for proj_dir in os.listdir(ai_dir):
    if not os.path.isdir(os.path.join(ai_dir, proj_dir)): continue
    if proj_dir.startswith('原始') or proj_dir == 'data': continue
    manifest_path = os.path.join(ai_dir, proj_dir, 'manifest.json')
    company = ''
    project = proj_dir
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            company = str(manifest.get('company', manifest.get('apply_unit', '')))[:40]
        except: pass
    comments_path = os.path.join(ai_dir, proj_dir, 'comments.jsonl')
    has_comments = os.path.exists(comments_path) and os.path.getsize(comments_path) > 100
    body_path = os.path.join(ai_dir, proj_dir, 'body.md')
    has_body = os.path.exists(body_path) and os.path.getsize(body_path) > 1000
    comments_data.append({
        'company': company, 'project': project[:60],
        'has_comments': has_comments, 'has_body': has_body
    })

print(f'Ai_package projects: {len(comments_data)}')

# ====== SOURCE 4: Database ======
conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
cursor = conn.cursor()

db_projects = []
plastic_kw_list = ['塑胶','塑料','注塑','涂装','涂料','包装','印刷','复合','薄膜','新材料','树脂']
for kw in plastic_kw_list[:6]:
    try:
        cursor.execute("SELECT DISTINCT f.business_id, f.file_name, f.file_type FROM hycx_hb.hp_file f WHERE f.file_name LIKE '%" + kw + "%' AND f.file_type = 'hp_pf_file' AND rownum <= 20")
        for r in cursor.fetchall():
            db_projects.append({'business_id': r[0] if r[0] else '', 'file_name': str(r[1])[:80], 'file_type': str(r[2])})
    except: pass

cursor.close()
conn.close()

print(f'DB approval files: {len(db_projects)}')

# ====== MATCHING ======
glue_kw = ['胶','复合','涂','贴合','熟化','印刷','涂布','淋膜','覆膜','流延']
all_entries = []

# Process each source into normalized entries
for a in acceptance:
    glue_score = sum(1 for kw in glue_kw if kw in a.get('project','') or kw in a.get('company',''))
    all_entries.append({
        'company_key': a['company'][:8].strip(),
        'project': a['project'][:60],
        'doc_num': '',
        'year': '',
        'source_type': 'acceptance',
        'is_glue': glue_score > 0,
        'file': a['file'][:60]
    })

for f in finals:
    glue_score = sum(1 for kw in glue_kw if kw in f.get('file','') or kw in f.get('company',''))
    all_entries.append({
        'company_key': f['company'][:8].strip(),
        'project': f['company'][:60],
        'doc_num': f['doc_num'],
        'year': f['year'],
        'source_type': 'final_approval',
        'is_glue': glue_score > 0,
        'file': f['file'][:60]
    })

for c in comments_data:
    glue_score = sum(1 for kw in glue_kw if kw in c.get('project','') or kw in c.get('company',''))
    all_entries.append({
        'company_key': c['company'][:8].strip() if c['company'] else c['project'][:8],
        'project': c['project'][:60],
        'doc_num': '',
        'year': '',
        'source_type': 'ai_package',
        'is_glue': glue_score > 0,
        'has_comments': c['has_comments'],
        'file': c['project'][:60]
    })

for d in db_projects:
    glue_score = sum(1 for kw in glue_kw if kw in str(d.get('file_name','')))
    all_entries.append({
        'company_key': str(d.get('file_name',''))[:12].strip(),
        'project': str(d.get('file_name',''))[:60],
        'doc_num': '',
        'year': '',
        'source_type': 'database',
        'is_glue': glue_score > 0,
        'file': str(d.get('file_name',''))[:60]
    })

# Group by company_key
from collections import defaultdict
groups = defaultdict(list)
for e in all_entries:
    key = e['company_key']
    if len(key) >= 4:
        groups[key].append(e)

# Build match table
matches = []
for key, entries in groups.items():
    source_types = set(e['source_type'] for e in entries)
    is_glue = any(e.get('is_glue', False) for e in entries)

    # Get best project name
    project_names = [e['project'] for e in entries if e['project'] and len(e['project'])>3]
    best_name = project_names[0] if project_names else key

    # Get doc info
    doc_nums = [e['doc_num'] for e in entries if e.get('doc_num')]
    years = [e['year'] for e in entries if e.get('year')]

    # Count
    has_acc = 'acceptance' in source_types
    has_fin = 'final_approval' in source_types
    has_com = any(e.get('has_comments', False) for e in entries if e['source_type']=='ai_package')
    has_db = 'database' in source_types
    chain = sum([has_acc, has_fin, has_com, has_db])

    # Grade
    if chain >= 4: grade = 'S'
    elif chain >= 3: grade = 'A'
    elif chain >= 2: grade = 'B'
    else: grade = 'C'

    # Downgrade if not glue-related
    if not is_glue and grade in ['S','A']: grade = 'B'
    if chain == 1 and not is_glue: grade = 'D'

    # Use
    if is_glue and grade in ['S','A']: use = 'mvp_benchmark'
    elif is_glue and grade == 'B': use = 'experience_source'
    elif not is_glue and grade in ['S','A']: use = 'reference_only'
    elif has_fin: use = 'approval_alignment'
    else: use = 'discard'

    matches.append({
        'company_key': key[:30],
        'project': best_name[:80],
        'doc_num': ', '.join(doc_nums[:2]),
        'year': ', '.join(years[:2]),
        'is_plastic_guide_applicable': 'Y' if is_glue else 'PARTIAL',
        'is_glue_or_composite': 'Y' if is_glue else 'N',
        'has_acceptance': 'Y' if has_acc else 'N',
        'has_review_comment': 'Y' if has_com else 'N',
        'has_pre_final': 'N',
        'has_final_approval': 'Y' if has_fin else 'N',
        'has_db_chain': 'Y' if has_db else 'N',
        'sample_grade': grade,
        'recommended_use': use,
        'match_sources': '+'.join(sorted(source_types)),
        'notes': ''
    })

matches.sort(key=lambda x: ['S','A','B','C','D'].index(x['sample_grade']))

print(f'\nTotal: {len(matches)} matched projects')
for g in ['S','A','B','C','D']:
    cnt = sum(1 for m in matches if m['sample_grade']==g)
    glue_cnt = sum(1 for m in matches if m['sample_grade']==g and m['is_glue_or_composite']=='Y')
    print(f'  {g}-grade: {cnt} ({glue_cnt} glue-related)')

# Save
csv_path = r"E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\plastic_project_sample_chain_matching_v1.csv"
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['project_id','company_name','project_name','doc_num','year',
                'is_plastic_guide_applicable','is_glue_or_composite',
                'has_acceptance_announcement','has_review_comment','has_pre_final_report',
                'has_final_approval','has_database_complete_chain',
                'sample_grade','recommended_use','match_sources','notes'])
    for i, m in enumerate(matches, 1):
        w.writerow([f'MATCH_{i:03d}', m['company_key'], m['project'][:80], m['doc_num'], m['year'],
                    m['is_plastic_guide_applicable'], m['is_glue_or_composite'],
                    m['has_acceptance'], m['has_review_comment'], m['has_pre_final'],
                    m['has_final_approval'], m['has_db_chain'],
                    m['sample_grade'], m['recommended_use'], m['match_sources'], m['notes']])

print(f'\nSaved: {csv_path}')
print(f'Rows: {len(matches)}')
