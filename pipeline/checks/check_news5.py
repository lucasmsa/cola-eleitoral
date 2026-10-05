"""doc-tdd for pipeline/news5: 2nd-round scenario polls, endorsements and new finalist statements.

Every number, quote and attribution is re-derived from the cached source page (and live with --live).
Writes pipeline/checks/news5.report.json with rows {id, status, claim}.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N5 = ROOT / "pipeline" / "news5"
RAW = N5 / "raw"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"
CACHE = {
    "lula-tem-45-e-flavio-42": "datafolha.html",
    "atlasintel-presidente-outubro-2026": "atlasintel.html",
    "cury-caiado-renan-santos": "midiamax.html",
    "o-que-farao-cury-renan": "em-2turno.html",
    "zema-faz-aceno-a-flavio": "zema-maio.html",
    "fim-da-era-do-pt": "flavio-fim-era.html",
}
LIVE = "--live" in sys.argv
_live = {}


def clean(raw):
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def cached_text(url):
    for key, name in CACHE.items():
        if key in url:
            return clean((RAW / name).read_bytes().decode("utf-8", errors="ignore"))
    raise KeyError(f"no cache for {url}")


def live_text(url):
    if url not in _live:
        out = subprocess.run(["curl", "-sL", "--compressed", "--max-time", "60", "-A", UA, url], capture_output=True)
        _live[url] = clean(out.stdout.decode("utf-8", errors="ignore"))
    return _live[url]


def texts(url):
    yield "cached", cached_text(url)
    if LIVE:
        yield "live", live_text(url)


def pct_forms(pct):
    s = f"{pct}".replace(".", ",")
    if float(pct).is_integer():
        s = str(int(pct))
    return [rf"\(PT\): {re.escape(s)}%", rf"\(PL\): {re.escape(s)}%", rf"{re.escape(s)}%"]


def poll_rows(polls):
    rows = []
    for p in polls:
        url = p["source"]["url"]
        for mode, t in texts(url):
            n = norm(t)
            ok_round = bool(re.search(r"(2º turno|segundo turno)", t, re.I))
            ok_meta = p["registration"].lower() in n and f"{p['sample']:,}".replace(",", ".") in t
            margin = "2 pontos" if p["marginPp"] == 2.0 else "1 ponto"
            ok_meta = ok_meta and margin in t
            rows.append((f"{p['id']}:meta:{mode}", ok_round and ok_meta, f"{p['institute']} registro {p['registration']}, n={p['sample']}, margem {p['marginPp']}"))
            block = round2_block(t)
            for r in p["results"]:
                label = r["label"]
                name = {"Lula": r"Lula \(PT\)", "Flávio Bolsonaro": r"Flávio Bolsonaro \(PL\)"}.get(label, re.escape(label))
                s = (f"{r['pct']}".replace(".", ",") if not float(r["pct"]).is_integer() else str(int(r["pct"])))
                ok = bool(re.search(rf"{name}:? {re.escape(s)}%", block))
                rows.append((f"{p['id']}:{label}:{mode}", ok, f"{label} {r['pct']}% no cenário de 2º turno ({p['institute']})"))
    return rows


def round2_block(t):
    starts = [m.start() for m in re.finditer(r"(2º TURNO O levantamento|simulação de segundo turno|Segundo turno para presidente pela AtlasIntel)", t)]
    return " ".join(t[i: i + 600] for i in starts)


def claim_rows(endorsements):
    rows = []
    for e in endorsements:
        for c in e["claims"]:
            for mode, t in texts(c["source"]["url"]):
                ok = norm(c["support"]) in norm(t)
                rows.append((f"{c['checkId']}:{mode}", ok, c["text"]))
    return rows


def evidence_rows(evidence):
    rows = []
    for e in evidence:
        for mode, t in texts(e["source"]["url"]):
            n = norm(t)
            q = norm(e["quote"])
            i = n.find(q)
            window = n[max(0, i - 400): i]
            ok = i >= 0 and ("flávio" in window or "candidato do pl" in window) and "4.out.2026" in t
            rows.append((f"{e['id']}:{mode}", ok, e["detail"]))
    return rows


def controls(polls, endorsements, evidence):
    df = json.loads(json.dumps(polls[0]))
    df["results"][0]["pct"] = 46
    wrong_reg = json.loads(json.dumps(polls[1]))
    wrong_reg["registration"] = "BR-01709/2026"
    cury = json.loads(json.dumps(endorsements[0]))
    cury["claims"][0]["support"] = "Eu declaro apoio a Lula no segundo turno"
    renan = json.loads(json.dumps(endorsements[1]))
    renan["claims"][0]["support"] = "anunciou apoio a Flávio Bolsonaro"
    zema = json.loads(json.dumps(endorsements[3]))
    zema["claims"][1]["source"]["url"] = endorsements[0]["claims"][0]["source"]["url"]
    flav = json.loads(json.dumps(evidence[0]))
    flav["quote"] = "Eu sou contra o fim da reeleição."
    return [
        ("NEG Datafolha Lula 46% no 2º turno", any(ok for i, ok, _ in poll_rows([df]) if ":Lula:" in i)),
        ("NEG AtlasIntel registro BR-01709/2026", all(ok for i, ok, _ in poll_rows([wrong_reg]) if ":meta:" in i)),
        ("NEG Cury declarou apoio a Lula", all(ok for _, ok, _ in claim_rows([cury]))),
        ("NEG Renan anunciou apoio a Flávio", all(ok for _, ok, _ in claim_rows([renan]))),
        ("NEG quote de Zema atribuída ao Midiamax", all(ok for i, ok, _ in claim_rows([zema]) if "zema-2" in i)),
        ("NEG Flávio contra o fim da reeleição", all(ok for _, ok, _ in evidence_rows([flav]))),
    ]


def main():
    polls = json.loads((N5 / "polls2.json").read_text())
    endorsements = json.loads((N5 / "endorsements.json").read_text())
    evidence = json.loads((N5 / "evidence.json").read_text())
    rows = poll_rows(polls) + claim_rows(endorsements) + evidence_rows(evidence)
    report = []
    ids_ok = {}
    for rid, ok, claim in rows:
        base = rid.rsplit(":", 1)[0]
        ids_ok[base] = ids_ok.get(base, True) and ok
        if not ok:
            print("FAIL", rid, claim)
    for base, ok in ids_ok.items():
        report.append({"id": base, "status": "PASS" if ok else "FAIL", "claim": base})
    for c in (e["claims"] for e in endorsements):
        for cl in c:
            report.append({"id": cl["checkId"], "status": "PASS" if ids_ok.get(cl["checkId"]) else "FAIL", "claim": cl["text"]})
    for e in evidence:
        report.append({"id": e["id"], "status": "PASS" if ids_ok.get(e["id"]) else "FAIL", "claim": e["detail"]})
    for p in polls:
        ok = all(v for k, v in ids_ok.items() if k.startswith(p["id"] + ":"))
        report.append({"id": p["id"], "status": "PASS" if ok else "FAIL", "claim": p["institute"]})
    ctl = controls(polls, endorsements, evidence)
    broken = [name for name, passed in ctl if passed]
    for name, passed in ctl:
        report.append({"id": name, "status": "CONTROL-PASSED" if passed else "FAIL", "claim": name})
        print("CONTROL", "BROKEN" if passed else "FAIL (ok)", name)
    (ROOT / "pipeline" / "checks" / "news5.report.json").write_text(json.dumps({"harness_ok": not broken, "rows": report}, ensure_ascii=False, indent=1))
    fails = [k for k, v in ids_ok.items() if not v]
    print(f"rows={len(ids_ok)} PASS={sum(ids_ok.values())} FAIL={len(fails)} controls={len(ctl)} broken={len(broken)} live={LIVE}")
    if broken:
        sys.exit("HARNESS BROKEN")


if __name__ == "__main__":
    main()
