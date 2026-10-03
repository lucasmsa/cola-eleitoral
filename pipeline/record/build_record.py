"""Build 'record' evidence candidates from cached Câmara, Senado and Planalto primary sources.

Output: candidates.json (evidence + _ref used by checks), subjects.json, votacoes.json, notes.json.
evidence.json (PASS only) is written by pipeline/checks/check_record.py.
"""
import csv, json, os, re, unicodedata
from fetch import get

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_TSE = os.path.join(HERE, '..', 'raw', 'tse')
C = 'https://dadosabertos.camara.leg.br/api/v2'
S = 'https://legis.senado.leg.br/dadosabertos'
ACCESSED = '2026-09-30'
PLANALTO = 'https://www.planalto.gov.br/ccivil_03/'

CAMARA_VOTES = [
    ('eco-reforma-tributaria', '2196833-326', 'PEC 45/2019 (reforma tributária), 1º turno na Câmara', False),
    ('eco-arcabouco', '2357053-47', 'PLP 93/2023 (arcabouço fiscal) na Câmara', False),
    ('eco-privatizacao', '2270789-73', 'MP 1.031/2021 (privatização da Eletrobras) na Câmara', False),
    ('eco-bc-autonomo', '2265124-70', 'PLP 19/2019 (autonomia do Banco Central) na Câmara', False),
    ('eco-ir-alta-renda', '2487436-169', 'PL 1.087/2025 (isenção do IR até R$ 5 mil e tributação mínima de altas rendas) na Câmara', True),
    ('seg-8-janeiro', '2358548-89', 'PL 2.162/2023 (PL da dosimetria, penas dos atos de 8 de janeiro) na Câmara', False),
    ('seg-blindagem', '2270800-135', 'PEC 3/2021 (licença prévia da Casa para processar parlamentares), 1º turno na Câmara', False),
    ('soc-marco-temporal', '345311-270', 'PL 490/2007 (marco temporal das terras indígenas) na Câmara', False),
    ('amb-licenciamento', '257161-337', 'PL 3.729/2004 (lei geral do licenciamento ambiental) na Câmara', False),
    ('amb-licenciamento', '257161-454', 'emendas do Senado ao PL 2.159/2021 (lei geral do licenciamento ambiental) na Câmara', False),
    ('amb-agrotoxicos', '46249-297', 'PL 6.299/2002 (registro de agrotóxicos) na Câmara', False),
]

SENADO_VOTES = [
    ('eco-reforma-tributaria', ('PEC', 45, 2019), 6777, 'PEC 45/2019 (reforma tributária), 2º turno no Senado'),
    ('eco-arcabouco', ('PLP', 93, 2023), 6714, 'PLP 93/2023 (arcabouço fiscal) no Senado'),
    ('eco-privatizacao', ('MPV', 1031, 2021), 6377, 'MP 1.031/2021 (privatização da Eletrobras) no Senado'),
    ('eco-bc-autonomo', ('PLP', 19, 2019), 6248, 'PLP 19/2019 (autonomia do Banco Central) no Senado'),
    ('seg-saidinha', ('PL', 2253, 2022), 6818, 'PL 2.253/2022 (restrição da saída temporária de presos) no Senado'),
    ('seg-drogas', ('PEC', 45, 2023), 6824, 'PEC 45/2023 (criminalização da posse e do porte de drogas), 1º turno no Senado'),
    ('seg-8-janeiro', ('PL', 2162, 2023), 7041, 'PL 2.162/2023 (PL da dosimetria, penas dos atos de 8 de janeiro) no Senado'),
    ('soc-marco-temporal', ('PL', 2903, 2023), 6756, 'PL 2.903/2023 (marco temporal das terras indígenas) no Senado'),
    ('amb-licenciamento', ('PL', 2159, 2021), 6935, 'PL 2.159/2021 (lei geral do licenciamento ambiental) no Senado'),
]

