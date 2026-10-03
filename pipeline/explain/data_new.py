"""Explainer for the 6x1 work-schedule question."""

SOURCES = {
    "6x1-plen": ("https://www.camara.leg.br/noticias/1277141-camara-aprova-em-dois-turnos-fim-da-escala-6x1-com-jornada-maxima-de-40-horas-semanais/",
                 "Agência Câmara, 27/05/2026"),
    "6x1-com": ("https://www.camara.leg.br/noticias/1277012-comissao-aprova-o-fim-da-escala-6x1-e-reducao-da-jornada-de-44-para-40-horas-semanais/",
                "Agência Câmara, 27/05/2026"),
}

EXPLAINERS = {
    "eco-6x1": {
        "whatItIs": [
            ("Na escala 6x1 a pessoa trabalha seis dias e descansa um, com até 44 horas por semana. A PEC 221/2019, aprovada na Câmara em 2026, fixa 40 horas em cinco dias, com dois de descanso.",
             "estabelece jornada de trabalho de 40 horas semanais em cinco dias com dois de descanso, acabando com a escala 6 X 1 (um dia de descanso e 44 horas semanais).", "6x1-plen"),
            ("O texto garante que a redução vale sem corte de salário, inclusive nos pisos salariais.",
             "A PEC garante que as 8 horas diárias e 40 horas semanais com dois dias de descanso serão aplicadas aos contratos de trabalho em vigor sem qualquer redução salarial", "6x1-plen"),
        ],
        "inPractice": [
            ("A mudança é gradual: dois meses depois de promulgada, a jornada cai para 42 horas com dois dias de folga; 14 meses depois, chega a 40 horas.",
             "Em um ano depois do fim desses dois meses, portanto 14 meses depois da promulgação, a jornada será de 40 horas por semana.", "6x1-plen"),
            ("Há exceções: quem tem diploma superior e ganha mais de 2,5 vezes o teto do INSS pode ficar fora do controle de jornada, e micro e pequenas empresas terão regras de transição em lei complementar.",
             "incorporou dispositivo para remeter a uma lei complementar a definição de regras transitórias para diminuir o impacto da mudança em microempreendedores individuais (MEIs), microempresas e empresas de pequeno porte.", "6x1-plen"),
            ("Escalas especiais, como 12x36 e atividades de saúde, segurança e transporte, podem compensar folgas dentro do mês por acordo coletivo.",
             "convenções ou acordos coletivos de trabalho poderão, excepcionalmente, prever um regime de compensação a fim de assegurar, na média, dois dias de repouso semanal remunerado dentro do mês-calendário.", "6x1-plen"),
        ],
        "argsFor": [
            ("O relator, deputado Leo Prates (Republicanos-BA), defendeu a mudança como forma de dar a pais e mães mais tempo com os filhos.",
             "dando a mães e pais a oportunidade de serem os melhores que eles podem ser, para, sobretudo, que as crianças possam ter seus pais e suas mães", "6x1-com"),
            ("A deputada Erika Hilton (Psol-SP), autora de uma das PECs, disse que a mudança responde a uma jornada exaustiva e garante descanso e tempo para a vida pessoal.",
             "Autora de uma das PECs, a deputada Erika Hilton disse que a aprovação é uma resposta a uma jornada exaustiva e garante dignidade, descanso e mais tempo para a vida pessoal.", "6x1-com"),
        ],
        "argsAgainst": [
            ("A deputada Julia Zanatta (PL-SC) argumentou que o custo maior da mão de obra pode recair sobre os próprios trabalhadores.",
             "A deputada Julia Zanatta (PL-SC) argumentou que a redução das jornadas pode aumentar custos e defendeu mais liberdade econômica para empresas e trabalhadores.", "6x1-com"),
            ("O líder do Novo, Gilson Marques (SC), propôs livre negociação no lugar de um teto fixo e disse que o custo extra acaba repassado aos preços.",
             "Para Marques, a redução obrigatória gera aumento de custos operacionais que acabam sendo repassados aos preços dos produtos, prejudicando o próprio trabalhador no momento da compra.", "6x1-com"),
        ],
        "nuance": [
            ("A divisão não segue esquerda e direita: o líder do PL, Sóstenes Cavalcante, defendeu ir além e adotar a escala 4x3 de forma imediata.",
             "afirmou que o partido vai defender, no plenário da Casa, uma mudança ainda mais profunda: a jornada de quatro dias trabalhados por três de descanso (escala 4x3).", "6x1-com"),
            ("A votação na Câmara foi quase unânime (461 a 19 no 2º turno). A disputa real é sobre o ritmo da transição e as exceções.",
             "A PEC 221/19 foi aprovada em 2º turno com 461 votos a favor e 19 contra .", "6x1-plen"),
        ],
    },
}

