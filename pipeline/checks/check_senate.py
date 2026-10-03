"""doc-tdd for pipeline/senate: every draft row is re-derived from its primary source; only PASS rows ship.

Usage: python3 pipeline/checks/check_senate.py [--draft path]
Writes pipeline/checks/senate.report.json, pipeline/senate/evidence.json, pipeline/senate/questions.json.
"""
import html
import json
import os
import random
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEN = os.path.join(ROOT, 'senate')
sys.path.insert(0, SEN)
from fetch import fetch, jget  # noqa: E402

C = 'https://dadosabertos.camara.leg.br/api/v2'
S = 'https://legis.senado.leg.br/dadosabertos'
WINDOW = 700
AFTER = 150
SUPPORT = {
    'sen-rec-senador-155-seg-armas-sf5971': [
        ('page', 'https://www12.senado.leg.br/noticias/materias/2019/06/18/senado-derruba-decreto-sobre-armas',
         'busca flexibilizar a posse e o porte de armas')],
    'sen-rec-senador-155-seg-blindagem-ccj38935': [('senado_processo', 8915268, 'pela rejeição unânime')],
}


def norm(s):
    s = unicodedata.normalize('NFC', html.unescape(s))
    s = s.replace(' ', ' ').replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    s = s.replace('×', 'x')
    return re.sub(r'\s+', ' ', s).strip()


def page_text(url, live=False):
    raw = fetch(url, accept='text/html', refresh=live).decode('utf-8', errors='ignore')
    body = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    title = re.search(r'(?is)<title>(.*?)</title>', raw)
    return norm(re.sub(r'<[^>]+>', ' ', body)), norm(title.group(1)) if title else '', raw


def page_date(raw):
    for pat in (r'"datePublished"\s*:\s*"([^"]+)"', r'article:published_time"\s+content="([^"]+)"',
                r'content="([^"]+)"\s+property="article:published_time"'):
        m = re.search(pat, raw)
        if m:
            return m.group(1)[:10]
    return None


def check_web_quote(row, live):
    ref = row['_ref']
    text, title, raw = page_text(ref['url'], live=live)
    q = norm(row['quote'])
    i = text.find(q)
    if i < 0:
        return False, 'quote not found verbatim'
    window = text[max(0, i - WINDOW): i + len(q) + AFTER]
    if not any(n.lower() in window.lower() or n.lower() in title.lower() for n in ref['names']):
        return False, f"candidate name {ref['names']} not within attribution window"
    if row['date'] < '2025-01-01':
        return False, 'statement older than 2025'
    if ref.get('date_marker'):
        if ref['date_marker'] not in raw:
            return False, f"date marker {ref['date_marker']} not in page"
    elif page_date(raw) != row['date']:
        return False, f'page date {page_date(raw)} != {row["date"]}'
    return True, ''


def check_camara_vote(row, live):
    ref = row['_ref']
    votes = jget(f"{C}/votacoes/{ref['votacao']}/votos", refresh=live)['dados']
    v = [x for x in votes if x['deputado_']['id'] == ref['deputado']]
    if not v:
        return False, 'deputy not in roll call'
    t = v[0]['tipoVoto']
    want = 1 if t == 'Sim' else -1 if t == 'Não' else None
    if want != row['position']:
        return False, f'position {row["position"]} but source says {t}'
    meta = jget(f"{C}/votacoes/{ref['votacao']}", refresh=live)['dados']
    if meta['data'][:10] != row['date']:
        return False, 'date differs'
    return True, ''


def check_senado_vote(row, live):
    ref = row['_ref']
    vot = [x for x in jget(ref['url'], refresh=live) if x['codigoSessaoVotacao'] == ref['cod']]
    if not vot:
        return False, 'votação not found'
    v = [x for x in vot[0]['votos'] if x['codigoParlamentar'] == ref['parl']]
    if not v:
        return False, 'senator not in roll call'
    t = v[0]['siglaVotoParlamentar']
    expected = -1 if t == 'Sim' else 1 if t == 'Não' else None
    if expected != row['position']:
        return False, f'position {row["position"]} but source vote {t}'
    if vot[0]['dataSessao'][:10] != row['date']:
        return False, 'date differs'
    return True, ''


