"""Build ALPB/PB draft questions and evidence from cached raw data. Run from pipeline/: .venv/bin/python alpb/build_alpb.py"""
import json, os, re
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ACCESSED = '2026-09-30'
PLAN_ZIP = 'https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_PB.zip'
CF88 = 'https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm'
SAPL_VOTES = 'https://sapl.al.pb.leg.br/api/sessao/votoparlamentar/?votacao={vid}&page_size=100'

VOTES = {
    22453: {
        'questionId': 'pb-cac-arma',
        'session_date': '2023-02-14',
        'pauta': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/pauta/1187_pauta_sessao.pdf',
        'ata': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1187/ata/1187_ata_sessao.pdf',
        'veto': 'Veto 321/2022 ao PL 3.536/2022 (arma de fogo para atiradores desportivos)',
    },
    49945: {
        'questionId': 'pb-nome-social',
        'session_date': '2025-09-23',
        'pauta': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/pauta/ordem_do_dia_23.09.2025_3a_sessao_ordinaria_itinerante.pdf',
        'ata': 'https://sapl.al.pb.leg.br/media/sapl/public/sessaoplenaria/1350/ata/3_ordinaria_itinerante_2025.pdf',
        'veto': 'Veto 214/2025 ao PL 2.496/2024 (nome social nas contas de água, luz e gás)',
    },
}

VOTE_RULE = 'Na ALPB, votar SIM num veto rejeita o veto e aprova o projeto; votar NÃO mantém o veto (regra impressa na pauta oficial).'

QUESTIONS = [
    {
        'id': 'pb-concessoes-ppp', 'area': 'economia', 'offices': ['governador', 'deputado_estadual'],
        'statement': 'O governo da Paraíba deve ampliar concessões e parcerias público-privadas (PPPs) em obras e serviços públicos.',
        'context': 'Concessões e PPPs passam a construção ou a operação de um serviço público para empresas privadas, por contrato. Os planos de governo registrados no TSE divergem: uns propõem ampliar, outros acabar com elas.',
        'sources': [{'url': PLAN_ZIP, 'accessed': ACCESSED, 'label': 'Planos de governo PB 2026 registrados no TSE'}],
    },
    {
        'id': 'pb-incentivos-fiscais', 'area': 'economia', 'offices': ['governador', 'deputado_estadual'],
        'statement': 'A Paraíba deve continuar dando incentivos fiscais a empresas, cobrando em troca metas de investimento e emprego.',
        'context': 'Incentivo fiscal é imposto que o estado deixa de cobrar para atrair empresas. Alguns planos registrados no TSE mantêm os incentivos com metas; outro propõe acabar com eles.',
        'sources': [{'url': PLAN_ZIP, 'accessed': ACCESSED, 'label': 'Planos de governo PB 2026 registrados no TSE'}],
    },
    {
        'id': 'pb-desmilitarizar-pm', 'area': 'seguranca', 'offices': ['governador', 'deputado_estadual'],
        'statement': 'A Polícia Militar da Paraíba deve ser desmilitarizada.',
        'context': 'A Constituição Federal define as PMs como forças auxiliares e reserva do Exército, subordinadas aos governadores (art. 144, § 6º), e reserva à União as normas gerais de sua organização (art. 22, XXI). Mudar isso depende do Congresso; o governo estadual comanda a PM e define prioridades.',
        'sources': [{'url': CF88, 'accessed': ACCESSED, 'label': 'Constituição Federal, art. 144 § 6º e art. 22 XXI'}],
    },
    {
        'id': 'pb-cac-arma', 'area': 'seguranca', 'offices': ['deputado_estadual'],
        'statement': 'Uma lei estadual deve reconhecer que atiradores esportivos precisam ter arma de fogo pelo risco da atividade.',
        'context': 'Em 14/02/2023 a ALPB votou o veto do governador ao PL 3.536/2022, que fazia esse reconhecimento. O veto, por inconstitucionalidade, foi mantido com 9 votos SIM (derrubar o veto) e 15 NÃO. ' + VOTE_RULE + ' Votações de veto também refletem o alinhamento com o governo estadual, não só a opinião sobre o tema.',
        'sources': [
            {'url': VOTES[22453]['pauta'], 'accessed': ACCESSED, 'label': 'ALPB, pauta da 3ª Sessão Ordinária de 2023'},
            {'url': VOTES[22453]['ata'], 'accessed': ACCESSED, 'label': 'ALPB, ata da 3ª Sessão Ordinária de 2023'},
        ],
    },
    {
        'id': 'pb-nome-social', 'area': 'social', 'offices': ['deputado_estadual'],
        'statement': 'As empresas de água, luz e gás devem poder usar o nome social do consumidor nas contas e comunicações.',
        'context': 'Nome social é o nome pelo qual uma pessoa trans ou travesti se identifica. Em 23/09/2025 a ALPB manteve o veto do governador ao PL 2.496/2024, com 7 votos SIM (derrubar o veto), 24 NÃO e 1 abstenção. ' + VOTE_RULE + ' Votações de veto também refletem o alinhamento com o governo estadual, não só a opinião sobre o tema.',
        'sources': [
            {'url': VOTES[49945]['pauta'], 'accessed': ACCESSED, 'label': 'ALPB, ordem do dia de 23/09/2025'},
            {'url': VOTES[49945]['ata'], 'accessed': ACCESSED, 'label': 'ALPB, ata de 23/09/2025'},
        ],
    },
]

