"""doc-tdd for pipeline/pb2 (PB governor + Senate, second pass).

Every row is re-derived from the cached original-language YouTube caption track:
- the track is the channel's original pt ASR (`.pt-orig.vtt`; for files cached by pb2 the info.json caption URL has no `tlang=`),
- the video title names the candidate and no other candidate of the same race (single-guest interview),
- the upload date equals the row date and is 2025 or later,
- the quote appears in the normalized caption stream at the timestamp written in the source URL and label,
- the interviewer's question (anchor) appears within ANCHOR_WINDOW characters before the quote,
- the question applies to the candidate's office and the row is not a duplicate of shipped evidence.
`--live` re-reads title and upload date from YouTube. Negative controls must FAIL.
Writes checks/pb2.report.json and pb2/evidence.json (PASS rows only)."""
import json
import re
import subprocess
import sys
import unicodedata
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PB2 = ROOT / "pipeline" / "pb2"
sys.path.insert(0, str(PB2))
from caps import META, hms, norm, stream, ts_at, vtt_path  # noqa: E402
from draft import ACCESSED, ROWS  # noqa: E402

ANCHOR_WINDOW = 3500
CANDIDATES = {c["id"]: c for c in json.loads((ROOT / "src" / "data" / "candidates.json").read_text())}
QUESTIONS = {q["id"]: q for q in json.loads((ROOT / "src" / "data" / "questions.json").read_text())}
SHIPPED = [e for e in json.loads((ROOT / "src" / "data" / "evidence.json").read_text()) if not e["id"].startswith("pb2-")]
YTDLP = ROOT / "pipeline" / ".venv" / "bin" / "yt-dlp"


