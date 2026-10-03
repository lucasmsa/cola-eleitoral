"""doc-tdd checks for ALPB/PB questions and evidence. Run from pipeline/: .venv/bin/python checks/check_alpb.py"""
import csv, json, os, re, subprocess, unicodedata, html, io, copy
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
OFFICE_CARGO = {'governador': 'GOVERNADOR', 'deputado_estadual': 'DEPUTADO ESTADUAL', 'deputado_federal': 'DEPUTADO FEDERAL'}
LOCAL_PDF = {
    'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/pauta/1187_pauta_sessao.pdf': 'alpb/raw/pauta_1187.pdf',
    'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/ata/1187_ata_sessao.pdf': 'alpb/raw/ata_1187.pdf',
    'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/pauta/ordem_do_dia_23.09.2025_3a_sessao_ordinaria_itinerante.pdf': 'alpb/raw/ordemdia_1350.pdf',
    'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/ata/3_ordinaria_itinerante_2025.pdf': 'alpb/raw/ata_1350.pdf',
}


def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()


def pdfnorm(s):
    # PDF line breaks split words as "público- privadas"; rejoin before matching.
    return re.sub(r'(\w)- (\w)', r'\1-\2', norm(s))


def namenorm(s):
    s = re.sub(r'\(.*?\)', ' ', s or '')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Z ]', ' ', s)).strip()


def curl(url, accept=None):
    cmd = ['curl', '-sL', '--max-time', '60', '-A', UA, '-w', '\n%{http_code}']
    if accept:
        cmd += ['-H', f'Accept: {accept}']
    p = subprocess.run(cmd + [url], capture_output=True)
    body, _, code = p.stdout.rpartition(b'\n')
    return body if code == b'200' else None


def pdf_text(data):
    return pdfnorm(' '.join((p.extract_text() or '') for p in PdfReader(io.BytesIO(data)).pages))


TSE = {}
with open('raw/tse/consulta_cand_2026_PB.csv', encoding='latin-1') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        TSE[r['SQ_CANDIDATO']] = r
        TSE[(r['DS_CARGO'], r['NR_CANDIDATO'])] = r
COMP = {}
with open('raw/tse/comp_PB.csv', encoding='latin-1') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        COMP[r['SQ_CANDIDATO']] = r
VOTES = json.load(open('alpb/raw/sessao_votoparlamentar.json'))['results']
PARL = {p['id']: p for p in json.load(open('alpb/raw/parlamentares_parlamentar.json'))['results']}
ROSTER_GOV = {c['number']: c for c in json.load(open('raw/roster.json'))['governor_PB']}
LOCAL = {url: pdf_text(open(path, 'rb').read()) for url, path in LOCAL_PDF.items()}
LIVE = {}
for url in LOCAL_PDF:
    b = curl(url)
    LIVE[url] = pdf_text(b) if b else None
LIVE_VOTES = {}
SESSION = {22453: json.load(open('alpb/raw/votacao_22453_meta.json')), 49945: json.load(open('alpb/raw/votacao_49945_meta.json'))}
LIVE_SESSION = {}
for vid in SESSION:
    b = curl(f'https://sapl.al.pb.leg.br/api/sessao/votoparlamentar/?votacao={vid}&page_size=100', 'application/json')
    LIVE_VOTES[vid] = json.loads(b)['results'] if b else None
    b = curl(f'https://sapl.al.pb.leg.br/api/sessao/sessaoplenaria/{SESSION[vid]["sessao"]["id"]}/', 'application/json')
    LIVE_SESSION[vid] = json.loads(b) if b else None
def html_text(b):
    try:
        t = b.decode('utf-8')
    except UnicodeDecodeError:
        t = b.decode('cp1252')
    return norm(html.unescape(re.sub(r'(?s)<[^>]+>', ' ', t)))


