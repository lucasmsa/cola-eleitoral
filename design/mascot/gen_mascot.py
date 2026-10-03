"""Writes the RML for the Cola Eleitoral mascot (the calango) into mascot/.

Same pipeline as lucas-app/design/rive/gen_moments.py: Python writes RML, the Rive CLI compiles it.
Run: python3 gen_mascot.py && rive mascot --verify && rive mascot --once
The artboard (256x256) has a view model { mood: 0 idle, 1 happy, 2 think, 3 reading, 4 cheer; nod (trigger); reduceMotion }.
"""
import math
from pathlib import Path

OUT = Path(__file__).parent / "mascot"

INK = "1F2A44"
WHITE = "FFFFFF"
PEN = "C2410C"
LINE = 8      # silhouette outline
INNER = 5     # inner feature outline
FIT = 0.82    # character to artboard, leaves room for the hop
RIM, RIM_W = "FBFAF5", 24
HEAD_Y = -104

X, Y, ROT, SX, SY, OPACITY = 13, 14, 15, 16, 17, 18


def argb(rgb, alpha=1.0):
    return f"{round(alpha * 255):02X}{rgb}"


class Ids:
    def __init__(self, client):
        self.client, self.n = client, 0

    def __call__(self):
        self.n += 1
        return f"{self.client}:{self.n}"


def f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def cubic(x1, y1, x2, y2):
    return f'<CubicEaseInterpolator x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


EASE_OUT = cubic(0.16, 1, 0.3, 1)
EASE_IN_OUT = cubic(0.42, 0, 0.58, 1)
EASE_IN = cubic(0.5, 0, 0.9, 0.4)


def kf(value, frame, ease=None):
    if ease is None:
        return f'<KeyFrameDouble value="{f(value)}" frame="{frame}" interpolationType="linear"/>'
    if ease == "hold":
        return f'<KeyFrameDouble value="{f(value)}" frame="{frame}" interpolationType="hold"/>'
    return f'<KeyFrameDouble value="{f(value)}" frame="{frame}" interpolationType="cubic">{ease}</KeyFrameDouble>'


def keyed(obj, key, frames):
    return f'<KeyedObject objectId="{obj}"><KeyedProperty propertyKey="{key}">{"".join(frames)}</KeyedProperty></KeyedObject>'


def smooth_path(points, closed):
    n = len(points)
    out = []
    for k, (x, y) in enumerate(points):
        if closed:
            px, py = points[k - 1]
            nx, ny = points[(k + 1) % n]
        else:
            px, py = points[max(k - 1, 0)]
            nx, ny = points[min(k + 1, n - 1)]
        ang = math.atan2(ny - py, nx - px)
        dist = math.hypot(nx - px, ny - py) / 6
        out.append(f'<CubicMirroredVertex x="{f(x)}" y="{f(y)}" rotation="{f(ang)}" distance="{f(dist)}"/>')
    return f'<PointsPath isClosed="{"true" if closed else "false"}" name="Path">{"".join(out)}</PointsPath>'


def paints(fill, stroke, sw, cap="round", alpha=1.0):
    xml = ""
    if fill:
        xml += f'<Fill name="Fill"><SolidColor colorValue="{argb(fill, alpha)}" name="C"/></Fill>'
    if stroke:
        xml += (f'<Stroke thickness="{f(sw)}" cap="{cap}" join="round" name="Stroke">'
                f'<SolidColor colorValue="{argb(stroke)}" name="C"/></Stroke>')
    return xml


def shape(i, name, geom, fill=None, stroke=INK, sw=LINE, x=0, y=0, rot=0, opacity=1, alpha=1.0, sid=None):
    sid = sid or i()
    return (f'<Shape x="{f(x)}" y="{f(y)}" rotation="{f(rot)}" opacity="{f(opacity)}" name="{name}" id="{sid}">'
            f'{geom}{paints(fill, stroke, sw, alpha=alpha)}</Shape>')


def ellipse(w, h):
    return f'<Ellipse width="{f(w)}" height="{f(h)}" originX="0.5" originY="0.5" name="Path"/>'


def rect(w, h, r):
    return f'<Rectangle width="{f(w)}" height="{f(h)}" cornerRadiusTL="{f(r)}" originX="0.5" originY="0.5" name="Path"/>'


