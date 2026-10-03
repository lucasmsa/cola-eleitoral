"""doc-tdd for question bank v3 (pipeline/q3).

Checks every explainer claim (support verbatim in its cached source, no 2026 ballot names), every
evidence row (plan quote on the stated PDF page of the right candidate's plan; roll-call position
re-derived from the cached Câmara/Senado API response with the question's sign; Planalto phrases),
and the question/option/axis shapes. Negative controls must FAIL or the harness is void.
Writes pipeline/checks/q3.report.json and, when the harness is OK, PASS-only outputs in pipeline/q3/.
"""
import copy
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
Q3 = ROOT / "pipeline" / "q3"
sys.path.insert(0, str(Q3))
sys.path.insert(0, str(ROOT / "pipeline" / "record"))
import tools  # noqa: E402
from fetch import get  # noqa: E402

C = "https://dadosabertos.camara.leg.br/api/v2"
STANCES = {-1, -0.5, 0, 0.5, 1}
OFFICES = {"presidente", "governador", "senador", "deputado_federal", "deputado_estadual"}
AREAS = {"economia", "seguranca", "social", "ambiente"}
PLAN_MAP = json.loads((ROOT / "pipeline" / "platform" / "plan_map.json").read_text())
_pdf_pages = {}


def norm(s):
    s = tools.norm(s)
    return s.replace("­", "")


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def ballot_names():
    names = set()
    for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text()):
        if c["office"] not in ("presidente", "governador", "senador"):
            continue
        for n in [c["ballotName"]] + c["runningMates"]:
            n = fold(re.sub(r"^(DR\.?|ESCRITOR|VETERINÁRIO|CORONEL|MAJOR)\s+", "", n.strip()))
            if len(n) >= 4:
                names.add(n)
    return names


BALLOT = ballot_names()


def names_ballot(text):
    t = fold(text)
    return [n for n in BALLOT if re.search(r"\b" + re.escape(n) + r"\b", t)]


def source_text(url, live=False):
    return norm(tools.fetch(url, force=live))


def check_claim(c, live=False):
    why = []
    if norm(c["support"]) not in source_text(c["source"]["url"], live):
        why.append("support not in source" + (" (live)" if live else ""))
    sup_nums = set(re.findall(r"\d+(?:[.,]\d+)*", c["support"]))
    missing = [n for n in re.findall(r"\d+(?:[.,]\d+)*", c["text"]) if n not in sup_nums]
    if missing:
        why.append(f"numbers in text not in support: {missing}")
    hits = names_ballot(c["text"] + " " + c["support"])
    if hits:
        why.append(f"names a 2026 ballot candidate: {hits}")
    return why


def pdf_page(pdf, page):
    key = (pdf, page)
    if key not in _pdf_pages:
        import pypdf
        r = pypdf.PdfReader(str(ROOT / "public" / "plans" / pdf))
        _pdf_pages[key] = norm(r.pages[page - 1].extract_text() or "") if 0 < page <= len(r.pages) else ""
    return _pdf_pages[key]


def check_plan(e):
    ref = e["_ref"]
    why = []
    owner = PLAN_MAP.get(ref["pdf"], {}).get("candidateId")
    if owner != e["subject"]["id"]:
        why.append(f"plan {ref['pdf']} belongs to {owner}, not {e['subject']['id']}")
    if norm(e["quote"]) not in pdf_page(ref["pdf"], ref["page"]):
        why.append(f"quote not on PDF page {ref['page']}")
    if f"p. {ref['page']}" not in e["detail"]:
        why.append("detail page differs")
    return why


def word_position(word):
    return {"Sim": 1, "Não": -1, "Abstenção": 0, "Obstrução": 0}.get(word)


