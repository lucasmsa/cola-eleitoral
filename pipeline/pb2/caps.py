"""Unified access to cached YouTube captions (original pt track only) across pipeline caches."""
import html
import json
import re
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent
DIRS = [PIPE / "pb2" / "raw" / "yt", PIPE / "gov" / "raw" / "yt", PIPE / "exec" / "raw" / "yt", PIPE / "senate" / "raw" / "yt"]


def _meta_index():
    idx = {}
    for row in (PIPE / "gov" / "raw" / "yt" / "meta2.txt").read_text(encoding="utf-8").splitlines():
        f = row.split("|")
        idx[f[0]] = {"title": f[1], "upload": f[2], "channel": f[3]}
    for row in (PIPE / "exec" / "raw" / "yt" / "meta.txt").read_text(encoding="utf-8").splitlines():
        f = row.split("|")
        if len(f) >= 4:
            idx.setdefault(f[0], {"title": f[2], "upload": f[3], "channel": f[1]})
    for d in (PIPE / "senate" / "raw" / "yt", PIPE / "pb2" / "raw" / "yt"):
        for p in d.glob("*.info.json"):
            info = json.loads(p.read_text())
            idx[info["id"]] = {"title": info.get("title", ""), "upload": info.get("upload_date", ""), "channel": info.get("channel", "")}
    return idx


META = _meta_index()


def vtt_path(video):
    for d in DIRS:
        p = d / f"{video}.pt-orig.vtt"
        if p.exists():
            return p
    return None


def norm(s):
    s = html.unescape(s).replace(">>", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def cues(video):
    out, ts = [], None
    for raw in vtt_path(video).read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d\d):(\d\d):(\d\d)\.\d+ -->", raw)
        if m:
            ts = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            continue
        txt = re.sub(r"<[^>]+>", "", raw).strip()
        if ts is None or not txt or txt.startswith(("WEBVTT", "Kind:", "Language:")):
            continue
        if out and (txt == out[-1][1] or out[-1][1].endswith(txt)):
            continue
        out.append((ts, txt))
    return out


def stream(video):
    parts, starts, pos = [], [], 0
    for ts, txt in cues(video):
        t = norm(txt) + " "
        parts.append(t)
        starts.append((pos, ts))
        pos += len(t)
    return "".join(parts), starts


def ts_at(starts, offset):
    ts = starts[0][1]
    for p, t in starts:
        if p > offset:
            break
        ts = t
    return ts


def hms(sec):
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def videos():
    seen = []
    for d in DIRS:
        for p in d.glob("*.pt-orig.vtt"):
            v = p.name[: -len(".pt-orig.vtt")]
            if v not in seen:
                seen.append(v)
    return seen
