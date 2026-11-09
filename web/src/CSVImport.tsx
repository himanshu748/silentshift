import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  ArrowRight,
  CheckCircle2,
  Download,
  LoaderCircle,
  LockKeyhole,
  ShieldCheck,
  Upload,
} from "lucide-react";
import { ApiError, request } from "./api";
import type { Resource } from "./api";
import type { Health } from "./schema";
import {
  Badge,
  Button,
  DecisionBadge,
  ErrorState,
  InlineError,
  PageHeading,
  useActions,
} from "./ui";
import "./csv-import.css";

const Text = z.string().min(1);
const CSVCase = z.object({
  id: Text,
  routing: z.enum(["PROCESSING", "DELIVERED", "QUARANTINED", "REVIEW", "REJECTED"]),
  trace_id: z.union([z.string(), z.number()]).nullable(),
  delivery_count: z.number().int().nonnegative(),
  agent: z
    .object({
      status: z.string().nullable().optional(),
      failure_code: z.string().nullable().optional(),
    })
    .nullable(),
});
type CSVCase = z.infer<typeof CSVCase>;
const PreviewSchema = z.object({
  preview_hash: Text,
  feed_sha256: Text,
  approved_sha256: Text,
  mode: z.literal("per-line-simulator"),
  atomic_order_delivery: z.literal(false),
  order_completeness: z.literal("not_verified"),
  records: z
    .array(
      z.object({
        order_id: Text,
        line_id: Text,
        partner: Text,
        source_row: z.number().int().positive(),
        message: z
          .object({
            event_id: Text,
            contract_id: Text,
            product_id: Text,
            quantity: Text,
            unit: Text,
          })
          .passthrough(),
        existing_case: CSVCase.nullable(),
      }),
    )
    .min(1)
    .max(20),
  references: z
    .array(
      z
        .object({
          id: Text,
          contract_id: Text,
          quantity: Text,
          unit: Text,
          approval_provenance: z.object({
            revision: Text,
            approved_by: Text,
            approved_at: Text,
          }),
        })
        .passthrough(),
    )
    .min(1)
    .max(20),
  import: z
    .object({
      created: z.number().int().nonnegative(),
      reused: z.number().int().nonnegative(),
      source_retained: z.literal(true),
      receipt: z
        .object({
          id: Text,
          imported_by: Text,
          imported_at: Text,
          reason: Text,
        })
        .passthrough(),
    })
    .optional(),
});
type Preview = z.infer<typeof PreviewSchema>;
type CSVFile = { name: string; content: string };
type Results = Record<string, CSVCase>;

const FEED =
  "partner,event_id,order_id,line_id,occurred_at,product_id,quantity,unit,business_unit";
const APPROVED =
  "partner,order_id,line_id,revision,effective_from,effective_to,approved_by,approved_at,product_id,quantity,unit,business_unit";

function sampleFiles(): [CSVFile, CSVFile] {
  const now = new Date();
  const stamp = crypto.randomUUID();
  const approved = new Date(now.valueOf() - 2 * 86400000).toISOString();
  const effective = new Date(now.valueOf() - 86400000).toISOString();
  const orders = [
    ["held", "20", "CASE"],
    ["clear", "240", "EA"],
  ];
  return [
    {
      name: "synthetic-orders.csv",
      content:
        FEED +
        "\n" +
        orders
          .map(
            ([id, quantity, unit]) =>
              `synthetic-ui-partner,${stamp}-${id},SYNTHETIC-${stamp}-${id},1,${now.toISOString()},SYNTHETIC-SKU,${quantity},${unit},TEST`,
          )
          .join("\n") +
        "\n",
    },
    {
      name: "synthetic-approved.csv",
      content:
        APPROVED +
        "\n" +
        orders
          .map(
            ([id]) =>
              `synthetic-ui-partner,SYNTHETIC-${stamp}-${id},1,v1,${effective},,synthetic-buyer,${approved},SYNTHETIC-SKU,240,EA,TEST`,
          )
          .join("\n") +
        "\n",
    },
  ];
}