def check_senado_committee(row, live):
    ref = row['_ref']
    vs = jget(ref['url'], refresh=live)['VotacoesComissao']['Votacoes']['Votacao']
    vs = [vs] if isinstance(vs, dict) else vs
    vot = [x for x in vs if x['CodigoVotacao'] == ref['cod']]
    if not vot:
        return False, 'votação not found'
    votos = vot[0]['Votos']['Voto']
    votos = [votos] if isinstance(votos, dict) else votos
    v = [x for x in votos if x['CodigoParlamentar'] == ref['parl']]
    if not v:
        return False, 'senator not in committee vote'
    expected = -1 if v[0]['QualidadeVoto'] == 'S' else 1
    if expected != row['position']:
        return False, f"position {row['position']} but source vote {v[0]['QualidadeVoto']}"
    if vot[0]['DataHoraInicioReuniao'][:10] != row['date']:
        return False, 'date differs'
    return True, ''


def check_support(kind, a, b=None):
    if kind == 'page':
        text, _, _ = page_text(a)
        return norm(b) in text
    if kind == 'senado_processo':
        return norm(b) in norm(json.dumps(jget(f'{S}/processo/{a}'), ensure_ascii=False))
    if kind == 'camara_desc':
        return norm(b) in norm(jget(f'{C}/votacoes/{a}')['dados']['descricao'])
    if kind == 'camara_date':
        return jget(f'{C}/votacoes/{a}')['dados']['data'][:10] == b
    if kind == 'camara_ementa':
        return norm(b) in norm(jget(f'{C}/proposicoes/{a}')['dados']['ementa'])
    if kind == 'cf':
        raw = open(os.path.join(ROOT, 'alpb', 'raw', 'cf88.html'), 'rb').read().decode('cp1252', errors='ignore')
        return norm(a) in norm(re.sub(r'<[^>]+>', ' ', raw))
    raise ValueError(kind)


YT = os.path.join(SEN, 'raw', 'yt')


def caption_norm(s):
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r"[^\w\s]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def parse_vtt(path):
    """[(start_seconds, line)] with YouTube rolling-caption duplicates removed."""
    out, start = [], None
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        m = re.match(r'(\d+):(\d+):(\d+(?:\.\d+)?) --> ', line)
        if m:
            start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
            continue
        if start is None or not line or line.startswith(('NOTE', 'WEBVTT', 'Kind:', 'Language:')):
            continue
        text = re.sub(r'<[^>]+>', '', line).strip()
        if text and (not out or out[-1][1] != text):
            out.append((start, text))
    return out


def original_track(video, vtt, info):
    if 'translated' in vtt:
        return False
    if vtt.endswith('.pt-orig.vtt'):
        return True
    ac = info.get('automatic_captions') or {}
    url = next((x.get('url', '') for x in ac.get('pt', []) if x.get('ext') == 'vtt'), '')
    return bool(url) and 'tlang=' not in url


def to_seconds(mmss):
    parts = [float(x) for x in mmss.split(':')]
    return sum(v * 60 ** i for i, v in enumerate(reversed(parts)))


