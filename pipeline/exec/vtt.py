"""Turn YouTube auto-caption VTT into de-duplicated (seconds, text) segments and a flat transcript."""
import re
from pathlib import Path

TS = re.compile(r"(\d+):(\d\d):(\d\d)\.(\d+) --> ")


def segments(path):
    out, last = [], ""
    t = None
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        m = TS.match(line)
        if m:
            h, mi, s, _ = m.groups()
            t = int(h) * 3600 + int(mi) * 60 + int(s)
            continue
        if t is None or not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean != last:
            out.append((t, clean))
            last = clean
    merged, prev = [], ""
    for t, text in out:
        if prev and text.startswith(prev):
            text = text[len(prev):].strip()
        if text:
            merged.append((t, text))
        prev = out[out.index((t, text))][1] if (t, text) in out else prev
    return merged


def transcript(path):
    segs = segments(path)
    words, index = [], []
    for t, text in segs:
        for w in text.split():
            words.append(w)
            index.append(t)
    return words, index


def hms(sec):
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def find(path, phrase, window=60):
    words, index = transcript(path)
    flat = " ".join(words).lower()
    hits = []
    for m in re.finditer(re.escape(phrase.lower()), flat):
        wi = flat[: m.start()].count(" ")
        hits.append((index[wi], " ".join(words[max(0, wi - window): wi + window])))
    return hits
