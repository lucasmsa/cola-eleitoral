"""Writes pipeline/profiles/profiles.draft.json: Profile records plus one check spec per Claim.

Run check_profiles.py afterwards; only claims whose check passes reach profiles.json.
"""
import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPE = ROOT / "pipeline"
DATA = ROOT / "src" / "data"
RAW = PIPE / "profiles" / "raw"
TSE = PIPE / "raw" / "tse"
ACCESSED = "2026-10-03"

CAND_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip"
HIST_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/historico_candidatura/historico_candidatura_2026.zip"
VOTES_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip"
PLAN_URL = {
    "BR": "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_BR.zip",
    "PB": "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_PB.zip",
}
HANDOVER_URL = "https://jornaldebrasilia.com.br/brasil-7/juventude-e-energia-nao-inexperiencia-diz-lucas-ribeiro-o-governador-mais-jovem-do-brasil/"
HANDOVER = "Lucas Ribeiro assumiu o Governo da Paraíba em 2 de abril de 2026, após a renúncia de João Azevêdo"

OFFICE_LABEL = {"PRESIDENTE": "presidente", "GOVERNADOR": "governador", "SENADOR": "senador",
                "DEPUTADO FEDERAL": "deputado federal", "DEPUTADO ESTADUAL": "deputado estadual"}

