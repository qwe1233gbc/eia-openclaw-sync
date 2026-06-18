import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('E:/软件/mineru_api_docs.html', encoding='utf-8') as f:
    html = f.read()

# Extract key sections by looking for API-related content
# Search for common API doc patterns
patterns = [
    (r'https?://[^\s"\'<>]+?(?:api|parse|upload|task)[^\s"\'<>]*', 'API URLs'),
    (r'[a-zA-Z]+\s*/\s*v\d+[^\s"\'<>]*', 'Versioned paths'),
    (r'(?:POST|GET|PUT|DELETE)\s+[^\s]+', 'HTTP methods'),
    (r'(?:Bearer|token|api[_-]?key|secret|authorization)', 'Auth patterns'),
    (r'(?:multipart|form[_-]?data|application/json|file)', 'Request types'),
    (r'(?:rate[_-]?limit|quota|concurrency|parallel)', 'Rate limits'),
]

for pattern, label in patterns:
    matches = set(re.findall(pattern, html, re.IGNORECASE))
    if matches:
        print(f'\n=== {label} ===')
        for m in sorted(matches)[:15]:
            print(f'  {m}')

# Also get text around key terms
key_terms = ['api-key', 'endpoint', 'curl', 'request', 'response', 'base_url', 'upload']
print('\n=== Key text context ===')
text_only = re.sub(r'<[^>]+>', ' ', html)
text_only = re.sub(r'\s+', ' ', text_only)
for term in key_terms:
    # Find first occurrence
    idx = text_only.lower().find(term)
    if idx >= 0:
        start = max(0, idx - 50)
        end = min(len(text_only), idx + 150)
        print(f'\n[{term}]: ...{text_only[start:end]}...')
