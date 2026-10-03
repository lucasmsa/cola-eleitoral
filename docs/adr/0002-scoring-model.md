# 2. Match score: record 80%, platform 20%, with a coverage band

Date: 2026-09-30

## Status

Accepted

## Decision

- Each answer is a stance in {-1, -0.5, 0, 0.5, 1} plus an importance of 0.5, 1 or 2
  ("quase nada", "um pouco", "muito"). Skipped questions do not count.
- A subject's position on a question is the mean of its `record` evidence (roll-call
  votes, sanctions, vetoes) blended with the mean of its `platform` evidence (registered
  plan, direct quotes) at 0.8 and 0.2. Without record evidence, platform counts 100% and
  the result is labelled "declarado, não medido".
- Agreement per question is `1 - |stance - position| / 2`. The score is the
  importance-weighted mean over covered questions.
- The score always shows its band: `low` assumes every uncovered answered question is a
  full disagreement, `high` a full agreement. Coverage and measured share are shown next
  to it. Ranking is by score, then coverage; subjects with no covered question are listed
  apart as "sem evidência".
- The 80/20 split and every importance stay editable on the results screen.
- Polls never enter the score. They are shown in a separate panel with institute, field
  dates, sample, margin and TSE registration.

## Context

A single match percentage hides how much of it is measured. A candidate who answered
two questions with a plan quote should not outrank one with ten roll calls on the same
footing, so coverage and the band are part of the result, not a footnote.

## Consequences

- Newcomers get wide bands. That is the honest state of the evidence.
- Implemented in `src/lib/score.ts`, specified by `src/lib/score.test.ts`.
