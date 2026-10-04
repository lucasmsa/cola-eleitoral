"""Draft governor-race evidence. Every row carries a `check` spec that checks/check_gov.py re-derives from cached sources."""

ACCESSED = "2026-10-01"
CAMARA_VOTOS = "https://dadosabertos.camara.leg.br/api/v2/votacoes/2209381-100/votos"
AGENCIA_3723 = "https://www.camara.leg.br/noticias/605418-plenario-pode-analisar-projeto-que-amplia-porte-de-armas/"


def yt(video_id, seconds):
    return f"https://www.youtube.com/watch?v={video_id}&t={seconds}s"


def secs(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


ROWS = [
    {
        "id": "gov-governador-22-seg-armas-cd2209381-100",
        "subject": "governador-22",
        "questionId": "seg-armas",
        "kind": "record",
        "position": 1,
        "detail": "Como deputado federal, votou SIM no texto principal do PL 3.723/2019, que tornava menos rigorosas as regras de posse e porte de armas, na Câmara, 05/11/2019.",
        "date": "2019-11-05",
        "source": {"url": CAMARA_VOTOS, "label": "Câmara dos Deputados, Dados Abertos, votos da votação 2209381-100"},
        "check": {"type": "camara_vote", "votos": "raw/v3723_votos.json", "deputadoId": 141422, "expect": "Sim",
                  "direction": {"page": AGENCIA_3723, "text": "torna menos rigorosas as regras para a posse e o porte de armas de fogo (PL 3723/19)"}},
    },
    {
        "id": "gov-governador-22-soc-aborto-cef-2025-07-26",
        "subject": "governador-22",
        "questionId": "soc-aborto",
        "kind": "platform",
        "position": -1,
        "detail": "Em evento do PL Mulher em Campina Grande, afirmou ter votado contra o aborto em todas as votações como deputado e senador.",
        "quote": "Todas as votações contra o aborto, em defesa da vida, teve o voto do deputado e do senador Efraim Filho lá cravado no painel de votações.",
        "date": "2025-07-26",
        "source": {"url": "https://www.congressoemfoco.com.br/noticia/110523/efraim-filho-recebe-apoio-de-michelle-e-do-pl-em-pre-candidatura",
                   "label": "Congresso em Foco, 26/07/2025"},
        "check": {"type": "web_quote", "anchor": "Efraim", "minDate": "2025-01-01"},
    },
    {
        "id": "gov-governador-22-eco-privatizacao-sbt-2026-09-23",
        "subject": "governador-22",
        "questionId": "eco-privatizacao",
        "kind": "platform",
        "position": -1,
        "detail": "No debate do SBT Tambaú, disse que não vai privatizar a Cagepa por ser uma empresa superavitária.",
        "quote": "Não vou privatizar a CAJEPA porque a CAJEPA é um órgão superavitário.",
        "date": "2026-09-23",
        "source": {"url": yt("-Wdp8SfV4PQ", secs("01:10:21")),
                   "label": "Debate TH+ SBT Tambaú, 23/09/2026, YouTube, 01:10:21, legenda automática"},
        "check": {"type": "yt_quote", "mode": "debate", "video": "-Wdp8SfV4PQ", "anchor": "efraim filho, o senhor tem 2 minutos", "title": "23 09 2026"},
    },
    {
        "id": "gov-governador-15-eco-privatizacao-jp-2026-02-05",
        "subject": "governador-15",
        "questionId": "eco-privatizacao",
        "kind": "platform",
        "position": -1,
        "detail": "Como prefeito, disse na Câmara Municipal que o contrato de João Pessoa com a Cagepa não autoriza privatização e que irá à Justiça contra ela.",
        "quote": "O contrato com a Cagepa não autoriza a privatização da concessão. Vamos enfrentar isso judicialmente, porque foi um compromisso assumido na campanha passada e seguimos mantendo nossos compromissos",
        "date": "2026-02-05",
        "source": {"url": "https://jornaldaparaiba.com.br/_/216116", "label": "Jornal da Paraíba, 05/02/2026"},
        "check": {"type": "web_quote", "anchor": "Cícero", "minDate": "2025-01-01"},
    },
    {
        "id": "gov-governador-15-pb-concessoes-ppp-etp-cemiterios",
        "subject": "governador-15",
        "questionId": "pb-concessoes-ppp",
        "kind": "record",
        "position": 1,
        "detail": "Na gestão de Cícero Lucena, a Prefeitura de João Pessoa publicou o estudo técnico para conceder os cemitérios públicos à iniciativa privada, no programa JP Parcerias (agosto de 2023).",
        "date": "2023-08-29",
        "source": {"url": "https://jpparcerias.joaopessoa.pb.gov.br/wp-content/uploads/2023/08/ETP-cemiterios.docx-Documentos-Google.pdf",
                   "label": "Prefeitura de João Pessoa, JP Parcerias, Estudo Técnico Preliminar dos cemitérios (p. 1 e 3)"},
        "check": {"type": "pdf_text", "pdf": "raw/etp_cemiterios.pdf",
                  "pages": {1: "Estudo Técnico Preliminar (ETP) para Concessão dos Cemitérios Públicos do Município de João Pessoa",
                            3: "análise de viabilidade para a realização de concessão dos cemitérios públicos do Município de João Pessoa"},
                  "creation": "20230829", "tenure": {"office": "Prefeito", "place": "João Pessoa", "years": [2020, 2024]}},
    },
    {
        "id": "gov-governador-29-soc-aborto-sofesta-2026-08-25",
        "subject": "governador-29",
        "questionId": "soc-aborto",
        "kind": "platform",
        "position": 1,
        "detail": "Em entrevista à Sofesta FM, defendeu que a decisão sobre o aborto cabe à mulher grávida.",
        "quote": "é a favor que a mulher que tá grávida possa decidir. Cabe a ela essa decisão.",
        "date": "2026-08-25",
        "source": {"url": yt("LvPKwMJdVbE", secs("01:27:14")),
                   "label": "Entrevista com Camilo Duarte, Sofesta FM, 25/08/2026, YouTube, 01:27:14, legenda automática"},
        "check": {"type": "yt_quote", "mode": "interview", "video": "LvPKwMJdVbE", "anchor": "então, senhor, a favor do aborto também", "title": "CAMILO DUARTE", "upload": "20260825"},
    },
    {
        "id": "gov-governador-80-seg-armas-sofesta-2026-09-01",
        "subject": "governador-80",
        "questionId": "seg-armas",
        "kind": "platform",
        "position": -1,
        "detail": "Na Sofesta FM, perguntado se o cidadão deve ter acesso a armas, disse que a população armada passaria a fazer justiça com as próprias mãos.",
        "quote": "parte da população vai andar armada e quando vê uma cena vai querer ser justiceiro, vai querer ser o Batman e vai querer combater o crime",
        "date": "2026-09-01",
        "source": {"url": yt("W1Vm4q95CHY", secs("00:52:10")),
                   "label": "Entrevista com Yuri Ezequiel, Sofesta FM, 01/09/2026, YouTube, 00:52:10, legenda automática"},
        "check": {"type": "yt_quote", "mode": "interview", "video": "W1Vm4q95CHY", "anchor": "tem que ter acesso a arma", "title": "YURI EZEQUIEL", "upload": "20260902"},
    },
]

# Same quotes now ship from pipeline/exec under pb-concessoes-ppp; kept here only as control templates.
CONTROL_TEMPLATES = [
    {
        "id": "gov-governador-15-pb-concessoes-ppp-98fm-2026-09-28",
        "subject": "governador-15",
        "questionId": "pb-concessoes-ppp",
        "kind": "platform",
        "position": -1,
        "detail": "No debate da Rádio 98 FM, respondendo sobre a PPP de saneamento da Cagepa, prometeu cancelar o leilão.",
        "quote": "você me dá uma oportunidade muito importante, porque eu já assumi de público que eu cancelarei esse leilão",
        "date": "2026-09-28",
        "source": {"url": yt("s56ijpZa39Y", secs("01:31:45")),
                   "label": "Debate da Rádio 98 FM (Portal Correio), 28/09/2026, YouTube, 01:31:45, legenda automática"},
        "check": {"type": "yt_quote", "mode": "debate", "video": "s56ijpZa39Y", "anchor": "cícero lucen candidato", "title": "DEBATE - GOVERNO DA PARAÍBA", "upload": "20260928"},
    },
    {
        "id": "gov-governador-29-pb-concessoes-ppp-tvcorreio-2026-09-16",
        "subject": "governador-29",
        "questionId": "pb-concessoes-ppp",
        "kind": "platform",
        "position": -1,
        "detail": "Na TV Correio, perguntado se desfaria a PPP de saneamento da Cagepa, respondeu que sim e que é contra qualquer privatização.",
        "quote": "Sim, nós somos totalmente contrários a qualquer tipo de privatização.",
        "date": "2026-09-16",
        "source": {"url": yt("dvfM_oTDPwQ", secs("00:03:30")),
                   "label": "Entrevista com Camilo Duarte, TV Correio (parte 2), 16/09/2026, YouTube, 00:03:30, legenda automática"},
        "check": {"type": "yt_quote", "mode": "interview", "video": "dvfM_oTDPwQ", "anchor": "desfaria esse trato", "title": "Camilo Duarte", "upload": "20260916"},
    },
]
