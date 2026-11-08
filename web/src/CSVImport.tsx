import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  ArrowRight,
  CheckCircle2,
  LoaderCircle,
  Download,
  FileSpreadsheet,
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
  routing: z.enum([
    "PROCESSING",
    "DELIVERED",
    "QUARANTINED",
    "REVIEW",
    "REJECTED",
  ]),
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
  const [files, setFiles] = useState<[CSVFile | null, CSVFile | null]>([
    null,
    null,
  ]);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [results, setResults] = useState<Results>({});
  const [confirmed, setConfirmed] = useState(false);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState<"preview" | "import" | "investigate" | null>(
    null,
  );
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

  function reset(next: [CSVFile | null, CSVFile | null]) {
    selection.current = selection.current.map((value) => value + 1);
    setFiles(next);
    setPreview(null);
    setResults({});
    setConfirmed(false);
    setComplete(false);
    setPending(null);
    setError(null);
  }
  async function choose(index: 0 | 1, file?: File) {
    if (running.current || !file) return;
    const version = ++selection.current[index];
    // Invalidate the old preview before asynchronous decoding, so it cannot
    // be submitted while a replacement file is still being read.
    setFiles((previous) => {
      const next: [CSVFile | null, CSVFile | null] = [...previous];
      next[index] = null;
      return next;
    });
    setPreview(null);
    setResults({});
    setConfirmed(false);
    setComplete(false);
    setPending(null);
    setError(null);
    try {
      if (file.size > 131072)
        throw new Error("Each CSV must be no larger than 128 KiB.");
      const content = new TextDecoder("utf-8", {
        fatal: true,
        ignoreBOM: true,
      }).decode(await file.arrayBuffer());
      if (version !== selection.current[index] || !active.current) return;
      setFiles((previous) => {
        const next: [CSVFile | null, CSVFile | null] = [...previous];
        next[index] = { name: file.name, content };
        return next;
      });
      setPreview(null);
      setResults({});
      setConfirmed(false);
      setComplete(false);
      setPending(null);
      setError(null);
    } catch (failure) {
      if (version !== selection.current[index] || !active.current) return;
      setFiles((previous) => {
        const next: [CSVFile | null, CSVFile | null] = [...previous];
        next[index] = null;
        return next;
      });
      setPreview(null);
      setResults({});
      setConfirmed(false);
      setComplete(false);
      setPending(null);
      setError(
        failure instanceof TypeError
          ? new Error("Use a UTF-8 encoded CSV file.")
          : failure,
      );
    }
  }
  function body() {
    if (!files[0] || !files[1])
      throw new Error("Choose both independent CSV files.");
    return { orders_csv: files[0].content, approved_csv: files[1].content };
  }
  async function validate() {
    if (running.current) return;
    running.current = true;
    setBusy("preview");
    setError(null);
    setPreview(null);
    setComplete(false);
    setConfirmed(false);
    setResults({});
    setPending(null);
    try {
      const data = await request("/api/imports/csv/preview", PreviewSchema, {
        body: body(),
      });
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
    if (running.current || !preview || !confirmed || reason.trim().length < 12)
      return;
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
          row.existing_case ??
          (await request("/api/messages", CSVCase, { body: row.message }));
        if (!active.current) return;
        setResults((previous) => ({
          ...previous,
          [row.message.event_id]: record,
        }));
        const deadline = Date.now() + 180000;
        while (record.routing === "PROCESSING" && Date.now() < deadline) {
          await new Promise((resolve) => window.setTimeout(resolve, 1000));
          if (!active.current) return;
          record = await request(
            `/api/cases/${encodeURIComponent(record.id)}`,
            CSVCase,
          );
          if (!active.current) return;
          setResults((previous) => ({
            ...previous,
            [row.message.event_id]: record,
          }));
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

function CSVQuantity({ quantity, unit }: { quantity: string; unit: string }) {
  return (
    <span className="csv-quantity">
      <span className="csv-quantity-number">{quantity}</span>{" "}
      <span className="csv-quantity-unit">{unit}</span>
    </span>
  );
}

function CSVFileControl({
  label,
  index,
  file,
  busy,
  choose,
}: {
  label: string;
  index: 0 | 1;
  file: CSVFile | null;
  busy: boolean;
  choose: (index: 0 | 1, file?: File) => Promise<void>;
}) {
  const Icon = index === 0 ? FileSpreadsheet : ShieldCheck;
  const bytes = file ? new TextEncoder().encode(file.content).length : 0;
  return (
    <div
      className="csv-file"
      data-selected={Boolean(file)}
      data-source={index === 0 ? "incoming" : "approved"}
    >
      <div className="csv-file-heading">
        <span className="csv-file-symbol">
          <Icon size={19} aria-hidden="true" />
        </span>
        <label className="field-label" htmlFor={`csv-file-${index}`}>
          {label}
        </label>
        {file && (
          <span className="csv-file-selected">
            <CheckCircle2 size={13} aria-hidden="true" /> Selected
          </span>
        )}
      </div>
      <p>
        {index === 0
          ? "Partner order lines before fulfillment."
          : "A separate export of approved terms and effective dates."}
      </p>
      <input
        id={`csv-file-${index}`}
        type="file"
        accept=".csv,text/csv"
        hidden
        disabled={busy}
        onChange={(event) => {
          void choose(index, event.target.files?.[0]);
          event.target.value = "";
        }}
      />
      <div className="csv-file-selection">
        <div className="csv-file-description">
          <span className="csv-filename" title={file?.name}>
            {file?.name ?? "Choose a CSV export"}
          </span>
          <small>
            {file
              ? `${bytes.toLocaleString()} bytes · selected for preview`
              : "UTF-8 CSV · independent source"}
          </small>
        </div>
        <Button
          icon={Upload}
          aria-label={`Choose ${index === 0 ? "order feed" : "approved export"}`}
          disabled={busy}
          onClick={() => document.getElementById(`csv-file-${index}`)?.click()}
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
  const delivered = resolved.filter(
    (result) => result.routing === "DELIVERED",
  ).length;
  const held = finalCount - delivered;
  const phase = complete ? "results" : preview ? "review" : "select";
  const stage =
    complete || busy === "import" || busy === "investigate"
      ? 2
      : preview
        ? 1
        : 0;
  const friendlyError =
    error instanceof ApiError && error.status === 422
      ? new Error("These files need a correction before they can be imported.")
      : error instanceof ApiError && error.status === 409
        ? new Error("This import conflicts with a saved record.")
        : error;
  return (
    <div className="csv-workflow" data-phase={phase}>
      <PageHeading
        eyebrow="Workspace / order feeds"
        title="CSV Import"
        description="Compare incoming orders with independently approved commitments."
      >
        <Badge>IRIS simulator</Badge>
      </PageHeading>
      {health.error && <ErrorState error={health.error} />}
      {!health.error && health.data && !supported && (
        <div className="csv-permission">
          <LockKeyhole size={18} aria-hidden="true" />
          <div>
            <strong>CSV backend update required</strong>
            <p>
              Update the source installation to use CSV Import. The public IPM
              0.2.0 backend does not include this workflow.
            </p>
          </div>
        </div>
      )}
      {!health.error && health.data && supported && !canImport && (
        <div className="csv-permission">
          <LockKeyhole size={18} aria-hidden="true" />
          <div>
            <strong>Reference-import permission required</strong>
            <p>
              You can preview files with this account. An administrator must
              authorize an importer account before approved references can be
              added.
            </p>
            <Button onClick={openConnect}>Connect importer session</Button>
          </div>
        </div>
      )}
      <ol className="csv-steps" aria-label="CSV import stages">
        {["Choose files", "Review evidence", "Investigate"].map(
          (step, index) => (
            <li
              key={step}
              aria-current={stage === index ? "step" : undefined}
              data-done={stage > index}
            >
              <span>
                {stage > index ? (
                  <CheckCircle2 size={14} aria-hidden="true" />
                ) : (
                  index + 1
                )}
              </span>
              {step}
            </li>
          ),
        )}
      </ol>
      <section className="csv-sources" aria-label="CSV files">
        <div className="csv-source-title">
          <h2>Source files</h2>
          <span>128 KiB per file · up to 20 rows</span>
        </div>
        <div className="csv-files">
          <CSVFileControl
            label="Order feed"
            index={0}
            file={files[0]}
            busy={Boolean(busy)}
            choose={state.choose}
          />
          <CSVFileControl
            label="Approved reference export"
            index={1}
            file={files[1]}
            busy={Boolean(busy)}
            choose={state.choose}
          />
        </div>
        <div className="csv-source-toolbar">
          <div className="csv-file-actions">
            <Button
              icon={busy === "preview" ? LoaderCircle : undefined}
              kind={preview ? "secondary" : "primary"}
              disabled={
                !files[0] ||
                !files[1] ||
                Boolean(busy) ||
                !health.data ||
                !supported
              }
              onClick={() => void state.validate()}
            >
              {busy === "preview"
                ? "Validating CSV files…"
                : error && preview
                  ? "Preview persisted state again"
                  : "Preview files"}
            </Button>
            <Button
              kind="ghost"
              disabled={Boolean(busy)}
              onClick={() => state.reset(samples)}
            >
              Use synthetic sample
            </Button>
          </div>
          <span className="csv-readonly-note">
            <ShieldCheck size={14} aria-hidden="true" /> Preview is read-only
          </span>
        </div>
      </section>
      <details className="csv-format">
        <summary>CSV layout and sample downloads</summary>
        <div className="csv-format-body">
          <p>
            Use the exact column names below, in any order. Quantities are
            positive decimal text; timestamps include a timezone. Only
            effective_to may be blank. No pack conversion is inferred.
          </p>
          <strong>Order feed</strong>
          <pre tabIndex={0}>{FEED}</pre>
          <strong>Approved export</strong>
          <pre tabIndex={0}>{APPROVED}</pre>
          <div className="csv-file-actions">
            {samples.map((sample, index) => (
              <Button
                key={sample.name}
                icon={Download}
                onClick={() =>
                  download(
                    sample.name,
                    sample.content,
                    "text/csv;charset=utf-8",
                  )
                }
              >
                Download {index === 0 ? "orders" : "approved"} sample
              </Button>
            ))}
          </div>
          <p>
            These matching samples are synthetic. An approver name in a CSV is
            supplied provenance, not an authenticated approval.
          </p>
        </div>
      </details>
      {Boolean(error) && (
        <div className="csv-error">
          <InlineError error={friendlyError} />
          {error instanceof ApiError && error.status === 422 && (
            <p>
              Check column names, decimal quantities, timezone offsets,
              duplicate identities and approval fields. Correct the file, then
              preview again.
            </p>
          )}
          {error instanceof ApiError && error.status === 409 && (
            <p>
              An event identity or approved revision has different content in
              the saved import. Inspect that record; use a new revision only for
              a genuinely approved change.
            </p>
          )}
          {pending && (
            <p>
              Stopped at event <code>{pending}</code>. Later lines were not
              submitted. Preview the same files to recover saved cases; keep the
              original event IDs.
            </p>
          )}
        </div>
      )}
      {preview && (
        <section
          className="csv-preview"
          aria-label="Validated CSV preview"
          aria-busy={busy === "import" || busy === "investigate"}
        >
          <div className="csv-section-title">
            <div>
              <h2>
                {complete
                  ? "Import results"
                  : busy === "investigate"
                    ? "Investigating orders"
                    : "Review order lines"}
              </h2>
              <p>
                {preview.records.length} order lines ·{" "}
                {preview.references.length} approved reference revisions
              </p>
            </div>
            <Badge tone="muted">
              {complete ? "Processing complete" : "Server validated"}
            </Badge>
          </div>
          {finalCount > 0 && (
            <div
              className="csv-outcome-summary"
              aria-label="Observed line outcomes"
            >
              <span className={held ? "csv-held-count" : ""}>
                <strong>{held}</strong> held or rejected
              </span>
              <span className={delivered ? "csv-delivered-count" : ""}>
                <strong>{delivered}</strong> delivered
              </span>
              <span>
                {finalCount} of {preview.records.length} lines resolved
                {!preview.import ? " · saved results" : ""}
              </span>
            </div>
          )}
          <div className="table-scroll">
            <table className="data-table csv-table">
              <colgroup>
                <col className="csv-order-col" />
                <col className="csv-incoming-col" />
                <col className="csv-approved-col" />
                <col className="csv-outcome-col" />
                <col className="csv-evidence-col" />
              </colgroup>
              <thead>
                <tr>
                  <th>Order / source row</th>
                  <th>Incoming</th>
                  <th>Approved export</th>
                  <th>Native outcome</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {preview.records.map((row) => {
                  const result = results[row.message.event_id];
                  const refs = preview.references.filter(
                    (ref) => ref.contract_id === row.message.contract_id,
                  );
                  const working =
                    pending === row.message.event_id && Boolean(busy);
                  return (
                    <tr
                      key={row.message.event_id}
                      data-route={result?.routing ?? "UNSUBMITTED"}
                      data-working={working}
                    >
                      <td>
                        <span className="csv-cell-label">
                          Order / source row
                        </span>
                        <strong
                          className="csv-order-title"
                          title={row.order_id}
                        >
                          {row.order_id}
                        </strong>
                        <small>
                          Line {row.line_id} · CSV row {row.source_row}
                        </small>
                        <small>{row.message.product_id}</small>
                      </td>
                      <td className="csv-incoming">
                        <span className="csv-cell-label">Incoming</span>
                        <CSVQuantity
                          quantity={row.message.quantity}
                          unit={row.message.unit}
                        />
                      </td>
                      <td>
                        <span className="csv-cell-label">Approved export</span>
                        {refs.length ? (
                          refs.map((ref) => (
                            <div className="csv-approved-value" key={ref.id}>
                              <CSVQuantity
                                quantity={ref.quantity}
                                unit={ref.unit}
                              />
                              <small>
                                {ref.approval_provenance.revision} ·{" "}
                                {ref.approval_provenance.approved_by}
                              </small>
                            </div>
                          ))
                        ) : (
                          <span>No matching line</span>
                        )}
                      </td>
                      <td>
                        <span className="csv-cell-label">Native outcome</span>
                        {result ? (
                          <>
                            <DecisionBadge value={result.routing} />
                            <small>
                              {result.delivery_count} simulator{" "}
                              {result.delivery_count === 1
                                ? "receipt"
                                : "receipts"}
                            </small>
                            {result.agent?.status === "failed" && (
                              <small className="csv-agent-failure">
                                Agent failed:{" "}
                                {result.agent.failure_code || "inspect case"}
                              </small>
                            )}
                          </>
                        ) : (
                          <Badge>
                            {working && (
                              <LoaderCircle
                                size={12}
                                className="csv-spinner"
                                aria-hidden="true"
                              />
                            )}
                            {working ? "Investigating…" : "Not submitted"}
                          </Badge>
                        )}
                      </td>
                      <td>
                        <span className="csv-cell-label">Evidence</span>
                        {result ? (
                          <>
                            <a
                              className="text-link csv-case-link"
                              href={`#investigations/${encodeURIComponent(result.id)}`}
                            >
                              Open case{" "}
                              <ArrowRight size={14} aria-hidden="true" />
                            </a>
                            <small className="mono">
                              Trace {result.trace_id || "pending"}
                            </small>
                          </>
                        ) : (
                          <span className="csv-evidence-pending">
                            After investigation
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {busy === "investigate" && (
            <div className="csv-run-progress">
              <progress
                max={preview.records.length}
                value={finalCount}
                aria-label="Order lines resolved"
              />
              <span>
                {finalCount} of {preview.records.length} lines resolved
              </span>
            </div>
          )}
          {!preview.import && (
            <div className="csv-authority">
              <div>
                <h3>Confirm the approved source</h3>
                <p>
                  Only import references you are authorized to use. Your account
                  and source note stay with the import.
                </p>
              </div>
              <div className="csv-authority-fields">
                <label className="field-label" htmlFor="csv-source-note">
                  Approved source note
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
                <label className="csv-confirm">
                  <input
                    type="checkbox"
                    checked={state.confirmed}
                    onChange={(event) =>
                      state.setConfirmed(event.target.checked)
                    }
                    disabled={Boolean(busy) || !canImport}
                  />
                  <span>
                    I am authorized to import this independently approved
                    reference export.
                  </span>
                </label>
              </div>
            </div>
          )}
          <div className="csv-run-footer">
            <div className="csv-run-actions">
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
                <span className="csv-run-finished">
                  <CheckCircle2 size={17} aria-hidden="true" /> Import complete
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
                      JSON.stringify(
                        { ...preview, results, completed: complete },
                        null,
                        2,
                      ),
                      "application/json",
                    )
                  }
                >
                  Download results
                </Button>
              )}
            </div>
            <p className="csv-progress" role="status" aria-live="polite">
              {busy === "investigate"
                ? "Local inference is running. Keep this tab open; switching workspace views preserves progress."
                : complete
                  ? "IRIS simulator only. Results cover submitted lines; whole-order completeness and delivery are not verified."
                  : "Import retains both CSV originals and approved references in local IRIS. Investigation can create per-line simulator receipts."}
            </p>
          </div>
          <div className="csv-hashes">
            <details>
              <summary>Source hashes and import provenance</summary>
              <dl>
                <dt>Order feed SHA-256</dt>
                <dd>
                  <code>{preview.feed_sha256}</code>
                </dd>
                <dt>Approved export SHA-256</dt>
                <dd>
                  <code>{preview.approved_sha256}</code>
                </dd>
                {preview.import && (
                  <>
                    <dt>Imported by / at</dt>
                    <dd>
                      {preview.import.receipt.imported_by} ·{" "}
                      {preview.import.receipt.imported_at}
                    </dd>
                    <dt>Approved source note</dt>
                    <dd>{preview.import.receipt.reason}</dd>
                    <dt>References</dt>
                    <dd>
                      {preview.import.created} created · {preview.import.reused}{" "}
                      reused
                    </dd>
                    <dt>Original uploads</dt>
                    <dd>
                      Retained in local IRIS with the source hashes above.
                    </dd>
                  </>
                )}
              </dl>
            </details>
          </div>
        </section>
      )}
    </div>
  );
}
