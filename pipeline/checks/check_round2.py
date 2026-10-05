"""doc-tdd for the 2nd-round data: every number and status in pipeline/round2/round2.json is re-derived
from the cached TSE result files, the files are re-fetched live, and the date is checked against the
Constituição (art. 77). Controls are mutated copies that must fail.

Usage: check_round2.py [--live]
"""
import copy
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline" / "round2"))
import build_round2 as b  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"
CONST_CACHE = ROOT / "pipeline" / "raw" / "laws" / "constituicao.htm"
ART77 = "no último domingo de outubro, em segundo turno"


def fetch(url, dest=None):
    out = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA, url], capture_output=True)
    if out.returncode != 0 or not out.stdout:
        return None
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(out.stdout)
    return out.stdout


def constitution_text():
    if not CONST_CACHE.exists():
        fetch(b.CONSTITUTION, CONST_CACHE)
    raw = CONST_CACHE.read_bytes().decode("latin-1", errors="ignore")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def results(live):
    out = {}
    for key, (name, url) in b.FILES.items():
        if live:
            body = fetch(url)
            out[key] = json.loads(body) if body else None
        else:
            out[key] = json.loads((b.TSE / name).read_text())
    return out


def by_number(result):
    return {c["number"]: c for c in b.candidates(result)}


def verify(r2, files, const):
    rows = []

    def row(cid, ok, claim, why=""):
        rows.append({"id": cid, "status": "PASS" if ok else "FAIL", "claim": claim, "why": "" if ok else why})

    for key, res in files.items():
        if res is None:
            row(f"r2-file-{key}", False, f"{key} reachable", "fetch failed")
            continue
        row(f"r2-final-{key}", res["tf"] == "s" and res["s"]["pst"] == "100,00",
            f"{key}: totalização final, 100% das seções", f"tf={res['tf']} pst={res['s']['pst']}")

    pres = next(o for o in r2["offices"] if o["office"] == "presidente")
    gov = next(o for o in r2["offices"] if o["office"] == "governador")
    br, pb, gv = files["presidente_br"], files["presidente_pb"], files["governador_pb"]

    if br and pb:
        br_c, pb_c = by_number(br), by_number(pb)
        tse_finalists = sorted(n for n, c in br_c.items() if c["status"] == "2º turno")
        ours = sorted(f["number"] for f in pres["finalists"])
        row("r2-pres-finalists", pres["status"] == "runoff" and ours == tse_finalists and len(ours) == 2,
            f"Presidente vai ao 2º turno entre {ours}", f"TSE finalists {tse_finalists}, status {pres['status']}")
        for f in pres["finalists"]:
            n = f["number"]
            row(f"r2-pres-{n}-br", br_c.get(n, {}).get("pctLabel") == f["pctBrasil"],
                f"{f['ballotName']} teve {f['pctBrasil']}% dos votos válidos no Brasil",
                f"TSE {br_c.get(n, {}).get('pctLabel')}")
            row(f"r2-pres-{n}-pb", pb_c.get(n, {}).get("pctLabel") == f["pctParaiba"],
                f"{f['ballotName']} teve {f['pctParaiba']}% dos votos válidos na Paraíba",
                f"TSE {pb_c.get(n, {}).get('pctLabel')}")
            row(f"r2-pres-{n}-name", br_c.get(n, {}).get("ballotName") == f["ballotName"],
                f"número {n} é {f['ballotName']}", f"TSE {br_c.get(n, {}).get('ballotName')}")
        for src, res in zip(pres["sources"], (br, pb)):
            row(f"r2-src-{src['url'].rsplit('/', 1)[1]}", f"{res['dg']} às {res['hg']}" in src["label"],
                src["label"], f"TSE gerado {res['dg']} {res['hg']}")

    if gv:
        gv_c = by_number(gv)
        elected = [n for n, c in gv_c.items() if c["status"] == "Eleito"]
        runoff = [n for n, c in gv_c.items() if c["status"] == "2º turno"]
        w = gov.get("winner") or {}
        row("r2-gov-decided", gov["status"] == "decided" and not runoff and elected == [w.get("number")],
            f"Governador da PB decidido no 1º turno: {w.get('ballotName')}",
            f"TSE eleito {elected}, 2º turno {runoff}, status {gov['status']}")
        row("r2-gov-pct", gv_c.get(w.get("number"), {}).get("pctLabel") == w.get("pct"),
            f"{w.get('ballotName')} teve {w.get('pct')}% dos votos válidos", f"TSE {gv_c.get(w.get('number'), {}).get('pctLabel')}")
        row("r2-src-gov", f"{gv['dg']} às {gv['hg']}" in gov["sources"][0]["label"], gov["sources"][0]["label"], "timestamp")

    row("r2-date", r2["date"] == b.last_sunday_of_october(2026) and ART77 in const,
        f"2º turno em {r2['date']} (último domingo de outubro, CF art. 77)", "date or constitution text")
    return rows


def controls(r2, files, const):
    def mutate(fn):
        m = copy.deepcopy(r2)
        fn(m)
        return m

    def swap(m):
        f = m["offices"][0]["finalists"]
        f[0]["pctBrasil"], f[1]["pctBrasil"] = f[1]["pctBrasil"], f[0]["pctBrasil"]

    def wrong_winner(m):
        m["offices"][1]["winner"].update({"number": "22", "ballotName": "EFRAIM FILHO"})

    def gov_runoff(m):
        m["offices"][1]["status"] = "runoff"

    def wrong_date(m):
        m["date"] = "2026-10-18"

    def cury_finalist(m):
        m["offices"][0]["finalists"][1].update({"number": "70", "ballotName": "ESCRITOR AUGUSTO CURY"})

    cases = {
        "NEG swapped percentages": swap,
        "NEG wrong governor winner": wrong_winner,
        "NEG governor marked as runoff": gov_runoff,
        "NEG wrong runoff date": wrong_date,
        "NEG Cury as finalist": cury_finalist,
    }
    out = []
    for name, fn in cases.items():
        failed = any(r["status"] == "FAIL" for r in verify(mutate(fn), files, const))
        out.append({"id": name, "status": "FAIL" if failed else "CONTROL-PASSED", "claim": name})
    return out


def main():
    live = "--live" in sys.argv
    r2 = json.loads((ROOT / "pipeline" / "round2" / "round2.json").read_text())
    const = constitution_text()
    cached = results(False)
    rows = verify(r2, cached, const)
    if live:
        for r in verify(r2, results(True), const):
            r["id"] += "-live"
            rows.append(r)
    ctl = controls(r2, cached, const)
    report = {"rows": rows, "controls": ctl}
    (ROOT / "pipeline" / "checks" / "round2.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    for r in rows + ctl:
        print(f"{r['status']:<15} {r['id']:<40} {r.get('why', '')}")
    broken = [c for c in ctl if c["status"] != "FAIL"]
    passed = sum(r["status"] == "PASS" for r in rows)
    print(f"PASS {passed}/{len(rows)}  controls broken {len(broken)}  live={live}")
    if broken or passed != len(rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