def node(i, name, x, y, children, nid=None, rot=0, opacity=1, scale=1):
    nid = nid or i()
    return (f'<Node x="{f(x)}" y="{f(y)}" rotation="{f(rot)}" scaleX="{f(scale)}" scaleY="{f(scale)}" opacity="{f(opacity)}" name="{name}" id="{nid}">'
            f'{"".join(children)}</Node>')


class Rig:
    """Ids every animation keys. Characters fill these in."""

    def __init__(self, i):
        self.i = i
        self.root, self.body, self.head, self.head_rim = i(), i(), i(), i()
        self.open_eyes, self.happy_eyes = i(), i()
        self.eyes, self.pupils = [i(), i()], [i(), i()]
        self.arms = [i(), i()]
        self.tail = i()
        self.arm_rest = (0.25, -0.25)
        self.head_tilt = -0.2


def eye(i, rig, k, x, y, w, h, outline, pupil=(20, 24), look=(3, 4)):
    pw, ph = pupil
    return node(i, f"Eye {k}", x, y, [
        node(i, f"Pupil {k}", look[0], look[1], [
            shape(i, "Shine", ellipse(pw * 0.38, pw * 0.38), WHITE, None, x=-pw * 0.2, y=-ph * 0.24),
            shape(i, "Shine small", ellipse(pw * 0.17, pw * 0.17), WHITE, None, x=pw * 0.22, y=ph * 0.2, alpha=0.9),
            shape(i, "Pupil", ellipse(pw, ph), INK, None),
        ], nid=rig.pupils[k]),
        shape(i, "White", ellipse(w, h), WHITE, INK if outline else None, sw=INNER),
    ], nid=rig.eyes[k])


def happy_arc(i, x, y, w):
    pts = [(x - w / 2, y + 5), (x, y - 8), (x + w / 2, y + 5)]
    return shape(i, "Happy eye", smooth_path(pts, False), None, INK, sw=7)


# ---------------------------------------------------------------- Calango
def tapered(center, w0, w1):
    """Closed outline around an open centerline, half-width going from w0 to w1."""
    n = len(center)
    left, right = [], []
    for k, (x, y) in enumerate(center):
        px, py = center[max(k - 1, 0)]
        nx, ny = center[min(k + 1, n - 1)]
        a = math.atan2(ny - py, nx - px) + math.pi / 2
        w = w0 + (w1 - w0) * k / (n - 1)
        left.append((x + math.cos(a) * w, y + math.sin(a) * w))
        right.append((x - math.cos(a) * w, y - math.sin(a) * w))
    return left + right[::-1]


def rim(i, geom, x=0, y=0, rot=0):
    """Paper-coloured halo behind the silhouette: invisible on the paper ground, an outline on dark."""
    return shape(i, "Rim", geom, RIM, RIM, sw=RIM_W, x=x, y=y, rot=rot)


MAIN, SHADE, BELLY = "4FA383", "35806A", "F3E1B5"
SOFT, LIGHT = "448F75", "8FD3B4"
EYE_X, EYE_Y = 56, -70
HEAD_PTS = [(-76, -56), (-68, -86), (-38, -103), (0, -107), (38, -103), (68, -86), (76, -56), (58, -26), (30, -10), (0, -6), (-30, -10), (-58, -26)]
CREST = [(-26, -104, 15, 22), (0, -111, 17, 28), (26, -104, 15, 22)]
MOUTH = [(-50, -36), (-24, -24), (0, -22), (24, -24), (50, -36)]
RIM_LIGHT = [(-62, -78), (-40, -95), (-14, -101), (10, -101)]


