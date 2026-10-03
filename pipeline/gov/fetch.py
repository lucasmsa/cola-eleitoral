"""Cache a web page under raw/ and print its text window around keywords."""
import hashlib, html, re, subprocess, sys
from pathlib import Path
RAW = Path(__file__).parent / "raw"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"

def path_for(url):
    slug = re.sub(r"[^a-z0-9]+", "_", url.lower())[-80:]
    return RAW / f"{slug}_{hashlib.md5(url.encode()).hexdigest()[:8]}.html"

def fetch(url, force=False):
    p = path_for(url)
    if force or not p.exists() or p.stat().st_size < 1500:
        subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, "-o", str(p), url], check=False)
    return p

def text_of(p):
    raw = p.read_bytes()
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("windows-1252", errors="ignore")
    s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))

def title_of(p):
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", p.read_bytes().decode("utf-8", errors="ignore"))
    return html.unescape(m.group(1)).strip() if m else ""

if __name__ == "__main__":
    url, kws = sys.argv[1], sys.argv[2:]
    p = fetch(url)
    t = text_of(p)
    print(p.name, len(t), "|", title_of(p))
    for kw in kws:
        for m in list(re.finditer(kw, t, re.I))[:4]:
            print(f"--[{kw}]", t[max(0, m.start()-300): m.end()+400])
