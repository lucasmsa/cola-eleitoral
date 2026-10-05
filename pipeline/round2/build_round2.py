"""Reads the TSE 1st-round result files (resultados.tse.jus.br) and writes pipeline/round2/round2.json.

The 2nd-round date comes from the Constituição, art. 77: the runoff is on the last Sunday of October.
"""
import calendar
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
TSE = HERE / "tse"
BASE = "https://resultados.tse.jus.br/oficial/ele2026"
ACCESSED = "2026-10-05"
CONSTITUTION = "https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm"

LABELS = {
    "presidente_br": "TSE, presidente no Brasil",
    "presidente_pb": "TSE, presidente na Paraíba",
    "governador_pb": "TSE, governador na Paraíba",
}
FILES = {
    "presidente_br": ("br-c0001-e006257-u.json", f"{BASE}/6257/dados/br/br-c0001-e006257-u.json"),
    "presidente_pb": ("pb-c0001-e006257-u.json", f"{BASE}/6257/dados/pb/pb-c0001-e006257-u.json"),
    "governador_pb": ("pb-c0003-e006259-u.json", f"{BASE}/6259/dados/pb/pb-c0003-e006259-u.json"),
}


def pct(raw):
    return float(raw.replace(",", "."))


def candidates(result):
    rows = []
    for cargo in result["carg"]:
        for agr in cargo.get("agr", []):
            for party in agr.get("par", []):
                for cand in party.get("cand", []):
                    rows.append({
                        "number": cand["n"],
                        "ballotName": cand["nmu"],
                        "pct": pct(cand["pvapn"]),
                        "pctLabel": cand["pvap"],
                        "status": cand["st"],
                    })
    return sorted(rows, key=lambda r: -r["pct"])


def last_sunday_of_october(year):
    last_day = calendar.monthrange(year, 10)[1]
    d = date(year, 10, last_day)
    while d.weekday() != 6:
        d = date(year, 10, d.day - 1)
    return d.isoformat()


def load(key):
    name, url = FILES[key]
    result = json.loads((TSE / name).read_text())
    source = {
        "url": url,
        "accessed": ACCESSED,
        "label": f"{LABELS[key]}, gerado em {result['dg']} às {result['hg']}",
    }
    return result, source


def build():
    data = {key: load(key) for key in FILES}
    br, br_src = data["presidente_br"]
    pb, pb_src = data["presidente_pb"]
    gov, gov_src = data["governador_pb"]
    pb_by_number = {c["number"]: c for c in candidates(pb)}

    finalists = [c for c in candidates(br) if c["status"] == "2º turno"]
    president = {
        "office": "presidente",
        "status": "runoff",
        "finalists": [
            {
                "candidateId": f"presidente-{c['number']}",
                "number": c["number"],
                "ballotName": c["ballotName"],
                "pctBrasil": c["pctLabel"],
                "pctParaiba": pb_by_number[c["number"]]["pctLabel"],
            }
            for c in finalists
        ],
        "sources": [br_src, pb_src],
    }
    winners = [c for c in candidates(gov) if c["status"] == "Eleito"]
    governor = {
        "office": "governador",
        "status": "decided",
        "winner": {
            "candidateId": f"governador-{winners[0]['number']}",
            "number": winners[0]["number"],
            "ballotName": winners[0]["ballotName"],
            "pct": winners[0]["pctLabel"],
        } if len(winners) == 1 else None,
        "sources": [gov_src],
    }
    out = {
        "date": last_sunday_of_october(2026),
        "dateSource": {"url": CONSTITUTION, "accessed": ACCESSED, "label": "Constituição Federal, art. 77"},
        "offices": [president, governor],
    }
    (HERE / "round2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=1))
