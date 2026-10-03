"""Fetch-and-cache plus snippet search for explainer sources."""
import hashlib
import html
import re
import subprocess
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"


def key(url):
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def to_text(raw):
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>|</div>", "\n", raw)
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    t = re.sub(r"[ \t\r\f\v ]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)


def decode(b):
    for enc in ("utf-8", "cp1252"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            pass
    return b.decode("latin-1", errors="ignore")


def fetch(url, force=False):
    RAW.mkdir(exist_ok=True)
    k = key(url)
    h, t = RAW / f"{k}.html", RAW / f"{k}.txt"
    if force or not t.exists() or t.stat().st_size < 500:
        subprocess.run(["curl", "-sL", "--compressed", "--max-time", "40", "-A", UA, "-o", str(h), url], check=False)
        b = h.read_bytes() if h.exists() else b""
        if url.lower().endswith(".pdf") or b[:4] == b"%PDF":
            out = subprocess.run([str(Path(__file__).resolve().parent.parent / ".venv" / "bin" / "python"), "-c",
                                  "import sys,pypdf;r=pypdf.PdfReader(sys.argv[1]);print('\\n'.join((p.extract_text() or '') for p in r.pages))", str(h)],
                                 capture_output=True, text=True)
            t.write_text(out.stdout)
        else:
            t.write_text(to_text(decode(b)))
    return t.read_text()


def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def find(url, *words, width=320):
    t = re.sub(r"\s+", " ", fetch(url))
    hits = 0
    for m in re.finditer(re.escape(words[0]), t, re.I):
        w = t[max(0, m.start() - width): m.end() + width]
        if all(x.lower() in w.lower() for x in words[1:]):
            print("...", w, "...\n")
            hits += 1
            if hits >= 4:
                break
    if not hits:
        print("NO HIT", words, "len", len(t))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fetch":
        for u in sys.argv[2:]:
            t = fetch(u)
            print(len(t), u)
    elif cmd == "find":
        find(sys.argv[2], *sys.argv[3:])
    elif cmd == "show":
        t = fetch(sys.argv[2])
        a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        print(t[a:a + 6000])


def body(url, minlen=70, limit=12000):
    lines = [l.strip() for l in fetch(url).split("\n")]
    out = "\n".join(l for l in lines if len(l) >= minlen)
    return out[:limit]
