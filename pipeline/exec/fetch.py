"""Fetch a URL into exec/raw/web and print the text around keywords. Usage: fetch.py URL [kw ...]"""
import hashlib, html, re, subprocess, sys
from pathlib import Path
RAW = Path(__file__).parent / 'raw' / 'web'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'

def path_for(url):
    return RAW / (hashlib.sha1(url.encode()).hexdigest()[:16] + '.html')

def fetch(url, force=False):
    p = path_for(url)
    if force or not p.exists() or p.stat().st_size < 1500:
        subprocess.run(['curl', '-sL', '--max-time', '40', '-A', UA, '-o', str(p), url], check=False)
    return p

def text_of(p):
    raw = p.read_bytes()
    try:
        s = raw.decode('utf-8')
    except UnicodeDecodeError:
        s = raw.decode('latin-1')
    s = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s))

if __name__ == '__main__':
    url, kws = sys.argv[1], sys.argv[2:]
    p = fetch(url)
    t = text_of(p)
    print(p.name, len(t))
    m = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}T)', t)
    print('first date:', m.group(0) if m else None)
    for kw in kws:
        for mm in list(re.finditer(kw, t, re.I))[:4]:
            print(f'--[{kw}]', t[max(0, mm.start()-350): mm.end()+350])


def published(p):
    raw = p.read_bytes().decode('utf-8', errors='ignore')
    for pat in [r'article:published_time"\s+content="([^"]+)"', r'content="([^"]+)"\s+property="article:published_time"',
                r'"datePublished"\s*:\s*"([^"]+)"', r'itemprop="datePublished"[^>]*content="([^"]+)"', r'<time[^>]*datetime="([^"]+)"']:
        m = re.search(pat, raw)
        if m:
            return m.group(1)[:10]
    return None


def render(url, wait_ms=6000):
    """Headless Chromium for pages behind a JS challenge. Caches the rendered DOM like fetch()."""
    import os
    from playwright.sync_api import sync_playwright
    p = path_for(url)
    exe = os.environ.get('PW_CHROMIUM')
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, **({'executable_path': exe} if exe else {}))
        page = b.new_page(user_agent=UA, locale='pt-BR')
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(wait_ms)
        p.write_text(page.content(), encoding='utf-8')
        b.close()
    return p
