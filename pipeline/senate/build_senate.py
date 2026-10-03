"""Draft evidence for the PB Senate candidates (and the new questions) into pipeline/senate/draft.json.

Every row carries a `_ref` that check_senate.py uses to re-derive the claim from the cached primary source.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch import jget  # noqa: E402

ACCESSED = '2026-10-01'
S = 'https://legis.senado.leg.br/dadosabertos'
C = 'https://dadosabertos.camara.leg.br/api/v2'
VEN = 'senador-155'


def src(url, label):
    return {'url': url, 'accessed': ACCESSED, 'label': label}


def br(iso):
    y, m, d = iso[:10].split('-')
    return f'{d}/{m}/{y}'


QUESTIONS = [
    {
        'id': 'seg-maioridade', 'area': 'seguranca', 'offices': ['presidente', 'senador', 'deputado_federal'],
        'statement': 'A maioridade penal deve cair para 16 anos nos crimes mais graves, como os hediondos.',
        'context': ('Em 2015 a Câmara aprovou a PEC 171/1993 (imputabilidade penal do maior de 16 anos): '
                    '323 sim e 155 não no 1º turno, em 01/07/2015, e 320 sim e 152 não no 2º turno, em 19/08/2015.'),
        'sources': [src(f'{C}/votacoes/14493-503', 'Câmara, Dados Abertos, votação 14493-503'),
                    src(f'{C}/votacoes/14493-536', 'Câmara, Dados Abertos, votação 14493-536')],
        '_checks': [('camara_desc', '14493-503', 'Sim: 323; não: 155'), ('camara_desc', '14493-536', 'Sim: 320; não: 152'),
                    ('camara_date', '14493-503', '2015-07-01'), ('camara_date', '14493-536', '2015-08-19'),
                    ('camara_ementa', 14493, 'imputabilidade penal do maior de dezesseis anos')],
    },
    {
        'id': 'eco-6x1', 'area': 'economia', 'offices': ['presidente', 'senador', 'deputado_federal'],
        'statement': 'A escala 6x1 deve acabar, com jornada de até 40 horas e dois dias de descanso por semana, sem redução de salário.',
        'context': ('Em 27/05/2026 a Câmara aprovou a PEC 221/2019 (redução da jornada de trabalho): 472 sim e 22 não no '
                    '1º turno e 461 sim e 19 não no 2º turno. No Senado, a votação em plenário ficou para depois do 1º turno das eleições.'),
        'sources': [src(f'{C}/votacoes/2233802-424', 'Câmara, Dados Abertos, votação 2233802-424'),
                    src(f'{C}/votacoes/2233802-438', 'Câmara, Dados Abertos, votação 2233802-438'),
                    src('https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/senado-oposicao-obstrui-e-fim-da-escala-6x1-nao-vai-plenario',
                        'Agência Brasil, 02/09/2026')],
        '_checks': [('camara_desc', '2233802-424', 'Sim: 472; Não: 22'), ('camara_desc', '2233802-438', 'Sim: 461; Não: 19'),
                    ('camara_date', '2233802-424', '2026-05-27'), ('camara_date', '2233802-438', '2026-05-27'),
                    ('page', 'https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/senado-oposicao-obstrui-e-fim-da-escala-6x1-nao-vai-plenario',
                     'a proposta só deve ser votada após o 1º turno das eleições'),
                    ('page', 'https://agenciabrasil.ebc.com.br/politica/noticia/2026-09/senado-oposicao-obstrui-e-fim-da-escala-6x1-nao-vai-plenario',
                     'A PEC 221/2019 prevê a obrigatoriedade de descanso remunerado de dois dias por semana, sem redução salarial, e reduz a atual jornada de trabalho de 44 para 40 horas semanais')],
    },
    {
        'id': 'seg-stf-mandato', 'area': 'seguranca', 'offices': ['presidente', 'senador'],
        'statement': 'Ministros do STF devem ter mandato com prazo fixo, em vez de cargo vitalício.',
        'context': 'A Constituição garante vitaliciedade aos juízes (art. 95, I), o que inclui os ministros do STF. Mudar isso exige emenda constitucional.',
        'sources': [src('https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', 'Constituição Federal, Planalto')],
        '_checks': [('cf', 'I - vitaliciedade')],
    },
]

CAMARA_SUBJECTS = {  # Câmara deputy id -> 2026 candidate id (identity confirmed in pipeline/record/subjects.json)
    178913: VEN,
}


def camara_subjects():
    subj = dict(CAMARA_SUBJECTS)
    with open(os.path.join(HERE, '..', 'record', 'subjects.json')) as fh:
        for s in json.load(fh):
            if s['house'] == 'camara' and s['candidateId'].startswith('deputado_federal-'):
                subj[s['parlId']] = s['candidateId']
    return subj


def camara_votes(qid, vid, label, low):
    rows = []
    meta = jget(f'{C}/votacoes/{vid}')['dados']
    date = meta['data'][:10]
    votes = jget(f'{C}/votacoes/{vid}/votos')['dados']
    subj = camara_subjects()
    for v in votes:
        d = v['deputado_']
        cid = subj.get(d['id'])
        if not cid:
            continue
        t = v['tipoVoto']
        if t not in ('Sim', 'Não'):
            continue
        pos = 1 if t == 'Sim' else -1
        eid = f'sen-rec-{cid}-{qid}-cd{vid}'
        rows.append({
            'id': eid, 'subject': {'type': 'candidate', 'id': cid}, 'questionId': qid, 'kind': 'record', 'position': pos,
            'detail': f"Votou {t.upper()} na {label}, {br(date)} (então no {d['siglaPartido']}).",
            'date': date, 'source': src(f'{C}/votacoes/{vid}/votos', f'Câmara dos Deputados, Dados Abertos, votação {vid}'),
            'checkId': eid, 'lowDiscrimination': low,
            '_ref': {'type': 'camara_vote', 'votacao': vid, 'deputado': d['id'], 'voto': t, 'date': date},
        })
    return rows


def senado_plenary(qid, sg, n, a, cod, parl, pos_if_sim, detail):
    url = f'{S}/votacao?sigla={sg}&numero={n}&ano={a}'
    vot = [x for x in jget(url) if x['codigoSessaoVotacao'] == cod][0]
    v = [x for x in vot['votos'] if x['codigoParlamentar'] == parl][0]
    t = v['siglaVotoParlamentar']
    pos = pos_if_sim if t == 'Sim' else -pos_if_sim
    eid = f'sen-rec-{VEN}-{qid}-sf{cod}'
    return {
        'id': eid, 'subject': {'type': 'candidate', 'id': VEN}, 'questionId': qid, 'kind': 'record', 'position': pos,
        'detail': detail.format(voto=t.upper(), date=br(vot['dataSessao']), party=v['siglaPartidoParlamentar']),
        'date': vot['dataSessao'][:10], 'source': src(url, f'Senado Federal, Dados Abertos, votação nominal {cod}'),
        'checkId': eid, 'lowDiscrimination': False,
        '_ref': {'type': 'senado_vote', 'url': url, 'cod': cod, 'parl': parl, 'voto': t},
    }


def senado_committee(qid, sg, n, a, cod, parl, pos_if_sim, detail):
    url = f'{S}/votacaoComissao/materia/{sg}/{n}/{a}.json'
    vs = jget(url)['VotacoesComissao']['Votacoes']['Votacao']
    vs = [vs] if isinstance(vs, dict) else vs
    vot = [x for x in vs if x['CodigoVotacao'] == cod][0]
    votos = vot['Votos']['Voto']
    votos = [votos] if isinstance(votos, dict) else votos
    v = [x for x in votos if x['CodigoParlamentar'] == parl][0]
    q = v['QualidadeVoto']
    pos = pos_if_sim if q == 'S' else -pos_if_sim
    date = vot['DataHoraInicioReuniao'][:10]
    eid = f'sen-rec-{VEN}-{qid}-ccj{cod}'
    return {
        'id': eid, 'subject': {'type': 'candidate', 'id': VEN}, 'questionId': qid, 'kind': 'record', 'position': pos,
        'detail': detail.format(voto='SIM' if q == 'S' else 'NÃO', date=br(date)),
        'date': date, 'source': src(url, f'Senado Federal, Dados Abertos, votação em comissão {cod}'),
        'checkId': eid, 'lowDiscrimination': True,
        '_ref': {'type': 'senado_committee', 'url': url, 'cod': cod, 'parl': parl, 'voto': q},
    }


def quote(cid, qid, pos, url, date, quote_text, detail, label, name_forms, date_marker=None):
    eid = f'sen-plat-{cid}-{qid}'
    return {
        'id': eid, 'subject': {'type': 'candidate', 'id': cid}, 'questionId': qid, 'kind': 'platform', 'position': pos,
        'detail': detail, 'quote': quote_text, 'date': date, 'source': src(url, label), 'checkId': eid,
        'lowDiscrimination': False,
        '_ref': {'type': 'web_quote', 'url': url, 'names': name_forms, 'date_marker': date_marker},
    }


CHANNEL = {'cAqSz5F2QCo': 'TV Arapuan, debate para o Senado', 'E40X9ovj42w': 'TV Diário do Sertão, debate para o Senado',
           'zc7d4U8eEnI': 'TV Diário do Sertão/ClickPB, sabatina', 'JNBjm8j4a3E': 'TV Correio, sabatina (parte 1)',
           'PN-anlkjfX8': 'TV Correio, sabatina (parte 1)', 'mG-u03CnNVI': 'TV Correio, sabatina (parte 2)',
           'AcTTehqamac': 'TV Correio, sabatina (parte 2)', 'cvAO0R7h8Vk': 'TV Correio, sabatina (parte 1)',
           'Hgm0PK8-JME': 'TV Correio, sabatina (parte 1)', 'KaW7KGxXXT4': 'TV Correio, sabatina (parte 1)'}


def caption(cid, qid, pos, video, start, quote_text, detail, names, speaker_cue=None, speaker_text=None, fuzzy=None, suffix='', turn_anchor=None):
    with open(os.path.join(HERE, 'raw', 'yt', f'{video}.audio.info.json')) as fh:
        up = json.load(fh)['upload_date']
    parts = [float(x) for x in start.split(':')]
    secs = int(sum(v * 60 ** i for i, v in enumerate(reversed(parts))))
    eid = f'sen-cap-{cid}-{qid}{suffix}'
    return {
        'id': eid, 'subject': {'type': 'candidate', 'id': cid}, 'questionId': qid, 'kind': 'platform', 'position': pos,
        'detail': detail, 'quote': quote_text, 'date': f'{up[:4]}-{up[4:6]}-{up[6:]}',
        'source': src(f'https://www.youtube.com/watch?v={video}&t={secs}s',
                      f'{CHANNEL[video]} (YouTube), {start}; legenda automática original em português do canal'),
        'checkId': eid, 'lowDiscrimination': False,
        '_ref': {'type': 'caption_quote', 'video': video, 'vtt': f'{video}.pt-orig.vtt' if os.path.exists(os.path.join(HERE, 'raw', 'yt', f'{video}.pt-orig.vtt')) else f'{video}.pt.vtt',
                 'start': start, 'names': names, 'speaker_cue': speaker_cue, 'speaker_text': speaker_text, 'turn_anchor': turn_anchor, 'fuzzy': fuzzy or []},
    }


def caption_rows():
    return [
        caption('senador-300', 'seg-maioridade', 1, 'E40X9ovj42w', '01:46:39',
                'Eu vou lutar por baixar a maioridade penal. Adolescente de 16 anos que pratica crime de adulto, ele tem que responder como adulto.',
                'No debate da TV Diário do Sertão (11/09/2026), em resposta a Veneziano, defendeu reduzir a maioridade penal para 16 anos.',
                ['major fábio'], '01:43:12', 'Questionamento agora é do candidato veneziano para o candidato major Fábio',
                turn_anchor='30 segundos agora para tréplica'),
        caption('senador-300', 'seg-saidinha', 1, 'E40X9ovj42w', '01:46:47',
                'E vou lutar também contra as saidinhas dos presídios.',
                'No debate da TV Diário do Sertão, disse que vai lutar contra as saídas temporárias de presos.',
                ['major fábio'], '01:43:12', 'Questionamento agora é do candidato veneziano para o candidato major Fábio',
                turn_anchor='30 segundos agora para tréplica'),
        caption('senador-300', 'seg-drogas', 1, 'JNBjm8j4a3E', '00:02:18',
                'Eu sou contra a legalização das drogas',
                'Na sabatina da TV Correio, declarou ser contra a legalização das drogas.', ['major fábio']),
        caption('senador-300', 'seg-stf-mandato', 1, 'zc7d4U8eEnI', '00:20:04',
                'E ser vitalício num cargo público é muito perigoso.',
                'Na sabatina ClickPB/TV Diário do Sertão, criticou o cargo vitalício e defendeu mandato de 8 a 10 anos para ministros do STF.',
                ['major fábio']),
        caption('senador-222', 'seg-8-janeiro', 1, 'cAqSz5F2QCo', '02:32:26',
                'faz um compromisso de pautar o projeto da anistia das vítimas do 8 de janeiro de 2023 e aí na hora descumpre o compromisso',
                'No debate da TV Arapuan (31/08/2026), criticou a Câmara por não votar a anistia aos condenados do 8 de janeiro e aprovar só a dosimetria.',
                ['queiroga'], '02:25:59', 'mais um confronto ao lado do candidato Marcelo Queiroga', fuzzy=[['8', 'lá']],
                turn_anchor='eu conduzi o Ministério da Saúde'),
        caption('senador-151', 'seg-maioridade', 1, 'cAqSz5F2QCo', '01:25:42',
                'Com certeza, candidato. Nós vamos defender o que é constitucional, o que vai ser discutido da redução da maioridade.',
                'No debate da TV Arapuan, perguntado por Queiroga se votaria a favor da redução da maioridade penal, respondeu que sim.',
                ['gadelha'], '01:23:03', 'precisa convidar o candidato André Gadelha',
                turn_anchor='se compromete comigo a votar a favor dessas'),
        caption('senador-272', 'seg-maioridade', 1, 'PN-anlkjfX8', '00:02:39',
                'E obviamente iremos votar também a favor da redução da maioridade penal.',
                'Na sabatina da TV Correio, disse que votará pela redução da maioridade penal, com 16 anos como limite.', ['rinaldo']),
        caption('senador-272', 'eco-6x1', 1, 'mG-u03CnNVI', '00:03:46',
                'Eu sou totalmente a favor',
                'Na sabatina da TV Correio, perguntado sobre o fim da escala 6x1, disse ser totalmente a favor de reduzir a jornada para 40 horas.', ['rinaldo']),
        caption('senador-272', 'seg-stf-mandato', 1, 'mG-u03CnNVI', '00:02:21',
                'Somos a favor de outro modelo, mas com certeza esse mandato com menor duração é de muita importância.',
                'Na sabatina da TV Correio, defendeu mandato de menor duração para ministros do STF.', ['rinaldo']),
        caption('senador-801', 'eco-6x1', 1, 'AcTTehqamac', '00:02:13',
                'Ela tem que ser modificada, a gente está defendendo as 36 horas',
                'Na sabatina da TV Correio, defendeu ir além da PEC do fim da escala 6x1, com jornada de 36 horas.', ['joão batista']),
        caption('senador-801', 'seg-maioridade', -1, 'cvAO0R7h8Vk', '00:07:20',
                'E acho que essa não é uma medida. a medida investir em educação, em saúde, transporte, lazer e trazer empregos para o povo trabalhar',
                'Na sabatina da TV Correio, disse que reduzir a maioridade penal não é a medida e defendeu investir em educação e emprego.', ['joão batista']),
        caption('senador-800', 'eco-6x1', 1, 'Hgm0PK8-JME', '00:03:31',
                'o que nós defendemos e acho como primeira medida é que a gente derrubar com a escala 6 por1',
                'Na sabatina da TV Correio, apontou o fim da escala 6x1 como sua primeira medida.', ['rosilene']),
        caption('senador-290', 'eco-6x1', 1, 'KaW7KGxXXT4', '00:06:16',
                'Somos a favor, né? Todo o direito eh que venha beneficiar a classe trabalhadoras, nós somos a favor.',
                'Na sabatina da TV Correio, declarou apoio ao fim da escala 6x1 e defendeu ir além, para a escala 4x3.', ['adriano']),
        caption('senador-290', 'seg-maioridade', -1, 'KaW7KGxXXT4', '00:07:35',
                'teríamos que ter uma discussão para aumentar não eh a menoridade, né, mas aumentar o tempo de reeducação desse menor que está interno',
                'Na sabatina da TV Correio, defendeu aumentar o tempo de internação de adolescentes infratores em vez de mudar a maioridade penal.', ['adriano']),
    ]


def build():
    rows = []
    rows.append(senado_plenary(
        'seg-armas', 'PDL', 233, 2019, 5971, 5748, -1,
        'Votou {voto} no PDL 233/2019, que sustou o Decreto 9.785/2019, de flexibilização da posse e do porte de armas, no plenário do Senado, {date} (então no {party}).'))
    rows.append(senado_committee(
        'seg-blindagem', 'PEC', 3, 2021, '38935', '5748', -1,
        'Votou {voto} no relatório da CCJ do Senado que rejeitou a PEC 3/2021 (licença prévia para processar parlamentares), {date}.'))
    rows += camara_votes('seg-maioridade', '14493-503', 'PEC 171/1993 (maioridade penal aos 16 anos), 1º turno na Câmara', False)
    rows += camara_votes('seg-maioridade', '14493-536', 'PEC 171/1993 (maioridade penal aos 16 anos), 2º turno na Câmara', False)
    rows += camara_votes('eco-6x1', '2233802-424', 'PEC 221/2019 (fim da escala 6x1), 1º turno na Câmara', True)
    rows += camara_votes('eco-6x1', '2233802-438', 'PEC 221/2019 (fim da escala 6x1), 2º turno na Câmara', True)

    jp_ven = 'https://jornaldaparaiba.com.br/_/218619'
    pol_nabor = 'https://www.polemicaparaiba.com.br/politica/candidato-ao-senado-nabor-wanderley-defende-fim-da-escala-6x1-e-reducao-da-maioridade-penal-para-crimes-hediondos/'
    pc_queiroga = 'https://portalcorreio.com.br/marcelo-queiroga-quer-mudar-legislacao-das-emendas-no-senado-e-critica-esquerda/'
    newspb_queiroga = 'https://newspb.com.br/marcelo-queiroga-candidato-a-senador-pela-paraiba-diz-ser-contra-o-fim-da-escala-6x1-e-a-favor-da-legislacao-atual-sobre-aborto/'
    pol_fabio = 'https://www.polemicaparaiba.com.br/politica/candidato-ao-senado-major-fabio-contraria-posicao-do-novo-e-defende-fim-da-escala-6x1/'
    ninja = 'https://blogdoninja.com.br/2026/09/11/tv-diario-do-sertao-debate-ao-senado-sobe-o-tom-e-termina-marcado-por-troca-de-farpas/'

    rows += [
        quote(VEN, 'eco-6x1', 1, jp_ven, '2026-06-01',
              'Eu sou a favor da matéria como ela veio da Câmara.',
              'Em sabatina na CBN, defendeu que o Senado vote o texto do fim da escala 6x1 aprovado pela Câmara.',
              'Jornal da Paraíba, 01/06/2026', ['Veneziano']),
        quote('senador-100', 'eco-6x1', 1, pol_nabor, '2026-08-26',
              'Sou a favor do fim da escala 6×1, porque o trabalhador e a trabalhadora precisam ter mais tempo para cuidar da família, para o lazer e para o descanso',
              'Em entrevista à FM 100.5, declarou ser a favor do fim da escala 6x1.',
              'Polêmica Paraíba, 26/08/2026', ['Nabor']),
        quote('senador-100', 'seg-maioridade', 1, pol_nabor, '2026-08-26',
              'Eu sou a favor do fim da maioridade penal para os crimes hediondos.',
              'Em entrevista à FM 100.5, defendeu reduzir a maioridade penal para crimes hediondos.',
              'Polêmica Paraíba, 26/08/2026', ['Nabor']),
        quote('senador-222', 'seg-maioridade', 1, pc_queiroga, '2026-08-19',
              'Na segurança, a redução da maioridade penal. Se um indivíduo com 16 anos pode votar, se ele comete um crime hediondo ele deve pagar por isso.',
              'Em entrevista ao Correio Debate, defendeu a redução da maioridade penal para crimes hediondos.',
              'Portal Correio, 19/08/2026', ['Queiroga'], '19/08/2026'),
        quote('senador-222', 'seg-drogas', 1, pc_queiroga, '2026-08-19',
              'A esquerda quer descriminalizar as drogas, queremos endurecer a legislação para endurecer e colocar os traficantes na cadeia.',
              'Em entrevista ao Correio Debate, criticou a descriminalização das drogas e defendeu endurecer a lei.',
              'Portal Correio, 19/08/2026', ['Queiroga'], '19/08/2026'),
        quote('senador-222', 'eco-6x1', -1, newspb_queiroga, '2026-09-08',
              'Se eu tivesse que votar hoje, eu votaria contrário à 6 por 1 da forma que está',
              'Na sabatina do Bom Dia Paraíba, disse que votaria contra o fim da escala 6x1 no texto em discussão.',
              'NewsPB, 08/09/2026', ['Queiroga']),
        quote('senador-300', 'eco-6x1', 1, pol_fabio, '2026-09-04',
              'Eu sou a favor da PEC que vai diminuir a jornada de trabalho, mas também sou a favor de que o Estado possa dizer de onde vai sair o dinheiro para eles continuarem a ganhar o mesmo salário',
              'Na sabatina do Bom Dia Paraíba, declarou apoio à PEC que reduz a jornada de trabalho, com ressalva sobre o custeio.',
              'Polêmica Paraíba, 04/09/2026', ['Major Fábio']),
        quote('senador-151', 'seg-stf-mandato', 1, ninja, '2026-09-11',
              'Ministro do STF já deveria ter sido cassado. E nós vamos estabelecer prazo de mandato de ministro',
              'No debate da TV Diário do Sertão, defendeu prazo de mandato para ministros do STF.',
              'Blog do Ninja, 11/09/2026', ['André', 'Gadelha']),
    ]
    rows += caption_rows()
    with open(os.path.join(HERE, 'draft.json'), 'w') as fh:
        json.dump({'questions': QUESTIONS, 'evidence': rows}, fh, ensure_ascii=False, indent=1)
    print(len(rows), 'draft rows')
    from collections import Counter
    print(Counter(r['subject']['id'] for r in rows))


if __name__ == '__main__':
    build()
