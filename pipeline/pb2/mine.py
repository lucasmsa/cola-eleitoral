"""python3 mine.py <title-regex> <keyword-regex> [window]: print caption windows around keywords in matching videos."""
import re
import sys
from caps import META, hms, stream, ts_at, videos

title_rx, kw_rx = re.compile(sys.argv[1], re.I), re.compile(sys.argv[2], re.I)
win = int(sys.argv[3]) if len(sys.argv) > 3 else 500
for v in videos():
    m = META.get(v, {})
    if not title_rx.search(m.get("title", "") + " " + v):
        continue
    text, starts = stream(v)
    hits = list(kw_rx.finditer(text))
    if not hits:
        continue
    print(f"\n######## {v} | {m.get('title','')} | {m.get('upload','')} | hits={len(hits)}")
    last = -10**9
    for h in hits:
        if h.start() - last < win:
            continue
        last = h.start()
        print(f"--[{hms(ts_at(starts, h.start()))}] ...{text[max(0, h.start()-win): h.end()+win]}...")
