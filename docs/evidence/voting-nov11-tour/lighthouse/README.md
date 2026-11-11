# Local Lighthouse reports

The compact summary is in [../lighthouse-summary.json](../lighthouse-summary.json). Full unmodified Lighthouse JSON output is gzip-compressed to keep generated audit data out of the PR's line-by-line code review. The [index](index.json) records compressed and uncompressed hashes/sizes. Decompress with `gzip -dc REPORT.json.gz` or Python's standard `gzip.open`.

Commands used Lighthouse 13.6.0, local HTTP preview, default mobile and `--preset=desktop`, `--chrome-flags=--headless`, and categories performance/accessibility/best-practices/SEO. These are one-pass local preview measurements; no public-host performance or general guarantee is implied.
