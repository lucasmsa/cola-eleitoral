# 3. Deputados: match the list first, then people inside it

Date: 2026-09-30

## Status

Accepted

## Decision

- For deputado federal and estadual the first ranking is of lists (party, or federation
  when the party is in one), scored from Câmara party orientations (`orientacoes`) and
  the platform evidence of the list's majoritarian candidates.
- Inside the chosen list, candidates with a record (deputies elected in 2022 running
  again, and anyone else who voted in the chosen roll calls) are ranked with the same
  model as ADR-0002. Others are listed with their TSE data only.
- Estadual adds PB-specific questions sourced from ALPB votes and the six governor plans.

## Context

Seats are distributed by electoral and party quotient (Código Eleitoral, arts. 106 to
109), and a federation runs as a single list (Lei 14.208/2021). A vote for a person counts
first for the list. With well over a hundred names per office in PB, a person-first
match would rank mostly candidates without any evidence.

## Consequences

- A voter can also cast a legenda vote (list number only). The cola supports it.
