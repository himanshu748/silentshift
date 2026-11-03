import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Beaker,
  Braces,
  Check,
  ChevronRight,
  CircleHelp,
  Clock3,
  Database,
  FileJson2,
  FlaskConical,
  GitCompareArrows,
  History,
  Inbox,
  KeyRound,
  Layers3,
  Play,
  Plus,
  Scale,
  Server,
  ShieldCheck,
  ShieldX,
  Terminal,
  Unplug,
} from "lucide-react";
import {
  CaseSchema,
  CasesSchema,
  EvaluationsSchema,
  JsonObject,
  OverviewSchema,
  PoliciesSchema,
  ScenariosSchema,
} from "./schema";
import type { Health, Investigation } from "./schema";
import { request, useApi } from "./api";
import type { Resource } from "./api";
import {
  Badge,
  Button,
  CaseTable,
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
  ResourceState,
  toneFor,
  useActions,
} from "./ui";
import { CaseDetail, Timeline } from "./Investigations";

export function ScenarioLab({ refresh }: { refresh: number }) {
  const catalog = useApi("/api/scenarios", ScenariosSchema, refresh);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [result, setResult] = useState<Investigation | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [polled, setPolled] = useState(0);
  const { inspectCase, notify } = useActions();
  const scenario =
    catalog.data?.scenarios.find((item) => item.id === selectedId) ??
    catalog.data?.scenarios[0];
  const [resultScenario, setResultScenario] = useState<string | null>(null);
  useEffect(() => {
    if (result?.routing !== "PROCESSING" || polled >= 30) return;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => {
      request(`/api/cases/${encodeURIComponent(result.id)}`, CaseSchema, {
        signal: controller.signal,
      })
        .then(setResult)
        .catch((failure) => {
          if (!controller.signal.aborted) setError(failure);
        })
        .finally(() => {
          if (!controller.signal.aborted) setPolled((count) => count + 1);
        });
    }, 2000);
    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, [result, polled]);
  const run = async () => {
    if (!scenario || running) return;
    const id =
      error && runId && resultScenario === scenario.id
        ? runId
        : crypto.randomUUID();
    setRunId(id);
    setResultScenario(scenario.id);
    setRunning(true);
    setError(null);
    setResult(null);
    setPolled(0);
    try {
      const item = await request(
        `/api/scenarios/${encodeURIComponent(scenario.id)}/run`,
        CaseSchema,
        { body: { run_id: id } },
      );
      setResult(item);
      notify(`Native API returned case ${item.id}.`);
    } catch (failure) {
      setError(failure);
    } finally {
      setRunning(false);
    }
  };
  return (
    <>
      <PageHeading
        eyebrow="Validation / reproducible experiments"
        title="Scenario Lab"
        description="Make a silent failure visible. Inject a real event into the native production."
      >
        <Badge tone="purple">
          <FlaskConical size={13} /> Synthetic fixtures
        </Badge>
      </PageHeading>
      <div className="lab-intro">
        <div>
          <span className="section-kicker">
            Technically successful ≠ semantically correct
          </span>
          <h2>Put meaning under pressure.</h2>
          <p>
            Five controlled experiments. Independent reference records. One
            inspectable route.
          </p>
        </div>
        <div className="lab-intro-mark" aria-hidden="true">
          <Braces size={30} strokeWidth={1.2} />
          <span />
          <Scale size={27} strokeWidth={1.2} />
        </div>
      </div>
      {!catalog.data ? (
        <div className="panel">
          <ResourceState resource={catalog} />
        </div>
      ) : (
        <div className="lab-layout">
          <aside className="scenario-list" aria-label="Synthetic scenarios">
            <div className="scenario-list-header">
              <span className="section-kicker">Choose an experiment</span>
              <code>{catalog.data.version}</code>
            </div>
            {catalog.data.scenarios.map((item, index) => (
              <button
                className={`scenario-choice ${scenario?.id === item.id ? "selected" : ""}`}
                key={item.id}
                onClick={() => {
                  setSelectedId(item.id);
                  setError(null);
                }}
                disabled={running}
              >
                <span className="scenario-number mono">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span>
                  <strong>{item.name.replace(/^[A-E] [·•] /, "")}</strong>
                  <small>{item.summary}</small>
                </span>
                <ChevronRight size={16} />
              </button>
            ))}
            <div className="scenario-list-note">
              <CircleHelp size={15} />
              <p>
                Expected outcomes are frozen ground truth, separate from
                observed production results.
              </p>
            </div>
          </aside>
          <section className="scenario-detail">
            {scenario ? (
              <>
                <div className="scenario-heading">
                  <div className="section-kicker">
                    <Beaker size={14} /> {scenario.id}
                  </div>
                  <h2>{scenario.name.replace(/^[A-E] [·•] /, "")}</h2>
                  <p>{scenario.summary}</p>
                </div>
                {scenario.id === "unsafe-agent-output" && (
                  <Notice tone="amber" icon={ShieldX}>
                    Validator fault injection: an unsafe recommendation is
                    inserted after the native investigation. This tests
                    deterministic policy, not a claim that the model produced
                    that recommendation.
                  </Notice>
                )}
                <div className="expected-result">
                  <div>
                    <span className="section-kicker">
                      Frozen expected decision
                    </span>
                    <DecisionBadge value={scenario.ground_truth.decision} />
                  </div>
                  <p>{scenario.ground_truth.reason}</p>
                </div>
                <div className="scenario-payload-grid">
                  <JsonBlock
                    value={scenario.message}
                    title="Partner event to inject"
                  />
                  <div>
                    <div className="section-header">
                      <h3>Independent references</h3>
                      <Badge>{scenario.references.length}</Badge>
                    </div>
                    {scenario.references.map((reference, index) => (
                      <details className="reference-record" key={index}>
                        <summary>
                          <ChevronRight size={14} />
                          <span className="mono">
                            {display(reference.id ?? `Reference ${index + 1}`)}
                          </span>
                        </summary>
                        <JsonBlock
                          value={reference}
                          title={`Frozen reference ${index + 1}`}
                          compact
                        />
                      </details>
                    ))}
                    <div className="fixture-clock">
                      <Clock3 size={15} />
                      <div>
                        <span>Frozen evaluation clock</span>
                        <time className="mono" dateTime={catalog.data.clock}>
                          {dateTime(catalog.data.clock)}
                        </time>
                      </div>
                    </div>
                    <p className="small subtle">
                      The server owns reference selection and execution. The
                      browser cannot substitute release evidence.
                    </p>
                  </div>
                </div>
                <div className="scenario-run">
                  <div>
                    <strong>Ready for a native run</strong>
                    <p>
                      Creates a persisted case through the IRIS Business
                      Service. A live agent call may be made.
                    </p>
                  </div>
                  <Button
                    icon={Play}
                    kind="primary"
                    disabled={running}
                    onClick={run}
                  >
                    {running
                      ? "Waiting for IRIS…"
                      : error && runId && resultScenario === scenario.id
                        ? "Retry same injection"
                        : "Inject into IRIS"}
                  </Button>
                </div>
                {running && (
                  <div className="run-pending" role="status">
                    <Database size={18} />
                    <div>
                      <strong>Request sent to IRIS</strong>
                      <p>
                        IRIS is investigating this event. Keep the run ID for a
                        safe retry if the connection is interrupted.
                      </p>
                    </div>
                  </div>
                )}
                {error !== null && <InlineError error={error} />}
                {runId && resultScenario === scenario.id && (
                  <div className="run-id">
                    <span>Run ID</span>
                    <code>{runId}</code>
                    <CopyButton value={runId} label="Copy run ID" />
                  </div>
                )}
                {result && resultScenario === scenario.id && (
                  <section className="observed-result">
                    <div className="section-header">
                      <div>
                        <div className="section-kicker">
                          Observed native result
                        </div>
                        <h3>
                          {result.policy
                            ? humanize(result.policy.decision)
                            : "Processing"}
                        </h3>
                      </div>
                      {result.policy && result.routing !== "PROCESSING" && (
                        <Badge
                          tone={
                            result.policy.decision ===
                            scenario.ground_truth.decision
                              ? "mint"
                              : "coral"
                          }
                        >
                          {result.policy.decision ===
                          scenario.ground_truth.decision ? (
                            <Check size={13} />
                          ) : (
                            <CircleHelp size={13} />
                          )}
                          {result.policy.decision ===
                          scenario.ground_truth.decision
                            ? "Matches expectation"
                            : "Differs from expectation"}
                        </Badge>
                      )}
                    </div>
                    <Metadata>
                      <MetaRow label="Case" mono>
                        {result.id}
                      </MetaRow>
                      <MetaRow label="Route">
                        <DecisionBadge value={result.routing} />
                      </MetaRow>
                      <MetaRow label="Native trace" mono>
                        {result.trace_id === null
                          ? "Not recorded"
                          : result.trace_id}
                      </MetaRow>
                    </Metadata>
                    <Timeline item={result} />
                    {result.routing === "PROCESSING" && polled >= 30 && (
                      <Notice tone="amber">
                        Automatic refresh paused. Open the investigation and
                        refresh for the current state.
                      </Notice>
                    )}
                    <Button
                      icon={ArrowUpRight}
                      onClick={() => inspectCase(result.id)}
                    >
                      Inspect full investigation
                    </Button>
                  </section>
                )}
              </>
            ) : (
              <EmptyState title="No scenarios in this version">
                The native catalog returned no executable fixtures.
              </EmptyState>
            )}
          </section>
        </div>
      )}
    </>
  );
}

