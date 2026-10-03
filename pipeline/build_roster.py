"""Builds src/data/candidates.json from the TSE 2026 candidate files (consulta_cand + complementar).

Only public ballot fields are kept. CPF, e-mail, título and birth data never leave pipeline/raw.
"""
import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "pipeline" / "raw"
TSE = RAW / "tse"
OUT = ROOT / "src" / "data" / "candidates.json"
PLANS_OUT = ROOT / "public" / "plans"

ACCESSED = "2026-09-30"
SRC_CAND = "https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip"
SRC_PLAN = {
    "BR": "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_BR.zip",
    "PB": "https://cdn.tse.jus.br/estatistica/sead/odsele/proposta_governo/proposta_governo_2026_PB.zip",
}

OFFICES = {
    "PRESIDENTE": "presidente",
    "GOVERNADOR": "governador",
    "SENADOR": "senador",
    "DEPUTADO FEDERAL": "deputado_federal",
    "DEPUTADO ESTADUAL": "deputado_estadual",
}
MATES = {"VICE-PRESIDENTE": "PRESIDENTE", "VICE-GOVERNADOR": "GOVERNADOR",
         "1º SUPLENTE": "SENADOR", "2º SUPLENTE": "SENADOR"}
ELECTED = {"Eleito", "Eleito por QP", "Eleito por média"}
WITHDRAWN = {"RENÚNCIA"}
ON_BALLOT = {
    "DEFERIDO",
    "DEFERIDO EM PRAZO RECURSAL OU COM RECURSO",
    "INDEFERIDO EM PRAZO RECURSAL OU COM RECURSO",
    "PENDENTE DE JULGAMENTO",
}


def read(path, encoding=None):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return list(csv.DictReader(text.splitlines(), delimiter=";"))


HISTORY_FILE = "historico_candidatura_2026_BRASIL.csv"


def history():
    out = {}
    for h in read(TSE / HISTORY_FILE, "latin-1"):
        if h["DS_SIT_TOT_TURNO"] not in ELECTED:
            continue
        place = h["NM_UE"].strip().title() if h["TP_ABRANGENCIA_ELEICAO"] == "M" else h["SG_UF"].strip()
        out.setdefault(h["SQ_CANDIDATO_ATUAL"], []).append(
            {"year": int(h["ANO_ELEICAO"]), "office": h["DS_CARGO"].strip(), "place": place, "party": h["SG_PARTIDO"].strip()})
    for v in out.values():
        v.sort(key=lambda e: -e["year"])
    return out


def list_name(row):
    nm = row["NM_FEDERACAO"].strip()
    return nm.title() if nm and nm not in ("#NULO", "#NE") else row["SG_PARTIDO"].strip()


def list_id(row):
    sg = row["SG_FEDERACAO"].strip()
    return sg if sg and sg not in ("#NULO", "#NE") else row["SG_PARTIDO"].strip()


def plan_files():
    roster = json.loads((RAW / "roster.json").read_text())
    files = {}
    for key in ("president", "governor_PB"):
        for c in roster[key]:
            plan = c.get("plano_de_governo")
            if plan and (RAW / "plans" / plan["file"]).exists():
                files[c["sq_candidato"]] = plan["file"]
    return files


def build():
    plans = plan_files()
    hist = history()
    PLANS_OUT.mkdir(parents=True, exist_ok=True)
    candidates, mates = [], {}
    for uf in ("BR", "PB"):
        rows = read(TSE / f"consulta_cand_2026_{uf}.csv", "latin-1")
        comp = {r["SQ_CANDIDATO"]: r for r in read(TSE / f"comp_{uf}.csv", "utf-8")}
        for r in rows:
            c = comp.get(r["SQ_CANDIDATO"], {})
            status = c.get("DS_SITUACAO_JULGAMENTO", "").strip()
            cargo = r["DS_CARGO"].strip()
            if cargo in MATES:
                if status in ON_BALLOT:
                    mates.setdefault((MATES[cargo], r["NR_CANDIDATO"]), []).append((cargo, r["NM_URNA_CANDIDATO"].strip()))
                continue
            if cargo not in OFFICES or status not in ON_BALLOT | WITHDRAWN:
                continue
            sq = r["SQ_CANDIDATO"]
            cand = {
                "id": f"{OFFICES[cargo]}-{r['NR_CANDIDATO']}",
                "office": OFFICES[cargo],
                "number": r["NR_CANDIDATO"],
                "ballotName": r["NM_URNA_CANDIDATO"].strip(),
                "party": r["SG_PARTIDO"].strip(),
                "list": list_id(r),
                "listName": list_name(r),
                "runningMates": [],
                "status": status,
                "withdrawn": status in WITHDRAWN,
                "_generated": f"{r['DT_GERACAO']} {r['HH_GERACAO'][:5]}",
                "elected": hist.get(sq, [])[:4],
                "source": {"url": SRC_CAND, "accessed": ACCESSED,
                           "label": f"TSE, consulta_cand_2026_{uf}.csv, SQ {sq}"},
                "_cargo": cargo,
            }
            if sq in plans:
                shutil.copy(RAW / "plans" / plans[sq], PLANS_OUT / plans[sq])
                cand["planUrl"] = f"/plans/{plans[sq]}"
                cand["planSource"] = SRC_PLAN[uf]
            candidates.append(cand)
    on_ballot_ids = {c["id"] for c in candidates if not c["withdrawn"]}
    candidates = [c for c in candidates if not (c["withdrawn"] and c["id"] in on_ballot_ids)]
    seen = set()
    candidates = [c for c in candidates if not (c["id"] in seen or seen.add(c["id"]))]
    for cand in candidates:
        generated = cand.pop("_generated")
        if cand["withdrawn"]:
            cand["notice"] = {"text": f"O TSE registrou a renúncia desta candidatura (dados de {generated}). Ela não concorre mais.",
                              "sources": [cand["source"]]}
    for cand in candidates:
        cand["runningMates"] = [n for _, n in sorted(mates.get((cand.pop("_cargo"), cand["number"]), []))]
    report = {r["id"] for r in json.loads((ROOT / "pipeline" / "checks" / "notices.report.json").read_text()) if r["status"] == "PASS"}
    for n in json.loads((ROOT / "pipeline" / "notices.json").read_text()):
        for cand in candidates:
            if cand["id"] == n["candidateId"] and n["candidateId"] in report:
                cand["notice"] = {"text": n["text"], "sources": [{k: s[k] for k in ("url", "accessed", "label")} for s in n["sources"]]}
    candidates.sort(key=lambda c: (list(OFFICES.values()).index(c["office"]), c["ballotName"]))
    ids = [c["id"] for c in candidates]
    assert len(ids) == len(set(ids)), "duplicate candidate id"
    OUT.write_text(json.dumps(candidates, ensure_ascii=False, indent=1))
    return candidates


if __name__ == "__main__":
    out = build()
    from collections import Counter
    print(Counter(c["office"] for c in out))
    print(sum(bool(c["elected"]) for c in out), "with an elected history")
