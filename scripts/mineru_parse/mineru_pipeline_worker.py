# -*- coding: utf-8 -*-
"""
MinerU v4 pipeline 高速Worker
 - model_version: pipeline（已验证，1.5min/文件）
 - 批次大小10，轮询间隔15s
 - 两worker错峰
 - 超时文件不标永久失败，自动重试
用法: python mineru_pipeline_worker.py <worker_id>
"""
import sys, os, json, time, hashlib, random
sys.stdout.reconfigure(encoding='utf-8')
import requests

WORKER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1

TOKENS = {
    1: "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI4MjYwODkyNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3NDY5NzE1NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTUyODAyNTkyNzYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJkOTBmY2IxMy0wNTZjLTRlNzAtODVlYS1iYjE1ODkyYzg1NzgiLCJlbWFpbCI6IiIsImV4cCI6MTc4MjQ3MzE1Nn0.6iy08CY3TL4lLccJqzfi6lM2owbXAjurC_Gi7SVW8PgyxGdfevtUCIBQnUaakO6MUejSQ6t6am3n1araO8GxNQ",
    2: "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI0NzIwMDU5NSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3OTk0MDA5NSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTU2Nzc3NTkyOTUiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJiZjdlOGNiNy02OTVjLTQyMzgtYmI3Zi1hNGU0YzZhOTYwNmQiLCJlbWFpbCI6IiIsImV4cCI6MTc4NzcxNjA5NX0.OBoWX3Gj1ieM5VYH39nFUkpvvY-YD1RRk4Sp2fhMib03C0vuKMhP8t9Y8gsSJlglWiK3zjaV0Vqm0dwMA8ZVlA"
}

TOKEN = TOKENS[WORKER_ID]
API = "https://mineru.net/api/v4"
HEADERS = {"Content-Type": "application/json", "Authorization": "Bearer " + TOKEN}
PDF_DIR = r"E:\软件\2023-2026年顺德受理公告"
OUT_DIR = r"E:\软件\mineru_parsed"
PROGRESS = r"E:\软件\mineru_progress.json"

BATCH_SIZE = 10
MAX_POLL_SEC = 600        # 最多等10min（pipeline通常1-3min）
POLL_INTERVAL = 15
COOLDOWN = 15
BIG_FILE_MB = 40

os.makedirs(OUT_DIR, exist_ok=True)

if WORKER_ID == 2:
    time.sleep(60 + random.randint(0, 30))

def log(msg):
    print("[W%s %s] %s" % (WORKER_ID, time.strftime('%H:%M:%S'), msg), flush=True)

def load_prog():
    for _ in range(5):
        try:
            if os.path.exists(PROGRESS):
                with open(PROGRESS, encoding='utf-8') as f:
                    return json.load(f)
            return {"ok": [], "fail": [], "done_batches": []}
        except: time.sleep(1)
    return {"ok": [], "fail": [], "done_batches": []}

