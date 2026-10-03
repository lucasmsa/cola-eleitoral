"""Builds pres2/draft.jsonl. Video quotes are sliced from cached captions between two anchors. Run from pipeline/."""
import json
import sys

sys.path.insert(0, 'platform')
sys.path.insert(0, 'pres2')
from vtt import ts_at  # noqa: E402
from search_path import path  # noqa: E402

ACCESSED = '2026-10-03'


def meta():
    out = {}
    for f in ('pres/raw/yt/meta.txt', 'pres2/raw/yt/meta.txt'):
        for line in open(f, encoding='utf-8'):
            p = line.rstrip('\n').split('|')
            vid, up, ch, title = p[0], p[1], p[2], '|'.join(p[3:])
            out[vid] = dict(date=f'{up[:4]}-{up[4:6]}-{up[6:]}', channel=ch, title=title.split('|pt')[0].rstrip('|'))
    return out


META = meta()

# (candidateId, questionId, position, video, alias, start anchor, end anchor, detail)
VIDEOS = [
    ('presidente-29', 'soc-aborto', 1, 'Kf70ybt-JCQ', 'Rui', 'Nós defendemos a legalização integral do aborto.', 'Nós defendemos a legalização integral do aborto.',
     'No Poder Entrevista (Poder360), perguntado se mantém as regras atuais sobre aborto, disse que defende a legalização integral do aborto.'),
    ('presidente-29', 'seg-drogas', -1, 'Kf70ybt-JCQ', 'Rui', 'nós somos favoráveis à liberação não só da maconha', 'mas das drogas em geral.',
     'No Poder Entrevista (Poder360), disse ser favorável à liberação da maconha e das drogas em geral.'),
    ('presidente-29', 'amb-margem-equatorial', 1, 'Kf70ybt-JCQ', 'Rui', 'que deu margem até que as pessoas quisessem proibir a prospecção de petróleo na margem equatorial.', 'É uma coisa absurda',
     'No Poder Entrevista (Poder360), chamou de absurda a ideia de proibir a prospecção de petróleo na Margem Equatorial.'),
    ('presidente-29', 'seg-8-janeiro', 0, 'BEgmPNuJkew', 'Rui', 'A anistia seria uma forma de remediar', 'porque o processo foi claramente antidemocrático.',
     'No Metrópoles, disse que a anistia seria uma forma de remediar, mas que o correto seria revisar os processos do 8 de janeiro, que chamou de antidemocráticos.'),
    ('presidente-55', 'eco-arcabouco', -1, '51g_wYigfag', 'Caiado', 'Exatamente essa minha proposta. Não vai ser', 'não vai ser teto de gasto',
     'No Roda Viva (TV Cultura), disse que sua regra fiscal não será o arcabouço (a legenda automática grafou "acabolso") nem o teto de gastos, e sim um corte anual de 1 ponto da dívida em relação ao PIB.'),
    ('presidente-55', 'eco-reforma-tributaria', 0, 'paCqhaxjKnk', 'Caiado', 'eu vou revisitar o tema da reforma tributária.', 'eu vou revisitar o tema da reforma tributária.',
     'Na sabatina da CBN, disse não ser contra a reforma tributária, mas que vai revisitar o tema.'),
    ('presidente-70', 'seg-armas', -1, '293zOwIne38', 'Cury', 'Não, nós temos que armar a nossa polícia', 'nós temos que valorizar a nossa polícia.',
     'Na sabatina da CBN, perguntado se armaria a população, respondeu que não e que é preciso armar e valorizar a polícia.'),
    ('presidente-70', 'eco-privatizacao', 0, '2S4C9xOFH04', 'Cury', 'Eu cogito privatizar sim todas as', 'que não for eficiente serão privatizadas',
     'Na Jovem Pan, disse que privatizaria as estatais que não forem eficientes, citando os Correios; em outra sabatina, defendeu manter a Petrobras para financiar programas.'),
    ('presidente-70', 'seg-maioridade', 1, '2S4C9xOFH04', 'Cury', 'Eu eu sou favorável, mas mais do que favorável', 'o problema não é esse.',
     'Na Jovem Pan, perguntado se é favorável à redução da maioridade penal para 16 anos, disse que é favorável.'),
    ('presidente-14', 'seg-maioridade', 1, 'K6Ns-ELnHu8', 'Renan', 'Vamos reduzir necessariamente.', 'Todos os crimes violentos vai ter redução da idade penal',
     'Em sabatina com empresários exibida pela CNN, defendeu reduzir a maioridade penal para crimes violentos (a legenda automática grafou "morade penal").'),
]

LAWS = [
    ('presidente-13', 'eco-privatizacao', -1, 'pres2/raw/web/d11478.htm', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/D11478.htm',
     'Ficam excluídos do PND e revogadas as qualificações no PPI', 'LUIZ INÁCIO LULA DA SILVA', 'DECRETO Nº 11.478, DE 6 DE ABRIL DE 2023', '2023-04-06',
     'Como presidente, assinou o Decreto 11.478/2023, que tirou do Programa Nacional de Desestatização os Correios, a EBC, a Dataprev, o Serpro, a Nuclep, a ABGF e o Ceitec.',
     'Presidência da República, Planalto, Decreto 11.478/2023'),
]

SENADO = [
    ('presidente-22', 'seg-armas', 1, 'pres2/raw/web/senado_pdl233_2019.json', 'https://legis.senado.leg.br/dadosabertos/votacao?sigla=PDL&numero=233&ano=2019',
     5971, 5894, 'Não', 'Susta o Decreto nº 9.785, de 07 de Maio de 2019',
     'Votou NÃO no PDL 233/2019, que sustava o Decreto 9.785/2019 sobre aquisição, posse e porte de armas, no Senado, em 18/06/2019 (então no PSL).',
     'Senado Federal, Dados Abertos, votação 5971'),
]


def video_rows():
    rows = []
    for cid, qid, pos, vid, alias, a, b, detail in VIDEOS:
        t = open(path(vid)).read()
        idx = json.load(open(path(vid) + '.idx.json'))
        i = t.find(a)
        assert i >= 0, (vid, a)
        j = t.find(b, i)
        assert j >= 0, (vid, b)
        quote = t[i:j + len(b)]
        ts = ts_at(idx, i)
        h, m, s = map(int, ts.split(':'))
        md = META[vid]
        rows.append(dict(candidateId=cid, questionId=qid, position=pos, kind='platform', type='video', video=vid, alias=alias,
                         url=f'https://www.youtube.com/watch?v={vid}&t={h * 3600 + m * 60 + s}s', timestamp=ts, quote=quote,
                         detail=detail, date=md['date'], channel=md['channel'], title=md['title']))
    return rows


def law_rows():
    return [dict(candidateId=c, questionId=q, position=p, kind='record', type='law', cache=f, url=u, quote=quote, signer=signer,
                 heading=heading, date=d, detail=detail, label=label)
            for c, q, p, f, u, quote, signer, heading, d, detail, label in LAWS]


def senado_rows():
    return [dict(candidateId=c, questionId=q, position=p, kind='record', type='senado', cache=f, url=u, session=sess, parl=parl,
                 vote=vote, ementa=em, date='2019-06-18', detail=detail, label=label)
            for c, q, p, f, u, sess, parl, vote, em, detail, label in SENADO]


if __name__ == '__main__':
    rows = video_rows() + law_rows() + senado_rows()
    with open('pres2/draft.jsonl', 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(len(rows), 'rows')
    for r in rows:
        print(r['candidateId'], r['questionId'], r['position'], r.get('timestamp', ''), (r.get('quote') or r.get('vote'))[:90])
