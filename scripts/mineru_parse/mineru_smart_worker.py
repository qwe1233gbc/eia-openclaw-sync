# -*- coding: utf-8 -*-
"""
MinerU v4 vlm 智能并行Worker v3
策略：
  - 批次大小10，最小化队列压力
  - 两worker错峰启动（W2晚60-90s）
  - 耐心等：取消aggressive stall检测，每批最多等60min
  - 超时的文件放回pending队列重试（不标永久失败）
  - >40MB文件提前跳过（大概率超200页）
  - 随机抖动防同步
用法: python mineru_smart_worker.py <worker_id>
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
MAX_POLL_SEC = 3600       # 最多等60分钟
POLL_INTERVAL = 30        # 每30s轮询一次
COOLDOWN_OK = 20
COOLDOWN_FAIL = 30
BIG_FILE_MB = 40

os.makedirs(OUT_DIR, exist_ok=True)

if WORKER_ID == 2:
    delay = 60 + random.randint(0, 30)
    print("[W2 %s] Staggering %ds..." % (time.strftime('%H:%M:%S'), delay), flush=True)
    time.sleep(delay)

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

def get_all_files():
    files = []
    for fn in os.listdir(PDF_DIR):
        if fn.lower().endswith('.pdf'):
            fp = os.path.join(PDF_DIR, fn)
            files.append({"name": fn, "path": fp, "size": os.path.getsize(fp)})
    return sorted(files, key=lambda x: x['name'])

def my_assigned(all_f, ok_set, fail_set):
    pending = [f for f in all_f if f['name'] not in ok_set and f['name'] not in fail_set]
    return [f for i, f in enumerate(pending) if i % 2 == (WORKER_ID - 1)]

def api_post(url, payload, timeout=60):
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=timeout)
            if resp.status_code == 429:
                w = 90 + random.randint(0, 30)
                log("  429, waiting %ds..." % w)
                time.sleep(w)
                continue
            data = resp.json() if resp.text else {}
            if isinstance(data, dict) and data.get("code") == 0:
                return data.get("data")
            msg = data.get("msg", "") if isinstance(data, dict) else str(data)[:100]
            log("  API err: " + msg)
            if "limit" in msg.lower() or "exceed" in msg.lower():
                time.sleep(90 + random.randint(0, 30))
                continue
            return None
        except Exception as e:
            log("  req err: " + str(e))
            time.sleep(10 + random.randint(0, 10))
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
    for attempt in range(3):
        try:
            resp = requests.put(url, data=data, timeout=300)
            if resp.status_code == 200:
                return True
        except Exception as e:
            log("    PUT err: " + str(e))
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
            log("    DL err: " + str(e))
            time.sleep(15)
    return False

def process_batch(batch_files, idx, total):
    """返回 (ok_list, perm_fail_list, retry_list)
    - ok_list: 完成并下载的文件
    - perm_fail_list: 永久失败（超页数等），不再重试
    - retry_list: 需要重试的文件（超时等）
    """
    log("=" * 50)
    log("Batch %d/%d: %d files" % (idx+1, total, len(batch_files)))
    log("=" * 50)

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

    # Step 1: 提交
    log("Step 1/4: Submitting batch...")
    result = api_post(API + "/file-urls/batch", {
        "files": [{"name": n} for n in names],
        "model_version": "vlm"
    })
    if not result:
        return [], skip_big, [f['name'] for f in good]

    batch_id = result.get('batch_id')
    urls = result.get('file_urls', [])
    if not batch_id or len(urls) != len(good):
        return [], skip_big, [f['name'] for f in good]
    log("batch_id=%s" % batch_id)

    # Step 2: 上传
    log("Step 2/4: Uploading...")
    up_ok_names = []
    upload_fail = []
    timed_out = False
    for i, (bf, u) in enumerate(zip(good, urls)):
        url = u if isinstance(u, str) else u.get('url', str(u))
        fn = bf['name']
        mb = bf['size'] / 1048576
        log("  [%d/%d] %s (%.0fMB)" % (i+1, len(good), fn[:50], mb))
        if put_file(bf['path'], url):
            up_ok_names.append(fn)
        else:
            log("    UPLOAD FAIL!")
            upload_fail.append(fn)
        time.sleep(0.3 + random.random() * 0.4)

    log("Upload: ok=%d fail=%d" % (len(up_ok_names), len(upload_fail)))
    if not up_ok_names:
        return [], skip_big, upload_fail

    # Step 3: 耐心轮询
    log("Step 3/4: Polling (max %d min, interval %ds)..." % (MAX_POLL_SEC//60, POLL_INTERVAL))
    waited = 0
    poll_ok, poll_fail, retry = [], [], []

    while waited < MAX_POLL_SEC:
        time.sleep(POLL_INTERVAL + random.randint(-5, 5))
        waited += POLL_INTERVAL

        cr = api_get(API + "/extract-results/batch/" + batch_id)
        if not cr or not isinstance(cr, dict):
            continue
        items = cr.get("data", {}).get("extract_result", [])
        if not items:
            continue

        done_items = [x for x in items if x.get('state') == 'done']
        failed_items = [x for x in items if x.get('state') == 'failed']
        other = [x for x in items if x.get('state') not in ('done', 'failed')]

        # 进度日志
        for x in other[:1]:
            p = x.get('extract_progress') or {}
            log("  -> %s [%s/%sp]" % (
                x['file_name'][:40], p.get('extracted_pages','?'), p.get('total_pages','?')))
        log("  [%dmin] done=%d fail=%d pending=%d" % (
            waited//60, len(done_items), len(failed_items), len(other)))

        if not other:
            # 全部完成
            for x in done_items:
                fn = x['file_name']
                zu = x.get('full_zip_url', '')
                if not zu:
                    retry.append(fn)
                    continue
                zn = os.path.splitext(fn)[0] + '_mineru.zip'
                zp = os.path.join(OUT_DIR, zn)
                if os.path.exists(zp):
                    poll_ok.append(fn)
                elif download(zu, zp):
                    log("  DL OK: %s" % fn[:50])
                    poll_ok.append(fn)
                else:
                    log("  DL FAIL: %s" % fn[:50])
                    retry.append(fn)
            for x in failed_items:
                fn = x['file_name']
                err = x.get('err_msg', '')
                log("  FAIL: %s -> %s" % (fn[:45], err))
                if '200 pages' in err:
                    poll_fail.append(fn)  # 永久失败
                else:
                    retry.append(fn)  # 可重试
            break

    else:  # 超时
        log("  TIMEOUT after %d min!" % (waited//60))
        timed_out = True
        # 取回当前状态
        cr = api_get(API + "/extract-results/batch/" + batch_id)
        items = cr.get("data", {}).get("extract_result", []) if cr and isinstance(cr, dict) else []
        if items:
            for x in items:
                fn = x['file_name']
                st = x.get('state')
                if st == 'done':
                    zu = x.get('full_zip_url', '')
                    if zu:
                        zn = os.path.splitext(fn)[0] + '_mineru.zip'
                        zp = os.path.join(OUT_DIR, zn)
                        if os.path.exists(zp) or download(zu, zp):
                            poll_ok.append(fn)
                            continue
                    retry.append(fn)
                elif st == 'failed':
                    err = x.get('err_msg', '')
                    if '200 pages' in err:
                        poll_fail.append(fn)
                    else:
                        retry.append(fn)
                else:
                    retry.append(fn)  # 超时未完成 → 重试
        else:
            retry.extend(up_ok_names)  # 完全拿不到结果就全部重试

    all_ok = poll_ok
    all_perm_fail = skip_big + poll_fail
    all_retry = upload_fail + retry

    log("Batch results: ok=%d perm_fail=%d retry=%d" % (len(all_ok), len(all_perm_fail), len(all_retry)))
    return all_ok, all_perm_fail, all_retry

def main():
    log("=" * 50)
    log("MinerU Smart Worker %d v3" % WORKER_ID)
    log("Token: ...%s" % TOKEN[-20:])
    log("Batch: %d, Max poll: %dmin" % (BATCH_SIZE, MAX_POLL_SEC//60))
    log("=" * 50)

    all_f = get_all_files()
    prog = load_prog()
    ok_set = set(prog.get("ok", []))
    fail_set = set(prog.get("fail", []))

    my_files = my_assigned(all_f, ok_set, fail_set)
    log("Progress: ok=%d fail=%d pending=%d" % (len(ok_set), len(fail_set), len(my_files)))
    if not my_files:
        log("All done!"); return

    batches = [my_files[i:i+BATCH_SIZE] for i in range(0, len(my_files), BATCH_SIZE)]
    log("My batches: %d" % len(batches))

    for i, batch in enumerate(batches):
        # 刷新进度（可能有另一个worker已处理）
        prog = load_prog()
        ok_set = set(prog.get("ok", []))
        fail_set = set(prog.get("fail", []))
        batch = [f for f in batch if f['name'] not in ok_set and f['name'] not in fail_set]
        if not batch:
            log("Batch %d: all done already" % (i+1))
            continue

        ok_list, perm_fail, retry = process_batch(batch, i, len(batches))

        # 更新进度
        prog = load_prog()
        ok_set = set(prog.get("ok", []))
        fail_set = set(prog.get("fail", []))
        for fn in ok_list:
            ok_set.add(fn)
        for fn in perm_fail:
            fail_set.add(fn)
        # retry的文件不记录到任何列表 → 自然留在pending池中
        prog["ok"] = sorted(ok_set)
        prog["fail"] = sorted(fail_set)
        save_prog(prog)

        log("Saved: ok=%d perm_fail=%d retry=%d" % (len(ok_list), len(perm_fail), len(retry)))

        cd = COOLDOWN_OK if not retry else COOLDOWN_FAIL
        cd += random.randint(0, 15)
        if i < len(batches) - 1:
            log("Cooldown %ds..." % cd)
            time.sleep(cd)

    log("WORKER %d DONE!" % WORKER_ID)

if __name__ == '__main__':
    main()
