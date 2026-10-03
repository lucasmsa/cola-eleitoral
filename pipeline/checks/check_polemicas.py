"""doc-tdd for controversies. Every claim must be re-derivable from its cached source; status keywords must
appear in the named source; expected responses must be present. Writes polemicas.report.json and, with
--write, pipeline/polemicas/polemicas.json (only items whose every check passed).

Usage: python3 pipeline/checks/check_polemicas.py [--live] [--write] [--draft path]
"""
import copy
import csv
import json
import random
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POL = ROOT / "pipeline" / "polemicas"
sys.path.insert(0, str(POL))
from fetch import UA, fetch, text_of  # noqa: E402

TSE_DIR = POL / "raw" / "tse"
HIST = ROOT / "pipeline" / "raw" / "tse" / "historico_candidatura_2026_BRASIL.csv"
BENS = {2026: "bem_candidato_2026_BRASIL.csv", 2022: "bem_candidato_2022_BRASIL.csv", 2018: "bem_candidato_2018_BRASIL.csv",
        2024: "bem_candidato_2024_PB.csv", 2020: "bem_candidato_2020_PB.csv"}
_text_cache, _rows_cache = {}, {}


def norm(s):
    for a, b in (("“", '"'), ("”", '"'), ("„", '"'), ("‘", "'"), ("’", "'"), (" ", " ")):
        s = s.replace(a, b)
    return " ".join(s.split()).lower()


def page(url):
    if url not in _text_cache:
        _text_cache[url] = norm(text_of(fetch(url)))
    return _text_cache[url]


def csv_rows(path):
    if path not in _rows_cache:
        raw = Path(path).read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        _rows_cache[path] = list(csv.DictReader(text.splitlines(), delimiter=";"))
    return _rows_cache[path]


_sq = {}


def sq_of(cid):
    if not _sq:
        for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text()):
            _sq[c["id"]] = c["source"]["label"].split("SQ ")[-1]
    return _sq[cid]


def history(cid):
    sq = sq_of(cid)
    return [r for r in csv_rows(HIST) if r["SQ_CANDIDATO_ATUAL"] == sq and int(r["ANO_ELEICAO"]) < 2026]


def money(v):
    return float(v.replace(".", "").replace(",", ".")) if "," in v else float(v)


def asset_total(cid, year):
    if year == 2026:
        sqs = {sq_of(cid)}
    else:
        sqs = {r["SQ_CANDIDATO"] for r in csv_rows(HIST) if r["SQ_CANDIDATO_ATUAL"] == sq_of(cid) and int(r["ANO_ELEICAO"]) == year}
    return round(sum(money(r["VR_BEM_CANDIDATO"]) for r in csv_rows(TSE_DIR / BENS[year]) if r["SQ_CANDIDATO"] in sqs), 2)


def check_claim(cl, name):
    kind = cl.get("kind", "text")
    if kind == "tse-assets":
        cid, *pairs = cl["support"].split("|")
        years = sorted(int(p.split("=")[0]) for p in pairs)
        prior = [int(r["ANO_ELEICAO"]) for r in history(cid)]
        expected_years = sorted({max(prior), 2026}) if prior else [2026]
        if years != expected_years:
            return False, f"years {years} != most recent earlier candidacy + 2026 {expected_years}"
        for p in pairs:
            year, value = p.split("=")
            got = asset_total(cid, int(year))
            if abs(got - float(value)) > 0.01:
                return False, f"TSE {year} total {got} != {value}"
        return True, "ok"
    if kind == "tse-history":
        parts = cl["support"].split("|")
        rows = history(parts[0])
        distinct = {(r["ANO_ELEICAO"], r["DS_CARGO"], r["NM_UE"]) for r in rows}
        if len(distinct) != int(parts[1]):
            return False, f"history count {len(distinct)} != {parts[1]}"
        if len(parts) > 2 and parts[2] != "any":
            elected = {(r["ANO_ELEICAO"], r["DS_CARGO"]) for r in rows if r["DS_SIT_TOT_TURNO"] in ("Eleito", "Eleito por QP", "Eleito por média")}
            if len(elected) != int(parts[2]):
                return False, f"elected {len(elected)} != {parts[2]}"
        return True, "ok"
    text = page(cl["source"]["url"])
    sup = norm(cl["support"])
    i = text.find(sup)
    if i < 0:
        return False, "support not in source"
    if kind == "rating":
        window = text[i: i + len(sup) + 700]
        if norm(cl["rating"]) not in window:
            return False, f"rating '{cl['rating']}' not after quote"
    if name and norm(name.split()[-1]) not in text:
        return False, f"name '{name}' not in source"
    return True, "ok"


def check_item(item, sources):
    results, ok = [], True
    for group in ("claims", "response"):
        for cl in item[group]:
            good, why = check_claim(cl, item["name"])
            results.append({"id": cl["checkId"], "status": "PASS" if good else "FAIL", "claim": cl["text"], "why": why})
            ok &= good
    for key, phrase in item["statusKeys"]:
        url = sources[key]
        good = norm(phrase) in page(url)
        results.append({"id": f"pol-{item['id']}-status-{key}", "status": "PASS" if good else "FAIL", "claim": f"status '{phrase}' in {key}", "why": "ok" if good else "status phrase missing"})
        ok &= good
    if item["responseExpected"] and not item["response"]:
        results.append({"id": f"pol-{item['id']}-response", "status": "FAIL", "claim": "response expected", "why": "response dropped"})
        ok = False
    return ok, results


