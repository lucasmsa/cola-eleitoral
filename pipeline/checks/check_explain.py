"""doc-tdd for question explainers.

Every claim's `support` must appear verbatim (normalized) in its source's cached text, inside a
window that mentions the question's topic. Attributed arguments must name someone who appears near
the snippet. Writes pipeline/checks/explain.report.json and, with --write, only PASS claims to
pipeline/explain/explainers.json plus pipeline/explain/axes.json.
"""
import importlib
import json
import random
import re
import unicodedata
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "pipeline" / "explain"
sys.path.insert(0, str(EXP))
import tools  # noqa: E402

MODULES = ["data_eco", "data_seg", "data_soc", "data_amb", "data_pb", "data_new"]
SECTIONS = ["whatItIs", "inPractice", "argsFor", "argsAgainst", "nuance"]
ATTRIBUTED = {"argsFor", "argsAgainst"}
ACCESSED = "2026-10-03"
TOPIC_WINDOW = 2500
NAME_WINDOW = 900
STOP = {"O", "A", "Os", "As", "Para", "Pela", "Pelo", "Segundo", "Em", "No", "Na", "Um", "Uma", "Se", "Mesmo",
        "Representantes", "Representante", "Parte", "Há", "Quase", "Boa", "Esse", "Essa", "Isso", "Com", "Sem",
        "Todo", "Itens", "Dividendos", "Ministério", "Economia", "Estado", "Constituição", "Lei", "Congresso",
        "Câmara", "Senado", "Nacional", "Federal", "Supremo", "Tribunal", "Brasil", "União", "Paraíba", "IR",
        "BC", "PT", "PL", "Novo", "Psol", "PCdoB", "Já", "Mas", "E", "De", "Do", "Da", "Ao", "Na", "Nas", "Nos",
        "Quem", "Pela", "Também", "Ainda", "Assim", "Antes", "Depois", "Desde", "Entre", "Sobre", "Até"}


def norm(s):
    return tools.norm(s)


TITLES = r"^(DR\.?|DRª|DR°|DRº|ESCRITOR|VETERINÁRIO|CORONEL|MAJOR|CABO|SARGENTO|PASTOR|DELEGADO|PROFESSORA?)\s+"
# Same first name, different person: a ballot token followed by these words is someone else.
NOT_THE_CANDIDATE = {"sergio": "moro", "silvia": "waiapi"}


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def ballot_names():
    cands = json.loads((ROOT / "src" / "data" / "candidates.json").read_text())
    names = set()
    for c in cands:
        majoritarian = c["office"] in ("presidente", "governador", "senador")
        for n in [c["ballotName"]] + c["runningMates"]:
            n = fold(re.sub(TITLES, "", n.strip()))
            if len(n) >= 4 and (" " in n or majoritarian):
                names.add(n)
    return names


def ballot_hit(text, names):
    t = fold(text)
    for n in names:
        for m in re.finditer(r"\b" + re.escape(n) + r"\b", t):
            follow = t[m.end():m.end() + 12].strip()
            if NOT_THE_CANDIDATE.get(n) and follow.startswith(NOT_THE_CANDIDATE[n]):
                continue
            return n
    return None


def topic_words():
    out = {}
    for m in MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError:
            continue
        out.update(getattr(mod, "TOPICS", {}))
    return out


def load():
    sources, explainers, axes = {}, {}, []
    for m in MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError:
            continue
        for k, v in mod.SOURCES.items():
            if k in sources and sources[k] != v:
                raise SystemExit(f"source key clash: {k}")
            sources[k] = v
        explainers.update(mod.EXPLAINERS)
        axes.extend(getattr(mod, "AXES", []))
    return sources, explainers, axes


def names_in(text):
    toks = re.findall(r"\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõçü]+)\b", text)
    return [t for t in toks if t not in STOP and len(t) > 2]


BALLOT = None


def check_claim(qid, section, claim, sources, topics, live=False):
    global BALLOT
    if BALLOT is None:
        BALLOT = ballot_names()
    text, support, key = claim
    why = []
    hit = ballot_hit(text + " " + support, BALLOT)
    if hit:
        why.append(f"names a 2026 ballot person: {hit}")
    if key not in sources:
        return "FAIL", ["unknown source key"]
    url = sources[key][0]
    if len(support) > 300:
        why.append("support over 300 chars")
    page = norm(tools.fetch(url, force=live))
    snip = norm(support)
    pos = page.find(snip)
    if pos < 0:
        return "FAIL", why + ["support not in " + ("live" if live else "cached") + " source"]
    words = [norm(w) for w in topics.get(qid, [])]
    win = page[max(0, pos - TOPIC_WINDOW): pos + len(snip) + TOPIC_WINDOW]
    if words and not any(w in win for w in words):
        why.append("no topic word near support")
    if section in ATTRIBUTED:
        ns = names_in(text)
        near = page[max(0, pos - NAME_WINDOW): pos + len(snip) + NAME_WINDOW]
        if not ns:
            why.append("argument not attributed to anyone")
        elif not any(norm(n) in near for n in ns):
            why.append("named actor not near support: " + ",".join(ns))
    return ("FAIL" if why else "PASS"), why


