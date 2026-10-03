"""doc-tdd for executive and public-statement evidence on João Azevêdo and Lucas Ribeiro.

Every row in exec/evidence.draft.json lists assertions; a row passes only if all of them hold
against the cached sources (and, for web pages, a live re-fetch when reachable).
Negative controls must FAIL; if one passes, the harness is void and nothing ships.
Writes checks/exec.report.json and exec/evidence.json (PASS rows only).
"""
import csv
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader

PIPE = Path(__file__).resolve().parents[1]
EXEC = PIPE / "exec"
sys.path.insert(0, str(EXEC))
from fetch import path_for, published, UA  # noqa: E402
from vtt import transcript  # noqa: E402
from captxt import hits as txt_hits  # noqa: E402

ROOT = PIPE.parent
HISTORY = PIPE / "raw" / "tse" / "historico_candidatura_2026_BRASIL.csv"
CAND_PB = PIPE / "raw" / "tse" / "consulta_cand_2026_PB.csv"
NORMAS = EXEC / "raw" / "normas_2019_2026.json"
ATA_0704 = EXEC / "raw" / "sapl" / "ata_13_extra_2026.pdf"
HANDOVER = "https://jornaldebrasilia.com.br/brasil-7/juventude-e-energia-nao-inexperiencia-diz-lucas-ribeiro-o-governador-mais-jovem-do-brasil/"
NEAR_WINDOW = 1500


def norm(s):
    s = s.replace("ﬁ ", "fi").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("­", "")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(?<=[a-zà-ú])- (?=[a-zà-ú])", "", s)
    s = s.replace("Nº s", "Nºs").replace("Rati fica", "Ratifica")
    return s.strip()


def html_text(raw):
    s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", s)))


def cached_web(url):
    p = path_for(url)
    if not p.exists():
        return None, None
    raw = p.read_bytes()
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("latin-1")
    return html_text(s), p


def live_web(url):
    with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, "-o", tmp.name, url], check=False)
        data = Path(tmp.name).read_bytes() if r.returncode == 0 else b""
    if len(data) < 2000:
        return None
    return html_text(data.decode("utf-8", errors="ignore"))


_pdf_cache = {}


def pdf_text(path, page=None):
    key = (str(path), page)
    if key not in _pdf_cache:
        r = PdfReader(str(path))
        pages = [r.pages[page - 1]] if page else r.pages
        _pdf_cache[key] = norm(" ".join(p.extract_text() or "" for p in pages))
    return _pdf_cache[key]


def governor_on(date, expect):
    """JOAO: elected governor 2018 and 2022 per TSE history, and the date precedes the 2026-04-02 handover.
    LUCAS: the ALPB minutes of 07/04/2026 call him 'atual Governador' and the date is on or after that."""
    if expect == "JOAO":
        sq = next(r["SQ_CANDIDATO"] for r in csv.DictReader(open(CAND_PB, encoding="latin-1"), delimiter=";")
                  if r["DS_CARGO"] == "SENADOR" and r["NR_CANDIDATO"] == "400")
        won = {int(h["ANO_ELEICAO"]) for h in csv.DictReader(open(HISTORY, encoding="latin-1"), delimiter=";")
               if h["SQ_CANDIDATO_ATUAL"] == sq and h["DS_CARGO"].upper() == "GOVERNADOR" and h["DS_SIT_TOT_TURNO"].startswith("Eleito")}
        handover, _ = cached_web(HANDOVER)
        handover_ok = bool(handover) and "Lucas Ribeiro assumiu o Governo da Paraíba em 2 de abril de 2026, após a renúncia de João Azevêdo" in handover
        return ({2018, 2022} <= won and handover_ok and "2019-01-01" <= date < "2026-04-02",
                f"TSE governor wins {sorted(won)}, handover source {'ok' if handover_ok else 'missing'}")
    ata = pdf_text(ATA_0704)
    ok = "atual Governador Lucas Ribeiro" in ata and "sete de abril do ano de dois mil e vinte e seis" in ata
    return ok and date >= "2026-04-07", "ALPB ata 07/04/2026 'atual Governador Lucas Ribeiro'"


def tokens(s):
    return re.findall(r"[0-9a-záàâãéêíóôõúüç]+", s.lower())


def caption_hits(path, phrase):
    words, index = transcript(path)
    flat, at = [], []
    for w, t in zip(words, index):
        for x in tokens(w):
            flat.append(x)
            at.append(t)
    p = tokens(phrase)
    return [at[k] for k in range(len(flat) - len(p) + 1) if flat[k:k + len(p)] == p]


def video_meta(video_id):
    for line in (EXEC / "raw" / "yt" / "meta.txt").read_text().splitlines():
        parts = line.split("|")
        if len(parts) < 5:
            continue
        vid, channel, title, upload = parts[0], parts[1], "|".join(parts[2:-2]), parts[-2]
        if vid == video_id:
            return {"channel": channel, "title": title, "upload": upload}
    return None


def check_vtt(c):
    """YouTube auto-captions (ASR). Match is token-exact after lowercasing and dropping punctuation;
    no fuzzy matching. The quote keeps the caption wording, stutters included."""
    path = EXEC / c["vtt"]
    hits = [t for t in caption_hits(path, c["contains"]) if abs(t - c["at"]) <= 30]
    if not hits:
        return False, f"caption phrase not found near {c['at']}s"
    t = hits[0]
    for cue in c.get("cues", []):
        lo, hi = cue["within"]
        if not any(lo <= ct - t <= hi for ct in caption_hits(path, cue["phrase"])):
            return False, f"speaker cue '{cue['phrase']}' not within {cue['within']}s"
    meta = video_meta(c["video"])
    if not meta or c["channel"] != meta["channel"] or c["title_contains"] not in meta["title"]:
        return False, f"video metadata mismatch {meta}"
    return True, f"caption at {t}s, {meta['channel']}"


