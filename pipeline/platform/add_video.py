import json, sys
sys.path.insert(0, 'platform'); from vtt import ts_at
c, q, pos, vid, mode, alias, anchor, start, end, detail = sys.argv[1:11]
raw = f'platform/raw/yt/{vid}.txt'; t = open(raw).read(); idx = json.load(open(raw + '.idx.json'))
meta = open(f'platform/raw/yt/meta_{vid}.txt').read().strip().splitlines()[0].split('|')
i = t.find(start); assert i >= 0, 'start not found'
j = t.find(end, i); assert j >= 0, 'end not found'
quote = t[i:j+len(end)]; assert len(quote) <= 300, f'too long {len(quote)}'
ts = ts_at(idx, i); h, m, s = map(int, ts.split(':'))
d = meta[1]; date = f'{d[:4]}-{d[4:6]}-{d[6:]}'
row = dict(candidateId=c, questionId=q, position=int(pos), video=vid, mode=mode, alias=alias, anchor=anchor or None,
           raw=raw, url=f'https://www.youtube.com/watch?v={vid}&t={h*3600+m*60+s}s', timestamp=ts, date=date,
           channel=meta[2], title=meta[3], quote=quote, detail=detail)
p = 'platform/draft.jsonl'; rows = [json.loads(l) for l in open(p)]
rows = [r for r in rows if not (r['candidateId'] == c and r['questionId'] == q)] + [row]
open(p, 'w').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
print(ts, len(quote), quote)
