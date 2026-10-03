"""Writes the RML for the app's UI moments: page turn, stamp, lesson-path node.

Same pipeline as design/mascot/gen_mascot.py. Run:
  python3 gen_ui.py && for p in pagina carimbo trilha; do rive $p --verify && rive $p --once; done
Each project compiles to <project>/build/<project>.riv, copied to public/rive/.
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "mascot"))
from gen_mascot import (EASE_IN, EASE_IN_OUT, EASE_OUT, OPACITY, ROT, SX, SY, X, Ids, argb, cond_bool, cond_trigger,  # noqa: E402
                        ellipse, f, keyed, kf, rect, smooth_path)

PAPER, INK, PEN, RULE, MUTED = "FBFAF5", "1F2A44", "C2410C", "D7DEEC", "9AA6C2"
TRIM_END = 115
WGHT = int.from_bytes(b"wght", "big")


def fill(color, alpha=1.0):
    return f'<Fill name="Fill"><SolidColor colorValue="{argb(color, alpha)}" name="C"/></Fill>'


def stroke(color, w, cap="round", trim=None):
    t = f'<TrimPath start="0" end="0" name="Trim" id="{trim}"/>' if trim else ""
    return f'<Stroke thickness="{f(w)}" cap="{cap}" join="round" name="Stroke"><SolidColor colorValue="{argb(color)}" name="C"/>{t}</Stroke>'


def shape(sid, name, geom, paint, x=0, y=0, rot=0, opacity=1, scale=1):
    return (f'<Shape x="{f(x)}" y="{f(y)}" rotation="{f(rot)}" scaleX="{f(scale)}" scaleY="{f(scale)}" opacity="{f(opacity)}" name="{name}" id="{sid}">'
            f'{geom}{paint}</Shape>')


def group(nid, name, x, y, children, opacity=1, rot=0, scale=1):
    return (f'<Node x="{f(x)}" y="{f(y)}" rotation="{f(rot)}" scaleX="{f(scale)}" scaleY="{f(scale)}" opacity="{f(opacity)}" name="{name}" id="{nid}">'
            f'{"".join(children)}</Node>')


def view_model(i, name, props):
    """props: list of (name, kind, default) with kind in number|boolean|trigger."""
    vm, inst = i(), i()
    tag = {"number": "Number", "boolean": "Boolean", "trigger": "Trigger"}
    ids = {n: i() for n, _, _ in props}
    decl = "".join(f'<ViewModelProperty{tag[k]} name="{n}" id="{ids[n]}"/>' for n, k, _ in props)
    vals = "".join(
        f'<ViewModelInstanceTrigger viewModelPropertyId="{ids[n]}"/>' if k == "trigger" else
        f'<ViewModelInstance{tag[k]} propertyValue="{d}" viewModelPropertyId="{ids[n]}"/>'
        for n, k, d in props)
    xml = (f'<ViewModel defaultInstanceId="{inst}" name="{name}" id="{vm}">{decl}'
           f'<ViewModelInstance exports="true" name="Default" id="{inst}">{vals}</ViewModelInstance></ViewModel>')
    return xml, vm, inst, {n: f"{vm}-{ids[n]}" for n in ids}


def anim(aid, name, duration, body, loop=False):
    lv = ' loopValue="loop"' if loop else ""
    return f'<LinearAnimation{lv} duration="{duration}" name="{name}" id="{aid}">{body}</LinearAnimation>'


def one_shot_machine(i, name, p, trigger, rest_id, play_id):
    """Rest (transparent) -> play on trigger -> back to rest at the end. Re-firing mid-play restarts it."""
    sm, layer, s_rest, s_play = i(), i(), i(), i()
    go = f'<StateTransition stateToId="{s_play}">{cond_trigger(p[trigger])}</StateTransition>'
    xml = f"""<StateMachine name="{name}" id="{sm}">
        <StateMachineLayer name="{name}" id="{layer}">
            <AnyState x="0" y="-120"/>
            <ExitState x="560" y="0"/>
            <EntryState x="0" y="0"><StateTransition stateToId="{s_rest}"/></EntryState>
            <AnimationState x="240" y="0" animationId="{rest_id}" id="{s_rest}">{go}</AnimationState>
            <AnimationState x="400" y="0" animationId="{play_id}" reset="true" id="{s_play}">
                <StateTransition stateToId="{s_rest}" enableExitTime="true" exitTimeIsPercetange="true" exitTime="100"/>{go}
            </AnimationState>
        </StateMachineLayer>
    </StateMachine>"""
    return sm, xml


def document(i, art_name, w, h, sm_xml, sm, vm_xml, vm, inst, anims, scene, roots=""):
    art, sty = i(), i()
    return f"""<Rive version="1" kind="fragment">
    <Artboard defaultStateMachineId="{sm}" viewModelId="{vm}" viewModelInstanceId="{inst}" x="0" y="0" width="{w}" height="{h}" styleId="{sty}" name="{art_name}" id="{art}">
        <LayoutComponentStyle name="Artboard Style" id="{sty}"/>
        {sm_xml}
        {anims}
        {scene}
    </Artboard>
    {vm_xml}
    {roots}
