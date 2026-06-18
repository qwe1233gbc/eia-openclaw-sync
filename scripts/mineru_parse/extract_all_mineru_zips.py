# -*- coding: utf-8 -*-
import os, zipfile, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ZIP_DIR = r"E:\软件\mineru_parsed"
OUT_DIR = r"E:\软件\mineru_extracted"
LOG_FILE = r"E:\软件\mineru_extract_log.txt"

os.makedirs(OUT_DIR, exist_ok=True)

def log(msg):
    line = "[%s] %s" % (time.strftime('%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

zips = sorted([f for f in os.listdir(ZIP_DIR) if f.endswith('.zip')])
log("=== Batch Extraction: %d ZIPs ===" % len(zips))
log("In:  %s" % ZIP_DIR)
log("Out: %s" % OUT_DIR)

done = 0
skipped = 0
failed = 0
start = time.time()

for i, zname in enumerate(zips):
    zpath = os.path.join(ZIP_DIR, zname)
    extract_to = os.path.join(OUT_DIR, zname[:-4])  # remove .zip

    # Skip if already extracted (full.md exists)
    if os.path.exists(os.path.join(extract_to, 'full.md')):
        skipped += 1
        if (i+1) % 100 == 0:
            log("[%d/%d] skipped=%d done=%d" % (i+1, len(zips), skipped, done))
        continue

    try:
        # Remove output dir first to avoid WinError 183 on Windows
        import shutil
        if os.path.exists(extract_to):
            shutil.rmtree(extract_to, ignore_errors=True)
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(zpath, 'r') as z:
            z.extractall(extract_to)
        done += 1
    except Exception as e:
        failed += 1
        log("FAIL [%d/%d] %s: %s" % (i+1, len(zips), zname[:60], str(e)[:80]))

    if (i+1) % 50 == 0:
        elapsed = time.time() - start
        rate = (i+1) / elapsed * 60
        log("[%d/%d] done=%d skip=%d fail=%d (%.1f zip/min)" % (
            i+1, len(zips), done, skipped, failed, rate))

elapsed = time.time() - start
log("=" * 55)
log("ALL DONE!")
log("Total: %d, Extracted: %d, Skipped: %d, Failed: %d" % (len(zips), done, skipped, failed))
log("Time: %.1f min (%.1f zip/min)" % (elapsed/60, len(zips)/elapsed*60))
log("Output: %s" % OUT_DIR)
