"""doc-tdd for candidate profiles: every Claim is re-derived from its primary source.

Writes pipeline/checks/profiles.report.json and pipeline/profiles/profiles.json (PASS claims only).
--live re-downloads the TSE plan zips and re-extracts a sample of quoted pages.
"""
import copy
import csv
import html
import io
import json
import random
import re
import subprocess
import sys
import unicodedata
import zipfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PIPE = ROOT / "pipeline"
TSE = PIPE / "raw" / "tse"
RAW = PIPE / "profiles" / "raw"
PLANS = PIPE / "raw" / "plans"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip().casefold()


def read_csv(path, encoding):
    with open(path, encoding=encoding, newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


@lru_cache(None)
def cand26():
    out = {}
    for uf in ("BR", "PB"):
        for r in read_csv(TSE / f"consulta_cand_2026_{uf}.csv", "latin-1"):
            out[r["SQ_CANDIDATO"]] = r
    return out


@lru_cache(None)
def hist():
    out = defaultdict(list)
    for h in read_csv(TSE / "historico_candidatura_2026_BRASIL.csv", "latin-1"):
        out[h["SQ_CANDIDATO_ATUAL"]].append(h)
    return out


@lru_cache(None)
def votes2022():
    out = defaultdict(int)
    for v in read_csv(RAW / "votacao_candidato_munzona_2022_PB.csv", "latin-1"):
        if v["NR_TURNO"] == "1":
            out[v["SQ_CANDIDATO"]] += int(v["QT_VOTOS_NOMINAIS"])
    return out


@lru_cache(None)
def pdf_page(file, page, data=None):
    reader = PdfReader(io.BytesIO(data) if data else str(PLANS / file))
    return reader.pages[page - 1].extract_text() or ""


@lru_cache(None)
def cached_page_text(file, page):
    p = PIPE / "platform" / "text" / f"{file}.p{page}.txt"
    return p.read_text(errors="ignore") if p.exists() else ""


@lru_cache(None)
def live_zip(uf):
    url = f"https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_{uf}.zip"
    data = subprocess.run(["curl", "-sL", "--max-time", "180", url], capture_output=True).stdout
    return zipfile.ZipFile(io.BytesIO(data))


@lru_cache(None)
def evidence_index():
    ev = {e["id"]: e for e in json.loads((ROOT / "src" / "data" / "evidence.json").read_text())}
    passed = set()
    for rep in (PIPE / "checks").glob("*.report.json"):
        if rep.name == "profiles.report.json":
            continue
        data = json.loads(rep.read_text())
        rows = data if isinstance(data, list) else next((data[k] for k in ("rows", "claims") if isinstance(data.get(k), list)), [])
        for r in rows:
            if str(r.get("status", "")).upper() == "PASS":
                passed.add(r.get("id") or (r.get("candidateId"), r.get("questionId"), r.get("quote")))
    return ev, passed


@lru_cache(None)
def senado_mandates(code, live=False):
    path = RAW / f"senador_{code}_mandatos.json"
    if live:
        data = subprocess.run(["curl", "-s", "--max-time", "60",
                               f"https://legis.senado.leg.br/dadosabertos/senador/{code}/mandatos.json"], capture_output=True).stdout
        return json.loads(data)
    return json.loads(path.read_text())


@lru_cache(None)
def web_text(url):
    path = RAW / (re.sub(r"[^a-z0-9]+", "_", url.lower())[-100:] + ".html")
    if not path.exists() or path.stat().st_size < 2000:
        subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, "-o", str(path), url], check=False)
    raw = path.read_bytes().decode("utf-8", errors="ignore")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return html.unescape(re.sub(r"<[^>]+>", " ", raw))