cf = curl('https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm')
CF_LIVE = html_text(cf) if cf else None
CF_LOCAL = html_text(open('alpb/raw/cf88.html', 'rb').read())
VOTE_META = {
    22453: {'pauta': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/pauta/1187_pauta_sessao.pdf',
            'ata': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/ata/1187_ata_sessao.pdf',
            'subject': 'Projeto Lei nº 3.536/2022', 'phrase': 'aporte de arma de fogo aos', 'veto': '321/2022',
            'tally_re': r'MANTIDO O VETO COM 09 VOTOS SIM, 15 VOTOS NÃO'},
    49945: {'pauta': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/pauta/ordem_do_dia_23.09.2025_3a_sessao_ordinaria_itinerante.pdf',
            'ata': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/ata/3_ordinaria_itinerante_2025.pdf',
            'subject': 'Projeto de Lei n° 2.496/2024', 'phrase': 'inclusão do nome social dos consumidores', 'veto': '214/2025',
            'tally_re': r'o veto foi mantido por maioria, obtendo 07 votos SIM, 24 votos NÃO e 01 abstenção'},
}
RULE = 'VOTANDO SIM O DEPUTADO REJEITA O VETO, APROVANDO O PROJETO, E VOTANDO NÃO, ACEITA O VETO'


def both(url, needle, flags=re.I):
    reasons = []
    if not re.search(needle, LOCAL[url], flags):
        reasons.append(f'cached {url.rsplit("/", 1)[-1]} lacks /{needle}/')
    if LIVE[url] is None:
        reasons.append(f'live {url} unreachable')
    elif not re.search(needle, LIVE[url], flags):
        reasons.append(f'live {url.rsplit("/", 1)[-1]} lacks /{needle}/')
    return reasons


def check_vote(row):
    c, r = row['_check'], []
    vid = c['votacao']
    meta = VOTE_META.get(vid)
    if not meta:
        return [f'unknown votacao {vid}']
    cached = [v for v in VOTES if v['votacao'] == vid and v['parlamentar'] == c['parlamentar']]
    if len(cached) != 1 or cached[0]['voto'].strip() != c['voto']:
        r.append(f'cached SAPL vote is {[v["voto"] for v in cached]}, claim {c["voto"]}')
    live = LIVE_VOTES.get(vid)
    if live is None:
        r.append('live SAPL unreachable')
    else:
        lv = [v for v in live if v['parlamentar'] == c['parlamentar']]
        if len(lv) != 1 or lv[0]['voto'].strip() != c['voto']:
            r.append(f'live SAPL vote is {[v["voto"] for v in lv]}, claim {c["voto"]}')
    expected_pos = 1 if c['voto'] == 'Sim' else -1
    if row['position'] != expected_pos:
        r.append(f'position {row["position"]} != {expected_pos} for {c["voto"]}')
    if c['voto'].upper() not in row['detail']:
        r.append('detail does not state the vote')
    p = PARL.get(c['parlamentar'])
    tse = TSE.get(c['sq'])
    if not p or not tse or namenorm(p['nome_completo']) != namenorm(tse['NM_CANDIDATO']):
        r.append(f'ALPB name {p and p["nome_completo"]} != TSE {tse and tse["NM_CANDIDATO"]}')
    office, nr = row['subject']['id'].split('-', 1)
    if not tse or tse['DS_CARGO'] != OFFICE_CARGO.get(office) or tse['NR_CANDIDATO'] != nr:
        r.append(f'subject {row["subject"]["id"]} != TSE {tse and (tse["DS_CARGO"], tse["NR_CANDIDATO"])}')
    if COMP.get(c['sq'], {}).get('ST_CANDIDATO_INSERIDO_URNA') != 'SIM':
        r.append('candidate not on urna per comp_PB.csv')
    if p and p['nome_parlamentar'] not in row['detail']:
        r.append('detail names a different parlamentar')
    sd = SESSION[vid]['sessao'].get('data_inicio')
    if sd != row['date']:
        r.append(f'cached session date {sd} != {row["date"]}')
    ls = LIVE_SESSION.get(vid)
    if ls is None or ls.get('data_inicio') != row['date']:
        r.append(f'live session date {ls and ls.get("data_inicio")} != {row["date"]}')
    r += both(meta['pauta'], re.escape(RULE))
    r += both(meta['pauta'], re.escape(meta['subject']))
    r += both(meta['pauta'], re.escape(meta['phrase']))
    if meta['veto'] not in row['detail'].replace(' ', '').replace('Veto', '') and meta['veto'] not in row['detail']:
        r.append('detail names a different veto')
    return r


