# CSV order-feed pilot — local prototype

**Local CSV pilot for the existing IRIS production.** Prepare incoming order lines and import a separate approved-order export, then investigate each line through the native agent and deterministic policy. All supplied samples are synthetic. This pilot is outside the packaged `src/` classes and is not installed by IPM; React workbench remains 0.2.1, while public native IPM 0.3.0 now includes the shared CSV backend/parser. The [workbench path](../docs/CSV_IMPORT.md) is separate from these CLI pilot files.

Prefer the browser? Use [CSV Import in the workbench](../docs/CSV_IMPORT.md). That source feature shares this CLI's parser and adds explicit reference-import permissions and an authenticated import receipt. Public IPM 0.2.0 does not include the CSV additions; its registry release has not changed.

## Prepare a feed without running a model

From the repository root:

```sh
uv run python pilot/make_sample.py .local/my-csv-sample
uv run python pilot/orders.py \
  --orders .local/my-csv-sample/orders.csv \
  --approved .local/my-csv-sample/approved.csv \
  --output .local/my-csv-sample/prepared.json
```

The sample generator uses the current UTC time and explicit synthetic partner/order/product labels. It creates a new private directory and refuses an existing one. The preparation command makes no API or model calls, writes a new mode-0600 bundle and refuses to overwrite a file. Samples are not real partner data.

Use UTF-8 CSV, comma delimiters, conventional double-quote escaping and exactly these named columns (column order may vary):

```text
partner,event_id,order_id,line_id,occurred_at,product_id,quantity,unit,business_unit
```

The independently supplied, operator-approved export has this layout:

```text
partner,order_id,line_id,revision,effective_from,effective_to,approved_by,approved_at,product_id,quantity,unit,business_unit
```

`effective_to` alone may be blank. Timestamps need an explicit offset; quantities use positive plain decimal notation with at most nine fractional places. The pilot does not infer pack conversions, strip whitespace or repair invalid cells. Both files are limited to 128 KiB and 20 records; prepared bundles are also bounded. Duplicate headers/identities, extra or missing cells, control characters and symlink inputs are rejected.

The bundle binds each row to its source file hash and row number. Partner/event/line identity becomes the existing ingestion key; partner/order/line identity selects the independent reference. Changed content under the same event identity reaches the existing conflict gate rather than silently creating a new revision. Approval provenance is supplied by the trusted operator export; a CSV field does not authenticate the approver. Real-data provenance and approval controls still need a pilot agreement.

## Run the native verification

First complete [INSTALL.md](../INSTALL.md), including the local model setup. The verifier expects the existing `colima-silentshift` context, `silentshift-clean-iris-1` container, loopback API at port 52773 and private root `.env`. It requires at least 2 GiB free on the host. Use a new output directory for every run:

```sh
uv run python pilot/verify_native_csv.py \
  --output-directory .local/my-csv-verification --execute
```

This command compiles the operator-only importer, creates two fresh synthetic CSV orders, imports their approved references and submits both through the existing native API. It checks that `20 CASE` against `240 EA` is held with zero deliveries and that a matching `240 EA` line creates one simulator receipt. It also requires actual reads of all four agent tools, checks repeated submissions, rejects changed content under the same event identity, and tests import rollback and approval provenance. Inspect `verification.json`; a safe held case with a failed agent still fails the full verification.

`ReferenceImport.cls` uses explicit `%Get()` access for dynamic JSON properties on 154U. A batch is transactional: a conflicting revision rolls back earlier rows in that batch. Exact references are reused; an existing revision cannot be overwritten. The helper has no REST route and must be run by a trusted local operator. It does not authenticate an approval merely because the CSV names an approver.

## Import your prepared export

The following commands use the container name from this verification instance. If yours differs, substitute its name from `docker ps`. Prepare the private bundle using the first command above, then copy only that bundle and the helper into a new temporary directory in the container:

```sh
csv_import_dir=$(docker --context colima-silentshift exec silentshift-clean-iris-1 \
  mktemp -d /tmp/silentshift-csv.XXXXXXXX)
docker --context colima-silentshift cp pilot/ReferenceImport.cls \
  "silentshift-clean-iris-1:$csv_import_dir/ReferenceImport.cls"
docker --context colima-silentshift cp .local/my-csv-sample/prepared.json \
  "silentshift-clean-iris-1:$csv_import_dir/prepared.json"
docker --context colima-silentshift exec -u root silentshift-clean-iris-1 \
  chown irisowner:irisowner "$csv_import_dir/prepared.json"
docker --context colima-silentshift exec -i silentshift-clean-iris-1 \
  iris session IRIS -U SILENTSHIFT <<EOF
set sc=\$system.OBJ.Load("$csv_import_dir/ReferenceImport.cls","ck")
write "COMPILED=",\$system.Status.IsOK(sc),!
if \$system.Status.IsOK(sc) write "IMPORT=",##class(SilentShiftPilot.ReferenceImport).Import("$csv_import_dir/prepared.json"),!
halt
EOF
```

Require `COMPILED=1` and an `IMPORT` JSON result with `passed:true` before submitting. The two-record sample creates two references on its first import and reuses them on an exact repeat. A refused import is a failure even if the terminal process exits successfully. Stop and inspect the safe `stage` code; do not rewrite the source identity or approval fields to force acceptance. Copying a private file preserves host ownership, so the single-file `chown` above allows `irisowner` to read it without making it public.

For that imported reference bundle, submit the order lines:

```sh
uv run --env-file .env python pilot/orders.py \
  --orders .local/my-csv-sample/orders.csv \
  --approved .local/my-csv-sample/approved.csv \
  --submit-local --output .local/my-csv-sample/native-result.json
```

This may create **per-line simulator receipts**; it is not a no-write mode inside IRIS. The CLI reserves a private output before submission and checkpoints pending event/case IDs and completed lines. An uncertain submission is not automatically repeated. Inspect persisted state before resuming with the same identity. Agent failures remain visible alongside routing outcomes.

Order summaries describe submitted lines only. A held/unresolved line yields `HOLD`; a fully simulated set yields `ALL_SUBMITTED_LINES_SIMULATED`. Every order result explicitly sets `atomic_order_delivery=false` and `order_completeness=not_verified`. There is no whole-order delivery gate, external ERP connector, X12 parser, hosted service or customer-data validation in this prototype.

## Verification

```sh
uv run pytest -q tests/test_csv_pilot.py
```

Tests cover strict format/numeric/time boundaries, independent references, event identity, mixed-order summaries, uncertain dispatch checkpoints, visible agent failures and refusal before submission when disk space is low or the output already exists. Transport doubles establish local logic only. Actual native results and retained failures are in [BUILD_STATUS.md](../docs/BUILD_STATUS.md).