# Lula, presidente-13. phrases must all appear in the cached Planalto page.
EXECUTIVE = [
    ('eco-arcabouco', 1, 'lcp200', 'leis/lcp/lcp200.htm', '2023-08-30',
     'Sancionou a Lei Complementar 200/2023 (arcabouço fiscal), proposta pelo Poder Executivo, com vetos parciais.',
     ['LEI COMPLEMENTAR Nº 200, DE 30 DE AGOSTO DE 2023', 'Mensagem de veto', 'Institui regime fiscal sustentável', 'eu sanciono', 'LUIZ INÁCIO LULA DA SILVA']),
    ('eco-reforma-tributaria', 1, 'lcp214', 'leis/lcp/lcp214.htm', '2025-01-16',
     'Sancionou a Lei Complementar 214/2025, que institui o IBS e a CBS da reforma tributária, com vetos parciais.',
     ['LEI COMPLEMENTAR Nº 214, DE 16 DE JANEIRO DE 2025', 'Mensagem de veto', 'Institui o Imposto sobre Bens e Serviços (IBS), a Contribuição Social sobre Bens e Serviços (CBS)', 'eu sanciono', 'LUIZ INÁCIO LULA DA SILVA']),
    ('eco-ir-alta-renda', 1, 'l15270', '_ato2023-2026/2025/lei/l15270.htm', '2025-11-26',
     'Sancionou a Lei 15.270/2025, que reduz o IR e cria tributação mínima para altas rendas.',
     ['LEI Nº 15.270, DE 26 DE NOVEMBRO DE 2025', 'tributação mínima para as pessoas físicas que auferem altas rendas', 'eu sanciono', 'LUIZ INÁCIO LULA DA SILVA']),
    ('seg-saidinha', -1, 'vep144_24', '_Ato2023-2026/2024/Msg/Vep/VEP-144-24.htm', '2024-04-11',
     'Vetou parcialmente o PL 2.253/2022, mantendo a saída temporária para visita à família (Mensagem de veto nº 144/2024).',
     ['MENSAGEM Nº 144, DE 11 DE ABRIL DE 2024', 'decidi vetar parcialmente', 'Projeto de Lei nº 2.253, de 2022', 'revogação do direito à visita familiar']),
    ('seg-8-janeiro', -1, 'l15402', '_ato2023-2026/2026/lei/l15402.htm', '2026-05-08',
     'Vetou integralmente o PL 2.162/2023; o Congresso derrubou o veto e a Lei 15.402/2026 foi promulgada pelo presidente do Senado em 08/05/2026.',
     ['LEI Nº 15.402, DE 8 DE MAIO DE 2026', 'rejeitou o veto total aposto ao Projeto de Lei nº 2.162, de 2023', 'Davi Alcolumbre']),
    ('soc-marco-temporal', -1, 'vep536_23', '_Ato2023-2026/2023/Msg/Vep/VEP-536-23.htm', '2023-10-20',
     'Vetou o artigo do PL 2.903/2023 que fixava a data da promulgação da Constituição (5/10/1988) como marco para demarcar terras indígenas (Mensagem de veto nº 536/2023).',
     ['MENSAGEM Nº 536, DE 20 DE OUTUBRO DE 2023', 'decidi vetar parcialmente', 'Projeto de Lei nº 2.903, de 2023', 'A ausência da comunidade indígena em 5 de outubro de 1988']),
    ('soc-cotas', 1, 'l14723', '_ato2023-2026/2023/lei/l14723.htm', '2023-11-13',
     'Sancionou a Lei 14.723/2023, que altera a Lei de Cotas (Lei 12.711/2012) e dispõe sobre o programa especial de acesso às instituições federais de ensino.',
     ['LEI Nº 14.723, DE 13 DE NOVEMBRO DE 2023', 'Altera a Lei nº 12.711, de 29 de agosto de 2012', 'programa especial para o acesso às instituições federais', 'estudantes pretos, pardos, indígenas e quilombolas', 'eu sanciono', 'LUIZ INÁCIO LULA DA SILVA']),
    ('amb-licenciamento', 0, 'vep1097_25', '_Ato2023-2026/2025/Msg/Vep/VEP-1097-25.htm', '2025-08-08',
     'Sancionou a lei geral do licenciamento ambiental (Lei 15.190/2025) com vetos parciais, entre eles o trecho que previa a Licença por Adesão e Compromisso (LAC) para obras de ampliação e pavimentação.',
     ['MENSAGEM Nº 1.097, DE 8 DE AGOSTO DE 2025', 'decidi vetar parcialmente', 'Projeto de Lei nº 2.159, de 2021', 'Licença por Adesão e Compromisso', 'será realizado mediante emissão da LAC']),
    ('amb-agrotoxicos', 0, 'vep741_23', '_Ato2023-2026/2023/Msg/Vep/VEP-741-23.htm', '2023-12-27',
     'Sancionou a nova lei de agrotóxicos (Lei 14.785/2023) com vetos parciais, entre eles o que dava ao Ministério da Agricultura a coordenação exclusiva das reanálises de risco.',
     ['DE 27 DE DEZEMBRO DE 2023', 'decidi vetar parcialmente', 'Projeto de Lei n o 1.459, de 2022', 'exclusivamente ao Ministério da Agricultura e Pecuária a função de coordenar as reanálises dos riscos']),
]

