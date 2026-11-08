#!/usr/bin/env sh
# Observed isolated Linux candidate commands, November 8, 2026 UTC.
# This is NOT a clean IRIS verification or public release procedure.
set -eu
git rev-parse HEAD # expected 5e5c8a66d8a33651eb65f170569b089ded3cb06a for these exact receipts
grep '<Version>0.3.0</Version>' module.xml
uv run pytest -q
uv run python scripts/package_ipm.py --output /tmp/silentshift-030-stage
npm --prefix web ci --no-audit --no-fund
npm --prefix web run check
npm --prefix web run build
# Attempted but browser download blocked by EAI_AGAIN:
# (cd web && npx playwright install chromium)