function download(name: string, text: string, type: string) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Lives in WorkbenchApp, so switching workspace views keeps an in-flight run
// and its checkpoints. Nothing sensitive is written to browser storage.
export function useCSVImport() {
  const [files, setFiles] = useState<[CSVFile | null, CSVFile | null]>([null, null]);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [results, setResults] = useState<Results>({});
  const [confirmed, setConfirmed] = useState(false);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState<"preview" | "import" | "investigate" | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [complete, setComplete] = useState(false);
  const active = useRef(true);
  const running = useRef(false);
  const selection = useRef([0, 0]);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
      selection.current = selection.current.map((value) => value + 1);
    };
  }, []);
  useEffect(() => {
    if (!busy) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [busy]);

  function clearRun() {
    setPreview(null);
    setResults({});
    setConfirmed(false);
    setComplete(false);
    setPending(null);
  }
  function setFile(index: 0 | 1, file: CSVFile | null) {
    setFiles((previous) => {
      const next: [CSVFile | null, CSVFile | null] = [...previous];
      next[index] = file;
      return next;
    });
  }
  function reset(next: [CSVFile | null, CSVFile | null]) {
    selection.current = selection.current.map((value) => value + 1);
    setFiles(next);
    clearRun();
    setError(null);
  }
  async function choose(index: 0 | 1, file?: File) {
    if (running.current || !file) return;
    const version = ++selection.current[index];
    // Invalidate the old preview before asynchronous decoding, so it cannot
    // be submitted while a replacement file is still being read.
    setFile(index, null);
    clearRun();
    setError(null);
    try {
      if (file.size > 131072) throw new Error("Each CSV must be no larger than 128 KiB.");
      const content = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(
        await file.arrayBuffer(),
      );
      if (version !== selection.current[index] || !active.current) return;
      setFile(index, { name: file.name, content });
      clearRun();
      setError(null);
    } catch (failure) {
      if (version !== selection.current[index] || !active.current) return;
      setFile(index, null);
      clearRun();
      setError(failure instanceof TypeError ? new Error("Use a UTF-8 encoded CSV file.") : failure);
    }
  }
  function body() {
    if (!files[0] || !files[1]) throw new Error("Choose both independent CSV files.");
    return { orders_csv: files[0].content, approved_csv: files[1].content };
  }
  async function validate() {
    if (running.current) return;
    running.current = true;
    setBusy("preview");
    setError(null);
    clearRun();
    try {
      const data = await request("/api/imports/csv/preview", PreviewSchema, { body: body() });
      if (!active.current) return;
      setPreview(data);
      setResults(
        Object.fromEntries(
          data.records
            .filter((row) => row.existing_case)
            .map((row) => [row.message.event_id, row.existing_case!]),
        ),
      );
    } catch (failure) {
      if (active.current) setError(failure);
    } finally {
      running.current = false;
      if (active.current) setBusy(null);
    }
  }
  async function start() {
    if (running.current || !preview || !confirmed || reason.trim().length < 12) return;
    running.current = true;
    setBusy("import");
    setError(null);
    setComplete(false);
    try {
      const data = await request("/api/imports/csv/commit", PreviewSchema, {
        body: {
          ...body(),
          preview_hash: preview.preview_hash,
          confirmation: confirmed,
          reason,
        },
      });
      if (!active.current) return;
      setPreview(data);
      setBusy("investigate");
      for (const row of data.records) {
        if (!active.current) return;
        setPending(row.message.event_id);
        // A resumed preview reads the persisted case before considering a
        // submission. Unknown POST outcomes stop this loop; no automatic retry.
        let record =
          row.existing_case ?? (await request("/api/messages", CSVCase, { body: row.message }));
        if (!active.current) return;
        setResults((previous) => ({ ...previous, [row.message.event_id]: record }));
        const deadline = Date.now() + 180000;
        while (record.routing === "PROCESSING" && Date.now() < deadline) {
          await new Promise((resolve) => window.setTimeout(resolve, 1000));
          if (!active.current) return;
          record = await request(`/api/cases/${encodeURIComponent(record.id)}`, CSVCase);
          if (!active.current) return;
          setResults((previous) => ({ ...previous, [row.message.event_id]: record }));
        }
        if (record.routing === "PROCESSING")
          throw new Error(
            "This case is still processing. Preview the same files to read its persisted state before continuing.",
          );
      }
      setPending(null);
      setComplete(true);
    } catch (failure) {
      if (active.current) setError(failure);
    } finally {
      running.current = false;
      if (active.current) setBusy(null);
    }
  }
  return {
    files,
    preview,
    results,
    confirmed,
    setConfirmed,
    reason,
    setReason,
    busy,
    pending,
    error,
    complete,
    choose,
    validate,
    start,
    reset,
  };
}

