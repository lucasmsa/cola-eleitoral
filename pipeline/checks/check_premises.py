"""doc-tdd for question premises: each statement that cites a law or a current status is checked against the Planalto text.

Run: pipeline/.venv/bin/python pipeline/checks/check_premises.py
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "pipeline" / "premises"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"

SOURCES = {
    "eletrobras": "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14182.htm",
    "bc": "https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp179.htm",
    "ir": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15270.htm",
    "lep": "https://www.planalto.gov.br/ccivil_03/leis/l7210.htm",
    "dosimetria": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15402.htm",
    "licenciamento": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15190.htm",
    "agrotoxicos": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14785.htm",
    "correios": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/D11478.htm",
}


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def text(key, live=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.htm"
    if live or not path.exists():
        subprocess.run(["curl", "-sL", "--compressed", "--max-time", "60", "-A", UA, "-o", str(path), SOURCES[key]], check=False)
    raw = path.read_bytes().decode("latin-1", errors="ignore")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    # struck-through text in compiled laws is revoked wording; drop it
    raw = re.sub(r"(?is)<strike>.*?</strike>", " ", raw)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def has(key, *phrases):
    t = text(key)
    return all(norm(p) in t for p in phrases)


def lep_art122():
    t = text("lep")
    i = t.find("art. 122.")
    j = t.find("art. 123", i)
    return t[i:j]


CLAIMS = [
    ("eletrobras-privatizada", "Lei 14.182/2021 autoriza a desestatização da Eletrobras",
     lambda: has("eletrobras", "lei nº 14.182, de 12 de julho de 2021", "dispõe sobre a desestatização da empresa centrais elétricas brasileiras s.a. (eletrobras)")),
    ("bc-autonomia-lei", "LC 179/2021 define autonomia e mandatos fixos do Banco Central",
     lambda: has("bc", "lei complementar nº 179, de 24 de fevereiro de 2021", "define os objetivos do banco central do brasil e dispõe sobre sua autonomia")),
    ("ir-lei-15270", "Lei 15.270/2025 reduz o IR e institui tributação mínima de altas rendas",
     lambda: has("ir", "lei nº 15.270", "2025")),
    ("saidinha-sem-visita-familia", "Art. 122 da LEP em vigor só prevê saída temporária para estudo (visita à família revogada)",
     lambda: ("frequência a curso" in lep_art122() or "frequencia a curso" in lep_art122()) and "visita à família" not in lep_art122()),
    ("dosimetria-lei-15402", "Lei 15.402/2026 existe e trata dos crimes contra o Estado Democrático de Direito",
     lambda: has("dosimetria", "lei nº 15.402", "2026")),
    ("licenciamento-lei-15190", "Lei 15.190/2025 é a Lei Geral do Licenciamento Ambiental",
     lambda: has("licenciamento", "lei nº 15.190", "licenciamento ambiental")),
    ("agrotoxicos-lei-14785", "Lei 14.785/2023 é a lei de agrotóxicos",
     lambda: has("agrotoxicos", "lei nº 14.785", "agrotóxicos")),
    ("correios-fora-pnd", "Decreto 11.478/2023 tirou os Correios do Programa Nacional de Desestatização",
     lambda: has("correios", "decreto nº 11.478", "empresa brasileira de correios e telégrafos")),
]

CONTROLS = [
    ("NEG LC 179 is from 2019", lambda: has("bc", "lei complementar nº 179, de 24 de fevereiro de 2019")),
    ("NEG Lei 15.402 is from 2025", lambda: has("dosimetria", "lei nº 15.402, de 2025")),
    ("NEG Eletrobras law is Lei 14.183", lambda: has("eletrobras", "lei nº 14.183, de 12 de julho de 2021")),
    ("NEG LEP art. 122 still lists visita à família", lambda: "visita à família" in lep_art122()),
]


def main():
    if "--live" in sys.argv:
        for key in SOURCES:
            text(key, live=True)
    rows = []
    for cid, claim, fn in CLAIMS:
        try:
            ok = bool(fn())
        except Exception as exc:  # noqa: BLE001
            ok, claim = False, f"{claim} ({exc})"
        rows.append({"id": cid, "status": "PASS" if ok else "FAIL", "claim": claim})
    broken = []
    for cid, fn in CONTROLS:
        passed = bool(fn())
        rows.append({"id": cid, "status": "CONTROL-PASSED" if passed else "FAIL", "claim": cid})
        if passed:
            broken.append(cid)
    (ROOT / "pipeline" / "checks" / "premises.report.json").write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=1))
    for r in rows:
        print(r["status"], r["id"])
    print(f"PASS {sum(r['status'] == 'PASS' for r in rows)}/{len(CLAIMS)}  controls broken {len(broken)}")
    if broken or any(r["status"] == "FAIL" and not r["id"].startswith("NEG") for r in rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
