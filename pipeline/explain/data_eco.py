"""Explainers for the economy questions. Each claim: (text, support, source key)."""

SOURCES = {
    "rt-senado": ("https://www12.senado.leg.br/noticias/materias/2023/11/08/senado-aprova-reforma-tributaria-no-primeiro-turno-no-plenario",
                  "Agência Senado, 08/11/2023"),
    "arc-camara": ("https://www.camara.leg.br/noticias/964821-camara-aprova-texto-base-do-projeto-do-arcabouco-fiscal-votacao-prossegue-nesta-quarta-feira/",
                   "Agência Câmara, 23/05/2023"),
    "arc-sancao": ("https://www.camara.leg.br/noticias/993734-lei-do-arcabouco-fiscal-e-sancionada-novo-regime-substitui-o-teto-de-gastos-publicos/",
                   "Agência Câmara, 31/08/2023"),
    "ele-audiencia": ("https://www.camara.leg.br/noticias/614978-governo-aponta-vantagens-na-privatizacao-da-eletrobras-deputados-veem-riscos-a-soberania/",
                      "Agência Câmara, audiência sobre a privatização da Eletrobras, 2019"),
    "ele-mp": ("https://www.camara.leg.br/noticias/761755-camara-aprova-mp-que-viabiliza-desestatizacao-da-eletrobras",
               "Agência Câmara, 20/05/2021"),
    "bc-lei": ("https://www.camara.leg.br/noticias/727367-CAMARA-APROVA-PROJETO-DE-AUTONOMIA-DO-BANCO-CENTRAL",
               "Agência Câmara, 10/02/2021"),
    "bc-radio": ("https://www12.senado.leg.br/radio/1/noticia/2021/03/01/autonomia-do-banco-central-ja-e-lei",
                 "Rádio Senado, 01/03/2021"),
    "bc-debate": ("https://www.camara.leg.br/noticias/939810-camara-discute-aumento-das-taxas-de-juros-e-autonomia-do-bc/",
                  "Agência Câmara, 2023"),
    "ir-entenda": ("https://www12.senado.leg.br/noticias/materias/2025/11/05/entenda-as-regras-para-isencao-do-imposto-de-renda-e-taxacao-de-altas-rendas",
                   "Agência Senado, 05/11/2025"),
    "ir-senado": ("https://www12.senado.leg.br/noticias/materias/2025/11/05/isencao-de-ir-para-quem-ganha-ate-r-5-mil-segue-para-sancao",
                  "Agência Senado, 05/11/2025"),
    "ir-camara": ("https://www.camara.leg.br/noticias/1206672-camara-aprova-projeto-que-isenta-do-imposto-de-renda-quem-ganha-ate-r$-5-mil-por-mes",
                  "Agência Câmara, 01/10/2025"),
}