def calango(i):
    rig = Rig(i)
    ex, ey = EYE_X, EYE_Y
    head_pts, crest = HEAD_PTS, CREST
    head = node(i, "Head", 0, HEAD_Y, [
        node(i, "Happy eyes", 0, 0, [happy_arc(i, -ex, ey, 28), happy_arc(i, ex, ey, 28)], nid=rig.happy_eyes, opacity=0),
        node(i, "Open eyes", 0, 0, [eye(i, rig, 0, -ex, ey, 40, 42, False), eye(i, rig, 1, ex, ey, 40, 42, False)], nid=rig.open_eyes),
        shape(i, "Mouth", smooth_path(MOUTH, False), None, INK, sw=6),
        shape(i, "Nostril", ellipse(6, 5), INK, None, x=-11, y=-50),
        shape(i, "Nostril", ellipse(6, 5), INK, None, x=11, y=-50),
        shape(i, "Cheek", ellipse(20, 11), PEN, None, x=-46, y=-30, alpha=0.26),
        shape(i, "Cheek", ellipse(20, 11), PEN, None, x=46, y=-30, alpha=0.26),
        shape(i, "Spot", ellipse(10, 10), SHADE, None, x=0, y=-84),
        shape(i, "Spot", ellipse(8, 8), SHADE, None, x=-18, y=-90),
        shape(i, "Spot", ellipse(8, 8), SHADE, None, x=18, y=-90),
        shape(i, "Rim light", smooth_path(RIM_LIGHT, False), None, LIGHT, sw=5),
        shape(i, "Head", smooth_path(head_pts, True), MAIN),
        shape(i, "Eye bulge", ellipse(58, 58), MAIN, x=-ex, y=ey),
        shape(i, "Eye bulge", ellipse(58, 58), MAIN, x=ex, y=ey),
        *(shape(i, "Crest", ellipse(w, h), SHADE, sw=INNER, x=x, y=y) for x, y, w, h in crest),
    ], nid=rig.head)
    head_rim = node(i, "Head rim", 0, HEAD_Y, [
        rim(i, smooth_path(head_pts, True)), rim(i, ellipse(58, 58), -ex, ey), rim(i, ellipse(58, 58), ex, ey),
        *(rim(i, ellipse(w, h), x, y) for x, y, w, h in crest),
    ], nid=rig.head_rim)
    arm = lambda k, x, rest: node(i, f"Arm {k}", x, -74, [
        shape(i, "Hand", ellipse(26, 46), MAIN, x=0, y=20)], nid=rig.arms[k], rot=rest)
    body_pts = [(0, -118), (40, -106), (58, -68), (56, -28), (32, -5), (0, 0), (-32, -5), (-56, -28), (-58, -68), (-40, -106)]
    belly_pts = [(0, -96), (28, -84), (38, -50), (30, -18), (0, -9), (-30, -18), (-38, -50), (-28, -84)]
    tail_line = [(30, -20), (66, -12), (96, -24), (108, -54), (101, -79), (88, -89), (77, -85), (75, -76), (82, -71)]
    toe_xy = [(sx * dx, 3) for sx in (-1, 1) for dx in (16, 33, 50)]
    tx, ty = 30, -20  # tail pivot at its base
    tail_geom = smooth_path([(x - tx, y - ty) for x, y in tapered(tail_line, 13, 3.5)], True)
    tail = node(i, "Tail", tx, ty, [
        shape(i, "Tail band", ellipse(16, 12), SHADE, None, x=103 - tx, y=-40 - ty, rot=1.2),
        shape(i, "Tail band", ellipse(14, 10), SHADE, None, x=86 - tx, y=-16 - ty, rot=0.4),
        shape(i, "Tail", tail_geom, MAIN),
        rim(i, tail_geom),
    ], nid=rig.tail)
    body = node(i, "Body", 0, 0, [
        head,
        arm(0, -48, rig.arm_rest[0]), arm(1, 48, rig.arm_rest[1]),
        shape(i, "Scale", smooth_path([(-20, -60), (0, -55), (20, -60)], False), None, SHADE, sw=4),
        shape(i, "Scale", smooth_path([(-22, -40), (0, -35), (22, -40)], False), None, SHADE, sw=4),
        shape(i, "Belly", smooth_path(belly_pts, True), BELLY, None),
        shape(i, "Side shade", ellipse(20, 66), SOFT, None, x=-41, y=-50, rot=0.12),
        shape(i, "Side shade", ellipse(20, 66), SOFT, None, x=41, y=-50, rot=-0.12),
        shape(i, "Body", smooth_path(body_pts, True), MAIN),
        *(shape(i, "Toe", ellipse(10, 10), MAIN, INK, sw=INNER, x=x, y=y) for x, y in toe_xy),
        shape(i, "Foot", ellipse(52, 22), MAIN, x=-34, y=-8),
        shape(i, "Foot", ellipse(52, 22), MAIN, x=34, y=-8),
        tail,
        head_rim,
        rim(i, smooth_path(body_pts, True)), rim(i, ellipse(52, 22), -34, -8), rim(i, ellipse(52, 22), 34, -8),
        *(rim(i, ellipse(10, 10), x, y) for x, y in toe_xy),
    ], nid=rig.body)
    rig.xml = node(i, "Calango", 128, 238, [node(i, "Fit", 0, 0, [body], scale=FIT)], nid=rig.root)
    return rig