export function Overview({
  refresh,
  health,
}: {
  refresh: number;
  health: Resource<Health>;
}) {
  const data = useApi("/api/overview", OverviewSchema, refresh);
  const metrics = [
    {
      key: "processed",
      label: "Messages processed",
      icon: Layers3,
      tone: "blue",
      caption: "Persisted native records",
    },
    {
      key: "contradictions",
      label: "Verified contradictions",
      icon: GitCompareArrows,
      tone: "coral",
      caption: "Independent evidence disagrees",
    },
    {
      key: "pending_reviews",
      label: "Pending reviews",
      icon: History,
      tone: "amber",
      caption: "Awaiting an authorized decision",
    },
    {
      key: "quarantined",
      label: "Quarantined transactions",
      icon: ShieldX,
      tone: "purple",
      caption: "Held from the destination",
    },
  ] as const;
  return (
    <>
      <PageHeading
        eyebrow="Workspace / operations"
        title="Overview"
        description="A clear view of what arrived, what changed, and what was contained."
      >
        <a href="#scenarios" className="button primary">
          <Play size={15} />
          Run a scenario
        </a>
      </PageHeading>
      <div className="metric-grid">
        {metrics.map(({ key, label, icon: Icon, tone, caption }) => (
          <article className="metric" key={key}>
            <div className="metric-heading">
              <span>{label}</span>
              <Icon size={17} className={tone} />
            </div>
            <strong className="metric-number mono">
              {data.data ? data.data[key].toLocaleString() : "—"}
            </strong>
            <p>
              {data.data
                ? caption
                : data.loading
                  ? "Reading native records…"
                  : "Unavailable until the API responds"}
            </p>
          </article>
        ))}
      </div>
      {data.error && <ErrorState error={data.error} />}
      <div className="overview-layout">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Recent investigations</h2>
              <p>The latest cases returned by the native API.</p>
            </div>
            <a href="#investigations" className="text-link">
              View queue <ArrowRight size={14} />
            </a>
          </div>
          {data.data ? (
            data.data.recent.length ? (
              <CaseTable cases={data.data.recent} />
            ) : (
              <EmptyState compact icon={Inbox} title="No investigations yet">
                Run a synthetic scenario or inject a partner event to begin.
              </EmptyState>
            )
          ) : data.loading ? (
            <div className="loading-state" role="status">
              Reading investigations…
            </div>
          ) : (
            <div className="quiet-panel">
              <Database size={20} />
              <p>
                Case history is unavailable while the native API is
                disconnected.
              </p>
            </div>
          )}
        </section>
        <aside className="panel production-summary">
          <div className="panel-header">
            <h2>Production signal</h2>
            <Activity size={17} />
          </div>
          <div className="production-summary-body">
            <div className="signal-identity">
              <span className="production-icon">
                <Server size={23} strokeWidth={1.4} />
              </span>
              <div>
                <strong>
                  {health.data?.production.name ?? "InterSystems IRIS"}
                </strong>
                <small>Native interoperability</small>
              </div>
            </div>
            <Metadata>
              <MetaRow label="Production">
                {health.data ? (
                  <Badge
                    tone={health.data.production.running ? "mint" : "amber"}
                    dot
                  >
                    {health.data.production.running ? "Running" : "Not running"}
                  </Badge>
                ) : (
                  "Not observed"
                )}
              </MetaRow>
              <MetaRow label="Agent configured">
                {health.data
                  ? health.data.agent.configured
                    ? "Yes"
                    : "No"
                  : "Not observed"}
              </MetaRow>
              <MetaRow label="Last native success">
                {health.data
                  ? dateTime(health.data.agent.last_success_at)
                  : "Not observed"}
              </MetaRow>
            </Metadata>
            <a href="#health" className="button secondary">
              Inspect health <ArrowRight size={14} />
            </a>
          </div>
        </aside>
      </div>
      <section className="principle-strip">
        <span className="section-kicker">How SilentShift works</span>
        <NativePath observed={Boolean(health.data)} />
        <p>
          A recommendation is evidence to evaluate. It is never permission to
          deliver.
        </p>
      </section>
    </>
  );
}

