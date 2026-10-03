"""Prints questions-with-evidence per majoritarian candidate, split record/platform."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
cands = json.loads((DATA / "candidates.json").read_text())
questions = json.loads((DATA / "questions.json").read_text())
evidence = json.loads((DATA / "evidence.json").read_text())

for office in ("governador", "senador", "presidente"):
    applicable = {q["id"] for q in questions if office in q["offices"]}
    print(f"\n{office} ({len(applicable)} perguntas)")
    for c in (c for c in cands if c["office"] == office):
        own = [e for e in evidence if e["subject"]["id"] == c["id"] and e["questionId"] in applicable]
        rec = {e["questionId"] for e in own if e["kind"] == "record"}
        plat = {e["questionId"] for e in own if e["kind"] == "platform"}
        print(f"  {c['number']:>4} {c['ballotName'][:24]:<24} {len(rec | plat):>2} perguntas  (registro {len(rec)}, declaração {len(plat)})")
