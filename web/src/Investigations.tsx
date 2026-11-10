import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ArrowRight,
  Check,
  ChevronDown,
  CircleDashed,
  History,
  Inbox,
  KeyRound,
  Search,
  ShieldCheck,
  ShieldX,
  Sparkles,
  X,
} from "lucide-react";
import { CaseSchema, CasesSchema } from "./schema";
import type { Investigation } from "./schema";
import { request, useApi } from "./api";
import { SessionWelcome } from "./SessionWelcome";
import {
  Badge,
  Button,
  CopyButton,
  dateTime,
  DecisionBadge,
  display,
  EmptyState,
  ErrorState,
  humanize,
  InlineError,
  JsonBlock,
  Loading,
  Metadata,
  MetaRow,
  Modal,
  NativePath,
  Notice,
  PageHeading,
  RouteMark,
  shortTime,
  toneFor,
  TraceLink,
  useActions,
} from "./ui";

// An absent or pending permission observation grants no reviewer controls.
// The server still authorizes every mutation independently.
export const ReviewPermissionContext = createContext(false);

type ReviewAction = "APPROVE" | "REJECT";
type ReviewRequest = {
  action: ReviewAction;
  reason: string;
  expected_version: number;
  idempotency_key: string;
};

function recordedAction(value: unknown): ReviewAction | null {
  if (value === "approve" || value === "APPROVE") return "APPROVE";
  if (value === "reject" || value === "REJECT") return "REJECT";
  return null;
}

function recordedRequest(item: Investigation): ReviewRequest | null {
  const action = recordedAction(item.review?.action);
  if (
    !item.workflow ||
    !item.review ||
    !action ||
    typeof item.review.reason !== "string" ||
    typeof item.review.expected_version !== "number" ||
    typeof item.review.idempotency_key !== "string"
  )
    return null;
  return {
    action,
    reason: item.review.reason,
    expected_version: item.review.expected_version,
    idempotency_key: item.review.idempotency_key,
  };
}

function checksFor(item: Investigation) {
  const checks = item.policy?.checks;
  if (!checks) return [];
  const rows = Array.isArray(checks)
    ? checks.map((value, index) => [String(index + 1), value] as const)
    : Object.entries(checks);
  return rows.map(([key, raw]) => {
    const value = raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {};
    return {
      label: typeof value.code === "string" ? humanize(value.code) : humanize(key),
      passed:
        typeof value.passed === "boolean"
          ? value.passed
          : typeof raw === "boolean"
            ? raw
            : null,
      reason: typeof value.reason === "string" ? value.reason : "",
    };
  });
}