# ---------------------------------------------------------------- animation + state machine
def pose_keys(rig, *, arms, tilt, look, happy, frames):
    """Holds that every mood animation sets, so a switch never inherits a stale value."""
    return "".join([
        keyed(rig.arms[0], ROT, [kf(arms[0], frames, "hold")]),
        keyed(rig.arms[1], ROT, [kf(arms[1], frames, "hold")]),
        keyed(rig.open_eyes, OPACITY, [kf(0 if happy else 1, 0, "hold")]),
        keyed(rig.happy_eyes, OPACITY, [kf(1 if happy else 0, 0, "hold")]),
        *(keyed(p, X, [kf(look[0], frames, "hold")]) for p in rig.pupils),
        *(keyed(p, Y, [kf(look[1], frames, "hold")]) for p in rig.pupils),
    ])


def tail_rot(rig, frames=None):
    return keyed(rig.tail, ROT, frames or [kf(0, 0, "hold")])


def arms_sy(rig, frames=None):
    frames = frames or [kf(1, 0, "hold")]
    return "".join(keyed(a, SY, frames) for a in rig.arms)


def head_keys(rig, key, frames):
    return keyed(rig.head, key, frames) + keyed(rig.head_rim, key, frames)


def animations(i, rig, base_look):
    ids = {k: i() for k in ("idle", "happy", "think", "still", "blink", "open", "reading", "cheer", "nod", "rest")}
    lx, ly = base_look
    still = f"""<LinearAnimation duration="1" name="Still" id="{ids['still']}">
        {keyed(rig.root, Y, [kf(rig_y(rig), 0, "hold")])}
        {keyed(rig.root, SX, [kf(1, 0, "hold")])}{keyed(rig.root, SY, [kf(1, 0, "hold")])}
        {head_keys(rig, ROT, [kf(0, 0, "hold")])}{head_keys(rig, Y, [kf(HEAD_Y, 0, "hold")])}
        {pose_keys(rig, arms=rig.arm_rest, tilt=0, look=(lx, ly), happy=False, frames=0)}
        {arms_sy(rig)}
        {tail_rot(rig)}
    </LinearAnimation>"""
    idle = f"""<LinearAnimation loopValue="loop" duration="150" name="Idle" id="{ids['idle']}">
        {keyed(rig.root, Y, [kf(rig_y(rig), 0, "hold")])}
        {keyed(rig.root, SY, [kf(1, 0, EASE_IN_OUT), kf(1.035, 75, EASE_IN_OUT), kf(1, 150)])}
        {keyed(rig.root, SX, [kf(1, 0, EASE_IN_OUT), kf(0.985, 75, EASE_IN_OUT), kf(1, 150)])}
        {head_keys(rig, ROT, [kf(0, 0, EASE_IN_OUT), kf(0.025, 75, EASE_IN_OUT), kf(0, 150)])}{head_keys(rig, Y, [kf(HEAD_Y, 0, "hold")])}
        {keyed(rig.arms[0], ROT, [kf(rig.arm_rest[0], 0, EASE_IN_OUT), kf(rig.arm_rest[0] + 0.08, 75, EASE_IN_OUT), kf(rig.arm_rest[0], 150)])}
        {keyed(rig.arms[1], ROT, [kf(rig.arm_rest[1], 0, EASE_IN_OUT), kf(rig.arm_rest[1] - 0.08, 75, EASE_IN_OUT), kf(rig.arm_rest[1], 150)])}
        {keyed(rig.open_eyes, OPACITY, [kf(1, 0, "hold")])}{keyed(rig.happy_eyes, OPACITY, [kf(0, 0, "hold")])}
        {"".join(keyed(p, X, [kf(lx, 0, "hold")]) + keyed(p, Y, [kf(ly, 0, "hold")]) for p in rig.pupils)}
        {arms_sy(rig)}
        {tail_rot(rig, [kf(-0.035, 0, EASE_IN_OUT), kf(0.055, 75, EASE_IN_OUT), kf(-0.035, 150)])}
    </LinearAnimation>"""
    y0 = rig_y(rig)
    # one dry beat, 36 frames (0.6 s): a small hop that lands in a nod, eyes closed in a satisfied smile
    happy = f"""<LinearAnimation duration="36" name="Happy" id="{ids['happy']}">
        {keyed(rig.root, Y, [kf(y0, 0, "hold"), kf(y0, 2, EASE_OUT), kf(y0 - 6, 10, EASE_IN), kf(y0, 18), kf(y0, 36)])}
        {keyed(rig.root, SY, [kf(1, 0, EASE_OUT), kf(0.97, 4, EASE_OUT), kf(1.02, 10, EASE_IN_OUT), kf(0.985, 18, EASE_OUT), kf(1, 28), kf(1, 36)])}
        {keyed(rig.root, SX, [kf(1, 0, EASE_OUT), kf(1.02, 4, EASE_OUT), kf(0.99, 10, EASE_IN_OUT), kf(1.01, 18, EASE_OUT), kf(1, 28), kf(1, 36)])}
        {head_keys(rig, ROT, [kf(0, 0, "hold")])}
        {head_keys(rig, Y, [kf(HEAD_Y, 0, "hold"), kf(HEAD_Y, 14, EASE_IN_OUT), kf(HEAD_Y + 5, 22, EASE_IN_OUT), kf(HEAD_Y, 32), kf(HEAD_Y, 36)])}
        {keyed(rig.arms[0], ROT, [kf(rig.arm_rest[0], 0, "hold")])}
        {keyed(rig.arms[1], ROT, [kf(rig.arm_rest[1], 0, "hold")])}
        {keyed(rig.open_eyes, OPACITY, [kf(0, 0, "hold")])}{keyed(rig.happy_eyes, OPACITY, [kf(1, 0, "hold")])}
        {"".join(keyed(p, X, [kf(lx, 0, "hold")]) + keyed(p, Y, [kf(ly, 0, "hold")]) for p in rig.pupils)}
        {arms_sy(rig)}
        {tail_rot(rig)}
    </LinearAnimation>"""
    t = rig.head_tilt
    think = f"""<LinearAnimation loopValue="loop" duration="180" name="Think" id="{ids['think']}">
        {keyed(rig.root, Y, [kf(y0, 0, "hold")])}
        {keyed(rig.root, SX, [kf(1, 0, "hold")])}{keyed(rig.root, SY, [kf(1, 0, "hold")])}
        {head_keys(rig, ROT, [kf(t, 0, EASE_IN_OUT), kf(t * 0.75, 90, EASE_IN_OUT), kf(t, 180)])}{head_keys(rig, Y, [kf(HEAD_Y, 0, "hold")])}
        {keyed(rig.arms[0], ROT, [kf(rig.arm_rest[0], 0, "hold")])}
        {keyed(rig.arms[1], ROT, [kf(rig.arm_rest[1], 0, "hold")])}
        {keyed(rig.open_eyes, OPACITY, [kf(1, 0, "hold")])}{keyed(rig.happy_eyes, OPACITY, [kf(0, 0, "hold")])}
        {"".join(keyed(p, X, [kf(lx - 6, 0, "hold")]) + keyed(p, Y, [kf(ly - 7, 0, "hold")]) for p in rig.pupils)}
        {arms_sy(rig)}
        {tail_rot(rig)}
    </LinearAnimation>"""
    blink = f"""<LinearAnimation loopValue="loop" duration="230" name="Blink" id="{ids['blink']}">
        {"".join(keyed(e, SY, [kf(1, 0, "hold"), kf(1, 196, EASE_IN), kf(0.08, 201, EASE_OUT), kf(1, 208), kf(1, 230)]) for e in rig.eyes)}
    </LinearAnimation>"""
    opened = f"""<LinearAnimation duration="1" name="Eyes open" id="{ids['open']}">
        {"".join(keyed(e, SY, [kf(1, 0, "hold")]) for e in rig.eyes)}
    </LinearAnimation>"""
    # reading: eyes scan a line left to right, a pause, a quick return sweep; head lowered a touch
    scan = [kf(lx - 8, 0, EASE_IN_OUT), kf(lx + 8, 54, "hold"), kf(lx + 8, 62, EASE_IN_OUT), kf(lx - 8, 74, "hold"), kf(lx - 8, 80, EASE_IN_OUT),
            kf(lx + 8, 134, "hold"), kf(lx + 8, 142, EASE_IN_OUT), kf(lx - 8, 154, "hold"), kf(lx - 8, 160)]
    reading = f"""<LinearAnimation loopValue="loop" duration="160" name="Reading" id="{ids['reading']}">
        {keyed(rig.root, Y, [kf(y0, 0, "hold")])}
        {keyed(rig.root, SX, [kf(1, 0, "hold")])}
        {keyed(rig.root, SY, [kf(1, 0, EASE_IN_OUT), kf(1.02, 80, EASE_IN_OUT), kf(1, 160)])}
        {head_keys(rig, ROT, [kf(0.04, 0, "hold")])}{head_keys(rig, Y, [kf(HEAD_Y + 3, 0, "hold")])}
        {keyed(rig.arms[0], ROT, [kf(rig.arm_rest[0], 0, "hold")])}
        {keyed(rig.arms[1], ROT, [kf(rig.arm_rest[1], 0, "hold")])}
        {keyed(rig.open_eyes, OPACITY, [kf(1, 0, "hold")])}{keyed(rig.happy_eyes, OPACITY, [kf(0, 0, "hold")])}
        {"".join(keyed(p, X, scan) + keyed(p, Y, [kf(ly + 4, 0, "hold")]) for p in rig.pupils)}
        {arms_sy(rig)}
        {tail_rot(rig)}
    </LinearAnimation>"""
    # cheer: one beat, 60 frames (1 s): crouch, a single higher hop with both arms up, land, arms come down
    a0, a1 = rig.arm_rest
    up0, up1 = 2.25, -2.25
    reach = [kf(1, 0, "hold"), kf(1, 6, EASE_OUT), kf(1.55, 18, "hold"), kf(1.55, 34, EASE_IN_OUT), kf(1, 52), kf(1, 60)]
    cheer = f"""<LinearAnimation duration="60" name="Cheer" id="{ids['cheer']}">
        {keyed(rig.root, Y, [kf(y0, 0, "hold"), kf(y0, 6, EASE_OUT), kf(y0 - 16, 18, EASE_IN), kf(y0, 28), kf(y0, 60)])}
        {keyed(rig.root, SY, [kf(1, 0, EASE_OUT), kf(0.94, 6, EASE_OUT), kf(1.05, 16, EASE_IN_OUT), kf(0.96, 28, EASE_OUT), kf(1.01, 38, EASE_IN_OUT), kf(1, 48), kf(1, 60)])}
        {keyed(rig.root, SX, [kf(1, 0, EASE_OUT), kf(1.04, 6, EASE_OUT), kf(0.97, 16, EASE_IN_OUT), kf(1.03, 28, EASE_OUT), kf(1, 40), kf(1, 60)])}
        {head_keys(rig, ROT, [kf(0, 0, "hold")])}
        {head_keys(rig, Y, [kf(HEAD_Y, 0, "hold"), kf(HEAD_Y, 26, EASE_IN_OUT), kf(HEAD_Y + 4, 32, EASE_IN_OUT), kf(HEAD_Y, 40), kf(HEAD_Y, 60)])}
        {keyed(rig.arms[0], ROT, [kf(a0, 0, "hold"), kf(a0, 6, EASE_OUT), kf(up0, 18, "hold"), kf(up0, 34, EASE_IN_OUT), kf(a0, 52), kf(a0, 60)])}
        {keyed(rig.arms[1], ROT, [kf(a1, 0, "hold"), kf(a1, 6, EASE_OUT), kf(up1, 18, "hold"), kf(up1, 34, EASE_IN_OUT), kf(a1, 52), kf(a1, 60)])}
        {arms_sy(rig, reach)}
        {keyed(rig.open_eyes, OPACITY, [kf(0, 0, "hold")])}{keyed(rig.happy_eyes, OPACITY, [kf(1, 0, "hold")])}
        {"".join(keyed(p, X, [kf(lx, 0, "hold")]) + keyed(p, Y, [kf(ly, 0, "hold")]) for p in rig.pupils)}
        {tail_rot(rig)}
    </LinearAnimation>"""
    # nod: 18 frames (0.3 s), head dips 6 px and comes back; keys only head Y so it stacks on any mood
    nod = f"""<LinearAnimation duration="18" name="Nod" id="{ids['nod']}">
        {head_keys(rig, Y, [kf(HEAD_Y, 0, EASE_OUT), kf(HEAD_Y + 6, 6, EASE_IN_OUT), kf(HEAD_Y, 18)])}
    </LinearAnimation>"""
    rest = f"""<LinearAnimation duration="1" name="Nod rest" id="{ids['rest']}"/>"""
    return ids, still + idle + happy + think + blink + opened + reading + cheer + nod + rest


