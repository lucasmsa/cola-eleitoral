"""Search cached YouTube auto-captions: text stream with a timestamp for every character offset."""
import html, re
from pathlib import Path
from vtt import lines

YT = Path(__file__).parent / "raw" / "yt"

def norm(s):
    s = html.unescape(s).replace(">>", " ")
    return re.sub(r"\s+", " ", s).strip().lower()

def stream(video_id):
    parts, starts, pos = [], [], 0
    for ts, txt in lines(YT / f"{video_id}.pt-orig.vtt"):
        t = norm(txt) + " "
        parts.append(t)
        starts.append((pos, ts))
        pos += len(t)
    return "".join(parts), starts

def timestamp_at(starts, offset):
    ts = starts[0][1]
    for p, t in starts:
        if p > offset:
            break
        ts = t
    return ts

def find(video_id, quote):
    text, starts = stream(video_id)
    i = text.find(norm(quote))
    return (i, timestamp_at(starts, i), text) if i >= 0 else (-1, None, text)

def meta(video_id):
    for row in (YT / "meta2.txt").read_text(encoding="utf-8").splitlines():
        if row.startswith(video_id + "|"):
            f = row.split("|")
            return {"id": f[0], "title": f[1], "upload": f[2], "channel": f[3]}
    return None
