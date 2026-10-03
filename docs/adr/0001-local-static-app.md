# 1. Static Vite app, answers stay in the browser

Date: 2026-09-30

## Status

Accepted

## Decision

- Vite, React 19 and TypeScript `strict`, Tailwind v4 on tokens, Zustand with `persist`
  for answers, Vitest and Testing Library, Playwright for the golden path. Same stack as
  hiit-maker.
- The app is static. Candidate data ships as JSON built by `pipeline/`. Answers are kept
  in `localStorage` only; there is no backend, no analytics and no network call after load.
- First target is localhost. A Vercel deploy is possible later without code changes,
  since nothing is stored server side.
- Components render only. State and handlers live in `use*` hooks, pure calculations in
  `src/lib`, constants and copy in `src/config`.

## Context

Answers are political opinions. Keeping them on the device removes the whole class of
storage, consent and leak questions.

## Consequences

- Clearing site data erases the answers. The results screen offers a JSON export.
- Data updates need a rebuild of the JSON and a redeploy.
