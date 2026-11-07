import { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  ArrowRight,
  Check,
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
  const sourceFields = ["Order feed", "Approved reference export"] as const;
  const finalCount =
    preview?.records.filter(
      (row) =>
        results[row.message.event_id] &&
        results[row.message.event_id].routing !== "PROCESSING",
    ).length ?? 0;
  const held =
    preview?.records.filter((row) => {
      const result = results[row.message.event_id];
      return (
        result &&
        result.routing !== "PROCESSING" &&
        result.routing !== "DELIVERED"
      );
    }).length ?? 0;
  return (
    <>
      <PageHeading
        eyebrow="Workspace / order feeds"
        title="CSV Import"
        description="Bring an order feed and its independently approved reference into the same investigation."
      >
        <Badge>Per-line simulator</Badge>
      </PageHeading>
      <div className="csv-scope">
        <ShieldCheck size={19} aria-hidden="true" />
        <p>
          Preview first. Only an authorized importer can add approved
          references. Native AI investigates each line; deterministic policy
          decides its route. No external ERP delivery.
        </p>
      </div>
      {health.error && <ErrorState error={health.error} />}
      {!health.error && health.data && !supported && (
        <div className="csv-permission">
          <LockKeyhole size={18} aria-hidden="true" />
          <div>
            <strong>CSV backend update required</strong>
            <p>
              CSV Import needs the current source backend. Public IPM 0.2.0 does
              not contain these endpoints. Update the source installation before
              previewing files.
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
              You can preview files. Ask your local administrator to grant
              SSImporter to an authorized account; review permission alone
              cannot add authority.
            </p>
            <Button onClick={openConnect}>Connect importer session</Button>
          </div>
        </div>
      )}
      <ol className="csv-steps" aria-label="CSV import stages">
        {["Choose files", "Preview evidence", "Import and investigate"].map(
          (step, index) => (
            <li
              key={step}
              aria-current={
                busy === "import" || busy === "investigate" || complete
                  ? index === 2
                    ? "step"
                    : undefined
                  : preview
                    ? index === 1
                      ? "step"
                      : undefined
                    : index === 0
                      ? "step"
                      : undefined
              }
            >
              <span>{index + 1}</span>
              {step}
            </li>
          ),
        )}
      </ol>
      <section className="csv-files" aria-label="CSV files">
        {sourceFields.map((label, index) => (
          <div className="csv-file" key={label}>
            <FileSpreadsheet size={24} aria-hidden="true" />
            <label className="field-label" htmlFor={`csv-file-${index}`}>
              {label}
            </label>
            <p>
              {index === 0
                ? "Incoming partner order lines, with explicit quantities and units."
                : "A separate approved order export, including revision, approver and effective dates."}
            </p>
            <input
              id={`csv-file-${index}`}
              type="file"
              accept=".csv,text/csv"
              hidden
              disabled={Boolean(busy)}
              onChange={(event) => {
                void state.choose(index as 0 | 1, event.target.files?.[0]);
                event.target.value = "";
              }}
            />
            <Button
              icon={Upload}
              disabled={Boolean(busy)}
              onClick={() =>
                document.getElementById(`csv-file-${index}`)?.click()
              }
            >
              Choose {index === 0 ? "order feed" : "approved export"}
            </Button>
            <span className="csv-filename">
              {files[index]?.name ?? "No file chosen"}
            </span>
            <small>UTF-8 · up to 128 KiB · up to 20 rows</small>
          </div>
        ))}
      </section>
      <div className="csv-file-actions">
        <Button
          icon={Upload}
          kind="primary"
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
        <Button disabled={Boolean(busy)} onClick={() => state.reset(samples)}>
          Use synthetic sample
        </Button>
        <details className="csv-format">
          <summary>CSV layout and sample downloads</summary>
          <p>
            Header names must match exactly; column order may vary. Keep
            quantities as positive decimal text and timestamps explicit about
            timezone. Only effective_to may be blank. No pack conversion is
            inferred.
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
            Both downloads are synthetic and use matching identities. An
            approver name in a CSV is provenance supplied by you, not an
            authenticated approval.
          </p>
        </details>
      </div>
      {error && (
        <div className="csv-error">
          <InlineError error={error} />
          {error instanceof ApiError && error.status === 422 && (
            <p>
              Check the documented headers, decimal quantities, timezone
              offsets, duplicate identities and reference approval fields.
              Preview the files again after a correction.
            </p>
          )}
          {error instanceof ApiError && error.status === 409 && (
            <p>
              An event identity or reference revision already exists with different
              content. Inspect the original import and approval record. Use a new
              revision only for a genuinely approved change.
            </p>
          )}
          {pending && (
            <p>
              Stopped at event <code>{pending}</code>. No later lines were
              submitted. Preview these same files to recover persisted cases; do
              not generate new event IDs to retry.
            </p>
          )}
        </div>
      )}
      {preview && (
        <section className="csv-preview" aria-label="Validated CSV preview">
          <div className="csv-section-title">
            <div>
              <h2>{complete ? "Native results" : "Validated feed"}</h2>
              <p>
                {preview.records.length} order lines ·{" "}
                {preview.references.length} approved reference revisions
              </p>
            </div>
            <Badge tone={complete ? "mint" : "muted"}>
              {complete ? "Processing complete" : "Server validated"}
            </Badge>
          </div>
          <div className="table-scroll">
            <table className="data-table csv-table">
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
                  return (
                    <tr key={row.message.event_id}>
                      <td>
                        <span className="csv-cell-label">
                          Order / source row
                        </span>
                        <strong>{row.order_id}</strong>
                        <small>
                          Line {row.line_id} · CSV row {row.source_row}
                        </small>
                        <small>{row.message.product_id}</small>
                      </td>
                      <td className="mono">
                        <span className="csv-cell-label">Incoming</span>
                        {row.message.quantity} {row.message.unit}
                      </td>
                      <td>
                        <span className="csv-cell-label">Approved export</span>
                        {refs.length ? (
                          refs.map((ref) => (
                            <div key={ref.id}>
                              <strong className="mono">
                                {ref.quantity} {ref.unit}
                              </strong>
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
                                {result.agent.failure_code ?? "inspect case"}
                              </small>
                            )}
                          </>
                        ) : (
                          <Badge>
                            {pending === row.message.event_id
                              ? "Investigating…"
                              : "Not submitted"}
                          </Badge>
                        )}
                      </td>
                      <td>
                        <span className="csv-cell-label">Evidence</span>
                        {result ? (
                          <>
                            <a
                              className="text-link"
                              href={`#investigations/${encodeURIComponent(result.id)}`}
                            >
                              Open case <ArrowRight size={14} />
                            </a>
                            <small className="mono">
                              Trace {result.trace_id || "pending"}
                            </small>
                          </>
                        ) : (
                          <span>Available after submission</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
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
                  <dd>Retained in local IRIS with the source hashes above.</dd>
                  </>
                )}
              </dl>
            </details>
          </div>
          {!preview.import && (
            <div className="csv-authority">
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
                placeholder="Where was this export approved, and who owns that reference?"
              />
              <label className="csv-confirm">
                <input
                  type="checkbox"
                  checked={state.confirmed}
                  onChange={(event) => state.setConfirmed(event.target.checked)}
                  disabled={Boolean(busy) || !canImport}
                />
                <span>
                  I am authorized to import this independently approved
                  reference export.
                </span>
              </label>
            </div>
          )}
          <div className="csv-run-actions">
            <Button
              icon={complete ? Check : ShieldCheck}
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
                  : complete
                    ? "Run complete"
                    : "Import references and investigate"}
            </Button>
            {Object.keys(results).length > 0 && (
              <Button
                icon={Download}
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
              ? `Local inference is running. ${finalCount} of ${preview.records.length} lines resolved. Keep this tab open; switching workspace views preserves progress.`
              : complete
                ? `${finalCount} lines resolved; ${held} held or rejected. Results cover submitted lines only. Order completeness and atomic whole-order delivery are not verified.`
            : "Preview makes no writes. Import stores both CSV originals and approved references in local IRIS; investigation can create per-line simulator receipts."}
          </p>
        </section>
      )}
    </>
  );
}
