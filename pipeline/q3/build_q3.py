"""Builds q3 drafts: questions, explainers, axes, option scales and evidence (with _ref for the check).

Roll calls reuse pipeline/record/build_record.py so subject matching and party-list mapping stay identical.
Run: pipeline/.venv/bin/python pipeline/q3/build_q3.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PIPE, "record"))

import data  # noqa: E402
import build_record as br  # noqa: E402

PLAN_MAP = json.load(open(os.path.join(PIPE, "platform", "plan_map.json")))


def plan_url(pdf):
    return PLAN_MAP[pdf]["url"]


def questions_and_explainers():
    questions, explainers, axes = [], [], []
    for q in data.QUESTIONS:
        questions.append({k: q[k] for k in ("id", "area", "offices", "statement", "context", "contextChecks", "sources", "options")})
        exp = {"questionId": q["id"]}
        for section, claims in q["explainer"].items():
            exp[section] = [dict(c, checkId=f"q3-exp-{q['id']}-{section}-{i}") for i, c in enumerate(claims)]
        explainers.append(exp)
        if q["axis"]:
            axes.append(dict(q["axis"], questionId=q["id"]))
    return questions, explainers, axes


def platform_rows():
    rows = []
    for cid, qid, pos, pdf, page, quote, detail in data.PLATFORM:
        eid = f"q3-plat-{cid}-{qid}"
        rows.append({
            "id": eid, "subject": {"type": "candidate", "id": cid}, "questionId": qid, "kind": "platform",
            "position": pos, "detail": detail, "quote": quote, "page": page, "date": "2026-08-15",
            "source": {"url": plan_url(pdf), "accessed": data.ACC,
                       "label": f"Plano de governo registrado no TSE ({PLAN_MAP[pdf]['name']}, p. {page}), arquivo {pdf}"},
            "checkId": eid, "lowDiscrimination": False,
            "_ref": {"type": "plan", "pdf": pdf, "page": page, "candidateId": cid},
        })
    return rows


def executive_rows():
    rows = []
    for cid, qid, pos, src, date, detail, phrases in data.EXECUTIVE:
        eid = f"q3-exec-{cid}-{qid}"
        rows.append({
            "id": eid, "subject": {"type": "candidate", "id": cid}, "questionId": qid, "kind": "record",
            "position": pos, "detail": detail, "date": date, "source": src, "checkId": eid,
            "lowDiscrimination": False, "_ref": {"type": "planalto", "url": src["url"], "phrases": phrases},
        })
    return rows


def roll_call_rows():
    subjects = json.load(open(os.path.join(PIPE, "record", "subjects.json")))
    br.CAMARA_VOTES = [(qid, vid, label, low) for qid, vid, label, sign, low in data.CAMARA]
    br.SENADO_VOTES = [(qid, prop, cod, label) for qid, prop, cod, label, sign in data.SENADO]
    sign_by_vote = {vid: sign for _, vid, _, sign, _ in data.CAMARA}
    sign_by_vote.update({str(cod): sign for _, _, cod, _, sign in data.SENADO})
    notes, votacoes = [], []
    ev = br.camara_evidence(subjects, notes, votacoes) + br.senado_evidence(subjects, notes, votacoes)
    ev = br.fix_pt_grammar(ev)
    for e in ev:
        ref = e["_ref"]
        vote_id = str(ref.get("votacao") or ref.get("codigoSessaoVotacao"))
        sign = sign_by_vote[vote_id]
        e["position"] = e["position"] * sign
        ref["sign"] = sign
        e["id"] = e["checkId"] = "q3-" + e["id"]
    json.dump(votacoes, open(os.path.join(HERE, "votacoes.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(notes, open(os.path.join(HERE, "notes.json"), "w"), ensure_ascii=False, indent=1)
    return ev


def main():
    questions, explainers, axes = questions_and_explainers()
    evidence = platform_rows() + executive_rows() + roll_call_rows()
    out = {
        "questions.draft.json": questions, "explainers.draft.json": explainers, "axes.json": axes,
        "options.json": data.OPTIONS_EXISTING, "evidence.draft.json": evidence,
    }
    for name, obj in out.items():
        json.dump(obj, open(os.path.join(HERE, name), "w"), ensure_ascii=False, indent=1)
    print(f"questions={len(questions)} claims={sum(len(e[k]) for e in explainers for k in e if k != 'questionId')} "
          f"axes={len(axes)} evidence={len(evidence)}")


if __name__ == "__main__":
    main()
