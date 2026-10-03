"""doc-tdd checks for record evidence.

Each evidence row is re-derived from the primary source instead of trusting build_record.py:
identity (TSE row <-> parliament record by civil name + birth date), the vote or orientation itself,
the date in the sentence, and for executive acts the exact phrases in the Planalto text.
A random 20% sample is re-fetched live. Negative controls must FAIL.

Usage: python3 check_record.py [candidates.json] [--no-write]
"""
import copy, csv, html, json, os, random, re, sys, unicodedata, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(HERE, '..', 'record')
sys.path.insert(0, REC)
from fetch import get, live  # noqa: E402

C = 'https://dadosabertos.camara.leg.br/api/v2'
S = 'https://legis.senado.leg.br/dadosabertos'
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36'}
ALIASES = {'CASSIO MURILLO GALDINO DE ARAUJO': 'CASSIO MURILO GALDINO DE ARAUJO'}
OFFICE = {'presidente': 'PRESIDENTE', 'governador': 'GOVERNADOR', 'senador': 'SENADOR',
          'deputado_federal': 'DEPUTADO FEDERAL', 'deputado_estadual': 'DEPUTADO ESTADUAL'}


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()).strip()


def plain_html(t):
    t = re.sub(r'(?is)<(style|script).*?</\1>', ' ', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t)


def br(iso):
    y, m, d = iso[:10].split('-')
    return f'{d}/{m}/{y}'


TSE = {}
for f in ('consulta_cand_2026_PB.csv', 'consulta_cand_2026_BR.csv'):
    for r in csv.DictReader(open(os.path.join(HERE, '..', 'raw', 'tse', f), encoding='latin-1'), delimiter=';'):
        TSE.setdefault((r['DS_CARGO'], r['NR_CANDIDATO']), []).append(r)


def tse_row(cid):
    office, num = cid.split('-', 1)
    rows = TSE.get((OFFICE[office], num), [])
    assert len(rows) == 1, f'TSE rows for {cid}: {len(rows)}'
    return rows[0]


def tse_birth(r):
    d, m, y = r['DT_NASCIMENTO'].split('/')
    return f'{y}-{m}-{d}'


def check_identity_camara(cid, parl_id):
    r = tse_row(cid)
    dep = get(f'{C}/deputados/{parl_id}')['dados']
    key = ALIASES.get(norm(r['NM_CANDIDATO']), norm(r['NM_CANDIDATO']))
    assert norm(dep['nomeCivil']) == key, f"civil name {dep['nomeCivil']} != {r['NM_CANDIDATO']}"
    assert dep['dataNascimento'] == tse_birth(r), 'birth date differs'


def check_identity_senado(cid, parl_id):
    r = tse_row(cid)
    p = get(f'{S}/senador/{parl_id}.json')['DetalheParlamentar']['Parlamentar']
    assert norm(p['IdentificacaoParlamentar']['NomeCompletoParlamentar']) == norm(r['NM_CANDIDATO']), 'full name differs'
    assert p['DadosBasicosParlamentar']['DataNascimento'] == tse_birth(r), 'birth date differs'


def expected_position(word):
    return {'Sim': 1, 'Não': -1, 'Abstenção': 0, 'Obstrução': 0}[word]


WORDS = {'Sim': 'SIM', 'Não': 'NÃO', 'Abstenção': 'abstenção', 'Obstrução': 'obstrução'}


def word_in_detail(word, detail):
    others = [w for k, w in WORDS.items() if k != word]
    return WORDS[word] in detail and not any(re.search(rf'\b{w}\b', detail) for w in others)


