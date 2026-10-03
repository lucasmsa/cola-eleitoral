"""Explainers for the environment and energy questions."""

SOURCES = {
    "lic-senado": ("https://www12.senado.leg.br/noticias/materias/2025/05/21/senado-aprova-projeto-da-lei-do-licenciamento-ambiental",
                   "Agência Senado, 21/05/2025"),
    "lic-veto": ("https://www12.senado.leg.br/noticias/materias/2025/11/27/congresso-derruba-52-itens-de-veto-a-lei-geral-do-licenciamento-ambiental",
                 "Agência Senado, 27/11/2025"),
    "mar-cma": ("https://www12.senado.leg.br/noticias/materias/2024/04/24/com-petrobras-e-ibama-cma-debate-exploracao-de-petroleo-na-margem-equatorial",
                "Agência Senado, 24/04/2024"),
    "mar-davi": ("https://www12.senado.leg.br/noticias/materias/2025/10/20/davi-aplaude-decisao-do-ibama-de-liberar-pesquisa-de-petroleo-na-margem-equatorial",
                 "Agência Senado, 20/10/2025"),
    "mar-ongs": ("https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2025-10/ongs-acionam-justica-para-barrar-perfuracao-na-foz-do-amazonas",
                 "Agência Brasil, 22/10/2025"),
    "mar-2026": ("https://agenciabrasil.ebc.com.br/economia/noticia/2026-10/nova-descoberta-aumenta-expectativa-da-petrobras-na-foz-do-amazonas",
                 "Agência Brasil, 02/10/2026"),
    "mar-camara": ("https://www.camara.leg.br/noticias/968988-deputados-debatem-exploracao-de-petroleo-na-bacia-da-foz-do-rio-amazonas/",
                   "Agência Câmara, 2023"),
    "mar-cme": ("https://www.camara.leg.br/noticias/1113628-comissao-debate-exploracao-de-petroleo-na-foz-do",
                "Agência Câmara, 2024"),
    "agr-senado": ("https://www12.senado.leg.br/noticias/materias/2023/11/28/senado-aprova-projeto-que-facilita-registro-de-agrotoxicos",
                   "Agência Senado, 28/11/2023"),
    "agr-sancao": ("https://www.camara.leg.br/noticias/1029773-LULA-SANCIONA-COM-VETOS-PROJETO-QUE-ALTERA-REGRAS-DE-REGISTRO-DE-AGROTOXICOS",
                   "Agência Câmara, 2023"),
    "agr-veto": ("https://www12.senado.leg.br/noticias/materias/2024/05/09/registro-de-pesticidas-cabera-apenas-ao-ministerio-da-agricultura",
                 "Agência Senado, 09/05/2024"),
}