GOV = {'11': 'LUCAS RIBEIRO', '15': 'CÍCERO LUCENA', '22': 'EFRAIM FILHO', '27': 'PEDRO COUTINHO', '29': 'CAMILO DUARTE', '80': 'YURI EZEQUIEL'}

PLATFORM = [
    ('27', 'pb-concessoes-ppp', 1, 2, 'promover uma política agressiva de privatizações e concessões',
     'O plano propõe uma política agressiva de privatizações e concessões (p. 2).'),
    ('27', 'pb-concessoes-ppp', 1, 5, 'Ampliar concessões e Parcerias Público-Privadas em áreas nas quais a iniciativa privada possa contribuir para acelerar investimentos e melhorar serviços.',
     'O plano propõe ampliar concessões e PPPs (p. 5).'),
    ('22', 'pb-concessoes-ppp', 1, 8, 'incentivando a construção de novos hotéis e equipamentos de lazer através de parcerias público-privadas inteligentes.',
     'O plano prevê PPPs para hotéis e equipamentos de lazer no turismo (p. 8).'),
    ('22', 'pb-concessoes-ppp', 1, 10, 'O plano será executado por fases, com parcerias público-privadas e captação de recursos federais.',
     'O plano prevê executar a logística com PPPs (p. 10).'),
    ('80', 'pb-concessoes-ppp', -1, 3, 'Reestatização de empresas estratégicas: Fim definitivo de leilões, parcerias público-privadas (PPPs) e concessões ao capital financeiro.',
     'O plano propõe o fim definitivo de leilões, PPPs e concessões (p. 3).'),
    ('15', 'pb-incentivos-fiscais', 1, 55, 'Garantir que toda nova concessão do FAIN terá metas públicas de investimento, empregos e salários, com devolução proporcional em caso de descumprimento.',
     'O plano mantém os incentivos do FAIN, com metas de investimento e emprego e devolução se descumpridas (p. 55).'),
    ('22', 'pb-incentivos-fiscais', 1, 4, 'Os incentivos serão avaliados por resultados e revisados continuamente, assegurando que cada renúncia fiscal se reverta em empregos e renda comprovados.',
     'O plano mantém os incentivos fiscais, avaliados por resultado em empregos e renda (p. 4).'),
    ('80', 'pb-incentivos-fiscais', -1, 2, 'Fim imediato de todos os subsídios e incentivos fiscais e financeiros concedidos pelo Estado aos monopólios, grandes empresários e agroexportadores, substituídos por auditoria popular.',
     'O plano propõe o fim imediato dos incentivos fiscais a grandes empresas e agroexportadores (p. 2).'),
    ('80', 'pb-desmilitarizar-pm', 1, 5, 'desmilitarização da Polícia Militar: Criação da Polícia Cidadã, fundamentada nos direitos humanos',
     'O plano propõe desmilitarizar a PM e criar uma Polícia Cidadã (p. 5).'),
    ('29', 'pb-desmilitarizar-pm', 1, 5, 'Dissolução da polícia militar e de todo o aparato repressivo',
     'O plano propõe dissolver a Polícia Militar (p. 5).'),
]


