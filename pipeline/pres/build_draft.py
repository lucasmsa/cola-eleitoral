"""Builds pres/draft.jsonl from caption excerpts and Goiás law records. Quotes are sliced from the cached sources."""
import json, sys
sys.path.insert(0, 'platform'); from vtt import ts_at

META = {}
for line in open('pres/raw/yt/meta.txt', encoding='utf-8'):
    vid, up, ch, title = line.rstrip('\n').split('|', 3)
    META[vid] = dict(date=f'{up[:4]}-{up[4:6]}-{up[6:]}', channel=ch, title=title)

VIDEOS = [
 ('presidente-30', 'seg-8-janeiro', 1, 'oNntj0DU-OA', 'Zema', 'Eu darei anistia ou pelo menos', 'foi perseguição.',
  'Em entrevista publicada pelo g1, disse que dará anistia ou ao menos "um tribunal que não seja político" aos condenados pelo 8 de janeiro.'),
 ('presidente-30', 'eco-6x1', -1, 'qRA6U_rKmxk', 'Zema', 'E vem um governo populista falar', 'além da CLT que existe',
  'No Jornal da Record, chamou de populista a proposta de acabar com a escala 6x1 e defendeu contrato por hora fora da CLT.'),
 ('presidente-55', 'seg-8-janeiro', 1, '51g_wYigfag', 'Caiado', 'Eu estou dizendo que eu, presidente da República', 'eu assinarei o ato de anistia imediatamente.',
  'No Roda Viva (TV Cultura), disse que assinará a anistia aos condenados pelo 8 de janeiro como primeiro ato se eleito.'),
 ('presidente-55', 'seg-stf-mandato', 1, '51g_wYigfag', 'Caiado', 'Eu vejo que o mandato ele é muito mais', 'nós estamos vivendo no Brasil.',
  'No Roda Viva (TV Cultura), defendeu mandato com início e fim para ministros do STF.'),
 ('presidente-70', 'seg-8-janeiro', 1, 'A0pNnVo2T6k', 'Cury', 'as condenações foram realmente exageradas', 'Isso não houve.',
  'Na CNN, disse que as condenações do 8 de janeiro foram exageradas em muitos casos e que o golpe não se materializou.'),
 ('presidente-70', 'amb-margem-equatorial', 1, 'A0pNnVo2T6k', 'Cury', 'Para mim, a margem equatorial já deveria', 'estar sendo explorada.',
  'Na CNN, disse que a Margem Equatorial já deveria estar sendo explorada.'),
 ('presidente-70', 'eco-bc-autonomo', 1, 'A0pNnVo2T6k', 'Cury', 'o Banco Central tem que ser independente.', 'obviamente.',
  'Na CNN, disse que o Banco Central tem que ser independente.'),
 ('presidente-14', 'eco-privatizacao', -1, 'gV564Fj2Qv0', 'Renan', 'No mundo desses, ter e controlar suas próprias reservas', 'faz sentido',
  'Na Revista Oeste, ao dizer que discorda de privatizar a Petrobras, afirmou que faz sentido o país controlar suas reservas e o refino de petróleo.'),
 ('presidente-14', 'eco-reforma-tributaria', 0, 'gV564Fj2Qv0', 'Renan', 'O modelo que tem esse imposto estadual único', 'Eu reformaria ela para tirar essas deturpações',
  'Na Revista Oeste, disse que o modelo de imposto único da reforma tributária é bom, mas que reformaria a lei para tirar as exceções.'),
 ('presidente-27', 'soc-aborto', -1, 'KLZsdpn944A', 'Clariana', 'Eu defendo a manutenção das regras atuais.', 'eu sou contra o aborto',
  'No Poder360, defendeu manter as regras atuais sobre aborto e disse ser contra o aborto.'),
 ('presidente-27', 'seg-8-janeiro', 0, 'KLZsdpn944A', 'Clariana', 'eu não sou a favor da anistia, mas', 'envolvidas no 8 de janeiro.',
  'No Poder360, disse não ser a favor da anistia, mas que o STF exagerou nos processos do 8 de janeiro; propõe revisão criminal caso a caso.'),
 ('presidente-27', 'eco-privatizacao', 0, 'KLZsdpn944A', 'Clariana', 'eu sou a favor das privatizações, mas não de tudo.', 'da privatização da Petrobras.',
  'No Poder360, disse ser a favor de privatizações, com exceções como a Petrobras.'),
 ('presidente-35', 'seg-8-janeiro', 1, 'Slj2v0RahfU', 'Grassi', 'depender de mim, eu solto todo mundo.', 'eu solto todo mundo.',
  'No Metrópoles, sobre a anistia aos condenados do 8 de janeiro, disse que soltaria todos.'),
 ('presidente-35', 'seg-drogas', -1, 'dYffqonVmjQ', 'Grassi', 'Eu sou a favor da liberação dos de droga.', 'Eu sou a favor da liberação dos de droga.',
  'No Poder360, disse ser a favor da liberação das drogas.'),
 ('presidente-35', 'eco-6x1', -1, 'dYffqonVmjQ', 'Grassi', 'eu não entendo porque o governo tem que ser babá', 'relação entre adultos.',
  'No Poder360, sobre o fim da escala 6x1, disse que o governo não deve se meter na relação entre adultos.'),
 ('presidente-35', 'eco-bc-autonomo', 1, 'dYffqonVmjQ', 'Grassi', 'O Banco Central não só tem que ser autônomo', 'quanto ao real',
  'No Poder360, disse que o Banco Central tem que ser autônomo.'),
 ('presidente-35', 'seg-stf-mandato', 1, 'dYffqonVmjQ', 'Grassi', 'E vamos colocar mandato 2, 3 anos no máximo.', 'no máximo.',
  'No Poder360, propôs mandato de dois a três anos para ministros do STF.'),
]

