# Mascot

`gen_mascot.py` writes `mascot/calango.rml`; `rive mascot --once` compiles it to `mascot/build/mascot.riv`, copied to `public/mascot/calango.riv` (runtime wasm next to it, `@rive-app/canvas` 2.43.1).

Artboard `Calango` (256x256), state machine `Mascot`, view model `CalangoMascot`:

| Input | Type | Values |
|---|---|---|
| `mood` | number | 0 idle (breathes, blinks), 1 happy (one 0.6 s nod with closed eyes, then idle), 2 think (head tilt, eyes up), 3 reading (eyes scan a line left to right, head lowered; use while the explainer is open), 4 cheer (end of quiz: crouch, one hop with both arms out, 1 s, then idle) |
| `nod` | trigger | tiny 0.3 s head dip, on its own layer, so it plays over any mood; fire on each answer |
| `reduceMotion` | boolean | freezes on a still pose; `nod` does not play |

Happy and cheer play once and settle into idle while `mood` stays put; set `mood` to 0 and back to replay.

## Drawing

The October pass kept the silhouette, pose, palette and inputs and added: a second green (`SOFT`) for belly-side shading, a light rim on the head (`LIGHT`), a second smaller highlight in each eye, a crest with three separate bumps, softer pen-orange cheeks, toes spaced apart, and a curled tail tip in its own `Tail` node that sways a few degrees in idle (held still in every other mood). Transitions into happy and cheer mix in 80 ms and settle back to idle in 100 ms, so the open eyes and the closed-eye arcs never sit half-crossfaded.

`gen_favicon.py` writes `public/favicon.svg` from the same head geometry (`HEAD_PTS`, `CREST`, `EYE_X`, `EYE_Y`), converting each Rive mirrored vertex into SVG cubics.