def check_plan(row):
    c, r = row['_check'], []
    q = row['quote']
    if len(q) > 300:
        r.append(f'quote {len(q)} chars > 300')
    file = c['file']
    sq = re.match(r'2026PB(\d+)_\d+\.pdf', file)
    tse = TSE.get(sq.group(1)) if sq else None
    office, nr = row['subject']['id'].split('-', 1)
    if not tse or tse['DS_CARGO'] != 'GOVERNADOR' or tse['NR_CANDIDATO'] != nr:
        r.append(f'plan file {file} belongs to {tse and (tse["DS_CARGO"], tse["NR_CANDIDATO"])}, claim {row["subject"]["id"]}')
    if ROSTER_GOV.get(nr, {}).get('plano_de_governo', {}).get('file') != file:
        r.append('roster.json maps a different plan file')
    reader = PdfReader(f'raw/plans/{file}')
    page = row['page']
    text = pdfnorm(reader.pages[page - 1].extract_text() or '') if 0 < page <= len(reader.pages) else ''
    if pdfnorm(q) not in text:
        r.append(f'quote not on p. {page}')
    m = re.match(r'D:(\d{4})(\d{2})(\d{2})', (reader.metadata or {}).get('/CreationDate', '') or '')
    if not m or f'{m.group(1)}-{m.group(2)}-{m.group(3)}' != row['date']:
        r.append(f'date {row["date"]} != PDF CreationDate')
    if f'p. {page}' not in row['detail'] or f'p. {page}' not in row['source']['label']:
        r.append('page missing from detail/label')
    return r


def check_questions(qs):
    out = []
    by = {q['id']: q for q in qs}
    def add(i, claim, reasons):
        out.append({'i': i, 'claim': claim, 'status': 'FAIL' if reasons else 'PASS', 'reasons': reasons})
    q = by['pb-cac-arma']['context']
    rs = []
    if '14/02/2023' not in q or SESSION[22453]['sessao']['data_inicio'] != '2023-02-14':
        rs.append('session date')
    rs += both(VOTE_META[22453]['ata'], VOTE_META[22453]['tally_re'])
    if '9 votos SIM' not in q or '15 NÃO' not in q:
        rs.append('context tally text')
    rs += both(VOTE_META[22453]['pauta'], r'321/2022.{0,400}RAZÕES DO VETO: INCONSTITUCIONALIDADE')
    add('q:pb-cac-arma', q, rs)
    q = by['pb-nome-social']['context']
    rs = []
    if '23/09/2025' not in q or SESSION[49945]['sessao']['data_inicio'] != '2025-09-23':
        rs.append('session date')
    rs += both(VOTE_META[49945]['ata'], VOTE_META[49945]['tally_re'])
    if '7 votos SIM' not in q or '24 NÃO' not in q or '1 abstenção' not in q:
        rs.append('context tally text')
    add('q:pb-nome-social', q, rs)
    for vid in VOTE_META:
        add(f'q:rule:{vid}', 'SIM rejeita o veto e aprova o projeto', both(VOTE_META[vid]['pauta'], re.escape(RULE)))
    rs = []
    for needle in [r'§ 6º As polícias militares e os corpos de bombeiros militares, forças auxiliares e reserva do Exército subordinam-se, juntamente com as polícias civis e as polícias penais estaduais e distrital, aos Governadores',
                   r'XXI - normas gerais de organização, efetivos, material bélico, garantias, convocação[^;]{0,80}das polícias militares']:
        if not re.search(needle, CF_LOCAL):
            rs.append(f'cached CF lacks /{needle[:40]}/')
        if CF_LIVE is None or not re.search(needle, CF_LIVE):
            rs.append(f'live CF lacks /{needle[:40]}/')
    add('q:pb-desmilitarizar-pm', by['pb-desmilitarizar-pm']['context'], rs)
    return out


def run(rows):
    res = []
    for i, row in enumerate(rows):
        t = row['_check']['type']
        reasons = check_vote(row) if t == 'alpb_vote' else check_plan(row)
        res.append({'i': i, 'id': row['id'], 'candidateId': row['subject']['id'], 'questionId': row['questionId'], 'status': 'FAIL' if reasons else 'PASS', 'reasons': reasons})
    return res


