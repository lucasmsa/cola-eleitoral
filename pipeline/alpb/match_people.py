import csv, json, unicodedata, re, collections
def norm(s):
    s = re.sub(r'\(.*?\)', ' ', s or '')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Z ]', ' ', s)).strip()
cands = list(csv.DictReader(open('../raw/tse/consulta_cand_2026_PB.csv', encoding='latin-1'), delimiter=';'))
comp = {r['SQ_CANDIDATO']: r for r in csv.DictReader(open('../raw/tse/comp_PB.csv', encoding='latin-1'), delimiter=';')}
OFFICE = {'GOVERNADOR': 'governador', 'SENADOR': 'senador', 'DEPUTADO FEDERAL': 'deputado_federal', 'DEPUTADO ESTADUAL': 'deputado_estadual'}
byname = collections.defaultdict(list)
for c in cands: byname[norm(c['NM_CANDIDATO'])].append(c)
parl = {p['id']: p for p in json.load(open('raw/parlamentares_parlamentar.json'))['results']}
out = {}
for pid, p in parl.items():
    hits = byname.get(norm(p.get('nome_completo')), [])
    rows = []
    for h in hits:
        cp = comp.get(h['SQ_CANDIDATO'], {})
        fed = h['SG_FEDERACAO'] if h['SG_FEDERACAO'] not in ('#NULO#', '#NULO', '') else None
        rows.append({'cargo': h['DS_CARGO'], 'office': OFFICE.get(h['DS_CARGO']), 'number': h['NR_CANDIDATO'], 'urna': h['NM_URNA_CANDIDATO'],
                     'full_name': h['NM_CANDIDATO'], 'party': h['SG_PARTIDO'], 'federacao_sigla': fed, 'federacao_nome': h['NM_FEDERACAO'] if fed else None,
                     'status_tot': cp.get('DS_SITUACAO_CANDIDATO_TOT'), 'on_urna': cp.get('ST_CANDIDATO_INSERIDO_URNA'), 'sq': h['SQ_CANDIDATO']})
    out[pid] = {'nome_parlamentar': p['nome_parlamentar'], 'nome_completo': p['nome_completo'], 'candidacies': rows}
json.dump(out, open('raw/parlamentar_to_2026.json', 'w'), ensure_ascii=False, indent=1)
