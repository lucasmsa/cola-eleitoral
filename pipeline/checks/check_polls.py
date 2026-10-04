"""doc-tdd for polls: every number must appear next to its candidate's name in the cached source page.

Writes pipeline/checks/polls.report.json and src/data/polls.json (only polls whose every row passed).
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "pipeline" / "raw"
CACHE = RAW / "polls"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"
OFFICE = {"president": "presidente", "governor_PB": "governador", "senate_PB": "senador"}
WINDOW = 160


def page_text(url):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (re.sub(r"[^a-z0-9]+", "_", url.lower())[-120:] + ".html")
    if not path.exists() or path.stat().st_size < 2000:
        subprocess.run(["curl", "-sL", "-A", UA, "-o", str(path), url], check=False)
    raw = path.read_bytes().decode("utf-8", errors="ignore")
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def number_forms(pct):
    if pct == 0:
        return [r"(?<![\d,.])0\s?%", r"não pontu", r"sem pontuar"]
    if isinstance(pct, int):
        n = str(int(pct))
        return [rf"(?<![\d,.]){n}(?:\s?%| pontos| por cento)"]
    s = f"{pct}".replace(".", ",")
    return [rf"(?<![\d,.]){re.escape(s)}\s?%?", rf"(?<![\d,.]){re.escape(str(pct))}\s?%"]


def name_forms(label):
    words = [w for w in re.split(r"[\s/]+", label) if len(w) > 2 and w.lower() not in {"dr.", "major"}]
    return [re.escape(w) for w in words]


def near(text, label, pct):
    names = name_forms(label)
    if not names:
        return False
    for nm in names:
        for m in re.finditer(nm, text, flags=re.I):
            window = text[max(0, m.start() - WINDOW): m.end() + WINDOW]
            if any(re.search(f, window) for f in number_forms(pct)):
                return True
    return False


def main():
    polls = json.loads((RAW / "roster.json").read_text())["polls"]
    for p in polls["governor_PB"]:
        if p.get("institute") == "AtlasIntel":
            p["drop"] = "Fonte inconsistente: Poder360 traz 42,5% no título e 42,4% no corpo para Lucas Ribeiro; outros veículos trazem outros valores."
    final = json.loads((RAW / "polls_final.json").read_text())
    base = lambda name: re.split(r"[ /(]", name)[0].lower()
    for key, items in final.items():
        newer = {base(p["institute"]) for p in items}
        polls[key] = [p for p in polls.get(key, []) if base(p.get("institute", "")) not in newer] + items
    report, shipped = [], []
    controls = []
    for key, items in polls.items():
        for p in items:
            if not p.get("sources") or not p.get("results"):
                continue
            if p.get("drop"):
                report.append({"id": f"{key}:{p['institute']}", "status": "DROPPED", "claim": p["drop"]})
                continue
            url = p["sources"][0]["url"]
            text = page_text(url)
            rows = []
            for label, pct in p["results"].items():
                ok = near(text, label, pct)
                rid = f"{key}:{p['institute']}:{label}"
                rows.append(ok)
                report.append({"id": rid, "status": "PASS" if ok else "FAIL", "claim": f"{label} {pct}% ({p['institute']} {p['field']})", "source": url})
            norm_text = re.sub(r"\s+", " ", text)
            for meta in p.get("verifyMeta", []):
                ok = meta in norm_text
                rows.append(ok)
                report.append({"id": f"{key}:{p['institute']}:meta:{meta}", "status": "PASS" if ok else "FAIL", "claim": f"fonte contém '{meta}'", "source": url})
            if p.get("verifyMeta"):
                controls.append((f"NEG {key}:{p['institute']}: registration BR-99999/2026", "BR-99999/2026" in norm_text))
            first_label, first_pct = next(iter(p["results"].items()))
            controls.append((f"NEG {key}:{p['institute']}: {first_label} at {first_pct + 23}%", near(text, first_label, first_pct + 23)))
            controls.append((f"NEG {key}:{p['institute']}: Pablo Marçal 31%", near(text, "Pablo Marçal", 31)))
            if all(rows):
                start, _, end = p["field"].partition("/")
                end_full = start[: len(start) - len(end)] + end if end else start
                shipped.append({
                    "id": f"{OFFICE[key]}-{base(p['institute'])}-{start}",
                    "office": OFFICE[key],
                    "institute": p["institute"],
                    "fieldStart": start,
                    "fieldEnd": end_full,
                    "sample": p["n"],
                    "marginPp": float(re.sub(r"[^\d.]", "", p["moe"])),
                    "registration": p["tse"],
                    "results": [{"label": k, "pct": v} for k, v in p["results"].items()],
                    "source": {"url": url, "accessed": p["sources"][0]["accessed"], "label": "Imprensa"},
                    "verified": "press",
                })
    bad_controls = [c for c, ok in controls if ok]
    for c, ok in controls:
        report.append({"id": c, "status": "FAIL" if not ok else "CONTROL-PASSED", "claim": c})
    (ROOT / "pipeline" / "checks" / "polls.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    passed = sum(r["status"] == "PASS" for r in report)
    failed = [r for r in report if r["status"] == "FAIL" and not r["id"].startswith("NEG")]
    print(f"{passed} PASS, {len(failed)} FAIL, {len(controls)} controls, {len(bad_controls)} controls wrongly passed")
    for r in failed:
        print("FAIL", r["id"], r["claim"])
    if bad_controls:
        print("HARNESS BROKEN:", bad_controls)
        sys.exit(1)
    if "--write" in sys.argv:
        (ROOT / "src" / "data" / "polls.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))
        print("wrote", len(shipped), "polls")


if __name__ == "__main__":
    main()
