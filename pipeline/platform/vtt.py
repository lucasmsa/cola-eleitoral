import re, sys, json
def cues(path):
    """Auto-caption VTT -> list of (seconds, new_text) without rolling duplicates."""
    out, prev = [], ''
    blocks = open(path).read().split('\n\n')
    for b in blocks:
        m = re.search(r'(\d+):(\d+):(\d+)\.\d+ -->', b)
        if not m: continue
        s = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3))
        lines = [re.sub(r'<[^>]+>', '', l).strip() for l in b.split('\n')[1:]]
        lines = [l for l in lines if l and '-->' not in l]
        for l in lines:
            if l == prev or (out and l == out[-1][1]): continue
            out.append((s, l)); prev = l
    # drop lines that are prefix-repeats of previous line
    clean = []
    for s, l in out:
        if clean and clean[-1][1] == l: continue
        clean.append((s, l))
    return clean
def flat(path):
    cs = cues(path); text = ''; idx = []
    for s, l in cs:
        idx.append((len(text), s)); text += l + ' '
    return re.sub(r'\s+', ' ', text).strip(), idx
def ts_at(idx, pos):
    s = 0
    for p, t in idx:
        if p > pos: break
        s = t
    return f'{s//3600:02d}:{s%3600//60:02d}:{s%60:02d}'
if __name__ == '__main__':
    t, idx = flat(sys.argv[1]); open(sys.argv[2], 'w').write(t); json.dump(idx, open(sys.argv[2] + '.idx.json', 'w'))
    print(len(t))
