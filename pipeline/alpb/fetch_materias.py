import json, re, collections
from fetch_sapl import get, BASE, RAW
v = json.load(open(RAW / 'sessao_votoparlamentar.json'))['results']
reg = {r['id']: r for r in json.load(open(RAW / 'sessao_registrovotacao.json'))['results']}
by = collections.defaultdict(list)
for r in v: by[r['votacao']].append(r)
cache = RAW / 'materias_20leg.json'
out = json.loads(cache.read_text()) if cache.exists() else {}
todo = [vid for vid, rs in by.items() if '20ª Legislatura' in rs[0]['__str__']]
for vid in todo:
    mid = reg[vid]['materia']
    if str(mid) in out: continue
    out[str(mid)] = get(f'{BASE}materia/materialegislativa/{mid}/')
    cache.write_text(json.dumps(out, ensure_ascii=False))
print(len(todo), len(out))