# Hand-picked verbatim quotes: (candidateId, field, page, quote). field is presents or proposals.
PLAN_QUOTES = {
    "presidente-13": ("2026BR280002542548_01.pdf", [
        ("presents", 4, "O que nos move são os sonhos do povo brasileiro."),
        ("presents", 10, "colocar o pobre no orçamento e o rico no Imposto de Renda"),
        ("proposals", 27, "Fortaleceremos o Programa Brasil Contra o Crime Organizado, lançado em maio de 2026."),
        ("proposals", 30, "Ampliaremos o programa de estímulos para uso de câmeras corporais, com padrões nacionais para utilização, gestão e preservação das imagens."),
        ("proposals", 32, "Vamos dar continuidade e fortalecer o Pé-de-Meia."),
        ("proposals", 60, "Ampliaremos o Programa Cisternas em regiões com estresse hídrico, garantindo água para consumo e produção."),
        ("proposals", 28, "Consolidaremos o Sistema de Inteligência de Segurança Pública e Justiça Criminal, modernizaremos o SINESP e a Infoseg e ampliaremos as Forças Integradas de Combate ao Crime Organizado (FICCOs)."),
    ]),
    "presidente-22": ("2026BR280002551544_01.pdf", [
        ("presents", 11, "Brasil sem Medo, para sua família voltar para casa em paz"),
        ("presents", 13, "A soberania começa na porta da sua casa"),
        ("proposals", 13, "Vamos punir também maiores de 14 anos que cometerem crimes graves, como estupro, tráfico, tortura e assassinato."),
        ("proposals", 14, "Em parceria com os governos estaduais, vamos criar meio milhão de novas vagas no sistema prisional em 4 anos e zerar o déficit carcerário."),
        ("proposals", 15, "Vamos implantar o Muralha Brasileira - um sistema nacional de reconhecimento facial integrado a bancos de dados criminais"),
        ("proposals", 30, "Vamos corrigir suas distorções, reduzir o IVA, hoje projetado num dos patamares mais altos do mundo, e assegurar a não cumulatividade, para que não se cobre imposto sobre imposto."),
        ("proposals", 44, "Por isso defendemos o negociado sobre o legislado"),
        ("proposals", 9, "Manteremos e aperfeiçoaremos os programas sociais, porque nenhum brasileiro pode ficar para trás"),
    ]),
    "presidente-14": ("2026BR280002540694_01.pdf", [
        ("presents", 1, "O FUTURO É GLORIOSO"),
        ("presents", 1, "Resumo executivo do Livro Amarelo"),
        ("proposals", 6, "Em “SUS Fila Zero” propomos uma agenda de inovação na área da saúde, com integração da inteligência artificial para melhoria e democratização dos serviços."),
        ("proposals", 6, "No nível universitário, propomos a ampliação das vagas de STEM e a substituição das cotas por um conceito de bolsas por mérito"),
        ("proposals", 13, "desde o primeiro dia do governo, estaremos em campanha contra o crime organizado, utilizando os mecanismos da GLO e do Estado de Defesa para romper o controle territorial das facções."),
        ("proposals", 28, "a fusão de Ministério da Cultura e Ministério da Educação"),
        ("proposals", 31, "buscaremos ampliar a competência da União para ela proceder à adoção do modelo de escolas civis-militares."),
    ]),
    "presidente-70": ("2026BR280002551547_01.pdf", [
        ("presents", 34, "Não queremos ser voz do ódio, mas a voz da cultura da paz."),
        ("presents", 34, "Queremos defender ideias sem destruir pessoas e construir pontes onde muitos constroem muros."),
        ("proposals", 39, "Implantaremos uma ampla rede nacional de Escolas de Empreendedorismo, formando milhões de jovens e adultos para criar empresas, inovar, administrar recursos e gerar empregos."),
        ("proposals", 39, "Criaremos um banco especializado em financiar pequenos empreendedores, microempresas e startups, oferecendo crédito acessível, orientação técnica e educação financeira."),
        ("proposals", 40, "Implantaremos um grande programa nacional para estimular a instalação de 10 mil novas indústrias ao longo dos próximos anos"),
        ("proposals", 37, "Iremos avaliar os impactos da reforma tributária sobre os diferentes setores da economia"),
        ("proposals", 2, "PROJETO 1 - A REVOLUÇÃO DA EDUCAÇÃO"),
    ]),
    "presidente-55": ("2026BR280002551932_01.pdf", [
        ("presents", 1, "Muito pra mostrar Nada pra esconder"),
        ("presents", 2, "como médico, produtor rural, parlamentar e governador"),
        ("proposals", 2, "reduzir desperdícios, rever privilégios e subsídios sem resultado, qualificar o gasto e recuperar a capacidade de investir."),
        ("proposals", 2, "Manteremos a rede de transferência de renda para quem precisa, mas conectaremos benefícios a qualificação, cuidado infantil, inclusão produtiva, habitação, saúde e educação."),
        ("proposals", 3, "Vamos combater com rigor o desmatamento, a grilagem e a mineração ilegal"),
        ("proposals", 20, "Aplicaremos esse método em escala nacional, combinando firmeza, tecnologia, integridade e respeito à lei para devolver a paz às famílias brasileiras."),
        ("proposals", 73, "Não adotaremos alinhamentos automáticos nem aceitaremos falsas escolhas entre polos geopolíticos rivais."),
    ]),
    "governador-11": ("2026PB150002551789_01.pdf", [
        ("presents", 1, "AGORA, É DAQUI PRA MELHOR."),
        ("presents", 2, "Conheço a Paraíba que acorda cedo, que trabalha muito, que enfrenta os desafios e não perde a coragem de sonhar."),
        ("proposals", 30, "Expandir a infraestrutura para segurança hídrica com a conclusão do plano Novas Adutoras, com destaque para a conclusão dos ramais Cariri e Curimataú, e do Programa de Construção de Barragens 7.3."),
        ("proposals", 12, "Expandir o ensino médio e o ensino técnico e profissional, ampliando a Escola Cidadã Integral (ECI) e a Escola Integral Cidadã Técnica (ECIT)."),
        ("proposals", 6, "implantar unidade prisional com modelo RDD"),
        ("proposals", 10, "Implantar, ainda, uma política estadual de prevenção e cuidado relacionados ao vício em apostas on-line, com atendimento aos usuários e seus familiares."),
        ("proposals", 5, "ampliar o socorro aeromédico com um helicóptero equipado com UTI aérea e integrado ao Corpo de Bombeiros"),
    ]),
    "governador-22": ("2026PB150002538692_01.pdf", [
        ("presents", 1, "Um Novo Tempo para a Paraíba"),
        ("presents", 1, "Porque a Paraíba pode mais, e nós vamos fazer, juntos."),
        ("proposals", 10, "implantar a zona de processamento para exportação"),
        ("proposals", 7, "criar um fundo de garantia para viabilizar crédito"),
        ("proposals", 15, "implantar uma rede de urgências e emergências com cobertura sertaneja"),
        ("proposals", 19, "ampliar o uso de inteligência e investigação para desarticular o crime organizado"),
        ("proposals", 11, "Queremos cidades feitas para pessoas, com calçadas largas, ciclovias conectadas e um transporte público que seja a primeira escolha do cidadão pela sua eficiência e conforto."),
    ]),
    "governador-15": ("2026PB150002544133_01.pdf", [
        ("presents", 6, "Queremos uma Paraíba que inspire confiança."),
        ("presents", 5, "Vamos planejar a Paraíba olhando para cada região, respeitando suas características, suas vocações, seu potencial, e suas lideranças."),
        ("proposals", 20, "Implantar seis “Centros Regionais de Comando e Controle” nas regiões de Cajazeiras, Sousa, Catolé do Rocha, Monteiro, Vale do Piancó e Guarabira"),
        ("proposals", 25, "Implantar o “SAMU Aéreo Paraíba”, rede estadual de transporte aeromédico"),
        ("proposals", 25, "Implantar a “Central Única Estadual de Regulação”, com aplicativo para o cidadão, transparência no respeito à ordem da fila e mutirões permanentes."),
        ("proposals", 75, "Garantir Passe Livre Estudantil para estudantes da Rede Pública."),
        ("proposals", 36, "Instituir o novo “Plano de Cargos, Carreiras e Remuneração da Educação” e realizar concurso público regular."),
    ]),
    "governador-80": ("2026PB150002540204_01.pdf", [
        ("presents", 1, "PARAÍBA PARA QUEM TRABALHA"),
        ("presents", 3, "Defendemos a retomada do controle público sobre os setores fundamentais da economia, garantindo planejamento estatal, eficiência social e acesso universal à população."),
        ("proposals", 2, "Fim das Organizações Sociais e da terceirização do serviço público."),
        ("proposals", 2, "Fim imediato de todos os subsídios e incentivos fiscais e financeiros concedidos pelo Estado aos monopólios, grandes empresários e agroexportadores, substituídos por auditoria popular."),
        ("proposals", 5, "Fim das terceirizações e rescisão imediata dos contratos com a iniciativa privada, garantindo 100% dos leitos nos setores públicos ou sem fins lucrativos."),
        ("proposals", 5, "Defendemos uma política de segurança comprometida com os direitos humanos, a proteção da vida e o enfrentamento de todas as formas de opressão."),
    ]),
    "governador-29": ("2026PB150002552603_01.pdf", [
        ("presents", 1, "Por salário, trabalho e terra"),
        ("presents", 1, "O PCO não participa das eleições para fazer promessas"),
        ("proposals", 3, "Revogar todas as \"reformas\" contra os trabalhadores da ativa e aposentados, em todos os níveis (federal, estadual e municipal)"),
        ("proposals", 4, "Fim do teto de gastos e da Lei de Responsabilidade Fiscal"),
        ("proposals", 6, "Fim dos impostos sobre o consumo e os salários."),
        ("proposals", 3, "Fim dos privilégios de oficiais militares, juízes e familiares"),
    ]),
    "governador-27": ("2026PB150002551911_01.pdf", [
        ("presents", 2, "Vamos diminuir o tamanho do Estado para aumentar o tamanho do cidadão!"),
        ("proposals", 2, "Vamos enxugar a estrutura, eliminar privilégios e promover uma política agressiva de privatizações e concessões."),
        ("proposals", 5, "Queremos transformar nosso sol e nossos ventos em emprego, renda e desenvolvimento."),
        ("proposals", 7, "Queremos que o jovem permaneça na Paraíba porque aqui encontrará oportunidades para realizar seus sonhos."),
    ]),
}

