import json, hashlib, os, re, time, urllib.request
RAW = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'
def path(url, ext):
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', url.split('://', 1)[1])[:140]
    return os.path.join(RAW, slug + '_' + hashlib.sha1(url.encode()).hexdigest()[:8] + ext)
def fetch(url, accept='application/json', refresh=False, binary=False):
    ext = '.json' if 'json' in accept else '.bin' if binary else '.html'
    p = path(url, ext)
    if os.path.exists(p) and not refresh:
        return open(p, 'rb').read()
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept, 'Accept-Language': 'pt-BR,pt;q=0.9'})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
            break
        except Exception:
            if i == 2: raise
            time.sleep(2)
    open(p, 'wb').write(body)
    return body
def jget(url, refresh=False):
    return json.loads(fetch(url, refresh=refresh).decode('utf-8'))
