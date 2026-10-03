import json, re, sys, os
c, q, pos, raw, url, date, start, end, detail = sys.argv[1:10]
t = open(raw).read()
i = t.find(start); assert i >= 0, 'start not found'
j = t.find(end, i); assert j >= 0, 'end not found'
quote = t[i:j+len(end)]; assert len(quote) <= 300, f'too long {len(quote)}'
row = dict(candidateId=c, questionId=q, position=int(pos), raw=raw, url=url, date=date, quote=quote, detail=detail)
path = 'platform/draft.jsonl'
rows = [json.loads(l) for l in open(path)]
rows = [r for r in rows if not (r['candidateId']==c and r['questionId']==q)] + [row]
open(path,'w').write(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
print(len(quote), quote)