def check_caption_quote(row, live):
    ref = row['_ref']
    fuzzy = ref.get('fuzzy') or []
    if len(fuzzy) > 2 or any(len(a.split()) != 1 or len(b.split()) != 1 for a, b in fuzzy):
        return False, 'fuzzy window exceeds 2 single-word substitutions'
    info = json.load(open(os.path.join(YT, f"{ref['video']}.audio.info.json")))
    if not original_track(ref['video'], ref['vtt'], info):
        return False, "caption track is not the channel's original pt ASR (translated or local transcript)"
    cues_all = parse_vtt(os.path.join(YT, ref['vtt']))
    t_quote = to_seconds(ref['start'])
    if ref.get('speaker_cue'):
        tc = to_seconds(ref['speaker_cue'])
        intro = caption_norm(' '.join(c[1] for c in cues_all if tc - 5 <= c[0] <= tc + 40))
        if caption_norm(ref['speaker_text']) not in intro:
            return False, 'moderator announcement not found at speaker cue'
        if not any(caption_norm(n) in intro for n in ref['names']):
            return False, 'announcement does not name the candidate'
        if not (tc <= t_quote <= tc + 420):
            return False, 'quote outside the announced confrontation'
        if ref.get('turn_anchor'):
            pre = caption_norm(' '.join(c[1] for c in cues_all if t_quote - 90 <= c[0] <= t_quote + 2))
            if caption_norm(ref['turn_anchor']) not in pre:
                return False, 'turn anchor not found right before the quote'
        between = caption_norm(' '.join(c[1] for c in cues_all if tc + 45 < c[0] < t_quote))
        if any(k in between for k in ('convido agora', 'obrigatoriamente', 'encerrado mais um confronto')):
            return False, 'a new confrontation starts before the quote'
    elif not any(n.lower() in info['title'].lower() for n in ref['names']):
        return False, 'video title does not name the candidate'
    up = info.get('upload_date') or ''
    date = f'{up[:4]}-{up[4:6]}-{up[6:]}'
    if date != row['date'] or date < '2025-01-01':
        return False, f'upload date {date} vs row {row["date"]}'
    t0 = t_quote
    window = caption_norm(' '.join(c[1] for c in cues_all if t0 - 20 <= c[0] <= t0 + 60))
    q = caption_norm(row['quote'])
    for expected, heard in fuzzy:
        q = re.sub(rf'\b{re.escape(caption_norm(expected))}\b', caption_norm(heard), q, count=1)
    if q not in window:
        return False, 'quote not in transcript window'
    if f"t={int(t0)}s" not in row['source']['url']:
        return False, 'source url timestamp mismatch'
    return True, ('fuzzy: ' + json.dumps(fuzzy, ensure_ascii=False)) if fuzzy else ''


CHECKERS = {'caption_quote': check_caption_quote, 'web_quote': check_web_quote, 'camara_vote': check_camara_vote,
            'senado_vote': check_senado_vote, 'senado_committee': check_senado_committee}


def run_row(row, live):
    try:
        ok, why = CHECKERS[row['_ref']['type']](row, live)
    except Exception as e:  # a fetch or parse failure is a FAIL, never a pass
        ok, why = False, f'error: {e}'
    if ok:
        for sup in SUPPORT.get(row['id'], []):
            if not check_support(*sup):
                return False, f'support check failed: {sup[2]}'
    return ok, why


def controls(rows):
    by = {r['id']: r for r in rows}
    out = []
    flip = dict(by['sen-rec-senador-155-seg-armas-sf5971'], position=1)
    out.append(('NEG-flip-veneziano-pdl233', flip))
    fake = dict(by['sen-plat-senador-100-eco-6x1'], quote='Sou contra o fim da escala 6x1')
    out.append(('NEG-fabricated-nabor-quote', fake))
    wrong = dict(by['sen-plat-senador-222-seg-drogas'], subject={'type': 'candidate', 'id': 'senador-100'})
    wrong['_ref'] = dict(wrong['_ref'], names=['Nabor'])
    out.append(('NEG-queiroga-quote-as-nabor', wrong))
    old = dict(by['sen-plat-senador-100-seg-maioridade'], date='2024-08-26')
    out.append(('NEG-old-statement', old))
    dep = [r for r in rows if r['_ref']['type'] == 'camara_vote' and r['subject']['id'] == 'deputado_federal-1345'][0]
    out.append(('NEG-flip-couto-maioridade', dict(dep, position=-dep['position'])))
    caps = {r['id']: r for r in rows if r['_ref']['type'] == 'caption_quote'}
    if caps:
        g = caps['sen-cap-senador-151-seg-maioridade']
        out.append(('NEG-caption-fabricated', dict(g, quote='Sou contra a redução da maioridade penal.')))
        wrong = dict(g, subject={'type': 'candidate', 'id': 'senador-100'})
        wrong['_ref'] = dict(g['_ref'], names=['nabor'])
        out.append(('NEG-caption-speaker-not-in-confrontation', wrong))
        f = caps['sen-cap-senador-300-seg-stf-mandato']
        tr = dict(f)
        tr['_ref'] = dict(f['_ref'], vtt='zc7d4U8eEnI.pt-translated-DO-NOT-QUOTE.vtt')
        out.append(('NEG-caption-translated-track', tr))
        q = caps['sen-cap-senador-222-seg-8-janeiro']
        wide = dict(q)
        wide['_ref'] = dict(q['_ref'], fuzzy=[['8', 'lá'], ['anistia', 'x'], ['vítimas', 'y']])
        out.append(('NEG-caption-fuzzy-over-2-words', wide))
        late = dict(g)
        late['_ref'] = dict(g['_ref'], speaker_cue='01:32:05', speaker_text='Gadelha ao candidato Major Fábio')
        out.append(('NEG-caption-wrong-confrontation', late))
    return out