def controls(items, sources):
    by = {i["id"]: i for i in items}
    out = []
    a = copy.deepcopy(by["queiroga-cpi"]); a["statusKeys"] = [("sen_cpi", "Queiroga foi condenado")]
    out.append(("NEG status escalated investigado->condenado (Queiroga)", a))
    b = copy.deepcopy(by["veneziano-stf"]); b["claims"][0]["support"] = b["claims"][0]["support"].replace("(AP) 912", "(AP) 913")
    out.append(("NEG wrong case number (AP 913)", b))
    c = copy.deepcopy(by["efraim-suplente"]); c["claims"][2]["support"] = "Lucas Ribeiro não é investigado."
    out.append(("NEG wrong candidate (Efraim fact moved to Lucas)", c))
    d = copy.deepcopy(by["zema-rejeito"]); d["claims"][0]["support"] = "Eu assinei o decreto a pedido da mineradora"
    out.append(("NEG fabricated quote (Zema)", d))
    e = copy.deepcopy(by["flavio-rachadinha"]); e["response"] = []
    out.append(("NEG dropped response (Flávio)", e))
    f = copy.deepcopy(by["cicero-registro-tse"]); f["statusKeys"] = [("jp_cicero_tse", "o TSE deferiu o registro")]
    out.append(("NEG outdated status (Cícero deferido)", f))
    g = copy.deepcopy(by["patrimonio-presidente-22"]); g["claims"][0]["support"] = g["claims"][0]["support"].rsplit("=", 1)[0] + "=9186555.83"
    out.append(("NEG wrong TSE asset total (Flávio)", g))
    h = copy.deepcopy(by["cury-experiencia"]); h["claims"][0]["support"] = "presidente-70|1"
    out.append(("NEG wrong history count (Cury)", h))
    j = copy.deepcopy(by["patrimonio-senador-155"]); j["claims"][0]["support"] = j["claims"][0]["support"].replace("2022=", "2018=")
    out.append(("NEG stale comparison year (Veneziano 2018 instead of latest)", j))
    k = copy.deepcopy(by["patrimonio-governador-11"]); k["claims"][0]["support"] = k["claims"][0]["support"].rsplit("=", 1)[0] + "=741354.00"
    out.append(("NEG wrong 2026 total (Lucas)", k))
    i = copy.deepcopy(by["lucas-checagem"]); i["claims"][0]["rating"] = "A INFORMAÇÃO É VERDADEIRA"
    out.append(("NEG flipped fact-check rating (Lucas)", i))
    return [(n, check_item(x, sources)[0]) for n, x in out]


def live_sample(items, rate=0.3):
    urls = sorted({cl["source"]["url"] for it in items for g in ("claims", "response") for cl in it[g] if cl.get("kind", "text") in ("text", "rating")})
    random.seed(11)
    picked = [u for u in urls if random.random() < rate]
    res = []
    import subprocess
    for u in picked:
        with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
            subprocess.run(["curl", "-sL", "--compressed", "--max-time", "40", "-A", UA, "-o", tmp.name, u], check=False)
            live = norm(text_of(Path(tmp.name)))
        sups = [norm(cl["support"]) for it in items for g in ("claims", "response") for cl in it[g] if cl["source"]["url"] == u and cl.get("kind", "text") in ("text", "rating")]
        if len(live) < 500:
            res.append((u, "LIVE-UNREACHABLE"))
            continue
        missing = [s for s in sups if s not in live]
        res.append((u, "PASS" if not missing else f"FAIL {len(missing)} missing"))
    return res


def main():
    draft_path = Path(sys.argv[sys.argv.index("--draft") + 1]) if "--draft" in sys.argv else POL / "draft.json"
    sys.path.insert(0, str(POL))
    from build_polemicas import S
    sources = {k: v[0] for k, v in S.items()}
    items = json.loads(draft_path.read_text())
    report, shipped = [], []
    for it in items:
        ok, rows = check_item(it, sources)
        report.extend(rows)
        if ok:
            shipped.append(it)
    ctl = controls(items, sources)
    for name, passed in ctl:
        report.append({"id": name, "status": "CONTROL-PASSED" if passed else "FAIL", "claim": name})
    live = live_sample(items) if "--live" in sys.argv else []
    for u, st in live:
        report.append({"id": f"live:{u}", "status": "PASS" if st == "PASS" else st, "claim": "live re-fetch"})
    (ROOT / "pipeline" / "checks" / "polemicas.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    fails = [r for r in report if r["status"] == "FAIL" and not r["id"].startswith("NEG")]
    broken = [n for n, p in ctl if p]
    for r in fails:
        print("FAIL", r["id"], "|", r.get("why"))
    for u, st in live:
        print("LIVE", st, u[:90])
    print(f"items={len(items)} shipped={len(shipped)} claims_pass={sum(r['status']=='PASS' for r in report if r['id'].startswith('pol-'))} fails={len(fails)} controls={len(ctl)} controls_broken={len(broken)}")
    if broken:
        print("HARNESS BROKEN:", broken)
        sys.exit(1)
    if "--write" in sys.argv:
        clean = []
        for it in shipped:
            clean.append({
                "id": it["id"], "candidateId": it["candidateId"], "category": it["category"], "title": it["title"],
                "status": it["status"], "date": it["date"],
                "claims": [{k: cl[k] for k in ("text", "support", "source", "checkId")} for cl in it["claims"]],
                "response": [{k: cl[k] for k in ("text", "support", "source", "checkId")} for cl in it["response"]],
            })
        (POL / "polemicas.json").write_text(json.dumps(clean, ensure_ascii=False, indent=1))
        print("wrote", len(clean), "items")


if __name__ == "__main__":
    main()