QUEIROGA_URL = "https://www.poder360.com.br/governo/marcelo-queiroga-assume-como-ministro-da-saude-em-cerimonia-fechada/"
AG_SENADO = "https://www12.senado.leg.br/noticias/candidatos-2026/paraiba"
LULA_URL = "https://www.gov.br/secretariageral/pt-br/centrais-de-conteudo/biblioteca-da-pr/galeria-dos-ex-presidentes/luiz-inacio-lula-da-silva"
RENAN_URL = "https://diariodonordeste.verdesmares.com.br/pontopoder/quem-e-renan-santos-candidato-ao-cargo-de-presidente-da-republica-em-2026-1.3778230"
CURY_URL = "https://jornaldebrasilia.com.br/noticias/politica-e-poder/quem-e-augusto-cury-anunciado-como-pre-candidato-a-presidencia/"
CAIADO_URL = "https://brasil61.com/n/daniel-vilela-assume-governo-de-goias-e-fala-em-continuidade-de-caiado-gvgo260018"
YURI_URL = "https://www.itatiaia.com.br/politica/eleicoes/conheca-a-carreira-politica-de-yuri-ezequiel-pre-candidato-ao-governo-da-paraiba/"
CAMILO_URL = "https://jornaldaparaiba.com.br/_/219742"
SENADO_API = "https://legis.senado.leg.br/dadosabertos/senador/{code}/mandatos.json"


