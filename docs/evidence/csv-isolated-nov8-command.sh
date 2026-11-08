docker --context colima-silentshift exec -i silentshift-bonus-load-main-nov8 \
  iris session IRIS -U SILENTSHIFT > .local/csv-importer-enable.txt <<'IRIS'
set sc=##class(SilentShift.Setup).EnableCSVImport($SYSTEM.Util.GetEnviron("SILENTSHIFT_IRIS_USERNAME"))
write "CSV_IMPORTER=",$system.Status.IsOK(sc),!
halt
IRIS
cat .local/csv-importer-enable.txt
python3 - <<'CHECK'
from pathlib import Path
assert "CSV_IMPORTER=1" in Path(".local/csv-importer-enable.txt").read_text().splitlines()
CHECK
SILENTSHIFT_WEB_URL=http://127.0.0.1:5178 \
SILENTSHIFT_API_URL=http://127.0.0.1:52913/silentshift/api \
node scripts/verify_csv_ui.mjs --execute --output-directory .local/csv-isolated-nov8
