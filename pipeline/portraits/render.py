"""Renders every profiled candidate's official TSE photo as a pen-and-ink portrait (same filter for everyone).

Run: pipeline/.venv/bin/python pipeline/portraits/render.py
Writes public/portraits/<candidateId>.svg and src/data/portraits.json.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "pipeline" / "portraits" / "raw"
OUT = ROOT / "public" / "portraits"
DATA = ROOT / "src" / "data"
ACCESSED = "2026-10-03"
ZIP_URL = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/fotos/foto_cand2026_{uf}_div.zip"
INK = "#1f2a44"
PAPER = "#fbfaf5"
TAPE = "#d7deec"
W, H = 160, 200
SCALE = 3
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def photo_path(sq):
    for uf in ("PB", "BR"):
        p = RAW / uf / f"F{uf}{sq}_div.jpg"
        if p.exists():
            return uf, p
    return None, None


HEAD_ZOOM = 3.0
FACE_Y = 0.38


def crop_to_frame(gray):
    h, w = gray.shape
    faces = CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(w // 6, w // 6))
    if len(faces):
        x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        target_h = min(h, int(round(fh * HEAD_ZOOM)))
        cx, cy = x + fw / 2, y + fh / 2
    else:
        target_h, cx, cy = h, w / 2, h * 0.38
    target_w = int(round(target_h * W / H))
    if target_w > w:
        target_w = w
        target_h = int(round(w * H / W))
    x0 = int(np.clip(cx - target_w / 2, 0, w - target_w))
    y0 = int(np.clip(cy - target_h * FACE_Y, 0, h - target_h))
    face = None
    if len(faces):
        face = ((x - x0) / target_w, (y - y0) / target_h, fw / target_w, fh / target_h)
    return gray[y0:y0 + target_h, x0:x0 + target_w], face


def xdog(img, sigma=1.3, k=1.6, p=22.0, eps=0.15, phi=12.0):
    f = img.astype(np.float32) / 255.0
    g1 = cv2.GaussianBlur(f, (0, 0), sigma)
    g2 = cv2.GaussianBlur(f, (0, 0), sigma * k)
    s = (1 + p) * g1 - p * g2
    out = np.where(s >= eps, 1.0, 1.0 + np.tanh(phi * (s - eps)))
    return out < 0.5


def hatch(shape, angle_deg, spacing, width):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    a = np.deg2rad(angle_deg)
    proj = xx * np.cos(a) + yy * np.sin(a)
    return (proj % spacing) < width


FACE_MEDIAN = 135.0


def face_region(g, face):
    h, w = g.shape
    if face is None:
        return g[int(h * 0.2):int(h * 0.6), int(w * 0.3):int(w * 0.7)]
    fx, fy, fw, fh = face
    return g[int(h * (fy + fh * 0.15)):int(h * (fy + fh * 0.85)), int(w * (fx + fw * 0.2)):int(w * (fx + fw * 0.8))]


def normalize(gray, face):
    lo, hi = np.percentile(gray, (1, 99))
    g = np.clip((gray.astype(np.float32) - lo) / max(hi - lo, 1.0), 0, 1)
    med = float(np.clip(np.median(face_region(g, face)), 0.05, 0.95))
    gamma = float(np.clip(np.log(FACE_MEDIAN / 255.0) / np.log(med), 0.6, 2.6))
    return (255 * np.power(g, gamma)).astype(np.uint8)


def vignette(shape):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = ((xx / w - 0.5) / 0.5) ** 2 + ((yy / h - 0.56) / 0.62) ** 2
    return r < 0.85, r < 1.15


def ink_mask(photo_bgr):
    gray = cv2.cvtColor(photo_bgr, cv2.COLOR_BGR2GRAY)
    gray, face = crop_to_frame(gray)
    gray = cv2.resize(gray, (W * SCALE, H * SCALE), interpolation=cv2.INTER_CUBIC)
    gray = normalize(gray, face)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(gray)
    gray = cv2.bilateralFilter(gray, 9, 40, 9)
    lines = xdog(gray)
    tone = cv2.GaussianBlur(gray, (0, 0), 3).astype(np.float32)
    mid = (tone < 105) & hatch(tone.shape, 45, 6, 1.4)
    dark = (tone < 65) & hatch(tone.shape, -45, 6, 1.4)
    darkest = tone < 28
    lines = cv2.dilate(lines.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)
    inner, outer = vignette(tone.shape)
    mask = (lines & outer) | ((mid | dark | darkest) & inner)
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)).astype(bool)
    return mask


def trace(mask):
    with tempfile.TemporaryDirectory() as d:
        pbm = Path(d) / "in.pbm"
        svg = Path(d) / "out.svg"
        h, w = mask.shape
        bits = np.packbits(mask.astype(np.uint8), axis=1)
        pbm.write_bytes(f"P4\n{w} {h}\n".encode() + bits.tobytes())
        subprocess.run(["potrace", str(pbm), "-s", "-o", str(svg), "--turdsize", "3", "--alphamax", "1.0",
                        "--opttolerance", "0.4", "--color", INK, "--flat"], check=True)
        text = svg.read_text()
    inner = re.search(r"<g[\s\S]*</g>", text).group(0)
    return inner, w, h


def frame_svg(inner, iw, ih):
    pad = 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W + 2 * pad} {H + 2 * pad + 6}" width="{W + 2 * pad}" height="{H + 2 * pad + 6}" role="img">
<g transform="rotate(-1.2 {W / 2 + pad} {H / 2 + pad})">
<rect x="2" y="6" width="{W + 2 * pad - 4}" height="{H + 2 * pad - 4}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>
<svg x="{pad}" y="{pad + 4}" width="{W}" height="{H}" viewBox="0 0 {iw} {ih}" preserveAspectRatio="xMidYMid slice">
<rect width="{iw}" height="{ih}" fill="{PAPER}"/>
{inner}
</svg>
</g>
<rect x="{(W + 2 * pad) / 2 - 22}" y="0" width="44" height="13" fill="{TAPE}" fill-opacity="0.85" transform="rotate(2 {(W + 2 * pad) / 2} 6)"/>
</svg>
'''


def main():
    candidates = {c["id"]: c for c in json.loads((DATA / "candidates.json").read_text())}
    profiles = json.loads((DATA / "profiles.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, missing = [], []
    for prof in profiles:
        cid = prof["candidateId"]
        sq = re.search(r"SQ (\d+)", candidates[cid]["source"]["label"]).group(1)
        uf, path = photo_path(sq)
        if not path:
            missing.append(cid)
            continue
        inner, iw, ih = trace(ink_mask(cv2.imread(str(path))))
        (OUT / f"{cid}.svg").write_text(frame_svg(inner, iw, ih))
        manifest.append({"candidateId": cid, "file": f"/portraits/{cid}.svg",
                         "photoSource": {"url": ZIP_URL.format(uf=uf), "accessed": ACCESSED,
                                         "label": f"Foto oficial do TSE, arquivo F{uf}{sq}_div.jpg"}})
    (DATA / "portraits.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
    print(len(manifest), "portraits;", "missing:", missing)


if __name__ == "__main__":
    main()