TOPICS = {"eco-6x1": ["6x1", "jornada", "escala"]}

_E = "Convenção de método, não fato: no eixo econômico, concordar aponta para "
_S = "Convenção de método, não fato: no eixo de costumes, concordar aponta para "
AXES = [
    {"questionId": "eco-privatizacao", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque transfere empresas do Estado para acionistas privados."},
    {"questionId": "eco-bc-autonomo", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque reduz o controle do governo eleito sobre a política de juros."},
    {"questionId": "eco-ir-alta-renda", "axis": "economico", "direction": -1, "rationale": _E + "mais Estado, porque aumenta a tributação de altas rendas para redistribuir."},
    {"questionId": "eco-6x1", "axis": "economico", "direction": -1, "rationale": _E + "mais Estado, porque amplia a regulação do contrato de trabalho por norma constitucional."},
    {"questionId": "amb-licenciamento", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque reduz exigências prévias do Estado sobre empreendimentos."},
    {"questionId": "amb-agrotoxicos", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque acelera e simplifica a liberação de produtos pelo Estado."},
    {"questionId": "pb-concessoes-ppp", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque passa a operação de serviços públicos a empresas privadas."},
    {"questionId": "pb-ppp-cagepa", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque mantém um serviço público operado por empresa privada."},
    {"questionId": "pb-vale-saude", "axis": "economico", "direction": 1, "rationale": _E + "mais mercado, porque leva dinheiro público da saúde para a rede privada por escolha do paciente."},
    {"questionId": "pb-empresas-publicas", "axis": "economico", "direction": -1, "rationale": _E + "mais Estado, porque cria empresas controladas pelo governo."},
    {"questionId": "seg-saidinha", "axis": "social", "direction": 1, "rationale": _S + "conservador, na convenção usual que associa punição mais dura a ordem e tradição."},
    {"questionId": "seg-drogas", "axis": "social", "direction": 1, "rationale": _S + "conservador, porque mantém a criminalização de uma conduta individual."},
    {"questionId": "seg-armas", "axis": "social", "direction": 1, "rationale": _S + "conservador, na convenção usada no debate brasileiro, embora defensores também invoquem liberdade individual."},
    {"questionId": "seg-maioridade", "axis": "social", "direction": 1, "rationale": _S + "conservador, na convenção usual que associa punição mais dura a ordem."},
    {"questionId": "soc-marco-temporal", "axis": "social", "direction": 1, "rationale": _S + "conservador, na convenção usual que associa direitos territoriais indígenas ao campo progressista."},
    {"questionId": "soc-aborto", "axis": "social", "direction": -1, "rationale": _S + "progressista, porque amplia a autonomia individual sobre um tema moral."},
    {"questionId": "soc-cotas", "axis": "social", "direction": -1, "rationale": _S + "progressista, porque mantém ação afirmativa racial e social."},
    {"questionId": "pb-desmilitarizar-pm", "axis": "social", "direction": -1, "rationale": _S + "progressista, na convenção usual que associa a estrutura militar da polícia ao campo da ordem."},
    {"questionId": "pb-cac-arma", "axis": "social", "direction": 1, "rationale": _S + "conservador, na mesma convenção usada para acesso a armas."},
    {"questionId": "pb-nome-social", "axis": "social", "direction": -1, "rationale": _S + "progressista, porque amplia o reconhecimento da identidade de gênero."},
]
