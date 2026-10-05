"""Merges checked evidence into src/data (ADR-0004). Only rows whose id is PASS in a check report ship."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPE = ROOT / "pipeline"
DATA = ROOT / "src" / "data"
ACCESSED = "2026-09-30"
STREAMS = {
    "record": ("record/evidence.json", "checks/record.report.json"),
    "platform": ("platform/evidence.json", "checks/platform.report.json"),
    "alpb": ("alpb/evidence.json", "checks/alpb.report.json"),
    "exec": ("exec/evidence.json", "checks/exec.report.json"),
    "senate": ("senate/evidence.json", "checks/senate.report.json"),
    "gov": ("gov/evidence.json", "checks/gov.report.json"),
    "pres2": ("pres2/evidence.json", "checks/pres2.report.json"),
    "pb2": ("pb2/evidence.json", "checks/pb2.report.json"),
    "q3": ("q3/evidence.json", "checks/q3.report.json"),
    "news5": ("news5/evidence.json", "checks/news5.report.json"),
    "pres": ("pres/evidence.json", "checks/pres.report.json"),
}
QUESTION_FILES = ("alpb/questions.json", "exec/questions.json", "senate/questions.json", "gov/questions.json", "q3/questions.json")
EXPECTED_STREAMS = {"record", "platform"}


def load(rel):
    path = PIPE / rel
    return json.loads(path.read_text()) if path.exists() else None


def passed_ids(report):
    rows = []
    if isinstance(report, list):
        rows = report
    elif isinstance(report, dict):
        for key in ("rows", "claims", "evidence", "results"):
            if isinstance(report.get(key), list):
                rows = report[key]
                break
    return {row_key(r) for r in rows if str(r.get("status", "")).upper() == "PASS"}


def row_key(r):
    if "id" in r:
        return r["id"]
    return (r["candidateId"], r["questionId"], r["quote"])


def evidence_keys(e):
    return {e["id"], e["checkId"], (e["subject"]["id"], e["questionId"], e.get("quote"))}


def br_date(iso):
    y, m, d = iso[:10].split("-")
    return f"{d}/{m}/{y}"


TALLY_KEYS = (("Sim", "sim"), ("Não", "não"), ("Abstenção", "abstenção"), ("Abstencao", "abstenção"))


def context_for(question_id, votacoes):
    lines, sources = [], []
    for v in votacoes:
        if v["questionId"] != question_id:
            continue
        desc = v["descricao"].lower()
        when = br_date(v["date"])
        if desc.startswith("aprovad"):
            outcome = f"aprovada em {when}"
        elif desc.startswith("rejeitad"):
            outcome = f"rejeitada em {when}"
        else:
            outcome = f"votação em {when}"
        tally = {k.lower(): n for k, n in (v.get("tally") or {}).items()}
        counts = ", ".join(f"{tally[k.lower()]} {label}" for k, label in TALLY_KEYS if tally.get(k.lower()))
        house = "Câmara" if v["house"] == "camara" else "Senado"
        lines.append(f"{v['label']}: {outcome}" + (f" ({counts})." if counts else "."))
        sources.append({"url": v["urls"][0], "accessed": ACCESSED, "label": f"{house}, Dados Abertos, votação {v['id']}"})
    return " ".join(lines), sources


def build():
    candidates = json.loads((DATA / "candidates.json").read_text())
    by_id = {c["id"]: c for c in candidates}
    list_ids = {c["list"] for c in candidates}
    draft = load("questions.draft.json")["questions"]
    pb_questions = []
    seen = {q["id"] for q in draft}
    for rel in QUESTION_FILES:
        for q in load(rel) or []:
            if q["id"] not in seen:
                seen.add(q["id"])
                pb_questions.append(q)
    votacoes = load("record/votacoes.json") or []

    evidence, stats = [], {}
    for stream, (ev_rel, rep_rel) in STREAMS.items():
        rows, report = load(ev_rel), load(rep_rel)
        if rows is None or report is None:
            if stream in EXPECTED_STREAMS:
                raise SystemExit(f"missing {stream} evidence or report")
            stats[stream] = {"shipped": 0, "note": "pending"}
            continue
        ok = passed_ids(report)
        kept = [e for e in rows if evidence_keys(e) & ok]
        known = {e["id"] for e in evidence}
        fresh = [e for e in kept if e["id"] not in known]
        stats[stream] = {"rows": len(rows), "passed": len(kept), "new": len(fresh)}
        evidence.extend(fresh)

    questions = []
    for q in draft + pb_questions:
        context, sources = context_for(q["id"], votacoes)
        questions.append({
            "id": q["id"], "area": q["area"], "offices": q["offices"], "statement": q["statement"],
            "context": q.get("context") or context, "sources": q.get("sources") or sources,
        } | ({"options": q["options"]} if q.get("options") else {}))
    for qid, opts in (load("q3/options.json") or {}).items():
        for q in questions:
            if q["id"] == qid:
                q["options"] = opts
    qmap = {q["id"]: q for q in questions}

    def fits(e):
        q = qmap.get(e["questionId"])
        if not q:
            return False
        if e["subject"]["type"] == "list":
            return e["subject"]["id"] in list_ids
        cand = by_id.get(e["subject"]["id"])
        return bool(cand) and cand["office"] in q["offices"]

    shipped = [{k: v for k, v in e.items() if k != "lowDiscrimination"} | {"lowDiscrimination": bool(e.get("lowDiscrimination"))} for e in evidence if fits(e)]
    used = {e["questionId"] for e in shipped}
    questions = [q for q in questions if q["id"] in used]

    (DATA / "questions.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1))
    (DATA / "evidence.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))
    meta = {"builtAt": date.today().isoformat(), "electionDate": "2026-10-04", "streams": stats,
            "evidence": len(shipped), "questions": len(questions), "droppedOffice": len(evidence) - len(shipped)}
    (DATA / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(json.dumps(meta, ensure_ascii=False))


CLAIM_FILES = {
    "explainers.json": [("explain/explainers.json", "checks/explain.report.json"), ("q3/explainers.json", "checks/q3.report.json")],
    "profiles.json": [("profiles/profiles.json", "checks/profiles.report.json")],
    "controversies.json": [("polemicas/polemicas.json", "checks/polemicas.report.json")],
}
CLAIM_KEYS = ("whatItIs", "inPractice", "argsFor", "argsAgainst", "nuance", "presents", "experience", "proposals", "claims", "response")


def build_claim_files(evidence_ids):
    stats = {}
    for out, parts in CLAIM_FILES.items():
        items, ok = [], set()
        for rel, rep in parts:
            part, report = load(rel), load(rep)
            if part is None or report is None:
                continue
            items += part
            ok |= passed_ids(report)
        if not items:
            stats[out] = "pending"
            continue
        kept_claims = 0
        for item in items:
            for key in CLAIM_KEYS:
                if key in item:
                    item[key] = [c for c in item[key] if c["checkId"] in ok]
                    kept_claims += len(item[key])
            if "defends" in item:
                item["defends"] = [i for i in item["defends"] if i in evidence_ids]
        (DATA / out).write_text(json.dumps(items, ensure_ascii=False, indent=1))
        stats[out] = kept_claims
    axes = (load("explain/axes.json") or []) + (load("q3/axes.json") or [])
    if axes:
        (DATA / "axes.json").write_text(json.dumps(axes, ensure_ascii=False, indent=1))
    round2, r2rep = load("round2/round2.json"), load("checks/round2.report.json")
    if round2 is not None and r2rep is not None:
        rows = r2rep.get("rows", [])
        if rows and all(r["status"] == "PASS" for r in rows):
            (DATA / "round2.json").write_text(json.dumps(round2, ensure_ascii=False, indent=1))
            stats["round2.json"] = "shipped"
        else:
            stats["round2.json"] = "check failing, not shipped"
    news_ok = passed_ids(load("checks/news5.report.json") or {})
    endorsements = load("news5/endorsements.json")
    if endorsements is not None:
        for item in endorsements:
            item["claims"] = [c for c in item["claims"] if c["checkId"] in news_ok]
        endorsements = [e for e in endorsements if e["claims"]]
        (DATA / "endorsements.json").write_text(json.dumps(endorsements, ensure_ascii=False, indent=1))
        stats["endorsements.json"] = len(endorsements)
    polls2 = load("news5/polls2.json")
    if polls2 is not None:
        polls2 = [p for p in polls2 if p["id"] in news_ok or all(f"{p['id']}:{r['label']}" in news_ok for r in p["results"])]
        (DATA / "polls2.json").write_text(json.dumps(polls2, ensure_ascii=False, indent=1))
        stats["polls2.json"] = len(polls2)
    countries, crep = load("countries/countries.json"), load("checks/countries.report.json")
    if countries is not None and crep is not None:
        ok = passed_ids(crep)
        rows = [c for c in countries if c["checkId"] in ok or c["id"] in ok]
        (DATA / "countries.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
        stats["countries.json"] = len(rows)
    return stats


if __name__ == "__main__":
    build()
    shipped = {e["id"] for e in json.loads((DATA / "evidence.json").read_text())}
    print(json.dumps(build_claim_files(shipped), ensure_ascii=False))