LAW_API = 'https://legisla.casacivil.go.gov.br/api/v2/pesquisa/legislacoes/{id}'
ACTS = [
 ('presidente-55', 'eco-privatizacao', 1, 100985, 'RONALDO RAMOS CAIADO',
  'Autoriza o Poder Executivo do Estado de Goiás a promover medidas de desestatização da CELG Geração e Transmissão S/A - CELG-GT',
  'Como governador de Goiás, sancionou a Lei 20.762/2020, que autoriza desestatizar a CELG-GT, a Metrobus, a Iquego, a Goiasgás e a Goiás Telecom.'),
 ('presidente-55', 'eco-privatizacao', 1, 107818, 'RONALDO CAIADO Governador do Estado',
  'Autoriza o Poder Executivo do Estado de Goiás a promover medidas de desestatização da Companhia Celg de Participações – CELGPAR.',
  'Como governador de Goiás, sancionou a Lei 22.286/2023, que autoriza desestatizar a CelgPar.'),
 ('presidente-55', 'amb-licenciamento', 1, 100893, 'RONALDO RAMOS CAIADO',
  'licença ambiental por adesão e compromisso - LAC: ato administrativo que autoriza a localização, instalação e a operação de atividade ou empreendimento, mediante declaração de adesão e compromisso do empreendedor',
  'Como governador de Goiás, sancionou a Lei 20.694/2019, que criou a licença por adesão e compromisso (LAC), concedida por declaração do empreendedor.'),
 ('presidente-55', 'soc-cotas', 1, 103280, 'RONALDO CAIADO Governador do Estado',
  'O sistema de cotas previsto nesta Lei será empregado durante 25 (vinte e cinco) anos',
  'Como governador de Goiás, sancionou a Lei 20.807/2020, que estende para 25 anos as cotas nas universidades estaduais.'),
 ('presidente-55', 'soc-aborto', -1, 108399, 'RONALDO CAIADO Governador do Estado',
  'Institui a Campanha de Conscientização contra o Aborto para as Mulheres no Estado de Goiás.',
  'Como governador de Goiás, sancionou a Lei 22.537/2024, que cria a Campanha de Conscientização contra o Aborto.'),
]


def video_row(c, q, pos, vid, alias, start, end, detail):
    raw = f'pres/raw/yt/{vid}.txt'
    t = open(raw, encoding='utf-8').read(); idx = json.load(open(raw + '.idx.json'))
    i = t.find(start); assert i >= 0, (vid, 'start not found', start)
    j = t.find(end, i); assert j >= 0, (vid, 'end not found', end)
    quote = t[i:j + len(end)]; assert len(quote) <= 300, (vid, len(quote))
    ts = ts_at(idx, i); h, m, s = map(int, ts.split(':'))
    meta = META[vid]
    return dict(candidateId=c, questionId=q, position=pos, kind='platform', video=vid, raw=raw, alias=alias,
                url=f'https://www.youtube.com/watch?v={vid}&t={h*3600+m*60+s}s', timestamp=ts, quote=quote, detail=detail, **meta)


def act_row(c, q, pos, law_id, signer, quote, detail):
    d = json.load(open(f'pres/raw/web/go_{law_id}.json', encoding='utf-8'))
    return dict(candidateId=c, questionId=q, position=pos, kind='record', act='go-law', lawId=law_id, raw=f'pres/raw/web/go_{law_id}.json',
                url=LAW_API.format(id=law_id), date=d['data_legislacao'][:10], number=d['numero'], signer=signer, quote=quote, detail=detail)


def main():
    import os
    for law in (100985, 107818, 100893, 103280, 108399, 108873):
        p = f'pres/raw/web/go_{law}.json'
        if not os.path.exists(p):
            os.system(f'curl -sL -A "Mozilla/5.0" -o {p} {LAW_API.format(id=law)}')
    rows = [video_row(*v) for v in VIDEOS] + [act_row(*a) for a in ACTS]
    with open('pres/draft.jsonl', 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(rows), 'rows')


if __name__ == '__main__':
    main()