</Rive>
"""


# ---------------------------------------------------------------- Pagina: notebook page turn
def pagina():
    """A ruled sheet sweeps in from the right with a curled leading edge, covers the screen at the
    midpoint (frame 13, ~220 ms: swap the screen underneath then), and leaves to the left (27 frames)."""
    i = Ids(1)
    W, H = 400, 800
    vm_xml, vm, inst, p = view_model(i, "PaginaVM", [("turn", "trigger", None)])
    sheet, shadow, curl = i(), i(), i()
    rules = "".join(shape(i(), "Rule", rect(W, 1.5, 0), fill(RULE), x=W / 2, y=y) for y in range(96, H, 32))
    margin = shape(i(), "Margin", rect(2, H, 0), fill(PEN, 0.55), x=56, y=H / 2)
    page = shape(i(), "Paper", rect(W, H, 0), fill(PAPER), x=W / 2, y=H / 2)
    # leading edge: a soft shadow band and a lighter curl, both riding on the sheet's left side
    shade = shape(i(), "Edge shadow", rect(36, H, 0), fill(INK, 0.16), x=-18, y=H / 2)
    lip = shape(i(), "Curl", smooth_path([(0, 0), (-16, H * 0.25), (-22, H * 0.5), (-16, H * 0.75), (0, H)], False), stroke(MUTED, 3))
    scene = group(sheet, "Sheet", W + 40, 0, [
        group(curl, "Edge", 0, 0, [lip]),
        group(shadow, "Shadow", 0, 0, [shade]),
        margin, rules, page,
    ])
    rest_id, turn_id = i(), i()
    rest = anim(rest_id, "Rest", 1, keyed(sheet, X, [kf(W + 40, 0, "hold")]) + keyed(shadow, OPACITY, [kf(0, 0, "hold")]))
    turn = anim(turn_id, "Turn", 27,
                keyed(sheet, X, [kf(W + 40, 0, EASE_IN_OUT), kf(0, 13, "hold"), kf(0, 14, EASE_IN_OUT), kf(-W - 40, 27)])
                + keyed(shadow, OPACITY, [kf(0, 0, EASE_OUT), kf(1, 6, "hold"), kf(1, 10, EASE_IN), kf(0, 13, "hold"), kf(0, 14, EASE_OUT), kf(1, 18, "hold"), kf(1, 27)])
                + keyed(curl, SX, [kf(1, 0, EASE_OUT), kf(1.6, 7, EASE_IN), kf(0.2, 13, "hold"), kf(0.2, 14, EASE_OUT), kf(1.6, 20, EASE_IN), kf(1, 27)]))
    sm, sm_xml = one_shot_machine(i, "Turn", p, "turn", rest_id, turn_id)
    return document(i, "Pagina", W, H, sm_xml, sm, vm_xml, vm, inst, rest + turn, scene)


# ---------------------------------------------------------------- Carimbo: REGISTRADO stamp
def carimbo():
    """Pen-orange rubber stamp: drops from 1.6x, thumps to 0.94x, settles at 1x tilted -6 degrees,
    holds, fades. 30 frames (500 ms)."""
    i = Ids(1)
    W, H = 240, 120
    vm_xml, vm, inst, p = view_model(i, "CarimboVM", [("stamp", "trigger", None)])
    stamp, ink = i(), i()
    font, style = i(), i()
    text = (f'<Text x="0" y="0" sizingValue="autoWidth" originX="0.5" originY="0.5" name="Word" id="{i()}">'
            f'<TextStylePaint fontSize="27" fontAssetId="{font}" name="Stamp" id="{style}">'
            f'<TextStyleAxis tag="{WGHT}" axisValue="800" name="wght"/>{fill(PEN)}</TextStylePaint>'
            f'<TextValueRun styleId="{style}" text="REGISTRADO" name="Run"/></Text>')
    # paper-coloured specks over the ink read as an uneven rubber impression
    specks = "".join(shape(i(), "Speck", ellipse(d, d * 0.7), fill(PAPER, 0.9), x=x, y=y)
                     for x, y, d in [(-74, -8, 5), (-40, 10, 4), (-12, -12, 3), (22, 6, 5), (58, -6, 4), (80, 12, 3), (-88, 14, 3), (40, 18, 3)])
    outer = shape(i(), "Border", rect(196, 66, 9), stroke(PEN, 4, cap="butt"))
    inner = shape(i(), "Border inner", rect(184, 54, 6), stroke(PEN, 1.5, cap="butt"))
    scene = group(stamp, "Stamp", W / 2, H / 2, [specks, text, inner, outer], opacity=0, rot=-0.105)
    smudge = shape(ink, "Ink halo", rect(204, 74, 11), fill(PEN, 0.10), x=W / 2, y=H / 2, rot=-0.105, opacity=0)
    rest_id, play_id = i(), i()
    rest = anim(rest_id, "Rest", 1, keyed(stamp, OPACITY, [kf(0, 0, "hold")]) + keyed(ink, OPACITY, [kf(0, 0, "hold")]))
    play = anim(play_id, "Stamp", 30,
                keyed(stamp, OPACITY, [kf(0, 0, EASE_OUT), kf(1, 4, "hold"), kf(1, 20, EASE_IN), kf(0, 30)])
                + keyed(stamp, SX, [kf(1.6, 0, EASE_IN), kf(0.94, 6, EASE_OUT), kf(1.02, 9, EASE_IN_OUT), kf(1, 12)])
                + keyed(stamp, SY, [kf(1.6, 0, EASE_IN), kf(0.94, 6, EASE_OUT), kf(1.02, 9, EASE_IN_OUT), kf(1, 12)])
                + keyed(stamp, ROT, [kf(-0.2, 0, EASE_IN), kf(-0.105, 6)])
                + keyed(ink, OPACITY, [kf(0, 0, "hold"), kf(0, 5, EASE_OUT), kf(1, 7, EASE_IN), kf(0, 16), kf(0, 30)]))
    sm, sm_xml = one_shot_machine(i, "Stamp", p, "stamp", rest_id, play_id)
    roots = f'<FontAsset file="Bitter.ttf" name="Bitter" id="{font}"/>'
    return document(i, "Carimbo", W, H, sm_xml, sm, vm_xml, vm, inst, rest + play, scene + smudge, roots)


# ---------------------------------------------------------------- Trilha: lesson-path node
def trilha():
    """Ring shows `progress` (0-100) as an ink arc; `done` floods the disc with ink and draws a check."""
    i = Ids(1)
    S = 96
    vm_xml, vm, inst, p = view_model(i, "TrilhaVM", [("progress", "number", 0), ("done", "boolean", "false"), ("reduceMotion", "boolean", "false")])
    arc_trim, check_trim, flood, check = i(), i(), i(), i()
    c = S / 2
    track = shape(i(), "Track", ellipse(76, 76), stroke(RULE, 8), x=c, y=c)
    arc = shape(i(), "Arc", ellipse(76, 76), stroke(INK, 8, trim=arc_trim), x=c, y=c)
    disc = shape(i(), "Disc", ellipse(62, 62), fill(PAPER), x=c, y=c)
    ink = shape(flood, "Flood", ellipse(84, 84), fill(INK), x=c, y=c, scale=0)
    tick = shape(check, "Check", smooth_path([(-14, 1), (-4, 11), (15, -10)], False), stroke(PAPER, 7, trim=check_trim), x=c, y=c + 2)
    scene = tick + ink + disc + arc + track
    a = {k: i() for k in ("p0", "p100", "open", "done", "doneStill")}
    anims = (
        anim(a["p0"], "Progress 0", 1, keyed(arc_trim, TRIM_END, [kf(0, 0, "hold")]))
        + anim(a["p100"], "Progress 100", 1, keyed(arc_trim, TRIM_END, [kf(1, 0, "hold")]))
        + anim(a["open"], "Open", 1, keyed(flood, SX, [kf(0, 0, "hold")]) + keyed(flood, SY, [kf(0, 0, "hold")])
               + keyed(check_trim, TRIM_END, [kf(0, 0, "hold")]))
        + anim(a["done"], "Done", 30,
               keyed(flood, SX, [kf(0, 0, EASE_OUT), kf(1.08, 12, EASE_IN_OUT), kf(1, 18)])
               + keyed(flood, SY, [kf(0, 0, EASE_OUT), kf(1.08, 12, EASE_IN_OUT), kf(1, 18)])
               + keyed(check_trim, TRIM_END, [kf(0, 0, "hold"), kf(0, 12, EASE_OUT), kf(1, 26), kf(1, 30)]))
        + anim(a["doneStill"], "Done still", 1, keyed(flood, SX, [kf(1, 0, "hold")]) + keyed(flood, SY, [kf(1, 0, "hold")])
               + keyed(check_trim, TRIM_END, [kf(1, 0, "hold")]))
    )
    sm, l_prog, l_done = i(), i(), i()
    blend = i()
    s = {k: i() for k in ("open", "done", "still")}

    def to(name, done, reduce=None, mix=120):
        conds = cond_bool(p["done"], done) + (cond_bool(p["reduceMotion"], reduce) if reduce else "")
        return f'<StateTransition stateToId="{s[name]}" duration="{mix}">{conds}</StateTransition>'

    sm_xml = f"""<StateMachine name="Node" id="{sm}">
        <StateMachineLayer name="Progress" id="{l_prog}">
            <AnyState x="0" y="-120"/>
            <ExitState x="480" y="0"/>
            <EntryState x="0" y="0"><StateTransition stateToId="{blend}"/></EntryState>
            <BlendState1DViewModel x="240" y="0" id="{blend}">
                <BindablePropertyNumber><DataBindContext sourcePathIds="{p['progress']}" propertyKey="636"/></BindablePropertyNumber>
                <BlendAnimation1D animationId="{a['p0']}" value="0"/><BlendAnimation1D animationId="{a['p100']}" value="100"/>
            </BlendState1DViewModel>
        </StateMachineLayer>
        <StateMachineLayer name="Done" id="{l_done}">
            <AnyState x="0" y="-160"/>
            <ExitState x="720" y="0"/>
            <EntryState x="0" y="0">{to("open", "false", mix=0)}{to("done", "true", "false", mix=0)}{to("still", "true", "true", mix=0)}</EntryState>
            <AnimationState x="240" y="0" animationId="{a['open']}" id="{s['open']}">{to("done", "true", "false", mix=0)}{to("still", "true", "true", mix=0)}</AnimationState>
            <AnimationState x="400" y="0" animationId="{a['done']}" id="{s['done']}">{to("open", "false")}</AnimationState>
            <AnimationState x="560" y="0" animationId="{a['doneStill']}" id="{s['still']}">{to("open", "false", mix=0)}</AnimationState>
        </StateMachineLayer>
    </StateMachine>"""
    return document(i, "Node", S, S, sm_xml, sm, vm_xml, vm, inst, anims, scene)


PROJECTS = {"pagina": ("Pagina", pagina), "carimbo": ("Carimbo", carimbo), "trilha": ("Node", trilha)}

if __name__ == "__main__":
    for proj, (main, build) in PROJECTS.items():
        d = HERE / proj
        d.mkdir(exist_ok=True)
        (d / "rive.yaml").write_text(f"name: {proj}\nmain: {main}\nlogs:\n  file: build/rive.log\n  problems: build/problems.log\n")
        (d / ".gitignore").write_text("build/\n")
        (d / f"{proj}.rml").write_text(build())
    shutil.copy(HERE / "fonts" / "Bitter-stamp.ttf", HERE / "carimbo" / "Bitter.ttf")
    print("wrote", ", ".join(PROJECTS))
