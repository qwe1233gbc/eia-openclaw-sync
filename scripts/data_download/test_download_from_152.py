import dmPython, requests, urllib3, os
urllib3.disable_warnings()

conn = dmPython.connect(server='172.16.168.163', port=5236, user='SYSDBA', password='SYSDBA001', autoCommit=True)
c = conn.cursor()

# Get plastic project files with file_path_zh
c.execute("SELECT file_name, file_path_zh, file_type FROM hycx_hb.hp_file WHERE file_name LIKE '%金亮塑胶%' AND file_path_zh IS NOT NULL AND LENGTH(file_path_zh) > 5 AND rownum <= 5")
rows = c.fetchall()

if not rows:
    c.execute("SELECT file_name, file_path_zh, file_type FROM hycx_hb.hp_file WHERE file_name LIKE '%塑胶%' AND file_path_zh IS NOT NULL AND LENGTH(file_path_zh) > 5 AND rownum <= 5")
    rows = c.fetchall()

print(f'Found {len(rows)} files')
base_url = 'http://10.8.0.152:8082/'

for r in rows:
    fname = str(r[0])[:80]
    fpath = str(r[1])
    ftype = str(r[2])
    print(f'[{ftype}] {fname}')
    print(f'  path: {fpath}')

    # Build URL
    relative = fpath.replace('\\', '/')
    relative = relative.lstrip('../').lstrip('./')
    url = base_url + relative
    print(f'  URL: {url}')

    try:
        resp = requests.get(url, timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200 and len(resp.content) > 1000:
            dst = r'E:\\软件\\test_download.pdf'
            with open(dst, 'wb') as f:
                f.write(resp.content)
            print(f'  SUCCESS: {len(resp.content):,} bytes')
            break
        else:
            print(f'  HTTP {resp.status_code}, size={len(resp.content)}')
    except Exception as e:
        print(f'  ERR: {e}')
    print()

c.close()
conn.close()
