"""doc-tdd for country stances.

Per row: (1) the support snippet and every extra snippet appear verbatim (normalized) in the cached
source; (2) a live re-fetch of a 25% sample still contains the main snippet; (3) the position is
re-derived from the snippets by a per-question rule and must match. Negative controls must FAIL.
Writes pipeline/countries/countries.json (PASS rows only) and pipeline/checks/countries.report.json.
"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline" / "countries"))
from fetch import norm, text  # noqa: E402
from rows import ROWS  # noqa: E402

ACCESSED = "2026-10-03"


def hours(s):
    words = {"quarenta horas": 40, "cuarenta horas": 40, "40 timmar": 40, "40 часов": 40,
             "cuarenta y dos (42) horas": 42, "cuarenta y ocho horas": 48, "forty hours in a week": 40,
             "40 hours per week": 40, "trente-cinq heures": 35, "average of 48 hours": 48}
    found = [v for k, v in words.items() if k in s]
    return min(found) if found else None


def derive(q, snippets):
    s = " ".join(snippets)
    if q == "eco-6x1":
        if "one and one-half times" in s or "quinto año" in s:
            return 0
        if "werktägliche arbeitszeit der arbeitnehmer darf acht stunden" in s:
            return -1
        h = hours(s)
        if h is None:
            return None
        return 1 if h <= 40 else 0 if h < 48 else -1
    if q == "seg-stf-mandato":
        if "president of the supreme people's court" in s:
            return 0
        if re.search(r"good behavio|age of|retirement age|retired upon|не ограничены", s):
            return -1
        if re.search(r"(nine|eight|ten|twelve) years|zwölf jahre", s):
            return 1
        return None
    if q == "soc-aborto":
        if "violación" in s and "riesgo vital" in s:
            return -1
        if "returned to the people" in s or "does not exceed twenty weeks" in s or "twenty-fourth week" in s:
            return 0
        if re.search(r"semana|weeks?|wochen|veckan|недель|interruption of pregnancy|semanas", s):
            return 1
        return None
    if q == "eco-bc-autonomo":
        if "directive" in s or "give the bank directions" in s or "give such directions to the bank" in s:
            return 0
        if re.search(r"autonom|autárquica|independent|no public authority may determine|fourteen years", s):
            return 1
        return None
    if q == "seg-drogas":
        if "lugares, vías" in s:
            return -1
        if re.search(r"a menos que justifique|eigenverbrauch|30 g of dried cannabis|administrative measures|в значительном размере", s):
            return 0
        if re.search(r"prisión|fängelse|unlawful for any person knowingly or intentionally to possess|it is an offence for a person to have a controll", s):
            return 1
        return None
    if q == "seg-maioridade":
        if "adult is liable to imprisonment" in s:
            return 0
        if re.search(r"as an adult|inimputáveis|no es punible el menor|шестнадцатилетнего|age of 16", s):
            return 1
        if re.search(r"menores de dieciocho|noch nicht achtzehn|menos de dieciocho", s):
            return -1
        return None
    if q == "seg-armas":
        if "right to keep arms at home" in s:
            return 0
        if "shall not be infringed" in s:
            return 1
        if re.search(r"good reason|bedürfnis", s):
            return -1
        return None
    if q == "eco-reforma-tributaria":
        if "without a vat" in s:
            return -1
        if re.search(r"valor añadido|valor agregado|umsatzsteuer|mervärdesskatt|goods and services tax|consumption tax|impuesto sobre las ventas|налога на добавленную стоимость", s):
            return 1
        return None
    if q == "eco-privatizacao":
        if "100% owned by the swedish state" in s:
            return -1
        if "investor-owned utilities served" in s:
            return 1
        return None
    if q == "amb-margem-equatorial":
        if "no se otorgarán" in s:
            return -1
        if "lease sales" in s:
            return 1
        return None
    if q == "q3-grandes-fortunas":
        if "abolish the wealth tax" in s:
            return -1
        if "patrimonio neto" in s:
            return 1
        return None
    if q == "soc-cotas":
        if "lack sufficiently focused and measurable objectives" in s:
            return -1
        if "admission to educational institutions" in s:
            return 1
        return None
    return None


SPELLED = {
    "2": ["two", "dos", "zwei", "två", "двух", "dos (2)"], "13": ["trece"], "15": ["fifteen", "пятнадцати"],
    "16": ["dieciséis", "sixteen", "шестнадцатилетнего", "age of 16", "16 anos"], "21": ["einundzwanzig"],
    "5": ["5-year", "five"], "1978": ["1978"], "72": ["72%"], "3": ["three", "tres", "drei", "tre", "três"], "6": ["six", "seis", "sechs"],
    "7": ["seven", "siete"], "8": ["eight", "ocho", "oito", "acht"], "9": ["nine", "nueve", "nove"],
    "10": ["ten", "diez", "dez", "zehn"], "12": ["twelve", "doce", "zwölf", "двенадцати", "doce años"],
    "14": ["fourteen", "catorce", "quatorze", "vierzehn", "четырнадцатилетнего", "age of 14"],
    "18": ["eighteen", "artonde", "dieciocho", "achtzehn"], "20": ["twenty", "veinte"],
    "24": ["twenty-four", "24"], "30": ["thirty", "30 g"], "40": ["forty", "cuarenta", "quarenta", "40 timmar", "40 часов"],
    "42": ["cuarenta y dos"], "44": ["cuarenta y cuatro"], "35": ["trente-cinq"], "48": ["cuarenta y ocho"], "50": ["one and one-half"], "65": ["sixty-five"],
    "70": ["семьдесят"], "75": ["seventy-five"],
}


def numbers_backed(detail, haystack):
    missing = []
    for tok in re.findall(r"\d[\d.:/]*\d|\d", detail):
        bare = tok.replace(".", "")
        forms = {tok, bare, tok.replace(".", ",")}
        if "/" in tok:
            forms |= {tok.split("/")[0], tok.split("/")[0].replace(".", "")}
        if ":" in tok:
            forms |= {tok.replace(":", "")}
        forms |= set(SPELLED.get(bare, []))
        if not any(norm(f) in haystack for f in forms):
            missing.append(tok)
    return missing


def check(row, live=False):
    country, q, position, detail, url, support, label, *rest = row
    extras = rest[0] if rest else []
    why = []
    main_text = text(url)
    snippets = [norm(support)]
    if norm(support) not in main_text:
        why.append("support not in cached source")
    for ex in extras:
        ex_url, ex_snip = (ex if isinstance(ex, tuple) else (url, ex))
        snippets.append(norm(ex_snip))
        if norm(ex_snip) not in text(ex_url):
            why.append(f"extra snippet not in source: {ex_snip[:50]}")
    haystack = main_text + " " + norm(url) + " " + norm(label) + " " + " ".join(
        text(ex[0]) if isinstance(ex, tuple) else "" for ex in extras)
    missing = numbers_backed(detail, haystack)
    if missing:
        why.append(f"numbers in detail not in source: {missing}")
    derived = derive(q, snippets)
    if derived is None:
        why.append("no derivation rule matched")
    elif derived != position:
        why.append(f"position {position} but rule derives {derived}")
    live_ok = None
    if live and not why:
        try:
            live_ok = norm(support) in text(url, refresh=True)
        except Exception:
            live_ok = False
        if live_ok is False:
            why.append("support not in live source")
    return why, live_ok


def row_id(row):
    country, q = row[0], row[1]
    return f"ctry-{re.sub(r'[^a-z]', '', norm(country))}-{q}-{hashlib.sha1(row[5].encode()).hexdigest()[:6]}"


def controls():
    by = {(r[0], r[1]): r for r in ROWS}
    se = by[("Suécia", "soc-aborto")]
    ar = by[("Argentina", "soc-aborto")]
    uy = by[("Uruguai", "soc-aborto")]
    ru = by[("Rússia", "seg-stf-mandato")]
    es = by[("Espanha", "eco-6x1")]
    inq = by[("Índia", "soc-cotas")]
    ukd = by[("Reino Unido", "seg-drogas")]
    jbc = by[("Japão", "eco-bc-autonomo")]
    return [
        ("NEG fabricated snippet: Suécia aborto até 12 semanas", (se[0], se[1], se[2], se[3], se[4], "före utgången av tolfte havandeskapsveckan", se[6])),
        ("NEG other country's law: Argentina text on Uruguay page", (uy[0], uy[1], uy[2], uy[3], uy[4], ar[5], uy[6])),
        ("NEG wrong age: Rússia court age 75", (ru[0], ru[1], ru[2], ru[3], ru[4], ru[5], ru[6], ["предельный возраст пребывания в должности судьи конституционного суда российской федерации - семьдесят пять лет"])),
        ("NEG flipped position: Espanha 40h as -1", (es[0], es[1], -1, es[3], es[4], es[5], es[6])),
        ("NEG flipped position: Índia cotas as -1", (inq[0], inq[1], -1, inq[3], inq[4], inq[5], inq[6])),
        ("NEG wrong number in detail: Suécia aborto 22ª semana", (se[0], se[1], se[2], se[3].replace("18ª", "22ª"), se[4], se[5], se[6])),
        ("NEG flipped position: Reino Unido drogas as -1", (ukd[0], ukd[1], -1, ukd[3], ukd[4], ukd[5], ukd[6], ukd[7])),
        ("NEG other country's law: Japão BoJ snippet on the RBI Act", ("Índia", jbc[1], jbc[2], jbc[3], by[("Índia", "eco-bc-autonomo")][4], jbc[5], jbc[6])),
    ]


def main():
    random.seed(11)
    report, shipped = [], []
    for row in ROWS:
        rid = row_id(row)
        why, live = check(row, live=random.random() < 0.25)
        status = "PASS" if not why else "FAIL"
        report.append({"id": rid, "status": status, "claim": f"{row[0]} / {row[1]}: {row[3]}", "why": why, "live": live})
        if status == "PASS":
            shipped.append({
                "id": rid, "country": row[0], "questionId": row[1], "position": row[2], "detail": row[3],
                "support": row[5], "source": {"url": row[4], "accessed": ACCESSED, "label": row[6]}, "checkId": rid,
            })
    broken = []
    for name, row in controls():
        why, _ = check(row)
        ok = bool(why)
        report.append({"id": name, "status": "CONTROL-FAIL(ok)" if ok else "CONTROL-PASSED", "claim": name, "why": why})
        if not ok:
            broken.append(name)
    for r in report:
        if r["status"] != "PASS":
            print(r["status"], r["id"], r.get("why"))
    passed = sum(r["status"] == "PASS" for r in report)
    print(f"PASS {passed}/{len(ROWS)}  controls broken {len(broken)}")
    (ROOT / "pipeline" / "checks" / "countries.report.json").write_text(json.dumps({"rows": report, "harness_ok": not broken}, ensure_ascii=False, indent=1))
    if broken:
        sys.exit("HARNESS BROKEN")
    (ROOT / "pipeline" / "countries" / "countries.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
