"""doc-tdd for presidential gap evidence (pipeline/pres). Run from pipeline/: .venv/bin/python checks/check_pres.py"""
import csv, difflib, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'platform')
from vtt import flat, ts_at  # noqa: E402

ACCESSED = '2026-10-01'
TURN = '&gt;&gt;'
ADDRESS = re.compile(r'\b(o senhor|a senhora|candidat[oa]|governador)\b', re.I)
FIRST_PERSON = re.compile(r'\b(eu|meu|minha|mim|nós|me)\b', re.I)
SANCTION = 'decreta e eu sanciono'
_live = {}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def tse_names():
    names = {}
    with open('raw/tse/consulta_cand_2026_BR.csv', encoding='latin-1') as fh:
        for r in csv.DictReader(fh, delimiter=';'):
            if r['DS_CARGO'] == 'PRESIDENTE':
                names[f"presidente-{r['NR_CANDIDATO']}"] = norm(r['NM_URNA_CANDIDATO'] + ' ' + r['NM_CANDIDATO'])
    return names


TSE = tse_names()


def names_match(alias, cid):
    tokens = [t for t in TSE.get(cid, '').lower().split() if len(t) > 2]
    return bool(tokens) and any(difflib.SequenceMatcher(None, a, t).ratio() >= 0.8 for a in alias.lower().split() for t in tokens)


def meta(vid):
    for line in open('pres/raw/yt/meta.txt', encoding='utf-8'):
        f = line.rstrip('\n').split('|', 3)
        if f[0] == vid:
            return dict(date=f'{f[1][:4]}-{f[1][4:6]}-{f[1][6:]}', channel=f[2], title=f[3])
    return None


def live_captions(vid):
    if vid not in _live:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['.venv/bin/yt-dlp', '--no-update', '--skip-download', '--write-auto-subs', '--sub-langs', 'pt-orig',
                            '--sub-format', 'vtt', '-o', f'{d}/%(id)s.%(ext)s', f'https://www.youtube.com/watch?v={vid}'],
                           capture_output=True, timeout=180)
            f = f'{d}/{vid}.pt-orig.vtt'
            _live[vid] = flat(f)[0] if os.path.exists(f) else None
    return _live[vid]


def live_json(url):
    if url not in _live:
        p = subprocess.run(['curl', '-sL', '--max-time', '40', '-A', 'Mozilla/5.0', url], capture_output=True)
        try:
            _live[url] = json.loads(p.stdout.decode('utf-8'))
        except ValueError:
            _live[url] = None
    return _live[url]


def check_video(r):
    why = []
    t = open(r['raw'], encoding='utf-8').read(); idx = json.load(open(r['raw'] + '.idx.json'))
    qi = t.find(r['quote'])
    if qi < 0:
        return 'FAIL', ['quote not in cached captions']
    if ts_at(idx, qi) != r['timestamp']:
        why.append(f"timestamp {r['timestamp']} != caption time {ts_at(idx, qi)}")
    m = meta(r['video'])
    if not m or m['date'] != r['date'] or m['title'] != r['title']:
        why.append('video metadata does not match meta.txt')
    if r['date'] < '2025-01-01':
        why.append('video older than 2025')
    if r['alias'].lower() not in r['title'].lower():
        why.append('alias not in video title')
    if not names_match(r['alias'], r['candidateId']):
        why.append(f"alias '{r['alias']}' does not match TSE name of {r['candidateId']}")
    if '?' in r['quote'] or TURN in r['quote']:
        why.append('quote contains a question mark or a speaker change')
    if ADDRESS.search(r['quote']):
        why.append('quote addresses the candidate (interviewer speech)')
    if '?' not in t[max(0, qi - 1500):qi]:
        why.append('no question within 1500 chars before the quote')
    turn_start = t.rfind(TURN, 0, qi)
    window = t[(turn_start if turn_start >= 0 else max(0, qi - 400)):qi + len(r['quote'])]
    if not FIRST_PERSON.search(window):
        why.append('no first-person speech in the quote turn')
    if why:
        return 'FAIL', why
    live = live_captions(r['video'])
    if live is None:
        return 'CACHED-ONLY', ['live caption fetch failed']
    if norm(r['quote']) not in norm(live):
        return 'FAIL', ['quote not in live captions']
    return 'PASS', []


def law_text(d):
    return norm(d.get('conteudo_sem_formatacao', '')) if d else ''