def main():
    draft_path = sys.argv[sys.argv.index('--draft') + 1] if '--draft' in sys.argv else os.path.join(SEN, 'draft.json')
    draft = json.load(open(draft_path))
    rows = draft['evidence']
    existing = json.load(open(os.path.join(os.path.dirname(ROOT), 'src', 'data', 'evidence.json')))
    have = {(e['subject']['id'], e['questionId'], e['source']['url'], e.get('quote')) for e in existing if not e['id'].startswith('sen-')}
    random.seed(7)
    report, shipped = [], []
    for r in rows:
        live = r['_ref']['type'] != 'web_quote' and random.random() < 0.25
        if (r['subject']['id'], r['questionId'], r['source']['url'], r.get('quote')) in have:
            report.append({'id': r['id'], 'status': 'DUPLICATE', 'claim': r['detail']})
            continue
        ok, why = run_row(r, live)
        report.append({'id': r['id'], 'status': 'PASS' if ok else 'FAIL', 'claim': r['detail'], 'live': live, 'error': why})
        if ok:
            shipped.append({k: v for k, v in r.items() if k != '_ref'})
    qreport, qshipped = [], []
    for q in draft['questions']:
        bad = [c for c in q['_checks'] if not check_support(*c)]
        qreport.append({'id': q['id'], 'status': 'FAIL' if bad else 'PASS', 'claim': q['context'], 'error': str(bad)})
        if not bad:
            qshipped.append({k: v for k, v in q.items() if k != '_checks'})
    ctl = []
    for cid, row in controls(rows):
        ok, why = run_row(row, False)
        ctl.append({'id': cid, 'status': 'CONTROL-PASSED' if ok else 'FAIL', 'reason': why})
    harness_ok = all(c['status'] == 'FAIL' for c in ctl)
    report_path = os.path.join(ROOT, 'checks', 'senate.report.json' if '--draft' not in sys.argv else 'senate.draft-report.json')
    json.dump({'harness_ok': harness_ok, 'rows': report + qreport, 'controls': ctl},
              open(report_path, 'w'), ensure_ascii=False, indent=1)
    passed = sum(r['status'] == 'PASS' for r in report)
    print(f"rows={len(report)} PASS={passed} FAIL={sum(r['status'] == 'FAIL' for r in report)} "
          f"live={sum(bool(r.get('live')) for r in report)} questions_pass={sum(q['status'] == 'PASS' for q in qreport)}/{len(qreport)} "
          f"controls={len(ctl)} harness_ok={harness_ok}")
    for r in report + qreport:
        if r['status'] == 'FAIL':
            print('  FAIL', r['id'], r['error'])
    for c in ctl:
        print('  CONTROL', c['id'], c['status'], c['reason'])
    if not harness_ok:
        sys.exit(1)
    if '--draft' not in sys.argv:
        json.dump(shipped, open(os.path.join(SEN, 'evidence.json'), 'w'), ensure_ascii=False, indent=1)
        json.dump(qshipped, open(os.path.join(SEN, 'questions.json'), 'w'), ensure_ascii=False, indent=1)
        print('evidence.json written:', len(shipped), 'rows;', len(qshipped), 'questions')


if __name__ == '__main__':
    main()