def web(url):
    return {"kind": "web", "url": url}


def senate_block(start):
    return {"kind": "web-block", "url": AG_SENADO, "start": start, "end": "Patrimônio"}


def ag(cid_start, items):
    return [(text, support, "Agência Senado, candidatos ao Senado na Paraíba (24/08/2026)", AG_SENADO, senate_block(cid_start))
            for text, support in items]


EXTRA_EXPERIENCE = {
    "senador-222": [("Tomou posse como ministro da Saúde em 23 de março de 2021, no governo Jair Bolsonaro.",
                     "O presidente Jair Bolsonaro assinou nesta 3ª feira (23.mar.2021) o termo de posse de Marcelo Queiroga como novo ministro da Saúde.",
                     "Poder360, 23/03/2021", QUEIROGA_URL, web(QUEIROGA_URL))]
                   + ag("DR. MARCELO QUEIROGA PL 222", [("Cargo anterior: ministro da Saúde, 2021-2022.", "Ministro da Saúde, 2021-2022"),
                                                       ("Atividade profissional: médico.", "Atividade profissional Médico")]),
    "senador-400": ag("JOAO AZEVÊDO PSB 400", [("Cargo anterior: governador da Paraíba, 2019-2026.", "Governador, 2019-2026"),
                                              ("Cargos anteriores: secretário municipal de Infraestrutura de João Pessoa e secretário estadual de Infraestrutura.",
                                               "Secretário municipal de Infraestrutura de João Pessoa Secretário estadual de Infraestrutura"),
                                              ("Atividade profissional: engenheiro civil e professor.", "Atividade profissional Engenheiro civil Professor")]),
    "senador-155": ag("VENEZIANO MDB 155", [("Vereador de Campina Grande, 1997-2005.", "Vereador de Campina Grande, 1997-2005"),
                                           ("Prefeito de Campina Grande, 2005-2013.", "Prefeito de Campina Grande, 2005-2013"),
                                           ("Deputado federal, 2015-2019.", "Deputado federal, 2015-2019"),
                                           ("Senador desde 2019.", "Senador, 2019-atual")]),
    "senador-100": ag("NABOR REPUBLICANOS 100", [("Prefeito de Patos em 2005-2013 e 2021-2026.", "Prefeito de Patos, 2005-2013, 2021-2026"),
                                                ("Deputado estadual, 2015-2020.", "Deputado estadual, 2015-2020"),
                                                ("Atividade profissional: advogado.", "Atividade profissional Advogado")]),
    "senador-300": ag("MAJOR FÁBIO NOVO 300", [("Deputado federal em 2007-2011, 2012 e 2013-2015.", "Deputado federal, 2007-2011, 2012, 2013-2015"),
                                              ("Atividade profissional: oficial da Polícia Militar (reformado).",
                                               "Atividade profissional Oficial da Polícia Militar (reformado)")]),
    "presidente-13": [("O plano de governo chama o mandato iniciado em 2023 de “governo Lula III”, o terceiro como presidente.",
                       "O governo Lula III começou com a tentativa golpista de 8 de janeiro de 2023",
                       "Plano de governo registrado no TSE, p. 8", PLAN_URL["BR"],
                       {"kind": "pdf", "file": "2026BR280002542548_01.pdf", "page": 8,
                        "quote": "O governo Lula III começou com a tentativa golpista de 8 de janeiro de 2023"}),
                      ("Posse como presidente da República em 1º/01/2003 (1º mandato), após eleição direta com 52.793.364 votos.",
                       "Votos recebidos 52.793.364 (cinquenta e dois milhões, setecentos e noventa e três mil e trezentos e sessenta e quatro votos) Posse 01/01/2003",
                       "Biblioteca da Presidência, galeria dos ex-presidentes (gov.br)", LULA_URL, web(LULA_URL)),
                      ("Posse para o 2º mandato em 1º/01/2007, após eleição direta com 58.295.042 votos.",
                       "Votos recebidos 58.295.042 (cinquenta e oito milhões, duzentos e noventa e cinco mil e quarenta e dois votos) Posse 01/01/2007",
                       "Biblioteca da Presidência, galeria dos ex-presidentes (gov.br)", LULA_URL, web(LULA_URL))],
    "presidente-22": [("Senador pelo Rio de Janeiro em exercício desde 1º/02/2019, com mandato até 31/01/2027.",
                       "5894|RJ|2019-02-01|2027-01-31", "Senado Federal, Dados Abertos, mandatos do senador 5894",
                       SENADO_API.format(code=5894),
                       {"kind": "senado-api", "code": 5894, "uf": "RJ", "start": "2019-02-01", "end": "2027-01-31"})],
    "presidente-55": [("Senador por Goiás de 1º/02/2015 até renunciar ao mandato em 1º/01/2019.",
                       "456|GO|2015-02-01|2019-01-01|Renúncia", "Senado Federal, Dados Abertos, mandatos do senador 456",
                       SENADO_API.format(code=456),
                       {"kind": "senado-api", "code": 456, "uf": "GO", "start": "2015-02-01", "exerciseEnd": "2019-01-01",
                        "cause": "Renúncia"}),
                      ("Deixou o governo de Goiás em 2026, após 7 anos e 3 meses no cargo, para concorrer à Presidência.",
                       "após 7 anos e 3 meses de gestão de Ronaldo Caiado (PSD), que deixa o cargo para concorrer à presidência da República",
                       "Brasil 61, 31/03/2026", CAIADO_URL, web(CAIADO_URL))],
    "presidente-14": [("Fundou o Movimento Brasil Livre (MBL) em 2014, com Kim Kataguiri, Fernando Holiday e Rubinho Nunes.",
                       "Em 2014, Renan Santos fundou o Movimento Brasil Livre (MBL), junto ao deputado federal Kim Kataguiri",
                       "Diário do Nordeste, 20/07/2026", RENAN_URL, web(RENAN_URL)),
                      ("2026 é a primeira eleição que disputa.", "Esta é a 1ª eleição que disputa.",
                       "Diário do Nordeste, 20/07/2026", RENAN_URL, web(RENAN_URL))],
    "presidente-70": [("Médico psiquiatra formado em São José do Rio Preto; publicou mais de 70 livros.",
                       "é médico psiquiatra formado pela Faculdade de Medicina de São José do Rio Preto e publicou mais de 70 livros",
                       "Jornal de Brasília, 08/04/2026", CURY_URL, web(CURY_URL))],
    "governador-80": [("Advogado; preside o diretório municipal da UP em João Pessoa e integra a direção nacional do partido.",
                       "Ezequiel preside o diretório municipal da UP na capital e integra a direção nacional da legenda.",
                       "Itatiaia", YURI_URL, web(YURI_URL))],
    "governador-29": [("Presidente estadual do PCO na Paraíba.", "Trata-se de Camilo Duarte, do PCO, presidente estadual da legenda.",
                       "Jornal da Paraíba", CAMILO_URL, web(CAMILO_URL)),
                      ("Disputou vereador (2004, 2012), deputado federal (2010, 2014) e prefeito de João Pessoa (2020, 2024), sem se eleger.",
                       "Desde então, ele se candidatou duas vezes a vereador, em 2004 e 2012; duas vezes a deputado federal, em 2010 e 2014; e mais duas para prefeito de João Pessoa, em 2020 e 2024. Camilo Duarte não conseguiu a eleição em nenhuma das candidaturas.",
                       "Jornal da Paraíba", CAMILO_URL, web(CAMILO_URL))],
}

