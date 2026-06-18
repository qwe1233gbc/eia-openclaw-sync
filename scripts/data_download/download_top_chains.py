import dmPython, requests, urllib3, os, re, json, shutil
urllib3.disable_warnings()

conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
c = conn.cursor()
BASE_URL = 'http://10.8.0.152:8082/'
dst = r'E:\软件\eia_plastic_guide_research_pack\05_样本链_受理公告_终稿_批复_修改意见\完整样本链_已下载'

targets = [
    ('金来塑料', '金来'),
    ('容桂木森新材料', '木森'),
    ('水性涂料', '水性涂料'),
    ('盈山包装', '盈山'),
    ('广辰伟业新材料', '广辰伟业'),
    ('利兴塑料包装', '利兴'),
]

downloaded_total = 0
chains = []

for comp_name, comp_core in targets:
    c.execute("SELECT u.unique_id, u.name FROM hycx_hb.hp_apply_unit u WHERE u.name LIKE '%" + comp_core[:4] + "%' AND rownum <= 5")
    units = c.fetchall()

    for unit in units:
        uid = str(unit[0])
        uname = str(unit[1])

        c.execute("SELECT sp_id FROM hycx_hb.hp_main_info WHERE apply_unit_id = '" + uid + "' AND rownum <= 1")
        sp = c.fetchone()
        if not sp: continue
        sp_id = str(sp[0])

        c.execute("SELECT file_type, file_name, file_path_zh FROM hycx_hb.hp_file WHERE business_id LIKE '%" + sp_id + "%' AND file_name IS NOT NULL AND LENGTH(file_name) > 3")
        db_files = c.fetchall()

        proj = [f for f in db_files if str(f[0]) == 'proj_file']
        tech = [f for f in db_files if str(f[0]) == 'hp_tech_file']
        pf = [f for f in db_files if str(f[0]) == 'hp_pf_file']

        if not pf: continue

        safe_name = uname[:30].replace('/', '_').replace('\\', '_')
        proj_dir = os.path.join(dst, safe_name)
        os.makedirs(proj_dir, exist_ok=True)

        dl = 0
        for f in proj[:3] + pf[:2]:
            ftype = str(f[0])
            fpath_zh = str(f[2]) if f[2] else ''
            if not fpath_zh: continue

            relative = fpath_zh.replace('\\', '/').lstrip('../').lstrip('./')
            url = BASE_URL + relative
            fname = str(f[1])[:80].replace('/', '_').replace('\\', '_')

            dst_file = os.path.join(proj_dir, '[' + ftype + ']_' + fname)
            if os.path.exists(dst_file) and os.path.getsize(dst_file) > 1000: continue

            try:
                resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30, verify=False)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(dst_file, 'wb') as fout:
                        fout.write(resp.content)
                    dl += 1
                    print('  DL: ' + fname[:60] + ' (' + str(len(resp.content)) + 'b)')
            except Exception as e:
                print('  ERR: ' + fname[:40] + ': ' + str(e))

        downloaded_total += dl
        grade = (1 if proj else 0) + (1 if tech else 0) + (1 if pf else 0)

        print('[' + str(grade) + '环|' + str(dl) + '下载] ' + uname[:50])
        for pf_file in pf[:2]:
            print('  批复: ' + str(pf_file[1])[:100])
        print()
        chains.append({'company': uname[:50], 'grade': grade, 'proj': len(proj), 'tech': len(tech), 'pf': len(pf), 'dl': dl})
        break

print('\nTotal downloaded: ' + str(downloaded_total) + ' files')
for g in [1, 2, 3]:
    cnt = sum(1 for c in chains if c['grade'] == g)
    print('  ' + str(g) + '环链: ' + str(cnt))

c.close()
conn.close()