function Quantity({ quantity, unit }: { quantity: string; unit: string }) {
  return (
    <span className="qty">
      <span className="qty-n">{quantity}</span> <span className="qty-u">{unit}</span>
    </span>
  );
}

function FileControl({
  label,
  description,
  index,
  file,
  busy,
  choose,
}: {
  label: string;
  description: string;
  index: 0 | 1;
  file: CSVFile | null;
  busy: boolean;
  choose: (index: 0 | 1, file?: File) => Promise<void>;
}) {
  const [dragging, setDragging] = useState(false);
  const bytes = file ? new TextEncoder().encode(file.content).length : 0;
  const inputId = `csv-file-${index}`;
  return (
    <div
      className={`csv-file ${dragging ? "dragging" : ""}`}
      data-selected={Boolean(file)}
      data-source={index === 0 ? "incoming" : "approved"}
      onDragOver={(event) => {
        if (busy) return;
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        if (!busy) void choose(index, event.dataTransfer.files[0]);
      }}
    >
      <div className="csv-file-head">
        <span className="csv-file-index mono">{index === 0 ? "A" : "B"}</span>
        <label className="label" htmlFor={inputId}>
          {label}
        </label>
        {file && (
          <span className="csv-file-ok">
            <CheckCircle2 size={13} aria-hidden="true" /> Selected
          </span>
        )}
      </div>
      <p>{description}</p>
      <input
        id={inputId}
        type="file"
        accept=".csv,text/csv"
        className="sr-only"
        tabIndex={-1}
        disabled={busy}
        onChange={(event) => {
          void choose(index, event.target.files?.[0]);
          event.target.value = "";
        }}
      />
      <div className="csv-file-pick">
        <div>
          <span className="csv-file-name" title={file?.name}>
            {file?.name ?? "No file chosen"}
          </span>
          <small>
            {file
              ? `${bytes.toLocaleString()} bytes · selected for preview`
              : "UTF-8 CSV · drop a file here or choose one"}
          </small>
        </div>
        <Button
          icon={Upload}
          aria-label={`Choose ${index === 0 ? "order feed" : "approved export"}`}
          disabled={busy}
          onClick={() => document.getElementById(inputId)?.click()}
        >
          {file ? "Replace file" : "Choose CSV"}
        </Button>
      </div>
    </div>
  );
}

