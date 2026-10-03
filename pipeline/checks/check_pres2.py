"""doc-tdd for pipeline/pres2. Run from the repo root or pipeline/: .venv/bin/python checks/check_pres2.py [--draft path]"""
import html
import json
import os
import random
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'platform')
sys.path.insert(0, 'pres2')
from vtt import flat, ts_at  # noqa: E402
from search_path import path  # noqa: E402

ACCESSED = '2026-10-03'
ADDRESS = re.compile(r'\b(o senhor|a senhora|candidat[oa])\b', re.I)
FIRST_PERSON = re.compile(r'\b(eu|meu|minha|nós|vamos|sou)\b', re.I)
OFFICIAL = {'Poder360', 'Metrópoles', 'Roda Viva', 'Rádio CBN', 'Jovem Pan News', 'CNN Brasil'}
_live = {}


def norm(s):
    return re.sub(r'\s+', ' ', html.unescape(s)).strip().lower()


def live_captions(vid):
    if vid not in _live:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['.venv/bin/yt-dlp', '--no-update', '--skip-download', '--write-auto-subs', '--write-subs',
                            '--sub-langs', 'pt-orig,pt-BR', '--sub-format', 'vtt', '-o', f'{d}/%(id)s.%(ext)s',
                            f'https://www.youtube.com/watch?v={vid}'], capture_output=True, timeout=240)
            vtts = [f for f in os.listdir(d) if f.endswith('.vtt')]
            pick = next((f for f in vtts if '.pt-orig.' in f), None) or (vtts[0] if vtts else None)
            _live[vid] = flat(f'{d}/{pick}')[0] if pick else None
    return _live[vid]


def check_video(r, live):
    why = []
    t = open(path(r['video'])).read()
    idx = json.load(open(path(r['video']) + '.idx.json'))
    qi = t.find(r['quote'])
    if qi < 0:
        return 'FAIL', ['quote not in cached captions']
    if ts_at(idx, qi) != r['timestamp']:
        why.append(f"timestamp {r['timestamp']} != {ts_at(idx, qi)}")
    if r['alias'].lower() not in r['title'].lower():
        why.append('video title does not name the candidate')
    if r['channel'] not in OFFICIAL:
        why.append(f"channel {r['channel']} not on the outlet list")
    if r['date'] < '2025-01-01':
        why.append('statement older than 2025')
    if ADDRESS.search(r['quote']):
        why.append('quote addresses the candidate (interviewer speech)')
    turn = t.rfind('&gt;&gt;', 0, qi)
    window = t[(turn if turn >= 0 else max(0, qi - 400)):qi + len(r['quote'])]
    if not FIRST_PERSON.search(window):
        why.append('no first-person speech in the quote turn')
    if why:
        return 'FAIL', why
    if live:
        lt = live_captions(r['video'])
        if lt is None:
            return 'CACHED-ONLY', ['live caption fetch failed']
        if norm(r['quote']) not in norm(lt):
            return 'FAIL', ['quote not in live captions']
    return 'PASS', []


def law_text(f):
    raw = open(f, 'rb').read().decode('latin-1', 'ignore')
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', raw)))


def check_law(r):
    t = law_text(r['cache'])
    missing = [k for k in ('quote', 'signer', 'heading') if r[k] not in t]
    return ('PASS', []) if not missing else ('FAIL', [f'{k} not in law text' for k in missing])


def check_senado(r, live):
    data = json.load(open(r['cache']))
    if live:
        p = subprocess.run(['curl', '-sL', '--max-time', '40', '-H', 'Accept: application/json', r['url']], capture_output=True)
        try:
            data = json.loads(p.stdout.decode('utf-8'))
        except ValueError:
            return 'CACHED-ONLY', ['live fetch failed']
    v = next((x for x in data if x['codigoSessaoVotacao'] == r['session']), None)
    if not v:
        return 'FAIL', ['session not found']
    why = []
    if r['ementa'] not in v['ementa']:
        why.append('ementa differs')
    if v['dataSessao'] != r['date']:
        why.append('date differs')
    vote = next((x['siglaVotoParlamentar'] for x in v['votos'] if x['codigoParlamentar'] == r['parl']), None)
    if vote != r['vote']:
        why.append(f'vote is {vote}, row says {r["vote"]}')
    # Sustar the 2019 arms decree = narrow access; voting Não keeps it = +1 on widening access.
    expected = {'Não': 1, 'Sim': -1}.get(r['vote'])
    if expected != r['position']:
        why.append('position does not follow the vote')
    return ('PASS', []) if not why else ('FAIL', why)