def check_vote(e):
    ref = e["_ref"]
    t = ref["type"]
    if t == "camara_vote":
        votos = get(f"{C}/votacoes/{ref['votacao']}/votos")["dados"]
        v = next((x for x in votos if x["deputado_"]["id"] == ref["parlId"]), None)
        word = v["tipoVoto"] if v else None
    elif t == "camara_orient":
        ors = get(f"{C}/votacoes/{ref['votacao']}/orientacoes")["dados"]
        o = next((x for x in ors if x["siglaPartidoBloco"] == ref["sigla"]), None)
        word = o["orientacaoVoto"] if o else None
    elif t == "senado_vote":
        vot = next(x for x in get(ref["url"]) if x["codigoSessaoVotacao"] == ref["codigoSessaoVotacao"])
        v = next((x for x in vot["votos"] if x["codigoParlamentar"] == ref["parlId"]), None)
        word = v["siglaVotoParlamentar"] if v else None
    else:
        return [f"unknown ref {t}"]
    base = word_position(word)
    if base is None:
        return [f"source vote '{word}' not mappable"]
    expected = base * ref["sign"]
    return [] if expected == e["position"] else [f"position {e['position']} but source says {word} (sign {ref['sign']})"]


def check_planalto(e):
    text = source_text(e["_ref"]["url"])
    missing = [p for p in e["_ref"]["phrases"] if norm(p) not in text]
    return [f"phrases not in source: {missing}"] if missing else []


def check_evidence(e):
    t = e["_ref"]["type"]
    if t == "plan":
        return check_plan(e)
    if t == "planalto":
        return check_planalto(e)
    return check_vote(e)


def check_question(q, axes_by_q):
    why = []
    if q["area"] not in AREAS:
        why.append("bad area")
    if not set(q["offices"]) <= OFFICES:
        why.append("bad office")
    opts = q.get("options") or []
    if opts and (len(opts) < 4 or {o["value"] for o in opts} - STANCES or len({o["value"] for o in opts}) != len(opts)):
        why.append("bad options scale")
    snippets = []
    for snippet, src in q.get("contextChecks") or []:
        if norm(snippet) not in source_text(src["url"]):
            why.append(f"context snippet not in source: {snippet[:50]}")
        snippets.append(snippet)
    nums = set(re.findall(r"\d+(?:[.,]\d+)*", " ".join(snippets)))
    missing = [n for n in re.findall(r"\d+(?:[.,]\d+)*", q["context"]) if n not in nums]
    if missing or not snippets:
        why.append(f"context numbers not in snippets: {missing}" if snippets else "context has no checked snippet")
    a = axes_by_q.get(q["id"])
    if a and (a["axis"] not in ("economico", "social") or a["direction"] not in (1, -1) or not a["rationale"]):
        why.append("bad axis")
    return why


def controls(explainers, evidence):
    out = []
    claim = copy.deepcopy(explainers[0]["whatItIs"][0])
    claim["support"] = "A reeleição foi criada em 1988 pela Assembleia Constituinte por unanimidade."
    out.append(("NEG fabricated support snippet", check_claim(claim)))
    fort = next(e for e in explainers if e["questionId"] == "q3-grandes-fortunas")["argsAgainst"][0]
    moved = copy.deepcopy(fort)
    moved["source"] = explainers[0]["whatItIs"][0]["source"]
    out.append(("NEG real support moved to another source", check_claim(moved)))
    named = copy.deepcopy(explainers[0]["argsAgainst"][0])
    named["text"] = "Lula defende manter a reeleição."
    out.append(("NEG explainer names a ballot candidate", check_claim(named)))
    cam = copy.deepcopy(next(e for e in evidence if e["_ref"]["type"] == "camara_vote"))
    cam["position"] = -cam["position"] or 1
    out.append(("NEG flipped Câmara vote", check_evidence(cam)))
    sen = copy.deepcopy(next(e for e in evidence if e["_ref"]["type"] == "senado_vote" and e["questionId"] == "q3-maconha-uso"))
    sen["position"] = -sen["position"]
    out.append(("NEG maconha vote read without the sign flip", check_evidence(sen)))
    plan = copy.deepcopy(next(e for e in evidence if e["_ref"]["type"] == "plan"))
    plan["_ref"]["page"] += 3
    out.append(("NEG plan quote on the wrong page", check_evidence(plan)))
    other = copy.deepcopy(next(e for e in evidence if e["_ref"]["type"] == "plan" and e["subject"]["id"] == "presidente-21"))
    other["subject"]["id"] = "presidente-13"
    out.append(("NEG plan quote attributed to another candidate", check_evidence(other)))
    nums = copy.deepcopy(explainers[0]["inPractice"][2])
    nums["text"] = nums["text"].replace("49", "41")
    out.append(("NEG wrong number in claim text", check_claim(nums)))
    ctxq = copy.deepcopy(questions_for_controls[0])
    ctxq["context"] = ctxq["context"].replace("2025", "2023")
    out.append(("NEG wrong year in question context", check_question(ctxq, {})))
    return out


