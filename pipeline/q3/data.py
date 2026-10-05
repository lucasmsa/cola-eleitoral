"""Question bank v3: new nuanced questions, explainers, axes, option scales and evidence specs.

Every Claim support and every quote is checked verbatim by pipeline/checks/check_q3.py.
"""

ACC = "2026-10-03"


def S(url, label):
    return {"url": url, "accessed": ACC, "label": label}


R1 = S("https://www.congressoemfoco.com.br/noticia/118682/pec-do-fim-da-reeleicao-trava-ha-um-ano-no-senado-otto-cobra-votacao", "Congresso em Foco, 08/05/2026")
C1 = S("https://www.congressoemfoco.com.br/noticia/9473/governo-encerra-programa-de-escolas-civico-militares", "Congresso em Foco, 21/07/2023")
C2 = S("https://www.politize.com.br/escolas/", "Politize!, O que são as escolas cívico-militares?")
M1 = S("https://sbtnews.sbt.com.br/noticia/brasil/apos-descriminalizar-porte-de-maconha-para-uso-pessoal-stf-define-limite-para-usuario-nesta-quarta-26", "SBT News, 26/06/2024")
M2 = S("https://www.diariodepernambuco.com.br/amp/noticia/brasil/2024/06/porte-de-maconha-entenda-a-decisao-do-supremo-tribunal-federal.html", "Diario de Pernambuco, 27/06/2024")
M3 = S("https://www12.senado.leg.br/radio/1/noticia/2025/02/18/stf-mantem-descriminalizacao-do-porte-de-maconha-mas-senado-tem-proposta-contraria-1", "Rádio Senado, 18/02/2025")
M4 = S("https://www12.senado.leg.br/noticias/materias/2024/04/16/senado-aprova-pec-sobre-drogas-que-segue-para-a-camara", "Agência Senado, 16/04/2024")
F1 = S("https://www.politize.com.br/impostos-sobre-grandes-fortunas/", "Politize!, 09/07/2025")
F2 = S("https://capitalaberto.com.br/artigos/igf-no-brasil-uma-proposta-na-contramao-do-mundo/", "Capital Aberto, 20/03/2022")
T1 = S("https://congressoemfoco.com.br/noticia/107342/tarifa-zero-cresce-e-chega-a-145-cidades-e-5-4-milhoes-de-pessoas", "Congresso em Foco, 30/03/2025")
T2 = S("https://www.dgabc.com.br/Noticia/4287023/tarifa-zero-universal-em-todo-o-pais-segue-nos-planos-do-governo", "Diário do Grande ABC, 24/02/2026")
N1 = S("https://www.politize.com.br/?p=19476", "Politize!, PL das Fake News, 03/05/2023")
N2 = S("https://www.congressoemfoco.com.br/area/congresso-nacional/camara-aprova-urgencia-do-pl-das-fake-news/", "Congresso em Foco, 25/04/2023")
P1 = S("https://www.congressoemfoco.com.br/noticia/118276/pec-da-seguranca-emperra-no-senado-50-dias-apos-aprovacao-na-camara", "Congresso em Foco, 23/04/2026")
P2 = S("https://www.infomoney.com.br/politica/tarcisio-diz-que-pec-da-seguranca-publica-fere-de-morte-autonomia-dos-estados/", "InfoMoney/Estadão Conteúdo, 02/12/2025")
P3 = S("https://brasil61.com/n/governadores-criticam-mudancas-na-pec-da-seguranca-entenda-polemica-bras2513351", "Brasil 61, 21/01/2025")
E1 = S("https://congressoemfoco.com.br/legislativo/reforma-administrativa-pode-gerar-aumento-de-corrupcao-aponta-especialista", "Congresso em Foco, 25/09/2021")
E2 = S("https://www.band.com.br/noticias/canal-livre/ultimas/reforma-administrativa-tera-processo-de-meritocracia-para-servidores-publicos-entenda-202509281929", "Band, Canal Livre, 2025")
E3 = S("https://www.metropoles.com/brasil/reforma-administrativa-preve-mudancas-no-periodo-pre-estabilidade", "Metrópoles, 03/10/2025")
D1 = S("https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11611.htm", "Planalto, Decreto nº 11.611/2023")


def C(text, support, src):
    return {"text": text, "support": support, "source": src}