def check(r, live=False):
    return {'video': check_video, 'law': lambda x, _l: check_law(x), 'senado': check_senado}[r['type']](r, live)


def to_evidence(r, i):
    eid = f"pres2-{r['candidateId']}-{r['questionId']}-{i}"
    if r['type'] == 'video':
        src = {'url': r['url'], 'accessed': ACCESSED, 'label': f"{r['channel']}, {r['title']} (legenda automática, {r['timestamp']})"}
    else:
        src = {'url': r['url'], 'accessed': ACCESSED, 'label': r['label']}
    ev = {'id': eid, 'subject': {'type': 'candidate', 'id': r['candidateId']}, 'questionId': r['questionId'], 'kind': r['kind'],
          'position': r['position'], 'detail': r['detail'], 'date': r['date'], 'source': src, 'checkId': eid, 'lowDiscrimination': False}
    if r['type'] != 'senado':
        ev['quote'] = r['quote']
    return ev


def controls(rows):
    by = {(r['candidateId'], r['questionId']): r for r in rows}
    out = []
    v = dict(by[('presidente-29', 'soc-aborto')]); v['quote'] = 'Nós somos contra a legalização do aborto.'
    out.append(('NEG-fabricated-rui-quote', v))
    s = dict(by[('presidente-22', 'seg-armas')]); s['vote'] = 'Sim'
    out.append(('NEG-flavio-voted-sim-pdl233', s))
    law = dict(by[('presidente-13', 'eco-privatizacao')]); law['signer'] = 'JAIR MESSIAS BOLSONARO'
    out.append(('NEG-decree-signed-by-bolsonaro', law))
    old = dict(by[('presidente-55', 'eco-arcabouco')]); old['date'] = '2019-06-10'
    out.append(('NEG-old-statement', old))
    wrong = dict(by[('presidente-70', 'seg-armas')]); wrong['alias'] = 'Zema'
    out.append(('NEG-cury-quote-as-zema', wrong))
    ask = dict(by[('presidente-70', 'seg-maioridade')]); ask['quote'] = 'Quando o senhor é favorável a redução então para 16 anos?'
    out.append(('NEG-interviewer-question-as-quote', ask))
    ts = dict(by[('presidente-14', 'seg-maioridade')]); ts['timestamp'] = '00:10:00'
    out.append(('NEG-tampered-timestamp', ts))
    return out


def main():
    draft = sys.argv[sys.argv.index('--draft') + 1] if '--draft' in sys.argv else 'pres2/draft.jsonl'
    rows = [json.loads(line) for line in open(draft, encoding='utf-8') if line.strip()]
    existing = json.load(open('../src/data/evidence.json'))
    seen = {(e['subject']['id'], e['questionId'], e.get('quote')) for e in existing if not e['id'].startswith('pres2-')}
    random.seed(11)
    report = {'rows': [], 'controls': []}
    shipped = []
    for i, r in enumerate(rows):
        live = r['type'] == 'senado' or random.random() < 0.4
        st, why = check(r, live)
        if (r['candidateId'], r['questionId'], r.get('quote')) in seen:
            st, why = 'FAIL', why + ['duplicate of an existing evidence row']
        ev = to_evidence(r, i)
        report['rows'].append({'id': ev['id'], 'status': st, 'claim': r['detail'], 'why': why, 'live': live})
        print(f"{st:<12}{ev['id']:<50}{'; '.join(why)}")
        if st == 'PASS':
            shipped.append(ev)
    broken = 0
    for name, row in controls(rows):
        st, why = check(row, False)
        ok = st != 'PASS'
        broken += not ok
        report['controls'].append({'id': name, 'status': 'FAIL' if ok else 'CONTROL-PASSED', 'why': why})
        print(f"CONTROL {name:<40} -> {'FAIL (ok)' if ok else 'PASSED (HARNESS BROKEN)'} {'; '.join(why)}")
    report['harness_ok'] = broken == 0
    json.dump(report, open('checks/pres2.report.json', 'w'), ensure_ascii=False, indent=1)
    if broken:
        sys.exit('harness broken: a control passed')
    json.dump(shipped, open('pres2/evidence.json', 'w'), ensure_ascii=False, indent=1)
    print({'total': len(rows), 'passed': len(shipped), 'failed': len(rows) - len(shipped), 'harnessOk': True})


if __name__ == '__main__':
    main()
