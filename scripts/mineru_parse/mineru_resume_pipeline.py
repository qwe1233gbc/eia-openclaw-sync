# -*- coding: utf-8 -*-
"""
MinerU 弹性解析 Pipeline
三步走: ①本地预检 → ②提交解析 → ③下载结果
支持断点续传、失败重试、自动跳过扫描件
"""
import sys, os, json, time, hashlib, requests, fitz
sys.stdout.reconfigure(encoding='utf-8')

TOKENS = [
    "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI4MjYwODkyNSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3NDY5NzE1NiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTUyODAyNTkyNzYiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJkOTBmY2IxMy0wNTZjLTRlNzAtODVlYS1iYjE1ODkyYzg1NzgiLCJlbWFpbCI6IiIsImV4cCI6MTc4MjQ3MzE1Nn0.6iy08CY3TL4lLccJqzfi6lM2owbXAjurC_Gi7SVW8PgyxGdfevtUCIBQnUaakO6MUejSQ6t6am3n1araO8GxNQ",
    "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI0NzIwMDU5NSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc3OTk0MDA5NSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTU2Nzc3NTkyOTUiLCJvcGVuSWQiOm51bGwsInV1aWQiOiJiZjdlOGNiNy02OTVjLTQyMzgtYmI3Zi1hNGU0YzZhOTYwNmQiLCJlbWFpbCI6IiIsImV4cCI6MTc4NzcxNjA5NX0.OBoWX3Gj1ieM5VYH39nFUkpvvY-YD1RRk4Sp2fhMib03C0vuKMhP8t9Y8gsSJlglWiK3zjaV0Vqm0dwMA8ZVlA",
]

API = "https://mineru.net/api/v4"
PDF_DIR = r"E:\软件\2023-2026年顺德受理公告"
OUT_DIR = r"E:\软件\mineru_parsed"
PROGRESS = r"E:\软件\mineru_progress.json"
os.makedirs(OUT_DIR, exist_ok=True)


def log(msg):
    print("[%s] %s" % (time.strftime('%H:%M:%S'), msg), flush=True)


def load_progress():
    if os.path.exists(PROGRESS):
        return json.load(open(PROGRESS, 'r', encoding='utf-8'))
    return {"ok": [], "fail": [], "done_batches": []}