def check(claim, cand_by_id, live=False):
    spec, sup = claim["_check"], norm(claim["support"])
    kind = spec["kind"]
    if kind == "pdf":
        if norm(spec["quote"]) != sup or (claim["text"].startswith("“") and sup not in norm(claim["text"])):
            return False, "support differs from quote or displayed text"
        cached, fresh = norm(cached_page_text(spec["file"], spec["page"])), norm(pdf_page(spec["file"], spec["page"]))
        if sup not in fresh:
            return False, f"quote not on PDF page {spec['page']}"
        if cached and sup not in cached:
            return False, "quote not in cached page text"
        if live:
            uf = "BR" if spec["file"].startswith("2026BR") else "PB"
            names = [n for n in live_zip(uf).namelist() if n.endswith(spec["file"])]
            if not names:
                return False, "plan file missing from live TSE zip"
            if sup not in norm(pdf_page(spec["file"], spec["page"], live_zip(uf).read(names[0]))):
                return False, "quote not in live TSE plan"
        return True, "pdf ok" + (" + live" if live else "")
    if kind == "tse-cand":
        row = cand26().get(spec["sq"])
        if not row:
            return False, "SQ not in TSE 2026 file"
        ok = row[spec["field"]].strip() == spec["value"] and norm(spec["value"]) in norm(claim["text"])
        return ok, f"{spec['field']}={row[spec['field']].strip()!r}"
    if kind == "tse-hist":
        for h in hist().get(spec["sq"], []):
            if (h["ANO_ELEICAO"], h["DS_CARGO"].strip(), h["DS_SIT_TOT_TURNO"].strip(), h["SG_PARTIDO"].strip()) == (
                    spec["ano"], spec["cargo"], spec["result"], spec["partido"]):
                ok = spec["ano"] in claim["text"] and spec["cargo"].lower() in claim["text"]
                return ok, "history row found"
        return False, "no TSE history row with that year, office, result and party"
    if kind == "tse-votes2022":
        total = votes2022().get(spec["sq2022"])
        shown = int(re.sub(r"\D", "", re.search(r"recebeu ([\d.]+)", claim["text"]).group(1)))
        ok = total == spec["total"] == int(claim["support"]) == shown
        return ok, f"TSE sum {total}"
    if kind == "evidence":
        ev, passed = evidence_index()
        e = ev.get(spec["evidenceId"])
        if not e:
            return False, "evidence row not shipped"
        key_ok = e["id"] in passed or e["checkId"] in passed or (e["subject"]["id"], e["questionId"], e.get("quote")) in passed
        return key_ok and norm(e.get("quote") or "") == sup, "evidence row PASS in its stream" if key_ok else "evidence row not PASS"
    if kind == "notice":
        rep = json.loads((PIPE / "checks" / "notices.report.json").read_text())
        ok = any(r["id"] == claim["checkId"].split("-presents")[0].replace("prof-", "") and r["status"] == "PASS" for r in rep)
        return ok, "notice PASS"
    if kind == "web":
        return sup in norm(web_text(spec["url"])), "web page text"
    if kind == "web-block":
        t = re.sub(r"\s+", " ", web_text(spec["url"]))
        i = t.find(spec["start"])
        if i < 0:
            return False, "candidate block not found"
        block = t[i:t.find(spec["end"], i)]
        return sup in norm(block), "inside the candidate's own block"
    if kind == "senado-api":
        d = senado_mandates(spec["code"], live)
        parl = d["MandatoParlamentar"]["Parlamentar"]
        mand = parl["Mandatos"]["Mandato"]
        for m in (mand if isinstance(mand, list) else [mand]):
            ex = m["Exercicios"]["Exercicio"]
            ex = ex if isinstance(ex, list) else [ex]
            for e in ex:
                ok = (m["UfParlamentar"] == spec["uf"] and e["DataInicio"] == spec["start"]
                      and (spec.get("end") is None or m["SegundaLegislaturaDoMandato"]["DataFim"] == spec["end"])
                      and (spec.get("exerciseEnd") is None or e.get("DataFim") == spec["exerciseEnd"])
                      and (spec.get("cause") is None or e.get("DescricaoCausaAfastamento") == spec["cause"]))
                if ok:
                    return True, "Senado API mandate matches" + (" (live)" if live else "")
        return False, "no Senado mandate/exercise with those dates"
    return False, f"unknown kind {kind}"


