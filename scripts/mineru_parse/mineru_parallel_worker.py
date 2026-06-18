# -*- coding: utf-8 -*-
"""
MinerU v4 vlm 并行worker
用法: python mineru_parallel_worker.py <worker_id>
  worker_id=1  -> token1 (原号)
  worker_id=2  -> token2 (新号)
通过奇偶索引拆分 pending 文件，互不重叠，共享同一进度文件。
"""
import sys, os, json, time, hashlib
sys.stdout.reconfigure(encoding='utf-8')
import requests

WORKER_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1

TOKENS = {
    1: "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI4MjYwODkyNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3NDY5NzE1NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTUyODAyNTkyNzYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJkOTBmY2IxMy0wNTZjLTRlNzAtODVlYS1iYjE1ODkyYzg1NzgiLCJlbWFpbCI6IiIsImV4cCI6MTc4MjQ3MzE1Nn0.6iy08CY3TL4lLccJqzfi6lM2owbXAjurC_Gi7SVW8PgyxGdfevtUCIBQnUaakO6MUejSQ6t6am3n1araO8GxNQ",
    2: "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI0NzIwMDU5NSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3OTk0MDA5NSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTU2Nzc3NTkyOTUiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJiZjdlOGNiNy02OTVjLTQyMzgtYmI3Zi1hNGU0YzZhOTYwNmQiLCJlbWFpbCI6IiIsImV4cCI6MTc4NzcxNjA5NX0.OBoWX3Gj1ieM5VYH39nFUkpvvY-YD1RRk4Sp2fhMib03C0vuKMhP8t9Y8gsSJlglWiK3zjaV0Vqm0dwMA8ZVlA"
}

TOKEN = TOKENS[WORKER_ID]
API = "https://mineru.net/api/v4"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + TOKEN
}
PDF_DIR = r"E:\软件\2023-2026年顺德受理公告"
OUT_DIR = r"E:\软件\mineru_parsed"
PROGRESS = r"E:\软件\mineru_progress.json"
BATCH_SIZE = 50
COOLDOWN = 75

os.makedirs(OUT_DIR, exist_ok=True)

def log(msg):
    print("[W%s %s] %s" % (WORKER_ID, time.strftime('%H:%M:%S'), msg), flush=True)

def load_prog():
    for _ in range(5):
        try:
            if os.path.exists(PROGRESS):
                with open(PROGRESS, encoding='utf-8') as f:
                    return json.load(f)
            return {"ok": [], "fail": [], "done_batches": []}
        except (json.JSONDecodeError, PermissionError):
            time.sleep(1)
    return {"ok": [], "fail": [], "done_batches": []}

