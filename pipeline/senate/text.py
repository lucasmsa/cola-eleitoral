import re, html, sys
sys.path.insert(0, '.')
from fetch import fetch
def page_text(url, refresh=False):
    raw = fetch(url, accept='text/html', refresh=refresh).decode('utf-8', errors='ignore')
    raw = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?i)<br\s*/?>|</p>|</h\d>|</li>', '\n', raw)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    return re.sub(r'\n\s*\n+', '\n', t)
def date_of(url):
    raw = fetch(url, accept='text/html').decode('utf-8', errors='ignore')
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', raw) or re.search(r'article:published_time"\s+content="([^"]+)"', raw) or re.search(r'content="([^"]+)"\s+property="article:published_time"', raw)
    return m.group(1)[:10] if m else None
if __name__ == '__main__':
    url = sys.argv[1]; kws = sys.argv[2:]
    t = page_text(url)
    print('DATE', date_of(url), 'LEN', len(t))
    for para in t.split('\n'):
        p = para.strip()
        if len(p) > 60 and (not kws or any(k.lower() in p.lower() for k in kws)):
            print('-', p[:700])