# Senators file no plan: proposals are their own checked quotes already in evidence.json.
SENATE_PROPOSAL_EVIDENCE = {
    "senador-400": ["exec-senador-400-eco-6x1-correio-sabatina", "exec-senador-400-seg-8-janeiro-pbagora-2025",
                    "exec-senador-400-eco-reforma-tributaria-debate-arapuan"],
    "senador-155": ["sen-plat-senador-155-eco-6x1", "plat-senador-155-seg-8-janeiro"],
    "senador-100": ["sen-plat-senador-100-eco-6x1", "sen-plat-senador-100-seg-maioridade"],
    "senador-222": ["sen-plat-senador-222-seg-maioridade", "sen-plat-senador-222-seg-drogas", "sen-plat-senador-222-eco-6x1"],
    "senador-300": ["sen-cap-senador-300-seg-maioridade", "sen-cap-senador-300-seg-saidinha", "sen-cap-senador-300-seg-drogas",
                    "sen-plat-senador-300-eco-6x1"],
}


def read_csv(path, encoding):
    with open(path, encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def clean(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"(\w)- (\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()


def br_int(n):
    return f"{n:,}".replace(",", ".")


def sq_of(c):
    return re.search(r"SQ (\d+)", c["source"]["label"]).group(1)


def nulo(v):
    return v.strip() in ("", "#NULO", "#NE", "#NULO#")


class Ids:
    def __init__(self):
        self.seen = defaultdict(int)

    def __call__(self, cid, field):
        self.seen[(cid, field)] += 1
        return f"prof-{cid}-{field}-{self.seen[(cid, field)]}"


def main():
    candidates = json.loads((DATA / "candidates.json").read_text())
    by_id = {c["id"]: c for c in candidates}
    evidence = json.loads((DATA / "evidence.json").read_text())
    ev_by_id = {e["id"]: e for e in evidence}
    polls = json.loads((DATA / "polls.json").read_text())
    cand26 = {}
    for uf in ("BR", "PB"):
        for r in read_csv(TSE / f"consulta_cand_2026_{uf}.csv", "latin-1"):
            cand26[r["SQ_CANDIDATO"]] = r
    hist = defaultdict(list)
    for h in read_csv(TSE / "historico_candidatura_2026_BRASIL.csv", "latin-1"):
        hist[h["SQ_CANDIDATO_ATUAL"]].append(h)
    votes = defaultdict(int)
    vote_meta = {}
    for v in read_csv(RAW / "votacao_candidato_munzona_2022_PB.csv", "latin-1"):
        if v["NR_TURNO"] != "1":
            continue
        votes[v["SQ_CANDIDATO"]] += int(v["QT_VOTOS_NOMINAIS"])
        vote_meta[v["SQ_CANDIDATO"]] = v
    next_id = Ids()

    def claim(cid, field, text, support, label, url, spec):
        cid_ = next_id(cid, field)
        return {"text": text, "support": support, "source": {"url": url, "accessed": ACCESSED, "label": label},
                "checkId": cid_, "_check": spec}

    # ---------- poll ranks ----------
    def mean_rank(office, names):
        sums = defaultdict(list)
        for p in polls:
            if p["office"] != office:
                continue
            for r in p["results"]:
                sums[r["label"]].append(r["pct"])
        means = {k: sum(v) / len(v) for k, v in sums.items() if k in names}
        return sorted(means.items(), key=lambda kv: -kv[1])

    pres_names = {"Lula": "presidente-13", "Flávio Bolsonaro": "presidente-22", "Augusto Cury": "presidente-70",
                  "Ronaldo Caiado": "presidente-55", "Renan Santos": "presidente-14", "Romeu Zema": "presidente-30",
                  "Samara": "presidente-80"}
    pres_rank = mean_rank("presidente", pres_names)
    gov_names = {"Lucas Ribeiro": "governador-11", "Efraim Filho": "governador-22", "Cícero Lucena": "governador-15",
                 "Pedro Coutinho": "governador-27", "Camilo Duarte": "governador-29", "Yuri Ezequiel": "governador-80"}
    sen_names = {"João Azevêdo": "senador-400", "Veneziano": "senador-155", "Nabor": "senador-100",
                 "Dr. Marcelo Queiroga": "senador-222", "Major Fábio": "senador-300", "André Gadelha": "senador-151",
                 "João Batista": "senador-801"}
    ranks = {}
    for office, names in (("presidente", pres_names), ("governador", gov_names), ("senador", sen_names)):
        for i, (label, _) in enumerate(mean_rank(office, names), start=1):
            ranks[names[label]] = i
    top_pres = [pres_names[l] for l, _ in pres_rank[:5]]
    top_sen = [sen_names[l] for l, _ in mean_rank("senador", sen_names)[:5]]
    majoritarian = top_pres + ["governador-11", "governador-22", "governador-15", "governador-80", "governador-29",
                               "governador-27"] + top_sen

    # ---------- shared claim builders ----------
    def tse_presents(c):
        sq = sq_of(c)
        row = cand26[sq]
        out = []
        uf = "BR" if c["office"] == "presidente" else "PB"
        if not nulo(row["NM_COLIGACAO"]):
            out.append(claim(c["id"], "presents",
                             f"Coligação registrada no TSE: {row['NM_COLIGACAO'].strip()} ({row['DS_COMPOSICAO_COLIGACAO'].strip()}).",
                             row["NM_COLIGACAO"].strip(), f"TSE, consulta_cand_2026_{uf}.csv, SQ {sq}", CAND_URL,
                             {"kind": "tse-cand", "uf": uf, "sq": sq, "field": "NM_COLIGACAO", "value": row["NM_COLIGACAO"].strip()}))
        if not nulo(row["NM_FEDERACAO"]):
            out.append(claim(c["id"], "presents", f"Concorre pela {row['NM_FEDERACAO'].strip().title()} ({row['DS_COMPOSICAO_FEDERACAO'].strip()}).",
                             row["NM_FEDERACAO"].strip(), f"TSE, consulta_cand_2026_{uf}.csv, SQ {sq}", CAND_URL,
                             {"kind": "tse-cand", "uf": uf, "sq": sq, "field": "NM_FEDERACAO", "value": row["NM_FEDERACAO"].strip()}))
        occ = row["DS_OCUPACAO"].strip()
        if not nulo(occ):
            out.append(claim(c["id"], "presents", f"Ocupação que declarou ao TSE: {occ.capitalize()}.", occ,
                             f"TSE, consulta_cand_2026_{uf}.csv, SQ {sq}", CAND_URL,
                             {"kind": "tse-cand", "uf": uf, "sq": sq, "field": "DS_OCUPACAO", "value": occ}))
        return out

    def tse_experience(c, limit=4):
        sq = sq_of(c)
        rows = [h for h in hist.get(sq, []) if h["DS_SIT_TOT_TURNO"] in ("Eleito", "Eleito por QP", "Eleito por média")]
        rows.sort(key=lambda h: -int(h["ANO_ELEICAO"]))
        out, seen = [], set()
        for h in rows:
            key = (h["ANO_ELEICAO"], h["DS_CARGO"])
            if key in seen:
                continue
            seen.add(key)
            place = h["NM_UE"].strip().title() if h["TP_ABRANGENCIA_ELEICAO"] == "M" else h["SG_UF"].strip()
            text = (f"{h['ANO_ELEICAO']}: eleição para {h['DS_CARGO'].strip().lower()} ({place}), pelo "
                    f"{h['SG_PARTIDO'].strip()}. Resultado no TSE: {h['DS_SIT_TOT_TURNO'].strip()}.")
            support = f"{h['ANO_ELEICAO']};{h['DS_CARGO'].strip()};{h['DS_SIT_TOT_TURNO'].strip()}"
            out.append(claim(c["id"], "experience", text, support, "TSE, histórico de candidaturas 2026", HIST_URL,
                             {"kind": "tse-hist", "sq": sq, "ano": h["ANO_ELEICAO"], "cargo": h["DS_CARGO"].strip(),
                              "result": h["DS_SIT_TOT_TURNO"].strip(), "partido": h["SG_PARTIDO"].strip()}))
            if len(out) >= limit:
                break
        return out

    def sq2022(c):
        for h in hist.get(sq_of(c), []):
            if h["ANO_ELEICAO"] == "2022" and h["SQ_CANDIDATO"] in votes:
                return h["SQ_CANDIDATO"], h
        return None, None

    def votes_claim(c):
        sq22, h = sq2022(c)
        if not sq22:
            return []
        total = votes[sq22]
        cargo = vote_meta[sq22]["DS_CARGO"].strip()
        return [claim(c["id"], "experience",
                      f"Em 2022 recebeu {br_int(total)} votos nominais no 1º turno para {cargo.lower()} na Paraíba.",
                      str(total), "TSE, votacao_candidato_munzona_2022_PB.csv (soma das zonas, 1º turno)", VOTES_URL,
                      {"kind": "tse-votes2022", "sq2022": sq22, "total": total})]

    def defends(cid, limit=6):
        own = [e for e in evidence if e["subject"]["type"] == "candidate" and e["subject"]["id"] == cid and e["position"] != 0]
        own.sort(key=lambda e: (e["lowDiscrimination"], e["kind"] != "record", e["date"] < "2025"))
        out, qs = [], set()
        for e in own:
            if e["questionId"] in qs:
                continue
            qs.add(e["questionId"])
            out.append(e["id"])
            if len(out) >= limit:
                break
        return out

    profiles = []
    for cid in majoritarian:
        c = by_id[cid]
        prof = {"candidateId": cid, "office": c["office"], "pollRank": ranks.get(cid), "presents": [], "experience": [],
                "proposals": [], "defends": defends(cid)}
        if cid in PLAN_QUOTES:
            pdf, quotes = PLAN_QUOTES[cid]
            uf = "BR" if pdf.startswith("2026BR") else "PB"
            for field, page, q in quotes:
                prof[field].append(claim(cid, field, f"“{clean(q)}”", q, f"Plano de governo registrado no TSE, p. {page}",
                                         PLAN_URL[uf], {"kind": "pdf", "file": pdf, "page": page, "quote": q}))
        for eid in SENATE_PROPOSAL_EVIDENCE.get(cid, []):
            e = ev_by_id[eid]
            prof["proposals"].append(claim(cid, "proposals", f"“{e['quote']}”", e["quote"], e["source"]["label"],
                                           e["source"]["url"], {"kind": "evidence", "evidenceId": eid}))
        prof["presents"] += tse_presents(c)
        if "notice" in c:
            prof["presents"].insert(0, claim(cid, "presents", c["notice"]["text"], c["notice"]["text"],
                                             c["notice"]["sources"][0]["label"], c["notice"]["sources"][0]["url"],
                                             {"kind": "notice"}))
        prof["experience"] += tse_experience(c)
        if cid in ("governador-11", "senador-400"):
            prof["experience"].append(claim(cid, "experience",
                                            "Em 2 de abril de 2026 João Azevêdo renunciou ao governo da Paraíba para disputar o Senado, e Lucas Ribeiro assumiu o cargo.",
                                            HANDOVER, "Jornal de Brasília", HANDOVER_URL, {"kind": "web", "url": HANDOVER_URL}))
        prof["experience"] += votes_claim(c)
        for text, support, label, url, spec in EXTRA_EXPERIENCE.get(cid, []):
            prof["experience"].append(claim(cid, "experience", text, support, label, url, spec))
        profiles.append(prof)

    # ---------- deputados: up to 5 per list ----------
    for office in ("deputado_federal", "deputado_estadual"):
        lists = defaultdict(list)
        for c in candidates:
            if c["office"] == office:
                lists[c["list"]].append(c)
        dep_word = "Deputado Federal" if office == "deputado_federal" else "Deputado Estadual"
        for lid, members in lists.items():
            scored = []
            for c in members:
                sq22, h = sq2022(c)
                elected_dep = bool(h) and h["DS_SIT_TOT_TURNO"].startswith("Eleito") and h["DS_CARGO"].strip().title().startswith("Deputado")
                scored.append((not elected_dep, -(votes[sq22] if sq22 else 0), c))
            scored.sort(key=lambda t: (t[0], t[1], t[2]["ballotName"]))
            picks = [t[2] for t in scored if t[1] < 0 or not t[0]][:5]
            for c in picks:
                profiles.append({"candidateId": c["id"], "office": office, "pollRank": None,
                                 "presents": tse_presents(c), "experience": tse_experience(c, 3) + votes_claim(c),
                                 "proposals": [], "defends": defends(c["id"])})

    (PIPE / "profiles" / "profiles.draft.json").write_text(json.dumps(profiles, ensure_ascii=False, indent=1))
    print(len(profiles), "profiles;", sum(len(p[f]) for p in profiles for f in ("presents", "experience", "proposals")), "claims")
    print("presidente top 5:", top_pres, "senador top 5:", top_sen)


if __name__ == "__main__":
    main()