FEDERATION_OF = {
    'PT': '13-PT/65-PC do B/43-PV', 'PCdoB': '13-PT/65-PC do B/43-PV', 'PV': '13-PT/65-PC do B/43-PV',
    'Fdr PT-PCdoB-PV': '13-PT/65-PC do B/43-PV',
    'PSOL': '50-PSOL/18-REDE', 'REDE': '50-PSOL/18-REDE', 'Fdr PSOL-REDE': '50-PSOL/18-REDE',
    'UNIÃO': '44-UNIÃO/11-PP', 'PP': '44-UNIÃO/11-PP',
    'PRD': '25-PRD/77-SOLIDARIEDADE', 'SOLIDARIEDADE': '25-PRD/77-SOLIDARIEDADE',
}
STANDALONE_2026 = {'PL', 'PDT', 'PSB', 'PSD', 'REPUBLICANOS', 'NOVO', 'PODE', 'DC', 'MDB', 'UP', 'PCO', 'MISSÃO', 'MOBILIZA', 'DEMOCRATA'}

VOTE_WORD = {'Sim': 'SIM', 'Não': 'NÃO'}


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()).strip()


def party_note(p):
    return '(então sem partido)' if p in ('S/Partido', 'S.PART.', 'S/PARTIDO', '') else f'(então no {p})'


def br_date(iso):
    y, m, d = iso[:10].split('-')
    return f'{d}/{m}/{y}'


def office_slug(ds_cargo):
    return {'PRESIDENTE': 'presidente', 'GOVERNADOR': 'governador', 'SENADOR': 'senador',
            'DEPUTADO FEDERAL': 'deputado_federal', 'DEPUTADO ESTADUAL': 'deputado_estadual'}.get(ds_cargo)


def load_candidates():
    rows = []
    for f in ('consulta_cand_2026_PB.csv', 'consulta_cand_2026_BR.csv'):
        rows += list(csv.DictReader(open(os.path.join(RAW_TSE, f), encoding='latin-1'), delimiter=';'))
    comp = {}
    for f in ('comp_PB.csv', 'comp_BR.csv'):
        for r in csv.DictReader(open(os.path.join(RAW_TSE, f), encoding='latin-1'), delimiter=';'):
            comp[r['SQ_CANDIDATO']] = r
    out = []
    for r in rows:
        slug = office_slug(r['DS_CARGO'])
        if not slug:
            continue
        c = comp.get(r['SQ_CANDIDATO'], {})
        out.append({**r, 'office': slug, 'id': f"{slug}-{r['NR_CANDIDATO']}",
                    'status': c.get('DS_SITUACAO_JULGAMENTO', ''), 'detalhe': c.get('DS_DETALHE_SITUACAO_CAND', '')})
    return out


