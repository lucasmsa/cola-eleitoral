"""doc-tdd checks for platform evidence. Run from pipeline/: .venv/bin/python checks/check_platform.py"""
import csv, json, re, subprocess, sys, os, html, difflib, tempfile
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ACCESSED = '2026-09-30'
OFFICE_CARGO = {'presidente': 'PRESIDENTE', 'governador': 'GOVERNADOR', 'senador': 'SENADOR'}
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36'


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def tse_rows():
    rows = {}
    for f in ('raw/tse/consulta_cand_2026_BR.csv', 'raw/tse/consulta_cand_2026_PB.csv'):
        with open(f, encoding='latin-1') as fh:
            for r in csv.DictReader(fh, delimiter=';'):
                rows[r['SQ_CANDIDATO']] = r
                rows[(r['DS_CARGO'], r['NR_CANDIDATO'])] = r
    return rows


TSE = tse_rows()
_pdf_cache = {}


def pdf_page(file, page):
    key = (file, page)
    if key not in _pdf_cache:
        r = PdfReader(f'raw/plans/{file}')
        _pdf_cache[key] = norm(r.pages[page - 1].extract_text() or '') if 0 < page <= len(r.pages) else ''
    return _pdf_cache[key]


def pdf_date(file):
    try:
        d = PdfReader(f'raw/plans/{file}').metadata.get('/CreationDate', '')
        m = re.match(r"D:(\d{4})(\d{2})(\d{2})", d or '')
        if m:
            return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    except Exception:
        pass
    return None


def live_text(url):
    p = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', UA, '-w', '\n%{http_code}', url], capture_output=True)
    body, _, code = p.stdout.decode('utf-8', 'ignore').rpartition('\n')
    if code != '200':
        return None
    body = re.sub(r'(?is)<(script|style|noscript|svg).*?</\1>', ' ', body)
    return norm(html.unescape(re.sub(r'(?s)<[^>]+>', ' ', body)))


def candidate_row(cid):
    office, nr = cid.split('-', 1)
    return TSE.get((OFFICE_CARGO[office], nr))


TURN = '&gt;&gt;'


def alias_matches(alias, cand):
    tokens = norm(cand['NM_URNA_CANDIDATO'] + ' ' + cand['NM_CANDIDATO']).lower().split()
    return any(difflib.SequenceMatcher(None, a, t).ratio() >= 0.75 for a in alias.lower().split() for t in tokens if len(t) > 2)


def live_captions(vid):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['yt-dlp', '--no-update', '--skip-download', '--write-auto-subs', '--sub-langs', 'pt-orig',
                        '--sub-format', 'vtt', '-o', f'{d}/%(id)s.%(ext)s', f'https://www.youtube.com/watch?v={vid}'],
                       capture_output=True, timeout=120)
        f = f'{d}/{vid}.pt-orig.vtt'
        if not os.path.exists(f):
            return None
        sys.path.insert(0, 'platform'); from vtt import flat
        return flat(f)[0]


