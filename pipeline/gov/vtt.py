"""Turn a YouTube auto-caption VTT into deduplicated lines with start timestamps."""
import re, sys
from pathlib import Path

def lines(path):
    out, last = [], ""
    ts = None
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d\d:\d\d:\d\d)\.\d+ -->", raw)
        if m:
            ts = m.group(1)
            continue
        txt = re.sub(r"<[^>]+>", "", raw).strip()
        if not txt or txt in ("WEBVTT",) or txt.startswith(("Kind:", "Language:")):
            continue
        if txt == last or (out and out[-1][1].endswith(txt)):
            continue
        last = txt
        out.append((ts, txt))
    return out

def flat(path):
    """Plain text with [hh:mm:ss] markers every line, for searching."""
    return " ".join(f"[{t}] {x}" for t, x in lines(path))

if __name__ == "__main__":
    p = sys.argv[1]
    Path(p).with_suffix(".txt").write_text("\n".join(f"{t} {x}" for t, x in lines(p)), encoding="utf-8")