EXPLAINERS = {
    "eco-reforma-tributaria": {
        "whatItIs": [
            ("A reforma tributária (PEC 45/2019) troca cinco tributos sobre consumo (ICMS, ISS, IPI, PIS e Cofins) por três: IBS, CBS e Imposto Seletivo.",
             "O texto prevê a substituição de cinco tributos (ICMS, ISS, IPI, PIS e Cofins) por três: Imposto sobre Bens e Serviços (IBS), Contribuição sobre Bens e Serviços (CBS) e Imposto Seletivo (IS).", "rt-senado"),
            ("IBS e CBS são um IVA, Imposto sobre Valor Agregado: cada etapa da produção paga só sobre o valor que acrescentou, sem imposto sobre imposto. Esse modelo existe em mais de 170 países.",
             "Esse tipo de tributo incide somente sobre o que foi agregado em cada etapa da produção de um bem ou serviço, excluindo valores pagos em etapas anteriores. O IVA já é adotado em mais de 170 países.", "rt-senado"),
            ("O Imposto Seletivo, apelidado de \"imposto do pecado\", cobra a mais de produtos que fazem mal à saúde ou ao meio ambiente, como cigarro e bebida alcoólica.",
             "funcionará como uma espécie de “taxa extra” sobre bens e serviços prejudiciais à saúde e ao meio ambiente. É o caso de cigarros e de bebidas alcoólicas.", "rt-senado"),
        ],
        "inPractice": [
            ("O imposto passa a ser cobrado no local onde o produto é consumido, e não onde é produzido. A ideia é acabar com a guerra fiscal, em que estados dão descontos de imposto para atrair empresas.",
             "a cobrança de impostos deixará de ser feita na origem (local de produção) e passará a ser feita no destino (local de consumo). A mudança visa dar fim à chamada guerra fiscal", "rt-senado"),
            ("Itens da cesta básica nacional, como arroz e feijão, ficam isentos, e famílias de baixa renda recebem de volta parte do imposto (o chamado cashback).",
             "o texto também prevê a devolução de parte do imposto pago pelos consumidores, o chamado “cashback”. A medida vale para famílias de baixa renda", "rt-senado"),
            ("A Emenda inclui uma \"trava\": a carga dos novos tributos não pode passar da média de 2012 a 2021, medida em proporção do PIB.",
             "o limite para a carga tributária será a média de 2012 a 2021, na proporção com o Produto Interno Bruto (PIB)", "rt-senado"),
        ],
        "argsFor": [
            ("O líder do governo no Congresso, senador Randolfe Rodrigues, disse que a reforma reduz tributos para os mais pobres e citou alíquota zero para arroz e feijão.",
             "afirmou que a aprovação da PEC é “histórica” e que vai garantir uma redução de tributos para a população mais pobre. Ele ressaltou que o texto prevê alíquota zero para arroz e feijão", "rt-senado"),
            ("O relator, senador Eduardo Braga, afirmou que o modelo não aumenta a carga tributária.",
             "Se o receio é que aprovação da PEC acarrete aumento de carga tributária, temos a convicção de que o modelo garante que isso não ocorrerá — disse Braga.", "rt-senado"),
        ],
        "argsAgainst": [
            ("O líder da oposição, senador Rogerio Marinho, disse que a reforma aumentaria a carga para a maior parte da população e que o texto foi \"desconfigurado\" por exceções a setores.",
             "afirmou que a reforma vai na prática aumentar a carga tributária para a maior parte da população. Segundo o senador, a proposta foi “desconfigurada” e está longe de simplificar o atual modelo.", "rt-senado"),
            ("O senador Oriovisto Guimarães argumentou que a transição deixa o sistema mais complexo e que estados e municípios perdem arrecadação.",
             "o sistema tributário vai ficar ainda mais complexo durante o período de transição, porque os atuais tributos vão coexistir com os novos. Ele ainda alertou sobre os riscos da reforma para o equilíbrio federativo.", "rt-senado"),
        ],
        "nuance": [
            ("Boa parte da divergência não é sobre trocar os impostos, e sim sobre quantos setores ganham regime diferenciado. Transportes, combustíveis, saneamento, planos de saúde e bancos estão na lista.",
             "Entre os setores que terão regimes diferenciados segundo o texto estão transportes, combustíveis, saneamento, planos de saúde, setor imobiliário, jogos de prognósticos, loterias, instituições financeiras, incluindo bancos.", "rt-senado"),
            ("A alíquota final ainda estava em disputa na votação: emendas da oposição para limitar a soma das alíquotas a 20% ou 25% foram rejeitadas.",
             "senadores rejeitaram destaques apresentados por senadores da oposição para limitar a soma das alíquotas dos tributos. Uma das emendas previa o teto de 20%; outra estabelecia um limite de 25%.", "rt-senado"),
        ],
    },
    "eco-arcabouco": {
        "whatItIs": [
            ("O arcabouço fiscal (Lei Complementar 200/2023) é a regra que limita quanto o governo federal pode gastar a cada ano. Ele substituiu o teto de gastos.",
             "novo regime para as contas da União que vai substituir o teto de gastos públicos.", "arc-sancao"),
            ("A despesa pode crescer, acima da inflação, até 70% do crescimento real da receita. Se a meta de resultado primário for descumprida, esse percentual cai para 50%. Resultado primário é a diferença entre receitas e despesas sem contar os juros da dívida.",
             "- 70% da variação real da receita caso seja cumprida a meta de resultado primário do ano anterior ao de elaboração da Lei Orçamentária Anual ( LOA ); ou", "arc-camara"),
        ],
        "inPractice": [
            ("Todo ano o gasto cresce pelo menos 0,6% e no máximo 2,5% acima da inflação, mesmo que a receita suba mais.",
             "todo ano ela crescerá ao menos 0,6%, com base na variação da receita. Já o máximo de aumento será equivalente a 2,5%, mesmo que a aplicação dos 70% da variação da receita resulte em valor maior.", "arc-camara"),
            ("Se a meta não for cumprida, o governo é obrigado a adotar medidas de contenção de gastos.",
             "Cajado incluiu ainda a obrigatoriedade de o governo adotar medidas de contenção de despesas caso não seja atingido o patamar mínimo para a meta de resultado primário", "arc-camara"),
        ],
        "argsFor": [
            ("O governo argumenta que a regra é mais flexível que o teto e permite \"acomodar choques econômicos\" sem perder o controle do Orçamento.",
             "Segundo o governo, o novo regime fiscal é mais flexível, o que permitirá \"acomodar choques econômicos, mas sem comprometer a consistência do Orçamento no médio e longo prazo\".", "arc-sancao"),
            ("O deputado Alencar Santana (PT-SP) disse que a regra garante o aumento real do salário mínimo e o Bolsa Família, que não estavam assegurados no teto de gastos.",
             "destacou o compromisso com o aumento real do salário mínimo e com o Bolsa Família, que não estavam garantidos sob o regime do teto de gastos.", "arc-camara"),
        ],
        "argsAgainst": [
            ("Pela direita, o deputado Marcel van Hattem (Novo-RS) disse que a regra vai \"incentivar a gastança\" e defendeu o modelo do teto de gastos.",
             "O deputado Marcel van Hattem (Novo-RS) afirmou que o novo regime fiscal vai \"incentivar a gastança\".", "arc-camara"),
            ("Pela esquerda, o deputado Chico Alencar (Psol-RJ) chamou a regra de \"regime de emagrecimento das políticas públicas\", por limitar o crescimento dos gastos.",
             "\"É um regime de emagrecimento das políticas públicas. Limitar de 0,6% a 2,5% de gastos não é teto?\", questionou.", "arc-camara"),
        ],
        "nuance": [
            ("A regra é criticada pelos dois lados: uns acham que permite gastar demais, outros que corta políticas públicas. Discordar da frase pode significar qualquer uma das duas posições.",
             "Para alguns deputados, no entanto, o ideal é o modelo do teto de gastos.", "arc-camara"),
            ("Parte das discussões é sobre o que fica dentro ou fora do limite, como o Fundeb, fundo que financia a educação básica.",
             "Muitos deputados, no entanto, destacaram preocupação com a inclusão do Fundeb nos limites da meta.", "arc-camara"),
        ],
    },
    "eco-privatizacao": {
        "whatItIs": [
            ("Privatizar é vender o controle de uma empresa estatal para acionistas privados. A MP 1031/2021 abriu caminho para privatizar a Eletrobras, que responde por cerca de 30% da energia gerada no país.",
             "viabiliza a desestatização da Eletrobras, estatal vinculada ao Ministério de Minas e Energia que responde por 30% da energia gerada no País.", "ele-mp"),
            ("O modelo usado foi a emissão de novas ações vendidas no mercado sem a participação do governo, que assim perdeu o controle de voto.",
             "O modelo de desestatização prevê a emissão de novas ações da Eletrobras, a serem vendidas no mercado sem a participação do governo, resultando na perda do controle acionário de voto mantido atualmente pela União.", "ele-mp"),
        ],
        "inPractice": [
            ("A União manteve uma \"golden share\", ação especial com poder de veto, para impedir que um acionista ou grupo tenha mais de 10% do capital votante.",
             "a União terá uma ação de classe especial ( golden share ) que lhe garante poder de veto em decisões da assembleia de acionistas a fim de evitar que algum deles ou um grupo de vários detenha mais de 10% do capital votante da Eletrobras.", "ele-mp"),
            ("Eletronuclear (usinas de Angra) e Itaipu ficaram fora da venda: pela Constituição, ambas precisam continuar sob controle da União.",
             "Por questões constitucionais, ambas devem ficar sob controle da União.", "ele-mp"),
        ],
        "argsFor": [
            ("Leandro Moreira, do Ministério da Economia, argumentou que a perspectiva de privatização trouxe eficiência e que o valor de mercado da empresa subiu de R$ 7,4 bilhões em 2013 para R$ 48 bilhões.",
             "o valor de mercado da Eletrobras passou de R$ 7,4 bilhões em 2013 para R$ 48 bilhões atualmente. Ele salientou que a perspectiva de desestatização trouxe eficiência e produtividade.", "ele-audiencia"),
            ("Leandro Moreira também argumentou que o Estado deve garantir abastecimento, qualidade e preço, e não necessariamente ser o dono da empresa, já que mantém regulação e fiscalização.",
             "o Estado brasileiro, mesmo com as privatizações, mantém o controle da concessão, da regulação, da fiscalização e da operação do setor elétrico.", "ele-audiencia"),
        ],
        "argsAgainst": [
            ("Gustavo Teixeira, da Federação Nacional dos Urbanitários, afirmou que os investimentos não dependem da privatização e que estatais têm papel importante em crises.",
             "afirmou que os investimentos no setor elétrico não dependem da desestatização e que especialistas reforçam o papel significativo das estatais em períodos de crise econômica.", "ele-audiencia"),
            ("A deputada Professora Marcivânia (PCdoB-AP) disse que a empresa era superavitária e estratégica para a soberania nacional, e lembrou que em vários países o setor hidrelétrico é majoritariamente estatal.",
             "acrescentou que em vários países o setor hidrelétrico é majoritariamente estatal por questões estratégicas.", "ele-audiencia"),
        ],
        "nuance": [
            ("Os próprios representantes do governo da época admitiram que as tarifas subiram nos anos anteriores mesmo com privatizações no setor, então o efeito no preço da luz é disputado.",
             "Os representantes do governo admitiram que, mesmo com a privatização de parte do setor elétrico, as tarifas para o consumidor aumentaram nos últimos anos.", "ele-audiencia"),
            ("A pergunta é geral: concordar não obriga a privatizar todas as estatais. O próprio modelo da Eletrobras deixou empresas estratégicas sob controle público.",
             "O texto autoriza o governo federal a criar uma empresa pública ou sociedade de economia mista para administrar a Eletronuclear (que controla as usinas de Angra) e a Itaipu Binacional.", "ele-mp"),
        ],
    },
    "eco-bc-autonomo": {
        "whatItIs": [
            ("A Lei Complementar 179/2021 deu ao Banco Central autonomia formal: presidente e diretores têm mandatos fixos de quatro anos que não coincidem com o do presidente da República.",
             "Os mandatos serão de quatro anos e haverá um escalonamento para que apenas no terceiro ano de um mandato presidencial a maioria da diretoria e o presidente do BC tenham sido indicados pelo mandatário do Poder Executivo.", "bc-lei"),
            ("O presidente da República continua indicando os nomes, que passam por sabatina no Senado, mas não pode demiti-los livremente.",
             "O presidente continua escolhendo. Mas o que entra não pode exonerar.", "bc-radio"),
        ],
        "inPractice": [
            ("A meta de inflação continua sendo fixada pelo Conselho Monetário Nacional (CMN), que inclui o governo. O BC decide como atingi-la, principalmente pela taxa de juros.",
             "as metas relacionadas ao controle da inflação anual continuam a cargo do Conselho Monetário Nacional (CMN), e o Banco Central terá os mesmos instrumentos atuais de política monetária.", "bc-lei"),
            ("Um diretor só pode ser exonerado por pedido próprio, doença, condenação ou \"desempenho insuficiente\", e neste último caso o Senado precisa aprovar.",
             "Neste último caso, caberá ao CMN submeter o pedido ao presidente da República; e a exoneração terá de passar também pelo Senado, com quórum de maioria absoluta para aprovação.", "bc-lei"),
        ],
        "argsFor": [
            ("O autor da lei, senador Plínio Valério, argumentou que mandatos fixos protegem as decisões do BC contra interferência do governo e do mercado.",
             "A ideia de mandatos fixos para os diretores do Banco Central é assegurar que eles tomem decisões sem interferências do mercado ou do próprio presidente da República ou ministro da Economia", "bc-radio"),
            ("O relator na Câmara, deputado Silvio Costa Filho, disse que a regra traz previsibilidade e permite um debate \"independente do governo de plantão\".",
             "\"Sobretudo para que a gente possa fazer um debate independente do governo de plantão. Se é um governo de centro, de esquerda, de direita\", defendeu.", "bc-debate"),
        ],
        "argsAgainst": [
            ("O então líder do PT, Enio Verri, defendeu que o BC também tivesse metas de emprego, como nos Estados Unidos, para evitar \"especulação financeira pura\".",
             "Se é importante a autonomia, por que não damos duplo papel, como nos Estados Unidos, cujo órgão tem de se preocupar também com o emprego, evitando a especulação financeira pura?", "bc-lei"),
            ("O deputado Chico Alencar (Psol-RJ) argumentou que o BC deveria estar a serviço do interesse público e criticou a ligação de diretores com o mercado financeiro.",
             "“Na verdade, um ente público como o BC tem que estar a serviço do interesse público e não como é hoje.", "bc-debate"),
        ],
        "nuance": [
            ("Há posições intermediárias: manter a autonomia, mas incluir o pleno emprego como objetivo. Uma emenda nesse sentido foi rejeitada em 2021, embora a lei cite fomentar o emprego como objetivo secundário.",
             "O principal objetivo da instituição continuará sendo assegurar a estabilidade de preços, mas também deverá zelar pela estabilidade e pela eficiência do sistema financeiro, suavizar as flutuações do nível de atividade econômica e fomentar o pleno emprego.", "bc-lei"),
            ("O debate costuma se misturar ao nível dos juros, mas são coisas diferentes: a autonomia define quem decide, não qual juro é o certo. Economistas divergem sobre se os juros altos de 2023 eram necessários.",
             "Logo, economistas como Armínio Fraga, ex-presidente do Banco Central, afirmaram que a taxa é alta mesmo; mas que só pode baixar quando existirem sinais mais claros de que as contas públicas ficarão equilibradas.", "bc-debate"),
        ],
    },
    "eco-ir-alta-renda": {
        "whatItIs": [
            ("O PL 1.087/2025 zera, na prática, o Imposto de Renda de quem ganha até R$ 5 mil por mês a partir de 2026 e reduz parcialmente para quem ganha até R$ 7.350.",
             "isenta do imposto os rendimentos mensais de até R$ 5 mil de pessoas físicas, e reduz parcialmente a tributação de rendas entre R$ 5.000,01 a R$ 7.350.", "ir-entenda"),
            ("Para compensar, cria um imposto mínimo para quem ganha a partir de R$ 600 mil por ano, que sobe gradualmente até 10% para rendas acima de R$ 1,2 milhão, contando dividendos.",
             "Haverá uma alíquota mínima de IR para quem ganha a partir de R$ 600 mil por ano. O texto prevê uma progressão, partindo de 0% e chegando a 10% para rendimentos acima de R$ 1,2 milhão por ano, incluindo dividendos.", "ir-entenda"),
        ],
        "inPractice": [
            ("O mínimo só é cobrado de quem paga menos que ele: quem já recolhe 10% ou mais sobre a renda total não paga nada a mais.",
             "o valor mínimo só será exigido se o imposto total já pago pelo contribuinte for inferior ao piso calculado.", "ir-entenda"),
            ("Dividendos acima de R$ 50 mil por mês de uma mesma empresa para uma pessoa passam a ter 10% retidos na fonte.",
             "em valor total maior de R$ 50.000 no mês ficará sujeita à incidência do IRPF de 10% sobre o pagamento", "ir-entenda"),
            ("Segundo a Câmara, cerca de 141,4 mil pessoas de alta renda pagavam em média 2,5% de IR sobre seus rendimentos totais, enquanto trabalhadores em geral pagam de 9% a 11%.",
             "pode atingir cerca de 141,4 mil contribuintes pessoas físicas de alta renda que hoje recolhem, em média, com alíquota efetiva de 2,5% de IR sobre seus rendimentos totais", "ir-camara"),
        ],
        "argsFor": [
            ("O relator no Senado, Renan Calheiros, resumiu a lógica: \"Quem tem menos, paga menos; quem tem mais, paga mais\".",
             "Quem tem menos, paga menos; quem tem mais, paga mais — disse o relator.", "ir-senado"),
            ("A senadora Eliziane Gama defendeu a medida como forma de reduzir desigualdade por meio da \"justiça tributária\".",
             "A justiça social se dá pelo resultado da justiça tributária — afirmou", "ir-senado"),
        ],
        "argsAgainst": [
            ("O líder do PL na Câmara, Sóstenes Cavalcante, chamou a isenção de \"troco\" e disse que o partido é \"sempre contra o aumento de impostos\".",
             "\"O nosso partido é sempre contra o aumento de impostos\", disse.", "ir-camara"),
            ("O deputado Capitão Alden (PL-BA) argumentou que os mais ricos vão levar recursos para o exterior e defendeu compensar a isenção com corte de gastos.",
             "Ele acredita que os brasileiros mais ricos que serão tributados devem transferir seus recursos para o exterior.", "ir-camara"),
        ],
        "nuance": [
            ("Mesmo críticos apoiam isentar quem ganha menos. O debate é sobre como pagar a isenção: imposto mínimo sobre altas rendas ou corte de gastos.",
             "Para o parlamentar, a isenção deveria subir para até R$ 10 mil, mas com a compensação dos recursos a ser feita por ações de austeridade do governo federal.", "ir-camara"),
            ("Há quem apoie a medida mas queira ir além: o senador Weverton disse que \"os especuladores ainda ganham muito mais do que os empreendedores\" e pediu correções mais amplas.",
             "Ainda temos um grave problema: os especuladores ainda ganham muito mais do que os empreendedores.", "ir-senado"),
        ],
    },
}

TOPICS = {
    "eco-reforma-tributaria": ["reforma tributária", "IBS", "CBS", "IVA"],
    "eco-arcabouco": ["arcabouço", "regime fiscal", "despesa"],
    "eco-privatizacao": ["Eletrobras", "privatiza", "desestatiza"],
    "eco-bc-autonomo": ["Banco Central", "BC"],
    "eco-ir-alta-renda": ["Imposto de Renda", "IR", "altas rendas"],
}