def rig_y(rig):
    return rig.root_y


def cond_number(path, value):
    return (f'<TransitionViewModelCondition opValue="equal"><TransitionPropertyViewModelComparator><BindablePropertyNumber>'
            f'<DataBindContext sourcePathIds="{path}" propertyKey="636"/></BindablePropertyNumber>'
            f'</TransitionPropertyViewModelComparator><TransitionValueNumberComparator value="{value}"/></TransitionViewModelCondition>')


def cond_bool(path, value):
    return (f'<TransitionViewModelCondition opValue="equal"><TransitionPropertyViewModelComparator><BindablePropertyBoolean>'
            f'<DataBindContext sourcePathIds="{path}" propertyKey="634"/></BindablePropertyBoolean>'
            f'</TransitionPropertyViewModelComparator><TransitionValueBooleanComparator value="{value}"/></TransitionViewModelCondition>')


def cond_trigger(path):
    return (f'<TransitionViewModelCondition><TransitionPropertyViewModelComparator><BindablePropertyTrigger>'
            f'<DataBindContext sourcePathIds="{path}" propertyKey="686"/></BindablePropertyTrigger>'
            f'</TransitionPropertyViewModelComparator><TransitionValueTriggerComparator/></TransitionViewModelCondition>')


def state_machine(i, p, anim):
    """Happy and cheer play once and settle into idle while mood stays put; set mood to 0 and back to replay."""
    sm, mood_layer, blink_layer, nod_layer = i(), i(), i(), i()
    s = {k: i() for k in ("idle", "happy", "think", "still", "settled", "reading", "cheer", "cheered")}
    moods = {"idle": 0, "happy": 1, "think": 2, "reading": 3, "cheer": 4}
    mix = 'duration="180"'

    def to_mood(name):
        # one-shot beats cut in fast so the open eyes and the happy arcs never sit half-crossfaded
        dur = 'duration="80"' if name in ("happy", "cheer") else mix
        return f'<StateTransition stateToId="{s[name]}" {dur}>{cond_bool(p["reduceMotion"], "false")}{cond_number(p["mood"], moods[name])}</StateTransition>'

    to_still = f'<StateTransition stateToId="{s["still"]}" {mix}>{cond_bool(p["reduceMotion"], "true")}</StateTransition>'
    def settle_to(name):
        return f'<StateTransition stateToId="{s[name]}" duration="100" enableExitTime="true" exitTimeIsPercetange="true" exitTime="100"/>'

    def away(*skip):
        return [to_mood(m) for m in moods if m not in skip] + [to_still]

    outs = {
        "idle": away("idle"),
        "happy": away("happy") + [settle_to("settled")],
        "settled": away("happy"),
        "think": away("think"),
        "reading": away("reading"),
        "cheer": away("cheer") + [settle_to("cheered")],
        "cheered": away("cheer"),
        "still": [to_mood(m) for m in moods],
    }
    clip = {"idle": "idle", "happy": "happy", "settled": "idle", "think": "think", "still": "still",
            "reading": "reading", "cheer": "cheer", "cheered": "idle"}
    states = [f'<AnimationState x="{240 + 160 * (n % 4)}" y="{160 * (n // 4)}" animationId="{anim[clip[name]]}" id="{s[name]}">{"".join(outs[name])}</AnimationState>'
              for n, name in enumerate(s)]
    entry = to_still + "".join(to_mood(m) for m in moods)

    b_blink, b_open = i(), i()
    blink = f"""<StateMachineLayer name="Blink" id="{blink_layer}">
            <AnyState x="0" y="-120"/>
            <ExitState x="480" y="0"/>
            <EntryState x="0" y="0">
                <StateTransition stateToId="{b_blink}">{cond_bool(p["reduceMotion"], "false")}</StateTransition>
                <StateTransition stateToId="{b_open}">{cond_bool(p["reduceMotion"], "true")}</StateTransition>
            </EntryState>
            <AnimationState x="240" y="-80" animationId="{anim['blink']}" id="{b_blink}"><StateTransition stateToId="{b_open}">{cond_bool(p["reduceMotion"], "true")}</StateTransition></AnimationState>
            <AnimationState x="240" y="80" animationId="{anim['open']}" id="{b_open}"><StateTransition stateToId="{b_blink}">{cond_bool(p["reduceMotion"], "false")}</StateTransition></AnimationState>
        </StateMachineLayer>"""
    n_rest, n_nod = i(), i()
    nod = f"""<StateMachineLayer name="Nod" id="{nod_layer}">
            <AnyState x="0" y="-120"/>
            <ExitState x="560" y="0"/>
            <EntryState x="0" y="0"><StateTransition stateToId="{n_rest}"/></EntryState>
            <AnimationState x="240" y="0" animationId="{anim['rest']}" id="{n_rest}"><StateTransition stateToId="{n_nod}">{cond_trigger(p["nod"])}{cond_bool(p["reduceMotion"], "false")}</StateTransition></AnimationState>
            <AnimationState x="400" y="0" animationId="{anim['nod']}" reset="true" id="{n_nod}"><StateTransition stateToId="{n_rest}" enableExitTime="true" exitTimeIsPercetange="true" exitTime="100"/><StateTransition stateToId="{n_nod}">{cond_trigger(p["nod"])}{cond_bool(p["reduceMotion"], "false")}</StateTransition></AnimationState>
        </StateMachineLayer>"""
    return sm, f"""<StateMachine name="Mascot" id="{sm}">
        <StateMachineLayer name="Mood" id="{mood_layer}">
            <AnyState x="0" y="-160"/>
            <ExitState x="900" y="-160"/>
            <EntryState x="0" y="0">{entry}</EntryState>
            {"".join(states)}
        </StateMachineLayer>
        {blink}
        {nod}
    </StateMachine>"""


