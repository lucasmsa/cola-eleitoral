"""Draft evidence for João Azevêdo (senador-400) and Lucas Ribeiro (governador-11).

Each row carries `checks`: the assertions check_exec.py runs against cached primary or press sources.
Only rows that pass are copied to evidence.json by the check script.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
ACC = "2026-10-01"
TSE_PLAN_PB = "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_PB.zip"

U = {
    "carta_rt": "https://rn.cut.org.br/noticias/governadores-do-nordeste-lancam-carta-de-apoio-pela-aprovacao-da-reforma-tributa-4ed1",
    "carta_rt_data": "https://www.terra.com.br/economia/dinheiro-em-acao/consorcio-de-governadores-do-nordeste-divulga-carta-em-apoio-a-aprovacao-da-reforma-tributaria,63b9337f3fa349c01f46f724a44ea27fe2nh51i0.html",
    "eletrobras": "https://www.congressoemfoco.com.br/noticia/51529/eletrobras-prvatizacao-governadores-nordeste",
    "anistia": "https://www.pbagora.com.br/noticia/politica/ouca-joao-azevedo-avalia-como-absurda-pec-da-blindagem-e-critica-pl-da-anistia-e-preciso-punir-os-que-cometeram-crimes/",
    "blindagem": "https://www.clickpb.com.br/politica/joao-azevedo-pec-blindagem.html",
    "armas_2024": "https://www.clickpb.com.br/paraiba/joao-azevedo-rebate-criticas-sobre-aumento-da-criminalidade-e-diz-que-no-governo-bolsonaro-era-pior.html",
    "armas_2019": "https://www.brasildefato.com.br/2019/05/21/governadores-de-13-estados-divulgam-carta-aberta-contra-decreto-de-armas-de-bolsonaro",
    "lei_12169": "http://sapl.al.pb.leg.br/media/sapl/public/normajuridica/2021/14823/14823_texto_integral.pdf",
    "cagepa": "https://www.clickcz.com.br/2026/05/18/lucas-ribeiro-diz-que-cagepa-seguira-publica-e-acusa-adversarios-de-espalharem-mentiras-sobre-ppp-do-saneamento/",
    "ppp": "https://movimentoeconomico.com.br/saneamento/2026/05/15/acciona-vence-ppp-da-cagepa-com-r-3-bilhoes-e-unico-lance-na-b3/",
    "doe_fain": "https://auniao.pb.gov.br/servicos/doe/2026/julho/diario-oficial-25-07-2026-portal.pdf",
    "lei_14657": "https://sapl.al.pb.leg.br/media/sapl/public/normajuridica/2026/19116/lei_14.657.pdf",
    "lei_12713": "http://sapl.al.pb.leg.br/media/sapl/public/normajuridica/2023/16224/16224_texto_integral.pdf",
    "ata_0704": "https://sapl3.al.pb.leg.br/media/sapl/public/sessaoplenaria/1391/ata/13_extraordinaria_2026.pdf",
}


def src(url, label):
    return {"url": url, "accessed": ACC, "label": label}


def row(rid, subject, qid, kind, position, detail, date, source, checks, quote=None, page=None):
    r = {"id": rid, "subject": {"type": "candidate", "id": subject}, "questionId": qid, "kind": kind,
         "position": position, "detail": detail, "date": date, "source": source, "checkId": rid, "checks": checks}
    if quote:
        r["quote"] = quote
    if page:
        r["page"] = page
    return r


JOAO, LUCAS = "senador-400", "governador-11"

rows = [
    row("exec-senador-400-eco-reforma-tributaria-carta-cn-2023", JOAO, "eco-reforma-tributaria", "platform", 1,
        "Como presidente do Consórcio Nordeste, assinou com os outros oito governadores da região a carta de apoio à aprovação da PEC 45/2019 (reforma tributária), em julho de 2023.",
        "2023-07-05", src(U["carta_rt"], "Carta de Apoio do Consórcio Nordeste pela aprovação da Reforma Tributária (íntegra publicada pela CUT-RN)"),
        [{"web": U["carta_rt"], "contains": ["A Reforma Tributária proposta pela PEC 45/2019 é uma vitória para a sociedade brasileira",
                                             "João Azevêdo (Presidente Consórcio Nordeste) - Governador da Paraíba"]},
         {"web": U["carta_rt_data"], "contains": ["uma carta em apoio à aprovação da reforma tributária"], "published": "2023-07-05"}],
        quote="A Reforma Tributária proposta pela PEC 45/2019 é uma vitória para a sociedade brasileira."),
    row("exec-senador-400-eco-privatizacao-carta-cn-2021", JOAO, "eco-privatizacao", "platform", -1,
        "Como governador da Paraíba, integrou a carta conjunta dos nove governadores do Nordeste contra a privatização da Eletrobras, divulgada em 19/05/2021.",
        "2021-05-19", src(U["eletrobras"], "Congresso em Foco, 19/05/2021"),
        [{"web": U["eletrobras"], "contains": ["Os governadores dos nove estados do Nordeste divulgaram nesta quarta-feira (19) uma carta conjunta contra a privatização da Eletrobras",
                                               "Este processo de desestatização, além de impactar a tarifa de energia para os consumidores, abrirá caminho para a precarização na prestação do serviço"],
          "published": "2021-05-19"},
         {"governor_on": "2021-05-19", "expect": "JOAO"}],
        quote="Este processo de desestatização, além de impactar a tarifa de energia para os consumidores, abrirá caminho para a precarização na prestação do serviço"),
    row("exec-senador-400-seg-8-janeiro-pbagora-2025", JOAO, "seg-8-janeiro", "platform", -1,
        "Em entrevista em setembro de 2025, disse ser contra anistiar quem atentou contra a democracia e contra uma anistia geral e irrestrita.",
        "2025-09-18", src(U["anistia"], "PB Agora, 18/09/2025"),
        [{"web": U["anistia"], "contains": ["Não se pode, de forma nenhuma, anistiar quem atentou contra a democracia",
                                            "Eu particularmente sou contra anistia geral e irrestrita"],
          "near": ["Azevêdo", "João"], "published": "2025-09-18"}],
        quote="Não se pode, de forma nenhuma, anistiar quem atentou contra a democracia."),
    row("exec-senador-400-seg-blindagem-clickpb-2025", JOAO, "seg-blindagem", "platform", -1,
        "Criticou a PEC da Blindagem, que exigiria licença do Congresso para processar parlamentares.",
        "2025-09-22", src(U["blindagem"], "ClickPB, 22/09/2025"),
        [{"web": U["blindagem"], "contains": ["Não se pode ter a criação de castas de pessoas privilegiadas, que é o que a PEC da Blindagem estava tentando fazer"],
          "near": ["Azevêdo"], "published": "2025-09-22"}],
        quote="Não se pode ter a criação de castas de pessoas privilegiadas, que é o que a PEC da Blindagem estava tentando fazer"),
    row("exec-senador-400-seg-armas-clickpb-2024", JOAO, "seg-armas", "platform", -1,
        "Como governador, chamou de irresponsável a liberação de armas do governo anterior.",
        "2024-04-18", src(U["armas_2024"], "ClickPB, 18/04/2024"),
        [{"web": U["armas_2024"], "contains": ["Infelizmente nós passamos quatro anos em que a liberação das armas foi feita de uma forma totalmente irresponsável"],
          "near": ["Azevêdo"], "published": "2024-04-18"}],
        quote="Infelizmente nós passamos quatro anos em que a liberação das armas foi feita de uma forma totalmente irresponsável, onde pessoas que se diziam sócio de um clube tiro podiam comprar mais de 600 armas"),
    row("exec-senador-400-seg-armas-carta-2019", JOAO, "seg-armas", "platform", -1,
        "Assinou em 21/05/2019, com governadores de 13 estados e do DF, carta pedindo a revogação do decreto que flexibilizou armas e munições.",
        "2019-05-21", src(U["armas_2019"], "Brasil de Fato, 21/05/2019, íntegra da carta"),
        [{"web": U["armas_2019"], "contains": ["julgamos que as medidas previstas pelo decreto não contribuirão para tornar nossos estados mais seguros",
                                               "João Azevedo (PSB-PB)", "21.maio.2019"]}],
        quote="julgamos que as medidas previstas pelo decreto não contribuirão para tornar nossos estados mais seguros"),
    # Lei 12.169/2021 (quotas in state civil-service exams) was dropped: soc-cotas asks about university admission.
    row("exec-governador-11-eco-privatizacao-clickcz-2026", LUCAS, "eco-privatizacao", "platform", -1,
        "Como governador, disse que a Cagepa não foi e não será privatizada.",
        "2026-05-18", src(U["cagepa"], "ClickCZ, 18/05/2026"),
        [{"web": U["cagepa"], "contains": ["Não privatizamos, nem vamos privatizar a Cagepa"], "near": ["Lucas Ribeiro"], "published": "2026-05-18"}],
        quote="Não privatizamos, nem vamos privatizar a Cagepa. A Cagepa continuará pública, continuará pertencendo ao Governo da Paraíba e continuará comandando o abastecimento de água e esgotamento sanitário do Estado"),
    row("exec-governador-11-pb-incentivos-fiscais-plano", LUCAS, "pb-incentivos-fiscais", "platform", 1,
        "O plano de governo registrado no TSE propõe atrair indústrias com uma política de incentivos fiscais orientada à geração de emprego e renda (p. 21).",
        "2026-08-13", src(TSE_PLAN_PB, "Plano de governo registrado no TSE (LUCAS RIBEIRO, p. 21), arquivo 2026PB150002551789_01.pdf"),
        [{"pdf": "../raw/plans/2026PB150002551789_01.pdf", "page": 21,
          "contains": ["Atrair novas plantas industriais por meio de uma política de incentivos fiscais competitiva, transparente e orientada à geração de emprego e renda"]}],
        quote="Atrair novas plantas industriais por meio de uma política de incentivos fiscais competitiva, transparente e orientada à geração de emprego e renda", page=21),
    row("exec-governador-11-pb-incentivos-fiscais-decreto-48520", LUCAS, "pb-incentivos-fiscais", "record", 1,
        "Como governador, ratificou pelo Decreto 48.520, de 24/07/2026, resoluções do Conselho do FAIN que concedem crédito presumido de ICMS a indústrias.",
        "2026-07-24", src(U["doe_fain"], "Diário Oficial do Estado da Paraíba nº 18.637, 25/07/2026"),
        [{"pdf": "raw/sapl/doe_2026-07-25.pdf", "url": U["doe_fain"], "page": 1,
          "contains": ["DECRETO Nº 48.520 DE 24 DE JULHO DE 2026", "do Conselho Delibera- tivo do FAIN, que aprovam a concessão de crédito presumido de ICMS", "O GOVERNADOR DO ESTADO DA PARAÍBA"]},
         {"governor_on": "2026-07-24", "expect": "LUCAS"}],
        quote="Ratifica as Resoluções Nºs 029, 030, 031, 032, 033, 034, 035, 036, 037, 038, 039, 040, 041, 042, 043, 053/2026, do Conselho Deliberativo do FAIN, que aprovam a concessão de crédito presumido de ICMS"),
    row("exec-governador-11-amb-licenciamento-lei-14657", LUCAS, "amb-licenciamento", "record", 1,
        "Sancionou a Lei 14.657/2026, que passou a exigir EIA/RIMA só de usinas hidrelétricas e termelétricas acima de 300 MW (antes, abaixo de 300 MW) e, na modernização por fonte menos poluente, só acima de 500 MW. Não trata de autolicenciamento.",
        "2026-08-12", src(U["lei_14657"], "ALPB, SAPL, Lei Ordinária nº 14.657/2026, texto assinado"),
        [{"pdf": "raw/sapl/lei_14.657.pdf", "url": U["lei_14657"],
          "contains": ["Faço saber que o Poder Legislativo decreta e eu sanciono a seguinte Lei",
                       "XV - Usinas Hidrelétricas - UHE e Usinas Termelétricas - UTE com capacidade instalada superior a 300 (trezentos) MW",
                       "LUCAS RIBEIRO NOVAIS DE ARAÚJO Governador"]},
         {"pdf": "raw/sapl/16224_texto_integral.pdf", "url": U["lei_12713"],
          "contains": ["XV - Usinas Hidrelétricas - UHE e Usinas Termelétricas - UTE com capacidade instalada inferior a 300 (trezentos) MW"]},
         {"norma": "14657", "data": "2026-08-12"}],
        quote="XV - Usinas Hidrelétricas - UHE e Usinas Termelétricas - UTE com capacidade instalada superior a 300 (trezentos) MW, e seus sistemas associados"),
]

YT = "https://www.youtube.com/watch?v="
rows += [
    row("exec-senador-400-eco-reforma-tributaria-debate-arapuan", JOAO, "eco-reforma-tributaria", "platform", 1,
        "No debate da TV Arapuan para o Senado, defendeu a reforma tributária aprovada como um sistema mais justo.",
        "2026-08-31", src(YT + "cAqSz5F2QCo&t=4908s", "TV Arapuan, debate para senador, 31/08/2026, em 1:21:48 (legenda automática do YouTube)"),
        [{"vtt": "raw/yt/cAqSz5F2QCo.pt.vtt", "video": "cAqSz5F2QCo", "at": 4908, "channel": "TV ARAPUAN", "title_contains": "DEBATE PARA SENADOR",
          "contains": "nós vamos ter um sistema muito mais justo que vai trazer benefícios para esse país",
          "cues": [{"phrase": "governador josevedo", "within": [-40, 0]},
                   {"phrase": "candidato joão azevedo volta para o seu lugar", "within": [0, 120]}]}],
        quote="nós vamos ter um sistema muito mais justo que vai trazer benefícios para esse país"),
    row("exec-senador-400-eco-6x1-correio-sabatina", JOAO, "eco-6x1", "platform", 1,
        "Na sabatina da TV Correio, disse ser plenamente a favor de acabar com a escala 6x1 e passar de 44 para 40 horas semanais.",
        "2026-08-25", src(YT + "Ocyi7pnQA94&t=160s", "TV Correio, sabatina com João Azevêdo (parte 2), 25/08/2026, em 0:02:40 (legenda automática do YouTube)"),
        [{"vtt": "raw/yt/Ocyi7pnQA94.pt-orig.vtt", "video": "Ocyi7pnQA94", "at": 160, "channel": "TV Correio", "title_contains": "Sabatina com João Azevêdo",
          "contains": "eu sou plenamente a favor dessa dessa alteração da legislação trabalhista",
          "cues": [{"phrase": "o fim da escala 6 por1", "within": [-90, 0]},
                   {"phrase": "saindo de 44 para 40 horas", "within": [-60, 0]}]}],
        quote="eu sou plenamente a favor dessa dessa alteração da legislação trabalhista"),
]

controls = [
    row("NEG-gadelha-stf-mandato-as-joao", JOAO, "seg-stf-mandato", "platform", 1, "control", "2026-08-31", src(YT + "cAqSz5F2QCo", "x"),
        [{"vtt": "raw/yt/cAqSz5F2QCo.pt.vtt", "video": "cAqSz5F2QCo", "at": 5235, "channel": "TV ARAPUAN", "title_contains": "DEBATE PARA SENADOR",
          "contains": "os ministros do supremo que são escolhidos pelos senadores eles também possam ter tempo de mandato",
          "cues": [{"phrase": "candidato joão azevedo volta para o seu lugar", "within": [0, 120]}]}]),
    row("NEG-joao-against-6x1-fabricated", JOAO, "eco-6x1", "platform", -1, "control", "2026-08-25", src(YT + "Ocyi7pnQA94", "x"),
        [{"vtt": "raw/yt/Ocyi7pnQA94.pt-orig.vtt", "video": "Ocyi7pnQA94", "at": 160, "channel": "TV Correio", "title_contains": "Sabatina com João Azevêdo",
          "contains": "eu sou contra o fim da escala 6 por1"}]),
    row("NEG-joao-aborto-fabricated", JOAO, "soc-aborto", "platform", 1, "control", "2025-09-18", src(U["anistia"], "x"),
        [{"web": U["anistia"], "contains": ["Defendo a descriminalização do aborto até a 12ª semana"], "near": ["Azevêdo"]}]),
    row("NEG-lucas-quote-as-joao", JOAO, "eco-privatizacao", "platform", -1, "control", "2026-05-18", src(U["cagepa"], "x"),
        [{"web": U["cagepa"], "contains": ["Não privatizamos, nem vamos privatizar a Cagepa"], "near": ["Azevêdo"]}]),
    row("NEG-lei-14657-signed-by-joao", JOAO, "amb-licenciamento", "record", 1, "control", "2026-08-12", src(U["lei_14657"], "x"),
        [{"pdf": "raw/sapl/lei_14.657.pdf", "contains": ["JOÃO AZEVÊDO LINS FILHO Governador"]}]),
    row("NEG-ppp-wrong-date", LUCAS, "pb-concessoes-ppp", "record", 1, "control", "2026-05-16", src(U["ppp"], "x"),
        [{"web": U["ppp"], "contains": ["O governador Lucas Ribeiro participou do certame na B3"], "published": "2026-05-16"}]),
    row("NEG-fain-decree-by-joao", JOAO, "pb-incentivos-fiscais", "record", 1, "control", "2026-07-24", src(U["doe_fain"], "x"),
        [{"governor_on": "2026-07-24", "expect": "JOAO"}]),
    row("NEG-old-licensing-threshold-swapped", LUCAS, "amb-licenciamento", "record", 1, "control", "2026-08-12", src(U["lei_12713"], "x"),
        [{"pdf": "raw/sapl/16224_texto_integral.pdf", "contains": ["UTE com capacidade instalada superior a 300 (trezentos) MW"]}]),
]

(HERE / "evidence.draft.json").write_text(json.dumps({"rows": rows, "controls": controls}, ensure_ascii=False, indent=1))
print(len(rows), "rows,", len(controls), "controls")

# ---- Governor race: new PB questions and transcript evidence -------------------------------
GOV_YT = "../gov/raw/yt/"
LUCAS, EFRAIM, CICERO, YURI, CAMILO, PEDRO = (f"governador-{n}" for n in (11, 22, 15, 80, 29, 27))
CF88 = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"
CLICKCZ = U["cagepa"]

PPP_LAW = "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11079.htm"
FAIN_PL = "https://sapl.al.pb.leg.br/media/sapl/public/materialegislativa/2015/49332/49332_texto_integral.pdf"
TSE_PLAN_ZIP = "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_PB.zip"

questions = [
    {"id": "pb-concessoes-ppp", "area": "economia", "offices": ["governador", "deputado_estadual"],
     "statement": "A Paraíba deve passar mais obras e serviços públicos, como o esgoto das cidades, para empresas privadas fazerem por contrato, recebendo tarifa ou pagamento do governo.",
     "context": "Concessão e PPP (parceria público-privada) são contratos em que uma empresa privada constrói ou opera um serviço público e recebe tarifa dos usuários. Na PPP, o governo também paga a empresa, e o contrato dura de 5 a 35 anos. Em 15/05/2026 a Paraíba leiloou a PPP do esgoto de 85 cidades atendidas pela Cagepa, num contrato de 25 anos. A Cagepa continua pública e segue cuidando da água.",
     "sources": [src(PPP_LAW, "Lei 11.079/2004 (Lei das PPPs), Planalto"), src(U["ppp"], "Movimento Econômico, 15/05/2026"), src(CLICKCZ, "ClickCZ, 18/05/2026")],
     "options": [
         {"label": "Não: obras e serviços como o esgoto devem ficar com o governo", "value": -1},
         {"label": "Só em casos pontuais, com regras mais duras", "value": -0.5},
         {"label": "Depende do caso, não sei", "value": 0},
         {"label": "Sim, mas revendo contratos como o da Cagepa", "value": 0.5},
         {"label": "Sim, mais parcerias com empresas privadas", "value": 1}],
     "checks": [{"file": "raw/l11079.htm", "encoding": "cp1252",
                 "contains": ["adicionalmente à tarifa cobrada dos usuários contraprestação pecuniária do parceiro público ao parceiro privado",
                              "não inferior a 5 (cinco), nem superior a 35 (trinta e cinco) anos"]},
                {"web": U["ppp"], "contains": ["leilão da Parceria Público-Privada (PPP) de esgotamento sanitário", "85 cidades", "25 anos",
                                               "O abastecimento de água segue integralmente sob responsabilidade da Cagepa"], "published": "2026-05-15"},
                {"web": CLICKCZ, "contains": ["A Cagepa continuará pública"]}]},
    {"id": "pb-incentivos-fiscais", "area": "economia", "offices": ["governador", "deputado_estadual"],
     "statement": "A Paraíba deve continuar cobrando menos imposto de indústrias que vêm para o estado, exigindo em troca que gerem empregos.",
     "context": "Incentivo fiscal é imposto que o estado deixa de cobrar para atrair empresas. Na Paraíba, o FAIN (Fundo de Apoio ao Desenvolvimento Industrial da Paraíba) concede crédito de ICMS, o imposto estadual sobre a circulação de mercadorias, a indústrias aprovadas pelo conselho do fundo. Os planos de governo divergem: uns mantêm os incentivos com metas de emprego, outro propõe acabar com eles.",
     "sources": [src(FAIN_PL, "ALPB, Projeto de Lei 639/2015 do Poder Executivo"), src(U["doe_fain"], "Diário Oficial do Estado da Paraíba nº 18.637, 25/07/2026"),
                 src(CF88, "Constituição Federal, art. 155"), src(TSE_PLAN_ZIP, "Planos de governo PB 2026 registrados no TSE")],
     "options": [
         {"label": "Não: acabar com os descontos de imposto", "value": -1},
         {"label": "Só para empresas pequenas e médias", "value": -0.5},
         {"label": "Não tenho opinião formada", "value": 0},
         {"label": "Sim, com metas e devolução se a empresa não cumprir", "value": 0.5},
         {"label": "Sim, e ampliar para atrair mais indústrias", "value": 1}],
     "checks": [{"pdf": "../alpb/raw/fain/49332.pdf", "contains": ["Conselho Deliberativo do Fundo de Apoio ao Desenvolvimento Industrial da Paraíba - FAIN"]},
                {"pdf": "raw/sapl/doe_2026-07-25.pdf", "page": 1, "contains": ["do Conselho Delibera- tivo do FAIN, que aprovam a concessão de crédito presumido de ICMS"]},
                {"file": "../alpb/raw/cf88.html", "encoding": "cp1252", "contains": ["operações relativas à circulação de mercadorias"]},
                {"pdf": "../raw/plans/2026PB150002540204_01.pdf", "page": 2, "contains": ["Fim imediato de todos os subsídios e incentivos fiscais"]},
                {"pdf": "../raw/plans/2026PB150002544133_01.pdf", "page": 55, "contains": ["metas públicas de investimento, empregos e salários"]}]},
]


def yt(vid, t, label):
    return src(f"{YT}{vid}&t={t}s", f"{label}, em {t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d} (legenda automática do YouTube)")


def cap(vid, at, phrase, title, channel, cues=()):
    return {"captxt": f"{GOV_YT}{vid}.pt-orig.txt", "video": vid, "at": at, "contains": phrase, "meta": f"{GOV_YT}meta2.txt",
            "title_contains": title, "channel": channel, "cues": list(cues)}


EF_CBN = ("IWccMOrxe2o", "Sabatina com Efraim Filho", "CBN Paraíba")
DEB_98 = ("s56ijpZa39Y", "DEBATE - GOVERNO DA PARAÍBA", "Portal Correio")
YURI_SOF = ("W1Vm4q95CHY", "ENTREVISTA COM YURI EZEQUIEL", "Sofesta FM")
CAM_COR = ("dvfM_oTDPwQ", "Camilo Duarte", "TV Correio")
PED_CLK = ("6tt_yulTpJ0", "Pedro Coutinho", "GClickTV")
YURI_NOR = ("2Ufs3qhUig8", "SABATINA COM YURI EZEQUIEL", "SISTEMA O NORTE")
CIC_CLK = ("XzySWIfa1mU", "Cícero Lucena", "GClickTV")
DEB_TAM = ("-Wdp8SfV4PQ", "TH+ SBT João Pessoa", "TH+ SBT TAMBAÚ")
CAM_SOF = ("LvPKwMJdVbE", "ENTREVISTA COM CAMILO DUARTE", "Sofesta FM")
YURI_COR = ("1Qu4nlbt1G8", "Yuri Ezequiel", "TV Correio")
CUE_CIC = [{"phrase": "Cícero Lucen candidato", "within": [-60, 0]}, {"phrase": "Réplica do candidato Yuri", "within": [0, 150]}]
CUE_CAM = [{"phrase": "desfaria esse trato", "within": [-20, 0]}]
CUE_EF_TAM = [{"phrase": "Efraim Filho, o senhor tem 2 minutos para responder", "within": [-30, 0]}]


def trow(subject, qid, pos, detail, date, v, at, phrase, label, cues=(), idq=None):
    vid, title, channel = v
    rid = f"exec-{subject}-{idq or qid}-{vid.strip('-')}-{at}"
    return row(rid, subject, qid, "platform", pos, detail, date, yt(vid, at, label),
               [cap(vid, at, phrase, title, channel, cues)], quote=phrase)


rows += [
    row("exec-governador-11-pb-ppp-cagepa-me-2026", LUCAS, "pb-concessoes-ppp", "platform", 1,
        "No leilão da PPP do esgoto da Cagepa, defendeu a parceria com a empresa vencedora.", "2026-05-15", src(U["ppp"], "Movimento Econômico, 15/05/2026"),
        [{"web": U["ppp"], "contains": ["Estamos dando mais um passo no caminho do desenvolvimento, com uma parceria que vai acelerar a expansão do saneamento"], "near": ["Lucas Ribeiro"], "published": "2026-05-15"}],
        quote="Estamos dando mais um passo no caminho do desenvolvimento, com uma parceria que vai acelerar a expansão do saneamento e garantir mais qualidade de vida para a nossa população."),
    row("exec-governador-11-pb-ppp-cagepa-leilao-2026", LUCAS, "pb-concessoes-ppp", "record", 1,
        "Seu governo levou a leilão na B3, em 15/05/2026, a PPP do esgoto de 85 cidades atendidas pela Cagepa.", "2026-05-15", src(U["ppp"], "Movimento Econômico, 15/05/2026"),
        [{"web": U["ppp"], "contains": ["O governador Lucas Ribeiro participou do certame na B3", "85 cidades"], "published": "2026-05-15"},
         {"governor_on": "2026-05-15", "expect": "LUCAS"}],
        quote="O governador Lucas Ribeiro participou do certame na B3 e classificou o resultado como um marco para o estado."),
    trow(EFRAIM, "pb-concessoes-ppp", -1, "Na sabatina da CBN, disse que cancelaria a PPP do esgoto da Cagepa no primeiro dia de governo, se fosse possível, alegando falta de transparência.",
         "2026-07-15", EF_CBN, 907, "Não só critico como vou cancelar ela no primeiro dia de governo, se isso já me for possível fazer", "CBN Paraíba, sabatina com Efraim Filho, 15/07/2026", idq="pb-ppp-cagepa"),
    trow(CICERO, "pb-concessoes-ppp", -1, "No debate da 98 FM e Portal Correio, disse que cancelará o leilão da PPP do esgoto da Cagepa.",
         "2026-09-28", DEB_98, 5507, "eu já assumi de público que eu cancelarei esse leilão", "Debate 98 FM e Portal Correio, 28/09/2026", CUE_CIC, idq="pb-ppp-cagepa"),
    trow(YURI, "pb-concessoes-ppp", -1, "Disse que acabará com a PPP do esgoto da Cagepa e não fará PPPs no governo.",
         "2026-09-01", YURI_SOF, 2835, "Nós vamos acabar com a PPP. Não vai ter PPP no governo da unidade popular aqui na Paraíba", "Sofesta FM, entrevista com Yuri Ezequiel, 01/09/2026", idq="pb-ppp-cagepa"),
    trow(CAMILO, "pb-concessoes-ppp", -1, "Perguntado se desfaria a PPP do esgoto da Cagepa, respondeu que sim e que é contra qualquer privatização.",
         "2026-09-16", CAM_COR, 210, "Sim, nós somos totalmente contrários a qualquer tipo de privatização", "TV Correio, entrevista com Camilo Duarte (parte 2), 16/09/2026", CUE_CAM, idq="pb-ppp-cagepa"),
    trow(YURI, "pb-incentivos-fiscais", -1, "Criticou as isenções fiscais a grandes empresas, como no polo turístico do Cabo Branco.",
         "2026-09-01", YURI_SOF, 728, "políticas de isenção fiscal para as grandes empresas, como no polo turístico do Cabo Branco", "Sofesta FM, entrevista com Yuri Ezequiel, 01/09/2026"),
    trow(CICERO, "pb-incentivos-fiscais", 1, "Citou a redução do ICMS em São Bento como incentivo que atraiu indústria e aumentou a arrecadação.",
         "2026-09-01", CIC_CLK, 1625, "baixaram a líquida para 1%, passou a desenvolver a indústria da de São Bento e a recardar mais", "ClickPB, sabatina com Cícero Lucena, 01/09/2026"),
    trow(YURI, "eco-privatizacao", -1, "Disse que a privatização troca patrimônio público por lucro, sem ganho de eficiência.",
         "2026-09-01", YURI_SOF, 911, "A privatização cumpre esse papel de tirar o patrimônio que é nosso para transformar em lucro e não em eficiência", "Sofesta FM, entrevista com Yuri Ezequiel, 01/09/2026"),
    trow(CAMILO, "eco-privatizacao", -1, "Disse ser totalmente contrário a qualquer privatização.",
         "2026-09-16", CAM_COR, 210, "Sim, nós somos totalmente contrários a qualquer tipo de privatização", "TV Correio, entrevista com Camilo Duarte (parte 2), 16/09/2026", CUE_CAM),
    trow(EFRAIM, "eco-privatizacao", -1, "No debate da TH+ SBT, disse que não privatizará a Cagepa.",
         "2026-09-23", DEB_TAM, 4221, "Não vou privatizar a CAJEPA porque a CAJEPA é um órgão superavitário", "Debate TH+ SBT Tambaú, 23/09/2026", CUE_EF_TAM),
    trow(CICERO, "eco-privatizacao", -1, "No debate da 98 FM e Portal Correio, disse não ser favorável à privatização da Cagepa.",
         "2026-09-28", DEB_98, 5550, "eu não sou favorável à privatização da Cajepa", "Debate 98 FM e Portal Correio, 28/09/2026", [{"phrase": "Cícero Lucen candidato", "within": [-120, 0]}, {"phrase": "Réplica do candidato Yuri", "within": [0, 120]}]),
    trow(CAMILO, "seg-armas", 1, "Defendeu que toda a população tenha acesso a armas.",
         "2026-08-24", CAM_SOF, 4597, "sim, nós defendemos que toda a população tem acesso a armamento", "Sofesta FM, entrevista com Camilo Duarte, 24/08/2026"),
    trow(CAMILO, "soc-aborto", 1, "Disse que a decisão sobre o aborto cabe à mulher grávida.",
         "2026-08-24", CAM_SOF, 5234, "é a favor que a mulher que tá grávida possa decidir. Cabe a ela essa decisão", "Sofesta FM, entrevista com Camilo Duarte, 24/08/2026"),
]

controls += [
    row("NEG-yuri-ppp-quote-as-cicero", CICERO, "pb-concessoes-ppp", "platform", -1, "control", "2026-09-28", src(YT + "s56ijpZa39Y", "x"),
        [cap("s56ijpZa39Y", 5600, "É fundamental enfrentar a precarização da CAJEP a partir desse leilão", "DEBATE - GOVERNO DA PARAÍBA", "Portal Correio", CUE_CIC)]),
    row("NEG-efraim-keeps-ppp-fabricated", EFRAIM, "pb-concessoes-ppp", "platform", 1, "control", "2026-07-15", src(YT + "IWccMOrxe2o", "x"),
        [cap("IWccMOrxe2o", 907, "vou manter a PPP da Cajepa", "Sabatina com Efraim Filho", "CBN Paraíba")]),
    row("NEG-camilo-quote-wrong-video", CAMILO, "seg-armas", "platform", 1, "control", "2026-08-24", src(YT + "dvfM_oTDPwQ", "x"),
        [cap("dvfM_oTDPwQ", 4597, "sim, nós defendemos que toda a população tem acesso a armamento", "Camilo Duarte", "TV Correio")]),
]

(HERE / "questions.json").write_text(json.dumps([{k: v for k, v in q.items() if k != "checks"} for q in questions], ensure_ascii=False, indent=1))
(HERE / "evidence.draft.json").write_text(json.dumps({"rows": rows, "controls": controls, "questions": questions}, ensure_ascii=False, indent=1))
print(len(rows), "rows,", len(controls), "controls,", len(questions), "questions")