def fold(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def same_race_names(office, exclude):
    out = []
    for c in CANDIDATES.values():
        if c["office"] == office and c["id"] != exclude:
            out.append(fold(c["ballotName"]))
    return out


def original_track(video):
    p = vtt_path(video)
    if p is None or not p.name.endswith(".pt-orig.vtt"):
        return False
    info = p.with_name(f"{video}.info.json")
    if info.exists():
        caps = json.loads(info.read_text()).get("automatic_captions") or {}
        urls = [x.get("url", "") for x in caps.get("pt-orig", []) if x.get("ext") == "vtt"]
        return bool(urls) and not any("tlang=" in u for u in urls)
    return True


def live_meta(video):
    out = subprocess.run([str(YTDLP), "--no-update", "--skip-download", "--extractor-args", "youtube:lang=pt",
                          "--print", "%(title)s|%(upload_date)s", f"https://www.youtube.com/watch?v={video}"],
                         capture_output=True, text=True, timeout=120).stdout.strip().splitlines()
    if not out or "|" not in out[-1]:
        return None
    title, upload = out[-1].rsplit("|", 1)
    return {"title": title, "upload": upload}


def turn_text(video):
    """Normalized caption text that keeps speaker-turn markers (>>) as the token ' | '."""
    import html as _h
    from caps import cues
    parts = []
    for _, txt in cues(video):
        t = _h.unescape(txt).replace(">>", " | ")
        parts.append(re.sub(r"\s+", " ", t).strip().lower())
    return " ".join(parts)


def check_debate(row, meta):
    c = row["check"]
    if "debate" not in fold(meta["title"]):
        return False, "not a debate video"
    raw = turn_text(c["video"])
    q = raw.find(norm(row["quote"]))
    a = raw.rfind(norm(c["selfAnchor"]), 0, q if q >= 0 else 0)
    if q < 0 or a < 0:
        return False, "quote or self-identifying anchor not in captions"
    if " | " in raw[a:q]:
        return False, "speaker turn changes between anchor and quote"
    cue = raw.find(norm(c["moderatorCue"]), q)
    if cue < 0 or cue - q > 3000 or not any(fold(n) in fold(c["moderatorCue"]) for n in c["names"]):
        return False, "moderator cue naming the candidate not right after the quote"
    return True, ""


def check_yt(row, live):
    c = row["check"]
    v = c["video"]
    if not original_track(v):
        return False, "caption track is not the channel's original pt ASR"
    meta = (live_meta(v) if live else None) or META.get(v)
    if not meta:
        return False, "no video metadata"
    title = fold(meta["title"])
    cand = CANDIDATES[row["subject"]]
    if c.get("mode") == "debate":
        ok, why = check_debate(row, meta)
        if not ok:
            return ok, why
    else:
        if not any(fold(n) in title for n in c["names"]):
            return False, "video title does not name the candidate"
        if any(n in title for n in same_race_names(cand["office"], cand["id"])):
            return False, "title names another candidate of the same race"
    up = meta["upload"]
    if f"{up[:4]}-{up[4:6]}-{up[6:]}" != row["date"] or up < "20250101":
        return False, f"upload {up} != row date {row['date']} or older than 2025"
    text, starts = stream(v)
    i = text.find(norm(row["quote"]))
    if i < 0:
        return False, "quote not in captions"
    sec = ts_at(starts, i)
    if f"t={sec}s" not in row["source"]["url"] or hms(sec) not in row["source"]["label"]:
        return False, f"timestamp {hms(sec)} not in source url/label"
    if c.get("mode") != "debate" and norm(c["anchor"]) not in text[max(0, i - c.get("anchorWindow", ANCHOR_WINDOW)): i]:
        return False, "interviewer question not found before the quote"
    return True, f"caption match at {hms(sec)}"


def common(row):
    cand = CANDIDATES.get(row["subject"])
    q = QUESTIONS.get(row["questionId"])
    if not cand or not q:
        return False, "unknown candidate or question"
    if cand["office"] not in q["offices"]:
        return False, f"question does not apply to {cand['office']}"
    if row["position"] not in (-1, 0, 1):
        return False, "bad position"
    if len(row.get("quote", "")) > 300:
        return False, "quote over 300 chars"
    if not row["id"].startswith("pb2-"):
        return False, "id prefix"
    for e in SHIPPED:
        if e["subject"]["id"] == row["subject"] and e["questionId"] == row["questionId"] and e.get("quote") == row.get("quote"):
            return False, "duplicate of shipped evidence"
    return True, ""


def run(row, live=False):
    ok, why = common(row)
    if not ok:
        return ok, why
    return check_yt(row, live)


def controls():
    by_id = {r["id"]: r for r in ROWS}
    base = by_id["pb2-senador-400-seg-stf-mandato-sofesta-2026-09-15"]
    out = []
    c = deepcopy(base); c["quote"] = "eu defendo que ministro do supremo seja vitalício e eterno"
    out.append(("NEG fabricated João quote", c))
    c = deepcopy(base); c["subject"] = "senador-100"; c["check"]["names"] = ["nabor"]
    out.append(("NEG João's STF quote attributed to Nabor", c))
    c = deepcopy(base); c["date"] = "2024-09-15"
    out.append(("NEG tampered date", c))
    c = deepcopy(base); c["source"] = {**c["source"], "url": c["source"]["url"].replace("t=3561s", "t=600s")}
    out.append(("NEG wrong timestamp", c))
    c = deepcopy(base); c["questionId"] = "pb-concessoes-ppp"
    out.append(("NEG senate candidate on a governor-only question", c))
    c = deepcopy(by_id["pb2-senador-222-eco-reforma-tributaria-clickpb-2026-08-21"]); c["check"]["anchor"] = "qual a sua opinião sobre o aborto"
    out.append(("NEG interviewer question that was never asked", c))
    c = deepcopy(by_id["pb2-senador-155-seg-stf-mandato-sofesta-2026-09-18"]); c["position"] = 2
    out.append(("NEG invalid position value", c))
    c = deepcopy(by_id["pb2-senador-222-seg-8-janeiro-arapuan-2026-09-01"]); c["check"]["selfAnchor"] = "major, tu já viste falar de um tal de andré cesarino"
    out.append(("NEG debate quote anchored to another speaker's earlier turn", c))
    c = deepcopy(by_id["pb2-senador-222-seg-8-janeiro-arapuan-2026-09-01"]); c["subject"] = "senador-300"; c["check"]["names"] = ["fábio"]
    out.append(("NEG Queiroga debate quote attributed to Major Fábio", c))
    return out


def main():
    live = "--live" in sys.argv
    report, shipped = [], []
    for row in ROWS:
        ok, why = run(row, live)
        report.append({"id": row["id"], "status": "PASS" if ok else "FAIL", "claim": row.get("quote") or row["detail"], "note": why})
        if ok:
            e = {k: v for k, v in row.items() if k not in ("check", "subject")}
            e["subject"] = {"type": "candidate", "id": row["subject"]}
            e["source"] = {**row["source"], "accessed": ACCESSED}
            e["checkId"] = row["id"]
            e["lowDiscrimination"] = False
            shipped.append(e)
    ctl = []
    for name, row in controls():
        ok, why = run(row, False)
        ctl.append({"id": name, "status": "CONTROL-PASSED" if ok else "FAIL", "note": why})
    harness_ok = all(c["status"] == "FAIL" for c in ctl)
    (ROOT / "pipeline" / "checks" / "pb2.report.json").write_text(
        json.dumps({"rows": report, "controls": ctl, "harness_ok": harness_ok, "live": live}, ensure_ascii=False, indent=1))
    for r in report:
        print(r["status"], r["id"], r["note"])
    for c in ctl:
        print("CONTROL", c["status"], c["id"], "|", c["note"])
    print(f"PASS={sum(r['status'] == 'PASS' for r in report)}/{len(report)} harness_ok={harness_ok} live={live}")
    if not harness_ok:
        sys.exit(1)
    (PB2 / "evidence.json").write_text(json.dumps(shipped, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
