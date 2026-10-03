"""Print keyword windows for each candidate's gap questions in the given videos. usage: scan.py <cid> <vid>... """
import json, re, sys, collections
sys.path.insert(0, 'platform'); from vtt import ts_at
sys.path.insert(0, 'pres2')
import importlib.util
spec = importlib.util.spec_from_file_location('s', 'pres/search.py')
src = open('pres/search.py').read().split('q, vids = sys.argv')[0]
ns = {}; exec(src, ns); KW = ns['KW']
from search_path import path
cid, vids = sys.argv[1], sys.argv[2:]
qs = [x['id'] for x in json.load(open('../src/data/questions.json')) if cid.split('-')[0] in x['offices']]
have = collections.defaultdict(set)
for x in json.load(open('../src/data/evidence.json')): have[x['subject']['id']].add(x['questionId'])
W = 230
for q in sorted(set(qs) - have[cid]):
    print(f'=== {cid} {q}')
    for v in vids:
        t = open(path(v)).read(); idx = json.load(open(path(v) + '.idx.json'))
        hits = sorted({m.start() for k in KW[q] for m in re.finditer(k, t, re.I)}); last = -10**9
        for h in hits:
            if h - last < W: continue
            last = h
            print(f'  {v} [{ts_at(idx, h)}] ...{t[max(0,h-W):h+W]}...')
