"""Fetch and cache country sources; text() returns whitespace-normalized plain text."""
import hashlib
import html
import re
import subprocess
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def cache_path(url):
    h = hashlib.sha1(url.encode()).hexdigest()[:12]
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("//", 1)[-1])[:80]
    return RAW / f"{slug}_{h}"


def fetch(url, refresh=False):
    p = cache_path(url)
    if refresh or not p.exists() or p.stat().st_size < 500:
        subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, "-o", str(p), url], check=False)
    return p


def pdf_text(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join((pg.extract_text() or "") for pg in pdf.pages)


def raw_text(path):
    b = Path(path).read_bytes()
    if b[:4] == b"%PDF":
        return pdf_text(path)
    for enc in ("utf-8", "latin-1"):
        try:
            s = b.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def norm(s):
    s = s.replace("­", "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def text(url, refresh=False):
    return norm(raw_text(fetch(url, refresh)))
