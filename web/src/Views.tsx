import { useCallback, useEffect, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  CircleHelp,
  FileJson2,
  FlaskConical,
  Inbox,
  KeyRound,
  Play,
  Plus,
  ShieldX,
  Terminal,
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
  Loading,
  Metadata,
  MetaRow,
  Modal,
  NativePath,
  Notice,
  PageHeading,
  ResourceState,
  RouteMark,
  toneFor,
  useActions,
} from "./ui";
import { CaseDetail, listKeys, Timeline } from "./Investigations";

const scenarioName = (name: string) => name.replace(/^[A-E] [·•] /, "");

export function ScenarioLab({ refresh }: { refresh: number }) {
  const catalog = useApi("/api/scenarios", ScenariosSchema, refresh);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [result, setResult] = useState<Investigation | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [polled, setPolled] = useState(0);
  const [resultScenario, setResultScenario] = useState<string | null>(null);
  const { inspectCase, notify } = useActions();
  const scenario =
    catalog.data?.scenarios.find((item) => item.id === selectedId) ?? catalog.data?.scenarios[0];
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
  const retrying = Boolean(error && runId && resultScenario === scenario?.id);
  const run = async () => {
    if (!scenario || running) return;
    // A retry after an uncertain outcome reuses the run ID so IRIS can deduplicate.
    const id = retrying && runId ? runId : crypto.randomUUID();
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
  const matches = result?.policy?.decision === scenario?.ground_truth.decision;
  return (
    <>
      <PageHeading
        title="Scenario Lab"
        description="Inject a synthetic partner event into the native production and compare the observed route with frozen ground truth."
      >
        <Badge tone="agent">
          <FlaskConical size={13} aria-hidden="true" /> Synthetic fixtures
        </Badge>
      </PageHeading>
      {!catalog.data ? (
        <section className="panel">
          <ResourceState resource={catalog} />
        </section>
      ) : (
        <div className="split">
          <aside className="queue" aria-label="Synthetic scenarios">
            <div className="queue-head">
              <h2>Experiments</h2>
              <code className="small">{catalog.data.version}</code>
            </div>
            <div className="queue-body">
              <ol className="queue-list" onKeyDown={listKeys}>
                {catalog.data.scenarios.map((item, index) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      data-list-item
                      className={`queue-item tone-${toneFor(item.ground_truth.decision)} ${scenario?.id === item.id ? "selected" : ""}`}
                      aria-pressed={scenario?.id === item.id}
                      onClick={() => {
                        setSelectedId(item.id);
                        setError(null);
                      }}
                      disabled={running}
                    >
                      <span className="queue-item-top">
                        <strong>{scenarioName(item.name)}</strong>
                        <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                      </span>
                      <span className="queue-item-source">{item.summary}</span>
                    </button>
                  </li>
                ))}
              </ol>
              <p className="queue-foot">
                Expected outcomes are frozen ground truth, separate from observed production
                results.
              </p>
            </div>
          </aside>
          <section className="split-main stack-lg" aria-label="Scenario detail">
            {scenario ? (
              <>
                <header className="case-head">
                  <div className="case-title">
                    <h2>{scenarioName(scenario.name)}</h2>
                    <Badge>Synthetic</Badge>
                  </div>
                  <p className="case-source">
                    <span>{scenario.summary}</span>
                  </p>
                  <code className="small quiet">{scenario.id}</code>
                </header>
                {scenario.id === "unsafe-agent-output" && (
                  <Notice tone="review" icon={ShieldX}>
                    Validator fault injection: an unsafe recommendation is inserted after the native
                    investigation. This tests deterministic policy, not a claim that the model
                    produced that recommendation.
                  </Notice>
                )}

                <div className="run-bar">
                  <div>
                    <strong>{running ? "Request sent to IRIS" : "Ready for a native run"}</strong>
                    <p>
                      {running
                        ? "IRIS is investigating this event. Keep the run ID for a safe retry if the connection is interrupted."
                        : "Creates a persisted case through the IRIS Business Service. A live agent call may be made."}
                    </p>
                  </div>
                  <Button icon={Play} kind="primary" disabled={running} onClick={run}>
                    {running
                      ? "Waiting for IRIS…"
                      : retrying
                        ? "Retry same injection"
                        : "Inject into IRIS"}
                  </Button>
                </div>
                {running && <Loading>Waiting for the native investigation…</Loading>}
                {error !== null && <InlineError error={error} />}
                {runId && resultScenario === scenario.id && (
                  <div className="copy-row run-id">
                    <span className="kicker">Run ID</span>
                    <code>{runId}</code>
                    <CopyButton value={runId} label="Copy run ID" />
                  </div>
                )}

                <div className="expected">
                  <div>
                    <span className="kicker">Frozen expected decision</span>
                    <DecisionBadge value={scenario.ground_truth.decision} />
                  </div>
                  <p>{scenario.ground_truth.reason}</p>
                </div>

                {result && resultScenario === scenario.id && (
                  <section className="panel observed" aria-label="Observed native result">
                    <div className="section-head">
                      <div>
                        <h3>
                          Observed native result:{" "}
                          {result.policy ? humanize(result.policy.decision) : "Processing"}
                        </h3>
                      </div>
                      {result.policy && result.routing !== "PROCESSING" && (
                        <Badge tone={matches ? "allow" : "hold"}>
                          {matches ? (
                            <Check size={13} aria-hidden="true" />
                          ) : (
                            <CircleHelp size={13} aria-hidden="true" />
                          )}
                          {matches ? "Matches expectation" : "Differs from expectation"}
                        </Badge>
                      )}
                    </div>
                    <Metadata>
                      <MetaRow label="Case" mono>
                        {result.id}
                      </MetaRow>
                      <MetaRow label="Route">
                        <RouteMark routing={result.routing} />
                      </MetaRow>
                      <MetaRow label="Native trace" mono>
                        {result.trace_id === null ? "Not recorded" : result.trace_id}
                      </MetaRow>
                    </Metadata>
                    <Timeline item={result} />
                    {result.routing === "PROCESSING" && polled >= 30 && (
                      <Notice tone="review">
                        Automatic refresh paused. Open the investigation and refresh for the current
                        state.
                      </Notice>
                    )}
                    <div className="row-actions">
                      <Button icon={ArrowUpRight} onClick={() => inspectCase(result.id)}>
                        Inspect full investigation
                      </Button>
                    </div>
                  </section>
                )}

                <div className="two-col">
                  <JsonBlock value={scenario.message} title="Partner event to inject" />
                  <div className="stack">
                    <div className="section-head">
                      <div>
                        <h3>Independent references</h3>
                      </div>
                      <Badge>{scenario.references.length}</Badge>
                    </div>
                    <div className="disclosures">
                      {scenario.references.map((reference, index) => (
                        <details className="disclosure" key={index}>
                          <summary>
                            <span className="mono">
                              {display(reference.id ?? `Reference ${index + 1}`)}
                            </span>
                          </summary>
                          <JsonBlock value={reference} title={`Frozen reference ${index + 1}`} />
                        </details>
                      ))}
                    </div>
                    <Metadata>
                      <MetaRow label="Frozen evaluation clock" mono>
                        <time dateTime={catalog.data.clock}>{dateTime(catalog.data.clock)}</time>
                      </MetaRow>
                    </Metadata>
                    <p className="small quiet">
                      The server owns reference selection and execution. The browser cannot
                      substitute release evidence.
                    </p>
                  </div>
                </div>
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

const METRICS = [
  { key: "processed", label: "Messages processed", caption: "Persisted native records", tone: "muted" },
  { key: "contradictions", label: "Verified contradictions", caption: "Independent evidence disagrees", tone: "hold" },
  { key: "pending_reviews", label: "Pending reviews", caption: "Awaiting an authorized decision", tone: "review" },
  { key: "quarantined", label: "Quarantined transactions", caption: "Held from the destination", tone: "hold" },
] as const;

export function Overview({ refresh, health }: { refresh: number; health: Resource<Health> }) {
  const data = useApi("/api/overview", OverviewSchema, refresh);
  return (
    <>
      <PageHeading
        title="Overview"
        description="What arrived, what contradicted its agreement, and what was contained."
      >
        <a href="#scenarios" className="btn btn-primary">
          <Play size={15} aria-hidden="true" /> Run a scenario
        </a>
      </PageHeading>
      <div className="metrics">
        {METRICS.map(({ key, label, caption, tone }) => (
          <article className={`metric metric-${tone}`} key={key}>
            <span className="kicker">{label}</span>
            <strong className="mono">
              {data.data ? data.data[key].toLocaleString() : "Not observed"}
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
      <div className="overview-grid">
        <section className="panel">
          <div className="section-head">
            <div>
              <h2>Recent investigations</h2>
              <p>The latest cases returned by the native API.</p>
            </div>
            <a href="#investigations" className="link">
              View queue <ArrowRight size={13} aria-hidden="true" />
            </a>
          </div>
          {data.data ? (
            data.data.recent.length ? (
              <CaseTable cases={data.data.recent} />
            ) : (
              <EmptyState icon={Inbox} title="No investigations yet">
                Run a synthetic scenario or inject a partner event to begin.
              </EmptyState>
            )
          ) : data.loading ? (
            <Loading>Reading investigations…</Loading>
          ) : (
            <p className="quiet">Case history is unavailable while the native API is disconnected.</p>
          )}
        </section>
        <aside className="panel" aria-label="Production signal">
          <div className="section-head">
            <div>
              <h2>Production signal</h2>
              <p className="mono">{health.data?.production.name ?? "InterSystems IRIS"}</p>
            </div>
          </div>
          <Metadata>
            <MetaRow label="Production">
              {health.data ? (
                <Badge tone={health.data.production.running ? "allow" : "review"}>
                  {health.data.production.running ? "Running" : "Not running"}
                </Badge>
              ) : (
                "Not observed"
              )}
            </MetaRow>
            <MetaRow label="Agent configured">
              {health.data ? (health.data.agent.configured ? "Yes" : "No") : "Not observed"}
            </MetaRow>
            <MetaRow label="Last native success">
              {health.data ? dateTime(health.data.agent.last_success_at) : "Not observed"}
            </MetaRow>
          </Metadata>
          <a href="#health" className="btn btn-secondary">
            Inspect health <ArrowRight size={14} aria-hidden="true" />
          </a>
        </aside>
      </div>
      <section className="panel principle">
        <div className="section-head">
          <div>
            <h2>How SilentShift works</h2>
            <p>A recommendation is evidence to evaluate. It is never permission to deliver.</p>
          </div>
        </div>
        <NativePath observed={Boolean(health.data)} />
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
      wide
      title="Inject a partner event"
      description="Submit original JSON through the authenticated IRIS Business Service. The native server retrieves reference evidence and controls routing."
      onClose={onClose}
    >
      <form
        className="form"
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          setBusy(true);
          setError(null);
          try {
            let parsed: unknown;
            try {
              parsed = JSON.parse(payload);
            } catch {
              throw new Error("Enter valid JSON. The payload could not be parsed.");
            }
            if (!JsonObject.safeParse(parsed).success)
              throw new Error("The message must be a JSON object.");
            onComplete(await request("/api/messages", CaseSchema, { rawBody: payload }));
          } catch (failure) {
            setError(failure);
          } finally {
            setBusy(false);
          }
        }}
      >
        <label htmlFor="message-json" className="label">
          Original message JSON
        </label>
        <textarea
          className="code-input"
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
        <p className="hint">
          Keep the event ID unchanged when retrying. A reused ID with changed content must be
          rejected by the server.
        </p>
        {error !== null && <InlineError error={error} />}
        <div className="dialog-actions">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" kind="primary" icon={Plus} disabled={busy || !payload.trim()}>
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
        .includes(query.toLowerCase().trim()),
    ) ?? [];
  const item = items.find((record) => record.id === selected) ?? items[0];
  return (
    <>
      <PageHeading
        title="Message Explorer"
        description="Inspect the original payload, reference snapshot and semantic differences."
      >
        <Button kind="primary" icon={Plus} onClick={() => setShowSubmit(true)}>
          Inject message
        </Button>
      </PageHeading>
      {!cases.data ? (
        <section className="panel">
          <ResourceState resource={cases} />
        </section>
      ) : !cases.data.items.length ? (
        <section className="panel">
          <EmptyState icon={FileJson2} title="No messages received">
            The native production has not returned any message records. Inject an event or choose
            a synthetic scenario.
          </EmptyState>
        </section>
      ) : (
        <div className="stack-lg">
          <div className="toolbar">
            <label className="search">
              <FileJson2 size={14} aria-hidden="true" />
              <span className="sr-only">Search messages</span>
              <input
                type="search"
                placeholder="Search event, source or case ID"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <select
              value={item?.id ?? ""}
              onChange={(event) => setSelected(event.target.value)}
              aria-label="Select message"
              disabled={!items.length}
            >
              {items.map((record) => (
                <option value={record.id} key={record.id}>
                  {record.event_id} · {record.source}
                </option>
              ))}
            </select>
            <span className="small quiet">
              {items.length} of {cases.data.total} records, limit {cases.data.limit}
            </span>
          </div>
          {item ? (
            <>
              <section className="panel">
                <div className="section-head">
                  <div>
                    <span className="kicker">Original payload</span>
                    <h2 className="mono">{item.event_id}</h2>
                  </div>
                  <Button icon={ArrowUpRight} onClick={() => inspectCase(item.id)}>
                    Open investigation
                  </Button>
                </div>
                <div className="two-col">
                  <JsonBlock value={item.message} title="Partner message" />
                  <JsonBlock value={item.references} title="Independent reference snapshot" />
                </div>
              </section>
              <CaseDetail item={item} key={item.id} />
            </>
          ) : (
            <EmptyState title="No messages match this search">
              Try another event ID or source.
            </EmptyState>
          )}
        </div>
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

function usageSummary(value: unknown): string {
  if (!value || typeof value !== "object" || Array.isArray(value)) return "Not collected";
  const counters = Object.values(value).filter(
    (entry): entry is Record<string, unknown> =>
      Boolean(entry) && typeof entry === "object" && !Array.isArray(entry),
  );
  const recorded = counters.filter(
    (counter) => typeof counter.value === "number" && Number.isFinite(counter.value),
  );
  if (!recorded.length) return "Not collected";
  const observations = recorded.filter(
    (counter) =>
      typeof counter.observed_records === "number" && typeof counter.total_records === "number",
  );
  const coverage = observations.length
    ? `, ${Math.min(...observations.map((counter) => counter.observed_records as number))}/${Math.max(...observations.map((counter) => counter.total_records as number))} records observed`
    : "";
  return `${recorded.length} counter${recorded.length === 1 ? "" : "s"} recorded${coverage}`;
}

const percent = (value: number | null) =>
  value === null ? "Not measured" : `${(value * 100).toFixed(1)}%`;

export function Evaluations({ refresh }: { refresh: number }) {
  const data = useApi("/api/evaluations", EvaluationsSchema, refresh);
  return (
    <>
      <PageHeading
        title="Evaluations"
        description="Compare deterministic rules, native recommendations and policy-constrained outcomes."
      >
        <Badge>
          <FlaskConical size={13} aria-hidden="true" /> Actual runs only
        </Badge>
      </PageHeading>
      <ol className="native-path compact" aria-label="Evaluation stages">
        <li>
          <span className="mono">01</span>
          <strong>Rule-only baseline</strong>
          <small>Independent deterministic assessment before the agent.</small>
        </li>
        <li>
          <span className="mono">02</span>
          <strong>AI-assisted investigation</strong>
          <small>The structured native recommendation and its evidence.</small>
        </li>
        <li>
          <span className="mono">03</span>
          <strong>Policy-constrained result</strong>
          <small>The final permitted route, checked against frozen ground truth.</small>
        </li>
      </ol>
      {!data.data ? (
        <section className="panel">
          <ResourceState resource={data} />
        </section>
      ) : !data.data.items.length ? (
        <section className="panel">
          <EmptyState icon={FlaskConical} title="No measured runs recorded">
            Execute the versioned evaluation against the native production, then refresh. Accuracy,
            safety, latency and usage stay unavailable until actual run records exist.
          </EmptyState>
          <dl className="meta meta-grid">
            {[
              "Correct / total",
              "False quarantine rate",
              "Unsafe releases",
              "Review rate",
              "Latency",
              "Model usage / cost",
            ].map((label) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd className="mono quiet">Not measured</dd>
              </div>
            ))}
          </dl>
        </section>
      ) : (
        <div className="stack-lg">
          {data.data.items.map((run) => (
            <section className="panel" key={run.id} aria-label={`Evaluation ${run.id}`}>
              <div className="section-head">
                <div>
                  <span className="kicker">Recorded evaluation on {dateTime(run.created_at)}</span>
                  <h2 className="mono break">{run.id}</h2>
                  <p>
                    <Badge>{run.dataset_version}</Badge> {run.native.accepted_records} /{" "}
                    {run.native.expected_cases} native records accepted
                  </p>
                </div>
                <Badge tone={run.native.passed ? "allow" : "review"}>
                  {humanize(run.native.status)}
                </Badge>
              </div>
              <div className="metrics">
                {(
                  [
                    ["Native proposal accuracy", run.native.proposal_accuracy],
                    ["Final decision accuracy", run.native.final_accuracy],
                    ["False quarantine rate", run.native.false_quarantine_rate],
                    ["Review rate", run.native.review_rate],
                  ] as const
                ).map(([label, metric]) => (
                  <article className="metric" key={label}>
                    <span className="kicker">{label}</span>
                    <strong className="mono">{percent(metric.value)}</strong>
                    <p className="mono">
                      {metric.numerator} / {metric.denominator}
                    </p>
                  </article>
                ))}
                <article
                  className={`metric ${run.native.unsafe_release.count === null ? "" : run.native.unsafe_release.count > 0 ? "metric-hold" : "metric-allow"}`}
                >
                  <span className="kicker">Unsafe releases</span>
                  <strong className="mono">
                    {run.native.unsafe_release.count ?? "Not measured"}
                  </strong>
                  <p className="mono">of {run.native.unsafe_release.denominator} cases</p>
                </article>
                <article className="metric">
                  <span className="kicker">Native latency</span>
                  <strong className="mono">
                    {run.native.latency.mean_ms === null
                      ? "Not measured"
                      : `${run.native.latency.mean_ms.toFixed(0)} ms`}
                  </strong>
                  <p className="mono">
                    p95{" "}
                    {run.native.latency.p95_ms === null
                      ? "unavailable"
                      : `${run.native.latency.p95_ms.toFixed(0)} ms`}{" "}
                    · {run.native.latency.observed_records}/{run.native.latency.total_records}{" "}
                    observed
                  </p>
                </article>
              </div>
              {run.native.issues.length > 0 && (
                <JsonBlock value={run.native.issues} title="Evaluation issues" />
              )}
              <Metadata>
                <MetaRow label="Model usage">{usageSummary(run.native.model_usage)}</MetaRow>
                <MetaRow label="Model cost">
                  {run.native.model_cost === null || run.native.model_cost === undefined
                    ? "Not recorded"
                    : display(run.native.model_cost)}
                </MetaRow>
              </Metadata>
              <details className="disclosure plain">
                <summary>Inspect all comparisons, case IDs and measurement evidence</summary>
                <JsonBlock value={run} title="Measured evaluation record" />
              </details>
              <p className="small quiet">
                Only server-recorded values are shown. Missing denominators, usage and cost are not
                inferred.
              </p>
            </section>
          ))}
        </div>
      )}
      <Notice icon={CircleHelp}>
        Five synthetic scenarios demonstrate specific behavior. Their results do not establish
        general accuracy on real business traffic.
      </Notice>
    </>
  );
}

export function Policies({ refresh }: { refresh: number }) {
  const data = useApi("/api/policies", PoliciesSchema, refresh);
  return (
    <>
      <PageHeading
        title="Policies"
        description="The agent recommends. Deterministic policy decides which actions are permitted."
      >
        {data.data && <Badge tone="allow">{data.data.version}</Badge>}
      </PageHeading>
      <section className="boundary" aria-label="Explicit trust boundary">
        <ol>
          <li>
            <span className="kicker">Recommends</span>
            <strong>AI Hub agent</strong>
          </li>
          <li aria-hidden="true">
            <ArrowRight size={16} />
          </li>
          <li>
            <span className="kicker">Decides</span>
            <strong>Deterministic policy</strong>
          </li>
          <li aria-hidden="true">
            <ArrowRight size={16} />
          </li>
          <li>
            <span className="kicker">Records</span>
            <strong>Route and checks</strong>
          </li>
        </ol>
        <p>
          Agent reasoning remains a recommendation. Inspect the policy version and checks returned
          by IRIS. Every case records the checks that permitted or denied its route.
        </p>
      </section>
      {!data.data ? (
        <section className="panel">
          <ResourceState resource={data} />
        </section>
      ) : (
        <section className="panel">
          <div className="section-head">
            <div>
              <h2>Configured safety rules</h2>
              <p>Server-reported policy · {data.data.version}</p>
            </div>
            <Badge>{data.data.rules.length} rules</Badge>
          </div>
          {data.data.rules.length ? (
            <ol className="rules">
              {data.data.rules.map((rule, index) => (
                <li key={rule.id}>
                  <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                  <div>
                    <code>{rule.id}</code>
                    <p>{rule.description}</p>
                    {Object.keys(rule).some((key) => !["id", "description"].includes(key)) && (
                      <details className="disclosure plain">
                        <summary>Rule configuration</summary>
                        <JsonBlock value={rule} title={`${rule.id} configuration`} />
                      </details>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyState title="No policy rules returned">
              This API response does not establish an enforced policy configuration.
            </EmptyState>
          )}
        </section>
      )}
      <Notice tone="review" icon={KeyRound}>
        Reviewer actions require server authorization, a recorded reason, a current case version
        and an idempotency key. Critical contradictions require corrected evidence and a new
        investigation.
      </Notice>
    </>
  );
}

export function SystemHealth({ health }: { health: Resource<Health> }) {
  const { openConnect } = useActions();
  return (
    <>
      <PageHeading
        title="System Health"
        description="Observe the runtime. Configured access is not proof of execution."
      >
        <Button icon={KeyRound} onClick={openConnect}>
          IRIS session
        </Button>
      </PageHeading>
      <div className="metrics three">
        <article
          className={`metric ${health.data ? (health.data.production.running ? "metric-allow" : "metric-review") : ""}`}
        >
          <span className="kicker">Native production</span>
          <strong>
            {health.data
              ? health.data.production.running
                ? "Running"
                : "Not running"
              : health.loading
                ? "Checking…"
                : "Not observed"}
          </strong>
          <p className="mono">{health.data?.production.name ?? "Awaiting a native API response"}</p>
          {health.data && <p className="small">Server-reported status</p>}
        </article>
        <article className="metric">
          <span className="kicker">Agent configuration</span>
          <strong>
            {health.data
              ? health.data.agent.configured
                ? "Configured"
                : "Not configured"
              : "Not observed"}
          </strong>
          <p>Configuration does not prove a model invocation.</p>
          {health.data && (
            <p className="small">
              Last native success: {dateTime(health.data.agent.last_success_at)}
            </p>
          )}
        </article>
        <article className="metric">
          <span className="kicker">Reported runtime build</span>
          <strong className="mono">{health.data?.build ?? "Unavailable"}</strong>
          <p>
            Required: <code>2026.3.0AI.154.0</code> Community · AI Hub Early Access
          </p>
        </article>
      </div>
      {health.error && <ErrorState error={health.error} />}
      {health.data ? (
        <section className="panel">
          <div className="section-head">
            <div>
              <h2>Production components</h2>
              <p>Statuses returned by the actual native API.</p>
            </div>
            <Badge>{health.data.components.length} components</Badge>
          </div>
          {health.data.components.length ? (
            <div className="table-wrap" role="region" aria-label="Production components" tabIndex={0}>
              <table className="table">
                <thead>
                  <tr>
                    <th scope="col">Component</th>
                    <th scope="col">Reported status</th>
                  </tr>
                </thead>
                <tbody>
                  {health.data.components.map((component) => (
                    <tr key={component.name}>
                      <td className="mono">{component.name}</td>
                      <td>
                        <Badge tone={toneFor(component.status)}>{component.status}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="No component statuses returned">
              The health response does not include individual component observations.
            </EmptyState>
          )}
          <details className="disclosure plain">
            <summary>Inspect full health response</summary>
            <JsonBlock value={health.data} title="Native health response" />
          </details>
        </section>
      ) : (
        <section className="panel">
          <div className="section-head">
            <div>
              <h2>Native production connection</h2>
              <p>
                The workbench needs a running build 154 production. It contains no mock operational
                backend.
              </p>
            </div>
          </div>
          <ol className="rules">
            <li>
              <span className="mono">01</span>
              <div>
                <strong>Load the official Community image</strong>
                <p>
                  Download the ARM64 or x64 build 154 from the AI Hub Early Access portal, then load
                  and retag it locally.
                </p>
                <a
                  className="link"
                  href="https://evaluation.intersystems.com/Eval/early-access/AIHub"
                  target="_blank"
                  rel="noreferrer"
                >
                  Open EAP portal <ArrowUpRight size={13} aria-hidden="true" />
                </a>
              </div>
            </li>
            <li>
              <span className="mono">02</span>
              <div>
                <strong>Start the native stack</strong>
                <p>
                  Follow the repository setup to compile the production and start its Web Gateway.
                  No EAP binary is bundled here.
                </p>
                <div className="command">
                  <Terminal size={14} aria-hidden="true" />
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
                <strong>Connect an IRIS account</strong>
                <p>
                  Use a viewer account for records and scenario ingestion. Reviewer actions need an
                  additional server permission.
                </p>
                <Button icon={KeyRound} onClick={openConnect}>
                  Connect to IRIS
                </Button>
              </div>
            </li>
          </ol>
          <p className="small quiet">
            <code>IRIS_API_ORIGIN</code>: the Vite development proxy forwards same-origin API
            requests to the configured IRIS Web Gateway. Credentials stay in this tab's memory.
          </p>
        </section>
      )}
      <p className="small quiet foot-note">
        {health.checkedAt
          ? `Last API check: ${dateTime(health.checkedAt.toISOString())}`
          : "No API check completed"}
        {" · "}Health checks do not invoke the agent.
      </p>
    </>
  );
}