def save_prog(p):
    tmp = PROGRESS + ".tmp." + str(WORKER_ID)
    json.dump(p, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    os.replace(tmp, PROGRESS)

def get_files():
    files = []
    for fn in os.listdir(PDF_DIR):
        if fn.lower().endswith('.pdf'):
            fp = os.path.join(PDF_DIR, fn)
            files.append({"name": fn, "path": fp, "size": os.path.getsize(fp)})
    return sorted(files, key=lambda x: x['name'])

def my_pending(all_f, ok_set, fail_set):
    """Return only the files assigned to this worker (by index parity)."""
    pending = [f for f in all_f if f['name'] not in ok_set and f['name'] not in fail_set]
    assigned = [f for i, f in enumerate(pending) if i % 2 == (WORKER_ID - 1)]
    return assigned

def api_post(url, payload, timeout=60):
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
            if resp.status_code == 429:
                log("  429 rate limit, waiting 90s...")
                time.sleep(90)
                continue
            try:
                data = resp.json()
            except:
                log("  non-JSON response: " + resp.text[:150])
                time.sleep(30)
                continue
            if isinstance(data, dict) and data.get("code") == 0:
                return data["data"]
            msg = data.get("msg", "") if isinstance(data, dict) else str(data)[:100]
            log("  API error: " + msg)
            if "limit" in str(msg).lower() or "exceed" in str(msg).lower():
                time.sleep(90)
                continue
        except Exception as e:
            log("  request error: " + str(e))
            time.sleep(10)
    return None

def api_get(url, timeout=30):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        return resp.json()
    except Exception as e:
        log("  GET error: " + str(e))
        return None

def put_file(filepath, url):
    with open(filepath, 'rb') as f:
        data = f.read()
    for attempt in range(3):
        try:
            resp = requests.put(url, data=data, timeout=300)
            if resp.status_code == 200:
                return True
        except Exception as e:
            log("    PUT error: " + str(e))
            time.sleep(10)
    return False

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
            log("    download error: " + str(e))
            time.sleep(15)
    return False

def process_batch(batch_files, idx, total):
    log("=" * 55)
    log("Batch %d/%d: %d files" % (idx+1, total, len(batch_files)))
    log("=" * 55)

    names = [f['name'] for f in batch_files]

    # Step 1: Submit
    log("Step 1/4: Submitting batch...")
    result = api_post(API + "/file-urls/batch", {
        "files": [{"name": n} for n in names],
        "model_version": "vlm"
    })
    if not result:
        log("Batch submission FAILED!")
        return [], names

    batch_id = result['batch_id']
    urls = result.get('file_urls', [])
    log("batch_id=%s, urls=%d" % (batch_id, len(urls)))

    if len(urls) != len(batch_files):
        log("URL count mismatch!")
        return [], names

    # Step 2: Upload
    log("Step 2/4: Uploading...")
    ok_up = []
    fail_up = []
    for i, (bf, u) in enumerate(zip(batch_files, urls)):
        url = u if isinstance(u, str) else u.get('url', str(u))
        fn = bf['name']
        mb = bf['size'] / 1048576
        log("  [%d/%d] %s (%.1fMB)" % (i+1, len(batch_files), fn[:55], mb))
        if put_file(bf['path'], url):
            ok_up.append(fn)
        else:
            fail_up.append(fn)
            log("    UPLOAD FAILED!")
        time.sleep(0.2)

    log("Upload: ok=%d fail=%d" % (len(ok_up), len(fail_up)))
    if not ok_up:
        return [], fail_up

    # Step 3: Poll
    log("Step 3/4: Waiting for parsing...")
    waited = 0
    while waited < 28800:
        time.sleep(60)
        waited += 60
        cr = api_get(API + "/extract-results/batch/" + batch_id)
        if not cr or not isinstance(cr, dict):
            continue
        items = cr.get("data", {}).get("extract_result", [])
        if not items:
            continue
        done = sum(1 for x in items if x.get('state') == 'done')
        fail = sum(1 for x in items if x.get('state') == 'failed')
        running = len(items) - done - fail
        for x in items:
            if x.get('state') == 'running':
                p = x.get('extract_progress', {})
                if p:
                    log("  running: %s [%s/%s pages]" % (
                        x['file_name'][:45],
                        p.get('extracted_pages', '?'),
                        p.get('total_pages', '?')
                    ))
                break
        log("  [%dmin] done=%d fail=%d running=%d/%d" % (
            waited//60, done, fail, running, len(items)
        ))
        if running == 0:
            break

    # Step 4: Download
    log("Step 4/4: Downloading results...")
    cr = api_get(API + "/extract-results/batch/" + batch_id)
    items = cr.get("data", {}).get("extract_result", []) if cr else []

    ok_dl = []
    fail_dl = fail_up[:]
    for item in items:
        fn = item.get('file_name', 'unknown')
        st = item.get('state', 'unknown')
        if st == 'done':
            zu = item.get('full_zip_url', '')
            if zu:
                zn = os.path.splitext(fn)[0] + '_mineru.zip'
                zp = os.path.join(OUT_DIR, zn)
                log("  DL: " + fn[:50] + "...")
                if download(zu, zp):
                    ok_dl.append(fn)
                    log("    OK (%.1fMB)" % (os.path.getsize(zp)/1048576))
                else:
                    fail_dl.append(fn)
        elif st == 'failed':
            log("  PARSE FAIL: " + fn[:50] + " -> " + item.get('err_msg', ''))
            fail_dl.append(fn)

    log("Batch result: ok=%d fail=%d" % (len(ok_dl), len(fail_dl)))
    return ok_dl, fail_dl

def main():
    log("=" * 55)
    log("MinerU v4 vlm Parallel Worker %d" % WORKER_ID)
    log("Token: ...%s" % TOKEN[-20:])
    log("In:  " + PDF_DIR)
    log("Out: " + OUT_DIR)
    log("=" * 55)

    all_f = get_files()
    log("Total PDFs: %d" % len(all_f))

    prog = load_prog()
    ok_set = set(prog.get("ok", []))
    fail_set = set(prog.get("fail", []))
    done_batches = set(prog.get("done_batches", []))

    my_files = my_pending(all_f, ok_set, fail_set)
    log("Shared progress: ok=%d fail=%d" % (len(ok_set), len(fail_set)))
    log("My pending files: %d" % len(my_files))

    if not my_files:
        log("No files assigned to me. All done!")
        return

    batches = [my_files[i:i+BATCH_SIZE] for i in range(0, len(my_files), BATCH_SIZE)]
    log("My batches: %d" % len(batches))

    for i, batch in enumerate(batches):
        # Re-check progress before each batch (other worker may have updated)
        prog = load_prog()
        current_ok = set(prog.get("ok", []))
        current_fail = set(prog.get("fail", []))
        batch = [f for f in batch if f['name'] not in current_ok and f['name'] not in current_fail]
        if not batch:
            log("Batch %d: all files already done, skip" % (i+1))
            continue

        # Check batch hash
        bh = hashlib.md5(str([f['name'] for f in batch]).encode()).hexdigest()[:8]
        if bh in done_batches:
            log("Batch %d (%s) already done, skip" % (i+1, bh))
            continue

        ok, fail = process_batch(batch, i, len(batches))

        # Update shared progress
        for _ in range(3):
            try:
                prog = load_prog()
                ok_set = set(prog.get("ok", []))
                fail_set = set(prog.get("fail", []))
                done_batches = set(prog.get("done_batches", []))
                for fn in ok:
                    ok_set.add(fn)
                for fn in fail:
                    fail_set.add(fn)
                done_batches.add(bh)
                prog["ok"] = list(ok_set)
                prog["fail"] = list(fail_set)
                prog["done_batches"] = list(done_batches)
                save_prog(prog)
                break
            except Exception as e:
                log("Save progress error: " + str(e))
                time.sleep(2)

        log("Cumulative: my_ok=%d my_fail=%d" % (len(ok), len(fail)))

        if i < len(batches) - 1:
            log("Cooldown %ds..." % COOLDOWN)
            time.sleep(COOLDOWN)

    log("=" * 55)
    log("WORKER %d ALL DONE!" % WORKER_ID)
    log("=" * 55)

if __name__ == '__main__':
    main()
