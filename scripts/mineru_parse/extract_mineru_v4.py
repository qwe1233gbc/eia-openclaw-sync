import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('E:/软件/mineru_api_docs.html', encoding='utf-8') as f:
    html = f.read()

# Get text around v4 API sections
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n\s*\n+', '\n\n', text)

# Find key sections
keywords = [
    'extract/task', 'extract-results', 'batch', 'v4', 'api/v4',
    'api-key', 'token', 'Authorization', 'Bearer',
    'concurrency', 'quota', 'price', 'limit', 'rate',
    'pdf', 'docx', 'format', 'response', 'result',
    'status', 'pending', 'processing', 'completed',
    'file upload', 'upload_url', 'presigned',
]

for kw in keywords:
    pattern = re.compile(re.escape(kw), re.IGNORECASE)
    for m in pattern.finditer(text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 400)
        snippet = text[start:end].replace('\n', ' ')
        snippet = re.sub(r'\s+', ' ', snippet)
        print(f'\n[{kw}] at pos {m.start()}:')
        print(f'  ...{snippet}...')
        print('---')
        break  # Only first occurrence per keyword