QUESTIONS = [
    {
        "id": "q3-fim-reeleicao", "area": "social", "offices": ["presidente", "governador", "senador", "deputado_federal"],
        "statement": "A reeleição para presidente, governador e prefeito deve acabar.",
        "context": "Uma PEC que acaba com a reeleição no Executivo e cria mandatos de cinco anos foi aprovada na CCJ do Senado em maio de 2025 e espera votação no plenário.",
        "contextChecks": [('Aprovada pela Comissão de Constituição e Justiça em maio de 2025 e pronta para votação em Plenário há quase um ano, a PEC que acaba com a reeleição para presidente, governadores e prefeitos continua parada no Senado.', R1), ('A proposta amplia os mandatos para cinco anos.', R1)],
        "sources": [R1],
        "options": [
            {"label": "Manter a reeleição como é hoje", "value": -1},
            {"label": "Manter, mas com regras mais duras para quem está no cargo", "value": -0.5},
            {"label": "Meio-termo, depende do desenho", "value": 0},
            {"label": "Acabar com a reeleição, com mandato de 4 anos", "value": 0.5},
            {"label": "Acabar com a reeleição e ter mandato único de 5 anos", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("A reeleição para presidente, governadores e prefeitos existe no Brasil desde 1997.",
                  "Marcelo Castro afirma que a experiência da reeleição, adotada no Brasil em 1997, não cumpriu a promessa de melhorar a qualidade dos governos", R1),
                C("A PEC 12/2022 acaba com a reeleição consecutiva para os chefes do Executivo e foi aprovada na CCJ do Senado em 21 de maio de 2025.",
                  "Relatada pelo senador Marcelo Castro (MDB-PI), a PEC 12/2022 foi aprovada na CCJ em 21 de maio de 2025.", R1),
            ],
            "inPractice": [
                C("Pela proposta, os mandatos passariam a ter cinco anos e todas as eleições aconteceriam no mesmo ano.",
                  "Pela proposta, todas as eleições ocorreriam no mesmo ano, a cada cinco anos. O eleitor seria chamado a escolher até nove cargos .", R1),
                C("A proibição começaria em 2028 para prefeitos e em 2030 para presidente e governadores.",
                  "A vedação à reeleição passaria a valer a partir de 2028 para prefeitos e de 2030 para presidente e governadores.", R1),
                C("Para virar regra, precisa de pelo menos 49 votos no Senado e 308 na Câmara, em dois turnos em cada Casa.",
                  "precisa passar em dois turnos no Senado, com pelo menos 49 votos favoráveis entre os 81 senadores. Se aprovada, seguirá para a Câmara, onde também dependerá do apoio de três quintos dos deputados (ao menos 308 votos) em dois turnos.", R1),
            ],
            "argsFor": [
                C("O relator, Marcelo Castro, argumenta que a reeleição estimula medidas de retorno eleitoral rápido em vez de projetos de longo prazo.",
                  "a possibilidade de recondução estimulou chefes do Executivo a adotar medidas de retorno eleitoral rápido, em prejuízo de projetos estruturantes e de longo prazo", R1),
                C("O parecer aprovado na CCJ diz que a reeleição favorece quem já está no cargo e dificulta a renovação política.",
                  "O parecer também sustenta que a reeleição favorece quem já ocupa o cargo, dificulta a renovação política e mantém governantes em estado permanente de campanha.", R1),
            ],
            "argsAgainst": [
                C("Críticos dizem que o fim da reeleição tira do eleitor a chance de manter um governante bem avaliado.",
                  "Uma das principais críticas é que o fim da reeleição reduziria o poder de escolha do eleitor. Mesmo um governante bem avaliado ficaria impedido de disputar a continuidade do mandato.", R1),
                C("Outro argumento contrário é que a reeleição funciona como prestação de contas: o eleitor premia ou pune a gestão.",
                  "Outro argumento é que a reeleição funciona como mecanismo de prestação de contas: o eleitor pode premiar uma boa administração ou punir uma gestão mal avaliada.", R1),
            ],
            "nuance": [
                C("Dá para ser contra a reeleição e contra o mandato de cinco anos: opositores dizem que cinco anos podem prolongar governos ruins.",
                  "Para opositores da mudança, mandatos de cinco anos podem ampliar o tempo de permanência de governos ruins.", R1),
                C("A eleição unificada também é debatida à parte: críticos temem que temas locais sejam engolidos pela disputa presidencial.",
                  "Já a eleição unificada poderia nacionalizar disputas locais, fazendo com que debates municipais fossem contaminados pela disputa presidencial.", R1),
            ],
        },
        "axis": None,
    },
    {
        "id": "q3-civico-militar", "area": "social", "offices": ["presidente", "governador", "deputado_estadual"],
        "statement": "O governo deve ampliar as escolas cívico-militares, em que militares cuidam da disciplina em escolas públicas.",
        "context": "O programa federal de escolas cívico-militares, criado em 2019, foi revogado por decreto em julho de 2023. Alguns governadores anunciaram que manteriam modelos próprios.",
        "contextChecks": [('O programa de escolas cívico-militares, estabelecido em 2019', C1), ('DECRETO Nº 11.611, DE 19 DE JULHO DE 2023 Revoga o Decreto nº 10.004, de 5 de setembro de 2019, que institui o Programa Nacional das Escolas Cívico-Militares.', D1), ('já anunciaram que pretendem preservar o modelo em suas unidades', C1)],
        "sources": [C1, D1],
        "options": [
            {"label": "Acabar com o modelo em todas as redes", "value": -1},
            {"label": "Não ampliar; manter só onde já existe", "value": -0.5},
            {"label": "Meio-termo, depende da escola e da comunidade", "value": 0},
            {"label": "Ampliar onde a comunidade escolar pedir", "value": 0.5},
            {"label": "Ampliar o modelo em todo o país", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("No modelo cívico-militar, reservistas das Forças Armadas, policiais militares e bombeiros passam a trabalhar em escolas públicas comuns.",
                  "insere reservistas das forças armadas, das polícias militares e dos corpos de bombeiros dentre os quadros dos centros de ensino fundamental e médio, adotando uma estrutura semelhante à dos colégios militares", C1),
                C("O programa federal foi revogado pelo Decreto 11.611, de 19 de julho de 2023.",
                  "DECRETO Nº 11.611, DE 19 DE JULHO DE 2023 Revoga o Decreto nº 10.004, de 5 de setembro de 2019, que institui o Programa Nacional das Escolas Cívico-Militares.", D1),
            ],
            "inPractice": [
                C("Com o fim do programa federal, as 216 escolas que tinham aderido deveriam voltar ao modelo comum.",
                  "as 216 escolas públicas que aderiram ao modelo deverão retornar ao modelo padrão", C1),
                C("Governadores como os de São Paulo e do Rio Grande do Sul anunciaram que manteriam o modelo em suas redes.",
                  "Alguns governadores, como Tarcício de Freitas , em São Paulo, e Eduardo Leite , no Rio Grande do Sul, já anunciaram que pretendem preservar o modelo em suas unidades.", C1),
            ],
            "argsFor": [
                C("Defensores dizem que a presença de militares traz disciplina e um ambiente menos violento.",
                  "um dos argumentos favoráveis ao programa é o de que a disciplina e a ordem instaurada pela presença dos militares colaboram com um ambiente mais pacífico e menos violento", C2),
                C("Uma pesquisa citada pela Politize! encontrou melhora no Ideb e queda da violência em escolas de Goiânia que aderiram.",
                  "Os números no Índice de Desenvolvimento da Educação Básica (Ideb) não apenas melhoraram, como os indicadores de violência escolar diminuíram.", C2),
            ],
            "argsAgainst": [
                C("O Todos Pela Educação argumenta que o modelo militarizado deveria ficar restrito às escolas das Forças Armadas e desvia recursos da educação.",
                  "O modelo militarizado de escolas deveria ser restrito às escolas das Forças Armadas, para jovens que desejam esse tipo de formação e carreira", C1),
                C("Professores criticam a troca da autoridade do professor pela do militar.",
                  "Uma das principais críticas dirigidas ao programa é a substituição do papel de autoridade e legitimidade dos professores.", C2),
            ],
            "nuance": [
                C("Há crítica também sobre custo: os estados poderiam não ter orçamento para contratar o pessoal extra sem tirar de outras áreas.",
                  "Outra crítica recorrente é a de que os estados não teriam orçamento suficiente para implementar a contratação dos novos funcionários escolares", C2),
                C("O então ministro da Educação, Camilo Santana, apontou que militares do programa recebiam bônus de R$ 9 mil, acima do salário médio de professor.",
                  "militares inscritos recebem um bônus de R$ 9 mil em seus soldos, enquanto que professores concursados recebem um salário médio de R$ 5 mil", C1),
            ],
        },
        "axis": {"axis": "social", "direction": 1, "rationale": "Convenção de método: ampliar a gestão disciplinar por militares nas escolas aponta para o polo de ordem e tradição do eixo de costumes."},
    },
    {
        "id": "q3-maconha-uso", "area": "seguranca", "offices": ["presidente", "senador", "deputado_federal"],
        "statement": "Portar até 40 gramas de maconha para uso próprio não deve ser crime, como decidiu o STF em 2024.",
        "context": "O STF decidiu em 2024 que portar maconha para consumo próprio não é crime e fixou 40 gramas como referência. O Senado aprovou em 2024 uma PEC que criminaliza o porte de qualquer quantidade; ela segue na Câmara.",
        "contextChecks": [('Foi estabelecido o parâmetro de 40g para diferenciar usuários de traficantes.', M3), ('Publicado em 27 de Junho, 2024 às 16:00 STF finalizou o julgamento que descriminalizou o porte de maconha para uso pessoal', M2), ('Da Agência Senado | 16/04/2024', M4), ('A PEC segue para a Câmara dos Deputados.', M4)],
        "sources": [M2, M4],
        "options": [
            {"label": "Deve ser crime, em qualquer quantidade", "value": -1},
            {"label": "Não ser crime, mas com limite menor que 40 g", "value": -0.5},
            {"label": "Meio-termo, não tenho certeza", "value": 0},
            {"label": "Não ser crime até 40 g, como decidiu o STF", "value": 0.5},
            {"label": "Não ser crime e regulamentar a venda", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("Por 6 votos a 3, o STF decidiu que portar maconha para uso pessoal não é crime e fixou 40 gramas para diferenciar usuário de traficante.",
                  "por 6 votos a 3, o Supremo Tribunal Federal (STF) finalizou o julgamento que descriminalizou o porte de maconha para uso pessoal e fixou a quantia de 40 gramas para diferenciar usuários de traficantes.", M2),
                C("O porte continua proibido: passou a ser um ilícito administrativo, não penal.",
                  "Os ministros concluíram que a conduta deve ser vista como um ilícito administrativo e não mais como ilícito penal .", M1),
            ],
            "inPractice": [
                C("Consumir em local público continua vedado.",
                  "Consumo em local público continua sendo vedado.", M1),
                C("O juiz ainda pode tratar como traficante quem está com uma quantidade permitida, mas com balança de precisão e muito dinheiro vivo.",
                  "se uma pessoa fosse flagrada com uma quantidade permitida de maconha, mas ela portasse balanças de precisão e alta quantia de dinheiro vivo, o magistrado poderia avaliar se nessas circunstâncias, ela seria enquadrada como traficante", M1),
            ],
            "argsFor": [
                C("O senador Marcelo Castro, que é psiquiatra, defende que dependentes precisam de atendimento médico e não de tratamento como criminosos.",
                  "Já o senador Marcelo Castro, MDB do Piauí, acredita que dependentes químicos precisam de atendimento médico e não ser tratados como criminosos.", M3),
                C("Para o senador Jaques Wagner, encher as cadeias não resolve o problema das drogas.",
                  "Não será entupindo as cadeias que nós vamos resolver os problemas das drogas no Brasil — disse Jaques Wagner.", M4),
            ],
            "argsAgainst": [
                C("O senador Rodrigo Pacheco, autor da PEC das drogas, argumenta que a decisão do STF invade a competência do Congresso e da Anvisa.",
                  "Para Pacheco, a decisão do STF invade a competência do Congresso Nacional e até da Anvisa.", M3),
                C("A PEC aprovada no Senado torna crime a posse de qualquer quantidade, mas proíbe prender o usuário.",
                  "faz a ressalva da impossibilidade da privação da liberdade do porte para uso; ou seja, o usuário não será, jamais, penalizado com o encarceramento", M4),
            ],
            "nuance": [
                C("O presidente do STF disse que a decisão disciplina a ilicitude e não legaliza a maconha.",
                  "Não estamos liberando, estamos tentando disciplinar a ilicitude de uma forma específica", M1),
                C("A decisão do STF partiu do artigo 28 da Lei de Drogas, de 2006, que trata do porte para consumo pessoal.",
                  "O julgamento no STF teve como ponto de partida o questionamento do artigo 28 da Lei de Drogas (de 2006)", M1),
            ],
        },
        "axis": {"axis": "social", "direction": -1, "rationale": "Convenção de método: tirar do direito penal o porte para uso pessoal aponta para o polo liberal nos costumes."},
    },
    {
        "id": "q3-grandes-fortunas", "area": "economia", "offices": ["presidente", "senador", "deputado_federal"],
        "statement": "O Brasil deve criar o imposto sobre grandes fortunas, previsto na Constituição e nunca regulamentado.",
        "context": "A Constituição de 1988 prevê o imposto sobre grandes fortunas (art. 153, VII), mas ele nunca foi regulamentado.",
        "contextChecks": [('O Imposto sobre Grandes Fortunas (IGF) está previsto na Constituição Federal de 1988 , no inciso VII do Artigo 153. Todavia, embora seja uma medida constitucional, o imposto nunca foi regulamentado e instituído no Brasil.', F1)],
        "sources": [F1],
        "options": [
            {"label": "Não criar; taxar patrimônio afasta investimento", "value": -1},
            {"label": "Não criar; preferir taxar lucros, dividendos e heranças", "value": -0.5},
            {"label": "Meio-termo, depende do desenho", "value": 0},
            {"label": "Criar, só para patrimônios muito altos", "value": 0.5},
            {"label": "Criar, com alíquotas progressivas", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("O imposto sobre grandes fortunas está no art. 153, VII, da Constituição de 1988, mas nunca foi regulamentado.",
                  "O Imposto sobre Grandes Fortunas (IGF) está previsto na Constituição Federal de 1988 , no inciso VII do Artigo 153. Todavia, embora seja uma medida constitucional, o imposto nunca foi regulamentado e instituído no Brasil.", F1),
                C("Diferente do imposto de renda, ele incide sobre o patrimônio acumulado, não sobre o que a pessoa ganha no ano.",
                  "Ele se distingue do imposto de renda (IR) ao incidir sobre o valor do patrimônio total acumulado (o que inclui propriedades e investimentos), em vez de se limitar aos valores recebidos no ano.", F2),
            ],
            "inPractice": [
                C("Propostas em debate cobrariam só de patrimônios acima de R$ 20 milhões.",
                  "O imposto seria cobrado, portanto, sobre aqueles patrimônios considerados grandes fortunas (acima de 20 milhões de reais)", F1),
                C("Poucos países cobram hoje: Espanha, Noruega, Suíça, Argentina, Colômbia e Uruguai, segundo a Capital Aberto.",
                  "Atualmente apenas Espanha, Noruega, Suíça, Argentina, Colômbia e Uruguai cobram tributo sobre o patrimônio de seus residentes", F2),
            ],
            "argsFor": [
                C("Segundo a Receita Federal, citada pela Politize!, os 10% mais pobres pagam proporcionalmente muito mais impostos que os mais ricos.",
                  "Segundo a Receita Federal, os 10% mais pobres comprometem até 32% da renda com tributos , enquanto os 0,1% mais ricos pagam menos de 7% .", F1),
                C("O economista Pedro Humberto argumenta que, como os contribuintes seriam poucos, a Receita teria como combater a sonegação.",
                  "Como o número de contribuintes é pequeno, a Receita Federal pode ter instrumentos para combater a evasão fiscal.", F1),
            ],
            "argsAgainst": [
                C("O principal argumento contrário é a fuga de capitais: os mais ricos levariam o dinheiro para outros países.",
                  "O principal ponto contra o IGF trata-se da fuga de capitais.", F1),
                C("A Capital Aberto lembra que vários países abandonaram o imposto por baixa arrecadação e fuga de capitais.",
                  "ao longo das últimas décadas diversos países foram abandonando a cobrança, seja porque ela tinha prazo para expirar, seja porque o imposto “não emplacou”, gerando baixa arrecadação³, fuga de capitais e impactos negativos para a economia.", F2),
            ],
            "nuance": [
                C("Há quem queira mais imposto sobre os ricos mas prefira outro caminho, como taxar lucros e dividendos.",
                  "Outra solução seria cobrar imposto sobre lucros e dividendos , que é o dinheiro que sócios ou investidores recebem de empresas.", F1),
                C("O pesquisador Celso Olindo Junior defende mudar o peso dos impostos para renda e propriedade em vez de criar o IGF.",
                  "o pesquisador Celso Olindo Junior entende que criar um imposto sobre grandes fortunas (IGF) não é a melhor solução para mudar a forma como o Brasil cobra impostos hoje", F1),
            ],
        },
        "axis": {"axis": "economico", "direction": -1, "rationale": "Convenção de método: criar um imposto sobre patrimônio para redistribuir aponta para o polo de mais Estado no eixo econômico."},
    },
    {
        "id": "q3-tarifa-zero", "area": "economia", "offices": ["presidente", "governador", "deputado_federal", "deputado_estadual"],
        "statement": "O transporte público por ônibus deve ser gratuito para todos (tarifa zero), pago com dinheiro público.",
        "context": "Segundo a NTU, 145 cidades têm algum tipo de gratuidade nos ônibus. O governo federal estuda uma tarifa zero nacional; um grupo de pesquisa estimou o custo em R$ 100 bilhões por ano.",
        "contextChecks": [('145 municípios oferecem gratuidade, parcial ou total, no sistema.', T1), ('A tarifa zero em todo o País segue nos planos da União.', T2), ('O custo estimado para garantir o funcionamento de todo o transporte público no Brasil é de R$ 100 bilhões por ano.', T2)],
        "sources": [T1, T2],
        "options": [
            {"label": "Não; quem usa deve pagar a passagem", "value": -1},
            {"label": "Só passagem mais barata com subsídio, sem gratuidade", "value": -0.5},
            {"label": "Meio-termo, depende da cidade", "value": 0},
            {"label": "Gratuidade para grupos (estudantes, desempregados) ou em alguns dias", "value": 0.5},
            {"label": "Tarifa zero para toda a população", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("Segundo a NTU, 145 municípios oferecem gratuidade total ou parcial nos ônibus, e em 120 deles vale todos os dias para todos.",
                  "145 municípios oferecem gratuidade, parcial ou total, no sistema. Em 120 deles, o benefício é válido todos os dias e para toda a população.", T1),
                C("Em média, o dinheiro público já cobre 32% do custo do serviço de ônibus no Brasil; o resto é pago pelos passageiros.",
                  "No Brasil, em média, 32% do custo de remuneração do serviço é coberto por subsídio público.O restante é bancado pelos passageiros.", T1),
            ],
            "inPractice": [
                C("Um grupo de pesquisa estimou em R$ 100 bilhões por ano o custo de bancar todo o transporte público do país.",
                  "O custo estimado para garantir o funcionamento de todo o transporte público no Brasil é de R$ 100 bilhões por ano.", T2),
                C("A maioria das cidades com tarifa zero é pequena: 61% têm menos de 50 mil habitantes.",
                  "61% das cidades com tarifa zero têm menos de 50 mil habitantes", T1),
            ],
            "argsFor": [
                C("As prefeituras que adotaram dizem que a medida reduz desigualdades, melhora o trânsito e incentiva o transporte coletivo.",
                  "Argumentam que a medida reduz desigualdades, melhora o trânsito e incentiva o uso do transporte coletivo.", T1),
                C("O ministro das Cidades vê a gratuidade como resposta à crise do modelo atual de financiamento dos ônibus.",
                  "pode ser uma resposta à crise enfrentada pela maioria dos sistemas de transporte público do País", T2),
            ],
            "argsAgainst": [
                C("A NTU, que reúne as empresas de ônibus, defende tarifa acessível e alerta que sem planejamento o sistema pode entrar em colapso.",
                  "Não somos contra a tarifa zero, mas defendemos uma tarifa acessível. Sem planejamento, o sistema pode entrar em colapso", T1),
                C("Nas capitais o custo é muito maior, o que dificulta universalizar a gratuidade.",
                  "O desafio para universalizar o benefício é maior nessas cidades devido aos altos custos envolvidos.", T1),
            ],
            "nuance": [
                C("Há caminhos intermediários: gratuidade aos domingos, só para desempregados ou só em linhas de periferia.",
                  "No Distrito Federal, desde o início de fevereiro o acesso aos ônibus é gratuito aos domingos e feriados. Em Curitiba, o benefício é voltado a pessoas desempregadas. Belo Horizonte oferece tarifa zero em linhas que atendem vilas e favelas.", T1),
                C("Algumas cidades cobram uma taxa das empresas no lugar do vale-transporte para ajudar a pagar a conta.",
                  "Algumas cidades, como Vargem Grande Paulista (SP), adotaram um modelo em que empresas pagam uma taxa em substituição ao vale-transporte, ajudando a redistribuir os custos.", T1),
            ],
        },
        "axis": {"axis": "economico", "direction": -1, "rationale": "Convenção de método: financiar com dinheiro público um serviço hoje pago pelo usuário aponta para o polo de mais Estado."},
    },
    {
        "id": "q3-redes-sociais", "area": "social", "offices": ["presidente", "senador", "deputado_federal"],
        "statement": "As redes sociais devem ser obrigadas por lei a remover conteúdo criminoso e responder na Justiça quando não agirem.",
        "context": "O PL das Fake News (PL 2630/2020) começou no Senado e chegou à Câmara em 2020. Na Câmara, a urgência foi aprovada em 2023.",
        "contextChecks": [('O Projeto de Lei nº 2630, de 2020 , PL das Fake News, está em tramitação desde 2020 e teve início no Senado Federal.', N1), ('Este foi o primeiro sucesso do texto em plenário desde 2020, quando a matéria chegou à Câmara.', N2), ('25/4/2023 | Atualizado 2/5/2023 às 15:53 A- A+ COMPARTILHE ESTA NOTÍCIA A urgência do PL das Fake News foi aprovada por 238 votos contra 192', N2)],
        "sources": [N1, N2],
        "options": [
            {"label": "Não; isso abre caminho para censura", "value": -1},
            {"label": "Só regras de transparência, sem punir as plataformas", "value": -0.5},
            {"label": "Meio-termo, depende das regras", "value": 0},
            {"label": "Sim, para crimes graves e proteção de crianças", "value": 0.5},
            {"label": "Sim, com um órgão regulador fiscalizando", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("O PL das Fake News cria regras para plataformas como Google, Meta, TikTok, WhatsApp e Telegram.",
                  "O PL das Fake News propõe a regulação das plataformas digitais , como Google, Meta (Instagram e Facebook), Twitter e TikTok, serviços de mensageria instantânea, como WhatsApp e Telegram.", N1),
                C("O ponto central é tornar obrigatória a moderação de conteúdo criminoso.",
                  "o ponto principal é tornar obrigatória a moderação de conteúdos publicados na internet para que contas ou publicações com conteúdos considerados criminosos possam ser identificadas, excluídas ou sinalizadas", N1),
            ],
            "inPractice": [
                C("O projeto responsabiliza as empresas por conteúdo publicado por terceiros, o que hoje não tem previsão em lei.",
                  "Uma das principais mudanças propostas é a responsabilização das empresas por conteúdos publicados por terceiros", N1),
                C("A Câmara aprovou a urgência do projeto por 238 votos a 192.",
                  "O item foi aprovado por 238 votos “sim” contra 192 votos “não”.", N2),
            ],
            "argsFor": [
                C("Defensores dizem que a lei fortalece a democracia e controla a difusão de notícias falsas e discursos de ódio.",
                  "Dentre os objetivos do PL 2630/2020, estão o fortalecimento da democracia, transparência dos provedores de internet que prestam serviço no Brasil e o controle na difusão de notícias falsas e discursos de ódio no ambiente virtual.", N1),
                C("O projeto também exige identificar quem patrocina anúncios, para evitar golpes financeiros.",
                  "Exige a identificação de usuários que patrocinam conteúdos publicados, essa seria uma forma de evitar anúncios falsos de golpes financeiros", N1),
            ],
            "argsAgainst": [
                C("Críticos, sobretudo à direita, chamam o texto de \"PL da Censura\" e dizem que ele ameaça a liberdade de expressão.",
                  "Parlamentares e cidadãos mais ligados à direita , têm criticado a proposta alegando cerceamento da liberdade de expressão dos usuários nas mídias sociais", N1),
                C("O partido Novo diz que o projeto transforma as plataformas em \"polícias digitais\".",
                  "Transforma as plataformas em “polícias digitais”", N1),
            ],
            "nuance": [
                C("As próprias big techs também se opuseram, por temer punições e riscos à liberdade de expressão.",
                  "Além de parlamentares, as big techs também acreditam que o projeto coloca em risco a liberdade de expressão dos usuários . As empresas também temem punições em caso de descumprimento da lei.", N1),
                C("Uma das versões do texto previa um conselho autônomo para supervisionar as plataformas, um dos pontos mais disputados.",
                  "Criação do Conselho de Transparência e Responsabilidade na Internet , entidade autônoma de supervisão para regulamentar e fiscalizar os provedores", N1),
            ],
        },
        "axis": None,
    },
    {
        "id": "q3-pec-seguranca", "area": "seguranca", "offices": ["presidente", "governador", "senador", "deputado_federal"],
        "statement": "A União deve ganhar mais poder para coordenar a segurança pública em todo o país, como prevê a PEC da Segurança.",
        "context": "A PEC 18/2025 foi aprovada pela Câmara em 4 de março de 2026 por ampla maioria e aguarda o Senado.",
        "contextChecks": [('A demora chama atenção porque a PEC 18/2025 é tratada pelo Planalto', P1), ('23/4/2026 7:00 A- A+ COMPARTILHE ESTA NOTÍCIA Aprovada há 50 dias pela Câmara dos Deputados , a PEC da Segurança Pública segue parada no Senado', P1), ('A proposta foi aprovada pelos deputados em 4 de março e autuada no Senado em 10 de março', P1), ('passou com ampla margem', P1)],
        "sources": [P1],
        "options": [
            {"label": "Não; segurança deve ficar com os estados", "value": -1},
            {"label": "Só mais dinheiro e cooperação, sem mudar a Constituição", "value": -0.5},
            {"label": "Meio-termo, não tenho certeza", "value": 0},
            {"label": "Sim, com coordenação federal e autonomia dos estados preservada", "value": 0.5},
            {"label": "Sim, com a União no comando da política de segurança", "value": 1},
        ],
        "explainer": {
            "whatItIs": [
                C("A PEC da Segurança põe na Constituição o Sistema Único de Segurança Pública (Susp) e reforça a integração entre as forças de União, estados e municípios.",
                  "constitucionaliza o Sistema Único de Segurança Pública (Susp); reforça a integração entre forças de segurança da União, dos estados, do DF e dos municípios", P1),
                C("O texto também dá à Polícia Federal competência expressa contra facções e milícias que atuam entre estados ou fora do país.",
                  "dá competência expressa à Polícia Federal para investigar crimes ligados a organizações criminosas e milícias com repercussão interestadual ou internacional", P1),
            ],
            "inPractice": [
                C("A Câmara aprovou a PEC por 487 a 15 no primeiro turno e 461 a 14 no segundo.",
                  "passou com ampla margem: 487 votos a 15 no primeiro turno e 461 a 14 no segundo", P1),
                C("A PEC autoriza municípios a criarem polícias municipais para policiamento ostensivo e comunitário.",
                  "autoriza a criação de polícias municipais para policiamento ostensivo e comunitário", P1),
            ],
            "argsFor": [
                C("O cientista político Eduardo Grin compara o desenho ao SUS: mais coordenação federal, com regras para acessar o fundo de segurança.",
                  "nos moldes de como é feito hoje com o Sistema Único de Saúde (SUS)", P3),
                C("O então ministro da Justiça, Ricardo Lewandowski, disse que a nova redação resolvia o ponto central da disputa, a autonomia dos estados.",
                  "põe fim ao ponto central da discussão: a perda da autonomia dos estados", P3),
            ],
            "argsAgainst": [
                C("O governador de São Paulo, Tarcísio de Freitas, disse que a proposta original era uma \"afronta\" à autonomia dos estados.",
                  "a PEC é uma “afronta” à autonomia dos Estados e os governos estaduais não podem aceitar serem “feridos de morte” pela União", P2),
                C("Tarcísio também chamou a proposta de \"cosmética\", sem resolver os problemas.",
                  "A gente percebeu logo de cara que a PEC era cosmética, que ela não resolveria os problemas.", P2),
            ],
            "nuance": [
                C("O texto aprovado diz que as novas atribuições da União não tiram dos governadores o comando das polícias.",
                  "nem restringem a subordinação das polícias militares, civis e penais e a dos corpos de bombeiros militares aos Governadores dos Estado", P3),
                C("A base do governo teme que o Senado inclua temas que ficaram de fora, como a redução da maioridade penal.",
                  "Um dos receios é que a oposição tente incluir temas que ficaram de fora da versão aprovada pela Câmara, como a redução da maioridade penal.", P1),
            ],
        },
        "axis": None,
    },
]

