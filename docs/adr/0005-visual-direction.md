# 5. Visual direction: Cartilha lessons, Teclado cola, Rive mascot

Date: 2026-09-30

## Status

Accepted

## Decision

- Lessons use the "Cartilha" direction: ruled notebook paper, Bitter for text and
  questions, Gaegu for hand-marked accents, ink #1f2a44 and pen orange #c2410c.
  Chosen from four rendered candidates (Urna, Cordel, Duolingo puro, Cartilha).
- The printable cola is "Teclado": credit-card size (85.6 × 54 mm), black on white,
  six numbered rows in urna order with one box per digit: deputado federal (4),
  deputado estadual (5), senador 1ª vaga (3), senador 2ª vaga (3), governador (2),
  presidente (2).
- The mascot is the Calango (caatinga lizard), a Rive character compiled from RML
  generated in `design/mascot/gen_mascot.py`. A `mood` number drives it (0 idle, 1 happy,
  2 think) and a `reduceMotion` boolean freezes it on a still pose. The happy state is
  a short nod with a closed-eye smile; the first, bouncier version was rejected as too
  much. Urninha and Carcará were the other candidates; the first SVG round was rejected.
- No palette uses a competing party's main colour as its dominant hue.

## Consequences

- Digit counts match `NR_CANDIDATO` lengths in the TSE 2026 candidate files.
