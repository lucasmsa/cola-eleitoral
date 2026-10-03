"""doc-tdd for candidate notices: every source must contain its expected text."""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
YTDLP = ROOT / "pipeline" / ".venv" / "bin" / "yt-dlp"


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def tse_status(src):
    import csv
    raw = (ROOT / src["cache"]).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    for row in csv.DictReader(text.splitlines(), delimiter=";"):
        if row["SQ_CANDIDATO"] == src["sq"]:
            return row["DS_SITUACAO_JULGAMENTO"]
    return ""


def source_text(src):
    if src["kind"] == "tse-status":
        return tse_status(src)
    if src["kind"] == "web":
        out = subprocess.run(["curl", "-sL", "--compressed", "-A", "Mozilla/5.0 (Macintosh) Chrome/128", src["url"]], capture_output=True)
        return html.unescape(re.sub(r"<[^>]+>", " ", out.stdout.decode("utf-8", errors="ignore")))
    if src["kind"] == "yt-title":
        out = subprocess.run([str(YTDLP), "--skip-download", "--print", "%(title)s|%(upload_date)s", src["url"]], capture_output=True, text=True)
        return out.stdout
    raw = (ROOT / src["cache"]).read_bytes().decode("latin-1", errors="ignore")
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def holds(src, expect):
    return norm(expect) in norm(source_text(src))


def main():
    notices = json.loads((ROOT / "pipeline" / "notices.json").read_text())
    rows, ok_ids = [], []
    for n in notices:
        results = [holds(s, s["expect"]) for s in n["sources"]]
        rows.append({"id": n["candidateId"], "status": "PASS" if all(results) else "FAIL", "claim": n["text"]})
        if all(results):
            ok_ids.append(n["candidateId"])
    controls = [
        ("NEG yt title says Lucas Ribeiro deixa disputa", holds(notices[0]["sources"][0], "Lucas Ribeiro deixa disputa")),
        ("NEG law says 30 dias", holds(notices[0]["sources"][1], "até 30 (trinta) dias antes do pleito")),
        ("NEG TSE says DEFERIDO", norm(source_text(notices[0]["sources"][2])) == "deferido"),
        ("NEG JP says Cícero cannot run", holds(notices[1]["sources"][1], "Cícero Lucena não pode concorrer")),
        ("NEG Cícero status INDEFERIDO", norm(source_text(notices[1]["sources"][0])) == "indeferido"),
    ]
    for name, passed in controls:
        rows.append({"id": name, "status": "CONTROL-PASSED" if passed else "FAIL", "claim": name})
    (ROOT / "pipeline" / "checks" / "notices.report.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    if any(p for _, p in controls):
        sys.exit("HARNESS BROKEN")


if __name__ == "__main__":
    main()