# Nuanced scales for existing questions; values keep each statement's stance mapping.
OPTIONS_EXISTING = {
    "soc-aborto": [
        {"label": "Crime em todos os casos, inclusive os permitidos hoje", "value": -1},
        {"label": "Manter só os casos atuais (estupro, risco de vida, anencefalia)", "value": -0.5},
        {"label": "Meio-termo, não tenho certeza", "value": 0},
        {"label": "Ampliar os casos permitidos, sem liberar até 12 semanas", "value": 0.5},
        {"label": "Permitido até 12 semanas", "value": 1},
    ],
    "seg-drogas": [
        {"label": "Descriminalizar o porte de todas as drogas para uso próprio", "value": -1},
        {"label": "Não ser crime só pequena quantidade de maconha, como decidiu o STF", "value": -0.5},
        {"label": "Meio-termo, não tenho certeza", "value": 0},
        {"label": "Crime, mas pela lei comum, sem mudar a Constituição", "value": 0.5},
        {"label": "Crime em qualquer quantidade, escrito na Constituição", "value": 1},
    ],
    "seg-armas": [
        {"label": "Proibir armas para civis", "value": -1},
        {"label": "Manter ou apertar as regras atuais", "value": -0.5},
        {"label": "Meio-termo, não tenho certeza", "value": 0},
        {"label": "Facilitar só a posse em casa", "value": 0.5},
        {"label": "Facilitar posse e porte", "value": 1},
    ],
    "eco-privatizacao": [
        {"label": "Reestatizar o que foi privatizado", "value": -1},
        {"label": "Manter as estatais que existem hoje", "value": -0.5},
        {"label": "Meio-termo, caso a caso", "value": 0},
        {"label": "Privatizar algumas, mantendo as estratégicas", "value": 0.5},
        {"label": "Privatizar a maioria das estatais", "value": 1},
    ],
}