def controls(rows):
    by = {r['id']: r for r in rows}
    out = []
    def ctl(name, row):
        reasons = check_vote(row) if row['_check']['type'] == 'alpb_vote' else check_plan(row)
        out.append({'control': name, 'status': 'FAIL' if reasons else 'PASS', 'expected': 'FAIL', 'reasons': reasons})
    r = copy.deepcopy(by['rec-alpb-22453-deputado_estadual-22190'])
    r['_check']['voto'] = 'Não'; r['position'] = -1; r['detail'] = r['detail'].replace('SIM', 'NÃO')
    ctl('Wallber Virgolino voted NÃO on veto 321/2022 (he voted SIM)', r)
    r = copy.deepcopy(by['plat-governador-27-pb-concessoes-ppp-p5'])
    r['subject']['id'] = 'governador-80'; r['_check']['file'] = by['plat-governador-80-pb-concessoes-ppp-p3']['_check']['file']
    ctl('Yuri Ezequiel plan says "Ampliar concessões e PPPs" (it is Pedro Coutinho)', r)
    r = copy.deepcopy(by['plat-governador-15-pb-incentivos-fiscais-p55'])
    r['subject']['id'] = 'governador-11'
    ctl('Cícero Lucena plan file belongs to governador-11', r)
    r = copy.deepcopy(next(x for x in rows if x['id'].startswith('rec-alpb-22453-')))
    r['date'] = '2023-02-15'
    ctl('veto 321/2022 voted on 2023-02-15 (it was 2023-02-14)', r)
    qs = json.load(open('alpb/questions.draft.json'))
    bad = copy.deepcopy(qs)
    for q in bad:
        if q['id'] == 'pb-nome-social':
            q['context'] = q['context'].replace('7 votos SIM', '24 votos SIM').replace('24 NÃO', '7 NÃO')
    VOTE_META_SAVE = VOTE_META[49945]['tally_re']
    VOTE_META[49945]['tally_re'] = r'obtendo 24 votos SIM, 07 votos NÃO'
    res = [x for x in check_questions(bad) if x['i'] == 'q:pb-nome-social'][0]
    VOTE_META[49945]['tally_re'] = VOTE_META_SAVE
    out.append({'control': 'veto 214/2025 tally was 24 SIM x 7 NÃO (swapped)', 'status': res['status'], 'expected': 'FAIL', 'reasons': res['reasons']})
    return out


if __name__ == '__main__':
    rows = json.load(open('alpb/evidence.draft.json'))
    qs = json.load(open('alpb/questions.draft.json'))
    claims = run(rows)
    qres = check_questions(qs)
    ctls = controls(rows)
    summary = {
        'evidence_pass': sum(c['status'] == 'PASS' for c in claims), 'evidence_fail': sum(c['status'] == 'FAIL' for c in claims),
        'question_pass': sum(c['status'] == 'PASS' for c in qres), 'question_fail': sum(c['status'] == 'FAIL' for c in qres),
        'controls_failed_as_expected': sum(c['status'] == 'FAIL' for c in ctls), 'controls_total': len(ctls),
    }
    harness_ok = summary['controls_failed_as_expected'] == summary['controls_total']
    summary['harness_ok'] = harness_ok
    json.dump({'claims': claims, 'questions': qres, 'controls': ctls, 'summary': summary}, open('checks/alpb.report.json', 'w'), ensure_ascii=False, indent=1)
    ok_ids = {c['id'] for c in claims if c['status'] == 'PASS'}
    q_fail = {c['i'][2:] for c in qres if c['status'] == 'FAIL' and not c['i'].startswith('q:rule')}
    if harness_ok:
        ev = [{k: v for k, v in r.items() if k != '_check'} | {'checkId': f'check_alpb:{i}'} for i, r in enumerate(rows) if r['id'] in ok_ids and r['questionId'] not in q_fail]
        used = {e['questionId'] for e in ev}
        json.dump(ev, open('alpb/evidence.json', 'w'), ensure_ascii=False, indent=1)
        json.dump([q for q in qs if q['id'] not in q_fail and q['id'] in used], open('alpb/questions.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(summary))
    for c in claims + qres:
        if c['status'] == 'FAIL':
            print('FAIL', c.get('id', c['i']), c['reasons'][:4])
    for c in ctls:
        print('CONTROL', c['status'], c['control'])
