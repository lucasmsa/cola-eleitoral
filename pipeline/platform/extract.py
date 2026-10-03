import json, os, pdfplumber
from pypdf import PdfReader
d = json.load(open('raw/roster.json'))
office = {'president': 'presidente', 'governor_PB': 'governador'}
mapping = {}
for k, off in office.items():
    for c in d[k]:
        p = c.get('plano_de_governo')
        if not p: continue
        mapping[p['file']] = {'candidateId': f"{off}-{c['number']}", 'name': c['ballot_name'], 'status': c['status'], 'url': p['source']['url']}
json.dump(mapping, open('platform/plan_map.json', 'w'), ensure_ascii=False, indent=1)
for f in mapping:
    path = f'raw/plans/{f}'
    r = PdfReader(path)
    n = len(r.pages); chars = 0
    for i, pg in enumerate(r.pages, 1):
        t = pg.extract_text() or ''
        chars += len(t)
        open(f'platform/text/{f}.p{i}.txt', 'w').write(t)
    print(f, mapping[f]['candidateId'], mapping[f]['name'], mapping[f]['status'], 'pages', n, 'chars', chars)