def controls(profiles):
    flat = {c["checkId"]: c for p in profiles for f in ("presents", "experience", "proposals") for c in p[f]}
    out = []
    votes = next(c for c in flat.values() if c["_check"]["kind"] == "tse-votes2022")
    bad = copy.deepcopy(votes)
    bad["_check"]["total"] += 1000
    bad["support"] = str(bad["_check"]["total"])
    bad["text"] = re.sub(r"recebeu [\d.]+", f"recebeu {bad['_check']['total']:,}".replace(",", "."), bad["text"])
    out.append(("NEG wrong 2022 vote total", bad))
    slogan = copy.deepcopy(next(c for c in flat.values() if c["support"] == "Muito pra mostrar Nada pra esconder"))
    slogan["_check"]["file"] = "2026BR280002542548_01.pdf"
    out.append(("NEG Caiado slogan attributed to Lula's plan", slogan))
    year = copy.deepcopy(next(c for c in flat.values() if c["_check"]["kind"] == "tse-hist" and c["checkId"].startswith("prof-governador-22")))
    year["_check"]["ano"] = str(int(year["_check"]["ano"]) - 1)
    year["text"] = year["text"].replace(year["text"][:4], year["_check"]["ano"])
    out.append(("NEG Efraim elected one year earlier", year))
    fake = copy.deepcopy(next(c for c in flat.values() if c["checkId"].startswith("prof-presidente-22-proposals")))
    fake["support"] = fake["_check"]["quote"] = "Vamos privatizar a Petrobras nos primeiros 100 dias de governo."
    fake["text"] = f"“{fake['support']}”"
    out.append(("NEG fabricated Flávio plan quote", fake))
    page = copy.deepcopy(next(c for c in flat.values() if c["checkId"].startswith("prof-presidente-13-proposals")))
    page["_check"]["page"] += 1
    out.append(("NEG Lula quote on the wrong page", page))
    occ = copy.deepcopy(next(c for c in flat.values() if c["_check"].get("field") == "DS_OCUPACAO"))
    occ["_check"]["value"] = "ASTRONAUTA"
    out.append(("NEG wrong declared occupation", occ))
    sen = copy.deepcopy(next(c for c in flat.values() if c["_check"]["kind"] == "web-block" and "Senador, 2019-atual" in c["support"]))
    sen["_check"]["start"] = "NABOR REPUBLICANOS 100"
    out.append(("NEG Veneziano's senate term credited to Nabor's block", sen))
    api = copy.deepcopy(next(c for c in flat.values() if c["_check"]["kind"] == "senado-api" and c["_check"]["code"] == 5894))
    api["_check"]["start"] = "2015-02-01"
    out.append(("NEG Flávio senator since 2015", api))
    return out


def main():
    live = "--live" in sys.argv
    draft = sys.argv[sys.argv.index("--draft") + 1] if "--draft" in sys.argv else PIPE / "profiles" / "profiles.draft.json"
    profiles = json.loads(Path(draft).read_text())
    cand_by_id = {c["id"]: c for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text())}
    random.seed(11)
    rows, shipped = [], []
    for p in profiles:
        out = {k: v for k, v in p.items() if k not in ("presents", "experience", "proposals")}
        for f in ("presents", "experience", "proposals"):
            out[f] = []
            for c in p[f]:
                sample = live and (c["_check"]["kind"] == "senado-api" or (c["_check"]["kind"] == "pdf" and random.random() < 0.3))
                ok, why = check(c, cand_by_id, live=sample)
                rows.append({"id": c["checkId"], "status": "PASS" if ok else "FAIL", "claim": c["text"], "why": why})
                if ok:
                    out[f].append({k: v for k, v in c.items() if k != "_check"})
        ev, _ = evidence_index()
        out["defends"] = [d for d in p["defends"] if d in ev]
        shipped.append(out)
    ctl = []
    for name, c in controls(profiles):
        ok, why = check(c, cand_by_id)
        ctl.append({"id": name, "status": "CONTROL-PASSED" if ok else "FAIL", "why": why})
    report = {"harness_ok": not any(c["status"] == "CONTROL-PASSED" for c in ctl), "rows": rows, "controls": ctl}
    (PIPE / "checks" / "profiles.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    passed = sum(r["status"] == "PASS" for r in rows)
    print(f"claims={len(rows)} PASS={passed} FAIL={len(rows) - passed} live={live} harness_ok={report['harness_ok']}")
    for r in rows:
        if r["status"] == "FAIL":
            print("FAIL", r["id"], r["why"], "|", r["claim"][:110])
    for c in ctl:
        print("CONTROL", c["status"], c["id"], "|", c["why"])
    if not report["harness_ok"]:
        sys.exit("HARNESS BROKEN: a negative control passed")
    if "--draft" in sys.argv:
        return
    (PIPE / "profiles" / "profiles.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
