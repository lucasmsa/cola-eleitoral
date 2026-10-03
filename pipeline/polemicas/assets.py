"""Declared assets per candidate from TSE bem_candidato files, linked across years by the TSE history file."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TSE = ROOT / "pipeline" / "polemicas" / "raw" / "tse"
HIST = ROOT / "pipeline" / "raw" / "tse" / "historico_candidatura_2026_BRASIL.csv"
TARGETS = {
    "presidente-13": "LULA", "presidente-22": "FLAVIO BOLSONARO", "presidente-14": "RENAN SANTOS",
    "presidente-70": "ESCRITOR AUGUSTO CURY", "presidente-55": "RONALDO CAIADO", "presidente-30": "ZEMA",
    "governador-11": "LUCAS RIBEIRO", "governador-22": "EFRAIM FILHO", "governador-15": "CÍCERO LUCENA",
    "governador-80": "YURI EZEQUIEL", "governador-29": "CAMILO DUARTE",
    "senador-400": "JOAO AZEVÊDO", "senador-155": "VENEZIANO", "senador-100": "NABOR",
    "senador-222": "DR. MARCELO QUEIROGA", "senador-300": "MAJOR FÁBIO",
}
FILES = {2026: "bem_candidato_2026_BRASIL.csv", 2022: "bem_candidato_2022_BRASIL.csv",
         2018: "bem_candidato_2018_BRASIL.csv", 2024: "bem_candidato_2024_PB.csv", 2020: "bem_candidato_2020_PB.csv"}


def rows(path):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return csv.DictReader(text.splitlines(), delimiter=";")


def money(v):
    return float(v.replace(".", "").replace(",", ".")) if "," in v else float(v)


def main():
    cands = json.loads((ROOT / "src" / "data" / "candidates.json").read_text())
    sq_now = {c["id"]: c["source"]["label"].split("SQ ")[-1] for c in cands if c["id"] in TARGETS}
    wanted = {2026: {sq: cid for cid, sq in sq_now.items()}}
    for h in rows(HIST):
        cid = next((c for c, sq in sq_now.items() if sq == h["SQ_CANDIDATO_ATUAL"]), None)
        if cid and int(h["ANO_ELEICAO"]) in FILES and int(h["ANO_ELEICAO"]) != 2026:
            wanted.setdefault(int(h["ANO_ELEICAO"]), {})[h["SQ_CANDIDATO"]] = cid
    totals = {}
    for year, sqs in wanted.items():
        for r in rows(TSE / FILES[year]):
            cid = sqs.get(r["SQ_CANDIDATO"])
            if cid:
                totals.setdefault(cid, {}).setdefault(year, 0.0)
                totals[cid][year] += money(r["VR_BEM_CANDIDATO"])
    out = {cid: {str(y): round(v, 2) for y, v in sorted(t.items())} for cid, t in totals.items()}
    for cid in TARGETS:
        out.setdefault(cid, {})
    (ROOT / "pipeline" / "polemicas" / "assets.json").write_text(json.dumps({"sq2026": sq_now, "totals": out}, ensure_ascii=False, indent=1))
    for cid, t in out.items():
        print(cid, TARGETS[cid], t)


if __name__ == "__main__":
    main()
