"""doc-tdd for round1.json: every number, status and seat count is re-derived from the TSE files.

Independent of build_round1.py: walks the raw JSON itself. With --live, re-fetches each file from
resultados.tse.jus.br (no query string; the CDN fans out to several buckets, so it retries).
"""
import copy
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "pipeline" / "round1"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"
KEYS = {
    "presidente_br": "br-c0001-e006257-u.json",
    "presidente_pb": "pb-c0001-e006257-u.json",
    "governador_pb": "pb-c0003-e006259-u.json",
    "senador_pb": "pb-c0005-e006259-u.json",
    "deputado_federal_pb": "pb-c0006-e006259-u.json",
    "deputado_estadual_pb": "pb-c0007-e006259-u.json",
}


def raw(name):
    return json.loads((R1 / "tse" / name).read_text())


def live(url):
    for _ in range(20):
        out = subprocess.run(["curl", "-s", "--max-time", "90", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True, text=True)
        body, _, code = out.stdout.rpartition("\n")
        if code == "200":
            return json.loads(body)
        time.sleep(1)
    return None


def cands(result):
    out = {}
    for agr in result["carg"][0].get("agr", []):
        for par in agr.get("par", []):
            for c in par.get("cand", []):
                out[c["n"]] = c | {"_party": par["sg"], "_list": agr["nm"]}
    return out


def seat_map(result):
    return {a["nm"]: int(a.get("vag", "0")) for a in result["carg"][0].get("agr", []) if int(a.get("vag", "0"))}


def check_majoritarian(section, result, rows):
    tse = cands(result)
    for c in section["candidates"]:
        t = tse.get(c["number"])
        rid = f"{section['source']['label']}:{c['number']}"
        ok = (
            t is not None
            and t["nmu"] == c["ballotName"]
            and int(t["vap"]) == c["votes"]
            and t["pvap"] == c["pctLabel"]
            and t["st"] == c["status"]
            and t["st"].startswith("Eleito") == c["elected"]
            and t["_party"] == c["party"]
        )
        rows.append({"id": rid, "status": "PASS" if ok else "FAIL", "claim": f"{c['ballotName']} {c['pctLabel']}% {c['status']}"})
    rows.append({
        "id": f"{section['source']['label']}:count",
        "status": "PASS" if len(section["candidates"]) == len(tse) else "FAIL",
        "claim": f"{len(section['candidates'])} candidates",
    })
    gen = f"{result['dg']} {result['hg'][:5]}"
    rows.append({"id": f"{section['source']['label']}:generated", "status": "PASS" if section["source"]["generated"] == gen and result["tf"] == "s" else "FAIL", "claim": gen})


def check_turnout(t, result, label, rows):
    e, v = result["e"], result["v"]
    pairs = [
        ("eleitores", int(e["te"])), ("eleitoresSecoesNaoInstaladas", int(e["esni"])), ("comparecimento", int(e["c"])), ("comparecimentoPct", e["pc"]),
        ("abstencao", int(e["a"])), ("abstencaoPct", e["pa"]), ("validos", int(v["vv"])),
        ("brancos", int(v["vb"])), ("brancosPct", v["pvb"]), ("nulos", int(v["tvn"])), ("nulosPct", v["ptvn"]),
    ]
    for k, want in pairs:
        rows.append({"id": f"{label}:turnout:{k}", "status": "PASS" if t[k] == want else "FAIL", "claim": f"{k} {t[k]}"})
    rows.append({
        "id": f"{label}:turnout:sum",
        "status": "PASS" if t["comparecimento"] + t["abstencao"] == t["eleitores"] - t["eleitoresSecoesNaoInstaladas"] == int(e["esi"]) else "FAIL",
        "claim": "comparecimento + abstenção = eleitores de seções instaladas",
    })


def check_proportional(section, result, rows):
    label = section["source"]["label"]
    tse = cands(result)
    elected_tse = {n for n, c in tse.items() if c["st"].startswith("Eleito")}
    elected_ours = {c["number"] for c in section["elected"]}
    rows.append({"id": f"{label}:elected-set", "status": "PASS" if elected_tse == elected_ours else "FAIL", "claim": f"{len(elected_ours)} eleitos"})
    for c in section["elected"]:
        t = tse[c["number"]]
        how = "QP" if t["st"] == "Eleito por QP" else "média" if t["st"] == "Eleito por média" else "?"
        ok = int(t["vap"]) == c["votes"] and t["nmu"] == c["ballotName"] and c["how"] == how and t["_party"] == c["party"]
        rows.append({"id": f"{label}:{c['number']}", "status": "PASS" if ok else "FAIL", "claim": f"{c['ballotName']} {c['votes']} por {c['how']}"})
    for c in section["candidates"]:
        t = tse.get(c["number"])
        ok = t is not None and int(t["vap"]) == c["votes"] and t["st"] == c["status"] and t["st"].startswith("Eleito") == c["elected"] and t["nmu"] == c["ballotName"]
        rows.append({"id": f"{label}:cand:{c['number']}", "status": "PASS" if ok else "FAIL", "claim": f"{c['ballotName']} {c['status']}"})
    rows.append({"id": f"{label}:cand-count", "status": "PASS" if len(section["candidates"]) == len(tse) else "FAIL", "claim": f"{len(section['candidates'])} candidatos"})
    ours = {s["list"]: s["seats"] for s in section["seats"]}
    rows.append({"id": f"{label}:seats", "status": "PASS" if ours == seat_map(result) else "FAIL", "claim": json.dumps(ours, ensure_ascii=False)})
    total = int(result["carg"][0]["nv"])
    ok_total = section["seatsTotal"] == total == sum(ours.values()) == len(elected_ours)
    rows.append({"id": f"{label}:seats-total", "status": "PASS" if ok_total else "FAIL", "claim": f"{total} vagas"})


def run(data, results):
    rows = []
    check_majoritarian(data["presidente"]["br"], results["presidente_br"], rows)
    check_majoritarian(data["presidente"]["pb"], results["presidente_pb"], rows)
    check_turnout(data["presidente"]["br"]["turnout"], results["presidente_br"], "BR", rows)
    check_turnout(data["presidente"]["pb"]["turnout"], results["presidente_pb"], "PB", rows)
    check_majoritarian(data["governador"], results["governador_pb"], rows)
    check_majoritarian(data["senador"], results["senador_pb"], rows)
    elected_senators = [c for c in data["senador"]["candidates"] if c["elected"]]
    rows.append({"id": "senado:two-elected", "status": "PASS" if len(elected_senators) == 2 == data["senador"]["seatsTotal"] else "FAIL", "claim": "2 senadores eleitos"})
    check_proportional(data["deputadoFederal"], results["deputado_federal_pb"], rows)
    check_proportional(data["deputadoEstadual"], results["deputado_estadual_pb"], rows)
    return rows


def failed(rows):
    return [r for r in rows if r["status"] != "PASS"]


def controls(data, results):
    out = []

    def mutate(fn):
        d = copy.deepcopy(data)
        fn(d)
        return failed(run(d, results))

    def swap_pct(d):
        a, b = d["presidente"]["br"]["candidates"][:2]
        a["pctLabel"], b["pctLabel"] = b["pctLabel"], a["pctLabel"]

    def wrong_governor(d):
        for c in d["governador"]["candidates"]:
            c["elected"] = c["number"] == "22"

    def third_senator(d):
        d["senador"]["candidates"][2]["elected"] = True

    def seat_shift(d):
        d["deputadoFederal"]["seats"][0]["seats"] += 1

    def qp_as_media(d):
        d["deputadoEstadual"]["elected"][0]["how"] = "média" if d["deputadoEstadual"]["elected"][0]["how"] == "QP" else "QP"

    def runoff_as_elected(d):
        d["presidente"]["br"]["candidates"][0]["elected"] = True

    def turnout_typo(d):
        d["presidente"]["pb"]["turnout"]["abstencao"] += 1000

    for name, fn in [("NEG swapped Flávio/Lula %", swap_pct), ("NEG Efraim elected governor", wrong_governor),
                     ("NEG third senator elected", third_senator), ("NEG extra federal seat", seat_shift),
                     ("NEG QP vs média flipped", qp_as_media), ("NEG abstenção +1000", turnout_typo), ("NEG runoff finalist marked elected", runoff_as_elected)]:
        out.append((name, len(mutate(fn)) > 0))
    return out


def main():
    data = json.loads((R1 / "round1.json").read_text())
    results = {k: raw(n) for k, n in KEYS.items()}
    rows = run(data, results)
    if "--live" in sys.argv:
        from build_round1 import url  # noqa: E402
        for k in KEYS:
            fresh = live(url(k))
            same = fresh is not None and fresh["dg"] == results[k]["dg"] and fresh["hg"] == results[k]["hg"] and fresh["carg"] == results[k]["carg"]
            rows.append({"id": f"live:{k}", "status": "PASS" if same else "FAIL", "claim": "live file equals cache" if fresh else "live fetch failed"})
    ctl = controls(data, results)
    for name, caught in ctl:
        rows.append({"id": name, "status": "FAIL" if caught else "CONTROL-PASSED", "claim": name})
    report = {"harness_ok": all(c for _, c in ctl), "rows": [r for r in rows if not r["id"].startswith("NEG")], "controls": [r for r in rows if r["id"].startswith("NEG")]}
    (ROOT / "pipeline" / "checks" / "round1.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    bad = failed(report["rows"])
    print(f"PASS {len(report['rows']) - len(bad)}/{len(report['rows'])}  controls caught {sum(c for _, c in ctl)}/{len(ctl)}  harness_ok={report['harness_ok']}")
    for r in bad:
        print("FAIL", r["id"], r["claim"])
    if not report["harness_ok"] or bad:
        sys.exit(1)


if __name__ == "__main__":
    sys.path.insert(0, str(R1))
    main()
