"""Reads the TSE 1st-round result files cached in tse/ and writes round1.json.

Files come from resultados.tse.jus.br. Presidente is in the federal election (6257);
governador, senador and both deputado offices are in the state election (6259).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TSE = HERE / "tse"
BASE = "https://resultados.tse.jus.br/oficial/ele2026"
ACCESSED = "2026-10-05"

FILES = {
    "presidente_br": ("6257", "br", "0001"),
    "presidente_pb": ("6257", "pb", "0001"),
    "governador_pb": ("6259", "pb", "0003"),
    "senador_pb": ("6259", "pb", "0005"),
    "deputado_federal_pb": ("6259", "pb", "0006"),
    "deputado_estadual_pb": ("6259", "pb", "0007"),
}
LABELS = {
    "presidente_br": "TSE, presidente no Brasil",
    "presidente_pb": "TSE, presidente na Paraíba",
    "governador_pb": "TSE, governador na Paraíba",
    "senador_pb": "TSE, senador na Paraíba",
    "deputado_federal_pb": "TSE, deputado federal na Paraíba",
    "deputado_estadual_pb": "TSE, deputado estadual na Paraíba",
}
OFFICE = {
    "presidente_br": "presidente",
    "presidente_pb": "presidente",
    "governador_pb": "governador",
    "senador_pb": "senador",
    "deputado_federal_pb": "deputado_federal",
    "deputado_estadual_pb": "deputado_estadual",
}


def file_name(key):
    election, uf, cargo = FILES[key]
    return f"{uf}-c{cargo}-e00{election}-u.json"


def url(key):
    election, uf, _ = FILES[key]
    return f"{BASE}/{election}/dados/{uf}/{file_name(key)}"


def num(raw):
    return float(raw.replace(",", "."))


def load(key):
    return json.loads((TSE / file_name(key)).read_text())


def source(key, result):
    return {
        "url": url(key),
        "accessed": ACCESSED,
        "label": LABELS[key],
        "generated": f"{result['dg']} {result['hg'][:5]}",
    }


def candidates(key, result):
    office = OFFICE[key]
    rows = []
    for cargo in result["carg"]:
        for agr in cargo.get("agr", []):
            for party in agr.get("par", []):
                for cand in party.get("cand", []):
                    rows.append({
                        "candidateId": f"{office}-{cand['n']}",
                        "number": cand["n"],
                        "ballotName": cand["nmu"],
                        "party": party["sg"],
                        "list": agr["nm"],
                        "votes": int(cand["vap"]),
                        "pct": num(cand["pvapn"]),
                        "pctLabel": cand["pvap"],
                        "status": cand["st"],
                        "elected": cand["st"].startswith("Eleito"),
                    })
    return sorted(rows, key=lambda r: -r["votes"])


def turnout(result):
    e, v = result["e"], result["v"]
    return {
        "eleitores": int(e["te"]),
        "eleitoresSecoesNaoInstaladas": int(e["esni"]),
        "comparecimento": int(e["c"]),
        "comparecimentoPct": e["pc"],
        "abstencao": int(e["a"]),
        "abstencaoPct": e["pa"],
        "validos": int(v["vv"]),
        "brancos": int(v["vb"]),
        "brancosPct": v["pvb"],
        "nulos": int(v["tvn"]),
        "nulosPct": v["ptvn"],
    }


def seats(result):
    out = []
    for agr in result["carg"][0].get("agr", []):
        vag = int(agr.get("vag", "0"))
        if vag:
            out.append({"list": agr["nm"], "parties": agr.get("com", ""), "seats": vag})
    return sorted(out, key=lambda s: -s["seats"])


def proportional(key, result):
    rows = candidates(key, result)
    elected = [
        r | {"how": "QP" if r["status"] == "Eleito por QP" else "média"}
        for r in rows
        if r["elected"]
    ]
    return {
        "seatsTotal": int(result["carg"][0]["nv"]),
        "seats": seats(result),
        "candidates": rows,
        "elected": elected,
        "source": source(key, result),
    }


def majoritarian(key, result):
    return {
        "candidates": candidates(key, result),
        "seatsTotal": int(result["carg"][0]["nv"]),
        "source": source(key, result),
    }


def build():
    res = {key: load(key) for key in FILES}
    for key, r in res.items():
        assert r["tf"] == "s", f"{key}: totalization not finished"
    out = {
        "round": 1,
        "date": "2026-10-04",
        "presidente": {
            "br": majoritarian("presidente_br", res["presidente_br"]) | {"turnout": turnout(res["presidente_br"])},
            "pb": majoritarian("presidente_pb", res["presidente_pb"]) | {"turnout": turnout(res["presidente_pb"])},
        },
        "governador": majoritarian("governador_pb", res["governador_pb"]),
        "senador": majoritarian("senador_pb", res["senador_pb"]),
        "deputadoFederal": proportional("deputado_federal_pb", res["deputado_federal_pb"]),
        "deputadoEstadual": proportional("deputado_estadual_pb", res["deputado_estadual_pb"]),
    }
    (HERE / "round1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    o = build()
    print("presidente BR top:", [(c["ballotName"], c["pctLabel"]) for c in o["presidente"]["br"]["candidates"][:2]])
    print("senado eleitos:", [c["ballotName"] for c in o["senador"]["candidates"] if c["elected"]])
    print("dep fed eleitos:", len(o["deputadoFederal"]["elected"]), "seats", sum(s["seats"] for s in o["deputadoFederal"]["seats"]))
    print("dep est eleitos:", len(o["deputadoEstadual"]["elected"]), "seats", sum(s["seats"] for s in o["deputadoEstadual"]["seats"]))
    print("turnout PB:", o["presidente"]["pb"]["turnout"])
