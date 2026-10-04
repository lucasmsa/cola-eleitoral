![Cola Eleitoral](public/cover.png)

# Cola Eleitoral

Quiz for the 2026 Paraíba ballot (presidente, governador, senado, deputados). You answer policy questions, the app compares your answers with what each candidate did and said, and you leave with a printable cola in urna order.

Live at [cola-eleitoral.lucasmsa.com](https://cola-eleitoral.lucasmsa.com).

## How facts get in

Every fact the app shows is a row produced by `pipeline/` and checked by a script in `pipeline/checks/` against its primary source: TSE open data, Câmara and Senado open-data APIs, Planalto law texts, ALPB, the government plans registered at the TSE, official debate captions and major press quotes. Each script carries negative controls that must fail. `pipeline/build.py` copies into `src/data/` only the rows whose check passed. Decisions are in `docs/adr/`.

Answers stay in the browser (`localStorage`); the site makes no request outside its own domain.

## Run

```bash
pnpm install
pnpm dev            # http://localhost:5173
pnpm test           # Vitest
pnpm test:e2e       # Playwright golden path
python3 pipeline/build.py   # rebuild src/data from checked evidence
scripts/deploy.sh           # build and deploy dist/ to Vercel
```

Made by [lucasmsa](https://github.com/lucasmsa). Independent personal project: no affiliation with candidates, parties or federations, and no funding or donations. Corrections: lucasmsea@outlook.com.
