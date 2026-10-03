import json, re, sys, os
def norm(s): return re.sub(r'\s+', ' ', s).strip()
mp = json.load(open('platform/plan_map.json'))
by_c = {v['candidateId']: k for k, v in mp.items() if v['status'] != 'INDEFERIDO'}
c, q, pos, page, start, end, detail = sys.argv[1:8]
f = by_c[c]; t = norm(open(f'platform/text/{f}.p{page}.txt').read())
i = t.find(start)
assert i >= 0, f'start not found: {start}'
j = t.find(end, i)
assert j >= 0, f'end not found: {end}'
quote = t[i:j+len(end)]
assert len(quote) <= 300, f'quote too long {len(quote)}: {quote}'
row = dict(candidateId=c, questionId=q, position=int(pos), page=int(page), file=f, url=mp[f]['url'], quote=quote, detail=detail)
path = 'platform/draft.jsonl'
rows = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
rows = [r for r in rows if not (r['candidateId']==c and r['questionId']==q)] + [row]
open(path,'w').write(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
print(len(quote), quote)
