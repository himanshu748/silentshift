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
  ArrowDownToLine,
  ArrowRight,
  Check,
  ChevronDown,
  ChevronRight,
  FileJson2,
  Fingerprint,
  GitCompareArrows,
  History,
  Inbox,
  Search,
  ShieldCheck,
  ShieldX,
  Sparkles,
  X,
} from "lucide-react";
import { CaseSchema, CasesSchema } from "./schema";
import type { Investigation } from "./schema";
import { request, useApi } from "./api";
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
  Metadata,
  MetaRow,
  Modal,
  NativePath,
  Notice,
  PageHeading,
  shortTime,
  toneFor,
  TraceLink,
  useActions,
} from "./ui";

// An absent or pending permission observation grants no reviewer controls.
// The server still authorizes every mutation independently.
export const ReviewPermissionContext = createContext(false);

function recordedAction(value: unknown): "APPROVE" | "REJECT" | null {
  if (value === "approve" || value === "APPROVE") return "APPROVE";
  if (value === "reject" || value === "REJECT") return "REJECT";
  return null;
}

function checksFor(
  item: Investigation,
): { label: string; passed: boolean | null; reason: string }[] {
  const checks = item.policy?.checks;
  if (!checks) return [];
  const rows = Array.isArray(checks)
    ? checks.map((value, index) => [String(index + 1), value] as const)
    : Object.entries(checks);
  return rows.map(([key, raw]) => {
    const value =
      raw && typeof raw === "object" ? (raw as Record<string, unknown>) : {};
    return {
      label:
        typeof value.code === "string" ? humanize(value.code) : humanize(key),
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
    <>
      <div className="section-header">
        <div>
          <h3>Semantic comparison</h3>
          <p>
            Original partner values against independently retrieved evidence.
          </p>
        </div>
        <Badge>
          {findings.length} finding{findings.length === 1 ? "" : "s"}
        </Badge>
      </div>
      {findings.length ? (
        <div
          className="table-scroll"
          role="region"
          aria-label="Semantic comparison"
          tabIndex={0}
        >
          <table className="evidence-table">
            <thead>
              <tr>
                <th>Field / finding</th>
                <th>Partner value</th>
                <th>Reference / requirement</th>
              </tr>
            </thead>
            <tbody>
              {findings.map((finding, index) => (
                <tr key={`${finding.code}-${index}`}>
                  <td>
                    <code>{finding.field}</code>
                    <small>{humanize(finding.code)}</small>
                    <p>{finding.explanation}</p>
                    <div className="evidence-citations">
                      {finding.evidence_ids.map((id) => (
                        <code key={id}>{id}</code>
                      ))}
                    </div>
                  </td>
                  <td>
                    <span className="mobile-value-label" aria-hidden="true">Partner value</span>
                    <code className={toneFor(finding.severity)}>
                      {display(finding.observed)}
                    </code>
                  </td>
                  <td>
                    <span className="mobile-value-label" aria-hidden="true">Reference / requirement</span>
                    <code>{display(finding.expected)}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="quiet-panel">
          <Check size={19} />
          <div>
            <strong>
              {item.assessment
                ? "No semantic differences recorded"
                : "Assessment is pending"}
            </strong>
            <p>
              {item.assessment
                ? "Inspect the reference snapshot and final policy before interpreting this result."
                : "A final decision is not available yet."}
            </p>
          </div>
        </div>
      )}
      <div className="section-header reference-heading">
        <div>
          <h3>Reference snapshot</h3>
          <p>Evidence preserved with this investigation.</p>
        </div>
        <Badge>
          {item.references.length} record
          {item.references.length === 1 ? "" : "s"}
        </Badge>
      </div>
      {item.references.length ? (
        <div className="reference-list" role="group" aria-label="Reference snapshot">
          {item.references.map((reference, index) => (
            <details
              className="reference-record"
              key={String(reference.id ?? index)}
            >
              <summary>
                <ChevronRight size={15} />
                <span className="mono">
                  {display(reference.id ?? `Reference ${index + 1}`)}
                </span>
                {typeof reference.authority === "string" && (
                  <Badge
                    tone={reference.authority === "approved" ? "mint" : "amber"}
                  >
                    {reference.authority}
                  </Badge>
                )}
              </summary>
              <JsonBlock
                value={reference}
                title={`Reference ${index + 1}`}
                compact
              />
            </details>
          ))}
        </div>
      ) : (
        <Notice tone="amber">
          No independent reference records were returned. Missing evidence
          cannot authorize an automatic release.
        </Notice>
      )}
      {item.runbook_context && (
        <section className="reference-heading" aria-label="Supporting procedures">
          <div className="section-header">
            <div>
              <h3>Supporting procedures</h3>
              <p>Retrieved by IRIS vector search. Text similarity grants no release permission.</p>
            </div>
          </div>
          {item.runbook_context.status === "unavailable" ? (
            <p className="small subtle">Procedural guidance is unavailable. Approved evidence and policy still determine the route.</p>
          ) : item.runbook_context.matches.length ? (
            <div className="reference-list">
              {item.runbook_context.matches.map((procedure) => (
                <details className="reference-record" key={procedure.id}>
                  <summary><ChevronRight size={15} /><span>{procedure.title}</span><Badge>Similarity {procedure.similarity.toFixed(2)}</Badge></summary>
                  <p>{procedure.guidance}</p>
                  <p className="small subtle">Supporting context · {procedure.id} · No contract authority</p>
                </details>
              ))}
            </div>
          ) : <p className="small subtle">No procedure met the retrieval threshold.</p>}
        </section>
      )}
      {item.precedent_context && (
        <section className="reference-heading precedent-evidence" aria-label="Similar precedents">
          <div className="section-header">
            <div>
              <h3>Similar precedents</h3>
              <p>Earlier resolved cases and approved amendments, ranked by cosine similarity.</p>
            </div>
            <Badge>No release authority</Badge>
          </div>
          <p className="small subtle">Precedents add context. Current approved references and deterministic policy still decide this transaction.</p>
          {item.precedent_context.status === "unavailable" ? (
            <Notice tone="amber">Precedent retrieval is unavailable. Inspect the preserved reference snapshot and policy checks.</Notice>
          ) : item.precedent_context.matches.length ? (
            <ol className="precedent-list">
              {item.precedent_context.matches.map((precedent) => (
                <li className="precedent-match" data-precedent-id={precedent.precedent_id} key={precedent.precedent_id}>
                  <div className="precedent-match-heading">
                    <span>{precedent.source_type === "resolved_case" ? "Resolved case" : "Approved amendment"}</span>
                    <span className="precedent-similarity mono">Cosine similarity {precedent.similarity.toFixed(3)}</span>
                  </div>
                  <h4>{humanize(precedent.kind)} · {humanize(precedent.outcome)}</h4>
                  <p>{precedent.summary}</p>
                  <dl className="precedent-identifiers">
                    <div><dt>Source</dt><dd>{precedent.source_type === "resolved_case" ? <a className="text-link mono" href={`#investigations/${encodeURIComponent(precedent.source_id)}`}>{precedent.source_id}</a> : <code>{precedent.source_id}</code>}</dd></div>
                    <div><dt>Precedent</dt><dd><code>{precedent.precedent_id}</code></dd></div>
                    <div><dt>Contract</dt><dd><code>{precedent.contract_id}</code></dd></div>
                  </dl>
                  {precedent.synthetic === true ? <Badge>Synthetic source</Badge> : precedent.synthetic === null ? <Badge>Source label not recorded</Badge> : null}
                </li>
              ))}
            </ol>
          ) : (
            <p className="small subtle">No similar records were returned for this case.</p>
          )}
        </section>
      )}
    </>
  );
}

export function Timeline({ item }: { item: Investigation }) {
  return item.events.length ? (
    <ol className="timeline">
      {item.events.map((event, index) => (
        <li key={event.id}>
          <span className="timeline-number">
            {String(index + 1).padStart(2, "0")}
          </span>
          <div>
            <div className="timeline-title">
              <strong>{humanize(event.kind)}</strong>
              <time className="mono" dateTime={event.at}>
                {shortTime(event.at)}
              </time>
            </div>
            <details>
              <summary>Inspect recorded event</summary>
              <JsonBlock
                value={event.detail}
                title={`${humanize(event.kind)} details`}
                compact
              />
            </details>
          </div>
        </li>
      ))}
    </ol>
  ) : (
    <EmptyState compact icon={History} title="No audit events returned">
      The native API has not returned timeline events for this case.
    </EmptyState>
  );
}

function AgentView({ item }: { item: Investigation }) {
  const reads = item.agent?.tool_reads;
  return (
    <>
      <Notice tone="purple" icon={Sparkles}>
        The agent proposes a decision. Only deterministic server policy can
        authorize a route.
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
            <section className="agent-tool-reads" aria-label="Evidence tool reads">
              <h3>Evidence tool reads</h3>
              <p className="small subtle">Counts come from the recorded callbacks for this investigation.</p>
              <Metadata>
                {([
                  ["message", "Current message"],
                  ["contracts", "Approved contracts"],
                  ["related", "Related records"],
                  ["precedents", "Similar precedents"],
                ] as const).map(([key, label]) => (
                  <MetaRow label={label} key={key} mono><span data-tool-read={key}>{typeof reads[key] === "number" ? reads[key] : "Not recorded"}</span></MetaRow>
                ))}
              </Metadata>
            </section>
          )}
          <JsonBlock value={item.agent} title="Native agent activity" />
        </>
      ) : (
        <EmptyState compact icon={Sparkles} title="No agent execution recorded">
          A configured provider alone does not prove that a native agent ran.
        </EmptyState>
      )}
      {item.recommendation ? (
        <JsonBlock
          value={item.recommendation}
          title="Persisted recommendation"
        />
      ) : (
        <Notice tone="amber">
          No structured recommendation is available. The route must remain
          subject to fail-closed policy.
        </Notice>
      )}
    </>
  );
}

function ReviewDialog({
  item,
  action,
  onClose,
  onComplete,
}: {
  item: Investigation;
  action: "APPROVE" | "REJECT";
  onClose: () => void;
  onComplete: (result: Investigation) => void;
}) {
  const savedAction = recordedAction(item.review?.action);
  const recorded: { action: "APPROVE" | "REJECT"; reason: string; expected_version: number; idempotency_key: string } | null = item.workflow && item.review
    && savedAction
    && typeof item.review.reason === "string"
    && typeof item.review.expected_version === "number"
    && typeof item.review.idempotency_key === "string"
      ? { action: savedAction, reason: item.review.reason,
          expected_version: item.review.expected_version, idempotency_key: item.review.idempotency_key }
      : null;
  const [reason, setReason] = useState(recorded?.reason ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [submittedRequest, setSubmittedRequest] = useState<{
    action: "APPROVE" | "REJECT"; reason: string; expected_version: number; idempotency_key: string;
  } | null>(recorded);
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (busy || reason.trim().length < 8) return;
    const body = submittedRequest ?? { action, reason: reason.trim(), expected_version: item.version, idempotency_key: crypto.randomUUID() };
    setSubmittedRequest(body);
    setBusy(true);
    setError(null);
    try {
      // Refresh persisted state before retrying an uncertain outcome. Reuse
      // the complete original request, including its original case version.
      if (submittedRequest) await request(`/api/cases/${encodeURIComponent(item.id)}`, CaseSchema);
      const result = await request(
        `/api/cases/${encodeURIComponent(item.id)}/review`,
        CaseSchema,
        {
          body,
        },
      );
      onComplete(result);
    } catch (failure) {
      setError(failure);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Modal
      title={
        action === "APPROVE"
          ? "Request a controlled release"
          : "Reject this transaction"
      }
      description={
        action === "APPROVE"
          ? "IRIS will verify reviewer permission, the current case version and every deterministic release gate before delivering."
          : "IRIS will record your reason and reject the held transaction. This action requires reviewer permission."
      }
      onClose={onClose}
    >
      <div className="review-context">
        <span>Case</span>
        <code>{item.id}</code>
        <Badge>{recorded ? "Original version" : "Version"} {submittedRequest?.expected_version ?? item.version}</Badge>
      </div>
      <form onSubmit={submit}>
        <label className="field-label" htmlFor="review-reason">
          Reason <span>Required · 8 characters minimum</span>
        </label>
        <textarea
          id="review-reason"
          data-autofocus
          rows={4}
          value={reason}
          onChange={(event) => {
            setReason(event.target.value);
          }}
          placeholder="Describe the evidence supporting this action…"
          maxLength={2000}
          disabled={busy || submittedRequest !== null}
          required
          minLength={8}
        />
        {error !== null && <InlineError error={error} />}
        <p className="form-hint">
          {submittedRequest ? "Retry resumes this exact recorded request. Its reason and original version stay fixed." : "IRIS checks the case version and preserves one review receipt. An uncertain result can be resumed safely."}
        </p>
        <div className="modal-actions">
          <Button type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            kind={action === "APPROVE" ? "primary" : "danger"}
            icon={action === "APPROVE" ? ShieldCheck : ShieldX}
            disabled={busy || reason.trim().length < 8}
          >
            {busy
              ? "Recording action…"
              : submittedRequest ? "Resume recorded review" : action === "APPROVE"
                ? "Request release"
                : "Reject transaction"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export function CaseDetail({
  item,
  compact = false,
}: {
  item: Investigation;
  compact?: boolean;
}) {
  const [tab, setTab] = useState<"evidence" | "timeline" | "payload" | "agent">(
    "evidence",
  );
  const [review, setReview] = useState<"APPROVE" | "REJECT" | null>(null);
  const canReview = useContext(ReviewPermissionContext);
  const { refresh, notify } = useActions();
  const closeReview = useCallback(() => setReview(null), []);
  const checks = checksFor(item);
  const held = item.routing === "QUARANTINED" || item.routing === "REVIEW";
  const nativeTask = Boolean(item.workflow?.task_id);
  return (
    <div className={`case-layout ${compact ? "case-layout-compact" : ""}`}>
      <article className="case-evidence">
        <div className="case-detail-heading">
          <div className="detail-title-row">
            <h2 tabIndex={-1}>
              {item.assessment
                ? humanize(item.assessment.classification)
                : "Investigation in progress"}
            </h2>
            <Badge tone={toneFor(item.routing)} dot>
              {humanize(item.routing)}
            </Badge>
          </div>
          <p className="detail-source">
            <span>{item.source}</span>
            <span aria-hidden="true">/</span>
            <code>{item.event_id}</code>
          </p>
          <div className="case-identifier">
            <Fingerprint size={13} aria-hidden="true" />
            <span>Investigation</span>
            <code>{item.id}</code>
          </div>
        </div>
        <div
          className={`decision-strip ${toneFor(item.policy?.decision ?? "")}`}
        >
          <div className="decision-icon">
            <ShieldCheck size={23} strokeWidth={1.5} />
          </div>
          <div>
            <div className="section-kicker">Policy-constrained outcome</div>
            <strong>
              {item.policy
                ? humanize(item.policy.decision)
                : "Awaiting policy evaluation"}
            </strong>
            <p>
              {item.routing === "DELIVERED"
                ? "The native API reports a delivery to the destination simulator."
                : item.routing === "PROCESSING"
                  ? "No final route has been reported. Refresh to inspect persisted progress."
                  : item.routing === "REJECTED"
                    ? "The transaction was rejected. Inspect the recorded reviewer action."
                    : "Held from the downstream destination."}
            </p>
          </div>
          {item.policy && (
            <span className="decision-version mono">
              {item.policy.policy_version}
            </span>
          )}
        </div>
        <div
          className="detail-tabs"
          role="tablist"
          aria-label="Investigation detail"
        >
          {(
            [
              { id: "evidence", label: "Evidence", icon: GitCompareArrows },
              { id: "timeline", label: "Timeline", icon: History },
              { id: "payload", label: "Payload", icon: FileJson2 },
              { id: "agent", label: "Agent", icon: Sparkles },
            ] as const
          ).map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              id={`tab-${item.id}-${id}`}
              role="tab"
              aria-selected={tab === id}
              aria-controls={`panel-${item.id}`}
              tabIndex={tab === id ? 0 : -1}
              onClick={() => setTab(id)}
              onKeyDown={(event) => {
                const tabs = [
                  "evidence",
                  "timeline",
                  "payload",
                  "agent",
                ] as const;
                let index = tabs.indexOf(tab);
                if (event.key === "ArrowRight")
                  index = (index + 1) % tabs.length;
                else if (event.key === "ArrowLeft")
                  index = (index + tabs.length - 1) % tabs.length;
                else if (event.key === "Home") index = 0;
                else if (event.key === "End") index = tabs.length - 1;
                else return;
                event.preventDefault();
                const next = tabs[index]!;
                setTab(next);
                document.getElementById(`tab-${item.id}-${next}`)?.focus();
              }}
            >
              <Icon size={15} />
              {label}
              {id === "timeline" && <span>{item.events.length}</span>}
            </button>
          ))}
        </div>
        <section
          id={`panel-${item.id}`}
          key={tab}
          className="detail-body"
          role="tabpanel"
          aria-labelledby={`tab-${item.id}-${tab}`}
        >
          {tab === "evidence" && <Evidence item={item} />}
          {tab === "timeline" && <Timeline item={item} />}
          {tab === "payload" && (
            <>
              <JsonBlock
                value={item.message}
                title="Original partner message"
              />
              <Metadata>
                <MetaRow label="Correlation ID" mono>
                  {display(item.message.correlation_id)}
                </MetaRow>
                <MetaRow label="Received">{dateTime(item.received_at)}</MetaRow>
              </Metadata>
            </>
          )}
          {tab === "agent" && <AgentView item={item} />}
        </section>
      </article>
      <aside className="case-provenance" aria-label="Provenance and actions">
        <div className="aside-section">
          <div className="section-kicker">
            <ShieldCheck size={14} /> Policy validation
          </div>
          {item.policy ? (
            <>
              <DecisionBadge value={item.policy.decision} />
              <details className="policy-rationale">
                <summary>Decision reasons</summary>
                <ul className="policy-reasons">
                {item.policy.reasons.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
                </ul>
              </details>
              <ul className="policy-checks">
                {checks.map((check, index) => (
                  <li
                    key={index}
                    className={
                      check.passed === true
                        ? "passed"
                        : check.passed === false
                          ? "failed"
                          : ""
                    }
                  >
                    {check.passed === true ? (
                      <Check size={14} />
                    ) : check.passed === false ? (
                      <X size={14} />
                    ) : (
                      <span className="unknown-check">?</span>
                    )}
                    <details className="policy-check-detail">
                      <summary>{check.label}</summary>
                      {check.reason && <p>{check.reason}</p>}
                    </details>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="subtle small">
              Policy has not produced a persisted result.
            </p>
          )}
        </div>
        <div className="aside-section">
          <div className="section-kicker">Provenance</div>
          <Metadata>
            <MetaRow label="Case ID" mono>
              <span className="copy-row">
                {item.id}
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
        </div>
        {held && (
          <div className="aside-section review-actions">
            <div className="section-kicker">Reviewer actions</div>
            {!nativeTask ? (
              <p className="small subtle">
                {item.assessment?.critical
                  ? "Critical contradictions require a corrected event or reference and a new investigation."
                  : item.workflow
                    ? "The native review task is being created. Refresh before acting on this hold."
                    : "This historical hold has no native review task. Start a new investigation with the corrected event and current approved references."}
              </p>
            ) : item.workflow && item.review && recordedAction(item.review.action) ? (
              <>
                <p className="small subtle">A review is recorded. Resume its native task completion and route using the original request.</p>
                <Button disabled={!canReview} onClick={() => setReview(recordedAction(item.review?.action))}>Resume recorded review</Button>
              </>
            ) : <>
            <Button
              icon={ArrowDownToLine}
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
              icon={ShieldX}
              disabled={!canReview}
              onClick={() => setReview("REJECT")}
            >
              Reject transaction
            </Button>
            <p className="small subtle">
              {!canReview
                ? "Review actions require IRIS reviewer permission to release or reject transactions."
                : item.assessment?.critical
                  ? "Critical contradictions require a corrected event or reference and a new investigation."
                  : "Reviewer permission, a reason and a current case version are required."}
            </p>
            </>}
          </div>
        )}
        {item.workflow && (
          <div className="aside-section">
            <div className="section-kicker">Native review task</div>
            <Metadata>
              <MetaRow label="Status">{humanize(item.workflow.status)}</MetaRow>
              <MetaRow label="Task" mono>{display(item.workflow.task_id)}</MetaRow>
              <MetaRow label="Worklist">{item.workflow.role}</MetaRow>
            </Metadata>
          </div>
        )}
        {item.review && (
          <div className="aside-section">
            <div className="section-kicker">Recorded review</div>
            <JsonBlock value={item.review} title="Reviewer audit" compact />
          </div>
        )}
      </aside>
      {review && canReview && nativeTask && (
        <ReviewDialog
          item={item}
          action={review}
          onClose={closeReview}
          onComplete={(result) => {
            setReview(null);
            notify(
              `Review recorded. Current route: ${humanize(result.routing)}.`,
            );
            refresh();
          }}
        />
      )}
    </div>
  );
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
  const [queueExpanded, setQueueExpanded] = useState(false);
  const detailRegion = useRef<HTMLDivElement>(null);
  const openedCase = useRef<string | null>(null);
  const { inspectCase } = useActions();
  const activeId = caseId ?? cases.data?.items[0]?.id;
  const detail = useApi(
    activeId ? `/api/cases/${encodeURIComponent(activeId)}` : null,
    CaseSchema,
    refresh * 1000 + polls,
  );
  useEffect(() => setPolls(0), [activeId]);
  useEffect(() => {
    // The old queue scroll position must not become the new case's viewport.
    // Wait for its actual record; polling and refreshes of the same case keep
    // the operator's reading position and keyboard focus.
    if (!caseId || !detail.data || detail.data.id !== activeId || openedCase.current === detail.data.id) return;
    openedCase.current = detail.data.id;
    window.scrollTo({ top: 0, behavior: "instant" });
    detailRegion.current?.querySelector<HTMLElement>(".detail-title-row h2")?.focus({ preventScroll: true });
  }, [activeId, caseId, detail.data]);
  useEffect(() => {
    if (detail.data?.routing === "PROCESSING" && polls < 30) {
      const timeout = window.setTimeout(
        () => setPolls((count) => count + 1),
        2000,
      );
      return () => window.clearTimeout(timeout);
    }
  }, [detail.data, polls]);
  const items = useMemo(
    () =>
      cases.data?.items.filter((item) => {
        const matches = `${item.id} ${item.event_id} ${item.source}`
          .toLowerCase()
          .includes(query.toLowerCase());
        return (
          matches &&
          (filter === "all" ||
            item.policy?.decision === filter ||
            item.routing === filter)
        );
      }) ?? [],
    [cases.data, query, filter],
  );
  return (
    <>
      <PageHeading
        eyebrow="Operations / semantic integrity"
        title="Investigations"
        description="Follow the message from original payload to approved evidence and outcome."
      >
        <a className="button secondary" href="#scenarios">
          Open Scenario Lab <ArrowRight size={15} />
        </a>
      </PageHeading>
      <div className="workbench">
        <aside className={`case-queue ${queueExpanded ? "queue-expanded" : ""}`} aria-label="Investigation queue">
          <div className="queue-heading">
            <h2>Investigation queue</h2>
            <span className="count mono">
              {cases.data ? cases.data.total : "—"}
            </span>
            <button
              type="button"
              className="icon-button queue-toggle"
              aria-label={queueExpanded ? "Collapse investigation queue" : "Expand investigation queue"}
              aria-expanded={queueExpanded}
              aria-controls="investigation-queue-content"
              onClick={() => setQueueExpanded((open) => !open)}
            >
              <ChevronDown size={18} />
            </button>
          </div>
          <div className="queue-content" id="investigation-queue-content">
          <div className="queue-controls">
            <label className="search-input">
              <Search size={15} />
              <span className="sr-only">Search investigations</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Event, source, or case ID"
                type="search"
              />
            </label>
            <label className="queue-filter">
              <span>Decision</span>
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
            </label>
          </div>
          {cases.loading ? (
            <div className="queue-state" role="status">
              Reading case records…
            </div>
          ) : cases.error ? (
            <div className="queue-state">
              <Inbox size={24} strokeWidth={1.4} />
              <strong>Queue unavailable</strong>
              <p>No native records have been loaded.</p>
              <span className="mono small">{cases.error.code}</span>
            </div>
          ) : !items.length ? (
            <div className="queue-state">
              <Inbox size={24} strokeWidth={1.4} />
              <strong>
                {cases.data?.items.length
                  ? "No matching cases"
                  : "Your queue is clear"}
              </strong>
              <p>
                {cases.data?.items.length
                  ? "Try another source or decision filter."
                  : "Run a synthetic scenario to create the first native investigation."}
              </p>
            </div>
          ) : (
            <ol className="case-list">
              {items.map((item) => (
                <li key={item.id}>
                  <button
                    className={`case-list-item ${activeId === item.id ? "selected" : ""}`}
                    aria-pressed={activeId === item.id}
                    onClick={() => {
                      inspectCase(item.id);
                      setQueueExpanded(false);
                      window.scrollTo({ top: 0, behavior: "instant" });
                      if (detail.data?.id === item.id) {
                        detailRegion.current?.querySelector<HTMLElement>(".detail-title-row h2")?.focus({ preventScroll: true });
                      }
                    }}
                  >
                    <span className="case-item-top">
                      <code>{item.id}</code>
                      <time dateTime={item.received_at}>
                        {shortTime(item.received_at)}
                      </time>
                    </span>
                    <strong>
                      {item.assessment
                        ? humanize(item.assessment.classification)
                        : "Processing event"}
                    </strong>
                    <span className="case-item-source">{item.source}</span>
                    <span className="case-item-bottom">
                      {item.policy ? (
                        <DecisionBadge value={item.policy.decision} />
                      ) : (
                        <Badge>Processing</Badge>
                      )}
                      <ChevronRight size={14} />
                    </span>
                  </button>
                </li>
              ))}
            </ol>
          )}
          <div className="queue-footer">
            <span>
              {cases.data
                ? `${items.length} shown from the first ${cases.data.limit} records`
                : "Native records only"}
            </span>
          </div>
          </div>
        </aside>
        <div className="investigation-main" ref={detailRegion}>
          {detail.data ? (
            <>
              <CaseDetail item={detail.data} key={detail.data.id} />
              {polls >= 30 && detail.data.routing === "PROCESSING" && (
                <Notice tone="amber">
                  Automatic refresh paused after one minute. Refresh to inspect
                  the current persisted state.
                </Notice>
              )}
            </>
          ) : detail.loading ? (
            <div className="loading-state" role="status">
              <Fingerprint size={25} />
              <span>Reading investigation…</span>
            </div>
          ) : detail.error ? (
            <ErrorState error={detail.error} />
          ) : (
            <div className="workbench-empty">
              <div className="empty-emblem">
                <GitCompareArrows size={38} strokeWidth={1.1} />
                <span />
              </div>
              <h2>Evidence workbench</h2>
              <p>
                Compare the message that arrived with the business meaning that
                was approved. Every finding, recommendation and route stays
                inspectable.
              </p>
              {cases.error && <ErrorState error={cases.error} compact />}
              <NativePath />
              <div className="workbench-empty-footer">
                <ShieldCheck size={14} />
                <span>
                  Original payload, approved references, and an auditable route.
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