def save_prog(p):
    tmp = PROGRESS + ".tmp." + str(WORKER_ID)
    json.dump(p, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    os.replace(tmp, PROGRESS)

def get_all():
    files = []
    for fn in os.listdir(PDF_DIR):
        if fn.lower().endswith('.pdf'):
            fp = os.path.join(PDF_DIR, fn)
            files.append({"name": fn, "path": fp, "size": os.path.getsize(fp)})
    return sorted(files, key=lambda x: x['name'])

def my_assigned(all_f, ok_set, fail_set):
    p = [f for f in all_f if f['name'] not in ok_set and f['name'] not in fail_set]
    return [f for i, f in enumerate(p) if i % 2 == (WORKER_ID - 1)]

def api_post(url, payload, timeout=60):
    for a in range(3):
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
            if resp.status_code == 429:
                time.sleep(90 + random.randint(0, 30)); continue
            data = resp.json() if resp.text else {}
            if isinstance(data, dict) and data.get("code") == 0:
                return data.get("data")
            msg = data.get("msg", "") if isinstance(data, dict) else str(data)[:100]
            log("  API err: " + msg)
            if "limit" in msg.lower() or "exceed" in msg.lower():
                time.sleep(90 + random.randint(0, 30)); continue
            return None
        except Exception as e:
            log("  req err: " + str(e))
            time.sleep(10)
    return None

def api_get(url, timeout=30):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        return resp.json() if resp.text else {}
    except Exception as e:
        log("  GET err: " + str(e))
        return None

def put_file(filepath, url):
    with open(filepath, 'rb') as f:
        data = f.read()
    for a in range(3):
        try:
            resp = requests.put(url, data=data, timeout=300)
            if resp.status_code == 200: return True
        except: time.sleep(10)
    return False

def download(url, filepath):
    for a in range(3):
        try:
            resp = requests.get(url, timeout=600, stream=True)
            resp.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(65536): f.write(chunk)
            if os.path.getsize(filepath) > 1024: return True
            os.remove(filepath)
        except: time.sleep(15)
    return False

def process_batch(batch_files, idx, total):
    log("=== Batch %d/%d: %d files ===" % (idx+1, total, len(batch_files)))

    # 预检大文件
    good, skip_big = [], []
    for f in batch_files:
        if f['size'] / 1048576 > BIG_FILE_MB:
            log("  SKIP BIG: %s (%.0fMB)" % (f['name'][:50], f['size']/1048576))
            skip_big.append(f['name'])
        else:
            good.append(f)
    if not good:
        return [], skip_big, []

    names = [f['name'] for f in good]

    # Step 1: Submit
    result = api_post(API + "/file-urls/batch", {
        "files": [{"name": n} for n in names],
        "model_version": "pipeline"   # <-- pipeline!
    })
    if not result:
        return [], skip_big, [f['name'] for f in good]

    batch_id = result.get('batch_id')
    urls = result.get('file_urls', [])
    if not batch_id or len(urls) != len(good):
        return [], skip_big, [f['name'] for f in good]

    # Step 2: Upload
    up_ok, up_fail = [], []
    for i, (bf, u) in enumerate(zip(good, urls)):
        url = u if isinstance(u, str) else u.get('url', str(u))
        fn = bf['name']
        log("  [%d/%d] %s (%.0fMB)" % (i+1, len(good), fn[:50], bf['size']/1048576))
        if put_file(bf['path'], url):
            up_ok.append(fn)
        else:
            up_fail.append(fn)
        time.sleep(0.2 + random.random() * 0.3)

    if not up_ok:
        return [], skip_big, up_fail

    # Step 3: Poll
    waited = 0
    poll_ok, poll_fail, retry = [], [], []
    while waited < MAX_POLL_SEC:
        time.sleep(POLL_INTERVAL + random.randint(-3, 5))
        waited += POLL_INTERVAL
        cr = api_get(API + "/extract-results/batch/" + batch_id)
        items = cr.get("data", {}).get("extract_result", []) if cr and isinstance(cr, dict) else []
        if not items: continue

        done = [x for x in items if x.get('state') == 'done']
        failed = [x for x in items if x.get('state') == 'failed']
        other = [x for x in items if x.get('state') not in ('done', 'failed')]

        for x in other[:1]:
            p = x.get('extract_progress') or {}
            log("  -> %s [%s/%sp]" % (x['file_name'][:40], p.get('extracted_pages','?'), p.get('total_pages','?')))
        log("  [%dmin] done=%d fail=%d pend=%d" % (waited//60, len(done), len(failed), len(other)))

        if not other:
            for x in done:
                fn, zu = x['file_name'], x.get('full_zip_url', '')
                if not zu: retry.append(fn); continue
                zp = os.path.join(OUT_DIR, os.path.splitext(fn)[0] + '_mineru.zip')
                if os.path.exists(zp) or download(zu, zp):
                    poll_ok.append(fn)
                else:
                    retry.append(fn)
            for x in failed:
                fn, err = x['file_name'], x.get('err_msg', '')
                log("  FAIL: %s -> %s" % (fn[:45], err))
                (poll_fail if '200 pages' in err else retry).append(fn)
            break
    else:
        log("  TIMEOUT %dmin, releasing %d files" % (waited//60, len(other) if 'other' in dir() else 0))
        cr = api_get(API + "/extract-results/batch/" + batch_id)
        items = cr.get("data", {}).get("extract_result", []) if cr and isinstance(cr, dict) else []
        for x in items:
            fn, st = x['file_name'], x.get('state')
            if st == 'done':
                zu = x.get('full_zip_url', '')
                zp = os.path.join(OUT_DIR, os.path.splitext(fn)[0] + '_mineru.zip')
                (poll_ok if (zu and (os.path.exists(zp) or download(zu, zp))) else retry).append(fn)
            elif st == 'failed':
                (poll_fail if '200 pages' in x.get('err_msg','') else retry).append(fn)
            else:
                retry.append(fn)

    return poll_ok, skip_big + poll_fail, up_fail + retry

def main():
    log("=== MinerU Pipeline Worker %d ===" % WORKER_ID)
    all_f = get_all()
    prog = load_prog()
    ok_set, fail_set = set(prog.get("ok", [])), set(prog.get("fail", []))
    my_files = my_assigned(all_f, ok_set, fail_set)
    log("Progress: ok=%d fail=%d my_pending=%d" % (len(ok_set), len(fail_set), len(my_files)))
    if not my_files: log("All done!"); return

    batches = [my_files[i:i+BATCH_SIZE] for i in range(0, len(my_files), BATCH_SIZE)]
    log("Batches: %d" % len(batches))

    for i, batch in enumerate(batches):
        prog = load_prog()
        ok_set, fail_set = set(prog.get("ok", [])), set(prog.get("fail", []))
        batch = [f for f in batch if f['name'] not in ok_set and f['name'] not in fail_set]
        if not batch: continue

        ok_list, perm_fail, retry = process_batch(batch, i, len(batches))

        prog = load_prog()
        ok_set, fail_set = set(prog.get("ok", [])), set(prog.get("fail", []))
        for fn in ok_list: ok_set.add(fn)
        for fn in perm_fail: fail_set.add(fn)
        # retry files 不记录 → 留在pending池
        prog["ok"], prog["fail"] = sorted(ok_set), sorted(fail_set)
        save_prog(prog)
        log("Saved: ok=%d perm_fail=%d retry=%d" % (len(ok_list), len(perm_fail), len(retry)))

        if i < len(batches) - 1:
            time.sleep(COOLDOWN + random.randint(0, 10))

    log("WORKER %d DONE!" % WORKER_ID)

if __name__ == '__main__':
    main()
