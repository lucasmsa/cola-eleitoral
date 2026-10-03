import json, hashlib, os, re, sys, time, urllib.request, urllib.parse
RAW = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) cola-eleitoral research', 'Accept': 'application/json'}
def key(url):
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', url.split('://',1)[1])[:150]
    return os.path.join(RAW, slug + '_' + hashlib.sha1(url.encode()).hexdigest()[:8] + '.json')
def get(url, refresh=False, accept='application/json'):
    p = key(url)
    if os.path.exists(p) and not refresh:
        return json.load(open(p))
    h = dict(UA); h['Accept'] = accept
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                body = r.read().decode('utf-8')
            break
        except Exception as e:
            if i == 3: raise
            time.sleep(2 * (i + 1))
    data = json.loads(body)
    json.dump(data, open(p, 'w'), ensure_ascii=False)
    return data
def live(url, accept='application/json'):
    h = dict(UA); h['Accept'] = accept
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))
