# 4. Evidence ships only after an executable check passes

Date: 2026-09-30

## Status

Accepted

## Decision

- Every fact in the app (roster rows, votes, quotes, poll numbers, urna order) is an
  `Evidence` or `Source` row produced by `pipeline/` and checked by a script in
  `pipeline/checks/`. Each check re-derives the claim from the cached primary source and,
  for a sample, from the live source.
- Each check script carries negative controls (known-false claims) that must fail. If a
  control passes, the whole report is void.
- `pipeline/build.py` copies into `src/data/` only the rows whose check passed.
- Source order: TSE open data; Câmara and Senado open-data APIs; Planalto law texts and
  Congresso veto pages; ALPB; plan PDFs registered at the TSE; direct quotes in major
  press. Press summaries without a direct quote are not evidence.
- Every row records its source URL and access date, shown on the fact card.

## Context

The app ranks real people for a real vote. A wrong vote attributed to a candidate is the
worst failure it can have, so nothing enters on memory or a summary.

## Consequences

- Gaps are visible: a question with no checked evidence for a candidate counts as
  uncovered (ADR-0002), never as a guess.
