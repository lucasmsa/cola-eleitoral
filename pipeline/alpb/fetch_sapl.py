import json, sys, time, pathlib, requests
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
BASE = 'https://sapl.al.pb.leg.br/api/'
RAW = pathlib.Path(__file__).parent / 'raw'
s = requests.Session(); s.headers.update({'User-Agent': UA, 'Accept': 'application/json'})

def get(url, params=None):
    for i in range(5):
        try:
            r = s.get(url, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            print('status', r.status_code, url, params, file=sys.stderr)
        except Exception as e:
            print('err', e, file=sys.stderr)
        time.sleep(2 * (i + 1))
    raise SystemExit(f'failed {url} {params}')

def dump(endpoint, page_size=100, params=None):
    out, page = [], 1
    while True:
        d = get(BASE + endpoint, {**(params or {}), 'page_size': page_size, 'page': page})
        out += d['results']
        if not d['pagination'].get('next_page'):
            break
        page += 1
    name = endpoint.strip('/').replace('/', '_')
    (RAW / f'{name}.json').write_text(json.dumps({'endpoint': BASE + endpoint, 'accessed': time.strftime('%Y-%m-%d'), 'results': out}, ensure_ascii=False))
    print(endpoint, len(out))

if __name__ == '__main__':
    for ep in sys.argv[1:]:
        dump(ep)