function MessageDialog({
  onClose,
  onComplete,
}: {
  onClose: () => void;
  onComplete: (item: Investigation) => void;
}) {
  const [payload, setPayload] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  return (
    <Modal
      title="Inject a partner event"
      description="Submit original JSON through the authenticated IRIS Business Service. The native server retrieves reference evidence and controls routing."
      onClose={onClose}
    >
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          setBusy(true);
          setError(null);
          try {
            JsonObject.parse(JSON.parse(payload));
            onComplete(
              await request("/api/messages", CaseSchema, { rawBody: payload }),
            );
          } catch (failure) {
            setError(failure);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label htmlFor="message-json" className="field-label">
          Original message JSON
        </label>
        <textarea
          className="json-input"
          id="message-json"
          data-autofocus
          value={payload}
          onChange={(event) => setPayload(event.target.value)}
          rows={12}
          maxLength={64000}
          required
          spellCheck={false}
          disabled={busy}
          placeholder="Paste a JSON object with event_id, source and contract fields…"
        />
        <p className="form-hint">
          Keep the event ID unchanged when retrying. A reused ID with changed
          content must be rejected by the server.
        </p>
        {error !== null && <InlineError error={error} />}
        <div className="modal-actions">
          <Button type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            kind="primary"
            icon={Plus}
            disabled={busy || !payload.trim()}
          >
            {busy ? "Waiting for IRIS…" : "Inject into IRIS"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export function Messages({ refresh }: { refresh: number }) {
  const cases = useApi("/api/cases?limit=50&offset=0", CasesSchema, refresh);
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [showSubmit, setShowSubmit] = useState(false);
  const { inspectCase, notify } = useActions();
  const close = useCallback(() => setShowSubmit(false), []);
  const items =
    cases.data?.items.filter((item) =>
      `${item.event_id} ${item.source} ${item.id}`
        .toLowerCase()
        .includes(query.toLowerCase()),
    ) ?? [];
  const item =
    cases.data?.items.find((record) => record.id === selected) ?? items[0];
  return (
    <>
      <PageHeading
        eyebrow="Operations / original records"
        title="Message Explorer"
        description="Inspect the original payload, reference snapshot, and semantic differences."
      >
        <Button kind="primary" icon={Plus} onClick={() => setShowSubmit(true)}>
          Inject message
        </Button>
      </PageHeading>
      {!cases.data ? (
        <div className="panel">
          <ResourceState resource={cases} />
        </div>
      ) : !cases.data.items.length ? (
        <div className="panel">
          <EmptyState icon={FileJson2} title="No messages received">
            The native production has not returned any message records. Inject
            an event or choose a synthetic scenario.
          </EmptyState>
        </div>
      ) : (
        <>
          <div className="message-toolbar">
            <label className="search-input">
              <span className="sr-only">Search messages</span>
              <FileJson2 size={16} />
              <input
                type="search"
                placeholder="Search event, source, or case ID"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <label className="message-select">
              <span>Message</span>
              <select
                value={item?.id ?? ""}
                onChange={(event) => setSelected(event.target.value)}
                aria-label="Select message"
              >
                {items.map((record) => (
                  <option value={record.id} key={record.id}>
                    {record.event_id} · {record.source}
                  </option>
                ))}
              </select>
            </label>
            <span className="small subtle">
              {items.length} of {cases.data.total} records · limit{" "}
              {cases.data.limit}
            </span>
          </div>
          {item ? (
            <>
              <section className="panel message-preview">
                <div className="panel-header">
                  <div>
                    <span className="section-kicker">Original payload</span>
                    <h2 className="mono">{item.event_id}</h2>
                  </div>
                  <Button
                    icon={ArrowUpRight}
                    onClick={() => inspectCase(item.id)}
                  >
                    Open investigation
                  </Button>
                </div>
                <div className="message-json-grid">
                  <JsonBlock value={item.message} title="Partner message" />
                  <JsonBlock
                    value={item.references}
                    title="Independent reference snapshot"
                  />
                </div>
              </section>
              <CaseDetail item={item} key={item.id} compact />
            </>
          ) : (
            <EmptyState title="No messages match this search">
              Try another event ID or source.
            </EmptyState>
          )}
        </>
      )}
      {showSubmit && (
        <MessageDialog
          onClose={close}
          onComplete={(result) => {
            setShowSubmit(false);
            notify(`IRIS returned case ${result.id}.`);
            inspectCase(result.id);
          }}
        />
      )}
    </>
  );
}

export function Evaluations({ refresh }: { refresh: number }) {
  const data = useApi("/api/evaluations", EvaluationsSchema, refresh);
  return (
    <>
      <PageHeading
        eyebrow="Validation / measured outcomes"
        title="Evaluations"
        description="Compare deterministic rules, native recommendations and policy-constrained outcomes."
      >
        <Badge>
          <FlaskConical size={13} /> Actual runs only
        </Badge>
      </PageHeading>
      <div className="evaluation-explainer">
        <div>
          <span className="evaluation-stage mono">01</span>
          <h3>Rule-only baseline</h3>
          <p>Independent deterministic assessment before the agent.</p>
        </div>
        <ArrowRight size={18} />
        <div>
          <span className="evaluation-stage mono">02</span>
          <h3>AI-assisted investigation</h3>
          <p>The structured native recommendation and its evidence.</p>
        </div>
        <ArrowRight size={18} />
        <div>
          <span className="evaluation-stage mono">03</span>
          <h3>Policy-constrained result</h3>
          <p>The final permitted route, checked against frozen ground truth.</p>
        </div>
      </div>
      {!data.data ? (
        <div className="panel">
          <ResourceState resource={data} />
        </div>
      ) : !data.data.items.length ? (
        <div className="panel evaluation-empty">
          <EmptyState icon={FlaskConical} title="No measured runs recorded">
            Execute the versioned evaluation against the native production, then
            refresh. Accuracy, safety, latency and usage stay unavailable until
            actual run records exist.
          </EmptyState>
          <div className="unmeasured-metrics">
            {[
              "Correct / total",
              "False quarantine rate",
              "Unsafe releases",
              "Review rate",
              "Latency",
              "Model usage / cost",
            ].map((label) => (
              <div key={label}>
                <span>{label}</span>
                <code>Not measured</code>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="evaluation-runs">
          {data.data.items.map((run) => (
            <section className="panel" key={run.id}>
              <div className="panel-header">
                <div>
                  <span className="section-kicker">
                    Recorded evaluation · {dateTime(run.created_at)}
                  </span>
                  <h2 className="mono">{run.id}</h2>
                </div>
                <Badge tone={run.native.passed ? "mint" : "amber"}>
                  {run.native.status}
                </Badge>
              </div>
              <div className="evaluation-record">
                <div className="evaluation-run-meta">
                  <Badge>{run.dataset_version}</Badge>
                  <span>
                    {run.native.accepted_records} / {run.native.expected_cases}{" "}
                    native records accepted
                  </span>
                </div>
                <div className="measured-metrics">
                  {(
                    [
                      [
                        "Native proposal accuracy",
                        run.native.proposal_accuracy,
                      ],
                      ["Final decision accuracy", run.native.final_accuracy],
                      [
                        "False quarantine rate",
                        run.native.false_quarantine_rate,
                      ],
                      ["Review rate", run.native.review_rate],
                    ] as const
                  ).map(([label, metric]) => (
                    <article key={label}>
                      <span>{label}</span>
                      <strong className="mono">
                        {metric.value === null
                          ? "Not measured"
                          : `${(metric.value * 100).toFixed(1)}%`}
                      </strong>
                      <small className="mono">
                        {metric.numerator} / {metric.denominator}
                      </small>
                    </article>
                  ))}
                  <article>
                    <span>Unsafe releases</span>
                    <strong
                      className={`mono ${run.native.unsafe_release.count === null ? "muted" : run.native.unsafe_release.count > 0 ? "coral" : "mint"}`}
                    >
                      {run.native.unsafe_release.count ?? "Not measured"}
                    </strong>
                    <small className="mono">
                      of {run.native.unsafe_release.denominator} cases
                    </small>
                  </article>
                  <article>
                    <span>Native latency</span>
                    <strong className="mono">
                      {run.native.latency.mean_ms === null
                        ? "Not measured"
                        : `${run.native.latency.mean_ms.toFixed(0)} ms`}
                    </strong>
                    <small className="mono">
                      p95{" "}
                      {run.native.latency.p95_ms === null
                        ? "unavailable"
                        : `${run.native.latency.p95_ms.toFixed(0)} ms`}{" "}
                      · {run.native.latency.observed_records}/
                      {run.native.latency.total_records} observed
                    </small>
                  </article>
                </div>
                {run.native.issues.length > 0 && (
                  <JsonBlock
                    value={run.native.issues}
                    title="Evaluation issues"
                  />
                )}
                <div className="evaluation-usage">
                  <span>
                    Model usage:{" "}
                    {run.native.model_usage === null ||
                    run.native.model_usage === undefined
                      ? "Not recorded"
                      : "Included in the measured record"}
                  </span>
                  <span>
                    Model cost:{" "}
                    {run.native.model_cost === null ||
                    run.native.model_cost === undefined
                      ? "Not recorded"
                      : display(run.native.model_cost)}
                  </span>
                </div>
                <details className="evaluation-raw">
                  <summary>
                    Inspect all comparisons, case IDs and measurement evidence
                  </summary>
                  <JsonBlock value={run} title="Measured evaluation record" />
                </details>
                <p className="small subtle">
                  Only server-recorded values are shown. Missing denominators,
                  usage and cost are not inferred.
                </p>
              </div>
            </section>
          ))}
        </div>
      )}
      <Notice tone="blue" icon={CircleHelp}>
        Five synthetic scenarios demonstrate specific behavior. Their results do
        not establish general accuracy on real business traffic.
      </Notice>
    </>
  );
}

export function Policies({ refresh }: { refresh: number }) {
  const data = useApi("/api/policies", PoliciesSchema, refresh);
  return (
    <>
      <PageHeading
        eyebrow="Governance / deterministic authority"
        title="Policies"
        description="The agent recommends. Policy decides which actions are permitted."
      >
        {data.data && (
          <Badge tone="mint">
            <ShieldCheck size={13} />
            {data.data.version}
          </Badge>
        )}
      </PageHeading>
      <div className="policy-principle">
        <div className="policy-principle-icon">
          <ShieldCheck size={31} strokeWidth={1.3} />
        </div>
        <div>
          <span className="section-kicker">An explicit trust boundary</span>
          <h2>Reasoning is not authorization.</h2>
          <p>
            Inspect the policy version and checks returned by IRIS. Every case
            records the checks that permitted or denied its route.
          </p>
        </div>
        <span className="mono">AI → POLICY → ROUTE</span>
      </div>
      {!data.data ? (
        <div className="panel">
          <ResourceState resource={data} />
        </div>
      ) : (
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Configured safety rules</h2>
              <p>Server-reported policy · {data.data.version}</p>
            </div>
            <Badge>{data.data.rules.length} rules</Badge>
          </div>
          {data.data.rules.length ? (
            <ol className="rules-list">
              {data.data.rules.map((rule, index) => (
                <li key={rule.id}>
                  <span className="rule-number mono">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <code>{rule.id}</code>
                    <p>{rule.description}</p>
                    {Object.keys(rule).some(
                      (key) => !["id", "description"].includes(key),
                    ) && (
                      <details>
                        <summary>Rule configuration</summary>
                        <JsonBlock
                          value={rule}
                          title={`${rule.id} configuration`}
                          compact
                        />
                      </details>
                    )}
                  </div>
                  <ShieldCheck size={18} />
                </li>
              ))}
            </ol>
          ) : (
            <EmptyState compact title="No policy rules returned">
              This API response does not establish an enforced policy
              configuration.
            </EmptyState>
          )}
        </section>
      )}
      <Notice tone="amber" icon={KeyRound}>
        Reviewer actions require server authorization, a recorded reason, a
        current case version and an idempotency key. Critical contradictions
        require corrected evidence and a new investigation.
      </Notice>
    </>
  );
}

export function SystemHealth({ health }: { health: Resource<Health> }) {
  const { openConnect } = useActions();
  return (
    <>
      <PageHeading
        eyebrow="Workspace / native dependencies"
        title="System Health"
        description="Observe the runtime. Separate configured access from proven execution."
      >
        <Button icon={KeyRound} onClick={openConnect}>
          IRIS session
        </Button>
      </PageHeading>
      <div className="health-metrics">
        <article className="panel health-status">
          <span className="health-icon">
            <Server size={23} />
          </span>
          <span className="section-kicker">Native production</span>
          <h2>
            {health.data
              ? health.data.production.running
                ? "Running"
                : "Not running"
              : health.loading
                ? "Checking…"
                : "Not observed"}
          </h2>
          <p className="mono">
            {health.data?.production.name ?? "Awaiting a native API response"}
          </p>
          {health.data && (
            <Badge tone={health.data.production.running ? "mint" : "amber"} dot>
              Server-reported status
            </Badge>
          )}
        </article>
        <article className="panel health-status">
          <span className="health-icon">
            <KeyRound size={23} />
          </span>
          <span className="section-kicker">Agent configuration</span>
          <h2>
            {health.data
              ? health.data.agent.configured
                ? "Configured"
                : "Not configured"
              : "Not observed"}
          </h2>
          <p>Configuration does not prove a model invocation.</p>
          {health.data && (
            <span className="small subtle">
              Last native success: {dateTime(health.data.agent.last_success_at)}
            </span>
          )}
        </article>
        <article className="panel health-status">
          <span className="health-icon">
            <Layers3 size={23} />
          </span>
          <span className="section-kicker">Reported runtime build</span>
          <h2 className="build-number mono">
            {health.data?.build ?? "Unavailable"}
          </h2>
          <p>
            Required: <code>2026.3.0AI.154.0</code> Community
          </p>
          <Badge tone="blue">AI Hub Early Access</Badge>
        </article>
      </div>
      {health.error && <ErrorState error={health.error} />}
      {health.data ? (
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Production components</h2>
              <p>Statuses returned by the actual native API.</p>
            </div>
            <Badge>{health.data.components.length} components</Badge>
          </div>
          {health.data.components.length ? (
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Component</th>
                    <th>Reported status</th>
                  </tr>
                </thead>
                <tbody>
                  {health.data.components.map((component) => (
                    <tr key={component.name}>
                      <td className="mono">{component.name}</td>
                      <td>
                        <Badge tone={toneFor(component.status)}>
                          {component.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState compact title="No component statuses returned">
              The health response does not include individual component
              observations.
            </EmptyState>
          )}
          <details className="raw-health">
            <summary>Inspect full health response</summary>
            <JsonBlock value={health.data} title="Native health response" />
          </details>
        </section>
      ) : (
        <section className="panel setup-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">Required native gate</span>
              <h2>Connect the substance.</h2>
              <p>
                The workbench needs a running build 154 production. It contains
                no mock operational backend.
              </p>
            </div>
            <Unplug size={25} strokeWidth={1.3} />
          </div>
          <ol className="setup-steps">
            <li>
              <span className="mono">01</span>
              <div>
                <h3>Load the official Community image</h3>
                <p>
                  Download the ARM64 or x64 build 154 from the AI Hub Early
                  Access portal, then load and retag it locally.
                </p>
                <a
                  className="text-link"
                  href="https://evaluation.intersystems.com/Eval/early-access/AIHub"
                  target="_blank"
                  rel="noreferrer"
                >
                  Open EAP portal <ArrowUpRight size={14} />
                </a>
              </div>
            </li>
            <li>
              <span className="mono">02</span>
              <div>
                <h3>Start the native stack</h3>
                <p>
                  Follow the repository setup to compile the production and
                  start its Web Gateway. No EAP binary is bundled here.
                </p>
                <div className="command-line">
                  <Terminal size={15} />
                  <code>uv run python scripts/bootstrap.py</code>
                  <CopyButton
                    value="uv run python scripts/bootstrap.py"
                    label="Copy Compose start command"
                  />
                </div>
              </div>
            </li>
            <li>
              <span className="mono">03</span>
              <div>
                <h3>Connect an IRIS account</h3>
                <p>
                  Use a viewer account for records and scenario ingestion.
                  Reviewer actions need an additional server permission.
                </p>
                <Button icon={KeyRound} onClick={openConnect}>
                  Connect to IRIS
                </Button>
              </div>
            </li>
          </ol>
          <div className="setup-footnote">
            <code>IRIS_API_ORIGIN</code>
            <p>
              The Vite development proxy forwards same-origin API requests to
              the configured IRIS Web Gateway. Credentials stay in this tab's
              memory.
            </p>
          </div>
        </section>
      )}
      <div className="health-footer">
        <span>
          <Activity size={14} />
          {health.checkedAt
            ? `Last API check: ${dateTime(health.checkedAt.toISOString())}`
            : "No API check completed"}
        </span>
        <span>Health checks do not invoke the agent.</span>
      </div>
    </>
  );
}
