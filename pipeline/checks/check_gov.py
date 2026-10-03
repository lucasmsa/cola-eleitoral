"""doc-tdd for governor-race evidence (pipeline/gov). Re-derives every row from cached sources; live re-fetch for web pages
and the Câmara API. Negative controls must FAIL. Writes checks/gov.report.json and gov/evidence.json (PASS rows only).
Captions are YouTube auto-captions (ASR): a quote passes on an exact match after lowercasing and collapsing whitespace."""
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / "pipeline" / "gov"
sys.path.insert(0, str(GOV))
import captions  # noqa: E402
import fetch  # noqa: E402
from draft import ACCESSED, ROWS  # noqa: E402

WINDOW = 1500
TURN = 400
CANDIDATES = {c["id"]: c for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text())}
QUESTIONS = {q["id"]: q for q in json.loads((ROOT / "src" / "data" / "questions.json").read_text())}
SHIPPED = json.loads((ROOT / "src" / "data" / "evidence.json").read_text())


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def published(path):
    raw = path.read_bytes().decode("utf-8", errors="ignore")
    m = re.search(r'"datePublished":"(\d{4}-\d{2}-\d{2})', raw) or re.search(r'published_time" content="(\d{4}-\d{2}-\d{2})', raw)
    if m:
        return m.group(1)
    m = re.search(r"Publicado em (\d{2})/(\d{2})/(\d{4})", fetch.text_of(path))
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def check_camara_vote(row, live):
    c = row["check"]
    votos = json.loads((GOV / c["votos"]).read_text())["dados"]
    if live:
        out = subprocess.run(["curl", "-s", "-H", "Accept: application/json", row["source"]["url"]], capture_output=True, text=True).stdout
        votos = json.loads(out)["dados"]
    mine = [v for v in votos if v["deputado_"]["id"] == c["deputadoId"]]
    if not mine:
        return False, "deputy not in roll call"
    if mine[0]["tipoVoto"] != c["expect"]:
        return False, f"source says {mine[0]['tipoVoto']}"
    page = fetch.text_of(fetch.fetch(c["direction"]["page"], force=live))
    if norm(c["direction"]["text"]) not in norm(page):
        return False, "direction text not in Agência Câmara page"
    return True, ""


def check_web_quote(row, live):
    p = fetch.fetch(row["source"]["url"], force=live)
    text = norm(fetch.text_of(p))
    i = text.find(norm(row["quote"]))
    if i < 0:
        return False, "quote not in page"
    if norm(row["check"]["anchor"]) not in text[max(0, i - WINDOW): i + len(row["quote"]) + 200]:
        return False, "speaker not in attribution window"
    pub = published(p)
    if not pub or pub < row["check"]["minDate"] or pub[:10] != row["date"]:
        return False, f"publish date {pub} != {row['date']} or too old"
    return True, ""


def check_yt_quote(row, _live):
    c = row["check"]
    meta = captions.meta(c["video"])
    if not meta:
        return False, "no video metadata"
    if c["title"].lower() not in meta["title"].lower():
        return False, "title mismatch"
    if "upload" in c and meta["upload"] != c["upload"]:
        return False, f"upload {meta['upload']} != {c['upload']}"
    i, ts, text = captions.find(c["video"], row["quote"])
    if i < 0:
        return False, "quote not in captions"
    surname = norm(CANDIDATES[row["subject"]]["ballotName"]).split()[0]
    if c["mode"] == "interview":
        if surname not in norm(meta["title"]):
            return False, f"interview title does not name {surname}"
        if norm(c["anchor"]) not in text[max(0, i - TURN): i]:
            return False, "interviewer question not right before the answer"
    else:
        cue = text[max(0, i - WINDOW): i]
        if norm(c["anchor"]) not in cue or surname not in norm(c["anchor"]):
            return False, "moderator cue naming the speaker not in window before quote"
    if ts not in row["source"]["label"] or str(captions_seconds(ts)) + "s" not in row["source"]["url"]:
        return False, f"timestamp {ts} not in source label/url"
    return True, f"ASR match at {ts}"