def check_camara_vote(e, fetcher):
    ref = e['_ref']
    vid = ref['votacao']
    check_identity_camara(e['subject']['id'], ref['parlId'])
    votos = fetcher(f'{C}/votacoes/{vid}/votos')['dados']
    mine = [v for v in votos if v['deputado_']['id'] == ref['parlId']]
    assert len(mine) == 1, f'{len(mine)} vote rows for deputy {ref["parlId"]}'
    t = mine[0]['tipoVoto']
    assert e['position'] == expected_position(t), f'position {e["position"]} but source says {t}'
    assert word_in_detail(t, e['detail']), f'detail does not state {t}'
    meta = fetcher(f'{C}/votacoes/{vid}')['dados']
    assert br(meta['data']) in e['detail'] and e['date'] == meta['data'], 'date differs'


def check_camara_orient(e, fetcher):
    ref = e['_ref']
    vid = ref['votacao']
    o = [x for x in fetcher(f'{C}/votacoes/{vid}/orientacoes')['dados'] if x['siglaPartidoBloco'] == ref['sigla']]
    assert len(o) == 1, f'{len(o)} orientation rows for {ref["sigla"]}'
    ov = o[0]['orientacaoVoto']
    assert e['position'] == expected_position(ov), f'position {e["position"]} but orientation {ov}'
    assert word_in_detail(ov, e['detail']), f'detail does not state {ov}'
    meta = fetcher(f'{C}/votacoes/{vid}')['dados']
    assert br(meta['data']) in e['detail'], 'date differs'


def check_senado_vote(e, fetcher):
    ref = e['_ref']
    check_identity_senado(e['subject']['id'], ref['parlId'])
    vots = [x for x in fetcher(ref['url']) if x['codigoSessaoVotacao'] == ref['codigoSessaoVotacao']]
    assert len(vots) == 1, 'votação not found'
    mine = [v for v in vots[0]['votos'] if v['codigoParlamentar'] == ref['parlId']]
    assert len(mine) == 1, f'{len(mine)} vote rows for senator {ref["parlId"]}'
    t = mine[0]['siglaVotoParlamentar']
    assert e['position'] == expected_position(t), f'position {e["position"]} but source says {t}'
    assert word_in_detail(t, e['detail']), f'detail does not state {t}'
    assert br(vots[0]['dataSessao']) in e['detail'], 'date differs'


def check_planalto(e, is_live):
    ref = e['_ref']
    if is_live:
        raw = urllib.request.urlopen(urllib.request.Request(ref['url'], headers=UA), timeout=60).read().decode('cp1252', errors='replace')
    else:
        raw = open(os.path.join(REC, ref['cache'])).read()
    text = plain_html(raw)
    missing = [p for p in ref['phrases'] if p not in text]
    assert not missing, f'phrases not in source: {missing}'


def run_one(e, is_live):
    fetcher = live if is_live else get
    t = e['_ref']['type']
    if t == 'camara_vote':
        check_camara_vote(e, fetcher)
    elif t == 'camara_orient':
        check_camara_orient(e, fetcher)
    elif t == 'senado_vote':
        check_senado_vote(e, fetcher)
    elif t == 'planalto':
        check_planalto(e, is_live)
    else:
        raise AssertionError(f'unknown ref type {t}')


