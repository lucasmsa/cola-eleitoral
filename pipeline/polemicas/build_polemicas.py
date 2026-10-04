"""Writes pipeline/polemicas/draft.json: Controversy items plus per-item check metadata.

Every claim's `support` is copied verbatim from the cached source (see fetch.py). TSE-derived claims
(patrimonio, experiencia) are re-derived from the TSE CSVs by the check instead of matched as text.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
ACC = "2026-10-03"

S = {
    "lupa": ("https://www.agencialupa.org/noticias/2026/10/01/erros-e-acertos-dos-candidatos-que-disputam-a-presidencia-do-brasil-em-2026/", "Lupa, 01/10/2026"),
    "lupa_cury_jn": ("https://www.agencialupa.org/checagem/2026/08/29/ao-vivo-checagem-da-entrevista-de-augusto-cury-ao-jornal-nacional/", "Lupa, 29/08/2026"),
    "dn_lula": ("https://diariodonordeste.verdesmares.com.br/politica/stf-mantem-anulacao-das-condenacoes-de-lula-na-lava-jato-1.3073726", "Diário do Nordeste/Folhapress, 15/04/2021"),
    "jb_lula": ("https://www.jb.com.br/pais/justica/2021/03/1028825-ministro-do-stf-anula-condenacoes-de-lula-ligadas-a-lava-jato.html", "Jornal do Brasil, 08/03/2021"),
    "istoe_lula": ("https://istoedinheiro.com.br/juiza-arquiva-acao-contra-lula-no-caso-do-triplex", "IstoÉ Dinheiro/Estadão Conteúdo, 28/01/2022"),
    "cb_flavio": ("https://www.correiobraziliense.com.br/politica/2022/10/5043990-rachadinha-o-que-aconteceu-com-caso-que-envolve-filho-de-bolsonaro.html", "Correio Braziliense/BBC, 03/10/2022"),
    "im_flavio": ("https://www.infomoney.com.br/?p=1856409", "InfoMoney/Reuters, 17/05/2022"),
    "ab_caiado": ("https://agenciabrasil.ebc.com.br/justica/noticia/2025-04/tre-go-afasta-inelegibilidade-de-governador-ronaldo-caiado", "Agência Brasil, 09/04/2025"),
    "em_zema": ("https://www.em.com.br/politica/2025/09/7251390-decreto-alterado-por-zema-favoreceu-empresa-investigada-na-operacao-rejeito.html", "Estado de Minas, 09/2025"),
    "ot_zema": ("https://www.otempo.com.br/politica/2025/9/18/zema-quebra-silencio-sobre-a-operacao-rejeito-espero-punicao-exemplar", "O Tempo, 18/09/2025"),
    "mig_renan": ("https://www.migalhas.com.br/quentes/449594/fundador-do-mbl-indenizara-djamila-ribeiro-por-associa-la-ao-crime", "Migalhas, 09/02/2026"),
    "met_renan": ("https://www.metropoles.com/sao-paulo/lider-mbl-indenizar-bolsonarista", "Metrópoles, 10/06/2025"),
    "jp_debate": ("https://jornaldaparaiba.com.br/politica/debate-1-turno-veja-acertos-erros-e-imprecisoes-nas-falas-dos-candidatos-ao-governo-da-paraiba", "Jornal da Paraíba, checagem do debate de 29/09/2026"),
    "pba_lucas": ("https://www.pbagora.com.br/noticia/politica/lucas-ribeiro-reage-a-acao-de-cicero-lucena-na-justica-eleitoral-e-acusa-adversario-de-espetacularizar-a-eleicao/", "PB Agora, 30/09/2026"),
    "jp_efraim": ("https://jornaldaparaiba.com.br/politica/pleno-poder/suplente-investigado-nas-fraudes-do-inss-e-pagamento-de-boleto-vao-exigir-explicacoes-de-efraim", "Jornal da Paraíba, 24/03/2026"),
    "termo_lucas_tre": ("https://www.termometrodapolitica.com.br/eleicoes/noticia/2026/07/10/tre-pb-condena-governador-lucas-ribeiro-por-uso-de-espaco-oficial-em-reuniao-politica/", "Termômetro da Política, 10/07/2026"),
    "jp_aije_folha": ("https://jornaldaparaiba.com.br/politica/conversa-politica/cicero-aciona-tre-pb-lucas-ribeiro-joao-azevedo-inchaco-folha-eleitoral", "Jornal da Paraíba, 10/09/2026"),
    "pbo_cicero_destaque": ("https://paraibaonline.com.br/eleicoes/2026/10/03/defesa-de-cicero-lucena-comemora-pedido-de-vista-em-julgamento-no-tse/", "Paraíba Online, 03/10/2026"),
    "jp_cicero_tse": ("https://jornaldaparaiba.com.br/politica/tse-forma-maioria-para-barrar-candidatura-de-cicero-lucena-ao-governo-da-paraiba", "Jornal da Paraíba, 02/10/2026"),
    "mppb_tl": ("https://www.mppb.mp.br/index.php/pt/comunicacao/noticias/51-gaeco/72-gaeco/26784-justica-acolhe-denuncia-do-mppb-no-ambito-da-operacao-territorio-livre", "MPPB, 16/09/2025"),
    "cf_cicero": ("https://congressoemfoco.com.br/area/pais/cicero-lucena-responsabiliza-adversarios-por-prisao-de-esposa-ataque-covarde-e-brutal", "Congresso em Foco, 28/09/2024"),
    "jp_confraria": ("https://jornaldaparaiba.com.br/_/125686", "Jornal da Paraíba, 13/11/2019"),
    "og_confraria": ("https://www.osguedes.com.br/2019/11/14/cicero-sobre-a-operacao-confraria-sempre-tive-a-consciencia-limpa/", "Os Guedes (Nonato Guedes), 14/11/2019"),
    "jp_calvario": ("https://jornaldaparaiba.com.br/politica/conversa-politica/operacao-calvario-mppb-arquiva-inquerito-joao-azevedo", "Jornal da Paraíba, 13/01/2026"),
    "jp_joao_2022": ("https://jornaldaparaiba.com.br/politica/conversa-politica/justica-insercoes-fake-news-calvario-contra-pedro", "Jornal da Paraíba, 25/10/2022"),
    "stf_ven_912": ("https://noticias.stf.jus.br/postsnoticias/determinado-trancamento-de-acao-penal-contra-deputado-veneziano-vital-do-rego/", "STF, notícia de 07/03/2017"),
    "stf_ven_933": ("https://noticias.stf.jus.br/postsnoticias/2a-turma-extingue-acao-penal-contra-deputado-federal-por-nulidade-na-investigacao/", "STF, notícia de 06/10/2015"),
    "rpb_nabor": ("https://www.reporterpb.com.br/noticia/sertao/2026/04/06/patos-recurso-de-nabor-wanderley-e-negado-e-tce-confirma-irregularidades/185662.html", "Repórter PB, 06/04/2026"),
    "pba_nabor": ("https://www.pbagora.com.br/noticia/politica/tse-da-provimento-a-recurso-de-nabor-wanderley-e-absolve-ex-prefeito-de-patos-em-caso-sobre-gastos-com-publicidade/", "PB Agora, 26/06/2026"),
    "cnn_cpi": ("https://www.cnnbrasil.com.br/politica/veja-lista-dos-supostos-crimes-apontados-no-relatorio-da-cpi-da-pandemia/", "CNN Brasil, 10/2021"),
    "sen_cpi": ("https://www12.senado.leg.br/noticias/materias/2022/07/26/senadores-contestam-arquivamento-de-investigacoes-indicadas-pela-cpi-da-pandemia", "Agência Senado, 26/07/2022"),
    "oeste_queiroga": ("https://revistaoeste.com/brasil/queiroga-nao-comento-relatorio-minha-funcao-e-salvar-vidas/", "Revista Oeste, 20/10/2021"),
    "tse_bens": ("https://cdn.tse.jus.br/estatistica/sead/odsele/bem_candidato/", "TSE, bens declarados (bem_candidato 2018, 2022, 2026)"),
    "tse_hist": ("https://cdn.tse.jus.br/estatistica/sead/odsele/historico_candidatura/historico_candidatura_2026.zip", "TSE, histórico de candidaturas 2026"),
}


def src(key):
    url, label = S[key]
    return {"url": url, "accessed": ACC, "label": label}


def c(text, support, key, kind="text", **meta):
    return {"text": text, "support": support, "source": src(key), "kind": kind, **meta}


ITEMS = [
    # ---------------- presidente ----------------
    dict(id="lula-lava-jato", candidateId="presidente-13", category="justica",
         title="Condenações da Lava Jato anuladas; caso do triplex arquivado por prescrição",
         status="Condenações anuladas pelo STF (2021); ação do triplex arquivada por prescrição (2022)",
         statusKeys=[("dn_lula", "manter a anulação das condenações"), ("istoe_lula", "prescrição")],
         date="2022-01-27", name="Lula",
         claims=[
             c("Em 2017, Lula foi condenado em primeira instância no caso do triplex do Guarujá por corrupção passiva e lavagem de dinheiro.",
               "Em 2017, Lula foi condenado pelo então juiz Sergio Moro a 9 anos e 6 meses de prisão por corrupção passiva e lavagem de dinheiro no caso do tríplex do Guarujá.", "jb_lula"),
             c("Em abril de 2021, o plenário do STF manteve, por 8 votos a 3, a anulação das condenações dele na Lava Jato.",
               "decidiu, por oito votos a favor e três contra, manter a anulação das condenações do ex-presidente Lula na operação Lava Jato", "dn_lula"),
             c("Em janeiro de 2022, a Justiça Federal do DF arquivou a ação do triplex por prescrição; ele não pode mais ser processado por esses fatos.",
               "ele não poderá ser processado pelos mesmos fatos que lhe foram imputados", "istoe_lula"),
         ],
         response=[c("A defesa afirma que o caso serviu para perseguição judicial com objetivos políticos (lawfare).",
                     "O encerramento definitivo do caso do tríplex pela Justiça reforça que ele serviu apenas para que alguns membros do Sistema de Justiça praticassem lawfare contra Lula", "istoe_lula")],
         responseExpected=True),
    dict(id="lula-checagem", candidateId="presidente-13", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "errou")],
         date="2026-10-01", name="Lula",
         claims=[
             c("A Lupa apontou erro ao dizer que o PIB só voltou a crescer acima de 3% depois de 2023.",
               "o presidente Lula errou ao falar que o Produto Interno Bruto (PIB) do país só voltou a crescer acima de 3% após seu retorno à Presidência, em 2023", "lupa"),
             c("A mesma checagem registrou acertos, como o crescimento de 7,5% em 2010.",
               "Lula acertou ao afirmar que o Brasil cresceu 7,5% em 2010", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="flavio-rachadinha", candidateId="presidente-22", category="justica",
         title="Caso das rachadinhas na Alerj",
         status="Denúncia rejeitada pelo TJRJ (maio/2022) depois que STJ e STF anularam provas; arquivado sem análise do mérito",
         statusKeys=[("im_flavio", "rejeitou a denúncia")],
         date="2022-05-16", name="Flávio",
         claims=[
             c("Em 2020, o MPRJ o denunciou sob acusação de liderar um esquema para recolher parte do salário de ex-funcionários do gabinete na Alerj.",
               "Em 2020, Flávio Bolsonaro — que é o filho mais velho do presidente — foi denunciado pelo Ministério Público do Rio de Janeiro sob acusação de liderar uma organização criminosa para recolher parte do salário de ex-funcionários públicos em benefício próprio", "cb_flavio"),
             c("Em 2022, o Órgão Especial do TJRJ rejeitou a denúncia, porque as provas usadas foram anuladas pelo STJ.",
               "O Órgão Especial do Tribunal de Justiça do Estado do Rio de Janeiro rejeitou a denúncia no processo movido contra o senador Flávio Bolsonaro", "im_flavio"),
             c("O arquivamento ocorreu sem análise do conteúdo das provas.",
               "por que o caso foi arquivado sem uma análise do conteúdo das provas", "cb_flavio"),
         ],
         response=[c("Ele e Fabrício Queiroz negaram todas as acusações.", "Fabrício Queiroz e Flávio Bolsonaro negaram todas as acusações.", "cb_flavio")],
         responseExpected=True),
    dict(id="flavio-checagem", candidateId="presidente-22", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "errou")],
         date="2026-10-01", name="Flávio",
         claims=[
             c("A Lupa apontou erro ao dizer que Jair Bolsonaro nunca foi ameaça para a democracia e ao negar o aquecimento global.",
               "Flávio, por sua vez, errou ao afirmar que Jair Bolsonaro “nunca foi ameaça para a democracia”, negou a existência do aquecimento global", "lupa"),
             c("A mesma checagem registrou acertos, como o Brasil seguir entre as economias com maior juro real.",
               "o candidato do PL acertou sobre o Brasil seguir no topo entre as economias com maior juro real do mundo", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="caiado-tre-go", candidateId="presidente-55", category="justica",
         title="Condenação por conduta vedada nas eleições de Goiânia em 2024",
         status="TRE-GO afastou a inelegibilidade e manteve multa de R$ 60 mil (abr/2025); cabia recurso ao TSE",
         statusKeys=[("ab_caiado", "manteve, contudo, a aplicação de multa de R$ 60 mil")],
         date="2025-04-08", name="Caiado",
         claims=[
             c("A Justiça Eleitoral entendeu que ele usou a sede do governo de Goiás em eventos da campanha do aliado Sandro Mabel.",
               "utilizar a sede do governo estadual para eventos ligados à campanha de seu aliado Sandro Mabel", "ab_caiado"),
             c("O TRE-GO derrubou por unanimidade a inelegibilidade aplicada em primeira instância.",
               "decidiu nessa terça-feira (8), por unanimidade, derrubar a inelegibilidade do governador do estado, Ronaldo Caiado", "ab_caiado"),
             c("O tribunal manteve a multa de R$ 60 mil por condutas vedadas nas eleições municipais de 2024.",
               "manteve, contudo, a aplicação de multa de R$ 60 mil ao governador, pela prática de condutas vedadas durante as eleições municipais de 2024", "ab_caiado"),
         ],
         response=[c("A defesa recorreu, alegando que os encontros foram regulares e restritos.",
                     "As defesas dos condenados entraram com recurso, alegando que os encontros foram regulares e fechados a um grupo restrito de pessoas", "ab_caiado")],
         responseExpected=True),
    dict(id="caiado-checagem", candidateId="presidente-55", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "errou")],
         date="2026-10-01", name="Caiado",
         claims=[
             c("A Lupa apontou erro ao dizer que Lula era alvo de investigações no STF.",
               "Caiado errou ao afirmar que Lula era alvo de investigações no Supremo Tribunal Federal (STF)", "lupa"),
             c("A mesma checagem registrou acertos sobre reforma administrativa e índices educacionais de Goiás.",
               "o ex-governador de Goiás acertou ao falar sobre reforma administrativa e índices educacionais do estado", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="cury-proposta-bolsa", candidateId="presidente-70", category="proposta",
         title="Proposta para o Bolsa Família que já existe",
         status="Checagem jornalística (Lupa, 29/08/2026): falta contexto", statusKeys=[("lupa_cury_jn", "já existe")],
         date="2026-08-29", name="Cury",
         claims=[
             c("No Jornal Nacional, prometeu que beneficiários do Bolsa Família poderiam ter uma segunda renda sem perder o benefício.",
               "Cury também prometeu o pagamento do Bolsa Família para pessoas que têm uma segunda fonte de renda, sem que elas percam o benefício. No entanto, essa possibilidade já existe.", "lupa_cury_jn"),
         ], response=[], responseExpected=False),
    dict(id="cury-checagem", candidateId="presidente-70", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "errou")],
         date="2026-10-01", name="Cury",
         claims=[
             c("A Lupa apontou erro, mais de uma vez, ao dizer que cada criança brasileira nasce devendo R$ 50 mil.",
               "O candidato errou, mais de uma vez, ao afirmar que uma criança brasileira “nasce devendo” R$ 50 mil", "lupa"),
             c("A mesma checagem registrou acertos, como o número de famílias no Bolsa Família.",
               "o candidato acertou ao citar o número de famílias que recebem o Bolsa Família", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="cury-experiencia", candidateId="presidente-70", category="experiencia",
         title="Primeira eleição disputada", status="Sem candidaturas anteriores no histórico do TSE", statusKeys=[],
         date="2026-08-15", name="Cury",
         claims=[c("O histórico de candidaturas do TSE não registra nenhuma eleição anterior disputada por ele.",
                   "presidente-70|0", "tse_hist", kind="tse-history")],
         response=[], responseExpected=False),
    dict(id="renan-danos-morais", candidateId="presidente-14", category="justica",
         title="Condenações cíveis por ofensas em redes sociais",
         status="Condenado a indenizar em ações cíveis por danos morais na Justiça de São Paulo (2025 e 2026)",
         statusKeys=[("mig_renan", "foi condenado a indenizar"), ("met_renan", "foi condenado")],
         date="2026-02-09", name="Renan",
         claims=[
             c("Foi condenado a pagar R$ 30 mil à filósofa Djamila Ribeiro por associá-la ao crime organizado em post no X.",
               "O fundador do MBL, Renan Santos, foi condenado a indenizar em R$ 30 mil a escritora e filósofa Djamila Ribeiro por ofensas publicadas na rede social X.", "mig_renan"),
             c("Foi condenado a indenizar o deputado estadual Gil Diniz (PL) por xingamentos publicados em 2021.",
               "foi condenado na Justiça paulista a indenizar o deputado estadual Gil Diniz", "met_renan"),
         ],
         response=[c("No caso de Gil Diniz, a defesa alegou liberdade de expressão e falta de prova de dano.",
                     "Já a defesa de Renan alegou que o deputado não provou os supostos danos causados à sua honra, e que o militante estava amparado pelo direito à liberdade de expressão", "met_renan")],
         responseExpected=True),
    dict(id="renan-checagem", candidateId="presidente-14", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "errou")],
         date="2026-10-01", name="Renan",
         claims=[
             c("A Lupa apontou erro ao dizer que o escândalo do Banco Master surgiu no governo Lula e dados falsos sobre o Bolsa Família.",
               "Renan Santos errou durante a campanha ao afirmar que o escândalo do Banco Master surgiu no governo Lula, citou dados falsos sobre o Bolsa Família", "lupa"),
             c("A mesma checagem registrou acertos, como sobre o endividamento do Brasil.",
               "Santos acertou ao falar do endividamento do Brasil", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="renan-experiencia", candidateId="presidente-14", category="experiencia",
         title="Primeira eleição disputada", status="Sem candidaturas anteriores no histórico do TSE", statusKeys=[],
         date="2026-08-15", name="Renan",
         claims=[c("O histórico de candidaturas do TSE não registra nenhuma eleição anterior disputada por ele.",
                   "presidente-14|0", "tse_hist", kind="tse-history")],
         response=[], responseExpected=False),
    dict(id="zema-rejeito", candidateId="presidente-30", category="investigacao",
         title="Decreto de licenciamento citado na Operação Rejeito",
         status="Investigação da PF em andamento (Operação Rejeito, set/2025); o despacho judicial cita o decreto",
         statusKeys=[("em_zema", "Operação Rejeito")],
         date="2025-09-17", name="Zema",
         claims=[
             c("Segundo o despacho judicial da Operação Rejeito, um decreto de Zema de novembro de 2024 retirou a exigência de pagar multas ambientais para seguir com o licenciamento e beneficiou uma mineradora investigada.",
               "foi modificado, em novembro do ano passado, por meio do Decreto 48.935, de 1º/11/2024 para retirar essa exigência e beneficiar a Patrimônio Mineração Ltda", "em_zema"),
         ],
         response=[c("Zema disse apoiar as investigações e esperar punição exemplar aos envolvidos.",
                     "Nós estamos dando todo o apoio às investigações.", "ot_zema")],
         responseExpected=True),
    dict(id="zema-checagem", candidateId="presidente-30", category="declaracao",
         title="Checagem da Lupa: erros e acertos na campanha",
         status="Checagem jornalística (Lupa, 01/10/2026)", statusKeys=[("lupa", "falsas")],
         date="2026-10-01", name="Zema",
         claims=[
             c("A Lupa apontou exagero sobre a dívida pública e afirmações falsas sobre segurança.",
               "Zema exagerou em dados sobre dívida pública, fez afirmações falsas sobre segurança pública", "lupa"),
             c("A mesma checagem registrou acertos, como a saída de Minas do déficit para o superávit.",
               "o ex-governador de Minas apontou avanços de sua gestão, como ter tirado o estado de um déficit para um superávit", "lupa"),
         ], response=[], responseExpected=False),
    dict(id="lucas-aije", candidateId="governador-11", category="justica",
         title="Ação eleitoral por suposta compra de votos",
         status="Ação de Investigação Judicial Eleitoral proposta por Cícero Lucena em 30/09/2026; sem julgamento",
         statusKeys=[("pba_lucas", "Ação de Investigação Judicial Eleitoral")],
         date="2026-09-30", name="Lucas",
         claims=[
             c("Cícero Lucena acionou a Justiça Eleitoral acusando ele e a vice Lígia Feliciano de compra de votos.",
               "A ação foi apresentada por Cícero Lucena à Justiça Eleitoral nesta quarta-feira (30), com acusações relacionadas à suposta compra de votos envolvendo Lucas Ribeiro e Lígia Feliciano.", "pba_lucas"),
         ],
         response=[c("Disse que os adversários estão desesperados e espetacularizando a eleição.",
                     "Estão desesperados, atacando de qualquer forma e qualquer jeito, espetacularizando a eleição para tentar chamar atenção de alguma forma", "pba_lucas")],
         responseExpected=True),
    dict(id="lucas-checagem", candidateId="governador-11", category="declaracao",
         title="Checagem do Jornal da Paraíba no debate de 29/09",
         status="Checagem jornalística (Jornal da Paraíba, 30/09/2026)", statusKeys=[("jp_debate", "A INFORMAÇÃO É INCORRETA")],
         date="2026-09-30", name="Lucas",
         claims=[
             c("Disse que 70% do PIB da Paraíba está fora da Grande João Pessoa; a checagem classificou como incorreto.",
               "“70% do nosso PIB está fora da grande João Pessoa.", "jp_debate", kind="rating", rating="A INFORMAÇÃO É INCORRETA"),
             c("A mesma checagem confirmou a fala sobre o resultado positivo do Caged em agosto.",
               "“Nesse mês de agosto, tivemos mais um resultado positivo do Caged, inclusive um dos maiores do país”.", "jp_debate", kind="rating", rating="A INFORMAÇÃO É VERDADEIRA"),
         ],
         response=[c("A assessoria disse que João Pessoa responde por 29,33% do PIB do estado.",
                     "A assessoria do candidato informou que João Pessoa responde por 29,33% do Produto Interno Bruto (PIB) da Paraíba", "jp_debate")],
         responseExpected=True),
    dict(id="lucas-tre-conduta", candidateId="governador-11", category="justica",
         title="Multa por reunião política em espaço oficial",
         status="TRE-PB aplicou multa de R$ 5 mil por conduta vedada (jul/2026), processo nº 0600060-87.2026.6.15.0000",
         statusKeys=[("termo_lucas_tre", "o TRE-PB aplicou multa no valor de R$ 5 mil")],
         date="2026-07-10", name="Lucas",
         claims=[
             c("O TRE-PB julgou procedente uma representação do MDB e reconheceu conduta vedada numa reunião político-eleitoral no gabinete da Vice-Governadoria, em abril de 2026.",
               "O Tribunal Regional Eleitoral da Paraíba (TRE-PB) julgou procedente representação movida pelo MDB estadual contra o governador Lucas Ribeiro.", "termo_lucas_tre"),
             c("Ele foi responsabilizado como beneficiário do ato e multado em R$ 5 mil.",
               "O governador foi responsabilizado na condição de beneficiário do ato, nos termos do artigo 73, § 8º, da Lei das Eleições.", "termo_lucas_tre"),
         ],
         response=[],
         responseExpected=False),
    dict(id="lucas-aije-folha", candidateId="governador-11", category="justica",
         title="Ação eleitoral sobre contratações temporárias",
         status="Ação de Investigação Judicial Eleitoral proposta em 10/09/2026 no TRE-PB; nenhum julgamento localizado até 04/10/2026",
         statusKeys=[("jp_aije_folha", "Ação de Investigação Judicial Eleitoral")],
         date="2026-09-10", name="Lucas",
         claims=[
             c("A coligação de Cícero Lucena acusa o governo estadual de abuso de poder e condutas vedadas pela contratação de mais de 6 mil servidores em ano eleitoral.",
               "A acusação é de que governo praticou suposto abuso de poder político e econômico e condutas vedadas com contratação de mais de 6 mil servidores.", "jp_aije_folha"),
             c("A ação pede a inelegibilidade por oito anos de Lucas Ribeiro e João Azevêdo.",
               "pede a declaração de inelegibilidade por oito anos de Lucas Ribeiro, João Azevêdo", "jp_aije_folha"),
         ],
         response=[],
         responseExpected=False),
    dict(id="joao-aije-folha", candidateId="senador-400", category="justica",
         title="Ação eleitoral sobre contratações temporárias",
         status="Ação de Investigação Judicial Eleitoral proposta em 10/09/2026 no TRE-PB; nenhum julgamento localizado até 04/10/2026",
         statusKeys=[("jp_aije_folha", "Ação de Investigação Judicial Eleitoral")],
         date="2026-09-10", name="João Azevêdo",
         claims=[
             c("A coligação de Cícero Lucena acusa o governo estadual de abuso de poder e condutas vedadas pela contratação de mais de 6 mil servidores em ano eleitoral.",
               "A acusação é de que governo praticou suposto abuso de poder político e econômico e condutas vedadas com contratação de mais de 6 mil servidores.", "jp_aije_folha"),
             c("A ação pede a inelegibilidade por oito anos de Lucas Ribeiro e João Azevêdo.",
               "pede a declaração de inelegibilidade por oito anos de Lucas Ribeiro, João Azevêdo", "jp_aije_folha"),
         ],
         response=[],
         responseExpected=False),
    dict(id="efraim-suplente", candidateId="governador-22", category="investigacao",
         title="Suplente no Senado investigado nas fraudes do INSS",
         status="Efraim não é investigado; o suplente Erik Marinho foi alvo de busca na Operação Sem Desconto (PF)",
         statusKeys=[("jp_efraim", "Efraim Filho não é investigado")],
         date="2026-03-24", name="Efraim",
         claims=[
             c("Seu suplente no Senado, Erik Marinho, é investigado pela PF por suspeita de ocultar patrimônio ligado ao chamado Careca do INSS.",
               "A Polícia Federal apontou que o suplente Erik Marinho atuava para ocultar e blindar patrimônio ligado a Antonio Carlos Camilo Antunes, conhecido como 'Careca do INSS'", "jp_efraim"),
             c("Reportagem do Estadão revelou que o suplente pagou um boleto de R$ 51 mil do senador.",
               "o senador teve um boleto de R$ 51 mil pago pelo suplente", "jp_efraim"),
             c("Efraim não é investigado no caso.", "Efraim Filho não é investigado.", "jp_efraim"),
         ],
         response=[c("Negou irregularidade e disse que o boleto vinha de uma dívida pessoal.",
                     "Efraim negou qualquer tipo de irregularidade. Afirmou que o boleto era oriundo de uma dívida pessoal", "jp_efraim")],
         responseExpected=True),
    dict(id="efraim-checagem", candidateId="governador-22", category="declaracao",
         title="Checagem do Jornal da Paraíba no debate de 29/09",
         status="Checagem jornalística (Jornal da Paraíba, 30/09/2026)", statusKeys=[("jp_debate", "A INFORMAÇÃO É INCORRETA")],
         date="2026-09-30", name="Efraim",
         claims=[
             c("Disse que 95% das delegacias da Paraíba fecham à noite; a checagem classificou como incorreto (são 86%).",
               "95% das delegacias são fechadas na Paraíba, à noite, na hora que você e sua família mais precisam\".", "jp_debate", kind="rating", rating="A INFORMAÇÃO É INCORRETA"),
             c("A mesma checagem confirmou a fala sobre os concursados da PB Saúde ainda aguardando convocação.",
               "“Nós vamos convocar, por exemplo, os concursados da PB Saúde, que até hoje estão esperando.”", "jp_debate", kind="rating", rating="A INFORMAÇÃO É VERDADEIRA"),
         ],
         response=[c("A assessoria disse que o número traduz a concentração do atendimento noturno.",
                     "a referência aos 95% traduz a dimensão apontada pelo candidato para a concentração do atendimento noturno", "jp_debate")],
         responseExpected=True),
    dict(id="cicero-registro-tse", candidateId="governador-15", category="justica",
         title="Registro de candidatura contestado no TSE",
         status="Registro sub judice: julgamento no TSE suspenso em 02/10/2026 por pedido de destaque do ministro André Mendonça; sem decisão final",
         statusKeys=[("pbo_cicero_destaque", "pedido de destaque do ministro Mendonça")],
         date="2026-10-02", name="Cícero",
         claims=[
             c("No julgamento virtual de 02/10/2026, já havia votos pelo indeferimento do registro dele, em recurso do Ministério Público Eleitoral.",
               "O Tribunal Superior Eleitoral (TSE) formou maioria pelo indeferimento da candidatura de Cícero Lucena (MDB) ao governo da Paraíba nas eleições de 2026.", "jp_cicero_tse"),
             c("O MP Eleitoral aponta suposto uso de uma facção criminosa para favorecer o projeto político dele.",
               "O Ministério Público Eleitoral apontou suposto uso de uma facção criminosa para favorecer o projeto político do ex-prefeito de João Pessoa.", "jp_cicero_tse"),
             c("O ministro André Mendonça pediu destaque e o julgamento foi suspenso, sem decisão final.",
               "ficou suspenso após também um pedido de destaque do ministro Mendonça", "pbo_cicero_destaque"),
             c("Ele pode disputar a eleição neste domingo.",
               "Cícero Lucena pode concorrer ao cargo de governador no domingo (4)", "jp_cicero_tse"),
             c("Ele não tem condenação criminal nem denúncia formal contra si.",
               "Cícero Lucena não tem condenação criminal nem denúncia formal apresentada contra ele", "jp_cicero_tse"),
         ],
         response=[c("A defesa disse que, com o destaque, os votos já dados caem e o julgamento recomeça do zero.",
                     "Amanhã caem todos os votos que foram dados e recomeça do zero", "pbo_cicero_destaque")],
         responseExpected=True),
    dict(id="cicero-territorio-livre", candidateId="governador-15", category="familia",
         title="Esposa denunciada na Operação Território Livre",
         status="A esposa, Lauremília Lucena, é ré em ação penal eleitoral (denúncia recebida em set/2025)",
         statusKeys=[("mppb_tl", "recebeu a denúncia")],
         date="2025-09-16", name="Lauremília",
         claims=[
             c("A Justiça Eleitoral recebeu denúncia contra a então primeira-dama de João Pessoa, Lauremília Lucena, e outras nove pessoas.",
               "Foram denunciados: a primeira-dama da Capital, Maria Lauremília Assis de Lucena", "mppb_tl"),
             c("Segundo o MP, líderes de uma facção e parentes recebiam cargos na prefeitura de João Pessoa em troca de controle territorial nas eleições.",
               "líderes do grupo criminoso e seus parentes recebiam cargos e benefícios na Administração Pública Municipal", "mppb_tl"),
         ],
         response=[c("Na prisão dela, em 2024, a assessoria de Cícero chamou a operação de ataque arquitetado por adversários.",
                     "foi alvo de mais um ataque covarde e brutal, ardilosamente arquitetado por seus adversários às vésperas da eleição, envolvendo sua família", "cf_cicero")],
         responseExpected=True),
    dict(id="cicero-confraria", candidateId="governador-15", category="justica",
         title="Operação Confraria (2005)",
         status="Absolvido pelo TRF5 (nov/2019)",
         statusKeys=[("jp_confraria", "não cometeu os crimes")],
         date="2019-11-13", name="Cícero",
         claims=[
             c("Em 2005 foi alvo de mandado de prisão da PF na Operação Confraria, sobre suposto favorecimento a empreiteiras.",
               "foi alvo de mandado de prisão expedido pela Polícia Federal em meio a denúncias sobre a “Operação Confraria”", "og_confraria"),
             c("Em 2019, a Quarta Turma do TRF5 concluiu que ele não cometeu os crimes apontados pelo MPF.",
               "Quarta turma do TRF5 entendeu que o ex-prefeito não cometeu os crimes apontados pelo MPF.", "jp_confraria"),
         ],
         response=[c("Disse ter sempre tido a consciência limpa.", "Sempre tive a consciência limpa", "og_confraria")],
         responseExpected=True),
    dict(id="cicero-checagem", candidateId="governador-15", category="declaracao",
         title="Checagem do Jornal da Paraíba no debate de 29/09",
         status="Checagem jornalística (Jornal da Paraíba, 30/09/2026)", statusKeys=[("jp_debate", "A INFORMAÇÃO É INCORRETA")],
         date="2026-09-30", name="Cícero",
         claims=[
             c("Disse que João Pessoa é o destino mais procurado do Brasil; a checagem classificou como incorreto.",
               "“É tanto que João Pessoa hoje é a queridinha do Brasil, é o destino mais procurado do Brasil…”", "jp_debate", kind="rating", rating="A INFORMAÇÃO É INCORRETA"),
             c("A mesma checagem confirmou a retirada do ITBI na entrada de imóveis do Minha Casa, Minha Vida.",
               "“Retiramos o ITBI para o Programa Minha Casa, Minha Vida como entrada dos imóveis", "jp_debate", kind="rating", rating="A INFORMAÇÃO É VERDADEIRA"),
         ],
         response=[c("A assessoria citou rankings de plataformas de viagem que põem João Pessoa entre os destinos em alta.",
                     "a assessoria do candidato Cícero Lucena informou que relatórios de tendências de viagens baseados em dados da Booking.com e da Expedia", "jp_debate")],
         responseExpected=True),
    dict(id="yuri-experiencia", candidateId="governador-80", category="experiencia",
         title="Sem mandato anterior", status="Uma candidatura anterior, não eleito (TSE)", statusKeys=[],
         date="2026-08-15", name="Yuri",
         claims=[c("O histórico do TSE registra uma candidatura anterior, a prefeito de João Pessoa em 2024, sem eleição.",
                   "governador-80|1|0", "tse_hist", kind="tse-history")],
         response=[], responseExpected=False),
    dict(id="camilo-experiencia", candidateId="governador-29", category="experiencia",
         title="Sem mandato anterior", status="Seis candidaturas anteriores, nenhuma eleita (TSE)", statusKeys=[],
         date="2026-08-15", name="Camilo",
         claims=[c("O histórico do TSE registra seis candidaturas anteriores, de 2004 a 2024, sem nenhuma eleição.",
                   "governador-29|6|0", "tse_hist", kind="tse-history")],
         response=[], responseExpected=False),
    # ---------------- senador ----------------
    dict(id="joao-calvario", candidateId="senador-400", category="investigacao",
         title="Operação Calvário",
         status="Inquérito arquivado pelo MPPB em relação a ele (jan/2026); parte das hipóteses já havia sido arquivada no STJ",
         statusKeys=[("jp_calvario", "promoveu o arquivamento")],
         date="2026-01-13", name="João Azevêdo",
         claims=[
             c("Foi investigado na Operação Calvário, que apurou desvios na saúde e na educação no governo de Ricardo Coutinho.",
               "O Ministério Público da Paraíba (MPPB) promoveu o arquivamento da investigação criminal que apurava supostos crimes atribuídos ao governador João Azevêdo (PSB) no âmbito da Operação Calvário.", "jp_calvario"),
             c("A PGR chegou a apontar 11 hipóteses envolvendo ele, parte delas arquivada no STJ.",
               "a Procuradoria-Geral da República chegou a apontar 11 hipóteses envolvendo João Azevêdo, parte delas já arquivadas no STJ", "jp_calvario"),
             c("O MPPB concluiu que as acusações se apoiavam só em delações e não encontrou indícios mínimos de participação dele.",
               "não foi possível identificar indícios mínimos da participação de João Azevêdo nos crimes investigados", "jp_calvario"),
         ], response=[], responseExpected=False),
    dict(id="joao-propaganda-2022", candidateId="senador-400", category="declaracao",
         title="Propaganda de 2022 suspensa pelo TRE-PB, que a considerou falsa",
         status="Inserção suspensa por decisão de juíza do TRE-PB (out/2022)",
         statusKeys=[("jp_joao_2022", "determinou a imediata suspensão")],
         date="2022-10-25", name="João Azevêdo",
         claims=[
             c("Em 2022, a Justiça Eleitoral suspendeu uma inserção da campanha dele contra Pedro Cunha Lima.",
               "determinou a imediata suspensão de uma inserção eleitoral de João Azevêdo (PSB) contra Pedro Cunha Lima (PSDB)", "jp_joao_2022"),
             c("A juíza considerou a peça propagação de informação falsa e difamatória.",
               "O material, veiculado em inserções no rádio e TV, foi considerado propagação de informação falsa e difamatória pela magistrada.", "jp_joao_2022"),
         ], response=[], responseExpected=False),
    dict(id="veneziano-stf", candidateId="senador-155", category="justica",
         title="Ações penais encerradas no STF",
         status="Duas ações penais encerradas pelo STF sem julgamento do mérito (2015 e 2017)",
         statusKeys=[("stf_ven_912", "trancamento"), ("stf_ven_933", "extinguir")],
         date="2017-03-07", name="Veneziano",
         claims=[
             c("Em 2017, a Primeira Turma do STF trancou a AP 912, em que era acusado de fraude em licitação, por ausência de justa causa.",
               "determinou o trancamento da Ação Penal (AP) 912, na qual o deputado federal Veneziano Vital do Rêgo (PMDB-PB) era acusado de fraude em licitação", "stf_ven_912"),
             c("Em 2015, a Segunda Turma extinguiu a AP 933, sobre compra de votos em Campina Grande, por nulidade na investigação.",
               "extinguir, por ausência de justa causa, a Ação Penal (AP) 933, ajuizada contra o deputado federal Veneziano Vital do Rego (PMDB-PB), acusado de compra de votos", "stf_ven_933"),
         ], response=[], responseExpected=False),
    dict(id="nabor-tce", candidateId="senador-100", category="justica",
         title="Licitação de serviços gráficos em Patos",
         status="TCE-PB manteve decisão que julgou a denúncia procedente (mar/2026), sem anular o pregão",
         statusKeys=[("rpb_nabor", "rejeitaram o recurso")],
         date="2026-03-25", name="Nabor",
         claims=[
             c("O TCE-PB rejeitou por unanimidade o recurso dele e manteve a decisão que julgou procedente denúncia sobre um pregão de serviços gráficos.",
               "De forma unânime, os conselheiros rejeitaram o recurso de apelação apresentado pelo prefeito Nabor Wanderley", "rpb_nabor"),
             c("O tribunal apontou falhas pontuais, mas entendeu que não houve prejuízo à legalidade geral do processo.",
               "não houve prejuízo à legalidade geral do processo", "rpb_nabor"),
         ], response=[], responseExpected=False),
    dict(id="nabor-tse-publicidade", candidateId="senador-100", category="justica",
         title="Gastos com publicidade em 2024",
         status="Absolvido pelo TSE (jun/2026) após condenação e multa no TRE-PB",
         statusKeys=[("pba_nabor", "absolveu")],
         date="2026-06-26", name="Nabor",
         claims=[
             c("O TRE-PB o havia condenado por gastos com publicidade acima do limite no ano eleitoral de 2024.",
               "Nabor havia sido condenado pelo Tribunal Regional Eleitoral da Paraíba (TRE/PB) por supostamente ter ultrapassado o limite legal de despesas com publicidade institucional", "pba_nabor"),
             c("O TSE o absolveu da acusação de conduta vedada.",
               "O Tribunal Superior Eleitoral (TSE) absolveu o ex-prefeito de Patos, Nabor Wanderley da Nóbrega Filho, de acusações de conduta vedada", "pba_nabor"),
         ], response=[], responseExpected=False),
    dict(id="queiroga-cpi", candidateId="senador-222", category="investigacao",
         title="Pedido de indiciamento na CPI da Covid",
         status="CPI pediu indiciamento (out/2021); a PGR pediu o arquivamento das apurações (2022)",
         statusKeys=[("sen_cpi", "pediu o arquivamento")],
         date="2022-07-26", name="Queiroga",
         claims=[
             c("O relatório final da CPI da Covid sugeriu o indiciamento dele por prevaricação.",
               "O documento sugere indiciamento de seis pessoas por prevaricação. Além do presidente Bolsonaro, os ministros da Saúde, Marcelo Queiroga", "cnn_cpi"),
             c("A PGR pediu o arquivamento das apurações que o envolviam.",
               "Lindôra Araújo também pediu o arquivamento de apurações que envolviam os ministros Marcelo Queiroga (Saúde)", "sen_cpi"),
         ],
         response=[c("Disse que não comentaria o relatório e que sua função era salvar vidas.",
                     "Eu não comento relatório. Eu não sou comentarista de relatório. Eu sou ministro da Saúde.", "oeste_queiroga")],
         responseExpected=True),
    dict(id="major-fabio-nada", candidateId="senador-300", category="experiencia",
         title="Nada documentado na busca padrão",
         status="Nenhum processo, investigação ou checagem encontrada nas fontes do protocolo", statusKeys=[],
         date="2026-10-03", name="Major Fábio",
         claims=[c("O histórico do TSE registra oito candidaturas anteriores, de 2004 a 2024.",
                   "senador-300|8|any", "tse_hist", kind="tse-history")],
         response=[], responseExpected=False),
]


PATRIMONIO_IDS = ["presidente-13", "presidente-22", "presidente-14", "presidente-70", "presidente-55", "presidente-30",
                  "governador-11", "governador-22", "governador-15", "governador-80", "governador-29",
                  "senador-400", "senador-155", "senador-100", "senador-222", "senador-300"]


def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def patrimonio_items():
    import sys
    sys.path.insert(0, str(HERE.parent / "checks"))
    from check_polemicas import asset_total, history
    items = []
    for cid in PATRIMONIO_IDS:
        rows = history(cid)
        now = asset_total(cid, 2026)
        now_txt = f"{brl(now)} em bens" if now else "nenhum bem (R$ 0,00)"
        if rows:
            year = max(int(r["ANO_ELEICAO"]) for r in rows)
            ufs = {r["SG_UF"] for r in rows if int(r["ANO_ELEICAO"]) == year}
            assert year in (2018, 2022) or ufs == {"PB"}, (cid, year, ufs)
            before = asset_total(cid, year)
            before_txt = brl(before) if before else "nenhum bem (R$ 0,00)"
            text = (f"Declarou ao TSE {now_txt} em 2026 e {before_txt} na candidatura anterior, em {year}. "
                    "Valores nominais, sem correção pela inflação.")
            support = f"{cid}|{year}={before:.2f}|2026={now:.2f}"
        else:
            text = f"Declarou ao TSE {now_txt} em 2026. Não há candidatura anterior no histórico do TSE. Valor nominal, sem correção pela inflação."
            support = f"{cid}|2026={now:.2f}"
        items.append(dict(id=f"patrimonio-{cid}", candidateId=cid, category="patrimonio", title="Patrimônio declarado ao TSE",
                          status="Valores nominais declarados ao TSE (dados de 03/10/2026)", statusKeys=[], date="2026-10-03", name="",
                          claims=[c(text, support, "tse_bens", kind="tse-assets")], response=[], responseExpected=False))
    return items


def main():
    out = []
    ITEMS.extend(patrimonio_items())
    for item in ITEMS:
        for group in ("claims", "response"):
            for i, cl in enumerate(item[group]):
                cl["checkId"] = f"pol-{item['id']}-{group[0]}{i}"
        out.append(item)
    (HERE / "draft.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(len(out), "items")


if __name__ == "__main__":
    main()
