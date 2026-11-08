#!/usr/bin/env sh
# Observed source-only freeze checks, 2026-11-08 UTC. Not native IRIS or browser runs.
set -eu
git rev-parse HEAD  # 915878fc36604fb942e778311697cc0bd7db7f8c
git status --porcelain  # clean
uv run pytest -q
uv run python scripts/package_ipm.py --output /tmp/silentshift-030-freeze-stage
# Verify package inventory, all FileCopy/Resource declarations and exact docs/IPM.md bytes.
npm --prefix web ci --no-audit --no-fund
npm --prefix web run check
npm --prefix web run build
# 410 local Markdown targets checked, 0 missing, across 12 release/entry docs.
# The clean IRIS, native live scenarios/replays and browser tests were not run here.