PLAN = "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_{uf}.zip"

# Platform rows from registered plans: (candidateId, questionId, position, pdf, page, quote, detail)
PLATFORM = [
    ("presidente-22", "q3-fim-reeleicao", 1, "2026BR280002551544_01.pdf", 66, "E propomos o fim da reeleição para o cargo de Presidente da República.",
     "O plano de governo registrado no TSE propõe o fim da reeleição para presidente (p. 66)."),
    ("presidente-70", "q3-fim-reeleicao", 1, "2026BR280002551547_01.pdf", 155, "Sou contra a reeleição, pois considero que ela seja uma das fontes da corrupção.",
     "O plano de governo registrado no TSE se declara contra a reeleição (p. 155)."),
    ("presidente-55", "q3-fim-reeleicao", 1, "2026BR280002551932_01.pdf", 8, "Encaminhar ao Congresso, no início do mandato, proposta de emenda à Constituição para extinguir a reeleição consecutiva para os cargos do Poder Executivo",
     "O plano de governo registrado no TSE propõe uma PEC para extinguir a reeleição no Executivo (p. 8)."),
    ("presidente-22", "q3-civico-militar", 1, "2026BR280002551544_01.pdf", 35, "Vamos ampliar as Escolas Cívico-Militares",
     "O plano de governo registrado no TSE propõe ampliar as escolas cívico-militares (p. 35)."),
    ("presidente-30", "q3-civico-militar", 1, "2026BR280002539826_01.pdf", 53, "avançando em uma agenda de parcerias com escolas conveniadas na educação, escolas cívico-militares",
     "O plano de governo registrado no TSE inclui as escolas cívico-militares na agenda de parcerias da educação (p. 53)."),
    ("presidente-21", "q3-civico-militar", -1, "2026BR280002551975_01.pdf", 10, "Fim das escolas cívico-militares.",
     "O plano de governo registrado no TSE propõe o fim das escolas cívico-militares (p. 10)."),
    ("presidente-21", "q3-maconha-uso", 1, "2026BR280002551975_01.pdf", 12, "Descriminalização do uso de drogas, com legalização da maconha a curto prazo.",
     "O plano de governo registrado no TSE propõe descriminalizar o uso de drogas e legalizar a maconha (p. 12)."),
    ("presidente-16", "q3-maconha-uso", 1, "2026BR280002541457_01.pdf", 19, "Descriminalização das drogas e revogação da Lei Antidrogas",
     "O plano de governo registrado no TSE propõe descriminalizar as drogas (p. 19)."),
    ("presidente-80", "q3-grandes-fortunas", 1, "2026BR280002538811_01.pdf", 16, "IMPOSTO SOBRE AS GRANDES FORTUNAS E PROGRESSIVO.",
     "O plano de governo registrado no TSE propõe imposto progressivo sobre grandes fortunas (p. 16)."),
    ("presidente-16", "q3-grandes-fortunas", 1, "2026BR280002541457_01.pdf", 27, "Imposto progressivo sobre as verdadeiras grandes fortunas",
     "O plano de governo registrado no TSE propõe imposto progressivo sobre grandes fortunas (p. 27)."),
    ("presidente-21", "q3-grandes-fortunas", 1, "2026BR280002551975_01.pdf", 14, "criação de um imposto especial sobre lucros e dividendos, grandes fortunas, transações financeiras e heranças",
     "O plano de governo registrado no TSE propõe imposto sobre grandes fortunas (p. 14)."),
    ("presidente-29", "q3-grandes-fortunas", 1, "2026BR280002552487_01.pdf", 3, "Imposto sobre as grandes fortunas para garantir os recursos necessários para as aposentadorias e pensões",
     "O plano de governo registrado no TSE propõe imposto sobre grandes fortunas (p. 3)."),
    ("presidente-16", "q3-tarifa-zero", 1, "2026BR280002541457_01.pdf", 14, "Tarifa zero no transporte público",
     "O plano de governo registrado no TSE propõe tarifa zero no transporte público (p. 14)."),
    ("presidente-21", "q3-tarifa-zero", 1, "2026BR280002551975_01.pdf", 11, "de forma a garantir a tarifa zero para toda a população",
     "O plano de governo registrado no TSE propõe tarifa zero para toda a população (p. 11)."),
    ("governador-11", "q3-tarifa-zero", 0, "2026PB150002551789_01.pdf", 12, "Criação do Passe Livre Univer- sitário, estendendo aos estudan- tes do ensino superior o benefício de transporte público gratuito.",
     "O plano de governo registrado no TSE propõe passe livre para estudantes universitários, sem tarifa zero geral (p. 12)."),
    ("governador-15", "q3-tarifa-zero", 0, "2026PB150002544133_01.pdf", 75, "Garantir Passe Livre Estudantil para estudantes da Rede Pública.",
     "O plano de governo registrado no TSE propõe passe livre para estudantes da rede pública, sem tarifa zero geral (p. 75)."),
    ("presidente-13", "q3-redes-sociais", 1, "2026BR280002542548_01.pdf", 16, "avançar ainda mais na regulação democrática das redes sociais e das plataformas digitais, de modo a impedir que elas difundam desinformação",
     "O plano de governo registrado no TSE defende regular redes sociais e plataformas para impedir a difusão de desinformação (p. 16)."),
    ("presidente-21", "q3-redes-sociais", 1, "2026BR280002551975_01.pdf", 13, "Defendemos a forte regulação das Big Techs e redes sociais",
     "O plano de governo registrado no TSE defende forte regulação das big techs e redes sociais (p. 13)."),
    ("presidente-70", "q3-redes-sociais", 0, "2026BR280002551547_01.pdf", 91, "estimularemos maior transparência e responsabilidade das plataformas digitais em relação a conteúdos potencialmente prejudiciais a crianças e adolescentes, dentro dos parâmetros constitucionais e legais",
     "O plano de governo registrado no TSE propõe mais responsabilidade das plataformas só para conteúdo prejudicial a crianças e adolescentes (p. 91)."),
    ("presidente-13", "q3-pec-seguranca", 1, "2026BR280002542548_01.pdf", 30, "Uma vez aprovada a PEC da Segurança Pública proposta pelo Executivo, criaremos o Ministério da Segurança Pública",
     "O plano de governo registrado no TSE defende a PEC da Segurança Pública proposta pelo governo (p. 30)."),
]