def save_progress(p):
    json.dump(p, open(PROGRESS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def has_text_content(filepath):
    """本地预检：PDF是否有可提取的文本"""
    try:
        doc = fitz.open(filepath)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()
        return len(text) > 200
    except:
        return False


def api_post(url, payload, headers, timeout=60):
    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 429:
                t = 90 + attempt * 30
                log("  429 rate limit, wait %ds..." % t)
                time.sleep(t)
                continue
            data = resp.json()
            if data.get("code") == 0:
                return data["data"]
            msg = data.get("msg", "")
            log("  API error: %s" % msg[:80])
            if "limit" in msg.lower():
                time.sleep(90)
                continue
        except Exception as e:
            log("  POST error: %s" % str(e)[:60])
            time.sleep(15)
    return None


def api_get(url, headers, timeout=30):
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            log("  GET error: %s" % str(e)[:60])
            time.sleep(10)
    return None


def upload_file(filepath, url):
    with open(filepath, 'rb') as f:
        data = f.read()
    for attempt in range(3):
        try:
            resp = requests.put(url, data=data, timeout=300)
            if resp.status_code == 200:
                return True
        except:
            time.sleep(10)
    return False


def download_result(url, filepath):
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
        except:
            time.sleep(15)
    return False


def main():
    # 预设token（token1有余额限制时切token2）
    token_idx = 0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + TOKENS[token_idx],
    }

    log("=" * 55)
    log("MinerU 弹性解析 Pipeline")
    log("=" * 55)

    # Step 1: 本地预检
    log("\nStep 1/3: 本地预检PDF...")
    all_pdfs = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    log("总PDF: %d" % len(all_pdfs))

    prog = load_progress()
    ok_set = set(prog.get("ok", []))
    fail_set = set(prog.get("fail", []))

    # 找出待解析文件
    pending_candidates = [f for f in all_pdfs if f not in ok_set and f not in fail_set]
    log("待处理: %d (OK=%d FAIL=%d)" % (len(pending_candidates), len(ok_set), len(fail_set)))

    # 预检：过滤掉扫描件
    valid = []
    skipped = 0
    for f in pending_candidates:
        fp = os.path.join(PDF_DIR, f)
        if has_text_content(fp):
            valid.append(f)
        else:
            skipped += 1
            fail_set.add(f)
    log("通过预检: %d, 跳过(扫描件): %d" % (len(valid), skipped))

    if not valid:
        log("没有待解析的文件")
        prog["ok"] = list(ok_set)
        prog["fail"] = list(fail_set)
        save_progress(prog)
        return

    # Step 2: 分批提交解析
    log("\nStep 2/3: 分批提交解析...")
    batch_size = 30  # 减小batch以降低失败率
    batches = [valid[i:i+batch_size] for i in range(0, len(valid), batch_size)]
    log("共 %d 批 (每批 %d 个)" % (len(batches), batch_size))

    total_ok = len(ok_set)
    total_fail = len(fail_set)

    for batch_idx, batch in enumerate(batches):
        # 检查是否已有token余额用完，切token2
        if token_idx == 0 and total_ok > 800:
            token_idx = 1
            headers["Authorization"] = "Bearer " + TOKENS[token_idx]
            log("切换到 Token 2")

        batch_id_str = hashlib.md5(str(batch).encode()).hexdigest()[:8]
        # 跳过可能有重复的batch
        if batch_id_str in prog.get("done_batches", []):
            log("Batch %s already done, skip" % batch_id_str)
            continue

        log("\n--- Batch %d/%d (%d files, %s) ---" % (batch_idx+1, len(batches), len(batch), batch_id_str))
        names = batch

        # 2a: 获取上传URL
        result = api_post(API + "/file-urls/batch", {
            "files": [{"name": n} for n in names],
            "model_version": "vlm"
        }, headers)
        if not result:
            log("Batch submission failed, will retry later")
            break

        batch_id = result["batch_id"]
        urls = result.get("file_urls", [])
        log("batch_id=%s, urls=%d" % (batch_id, len(urls)))

        # 2b: 上传文件
        ok_up = []
        for i, (fn, u) in enumerate(zip(names, urls)):
            url = u if isinstance(u, str) else u.get('url', str(u))
            fp = os.path.join(PDF_DIR, fn)
            if upload_file(fp, url):
                ok_up.append(fn)
            else:
                log("  Upload FAIL: %s" % fn[:50])
            time.sleep(0.2)
        log("Upload: ok=%d/%d" % (len(ok_up), len(names)))

        if not ok_up:
            for fn in names:
                fail_set.add(fn)
            total_fail += len(names)
            continue

        # 2c: 轮询解析结果
        log("Polling for results (max 30min)...")
        waited = 0
        while waited < 1800:  # 30min
            time.sleep(60)
            waited += 60
            cr = api_get(API + "/extract-results/batch/" + batch_id, headers)
            if not cr:
                continue
            items = cr.get("data", {}).get("extract_result", [])
            if not items:
                continue
            done = sum(1 for x in items if x.get('state') == 'done')
            fail = sum(1 for x in items if x.get('state') == 'failed')
            running = len(items) - done - fail
            log("  [%dmin] done=%d fail=%d running=%d/%d" % (waited//60, done, fail, running, len(items)))
            if running == 0:
                break

        # 2d: 下载结果
        cr = api_get(API + "/extract-results/batch/" + batch_id, headers)
        items = cr.get("data", {}).get("extract_result", []) if cr else []

        for item in items:
            fn = item.get('file_name', '')
            st = item.get('state', '')
            if st == 'done':
                zu = item.get('full_zip_url', '')
                if zu:
                    zn = os.path.splitext(fn)[0] + '_mineru.zip'
                    zp = os.path.join(OUT_DIR, zn)
                    if download_result(zu, zp):
                        ok_set.add(fn)
                        total_ok += 1
                    else:
                        fail_set.add(fn)
                        total_fail += 1
            elif st == 'failed':
                fail_set.add(fn)
                total_fail += 1

        # 更新进度
        prog["ok"] = list(ok_set)
        prog["fail"] = list(fail_set)
        done_batches = set(prog.get("done_batches", []))
        done_batches.add(batch_id_str)
        prog["done_batches"] = list(done_batches)
        save_progress(prog)
        log("Cumulative: OK=%d FAIL=%d" % (total_ok, total_fail))

        # batch间隔
        if batch_idx < len(batches) - 1:
            log("Cooldown 75s...")
            time.sleep(75)

    log("\n" + "=" * 55)
    log("Pipeline 完成!")
    log("最终: OK=%d FAIL=%d" % (total_ok, total_fail))


if __name__ == '__main__':
    main()
