"""Writes public/favicon.svg: the Calango's head, from the same geometry gen_mascot.py feeds to Rive.

Rive's CubicMirroredVertex puts both control points at `distance` along `rotation`; the same rule
turns each smoothed outline into SVG cubic segments here, so the favicon and the mascot share one drawing.
"""
import math
from pathlib import Path

from gen_mascot import CREST, EYE_X, EYE_Y, HEAD_PTS, INK, MAIN, SHADE, f

OUT = Path(__file__).resolve().parents[2] / "public" / "favicon.svg"
PAPER, PEN = "FBFAF5", "C2410C"


def smooth_d(points, closed):
    n = len(points)
    verts = []
    for k, (x, y) in enumerate(points):
        if closed:
            px, py = points[k - 1]
            nx, ny = points[(k + 1) % n]
        else:
            px, py = points[max(k - 1, 0)]
            nx, ny = points[min(k + 1, n - 1)]
        a = math.atan2(ny - py, nx - px)
        d = math.hypot(nx - px, ny - py) / 6
        verts.append(((x, y), (x - math.cos(a) * d, y - math.sin(a) * d), (x + math.cos(a) * d, y + math.sin(a) * d)))
    out = [f"M{f(verts[0][0][0])} {f(verts[0][0][1])}"]
    segs = n if closed else n - 1
    for k in range(segs):
        (_, _, c1), (p2, c2, _) = verts[k], verts[(k + 1) % n]
        out.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(out) + (" Z" if closed else "")


def main():
    stroke = f'stroke="#{INK}" stroke-width="9" stroke-linejoin="round"'
    crest = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="{h / 2}" fill="#{SHADE}" {stroke}/>' for x, y, w, h in CREST)
    bulges = "".join(f'<circle cx="{sx * EYE_X}" cy="{EYE_Y}" r="29" fill="#{MAIN}" {stroke}/>' for sx in (-1, 1))
    eyes = "".join(
        f'<circle cx="{sx * EYE_X}" cy="{EYE_Y}" r="21" fill="#fff"/>'
        f'<circle cx="{sx * EYE_X + 3}" cy="{EYE_Y + 4}" r="11" fill="#{INK}"/>'
        f'<circle cx="{sx * EYE_X - 1}" cy="{EYE_Y - 1}" r="4" fill="#fff"/>'
        for sx in (-1, 1))
    mouth = f'<path d="{smooth_d([(-46, -34), (-22, -24), (0, -22), (22, -24), (46, -34)], False)}" fill="none" stroke="#{INK}" stroke-width="8" stroke-linecap="round"/>'
    head = f'<path d="{smooth_d(HEAD_PTS, True)}" fill="#{MAIN}" {stroke}/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -164 200 200">'
           f'<title>Cola Eleitoral</title>'
           f'<rect x="-100" y="-164" width="200" height="200" rx="44" fill="#{PAPER}"/>'
           f'<g transform="translate(0 -6)">{crest}{bulges}{head}{eyes}{mouth}</g></svg>\n')
    OUT.write_text(svg)
    print("wrote", OUT, len(svg), "bytes")


if __name__ == "__main__":
    main()