def check_video(row, cand):
    sys.path.insert(0, 'platform'); from vtt import ts_at
    reasons = []
    if row.get('date', '') < '2025-01-01':
        reasons.append('video older than 2025')
    t = open(row['raw']).read(); idx = json.load(open(row['raw'] + '.idx.json'))
    qi = t.find(row['quote'])
    if qi < 0:
        return 'FAIL', reasons + ['quote not in cached captions']
    if ts_at(idx, qi) != row['timestamp']:
        reasons.append(f"timestamp {row['timestamp']} != caption time {ts_at(idx, qi)}")
    if not alias_matches(row['alias'], cand):
        reasons.append(f"alias '{row['alias']}' does not match TSE name {cand['NM_URNA_CANDIDATO']}")
    if '?' in row['quote']:
        reasons.append('quote contains a question')
    if row['mode'] == 'debate':
        ai = t.rfind(row['anchor'], 0, qi)
        if ai < 0 or qi - ai > 3000:
            reasons.append('moderator anchor not found within 3000 chars before quote')
        elif row['alias'].lower() not in row['anchor'].lower():
            reasons.append('anchor does not name the alias')
        elif t[ai:qi].count(TURN) > 3:
            reasons.append('more than 3 speaker turns between anchor and quote')
    else:
        if row['alias'].lower() not in row['title'].lower():
            reasons.append('interviewee alias not in video title')
        qm = t.rfind('?', 0, qi)
        if qm < 0 or t[qm:qi].count(TURN) > 1:
            reasons.append('quote is not in the answer right after a question')
        qe = qi + len(row['quote']); nt = t.find(TURN, qe)
        if '?' in t[qe:nt if nt >= 0 else len(t)]:
            reasons.append('a question follows the quote in the same turn (interviewer speech)')
    if reasons:
        return 'FAIL', reasons
    live = live_captions(row['video'])
    if live is None:
        return 'CACHED-ONLY', ['live caption fetch failed']
    if row['quote'] not in live:
        return 'FAIL', ['quote not in live captions']
    return 'PASS', []


def check(row):
    """Returns (status, reasons). status in PASS, CACHED-ONLY, FAIL."""
    reasons = []
    if row['position'] not in (-1, 0, 1):
        reasons.append('bad position')
    if not row['quote'] or len(row['quote']) > 300:
        reasons.append('quote empty or > 300 chars')
    cand = candidate_row(row['candidateId'])
    if cand is None:
        return 'FAIL', reasons + ['candidate number/office not in TSE CSV']
    if 'file' in row:
        sq = re.match(r'2026(?:BR|PB)(\d+)_', row['file'])
        if not sq or sq.group(1) != cand['SQ_CANDIDATO']:
            reasons.append(f"plan file SQ != TSE SQ_CANDIDATO {cand['SQ_CANDIDATO']} for {row['candidateId']}")
        if not row.get('page'):
            reasons.append('plan quote without page')
        elif norm(row['quote']) not in pdf_page(row['file'], row['page']):
            reasons.append(f"quote not on PDF page {row['page']}")
        return ('FAIL', reasons) if reasons else ('PASS', [])
    if 'video' in row:
        st, why = check_video(row, cand)
        return st, reasons + why
    if row.get('date', '') < '2025-01-01':
        reasons.append('web source older than 2025')
    surname = norm(cand['NM_URNA_CANDIDATO']).split()[-1].lower()
    cached = norm(open(row['raw']).read())
    if norm(row['quote']) not in cached:
        reasons.append('quote not in cached page')
    qi = cached.find(norm(row['quote']))
    window = cached[max(0, qi - 500):qi + len(row['quote']) + 150].lower() if qi >= 0 else ''
    if surname not in window and surname not in cached[:300].lower():
        reasons.append(f'candidate name "{surname}" not within the quote attribution window')
    if reasons:
        return 'FAIL', reasons
    live = live_text(row['url'])
    if live is None:
        return 'CACHED-ONLY', ['live fetch failed']
    if norm(row['quote']) not in live:
        return 'FAIL', ['quote not in live page']
    return 'PASS', []