def plan_meta(nr):
    d = json.load(open(f'alpb/raw/plans_text/governador-{nr}.json'))
    md = PdfReader(f'raw/plans/{d["file"]}').metadata or {}
    m = re.match(r'D:(\d{4})(\d{2})(\d{2})', md.get('/CreationDate', '') or '')
    return d['file'], (f'{m.group(1)}-{m.group(2)}-{m.group(3)}' if m else None)


def platform_rows():
    rows = []
    for nr, qid, pos, page, quote, detail in PLATFORM:
        file, date = plan_meta(nr)
        rows.append({
            'id': f'plat-governador-{nr}-{qid}-p{page}', 'subject': {'type': 'candidate', 'id': f'governador-{nr}'},
            'questionId': qid, 'kind': 'platform', 'position': pos, 'detail': detail, 'quote': quote, 'page': page,
            'date': date, 'lowDiscrimination': False,
            'source': {'url': PLAN_ZIP, 'accessed': ACCESSED, 'label': f'Plano de governo registrado no TSE ({GOV[nr]}, p. {page}), arquivo {file} em proposta_governo_2026_PB.zip'},
            '_check': {'type': 'plan_quote', 'file': file, 'nr': nr},
        })
    return rows


def record_rows():
    votes = json.load(open('alpb/raw/sessao_votoparlamentar.json'))['results']
    people = json.load(open('alpb/raw/parlamentar_to_2026.json'))
    rows = []
    for vid, meta in VOTES.items():
        for v in votes:
            if v['votacao'] != vid:
                continue
            voto = v['voto'].strip()
            if voto not in ('Sim', 'Não'):
                continue
            p = people[str(v['parlamentar'])]
            for c in p['candidacies']:
                if c['office'] not in ('deputado_estadual', 'deputado_federal', 'governador') or c['on_urna'] != 'SIM':
                    continue
                pos = 1 if voto == 'Sim' else -1
                action = 'derrubar o veto (a favor do projeto)' if pos == 1 else 'manter o veto (contra o projeto)'
                rows.append({
                    'id': f'rec-alpb-{vid}-{c["office"]}-{c["number"]}', 'subject': {'type': 'candidate', 'id': f'{c["office"]}-{c["number"]}'},
                    'questionId': meta['questionId'], 'kind': 'record', 'position': pos,
                    'detail': f'Como deputado(a) estadual, {p["nome_parlamentar"]} votou {voto.upper()} no {meta["veto"]}, em {meta["session_date"][8:]}/{meta["session_date"][5:7]}/{meta["session_date"][:4]}: votou para {action}.',
                    'date': meta['session_date'], 'lowDiscrimination': False,
                    'source': {'url': SAPL_VOTES.format(vid=vid), 'accessed': ACCESSED, 'label': f'ALPB, SAPL, voto nominal (votação {vid})'},
                    '_check': {'type': 'alpb_vote', 'votacao': vid, 'parlamentar': v['parlamentar'], 'voto': voto, 'nome': p['nome_parlamentar'], 'full_name_tse': c['full_name'], 'sq': c['sq']},
                })
    return rows


if __name__ == '__main__':
    json.dump(QUESTIONS, open('alpb/questions.draft.json', 'w'), ensure_ascii=False, indent=1)
    rows = platform_rows() + record_rows()
    json.dump(rows, open('alpb/evidence.draft.json', 'w'), ensure_ascii=False, indent=1)
    print(len(QUESTIONS), 'questions', len(rows), 'draft evidence rows')