def captions_seconds(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


def check_pdf_text(row, _live):
    from pypdf import PdfReader
    c = row["check"]
    reader = PdfReader(str(GOV / c["pdf"]))
    for page, needle in c["pages"].items():
        if norm(needle) not in norm(reader.pages[page - 1].extract_text() or ""):
            return False, f"text not on page {page}"
    if c["creation"] not in str(reader.metadata.get("/CreationDate", "")):
        return False, "creation date mismatch"
    if c["creation"][:4] + "-" + c["creation"][4:6] + "-" + c["creation"][6:] != row["date"]:
        return False, "row date != PDF creation date"
    t = c["tenure"]
    years = sorted(e["year"] for e in CANDIDATES[row["subject"]]["elected"] if e["office"] == t["office"] and e["place"] == t["place"])
    if not set(t["years"]) <= set(years):
        return False, "TSE history does not show the tenure"
    if not (t["years"][0] < int(c["creation"][:4]) <= t["years"][-1] + 4):
        return False, "document outside tenure"
    return True, ""


CHECKS = {"camara_vote": check_camara_vote, "web_quote": check_web_quote, "yt_quote": check_yt_quote, "pdf_text": check_pdf_text}


def common(row):
    cand = CANDIDATES.get(row["subject"])
    q = QUESTIONS.get(row["questionId"])
    if not cand or cand["office"] != "governador":
        return False, "subject is not a governor candidate"
    if not q or "governador" not in q["offices"]:
        return False, "question does not apply to governador"
    if row["position"] not in (-1, 0, 1):
        return False, "bad position"
    if "quote" in row and len(row["quote"]) > 300:
        return False, "quote over 300 chars"
    for e in SHIPPED:
        if e["subject"]["id"] == row["subject"] and e["questionId"] == row["questionId"] and e.get("quote") == row.get("quote") and e["kind"] == row["kind"]:
            return False, "duplicate of shipped evidence"
    return True, ""


def run(row, live=False):
    ok, why = common(row)
    if not ok:
        return ok, why
    return CHECKS[row["check"]["type"]](row, live)


def controls():
    by_id = {r["id"]: r for r in ROWS}
    out = []
    c1 = deepcopy(by_id["gov-governador-22-seg-armas-cd2209381-100"]); c1["check"]["expect"] = "Não"
    out.append(("NEG Efraim voted NÃO on PL 3723/2019", c1))
    c2 = deepcopy(by_id["gov-governador-15-pb-concessoes-ppp-98fm-2026-09-28"]); c2["quote"] = "eu sou contra o aborto e contra o leilão"
    out.append(("NEG fabricated Cícero quote in 98 FM captions", c2))
    c3 = deepcopy(by_id["gov-governador-29-soc-aborto-sofesta-2026-08-25"]); c3["subject"] = "governador-80"; c3["check"]["anchor"] = "yuri"
    out.append(("NEG Camilo's abortion quote attributed to Yuri", c3))
    c4 = deepcopy(by_id["gov-governador-15-eco-privatizacao-jp-2026-02-05"]); c4["date"] = "2024-02-05"
    out.append(("NEG Cícero Cagepa quote with tampered date", c4))
    c5 = deepcopy(by_id["gov-governador-15-pb-concessoes-ppp-etp-cemiterios"]); c5["subject"] = "governador-22"
    out.append(("NEG cemetery concession study attributed to Efraim's tenure", c5))
    return out


def main():
    live = "--live" in sys.argv
    report, shipped = [], []
    for row in ROWS:
        ok, why = run(row, live)
        report.append({"id": row["id"], "status": "PASS" if ok else "FAIL", "claim": row.get("quote") or row["detail"], "note": why})
        if ok:
            e = {k: v for k, v in row.items() if k not in ("check", "subject")}
            e["subject"] = {"type": "candidate", "id": row["subject"]}
            e["source"] = {**row["source"], "accessed": ACCESSED}
            e["checkId"] = row["id"]
            e["lowDiscrimination"] = False
            shipped.append(e)
    ctl = []
    for name, row in controls():
        ok, why = run(row, live)
        ctl.append({"id": name, "status": "CONTROL-PASSED" if ok else "FAIL", "note": why})
    harness_ok = all(c["status"] == "FAIL" for c in ctl)
    (ROOT / "pipeline" / "checks" / "gov.report.json").write_text(json.dumps({"rows": report, "controls": ctl, "harness_ok": harness_ok}, ensure_ascii=False, indent=1))
    for r in report:
        print(r["status"], r["id"], r["note"])
    for c in ctl:
        print("CONTROL", c["status"], c["id"], c["note"])
    print(f"PASS={sum(r['status'] == 'PASS' for r in report)}/{len(report)} harness_ok={harness_ok} live={live}")
    if not harness_ok:
        sys.exit(1)
    (GOV / "evidence.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
