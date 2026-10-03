"""Explainers for the social questions."""

SOURCES = {
    "mt-pec": ("https://www12.senado.leg.br/noticias/materias/2025/12/09/aprovada-em-dois-turnos-pec-do-marco-temporal-vai-a-camara",
               "Agência Senado, 09/12/2025"),
    "mt-impasse": ("https://www12.senado.leg.br/noticias/materias/2023/09/21/terras-indigenas-marco-temporal-cria-impasse-entre-congresso-e-stf",
                   "Agência Senado, 21/09/2023"),
    "ab-cp": ("https://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm",
              "Código Penal (Decreto-Lei 2.848/1940), Planalto"),
    "ab-weber": ("https://noticias.stf.jus.br/postsnoticias/relatora-vota-pela-descriminalizacao-do-aborto-ate-12-semanas-de-gestacao-julgamento-e-suspenso/",
                 "STF, notícia de 22/09/2023"),
    "ab-barroso": ("https://noticias.stf.jus.br/postsnoticias/ministro-barroso-vota-pela-descriminalizacao-do-aborto-ate-12-semanas-de-gestacao/",
                   "STF, notícia de 17/10/2025"),
    "ab-camara": ("https://www.camara.leg.br/noticias/539309-deputados-defendem-que-congresso-e-nao-stf-decida-sobre-descriminalizacao-do-aborto-no-brasil/",
                  "Agência Câmara, 2018"),
    "ab-girao": ("https://www12.senado.leg.br/noticias/materias/2025/10/22/girao-voto-de-barroso-sobre-aborto-foi-atitude-covarde-e-sera-questionado",
                 "Agência Senado, 22/10/2025"),
    "co-camara": ("https://www.camara.leg.br/noticias/984747-camara-aprova-projeto-que-reformula-politica-de-cotas-nas-universidades-federais/",
                  "Agência Câmara, 09/08/2023"),
    "co-senado": ("https://www12.senado.leg.br/noticias/materias/2023/10/24/senado-aprova-atualizacao-da-lei-de-cotas",
                  "Agência Senado, 24/10/2023"),
}