def check_captxt(c):
    """Timestamped auto-caption transcript (one line per caption, 'HH:MM:SS text'). Token-exact match."""
    path = (EXEC / c["captxt"]).resolve()
    hits = [t for t in txt_hits(path, c["contains"]) if abs(t - c["at"]) <= 30]
    if not hits:
        return False, f"caption phrase not found near {c['at']}s"
    t = hits[0]
    for cue in c.get("cues", []):
        lo, hi = cue["within"]
        if not any(lo <= ct - t <= hi for ct in txt_hits(path, cue["phrase"])):
            return False, f"speaker cue '{cue['phrase']}' not within {cue['within']}s"
    line = next((ln for ln in (EXEC / c["meta"]).resolve().read_text().splitlines() if ln.startswith(c["video"] + "|")), "")
    if c["title_contains"] not in line or c["channel"] not in line:
        return False, f"video metadata mismatch for {c['video']}"
    return True, f"caption at {t}s"


def run_check(c, row):
    if "captxt" in c:
        ok, why = check_captxt(c)
        return ok, why, True
    if "file" in c:
        raw = (EXEC / c["file"]).resolve().read_bytes().decode(c.get("encoding", "utf-8"), errors="ignore")
        text = html_text(raw)
        missing = [x for x in c["contains"] if norm(x) not in text]
        return (not missing), ("ok" if not missing else f"not in file: {missing[0][:60]}"), True
    if "vtt" in c:
        ok, why = check_vtt(c)
        return ok, why, True
    if "web" in c:
        text, p = cached_web(c["web"])
        if text is None:
            return False, "not cached", False
        missing = [s for s in c["contains"] if norm(s) not in text]
        if missing:
            return False, f"not in source: {missing[0][:70]}", False
        if "near" in c:
            for s in c["contains"]:
                i = text.find(norm(s))
                window = text[max(0, i - NEAR_WINDOW): i + len(s) + NEAR_WINDOW]
                title = text[:400]
                if not any(n in window or n in title for n in c["near"]):
                    return False, f"attribution {c['near']} not near quote", False
        if "published" in c and published(p) != c["published"]:
            return False, f"published {published(p)} != {c['published']}", False
        live = live_web(c["web"])
        live_ok = live is not None and all(norm(s) in live for s in c["contains"])
        return True, "ok", live_ok
    if "pdf" in c:
        path = (EXEC / c["pdf"]).resolve()
        text = pdf_text(path, c.get("page"))
        missing = [s for s in c["contains"] if norm(s) not in text]
        return (not missing), ("ok" if not missing else f"not in pdf: {missing[0][:70]}"), True
    if "norma" in c:
        n = next((x for x in json.loads(NORMAS.read_text())["results"] if x["numero"] == c["norma"]), None)
        ok = bool(n) and n["data"] == c["data"]
        return ok, ("ok" if ok else f"norma {c['norma']} date {n and n['data']}"), True
    if "governor_on" in c:
        ok, why = governor_on(c["governor_on"], c["expect"])
        return ok, why, True
    return False, "unknown check", False


def evaluate(row):
    reasons, live_all = [], True
    for c in row["checks"]:
        ok, why, live = run_check(c, row)
        if not ok:
            return "FAIL", why, False
        reasons.append(why)
        live_all = live_all and live
    return "PASS", "; ".join(reasons), live_all


def main():
    draft = json.loads((EXEC / "evidence.draft.json").read_text())
    candidates = {c["id"] for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text())}
    questions = {q["id"]: q for q in json.loads((ROOT / "src" / "data" / "questions.json").read_text())}
    questions.update({q["id"]: q for q in draft.get("questions", [])})
    office = {c["id"]: c["office"] for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text())}
    report, shipped = [], []
    for row in draft["rows"]:
        sid, q = row["subject"]["id"], questions.get(row["questionId"])
        if sid not in candidates or not q or office[sid] not in q["offices"]:
            status, why, live = "FAIL", "subject/question/office mismatch", False
        else:
            status, why, live = evaluate(row)
        report.append({"id": row["id"], "status": status, "claim": row["detail"], "why": why, "live": live})
        if status == "PASS":
            shipped.append({k: v for k, v in row.items() if k != "checks"} | {"lowDiscrimination": False})
    for q in draft.get("questions", []):
        status, why, _ = evaluate(q)
        report.append({"id": "question:" + q["id"], "status": status, "claim": q["context"], "why": why})
    bad = []
    for row in draft["controls"]:
        status, why, _ = evaluate(row)
        report.append({"id": row["id"], "status": "CONTROL-" + ("FAIL(ok)" if status == "FAIL" else "PASSED(BROKEN)"), "claim": row["id"], "why": why})
        if status == "PASS":
            bad.append(row["id"])
    out = {"harness_ok": not bad, "rows": report}
    (PIPE / "checks" / "exec.report.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for r in report:
        print(f"{r['status']:<22} {r['id']:<62} {r.get('why','')[:90]}")
    passed = sum(r["status"] == "PASS" for r in report)
    print(f"PASS {passed}  FAIL {sum(r['status'] == 'FAIL' for r in report)}  controls broken {len(bad)}")
    failed_q = [r["id"] for r in report if r["id"].startswith("question:") and r["status"] != "PASS"]
    if bad:
        print("HARNESS BROKEN, nothing written")
        sys.exit(1)
    if failed_q:
        print("question context failed, its rows are withheld:", failed_q)
        shipped = [e for e in shipped if "question:" + e["questionId"] not in failed_q]
    (EXEC / "evidence.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