def check_act(r):
    why = []
    d = json.load(open(r['raw'], encoding='utf-8'))
    t = law_text(d)
    for s, label in ((r['quote'], 'quote'), (r['signer'], 'signer'), (SANCTION, 'sanction formula')):
        if norm(s) not in t:
            why.append(f'{label} not in cached law text')
    if d.get('numero') != r['number'] or d.get('data_legislacao', '')[:10] != r['date']:
        why.append('law number/date mismatch')
    if r['date'] < '2019-01-01':
        why.append('act before the candidate took office as governor (2019-01-01)')
    if not names_match(r['signer'], r['candidateId']):
        why.append('signer does not match the candidate TSE name')
    if why:
        return 'FAIL', why
    live = law_text(live_json(r['url']))
    if not live:
        return 'CACHED-ONLY', ['live law fetch failed']
    if not all(norm(s) in live for s in (r['quote'], r['signer'], SANCTION)):
        return 'FAIL', ['live law text differs']
    return 'PASS', []


def check(r):
    if r['position'] not in (-1, 0, 1) or not r['quote'] or len(r['quote']) > 300:
        return 'FAIL', ['bad position or quote length']
    if r['candidateId'] not in TSE:
        return 'FAIL', ['candidate not in TSE presidential file']
    return check_video(r) if 'video' in r else check_act(r)


def controls(rows):
    by = {}
    for r in rows:
        by.setdefault((r['candidateId'], r['questionId']), r)
    zema = by[('presidente-30', 'seg-8-janeiro')]
    caiado = by[('presidente-55', 'seg-8-janeiro')]
    aborto = by[('presidente-55', 'soc-aborto')]
    priv = by[('presidente-55', 'eco-privatizacao')]
    promulgated = dict(aborto, lawId=108873, raw='pres/raw/web/go_108873.json', number='22.690', date='2024-05-14',
                       url=aborto['url'].replace('108399', '108873'), quote='Institui o Dia Estadual de Conscientização contra o Aborto.')
    return [
        ('NEG-fabricated-zema', dict(zema, quote='eu sou contra a anistia aos condenados')),
        ('NEG-caiado-quote-as-zema', dict(caiado, candidateId='presidente-30')),
        ('NEG-wrong-timestamp', dict(zema, timestamp='00:30:00')),
        ('NEG-interviewer-question', dict(zema, quote='O senhor pode explicar porquê?')),
        ('NEG-old-video', dict(caiado, date='2022-05-01')),
        ('NEG-law-promulgated-by-assembly', promulgated),
        ('NEG-law-tampered', dict(priv, quote='Autoriza o Poder Executivo do Estado de Goiás a promover medidas de desestatização da Saneago')),
    ]


def to_evidence(r, i):
    if 'video' in r:
        label = f"Vídeo: {r['channel']}, \"{r['title']}\", {r['timestamp']} (legenda automática em português)"
    else:
        y, m, d = r['date'].split('-')
        label = f"Casa Civil de Goiás, Legisla: Lei nº {r['number']}, de {d}/{m}/{y}"
    eid = f"pres-{r['candidateId']}-{r['questionId']}-{i}"
    ev = dict(id=eid, subject={'type': 'candidate', 'id': r['candidateId']}, questionId=r['questionId'], kind=r['kind'],
              position=r['position'], detail=r['detail'], quote=r['quote'], date=r['date'],
              source={'url': r['url'], 'accessed': ACCESSED, 'label': label}, checkId=eid, lowDiscrimination=False)
    if 'timestamp' in r:
        ev['timestamp'] = r['timestamp']
    return ev


def main():
    rows = [json.loads(line) for line in open('pres/draft.jsonl', encoding='utf-8')]
    existing = json.load(open('../src/data/evidence.json', encoding='utf-8'))
    seen = {(e['subject']['id'], e['questionId'], e.get('quote')) for e in existing if not e['id'].startswith('pres-')}
    report = {'rows': [], 'controls': []}
    passed = []
    for i, r in enumerate(rows):
        eid = f"pres-{r['candidateId']}-{r['questionId']}-{i}"
        st, why = check(r)
        if (r['candidateId'], r['questionId'], r['quote']) in seen:
            st, why = 'FAIL', why + ['duplicate of an existing evidence row']
        report['rows'].append(dict(id=eid, status=st, claim=r['detail'], reasons=why))
        print(f"{st:11} {eid:46} {'; '.join(why)}")
        if st in ('PASS', 'CACHED-ONLY'):
            passed.append(to_evidence(r, i))
    ok = True
    for name, r in controls(rows):
        st, why = check(r)
        good = st == 'FAIL'
        ok &= good
        report['controls'].append(dict(id=name, status=st, expectedFail=True, ok=good, reasons=why))
        print(f"CONTROL {name:34} -> {st} ({'ok' if good else 'HARNESS BROKEN'}) {'; '.join(why)}")
    report['summary'] = dict(total=len(rows), passed=sum(x['status'] == 'PASS' for x in report['rows']),
                             cachedOnly=sum(x['status'] == 'CACHED-ONLY' for x in report['rows']),
                             failed=sum(x['status'] == 'FAIL' for x in report['rows']), harnessOk=ok)
    json.dump(report, open('checks/pres.report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if ok:
        json.dump(passed, open('pres/evidence.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(report['summary'])
    sys.exit(0 if ok and report['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
