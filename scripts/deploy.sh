#!/usr/bin/env bash
# Builds the static app and deploys only dist/ to the personal Vercel team (cola-eleitoral.lucasmsa.com).
set -euo pipefail
cd "$(dirname "$0")/.."
SCOPE=lucas-moreira-e-silva-alves-projects
python3 pipeline/build_roster.py >/dev/null
python3 pipeline/build.py >/dev/null
pnpm typecheck && pnpm test && pnpm build
mkdir -p .deploy
find .deploy -mindepth 1 -maxdepth 1 ! -name .vercel -exec rm -rf {} +
cp -R dist/. .deploy/
cp vercel.json .deploy/
cd .deploy
npx -y vercel@latest deploy --prod --yes --scope "$SCOPE" | grep -E '"productionUrl"|"readyState"'