function Evidence({ item }: { item: Investigation }) {
  const findings = item.assessment?.findings ?? [];
  return (
    <div className="stack-lg">
      <section aria-labelledby={`findings-${item.id}`}>
        <div className="section-head">
          <div>
            <h3 id={`findings-${item.id}`}>Semantic comparison</h3>
            <p>Original partner values against independently retrieved evidence.</p>
          </div>
          <Badge>
            {findings.length} finding{findings.length === 1 ? "" : "s"}
          </Badge>
        </div>
        {findings.length ? (
          <ol className="ledger">
            {findings.map((finding, index) => (
              <li key={`${finding.code}-${index}`} className={`ledger-row sev-${toneFor(finding.severity)}`}>
                <div className="ledger-field">
                  <code>{finding.field}</code>
                  <Badge tone={toneFor(finding.severity)}>{humanize(finding.severity)}</Badge>
                  <small>{humanize(finding.code)}</small>
                </div>
                <div className="ledger-compare">
                  <div>
                    <span className="kicker">Partner value</span>
                    <code className="ledger-value">{display(finding.observed)}</code>
                  </div>
                  <span className="ledger-mark" aria-hidden="true">
                    vs
                  </span>
                  <div>
                    <span className="kicker">Reference / requirement</span>
                    <code className="ledger-value">{display(finding.expected)}</code>
                  </div>
                </div>
                <p className="ledger-explain">{finding.explanation}</p>
                {finding.evidence_ids.length > 0 && (
                  <div className="citations" aria-label="Cited evidence">
                    {finding.evidence_ids.map((id) => (
                      <code key={id}>{id}</code>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ol>
        ) : (
          <div className="quiet-box">
            <Check size={18} aria-hidden="true" />
            <div>
              <strong>
                {item.assessment ? "No semantic differences recorded" : "Assessment is pending"}
              </strong>
              <p>
                {item.assessment
                  ? "Inspect the reference snapshot and final policy before interpreting this result."
                  : "A final decision is not available yet."}
              </p>
            </div>
          </div>
        )}
      </section>

      <section aria-labelledby={`refs-${item.id}`}>
        <div className="section-head">
          <div>
            <h3 id={`refs-${item.id}`}>Reference snapshot</h3>
            <p>Evidence preserved with this investigation.</p>
          </div>
          <Badge>
            {item.references.length} record{item.references.length === 1 ? "" : "s"}
          </Badge>
        </div>
        {item.references.length ? (
          <div className="disclosures">
            {item.references.map((reference, index) => (
              <details className="disclosure" key={String(reference.id ?? index)}>
                <summary>
                  <span className="mono">{display(reference.id ?? `Reference ${index + 1}`)}</span>
                  {typeof reference.authority === "string" && (
                    <Badge tone={reference.authority === "approved" ? "allow" : "review"}>
                      {reference.authority}
                    </Badge>
                  )}
                </summary>
                <JsonBlock value={reference} title={`Reference ${index + 1}`} />
              </details>
            ))}
          </div>
        ) : (
          <Notice tone="review">
            No independent reference records were returned. Missing evidence cannot authorize an
            automatic release.
          </Notice>
        )}
      </section>

      {item.runbook_context && (
        <section aria-label="Supporting procedures">
          <div className="section-head">
            <div>
              <h3>Supporting procedures</h3>
              <p>Retrieved by IRIS vector search. Text similarity grants no release permission.</p>
            </div>
          </div>
          {item.runbook_context.status === "unavailable" ? (
            <p className="quiet small">
              Procedural guidance is unavailable. Approved evidence and policy still determine the
              route.
            </p>
          ) : item.runbook_context.matches.length ? (
            <div className="disclosures">
              {item.runbook_context.matches.map((procedure) => (
                <details className="disclosure" key={procedure.id}>
                  <summary>
                    <span>{procedure.title}</span>
                    <Badge>Similarity {procedure.similarity.toFixed(2)}</Badge>
                  </summary>
                  <div className="disclosure-body">
                    <p>{procedure.guidance}</p>
                    <p className="quiet small">
                      Supporting context · {procedure.id} · No contract authority
                    </p>
                  </div>
                </details>
              ))}
            </div>
          ) : (
            <p className="quiet small">No procedure met the retrieval threshold.</p>
          )}
        </section>
      )}

      {item.precedent_context && (
        <section aria-label="Similar precedents">
          <div className="section-head">
            <div>
              <h3>Similar precedents</h3>
              <p>Earlier resolved cases and approved amendments, ranked by cosine similarity.</p>
            </div>
            <Badge>No release authority</Badge>
          </div>
          <p className="quiet small">
            Precedents add context. Current approved references and deterministic policy still
            decide this transaction.
          </p>
          {item.precedent_context.status === "unavailable" ? (
            <Notice tone="review">
              Precedent retrieval is unavailable. Inspect the preserved reference snapshot and
              policy checks.
            </Notice>
          ) : item.precedent_context.matches.length ? (
            <ol className="precedents">
              {item.precedent_context.matches.map((precedent) => (
                <li data-precedent-id={precedent.precedent_id} key={precedent.precedent_id}>
                  <div className="precedent-top">
                    <span className="kicker">
                      {precedent.source_type === "resolved_case"
                        ? "Resolved case"
                        : "Approved amendment"}
                    </span>
                    <span className="mono small">
                      Cosine similarity {precedent.similarity.toFixed(3)}
                    </span>
                  </div>
                  <h4>
                    {humanize(precedent.kind)} · {humanize(precedent.outcome)}
                  </h4>
                  <p>{precedent.summary}</p>
                  <Metadata>
                    <MetaRow label="Source" mono>
                      {precedent.source_type === "resolved_case" ? (
                        <a
                          className="link"
                          href={`#investigations/${encodeURIComponent(precedent.source_id)}`}
                        >
                          {precedent.source_id}
                        </a>
                      ) : (
                        precedent.source_id
                      )}
                    </MetaRow>
                    <MetaRow label="Precedent" mono>
                      {precedent.precedent_id}
                    </MetaRow>
                    <MetaRow label="Contract" mono>
                      {precedent.contract_id}
                    </MetaRow>
                  </Metadata>
                  {precedent.synthetic === true ? (
                    <Badge>Synthetic source</Badge>
                  ) : precedent.synthetic === null ? (
                    <Badge>Source label not recorded</Badge>
                  ) : null}
                </li>
              ))}
            </ol>
          ) : (
            <p className="quiet small">No similar records were returned for this case.</p>
          )}
        </section>
      )}
    </div>
  );
}

export function Timeline({ item }: { item: Investigation }) {
  return item.events.length ? (
    <ol className="timeline">
      {item.events.map((event, index) => (
        <li key={event.id}>
          <span className="timeline-index mono">{String(index + 1).padStart(2, "0")}</span>
          <div>
            <div className="timeline-head">
              <strong>{humanize(event.kind)}</strong>
              <time className="mono" dateTime={event.at}>
                {shortTime(event.at)}
              </time>
            </div>
            <details className="disclosure plain">
              <summary>Inspect recorded event</summary>
              <JsonBlock value={event.detail} title={`${humanize(event.kind)} details`} />
            </details>
          </div>
        </li>
      ))}
    </ol>
  ) : (
    <EmptyState icon={History} title="No audit events returned">
      The native API has not returned timeline events for this case.
    </EmptyState>
  );
}

function AgentView({ item }: { item: Investigation }) {
  const reads = item.agent?.tool_reads;
  return (
    <div className="stack-lg">
      <Notice tone="agent" icon={Sparkles}>
        The agent proposes a decision. Only deterministic server policy can authorize a route.
      </Notice>
      {item.agent ? (
        <>
          <Metadata>
            <MetaRow label="Reported mode" mono>
              {display(item.agent.mode)}
            </MetaRow>
            <MetaRow label="Model" mono>
              {display(item.agent.model)}
            </MetaRow>
            <MetaRow label="Elapsed" mono>
              {typeof item.agent.elapsed_ms === "number"
                ? `${item.agent.elapsed_ms} ms`
                : "Not recorded"}
            </MetaRow>
          </Metadata>
          {reads && (
            <section aria-label="Evidence tool reads">
              <div className="section-head">
                <div>
                  <h3>Evidence tool reads</h3>
                  <p>Counts come from the recorded callbacks for this investigation.</p>
                </div>
              </div>
              <Metadata>
                {(
                  [
                    ["message", "Current message"],
                    ["contracts", "Approved contracts"],
                    ["related", "Related records"],
                    ["precedents", "Similar precedents"],
                  ] as const
                ).map(([key, label]) => (
                  <MetaRow label={label} key={key} mono>
                    <span data-tool-read={key}>
                      {typeof reads[key] === "number" ? reads[key] : "Not recorded"}
                    </span>
                  </MetaRow>
                ))}
              </Metadata>
            </section>
          )}
          <JsonBlock value={item.agent} title="Native agent activity" />
        </>
      ) : (
        <EmptyState icon={Sparkles} title="No agent execution recorded">
          A configured provider alone does not prove that a native agent ran.
        </EmptyState>
      )}
      {item.recommendation ? (
        <JsonBlock value={item.recommendation} title="Persisted recommendation" />
      ) : (
        <Notice tone="review">
          No structured recommendation is available. The route must remain subject to fail-closed
          policy.
        </Notice>
      )}
    </div>
  );
}

function ReviewDialog({
  item,
  action,
  onClose,
  onComplete,
}: {
  item: Investigation;
  action: ReviewAction;
  onClose: () => void;
  onComplete: (result: Investigation) => void;
}) {
  const recorded = recordedRequest(item);
  const [reason, setReason] = useState(recorded?.reason ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [submitted, setSubmitted] = useState<ReviewRequest | null>(recorded);
  const length = reason.trim().length;
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (busy || length < 8) return;
    const body = submitted ?? {
      action,
      reason: reason.trim(),
      expected_version: item.version,
      idempotency_key: crypto.randomUUID(),
    };
    setSubmitted(body);
    setBusy(true);
    setError(null);
    try {
      // Refresh persisted state before retrying an uncertain outcome. Reuse
      // the complete original request, including its original case version.
      if (submitted) await request(`/api/cases/${encodeURIComponent(item.id)}`, CaseSchema);
      const result = await request(
        `/api/cases/${encodeURIComponent(item.id)}/review`,
        CaseSchema,
        { body },
      );
      onComplete(result);
    } catch (failure) {
      setError(failure);
    } finally {
      setBusy(false);
    }
  };
  const approve = (submitted?.action ?? action) === "APPROVE";
  return (
    <Modal
      title={approve ? "Request a controlled release" : "Reject this transaction"}
      description={
        approve
          ? "IRIS will verify reviewer permission, the current case version and every deterministic release gate before delivering."
          : "IRIS will record your reason and reject the held transaction. This action requires reviewer permission."
      }
      onClose={onClose}
    >
      <div className="review-context">
        <span className="kicker">Case</span>
        <code>{item.id}</code>
        <Badge>
          {recorded ? "Original version" : "Version"} {submitted?.expected_version ?? item.version}
        </Badge>
      </div>
      <form onSubmit={submit} className="form">
        <label className="label" htmlFor="review-reason">
          Reason <span>Required · 8 characters minimum</span>
        </label>
        <textarea
          id="review-reason"
          data-autofocus
          rows={4}
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          placeholder="Describe the evidence supporting this action…"
          maxLength={2000}
          disabled={busy || submitted !== null}
          required
          minLength={8}
          aria-describedby="review-reason-count"
        />
        <span id="review-reason-count" className={`counter ${length >= 8 ? "ok" : ""}`}>
          {length < 8 ? `${8 - length} more character${8 - length === 1 ? "" : "s"} required` : "Reason recorded with the review"}
        </span>
        {error !== null && <InlineError error={error} />}
        <p className="hint">
          {submitted
            ? "Retry resumes this exact recorded request. Its reason and original version stay fixed."
            : "IRIS checks the case version and preserves one review receipt. An uncertain result can be resumed safely."}
        </p>
        <div className="dialog-actions">
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            kind={approve ? "primary" : "danger"}
            icon={approve ? ShieldCheck : ShieldX}
            disabled={busy || length < 8}
          >
            {busy
              ? "Recording action…"
              : submitted
                ? "Resume recorded review"
                : approve
                  ? "Request release"
                  : "Reject transaction"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

const TABS = [
  { id: "evidence", label: "Evidence" },
  { id: "timeline", label: "Timeline" },
  { id: "payload", label: "Payload" },
  { id: "agent", label: "Agent" },
] as const;
type Tab = (typeof TABS)[number]["id"];

function outcomeText(routing: Investigation["routing"]) {
  if (routing === "DELIVERED")
    return "The native API reports a delivery to the destination simulator.";
  if (routing === "PROCESSING")
    return "No final route has been reported. Refresh to inspect persisted progress.";
  if (routing === "REJECTED")
    return "The transaction was rejected. Inspect the recorded reviewer action.";
  return "Held from the downstream destination.";
}

export function CaseDetail({ item }: { item: Investigation }) {
  const [tab, setTab] = useState<Tab>("evidence");
  const [review, setReview] = useState<ReviewAction | null>(null);
  const canReview = useContext(ReviewPermissionContext);
  const { refresh, notify } = useActions();
  const closeReview = useCallback(() => setReview(null), []);
  const checks = checksFor(item);
  const held = item.routing === "QUARANTINED" || item.routing === "REVIEW";
  const nativeTask = Boolean(item.workflow?.task_id);
  const resumable = item.workflow && item.review && recordedAction(item.review.action);
  const decisionTone = toneFor(item.policy?.decision ?? "");
  return (
    <div className="case">
      <article className="case-main">
        <header className="case-head">
          <div className="case-title">
            <h2 tabIndex={-1} data-case-heading>
              {item.assessment ? humanize(item.assessment.classification) : "Investigation in progress"}
            </h2>
            <RouteMark routing={item.routing} />
          </div>
          <p className="case-source">
            <span>{item.source}</span>
            <span aria-hidden="true">/</span>
            <code>{item.event_id}</code>
          </p>
        </header>

        <div className={`verdict verdict-${decisionTone}`}>
          <div>
            <span className="kicker">Policy-constrained outcome</span>
            <strong>
              {item.policy ? humanize(item.policy.decision) : "Awaiting policy evaluation"}
            </strong>
            <p>{outcomeText(item.routing)}</p>
          </div>
          {item.policy && <code className="verdict-version">{item.policy.policy_version}</code>}
        </div>

        <div className="tabs" role="tablist" aria-label="Investigation detail">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              id={`tab-${item.id}-${id}`}
              type="button"
              role="tab"
              aria-selected={tab === id}
              aria-controls={`panel-${item.id}`}
              tabIndex={tab === id ? 0 : -1}
              onClick={() => setTab(id)}
              onKeyDown={(event) => {
                let index = TABS.findIndex((entry) => entry.id === tab);
                if (event.key === "ArrowRight") index = (index + 1) % TABS.length;
                else if (event.key === "ArrowLeft") index = (index + TABS.length - 1) % TABS.length;
                else if (event.key === "Home") index = 0;
                else if (event.key === "End") index = TABS.length - 1;
                else return;
                event.preventDefault();
                const next = TABS[index]!.id;
                setTab(next);
                document.getElementById(`tab-${item.id}-${next}`)?.focus();
              }}
            >
              {label}
              {id === "timeline" && <span className="tab-count mono">{item.events.length}</span>}
            </button>
          ))}
        </div>
        <section
          id={`panel-${item.id}`}
          className="tab-panel"
          role="tabpanel"
          aria-labelledby={`tab-${item.id}-${tab}`}
          tabIndex={0}
        >
          {tab === "evidence" && <Evidence item={item} />}
          {tab === "timeline" && <Timeline item={item} />}
          {tab === "payload" && (
            <div className="stack-lg">
              <JsonBlock value={item.message} title="Original partner message" />
              <Metadata>
                <MetaRow label="Correlation ID" mono>
                  {display(item.message.correlation_id)}
                </MetaRow>
                <MetaRow label="Received">{dateTime(item.received_at)}</MetaRow>
              </Metadata>
            </div>
          )}
          {tab === "agent" && <AgentView item={item} />}
        </section>
      </article>

      <aside className="case-side" aria-label="Provenance and actions">
        {held && (
          <section className="side-block side-actions" aria-label="Reviewer actions">
            <span className="kicker">Reviewer actions</span>
            {!nativeTask ? (
              <p className="small quiet">
                {item.assessment?.critical
                  ? "Critical contradictions require a corrected event or reference and a new investigation."
                  : item.workflow
                    ? "The native review task is being created. Refresh before acting on this hold."
                    : "This historical hold has no native review task. Start a new investigation with the corrected event and current approved references."}
              </p>
            ) : resumable ? (
              <>
                <p className="small quiet">
                  A review is recorded. Resume its native task completion and route using the
                  original request.
                </p>
                <Button
                  disabled={!canReview}
                  onClick={() => setReview(recordedAction(item.review?.action))}
                >
                  Resume recorded review
                </Button>
              </>
            ) : (
              <>
                <div className="action-pair">
                  <Button
                    kind="primary"
                    icon={ShieldCheck}
                    onClick={() => setReview("APPROVE")}
                    disabled={!canReview || item.assessment?.critical !== false}
                    title={
                      !canReview
                        ? "This session does not have IRIS reviewer permission."
                        : item.assessment?.critical !== false
                          ? "Critical or unassessed cases require corrected evidence and a new investigation."
                          : "All release gates will be rechecked by IRIS."
                    }
                  >
                    Approve release
                  </Button>
                  <Button
                    kind="danger"
                    icon={ShieldX}
                    disabled={!canReview}
                    onClick={() => setReview("REJECT")}
                  >
                    Reject transaction
                  </Button>
                </div>
                <p className="small quiet">
                  {!canReview
                    ? "Review actions require IRIS reviewer permission to release or reject transactions."
                    : item.assessment?.critical
                      ? "Critical contradictions require a corrected event or reference and a new investigation."
                      : "Reviewer permission, a reason and a current case version are required."}
                </p>
              </>
            )}
          </section>
        )}

        <section className="side-block" aria-label="Policy validation">
          <span className="kicker">Policy validation</span>
          {item.policy ? (
            <>
              <DecisionBadge value={item.policy.decision} />
              {item.policy.reasons.length > 0 && (
                <details className="disclosure plain">
                  <summary>Decision reasons</summary>
                  <ul className="reasons">
                    {item.policy.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </details>
              )}
              <ul className="checks">
                {checks.map((check, index) => (
                  <li
                    key={index}
                    className={check.passed === true ? "pass" : check.passed === false ? "fail" : ""}
                  >
                    {check.passed === true ? (
                      <Check size={14} aria-label="Passed" />
                    ) : check.passed === false ? (
                      <X size={14} aria-label="Failed" />
                    ) : (
                      <CircleDashed size={14} aria-label="Not reported" />
                    )}
                    {check.reason ? (
                      <details>
                        <summary>{check.label}</summary>
                        <p>{check.reason}</p>
                      </details>
                    ) : (
                      <span>{check.label}</span>
                    )}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="quiet small">Policy has not produced a persisted result.</p>
          )}
        </section>

        <section className="side-block" aria-label="Provenance">
          <span className="kicker">Provenance</span>
          <Metadata>
            <MetaRow label="Case ID" mono>
              <span className="copy-row">
                <span className="break">{item.id}</span>
                <CopyButton value={item.id} label="Copy case ID" />
              </span>
            </MetaRow>
            <MetaRow label="Source" mono>
              {item.source}
            </MetaRow>
            <MetaRow label="Received">{dateTime(item.received_at)}</MetaRow>
            <MetaRow label="Version" mono>
              {item.version}
            </MetaRow>
          </Metadata>
          <TraceLink item={item} />
        </section>

        {item.workflow && (
          <section className="side-block" aria-label="Native review task">
            <span className="kicker">Native review task</span>
            <Metadata>
              <MetaRow label="Status">{humanize(item.workflow.status)}</MetaRow>
              <MetaRow label="Task" mono>
                {display(item.workflow.task_id)}
              </MetaRow>
              <MetaRow label="Worklist">{item.workflow.role}</MetaRow>
            </Metadata>
          </section>
        )}
        {item.review && (
          <section className="side-block" aria-label="Recorded review">
            <span className="kicker">Recorded review</span>
            <JsonBlock value={item.review} title="Reviewer audit" />
          </section>
        )}
      </aside>

      {review && canReview && nativeTask && (
        <ReviewDialog
          item={item}
          action={review}
          onClose={closeReview}
          onComplete={(result) => {
            setReview(null);
            notify(`Review recorded. Current route: ${humanize(result.routing)}.`);
            refresh();
          }}
        />
      )}
    </div>
  );
}

/** Arrow keys move between sibling links/buttons in a list. */
export function listKeys(event: React.KeyboardEvent<HTMLElement>) {
  if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
  const items = [
    ...event.currentTarget.querySelectorAll<HTMLElement>("[data-list-item]"),
  ];
  const index = items.indexOf(document.activeElement as HTMLElement);
  if (index < 0) return;
  event.preventDefault();
  const next =
    event.key === "Home"
      ? 0
      : event.key === "End"
        ? items.length - 1
        : event.key === "ArrowDown"
          ? Math.min(items.length - 1, index + 1)
          : Math.max(0, index - 1);
  items[next]?.focus();
}

export default function Investigations({
  refresh,
  caseId,
}: {
  refresh: number;
  caseId?: string;
}) {
  const cases = useApi("/api/cases?limit=50&offset=0", CasesSchema, refresh);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [polls, setPolls] = useState(0);
  const [queueOpen, setQueueOpen] = useState(false);
  const detailRegion = useRef<HTMLDivElement>(null);
  const openedCase = useRef<string | null>(null);
  const { openConnect } = useActions();
  const needsSession =
    !cases.loading && cases.error?.status === 401 && !cases.data?.items.length;
  const activeId = caseId ?? cases.data?.items[0]?.id;
  const detail = useApi(
    activeId ? `/api/cases/${encodeURIComponent(activeId)}` : null,
    CaseSchema,
    refresh * 1000 + polls,
  );
  useEffect(() => setPolls(0), [activeId]);
  useEffect(() => {
    // Move focus to a newly opened case once its record arrives; polling and
    // refreshes of the same case keep the operator's position.
    if (
      !caseId ||
      !detail.data ||
      detail.data.id !== activeId ||
      openedCase.current === detail.data.id
    )
      return;
    openedCase.current = detail.data.id;
    window.scrollTo({ top: 0, behavior: "instant" });
    detailRegion.current
      ?.querySelector<HTMLElement>("[data-case-heading]")
      ?.focus({ preventScroll: true });
  }, [activeId, caseId, detail.data]);
  useEffect(() => {
    if (detail.data?.routing === "PROCESSING" && polls < 30) {
      const timeout = window.setTimeout(() => setPolls((count) => count + 1), 2000);
      return () => window.clearTimeout(timeout);
    }
  }, [detail.data, polls]);
  const items = useMemo(
    () =>
      cases.data?.items.filter((item) => {
        const matches = `${item.id} ${item.event_id} ${item.source}`
          .toLowerCase()
          .includes(query.toLowerCase().trim());
        return (
          matches &&
          (filter === "all" || item.policy?.decision === filter || item.routing === filter)
        );
      }) ?? [],
    [cases.data, query, filter],
  );
  return (
    <>
      <PageHeading
        title="Investigations"
        description="Follow each message from original payload to approved evidence and outcome."
      >
        <a className="btn btn-secondary" href="#scenarios">
          Open Scenario Lab <ArrowRight size={15} aria-hidden="true" />
        </a>
      </PageHeading>
      <div className="split">
        <aside className={`queue ${queueOpen ? "open" : ""}`} aria-label="Investigation queue">
          <div className="queue-head">
            <h2>Queue</h2>
            <span className="count mono">{cases.data ? cases.data.total : "..."}</span>
            <button
              type="button"
              className="icon-btn queue-toggle"
              aria-label={queueOpen ? "Collapse investigation queue" : "Expand investigation queue"}
              aria-expanded={queueOpen}
              aria-controls="investigation-queue-content"
              onClick={() => setQueueOpen((open) => !open)}
            >
              <ChevronDown size={17} aria-hidden="true" />
            </button>
          </div>
          <div className="queue-body" id="investigation-queue-content">
            <div className="queue-filters">
              <label className="search">
                <Search size={14} aria-hidden="true" />
                <span className="sr-only">Search investigations</span>
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Event, source or case ID"
                  type="search"
                />
              </label>
              <select
                aria-label="Filter investigations by decision"
                value={filter}
                onChange={(event) => setFilter(event.target.value)}
              >
                <option value="all">All decisions</option>
                <option value="QUARANTINE">Quarantine</option>
                <option value="REQUEST_REVIEW">Request review</option>
                <option value="ALLOW">Allow</option>
                <option value="PROCESSING">Processing</option>
              </select>
            </div>
            {cases.loading ? (
              <Loading>Reading case records…</Loading>
            ) : needsSession ? (
              <div className="queue-state">
                <KeyRound size={20} strokeWidth={1.5} aria-hidden="true" />
                <strong>Connection required</strong>
                <p>Connect your IRIS session to load investigations.</p>
              </div>
            ) : cases.error ? (
              <div className="queue-state">
                <Inbox size={20} strokeWidth={1.5} aria-hidden="true" />
                <strong>Queue unavailable</strong>
                <p>No native records have been loaded.</p>
                <code className="small">{cases.error.code}</code>
              </div>
            ) : !items.length ? (
              <div className="queue-state">
                <Inbox size={20} strokeWidth={1.5} aria-hidden="true" />
                <strong>{cases.data?.items.length ? "No matching cases" : "Your queue is clear"}</strong>
                <p>
                  {cases.data?.items.length
                    ? "Try another source or decision filter."
                    : "Run a synthetic scenario to create the first native investigation."}
                </p>
              </div>
            ) : (
              <ol className="queue-list" onKeyDown={listKeys}>
                {items.map((item) => {
                  const selected = activeId === item.id;
                  return (
                    <li key={item.id}>
                      <a
                        data-list-item
                        className={`queue-item tone-${toneFor(item.policy?.decision ?? item.routing)} ${selected ? "selected" : ""}`}
                        href={`#investigations/${encodeURIComponent(item.id)}`}
                        aria-current={selected ? "true" : undefined}
                        onClick={() => {
                          setQueueOpen(false);
                          if (detail.data?.id === item.id)
                            detailRegion.current
                              ?.querySelector<HTMLElement>("[data-case-heading]")
                              ?.focus({ preventScroll: true });
                        }}
                      >
                        <span className="queue-item-top">
                          <strong>
                            {item.assessment
                              ? humanize(item.assessment.classification)
                              : "Processing event"}
                          </strong>
                          <time dateTime={item.received_at} className="mono">
                            {shortTime(item.received_at)}
                          </time>
                        </span>
                        <span className="queue-item-meta mono">{item.event_id}</span>
                        <span className="queue-item-bottom">
                          <span className="queue-item-source">{item.source}</span>
                          {item.policy ? (
                            <DecisionBadge value={item.policy.decision} />
                          ) : (
                            <Badge>Processing</Badge>
                          )}
                        </span>
                      </a>
                    </li>
                  );
                })}
              </ol>
            )}
            <p className="queue-foot">
              {cases.data
                ? `${items.length} shown from the first ${cases.data.limit} records`
                : "Native records only"}
            </p>
          </div>
        </aside>
        <div className="split-main" ref={detailRegion}>
          {detail.data ? (
            <>
              <CaseDetail item={detail.data} key={detail.data.id} />
              {polls >= 30 && detail.data.routing === "PROCESSING" && (
                <Notice tone="review">
                  Automatic refresh paused after one minute. Refresh to inspect the current
                  persisted state.
                </Notice>
              )}
            </>
          ) : detail.loading ? (
            <Loading>Reading investigation…</Loading>
          ) : needsSession ? (
            <SessionWelcome onConnect={openConnect} />
          ) : detail.error ? (
            <ErrorState error={detail.error} />
          ) : (
            <div className="intro-panel">
              <h2>Evidence workbench</h2>
              <p>
                Compare the message that arrived with the business meaning that was approved.
                Every finding, recommendation and route stays inspectable.
              </p>
              {cases.error && <ErrorState error={cases.error} compact />}
              <NativePath />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