export default function CSVImport({
  state,
  health,
}: {
  state: ReturnType<typeof useCSVImport>;
  health: Resource<Health>;
}) {
  const { openConnect } = useActions();
  const { files, preview, results, busy, pending, error, complete } = state;
  const canImport = health.data?.permissions?.csv_import === true;
  const supported = typeof health.data?.permissions?.csv_import === "boolean";
  const [samples] = useState(sampleFiles);
  const resolved =
    preview?.records
      .map((row) => results[row.message.event_id])
      .filter((result) => result && result.routing !== "PROCESSING") ?? [];
  const finalCount = resolved.length;
  const delivered = resolved.filter((result) => result.routing === "DELIVERED").length;
  const held = finalCount - delivered;
  const phase = complete ? "results" : preview ? "review" : "select";
  const stage = complete || busy === "import" || busy === "investigate" ? 2 : preview ? 1 : 0;
  const friendlyError =
    error instanceof ApiError && error.status === 422
      ? new Error("These files need a correction before they can be imported.")
      : error instanceof ApiError && error.status === 409
        ? new Error("This import conflicts with a saved record.")
        : error;
  return (
    <div className="csv" data-phase={phase}>
      <PageHeading
        title="CSV Import"
        description="Compare incoming orders with independently approved commitments, then investigate each line."
      >
        <Badge>IRIS simulator delivery</Badge>
      </PageHeading>
      {health.error && <ErrorState error={health.error} />}
      {!health.error && health.data && !supported && (
        <div className="callout callout-review">
          <LockKeyhole size={17} aria-hidden="true" />
          <div>
            <strong>CSV backend update required</strong>
            <p>
              Update the source installation to use CSV Import. The public IPM 0.2.0 backend does
              not include this workflow.
            </p>
          </div>
        </div>
      )}
      {!health.error && health.data && supported && !canImport && (
        <div className="callout callout-review">
          <LockKeyhole size={17} aria-hidden="true" />
          <div>
            <strong>Reference-import permission required</strong>
            <p>
              You can preview files with this account. An administrator must authorize an importer
              account before approved references can be added.
            </p>
            <Button onClick={openConnect}>Connect importer session</Button>
          </div>
        </div>
      )}

      <ol className="steps" aria-label="CSV import stages">
        {["Choose files", "Review evidence", "Investigate"].map((step, index) => (
          <li
            key={step}
            aria-current={stage === index ? "step" : undefined}
            data-done={stage > index}
          >
            <span className="mono">
              {stage > index ? <CheckCircle2 size={14} aria-hidden="true" /> : index + 1}
            </span>
            {step}
          </li>
        ))}
      </ol>

      <section className="panel" aria-label="CSV files">
        <div className="section-head">
          <div>
            <h2>Source files</h2>
            <p>Two independent exports. 128 KiB per file, up to 20 rows.</p>
          </div>
          <span className="csv-readonly">
            <ShieldCheck size={14} aria-hidden="true" /> Preview is read-only
          </span>
        </div>
        <div className="csv-files">
          <FileControl
            label="Order feed"
            description="Partner order lines before fulfillment."
            index={0}
            file={files[0]}
            busy={Boolean(busy)}
            choose={state.choose}
          />
          <FileControl
            label="Approved reference export"
            description="A separate export of approved terms and effective dates."
            index={1}
            file={files[1]}
            busy={Boolean(busy)}
            choose={state.choose}
          />
        </div>
        <div className="row-actions">
          <Button
            icon={busy === "preview" ? LoaderCircle : undefined}
            kind={preview ? "secondary" : "primary"}
            disabled={!files[0] || !files[1] || Boolean(busy) || !health.data || !supported}
            onClick={() => void state.validate()}
          >
            {busy === "preview"
              ? "Validating CSV files…"
              : error && preview
                ? "Preview persisted state again"
                : "Preview files"}
          </Button>
          <Button kind="ghost" disabled={Boolean(busy)} onClick={() => state.reset(samples)}>
            Use synthetic sample
          </Button>
        </div>
        <details className="disclosure plain csv-format">
          <summary>CSV layout and sample downloads</summary>
          <div className="disclosure-body">
            <p>
              Use the exact column names below, in any order. Quantities are positive decimal text;
              timestamps include a timezone. Only effective_to may be blank. No pack conversion is
              inferred.
            </p>
            <span className="kicker">Order feed</span>
            <pre tabIndex={0} className="code-line">
              {FEED}
            </pre>
            <span className="kicker">Approved export</span>
            <pre tabIndex={0} className="code-line">
              {APPROVED}
            </pre>
            <div className="row-actions">
              {samples.map((sample, index) => (
                <Button
                  key={sample.name}
                  icon={Download}
                  onClick={() => download(sample.name, sample.content, "text/csv;charset=utf-8")}
                >
                  Download {index === 0 ? "orders" : "approved"} sample
                </Button>
              ))}
            </div>
            <p className="small quiet">
              These matching samples are synthetic. An approver name in a CSV is supplied
              provenance, not an authenticated approval.
            </p>
          </div>
        </details>
      </section>

      {Boolean(error) && (
        <div className="csv-error">
          <InlineError error={friendlyError} />
          {error instanceof ApiError && error.status === 422 && (
            <p>
              Check column names, decimal quantities, timezone offsets, duplicate identities and
              approval fields. Correct the file, then preview again.
            </p>
          )}
          {error instanceof ApiError && error.status === 409 && (
            <p>
              An event identity or approved revision has different content in the saved import.
              Inspect that record; use a new revision only for a genuinely approved change.
            </p>
          )}
          {pending && (
            <p>
              Stopped at event <code>{pending}</code>. Later lines were not submitted. Preview the
              same files to recover saved cases; keep the original event IDs.
            </p>
          )}
        </div>
      )}

      {preview && (
        <section
          className="panel"
          aria-label="Validated CSV preview"
          aria-busy={busy === "import" || busy === "investigate"}
        >
          <div className="section-head">
            <div>
              <h2>
                {complete
                  ? "Import results"
                  : busy === "investigate"
                    ? "Investigating orders"
                    : "Review order lines"}
              </h2>
              <p>
                {preview.records.length} order lines · {preview.references.length} approved
                reference revisions
              </p>
            </div>
            <Badge>{complete ? "Processing complete" : "Server validated"}</Badge>
          </div>

          {finalCount > 0 && (
            <div className="tally" aria-label="Observed line outcomes">
              <span data-tone={held ? "hold" : undefined}>
                <strong className="mono">{held}</strong> held or rejected
              </span>
              <span data-tone={delivered ? "allow" : undefined}>
                <strong className="mono">{delivered}</strong> delivered to simulator
              </span>
              <span>
                {finalCount} of {preview.records.length} lines resolved
                {!preview.import ? " · saved results" : ""}
              </span>
            </div>
          )}

          <div className="table-wrap" role="region" aria-label="Order lines" tabIndex={0}>
            <table className="table csv-table">
              <thead>
                <tr>
                  <th scope="col">Order / source row</th>
                  <th scope="col">Incoming</th>
                  <th scope="col">Approved export</th>
                  <th scope="col">Native outcome</th>
                  <th scope="col">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {preview.records.map((row) => {
                  const result = results[row.message.event_id];
                  const refs = preview.references.filter(
                    (ref) => ref.contract_id === row.message.contract_id,
                  );
                  const working = pending === row.message.event_id && Boolean(busy);
                  return (
                    <tr
                      key={row.message.event_id}
                      data-route={result?.routing ?? "UNSUBMITTED"}
                      data-working={working}
                    >
                      <td data-label="Order / source row">
                        <strong className="break" title={row.order_id}>
                          {row.order_id}
                        </strong>
                        <small>
                          Line {row.line_id} · CSV row {row.source_row}
                        </small>
                        <small className="mono">{row.message.product_id}</small>
                      </td>
                      <td data-label="Incoming">
                        <Quantity quantity={row.message.quantity} unit={row.message.unit} />
                      </td>
                      <td data-label="Approved export">
                        {refs.length ? (
                          refs.map((ref) => (
                            <div key={ref.id} className="csv-ref">
                              <Quantity quantity={ref.quantity} unit={ref.unit} />
                              <small>
                                {ref.approval_provenance.revision} ·{" "}
                                {ref.approval_provenance.approved_by}
                              </small>
                            </div>
                          ))
                        ) : (
                          <span className="quiet">No matching line</span>
                        )}
                      </td>
                      <td data-label="Native outcome">
                        {result ? (
                          <>
                            <DecisionBadge value={result.routing} />
                            <small>
                              {result.delivery_count} simulator{" "}
                              {result.delivery_count === 1 ? "receipt" : "receipts"}
                            </small>
                            {result.agent?.status === "failed" && (
                              <small className="csv-agent-fail">
                                Agent failed: {result.agent.failure_code || "inspect case"}
                              </small>
                            )}
                          </>
                        ) : (
                          <Badge>
                            {working && (
                              <LoaderCircle size={12} className="spin" aria-hidden="true" />
                            )}
                            {working ? "Investigating…" : "Not submitted"}
                          </Badge>
                        )}
                      </td>
                      <td data-label="Evidence">
                        {result ? (
                          <>
                            <a
                              className="link"
                              href={`#investigations/${encodeURIComponent(result.id)}`}
                            >
                              Open case <ArrowRight size={13} aria-hidden="true" />
                            </a>
                            <small className="mono">Trace {result.trace_id || "pending"}</small>
                          </>
                        ) : (
                          <span className="quiet">After investigation</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {busy === "investigate" && (
            <div className="csv-progress-bar">
              <progress
                max={preview.records.length}
                value={finalCount}
                aria-label="Order lines resolved"
              />
              <span className="mono">
                {finalCount} / {preview.records.length}
              </span>
            </div>
          )}

          {!preview.import && (
            <div className="csv-authority">
              <div>
                <h3>Confirm the approved source</h3>
                <p>
                  Only import references you are authorized to use. Your account and source note
                  stay with the import.
                </p>
              </div>
              <div className="form">
                <label className="label" htmlFor="csv-source-note">
                  Approved source note <span>Required · 12 characters minimum</span>
                </label>
                <textarea
                  id="csv-source-note"
                  rows={2}
                  maxLength={160}
                  minLength={12}
                  value={state.reason}
                  onChange={(event) => state.setReason(event.target.value)}
                  disabled={Boolean(busy) || !canImport}
                  placeholder="Approval record and reference owner"
                />
                <label className="check">
                  <input
                    type="checkbox"
                    checked={state.confirmed}
                    onChange={(event) => state.setConfirmed(event.target.checked)}
                    disabled={Boolean(busy) || !canImport}
                  />
                  <span>I am authorized to import this independently approved reference export.</span>
                </label>
              </div>
            </div>
          )}

          <div className="csv-run">
            <div className="row-actions">
              {!complete && (
                <Button
                  icon={busy ? LoaderCircle : ShieldCheck}
                  kind="primary"
                  disabled={
                    !canImport ||
                    Boolean(busy) ||
                    Boolean(error) ||
                    !state.confirmed ||
                    state.reason.trim().length < 12 ||
                    Boolean(preview.import)
                  }
                  onClick={() => void state.start()}
                >
                  {busy === "import"
                    ? "Importing approved references…"
                    : busy === "investigate"
                      ? `Investigating lines · ${finalCount}/${preview.records.length}`
                      : "Import references and investigate"}
                </Button>
              )}
              {complete && (
                <span className="csv-done">
                  <CheckCircle2 size={16} aria-hidden="true" /> Import complete
                </span>
              )}
              {Object.keys(results).length > 0 && (
                <Button
                  icon={Download}
                  kind={complete ? "primary" : "secondary"}
                  disabled={Boolean(busy)}
                  onClick={() =>
                    download(
                      "silentshift-csv-results.json",
                      JSON.stringify({ ...preview, results, completed: complete }, null, 2),
                      "application/json",
                    )
                  }
                >
                  Download results
                </Button>
              )}
            </div>
            <p className="small quiet" role="status" aria-live="polite">
              {busy === "investigate"
                ? "Local inference is running. Keep this tab open; switching workspace views preserves progress."
                : complete
                  ? "IRIS simulator only. Results cover submitted lines; whole-order completeness and delivery are not verified."
                  : "Import retains both CSV originals and approved references in local IRIS. Investigation can create per-line simulator receipts."}
            </p>
          </div>

          <details className="disclosure plain">
            <summary>Source hashes and import provenance</summary>
            <dl className="meta meta-stacked">
              <div>
                <dt>Order feed SHA-256</dt>
                <dd className="mono break">{preview.feed_sha256}</dd>
              </div>
              <div>
                <dt>Approved export SHA-256</dt>
                <dd className="mono break">{preview.approved_sha256}</dd>
              </div>
              {preview.import && (
                <>
                  <div>
                    <dt>Imported by / at</dt>
                    <dd>
                      {preview.import.receipt.imported_by} · {preview.import.receipt.imported_at}
                    </dd>
                  </div>
                  <div>
                    <dt>Approved source note</dt>
                    <dd>{preview.import.receipt.reason}</dd>
                  </div>
                  <div>
                    <dt>References</dt>
                    <dd>
                      {preview.import.created} created · {preview.import.reused} reused
                    </dd>
                  </div>
                  <div>
                    <dt>Original uploads</dt>
                    <dd>Retained in local IRIS with the source hashes above.</dd>
                  </div>
                </>
              )}
            </dl>
          </details>
        </section>
      )}
    </div>
  );
}