def controls(explainers, sources, topics):
    qids = [q for q in explainers if explainers[q].get("argsFor") and explainers[q].get("argsAgainst")]
    a, b = qids[0], qids[1]
    fa, ag = explainers[a]["argsFor"][0], explainers[a]["argsAgainst"][0]
    other = next(k for k in sources if k != fa[2] and sources[k][0] != sources[fa[2]][0])
    return [
        ("NEG fabricated snippet", (a, "whatItIs", (fa[0], "esta frase foi inventada e não existe em fonte nenhuma do mundo", fa[2]))),
        ("NEG snippet moved to another question", (b, "whatItIs", explainers[a]["whatItIs"][0])),
        ("NEG swapped argsFor/argsAgainst attribution", (a, "argsFor", (ag[0], fa[1], fa[2]))),
        ("NEG wrong source URL", (a, "argsFor", (fa[0], fa[1], other))),
        ("NEG cites a 2026 candidate", ("seg-saidinha", "argsFor", ("O senador Flávio Bolsonaro disse que a saída põe a população em risco.",
          "o poder público coloca toda a população em risco", "sai-debate"))),
    ]


def main():
    sources, explainers, axes = load()
    topics = topic_words()
    random.seed(11)
    report, kept = [], {}
    for qid, ex in explainers.items():
        kept[qid] = {"questionId": qid}
        for section in SECTIONS:
            kept[qid][section] = []
            for i, claim in enumerate(ex.get(section, [])):
                cid = f"exp-{qid}-{section}-{i}"
                live = "--live" in sys.argv and random.random() < 0.2
                status, why = check_claim(qid, section, claim, sources, topics, live=live)
                report.append({"id": cid, "status": status, "claim": claim[0], "why": why, "live": live})
                if status == "PASS":
                    url, label = sources[claim[2]]
                    kept[qid][section].append({"text": claim[0], "support": claim[1],
                                               "source": {"url": url, "accessed": ACCESSED, "label": label},
                                               "checkId": cid})
        n = min(len(kept[qid]["argsFor"]), len(kept[qid]["argsAgainst"]))
        if len(kept[qid]["argsFor"]) != len(kept[qid]["argsAgainst"]):
            report.append({"id": f"balance-{qid}", "status": "TRIMMED", "claim": f"argsFor/argsAgainst trimmed to {n} each"})
        kept[qid]["argsFor"] = kept[qid]["argsFor"][:n]
        kept[qid]["argsAgainst"] = kept[qid]["argsAgainst"][:n]
    bad = []
    for name, (qid, section, claim) in controls(explainers, sources, topics):
        status, why = check_claim(qid, section, claim, sources, topics)
        report.append({"id": name, "status": "CONTROL-PASSED" if status == "PASS" else "FAIL", "claim": name, "why": why})
        if status == "PASS":
            bad.append(name)
    qids = set(explainers)
    axis_rows = [a for a in axes if a["questionId"] in qids]
    for a in axis_rows:
        ok = a["axis"] in ("economico", "social") and a["direction"] in (1, -1) and a.get("rationale")
        report.append({"id": f"axis-{a['questionId']}", "status": "PASS" if ok else "FAIL", "claim": a.get("rationale", "")})
    (ROOT / "pipeline" / "checks" / "explain.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    claims = [r for r in report if r["id"].startswith("exp-")]
    passed = sum(r["status"] == "PASS" for r in claims)
    print(f"questions={len(explainers)} claims={len(claims)} PASS={passed} FAIL={len(claims) - passed} "
          f"controls_ok={not bad} live={sum(r.get('live', False) for r in claims)}")
    for r in claims:
        if r["status"] != "PASS":
            print("FAIL", r["id"], r["why"])
    if bad:
        print("HARNESS BROKEN:", bad)
        sys.exit(1)
    if "--write" in sys.argv:
        (EXP / "explainers.json").write_text(json.dumps(list(kept.values()), ensure_ascii=False, indent=1))
        (EXP / "axes.json").write_text(json.dumps(axis_rows, ensure_ascii=False, indent=1))
        print("wrote", len(kept), "explainers,", len(axis_rows), "axes")


if __name__ == "__main__":
    main()