EXPLAINERS = {
    "amb-licenciamento": {
        "whatItIs": [
            ("Licenciamento ambiental é a autorização do poder público para instalar ou ampliar obras que usam recursos naturais ou podem causar impacto, como rodovias, hidrelétricas, indústrias e loteamentos.",
             "É pelo licenciamento ambiental que o poder público autoriza a instalação, a ampliação e a operação de empreendimentos que utilizam recursos naturais ou podem causar impacto ao meio ambiente.", "lic-senado"),
            ("A Lei Geral do Licenciamento (Lei 15.190/2025) criou a LAC, Licença por Adesão e Compromisso: o empreendedor faz uma espécie de autodeclaração em vez de passar por todas as etapas de análise.",
             "a Licença Ambiental por Adesão e Compromisso (LAC) será simplificada e expedida mediante uma espécie de autodeclaração de adesão e compromisso do empreendedor", "lic-senado"),
        ],
        "inPractice": [
            ("A LAC vale para obras de pequeno ou médio porte e baixo ou médio potencial poluidor. Não pode ser usada se houver desmatamento de vegetação nativa.",
             "A licença não será autorizada se houver desmatamento de vegetação nativa, já que nesse caso há necessidade de autorização específica.", "lic-senado"),
            ("Entre os vetos presidenciais derrubados pelo Congresso em 2025 está o trecho que torna apenas opinativas as manifestações da Funai, da Fundação Palmares e dos órgãos de unidades de conservação.",
             "tornar opinativa as decisões da Funai (indígenas), Fundação Palmares (quilombolas) e dos órgãos gestores de unidades de conservação da natureza", "lic-veto"),
        ],
        "argsFor": [
            ("A relatora, senadora Tereza Cristina, disse que a legislação atual é \"um verdadeiro cipoal\" de cerca de 27 mil normas.",
             "Segundo a relatora de Plenário, senadora Tereza Cristina (PP-MS), a legislação atual configura um verdadeiro cipoal com cerca de 27 mil normativos.", "lic-senado"),
            ("O senador Marcos Rogério defendeu a lei como \"equilibrada\" e disse que o que trava o país são interpretações e regras do Conama.",
             "Essa Lei do Licenciamento Ambiental aprovada pelo Congresso Nacional é uma lei equilibrada, é uma lei que respeita a sustentabilidade no Brasil.", "lic-veto"),
        ],
        "argsAgainst": [
            ("A senadora Eliziane Gama chamou a lei de \"retrocesso\" e disse que ela fere a proteção da Mata Atlântica.",
             "A senadora Eliziane Gama (PSD-MA) afirmou na tribuna que a aprovação da Lei do Licenciamento Ambiental \"é um retrocesso e uma vergonha para o Brasil\"", "lic-veto"),
            ("O líder do governo no Congresso, Randolfe Rodrigues, defendeu manter os vetos porque vários trechos seriam inconstitucionais, como os que atingem a Mata Atlântica.",
             "Ele lembrou que muitos dos itens vetados são temas inconstitucionais, como os que atingem a Mata Atlântica, protegida pela Constituição.", "lic-veto"),
        ],
        "nuance": [
            ("O próprio governo apoiou partes da simplificação: emendas de senadores do PT limitaram a LAC a obras menores em vez de derrubá-la.",
             "No Senado, foram acatadas parcialmente emendas dos senadores Jaques Wagner (PT-BA), Randolfe Rodrigues (PT-AP) e Eliziane Gama (PSD-MA) para prever que a LAC só será permitida para empreendimentos considerados de pequeno ou médio porte e baixo ou médio potencial poluidor", "lic-senado"),
            ("A lei também aumentou a pena para quem constrói sem licença: de um a seis meses passou para seis meses a dois anos.",
             "No Senado, a pena mudou para seis meses a dois anos.", "lic-senado"),
        ],
    },
    "amb-margem-equatorial": {
        "whatItIs": [
            ("A Margem Equatorial é uma faixa do mar que vai do Rio Grande do Norte ao Amapá e inclui a bacia da foz do rio Amazonas. É apontada como um possível \"novo pré-sal\".",
             "Apontado por especialistas como um possível “novo pré-sal”, a região abrange uma área com mais de 2.200 quilômetros de litoral que vai do Rio Grande do Norte ao Amapá e inclui as bacias hidrográficas da foz do rio Amazonas.", "mar-cma"),
            ("O Ibama autorizou a Petrobras a perfurar na bacia da Foz do Amazonas em outubro de 2025.",
             "A Petrobras obteve autorização para perfurar áreas na Foz do Amazonas em outubro de 2025 .", "mar-2026"),
        ],
        "inPractice": [
            ("A Petrobras anunciou descobertas de petróleo no poço Morpho, a 175 km da costa do Amapá, mas ainda sem confirmação de valor comercial.",
             "Não sabemos se vamos ter uma descoberta com valor comercial, mas tudo indica que sim", "mar-2026"),
            ("Estudo da Empresa de Pesquisa Energética estima até 10 bilhões de barris recuperáveis na bacia da Foz do Amazonas.",
             "estima que o volume potencial total recuperável da Bacia da Foz do Amazonas pode chegar a 10 bilhões de barris de óleo equivalente", "mar-2026"),
        ],
        "argsFor": [
            ("O presidente do Senado, Davi Alcolumbre (AP), disse que a exploração mostra que é possível conciliar crescimento e preservação e fortalece a \"soberania energética\".",
             "A autorização do Ibama reafirma que é possível conciliar crescimento econômico e preservação ambiental, garantindo que os benefícios dessa atividade cheguem às populações locais e fortaleçam a soberania energética nacional.", "mar-davi"),
            ("A deputada Silvia Waiãpi (PL-AP) argumentou que os estados do Norte têm baixo IDH e pouco saneamento e que o petróleo pode reverter isso a médio prazo.",
             "\"Os estados do Norte sofrem com baixo Índice de Desenvolvimento Humano, baixa cobertura de saneamento básico e toda a sorte de problemas que no médio/longo prazo a exploração daquele petróleo podem reverter\"", "mar-cme"),
        ],
        "argsAgainst": [
            ("Suely Araújo, do Observatório do Clima, disse que a licença foi dada \"de forma inconsequente\" e põe em risco o legado climático do país.",
             "liberou-se a perfuração de forma inconsequente”, disse Suely Araújo, coordenadora de Políticas Públicas do Observatório do Clima.", "mar-ongs"),
            ("Kleber Karipuna, da Apib, chamou o projeto de \"predatório\" e disse que ignora a voz dos povos indígenas.",
             "“Este projeto é predatório, ignora a voz dos povos indígenas, verdadeiros guardiões da floresta", "mar-ongs"),
        ],
        "nuance": [
            ("O debate mistura risco local e clima global: as ONGs dizem que até 20% do óleo de um vazamento grave poderia atingir o sistema de recifes da foz do Amazonas.",
             "em caso de acidente grave, até 20% do óleo derramado poderia atingir o Grande Sistema Recifal Amazônico", "mar-ongs"),
            ("O Ibama afirma que a licença saiu depois de estudo de impacto, três audiências públicas e 65 reuniões técnicas em mais de 20 municípios.",
             "com a realização de três audiências públicas, 65 reuniões técnicas setoriais em mais de 20 municípios dos estados do Pará e do Amapá", "mar-ongs"),
        ],
    },
    "amb-agrotoxicos": {
        "whatItIs": [
            ("A nova Lei dos Agrotóxicos (Lei 14.785/2023) concentrou no Ministério da Agricultura a liberação desses produtos. Antes, Agricultura, Meio Ambiente (Ibama) e Saúde (Anvisa) decidiam juntos.",
             "Atualmente, há um sistema tripartite de decisão, que congrega a pasta da Agricultura, o Ministério do Meio Ambiente, por meio do Ibama, e o Ministério da Saúde, representado pela Anvisa.", "agr-senado"),
            ("A lei fixa prazos para o registro, de 30 dias a 2 anos, e permite registro temporário de produtos já usados em pelo menos três países da OCDE quando o prazo vence.",
             "Isso acontecerá desde que estejam registrados para culturas similares ou usos ambientais similares em pelo menos três países membros da Organização para Cooperação e Desenvolvimento Econômico (OCDE).", "agr-senado"),
        ],
        "inPractice": [
            ("A lei antiga proibia expressamente produtos cancerígenos ou que causam mutações e deformações. A nova proíbe os que apresentem \"risco\", avaliado pelo Ministério da Agricultura.",
             "O projeto apenas define como proibido o registro de pesticidas, de produtos de controle ambiental e afins que apresentem risco para os seres humanos ou meio ambiente.", "agr-senado"),
            ("Mesmo com a centralização, se a Anvisa não aprovar um produto, o ministério precisa acatar a decisão.",
             "Apesar de concentrar a liberação sobre os agrotóxicos no Ministério da Agricultura, se o produto não for aprovado pela Anvisa, o ministério terá que acatar a decisão.", "agr-senado"),
        ],
        "argsFor": [
            ("O senador Luis Carlos Heinze disse que o Brasil leva em média sete anos para liberar novos produtos, o que na Europa leva poucos meses.",
             "Heinze afirmou que, atualmente, o Brasil demora em média sete anos para liberar novos produtos, o que é feito em poucos meses em países europeus.", "agr-senado"),
            ("A senadora Tereza Cristina, ex-ministra da Agricultura, disse que a mudança permite modernizar os defensivos agrícolas com rigor técnico.",
             "Tereza Cristina disse que a aprovação vai permitir a modernização dos defensivos agrícolas no Brasil.", "agr-senado"),
        ],
        "argsAgainst": [
            ("Ao vetar trechos, o Planalto argumentou que tirar o Ibama e a Anvisa da reanálise acabaria com o modelo tripartite ligado aos direitos à vida, à saúde e ao meio ambiente.",
             "garantindo a manutenção do modelo tripartite, diretamente associado aos direitos à vida, à saúde e ao meio ambiente ecologicamente equilibrado previstos na Constituição Federal", "agr-sancao"),
            ("A Presidência da República também alegou que permitir registro de produto em reanálise ofende o princípio da precaução. O Congresso derrubou esse veto em 2024.",
             "O governo alega que esse dispositivo ofende o princípio da precaução, colocando em risco os direitos à vida, à saúde e ao meio ambiente ecologicamente equilibrado.", "agr-veto"),
        ],
        "nuance": [
            ("O Brasil é o maior consumidor de agrotóxicos do mundo. Antes da nova lei, entre 2019 e 2022, foram liberados 2.181 novos registros.",
             "O Brasil é o maior consumidor de agrotóxicos do mundo. Entre 2019 e 2022, foram liberados 2.181 novos registros", "agr-sancao"),
            ("No Senado, a votação foi simbólica, e só a senadora Zenaide Maia registrou voto contrário.",
             "A senadora Zenaide Maia (PSD-RN) foi a única a registrar voto contrário ao projeto.", "agr-senado"),
        ],
    },
}

TOPICS = {
    "amb-licenciamento": ["licenciamento", "licença"],
    "amb-margem-equatorial": ["Margem Equatorial", "Foz do Amazonas", "petróleo"],
    "amb-agrotoxicos": ["agrotóxico", "pesticida", "defensivo"],
}