EXPLAINERS = {
    "soc-marco-temporal": {
        "whatItIs": [
            ("Marco temporal é a tese de que só podem ser demarcadas como terra indígena as áreas ocupadas por indígenas em 5 de outubro de 1988, data da Constituição.",
             "determinando que somente poderão ser demarcadas as terras que estavam sob a posse dos indígenas na data da promulgação da Constituição, em 5 de outubro de 1988.", "mt-pec"),
            ("Em 2023 o STF decidiu contra a tese, mas o Congresso aprovou uma lei com ela (Lei 14.701/2023) e derrubou o veto do governo.",
             "No mesmo mês, o Supremo Tribunal Federal (STF) decidiu contra a tese, e o governo vetou o trecho da lei que instituía o marco temporal. O veto, no entanto, foi derrubado pelo Congresso Nacional logo depois.", "mt-pec"),
        ],
        "inPractice": [
            ("Em dezembro de 2025 o Senado aprovou a PEC 48/2023, que põe o marco temporal na própria Constituição. O texto foi para a Câmara.",
             "Aprovada em dois turnos, a proposta segue para a Câmara dos Deputados.", "mt-pec"),
            ("A PEC também prevê indenização prévia aos ocupantes regulares de terras que forem demarcadas.",
             "acrescentou dispositivos que garantem prévia indenização aos ocupantes regulares de terras que serão demarcadas.", "mt-pec"),
            ("Em 2025, o ministro Gilmar Mendes suspendeu as ações sobre o tema no STF e criou um grupo de conciliação com Executivo e Legislativo.",
             "Em abril de 2025, o ministro Gilmar Mendes estabeleceu a suspensão das ações que tratam da questão no Supremo, até que haja uma decisão final dos ministros.", "mt-pec"),
        ],
        "argsFor": [
            ("O senador Zequinha Marinho defendeu o marco como segurança jurídica para produtores rurais e lembrou que 14,1% do território já é terra indígena demarcada.",
             "Zequinha Marinho apoiou a aprovação do projeto do marco temporal como garantia de segurança jurídica para todos os produtores rurais.", "mt-impasse"),
            ("O relator, senador Esperidião Amin, argumentou que desde 1934 as Constituições garantem aos indígenas a terra \"em que eles se encontram\".",
             "Ao apresentar seu relatório, Amin lembrou que, desde 1934, todas as Constituições reconheceram implicitamente o princípio do marco temporal", "mt-pec"),
        ],
        "argsAgainst": [
            ("O senador Humberto Costa disse que o projeto tem \"vícios de constitucionalidade\" e, na prática, inviabiliza a demarcação de novos territórios indígenas.",
             "Humberto Costa avaliou o projeto como “cheio de vícios de constitucionalidade” e disse que, na prática, vai inviabilizar a demarcação de novos territórios indígenas.", "mt-impasse"),
            ("O senador Jaques Wagner disse que o marco temporal não resolve o problema e põe os indígenas em desvantagem; para ele, a culpa é do Estado, que não demarcou no prazo.",
             "Para ele, o marco temporal não resolve o problema e põe os indígenas em desvantagem na regularização de terras.", "mt-pec"),
        ],
        "nuance": [
            ("Os dois lados falam em \"insegurança jurídica\". O líder do governo admitiu que ela é \"insuportável\" e pediu acordo, e o STF mantém uma mesa de conciliação.",
             "o líder do governo no Senado, Jaques Wagner (PT-BA), apelou por um acordo, admitindo que a insegurança jurídica é “insuportável”.", "mt-pec"),
            ("Pela tese, não basta ocupar a área em 1988: também é preciso provar uso permanente e que a terra é necessária à reprodução física e cultural da comunidade.",
             "Também será preciso demonstrar que essas terras eram necessárias para a reprodução física e cultural dos indígenas", "mt-impasse"),
            ("Integrantes de grupos indígenas afirmam que a tese desconsidera povos nômades e comunidades expulsas de suas terras antes de 1988.",
             "Integrantes de grupos indígenas são contrários ao marco temporal e afirmam que a tese desconsidera, por exemplo, povos nômades e comunidades que foram expulsas de suas terras antes da promulgação da Constituição.", "mt-pec"),
        ],
    },
    "soc-aborto": {
        "whatItIs": [
            ("Hoje o aborto é crime no Brasil, com exceções. O Código Penal não pune o aborto feito por médico quando não há outro meio de salvar a vida da gestante ou quando a gravidez resulta de estupro.",
             "Art. 128 - Não se pune o aborto praticado por médico:", "ab-cp"),
            ("Em 2012, no julgamento da ADPF 54, o STF também permitiu interromper a gravidez de feto anencéfalo, ou seja, sem formação do cérebro.",
             "quanto no da interrupção da gravidez de feto anencéfalo (ADPF 54)", "ab-weber"),
            ("A ADPF 442, ação do Psol, pede ao STF que o aborto deixe de ser crime até a 12ª semana. Os ministros Rosa Weber e Luís Roberto Barroso votaram a favor, e o julgamento está suspenso.",
             "O julgamento da Arguição de Descumprimento de Preceito Fundamental (ADPF) 442 estava suspenso por pedido de destaque de Barroso em sessão virtual após o voto da relatora, ministra Rosa Weber (aposentada), em setembro de 2023.", "ab-barroso"),
        ],
        "inPractice": [
            ("Pelo Código Penal, a gestante que provoca o aborto ou autoriza alguém a fazê-lo pode ser punida com detenção de um a quatro anos.",
             "é desproporcional atribuir pena de detenção de um a quatro anos para a gestante, caso provoque o aborto por conta própria ou autorize alguém a fazê-lo", "ab-weber"),
            ("Descriminalizar não é o mesmo que obrigar alguém a fazer aborto: a proposta tira a punição criminal nas 12 primeiras semanas. Barroso defendeu tratar o tema como saúde pública.",
             "“A interrupção da gestação deve ser tratada como uma questão de saúde pública, não de direito penal”, afirmou.", "ab-barroso"),
        ],
        "argsFor": [
            ("O ministro Luís Roberto Barroso argumentou que a criminalização atinge sobretudo mulheres pobres, enquanto as ricas podem abortar fora do país.",
             "Mas, na sua avaliação, a criminalização penaliza especialmente meninas e mulheres pobres, que não podem recorrer ao sistema público de saúde para obter informações, medicação ou procedimentos adequados.", "ab-barroso"),
            ("A ministra Rosa Weber argumentou que proibir totalmente o aborto com base no direito à vida desde a concepção \"não encontra suporte jurídico\" na Constituição.",
             "Para Rosa Weber, o argumento do direito à vida desde a concepção como fundamento para a proibição total da interrupção da gestação, como defendem alguns setores, “não encontra suporte jurídico no desenho constitucional brasileiro”.", "ab-weber"),
        ],
        "argsAgainst": [
            ("A advogada Angela Vidal Gandra sustentou que não existe direito constitucional ao aborto e que a vida do feto se sobrepõe à escolha da mulher.",
             "Ela avaliou ainda que o direito da vida do feto se sobrepõe ao direito de escolha da mulher.", "ab-camara"),
            ("O deputado Takayama, então presidente da Frente Parlamentar Evangélica, defendeu que, se a criança for indesejada, a mãe a entregue para adoção.",
             "Na visão do presidente da Frente Parlamentar Evangélica, o deputado Takayama (PSC-PR), se a criança for indesejada, a mãe deve entregá-la à adoção.", "ab-camara"),
        ],
        "nuance": [
            ("Parte do debate não é sobre o aborto em si, mas sobre quem decide: deputados como Diego Garcia defendem que só o Congresso pode mudar a lei, não o STF.",
             "Estão tentando, por meio de medida judicial, tirar prerrogativas do Parlamento", "ab-camara"),
            ("Discordar da frase não significa querer acabar com os casos de aborto legal que já existem. Concordar não significa defender aborto depois de 12 semanas.",
             "A pretensão do partido é que seja permitida a interrupção da gravidez nas primeiras 12 semanas de gestação.", "ab-camara"),
        ],
    },
    "soc-cotas": {
        "whatItIs": [
            ("A Lei de Cotas (Lei 12.711/2012) reserva pelo menos metade das vagas de universidades e institutos federais para quem estudou todo o ensino médio em escola pública.",
             "que reserva no mínimo 50% das vagas em universidades e institutos federais para pessoas que estudaram todo o ensino médio em escolas públicas.", "co-senado"),
            ("A parte racial fica dentro dessa metade: um aluno negro que estudou em escola particular, por exemplo, não entra pela cota.",
             "um aluno negro que estudou o ensino médio em escola particular, por exemplo, não é beneficiado.", "co-senado"),
        ],
        "inPractice": [
            ("A revisão de 2023 reduziu o limite de renda para metade das vagas de 1,5 para 1 salário mínimo por pessoa e incluiu quilombolas.",
             "Pela proposta aprovada, a renda familiar máxima será de 1 salário mínimo (que hoje corresponde a R$ 1.320) por pessoa.", "co-senado"),
            ("O cotista agora disputa primeiro as vagas gerais e só usa a cota se não alcançar a nota. A lei prevê avaliação a cada dez anos.",
             "Se o candidato não conseguir nota para aprovação nas vagas gerais, passará a concorrer às vagas reservadas.", "co-senado"),
        ],
        "argsFor": [
            ("O relator no Senado, Paulo Paim, disse que antes da lei as universidades tinham 6% de pobres, indígenas, pretos e pessoas com deficiência, e que depois passaram de 40%.",
             "Antes da Lei de Cotas, as universidades tinham apenas 6% de pobres, vulneráveis, indígenas, pretos e pessoas com deficiência. Depois que surgiram as cotas, somos mais de 40%.", "co-senado"),
            ("A relatora na Câmara, deputada Dandara, defendeu a política dizendo que ela própria foi cotista na graduação e na pós.",
             "\"Eu sou o resultado da política de cotas, tenho muito orgulho de ter sido cotista na graduação e na pós-graduação.", "co-camara"),
        ],
        "argsAgainst": [
            ("O senador Rogério Marinho defendeu cotas apenas sociais e econômicas, não raciais, dizendo que a lei \"divide o país\".",
             "Nós não somos aqui contra essa ou aquela raça, mas acreditamos que, se tem que haver políticas de cotas, que seja a política social e econômica, e não uma política racial", "co-senado"),
            ("O deputado Carlos Jordy (PL-RJ) afirmou que as cotas raciais nunca deram certo e ampliam a divisão entre grupos étnicos.",
             "Líder da oposição, o deputado Carlos Jordy (PL-RJ) afirmou que as cotas raciais nunca deram certo e ampliam a divisão entre grupos étnicos.", "co-camara"),
        ],
        "nuance": [
            ("A divisão principal não é entre ter ou não ter cotas, e sim entre cotas sociais (renda e escola pública) e cotas raciais. Uma emenda rejeitada no Senado mantinha 50% das vagas só por renda, sem reserva racial.",
             "A emenda estabelecia cotas nas instituições federais de ensino superior e técnico de nível médio apenas para estudantes oriundos de famílias com renda per capita igual ou inferior a 1,5 salário mínimo per capita", "co-senado"),
            ("O deputado Kim Kataguiri argumentou que o aluno mais pobre muitas vezes nem chega à cota, porque abandona o ensino médio para trabalhar.",
             "\"O aluno de baixa renda não tem acesso às cotas porque ele não termina o ensino médio, ele sai porque precisa trabalhar.\"", "co-camara"),
        ],
    },
}

TOPICS = {
    "soc-marco-temporal": ["marco temporal", "indígena"],
    "soc-aborto": ["aborto", "gestação", "gravidez"],
    "soc-cotas": ["cotas", "Cotas"],
}