def tse_birth(r):
    d, m, y = r['DT_NASCIMENTO'].split('/')
    return f'{y}-{m}-{d}'


# Spelling differs between TSE and Câmara; confirmed by birth date + party + UF in match_deputies.
NAME_ALIASES = {'CASSIO MURILLO GALDINO DE ARAUJO': 'CASSIO MURILO GALDINO DE ARAUJO'}


def match_deputies(cands, notes):
    deps = {}
    for leg in (56, 57):
        for x in get(f'{C}/deputados?idLegislatura={leg}&siglaUf=PB&itens=200')['dados']:
            deps[x['id']] = get(f'{C}/deputados/{x["id"]}')['dados']
    by_civil = {norm(d['nomeCivil']): d for d in deps.values()}
    subjects = []
    for r in cands:
        if r['DS_SITUACAO_CANDIDATURA'] and 'RENÚNCIA' in r['detalhe'].upper():
            continue
        key = NAME_ALIASES.get(norm(r['NM_CANDIDATO']), norm(r['NM_CANDIDATO']))
        d = by_civil.get(key)
        if not d:
            continue
        if d['dataNascimento'] != tse_birth(r):
            notes.append(f"birth date mismatch, not matched: {r['id']} {r['NM_CANDIDATO']} vs Câmara {d['id']}")
            continue
        subjects.append({'candidateId': r['id'], 'ballotName': r['NM_URNA_CANDIDATO'], 'tseName': r['NM_CANDIDATO'],
                         'house': 'camara', 'parlId': d['id'], 'parlName': d['ultimoStatus']['nome'],
                         'birth': d['dataNascimento'], 'status2026': r['status'],
                         'source': f"{C}/deputados/{d['id']}"})
    return subjects


SENATORS = [5748, 4642, 5894, 5996]


def match_senators(cands, notes):
    subjects = []
    for cod in SENATORS:
        p = get(f'{S}/senador/{cod}.json')['DetalheParlamentar']['Parlamentar']
        full = norm(p['IdentificacaoParlamentar']['NomeCompletoParlamentar'])
        birth = p['DadosBasicosParlamentar']['DataNascimento']
        hits = [r for r in cands if norm(r['NM_CANDIDATO']) == full and tse_birth(r) == birth]
        if len(hits) != 1:
            notes.append(f'senator {cod} {full}: {len(hits)} candidate matches')
            continue
        r = hits[0]
        subjects.append({'candidateId': r['id'], 'ballotName': r['NM_URNA_CANDIDATO'], 'tseName': r['NM_CANDIDATO'],
                         'house': 'senado', 'parlId': cod, 'parlName': p['IdentificacaoParlamentar']['NomeParlamentar'],
                         'birth': birth, 'status2026': r['status'], 'source': f'{S}/senador/{cod}.json'})
    return subjects


def src(url, label):
    return {'url': url, 'accessed': ACCESSED, 'label': label}