def view_model(i, name):
    vm, inst, mood, reduce, nod = i(), i(), i(), i(), i()
    xml = (f'<ViewModel defaultInstanceId="{inst}" name="{name}" id="{vm}">'
           f'<ViewModelPropertyNumber name="mood" id="{mood}"/><ViewModelPropertyBoolean name="reduceMotion" id="{reduce}"/>'
           f'<ViewModelPropertyTrigger name="nod" id="{nod}"/>'
           f'<ViewModelInstance exports="true" name="Default" id="{inst}">'
           f'<ViewModelInstanceNumber propertyValue="0" viewModelPropertyId="{mood}"/>'
           f'<ViewModelInstanceBoolean propertyValue="false" viewModelPropertyId="{reduce}"/>'
           f'<ViewModelInstanceTrigger viewModelPropertyId="{nod}"/>'
           f'</ViewModelInstance></ViewModel>')
    return xml, vm, inst, {"mood": f"{vm}-{mood}", "reduceMotion": f"{vm}-{reduce}", "nod": f"{vm}-{nod}"}


def artboard(client, name, build, x, root_y, look):
    i = Ids(client)
    vm_xml, vm, inst, p = view_model(i, f"{name}Mascot")
    rig = build(i)
    rig.root_y = root_y
    anim_ids, anim_xml = animations(i, rig, look)
    sm, sm_xml = state_machine(i, p, anim_ids)
    art, sty = i(), i()
    return f"""<Rive version="1" kind="fragment">
    <Artboard defaultStateMachineId="{sm}" viewModelId="{vm}" viewModelInstanceId="{inst}" x="{x}" y="0" width="256" height="256" styleId="{sty}" name="{name}" id="{art}">
        <LayoutComponentStyle name="Artboard Style" id="{sty}"/>
        {sm_xml}
        {anim_xml}
        {rig.xml}
    </Artboard>
    {vm_xml}
</Rive>
"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.rml"):
        old.unlink()
    (OUT / "calango.rml").write_text(artboard(1, "Calango", calango, 0, 238, (3, 4)))
    print("wrote", *sorted(q.name for q in OUT.glob("*.rml")))