def negative_controls(rows):
    ctrls = []
    by_type = {}
    for e in rows:
        by_type.setdefault(e['_ref']['type'], []).append(e)
    # 1. Flip a real Câmara vote: Luiz Couto (PT) on the marco temporal.
    for e in by_type.get('camara_vote', []):
        if e['subject']['id'] == 'deputado_federal-1345' and e['questionId'] == 'soc-marco-temporal':
            c = copy.deepcopy(e); c['position'] = -c['position']; c['id'] = 'NEG-flip-couto-marco'; ctrls.append(c); break
    # 2. Flip a Senado vote: Flávio Bolsonaro on PEC 45/2023 (drogas).
    for e in by_type.get('senado_vote', []):
        if e['subject']['id'] == 'presidente-22' and e['questionId'] == 'seg-drogas':
            c = copy.deepcopy(e); c['position'] = -c['position']; c['detail'] = c['detail'].replace('SIM', 'NÃO'); c['id'] = 'NEG-flip-flavio-drogas'; ctrls.append(c); break
    # 3. Attribute a vote to the wrong person: same row, another deputy's id (Hugo Motta presided on 2358548-89).
    for e in by_type.get('camara_vote', []):
        if e['_ref']['votacao'] == '2358548-89':
            c = copy.deepcopy(e); c['_ref']['parlId'] = 160674; c['subject']['id'] = 'deputado_federal-1011'; c['id'] = 'NEG-hugo-voted-dosimetria'; ctrls.append(c); break
    # 4. Executive: claim Lula sanctioned Lei 15.402/2026 (it was promulgated after a veto override).
    for e in by_type.get('planalto', []):
        if 'l15402' in e['_ref']['cache']:
            c = copy.deepcopy(e); c['_ref']['phrases'] = ['eu sanciono', 'LUIZ INÁCIO LULA DA SILVA']; c['id'] = 'NEG-lula-sanctioned-dosimetria'; ctrls.append(c); break
    # 5. Orientation flip: PL leadership on PEC 45/2019.
    for e in by_type.get('camara_orient', []):
        if e['_ref']['sigla'] == 'PL' and e['questionId'] == 'eco-reforma-tributaria':
            c = copy.deepcopy(e); c['position'] = -c['position']; c['id'] = 'NEG-flip-PL-orient-reforma'; ctrls.append(c); break
    # 6. Date tamper on a real row.
    for e in by_type.get('camara_vote', []):
        c = copy.deepcopy(e); c['detail'] = re.sub(r'\d{2}/\d{2}/\d{4}', '01/01/2020', c['detail']); c['id'] = 'NEG-date-tamper'; ctrls.append(c); break
    return ctrls


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    path = args[0] if args else os.path.join(REC, 'candidates.json')
    rows = json.load(open(path))
    random.seed(20261004)
    live_ids = {e['id'] for e in random.sample(rows, max(1, len(rows) // 5))} if rows else set()
    report = []
    for e in rows:
        status, err = 'PASS', ''
        try:
            run_one(e, False)
            if e['id'] in live_ids:
                run_one(e, True)
        except Exception as ex:
            status, err = 'FAIL', f'{type(ex).__name__}: {ex}'
        report.append({'id': e['id'], 'status': status, 'claim': e['detail'], 'live': e['id'] in live_ids, 'error': err})
    ctrl_report = []
    for c in negative_controls(rows):
        try:
            run_one(c, False)
            ctrl_report.append({'id': c['id'], 'status': 'PASS', 'claim': c['detail'], 'expected': 'FAIL', 'harness_ok': False})
        except Exception as ex:
            ctrl_report.append({'id': c['id'], 'status': 'FAIL', 'claim': c['detail'], 'expected': 'FAIL', 'harness_ok': True, 'error': str(ex)})
    harness_ok = len(ctrl_report) >= 3 and all(c['harness_ok'] for c in ctrl_report)
    n_pass = sum(r['status'] == 'PASS' for r in report)
    print(f'rows={len(report)} PASS={n_pass} FAIL={len(report) - n_pass} live_checked={len(live_ids)} controls={len(ctrl_report)} harness_ok={harness_ok}')
    for r in report:
        if r['status'] == 'FAIL':
            print('  FAIL', r['id'], r['error'])
    for c in ctrl_report:
        print('  CONTROL', c['id'], c['status'], c.get('error', '')[:90])
    if '--no-write' in sys.argv:
        return
    json.dump({'harness_ok': harness_ok, 'rows': report, 'controls': ctrl_report},
              open(os.path.join(HERE, 'record.report.json'), 'w'), ensure_ascii=False, indent=1)
    if not harness_ok:
        print('harness broken: evidence.json NOT written')
        return
    passed = {r['id'] for r in report if r['status'] == 'PASS'}
    out = [{k: v for k, v in e.items() if k != '_ref'} for e in rows if e['id'] in passed]
    json.dump(out, open(os.path.join(REC, 'evidence.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'evidence.json written: {len(out)} rows')


if __name__ == '__main__':
    main()