# Executive act: (candidateId, questionId, position, source, date, detail, phrases)
EXECUTIVE = [
    ("presidente-13", "q3-civico-militar", -1, D1, "2023-07-19",
     "O governo Lula revogou o Programa Nacional das Escolas Cívico-Militares pelo Decreto 11.611/2023, assinado pelo vice-presidente Geraldo Alckmin no exercício da Presidência.",
     ["DECRETO Nº 11.611, DE 19 DE JULHO DE 2023", "que institui o Programa Nacional das Escolas Cívico-Militares", "O VICE-PRESIDENTE DA REPÚBLICA , no exercício do cargo de Presidente da República"]),
]

# Roll calls: (questionId, house, id_or_tuple, label, sign, lowDiscrimination)
# sign maps Sim -> position: +1 when Sim agrees with the statement, -1 when Sim disagrees.
CAMARA = [
    ("q3-redes-sociais", "2310837-8", "requerimento de urgência do PL 2.630/2020 (PL das Fake News) na Câmara", 1, False),
    ("q3-pec-seguranca", "2500080-320", "PEC 18/2025 (PEC da Segurança Pública), 1º turno na Câmara", 1, True),
]
SENADO = [
    ("q3-redes-sociais", ("PL", 2630, 2020), 6147, "PL 2.630/2020 (PL das Fake News), substitutivo no Senado", 1),
    ("q3-maconha-uso", ("PEC", 45, 2023), 6824, "PEC 45/2023 (criminalização da posse e do porte de drogas), 1º turno no Senado", -1),
]
