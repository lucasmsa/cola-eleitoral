"""Timestamped transcript lines ('HH:MM:SS text') from pipeline/gov/raw/yt/*.txt -> token stream with times."""
import re
from pathlib import Path

TOK = re.compile(r"[0-9a-záàâãéêíóôõúüç]+")


def stream(path):
    flat, at = [], []
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"(\d\d):(\d\d):(\d\d) (.*)", line)
        if not m:
            continue
        t = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
        for w in TOK.findall(m[4].replace("&gt;", " ").lower()):
            flat.append(w)
            at.append(t)
    return flat, at


def hits(path, phrase):
    flat, at = stream(path)
    p = TOK.findall(phrase.lower())
    return [at[k] for k in range(len(flat) - len(p) + 1) if flat[k:k + len(p)] == p]
