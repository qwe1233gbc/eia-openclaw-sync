# -*- coding: utf-8 -*-
"""
恢复已提交但未取回的批次结果
batch_id = 515c5754-2885-4643-8be5-2d804c3fd8a6 (原token)
"""
import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8')
import requests

TOKEN = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI4MjYwODkyNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3NDY5NzE1NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTUyODAyNTkyNzYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJkOTBmY2IxMy0wNTZjLTRlNzAtODVlYS1iYjE1ODkyYzg1NzgiLCJlbWFpbCI6IiIsImV4cCI6MTc4MjQ3MzE1Nn0.6iy08CY3TL4lLccJqzfi6lM2owbXAjurC_Gi7SVW8PgyxGdfevtUCIBQnUaakO6MUejSQ6t6am3n1araO8GxNQ"
BATCH_ID = "515c5754-2885-4643-8be5-2d804c3fd8a6"
API = "https://mineru.net/api/v4"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer " + TOKEN}
OUT_DIR = r"E:\软件\mineru_parsed"
PROGRESS = r"E:\软件\mineru_progress.json"

def log(msg):
    print("[RECOVER %s] %s" % (time.strftime('%H:%M:%S'), msg), flush=True)

def download(url, filepath):
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=600, stream=True)
            resp.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(65536):
                    f.write(chunk)
            if os.path.getsize(filepath) > 1024:
                return True
            os.remove(filepath)
        except Exception as e:
            log("  DL error: " + str(e))
            time.sleep(15)
    return False

log("Checking batch %s ..." % BATCH_ID)
resp = requests.get(API + "/extract-results/batch/" + BATCH_ID, headers=HEADERS, timeout=30)
data = resp.json()
items = data.get("data", {}).get("extract_result", [])
log("Items: %d" % len(items))

done_names = []
fail_names = []
for item in items:
    fn = item.get('file_name', 'unknown')
    st = item.get('state', 'unknown')
    log("  %s: state=%s" % (fn[:55], st))
    if st == 'done':
        zu = item.get('full_zip_url', '')
        if zu:
            zn = os.path.splitext(fn)[0] + '_mineru.zip'
            zp = os.path.join(OUT_DIR, zn)
            if os.path.exists(zp):
                log("    already downloaded, skip")
                done_names.append(fn)
                continue
            log("    downloading...")
            if download(zu, zp):
                done_names.append(fn)
                log("    OK")
            else:
                fail_names.append(fn)
        else:
            fail_names.append(fn)
    elif st == 'failed':
        err = item.get('err_msg', '')
        log("    FAILED: " + err)
        fail_names.append(fn)
    elif st == 'running':
        p = item.get('extract_progress', {})
        log("    STILL RUNNING: pages %s/%s" % (
            p.get('extracted_pages', '?'), p.get('total_pages', '?')))
        fail_names.append(fn)  # treat as fail for now
    else:
        fail_names.append(fn)  # pending or unknown

# Update progress
log("Done: %d, Fail: %d" % (len(done_names), len(fail_names)))
if done_names or fail_names:
    prog = json.load(open(PROGRESS, encoding='utf-8'))
    ok_set = set(prog.get("ok", []))
    fail_set = set(prog.get("fail", []))
    for fn in done_names:
        ok_set.add(fn)
    for fn in fail_names:
        fail_set.add(fn)
    prog["ok"] = list(ok_set)
    prog["fail"] = list(fail_set)
    json.dump(prog, open(PROGRESS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    log("Progress updated.")

    not_ready = [x for x in items if x.get('state') == 'running']
    if not_ready:
        log("WARNING: %d files still running. Will be retried by workers." % len(not_ready))
else:
    log("Nothing to recover.")

log("Done.")