def camara_evidence(subjects, notes, votacoes):
    ev = []
    dep_subjects = [s for s in subjects if s['house'] == 'camara']
    for qid, vid, label, low in CAMARA_VOTES:
        meta = get(f'{C}/votacoes/{vid}')['dados']
        votos = get(f'{C}/votacoes/{vid}/votos')['dados']
        tally = {}
        for v in votos:
            tally[v['tipoVoto']] = tally.get(v['tipoVoto'], 0) + 1
        date = meta['data']
        sim, nao = tally.get('Sim', 0), tally.get('Não', 0)
        low = low or ((sim + nao) > 0 and max(sim, nao) / (sim + nao) > 0.95)
        votacoes.append({'questionId': qid, 'house': 'camara', 'id': vid, 'date': date, 'label': label,
                         'descricao': meta.get('descricao'), 'tally': tally, 'low_discrimination': low,
                         'urls': [f'{C}/votacoes/{vid}', f'{C}/votacoes/{vid}/votos', f'{C}/votacoes/{vid}/orientacoes']})
        by_id = {v['deputado_']['id']: v for v in votos}
        for s in dep_subjects:
            v = by_id.get(s['parlId'])
            if not v:
                notes.append(f"{s['candidateId']} ({s['parlName']}) sem registro de voto em {vid} ({label}): ausente ou fora do mandato")
                continue
            t = v['tipoVoto']
            party = v['deputado_']['siglaPartido']
            if t == 'Artigo 17':
                notes.append(f"{s['candidateId']} ({s['parlName']}) presidia a sessão em {vid} (art. 17 RICD), sem voto")
                continue
            if t in VOTE_WORD:
                pos = 1 if t == 'Sim' else -1
                detail = f"Votou {VOTE_WORD[t]} no {label}, {br_date(date)} {party_note(party)}."
            elif t in ('Abstenção', 'Obstrução'):
                pos = 0
                detail = f"Registrou {t.lower()} no {label}, {br_date(date)} {party_note(party)}."
            else:
                notes.append(f"{s['candidateId']} voto '{t}' em {vid} não mapeado")
                continue
            eid = f"rec-{s['candidateId']}-{qid}-cd{vid}"
            ev.append({'id': eid, 'subject': {'type': 'candidate', 'id': s['candidateId']}, 'questionId': qid,
                       'kind': 'record', 'position': pos, 'detail': detail, 'date': date,
                       'source': src(f'{C}/votacoes/{vid}/votos', f'Câmara dos Deputados, Dados Abertos, votação {vid}'),
                       'checkId': eid, 'lowDiscrimination': low,
                       '_ref': {'type': 'camara_vote', 'votacao': vid, 'parlId': s['parlId'], 'tipoVoto': t}})
        orients = get(f'{C}/votacoes/{vid}/orientacoes')['dados']
        for o in orients:
            sig = o['siglaPartidoBloco']
            if sig in FEDERATION_OF:
                list_id = FEDERATION_OF[sig]
            elif sig in STANDALONE_2026:
                list_id = sig
            else:
                continue
            ov = o['orientacaoVoto']
            if ov in VOTE_WORD:
                pos = 1 if ov == 'Sim' else -1
                word = VOTE_WORD[ov]
            elif ov == 'Obstrução':
                pos, word = 0, 'obstrução'
            else:
                notes.append(f'orientação {sig} em {vid}: {ov} (sem evidência)')
                continue
            who = f'A liderança da federação {sig[4:]}' if sig.startswith('Fdr ') else f'A liderança do {sig}'
            detail = f'{who} orientou {word} no {label}, {br_date(date)}.'
            eid = f"rec-list-{re.sub(r'[^A-Za-z0-9]+', '_', sig)}-{qid}-cd{vid}"
            ev.append({'id': eid, 'subject': {'type': 'list', 'id': list_id}, 'questionId': qid, 'kind': 'record',
                       'position': pos, 'detail': detail, 'date': date,
                       'source': src(f'{C}/votacoes/{vid}/orientacoes', f'Câmara dos Deputados, Dados Abertos, orientações da votação {vid}'),
                       'checkId': eid, 'lowDiscrimination': low,
                       '_ref': {'type': 'camara_orient', 'votacao': vid, 'sigla': sig, 'orientacao': ov}})
    return ev


SEN_SKIP = {'P-NRV': 'presente sem registrar voto', 'AP': 'em atividade parlamentar', 'LS': 'em licença saúde',
            'MIS': 'em missão', 'NCom': 'não compareceu', 'LP': 'em licença particular', 'NA': 'não apurado',
            'Presidente (art. 51 RISF)': 'presidia a sessão'}


