# UI Rive moments

`gen_ui.py` writes one RML project per moment; `rive <project> --once` compiles it, and the `.riv` is copied to `public/rive/`. All use `@rive-app/canvas` 2.43.1 with the wasm at `public/mascot/rive.wasm`, and the Cartilha palette (paper #fbfaf5, ink #1f2a44, pen #c2410c, rule #d7deec).

```
python3 gen_ui.py
for p in pagina carimbo trilha; do rive $p --verify && rive $p --once && cp $p/build/$p.riv ../../public/rive/; done
```

| File | Artboard | State machine | View model inputs | Behaviour |
|---|---|---|---|---|
| `public/rive/pagina.riv` | `Pagina` (400x800, play with Fit.Cover) | `Turn` | `turn` (trigger) | A ruled sheet sweeps in from the right with a curled edge, covers the screen at frame 13 (~220 ms: swap the screen underneath then), and leaves to the left at frame 27 (450 ms). Transparent at rest. |
| `public/rive/carimbo.riv` | `Carimbo` (240x120) | `Stamp` | `stamp` (trigger) | "REGISTRADO" stamp drops from 1.6x, thumps to 1x tilted -6 degrees, holds, fades out by 500 ms. Transparent at rest. Re-firing restarts it. |
| `public/rive/trilha.riv` | `Node` (96x96) | `Node` | `progress` (number 0-100), `done` (boolean), `reduceMotion` (boolean) | Ring arc from 12 o'clock shows progress. `done` true floods the disc with ink and draws a paper check (500 ms); with `reduceMotion` it jumps to the finished pose. `done` false empties it. |

The stamp text uses Bitter (variable, weight 800 via a `wght` axis), subset to the letters of REGISTRADO (`fonts/Bitter-stamp.ttf`, from Google Fonts `fonts/Bitter.ttf`, OFL), copied into `carimbo/` at generation time.

The CLI renders screenshots on an opaque dark ground; to judge colours on paper, copy a project to a scratch folder and add a paper rectangle as the artboard's last child.