questions_for_controls = []


def main():
    live = "--live" in sys.argv
    questions = json.loads((Q3 / "questions.draft.json").read_text())
    explainers = json.loads((Q3 / "explainers.draft.json").read_text())
    axes = json.loads((Q3 / "axes.json").read_text())
    evidence = json.loads((Q3 / "evidence.draft.json").read_text())
    options = json.loads((Q3 / "options.json").read_text())
    axes_by_q = {a["questionId"]: a for a in axes}
    questions_for_controls.extend(questions)
    rows = []

    for q in questions:
        why = check_question(q, axes_by_q)
        rows.append({"id": f"q3-question-{q['id']}", "status": "FAIL" if why else "PASS", "claim": q["statement"], "why": why})
    for qid, opts in options.items():
        bad = len(opts) < 4 or {o["value"] for o in opts} - STANCES
        rows.append({"id": f"q3-options-{qid}", "status": "FAIL" if bad else "PASS", "claim": f"escala de respostas de {qid}", "why": []})

    random.seed(3)
    for exp in explainers:
        for section, claims in exp.items():
            if section == "questionId":
                continue
            for c in claims:
                why = check_claim(c)
                if not why and live and random.random() < 0.25:
                    why = check_claim(c, live=True)
                rows.append({"id": c["checkId"], "status": "FAIL" if why else "PASS", "claim": c["text"], "why": why})
    for e in evidence:
        why = check_evidence(e)
        rows.append({"id": e["id"], "status": "FAIL" if why else "PASS", "claim": e["detail"], "why": why})

    ctl = controls(explainers, evidence)
    harness_ok = all(why for _, why in ctl)
    report = {"harness_ok": harness_ok, "rows": rows,
              "controls": [{"id": n, "status": "FAIL" if why else "CONTROL-PASSED", "why": why} for n, why in ctl]}
    (ROOT / "pipeline" / "checks" / "q3.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))

    passed = {r["id"] for r in rows if r["status"] == "PASS"}
    for r in rows:
        if r["status"] != "PASS":
            print("FAIL", r["id"], r["why"])
    for n, why in ctl:
        print("CONTROL", "FAIL (ok)" if why else "PASSED (HARNESS BROKEN)", n, why[:1])
    print(f"rows={len(rows)} PASS={len(passed)} FAIL={len(rows) - len(passed)} controls={len(ctl)} harness_ok={harness_ok}")
    if not harness_ok:
        sys.exit(1)

    (Q3 / "questions.json").write_text(json.dumps(
        [{k: v for k, v in q.items() if k != "contextChecks"} for q in questions if f"q3-question-{q['id']}" in passed],
        ensure_ascii=False, indent=1))
    kept = []
    for exp in explainers:
        out = {"questionId": exp["questionId"]}
        for section, claims in exp.items():
            if section != "questionId":
                out[section] = [c for c in claims if c["checkId"] in passed]
        kept.append(out)
    (Q3 / "explainers.json").write_text(json.dumps(kept, ensure_ascii=False, indent=1))
    (Q3 / "evidence.json").write_text(json.dumps(
        [{k: v for k, v in e.items() if k != "_ref"} for e in evidence if e["id"] in passed], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