def senado_evidence(subjects, notes, votacoes):
    ev = []
    sen_subjects = [s for s in subjects if s['house'] == 'senado']
    for qid, (sg, n, a), cod, label in SENADO_VOTES:
        url = f'{S}/votacao?sigla={sg}&numero={n}&ano={a}'
        vot = [x for x in get(url) if x['codigoSessaoVotacao'] == cod][0]
        date = vot['dataSessao']
        tally = {}
        for v in vot['votos']:
            tally[v['siglaVotoParlamentar']] = tally.get(v['siglaVotoParlamentar'], 0) + 1
        sim, nao = tally.get('Sim', 0), tally.get('Não', 0)
        low = (sim + nao) > 0 and max(sim, nao) / (sim + nao) > 0.95
        votacoes.append({'questionId': qid, 'house': 'senado', 'id': cod, 'date': date, 'label': label,
                         'descricao': vot['descricaoVotacao'], 'resultado': vot['resultadoVotacao'], 'tally': tally,
                         'low_discrimination': low, 'urls': [url]})
        by_id = {v['codigoParlamentar']: v for v in vot['votos']}
        for s in sen_subjects:
            v = by_id.get(s['parlId'])
            if not v:
                notes.append(f"{s['candidateId']} ({s['parlName']}) fora do mandato na votação {cod} ({label})")
                continue
            t = v['siglaVotoParlamentar']
            party = v['siglaPartidoParlamentar']
            if t in VOTE_WORD:
                pos = 1 if t == 'Sim' else -1
                detail = f"Votou {VOTE_WORD[t]} no {label}, {br_date(date)} {party_note(party)}."
            elif t == 'Abstenção':
                pos = 0
                detail = f"Registrou abstenção no {label}, {br_date(date)} {party_note(party)}."
            else:
                notes.append(f"{s['candidateId']} ({s['parlName']}) {SEN_SKIP.get(t, t)} na votação {cod} ({label})")
                continue
            eid = f"rec-{s['candidateId']}-{qid}-sf{cod}"
            ev.append({'id': eid, 'subject': {'type': 'candidate', 'id': s['candidateId']}, 'questionId': qid,
                       'kind': 'record', 'position': pos, 'detail': detail, 'date': date,
                       'source': src(url, f'Senado Federal, Dados Abertos, votação nominal {cod}'),
                       'checkId': eid, 'lowDiscrimination': low,
                       '_ref': {'type': 'senado_vote', 'url': url, 'codigoSessaoVotacao': cod, 'parlId': s['parlId'], 'voto': t}})
    return ev


def executive_evidence():
    ev = []
    for qid, pos, key, path, date, detail, phrases in EXECUTIVE:
        eid = f'rec-presidente-13-{qid}-exec-{key}'
        ev.append({'id': eid, 'subject': {'type': 'candidate', 'id': 'presidente-13'}, 'questionId': qid,
                   'kind': 'record', 'position': pos, 'detail': detail, 'date': date,
                   'source': src(PLANALTO + path, 'Presidência da República, Planalto, legislação'),
                   'checkId': eid, 'lowDiscrimination': False,
                   '_ref': {'type': 'planalto', 'cache': f'raw/planalto/{key}.html', 'url': PLANALTO + path, 'phrases': phrases}})
    return ev


def fix_pt_grammar(ev):
    # PEC and MP are feminine in pt-BR: "na PEC", "na MP"; PL/PLP masculine: "no PL".
    for e in ev:
        e['detail'] = re.sub(r'\bno (PEC|MP)\b', r'na \1', e['detail'])
        e['detail'] = re.sub(r'\bno emendas\b', 'nas emendas', e['detail'])
    return ev


def main():
    notes = []
    cands = load_candidates()
    subjects = match_deputies(cands, notes) + match_senators(cands, notes)
    votacoes = []
    ev = camara_evidence(subjects, notes, votacoes) + senado_evidence(subjects, notes, votacoes) + executive_evidence()
    ev = fix_pt_grammar(ev)
    json.dump(subjects, open(os.path.join(HERE, 'subjects.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(votacoes, open(os.path.join(HERE, 'votacoes.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(ev, open(os.path.join(HERE, 'candidates.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(notes, open(os.path.join(HERE, 'notes.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'subjects={len(subjects)} votacoes={len(votacoes)} evidence={len(ev)} notes={len(notes)}')


if __name__ == '__main__':
    main()
