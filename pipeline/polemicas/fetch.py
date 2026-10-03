"""Fetch a URL into raw/web with a stable name and print normalized text around keywords."""
import hashlib
import html
import re
import subprocess
import sys
from pathlib import Path

RAW = Path(__file__).parent / "raw" / "web"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"


def path_for(url):
    return RAW / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".html")


def fetch(url, force=False):
    RAW.mkdir(parents=True, exist_ok=True)
    p = path_for(url)
    if force or not p.exists() or p.stat().st_size < 3000:
        subprocess.run(["curl", "-sL", "--compressed", "--max-time", "40", "-A", UA, "-o", str(p), url], check=False)
    return p


def text_of(p):
    raw = p.read_bytes()
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("latin-1")
    s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s)


if __name__ == "__main__":
    url = sys.argv[1]
    keys = sys.argv[2:]
    p = fetch(url)
    t = text_of(p)
    print(p.name, p.stat().st_size, "chars", len(t))
    for k in keys:
        for m in list(re.finditer(re.escape(k), t, re.I))[:3]:
            print(f"--[{k}]--", t[max(0, m.start() - 300): m.end() + 400])
