#!/usr/bin/env sh
# Integrated mainline 0.3.0 source-only release checks run on Nov 8 2026 UTC.
# These are not a new clean-IRIS installation or browser E2E verification.
set -eu
git rev-parse HEAD  # b6bfdd099d9273fa4134ce34bfbc7269c52f8f6b
git status --porcelain
uv run pytest -q
uv run python scripts/package_ipm.py --output /tmp/silentshift-merged-final-stage
npm --prefix web run check
npm --prefix web run build
# Verify stage contains 58 files, 45 class resources, 11 assets,
# module 0.3.0 and docs/IPM.md with byte-for-byte matching source.
# Check local relative links across 12 release documents.