def controls(rows):
    by = {(r['candidateId'], r['questionId']): r for r in rows}
    zema = by[('presidente-30', 'eco-privatizacao')]
    lula = by[('presidente-13', 'eco-reforma-tributaria')]
    gadelha = by[('senador-151', 'soc-aborto')]
    renan = by[('presidente-14', 'eco-6x1')]
    flavio = by[('presidente-22', 'eco-6x1')]
    lula_file = lula['file']
    return [
        ('ctl-fabricated-plan', dict(lula, quote='Vamos privatizar a Petrobras e todos os bancos públicos.')),
        ('ctl-wrong-page', dict(zema, page=zema['page'] + 1)),
        ('ctl-wrong-candidate', dict(zema, candidateId='presidente-13', file=lula_file)),
        ('ctl-plan-sq-mismatch', dict(zema, candidateId='presidente-13')),
        ('ctl-fabricated-web', dict(gadelha, quote='Eu sou a favor da legalização do aborto')),
        ('ctl-wrong-candidate-web', dict(gadelha, candidateId='senador-222')),
        ('ctl-old-web', dict(gadelha, date='2022-05-01')),
        ('ctl-video-wrong-candidate', dict(renan, candidateId='presidente-70')),
        ('ctl-video-wrong-anchor', dict(renan, anchor='quem comenta é Augusto Curi', alias='Curi', candidateId='presidente-70')),
        ('ctl-video-wrong-timestamp', dict(renan, timestamp='01:40:00')),
        ('ctl-video-interviewer-question', dict(flavio, quote='O senhor é a favor ou é contra essa mudança?')),
        ('ctl-video-interviewer-preamble', dict(flavio, quote='Claro que o setor produtivo diz que o fim da escala 6x1 traria uma série de problemas', timestamp='00:10:52')),
        ('ctl-video-fabricated', dict(flavio, quote='eu sou a favor do fim da escala 6x1')),
    ]


def to_evidence(r, i):
    cand = candidate_row(r['candidateId'])
    if 'video' in r:
        label = f"Vídeo: {r['channel']}, \"{r['title']}\", {r['timestamp']} (legenda automática em português)"
        date = r['date']
    elif 'file' in r:
        label = f"Plano de governo registrado no TSE ({cand['NM_URNA_CANDIDATO']}, p. {r['page']}), arquivo {r['file']} em {r['url'].rsplit('/', 1)[-1]}"
        date = pdf_date(r['file']) or ACCESSED
    else:
        label = f"Reportagem: {r['url'].split('/')[2]}"
        date = r['date']
    ev = dict(id=f"plat-{r['candidateId']}-{r['questionId']}", subject={'type': 'candidate', 'id': r['candidateId']},
              questionId=r['questionId'], kind='platform', position=r['position'], detail=r['detail'], quote=r['quote'],
              date=date, source={'url': r['url'], 'accessed': ACCESSED, 'label': label}, checkId=f'check_platform:{i}')
    if 'page' in r:
        ev['page'] = r['page']
    if 'video' in r:
        ev['timestamp'] = r['timestamp']
    return ev


def main():
    rows = [json.loads(l) for l in open('platform/draft.jsonl')]
    report = {'claims': [], 'controls': []}
    passed = []
    for i, r in enumerate(rows):
        st, why = check(r)
        report['claims'].append(dict(i=i, candidateId=r['candidateId'], questionId=r['questionId'], status=st, reasons=why, quote=r['quote']))
        print(f"{st:11} {r['candidateId']:16} {r['questionId']:24} {'; '.join(why)}")
        if st in ('PASS', 'CACHED-ONLY'):
            passed.append(to_evidence(r, i))
    ctl_ok = True
    for name, r in controls(rows):
        st, why = check(r)
        ok = st == 'FAIL'
        ctl_ok &= ok
        report['controls'].append(dict(name=name, status=st, expectedFail=True, ok=ok, reasons=why))
        print(f"CONTROL {name:26} -> {st} ({'ok' if ok else 'HARNESS BROKEN'}) {'; '.join(why)}")
    report['summary'] = dict(total=len(rows), passed=sum(c['status'] == 'PASS' for c in report['claims']),
                             cachedOnly=sum(c['status'] == 'CACHED-ONLY' for c in report['claims']),
                             failed=sum(c['status'] == 'FAIL' for c in report['claims']), controlsOk=ctl_ok)
    json.dump(report, open('checks/platform.report.json', 'w'), ensure_ascii=False, indent=1)
    if ctl_ok:
        json.dump(passed, open('platform/evidence.json', 'w'), ensure_ascii=False, indent=1)
    print(report['summary'])
    sys.exit(0 if ctl_ok and report['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
