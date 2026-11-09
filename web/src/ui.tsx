import {
  createContext,
  useContext,
  useEffect,
  useId,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import {
  AlertCircle,
  ArrowRight,
  Check,
  Copy,
  ExternalLink,
  Info,
  KeyRound,
  Unplug,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ApiError, Resource } from "./api";
import type { Investigation } from "./schema";

export const AppContext = createContext({
  refresh: () => {},
  openConnect: () => {},
  inspectCase: (_id: string) => {},
  notify: (_message: string) => {},
});
export const useActions = () => useContext(AppContext);

export type Tone = "hold" | "allow" | "review" | "agent" | "accent" | "muted";

export function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/^./, (letter) => letter.toUpperCase());
}
export function display(value: unknown): string {
  if (value === null) return "null";
  if (value === undefined) return "Not provided";
  return typeof value === "string" ? value : JSON.stringify(value);
}
export function dateTime(value: string | null | undefined) {
  if (!value) return "Not recorded";
  const date = new Date(value);
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat("en", {
        dateStyle: "medium",
        timeStyle: "medium",
      }).format(date);
}
export function shortTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return value;
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
export function toneFor(value: string): Tone {
  if (
    ["ALLOW", "DELIVERED", "CLEAR", "LEGITIMATE_CHANGE", "running", "ready"].includes(value)
  )
    return "allow";
  if (
    [
      "QUARANTINE",
      "QUARANTINED",
      "REJECTED",
      "VERIFIED_CONTRADICTION",
      "INVALID_MESSAGE",
      "critical",
    ].includes(value)
  )
    return "hold";
  if (
    ["REQUEST_REVIEW", "REVIEW", "SUSPICIOUS", "INSUFFICIENT_EVIDENCE", "warning"].includes(value)
  )
    return "review";
  return "muted";
}

export function Badge({
  children,
  tone = "muted",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return <span className={`tag tag-${tone}`}>{children}</span>;
}
export function DecisionBadge({ value }: { value: string }) {
  return <Badge tone={toneFor(value)}>{humanize(value)}</Badge>;
}

export function PageHeading({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <header className="page-head">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children && <div className="page-head-actions">{children}</div>}
    </header>
  );
}

export function Button({
  children,
  icon: Icon,
  kind = "secondary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: LucideIcon;
  kind?: "primary" | "secondary" | "ghost" | "danger";
}) {
  return (
    <button
      type={props.type ?? "button"}
      className={`btn btn-${kind} ${className}`}
      {...props}
    >
      {Icon && <Icon size={15} aria-hidden="true" />}
      {children}
    </button>
  );
}

export function CopyButton({
  value,
  label = "Copy",
}: {
  value: string;
  label?: string;
}) {
  const [copied, setCopied] = useState(false);
  const { notify } = useActions();
  useEffect(() => {
    if (!copied) return;
    const timeout = window.setTimeout(() => setCopied(false), 1800);
    return () => window.clearTimeout(timeout);
  }, [copied]);
  return (
    <button
      className="icon-btn"
      type="button"
      aria-label={copied ? "Copied" : label}
      title={copied ? "Copied" : label}
      onClick={() => {
        if (!navigator.clipboard) {
          notify("Clipboard access is unavailable. Select the text and copy it manually.");
          return;
        }
        navigator.clipboard
          .writeText(value)
          .then(() => setCopied(true))
          .catch(() => notify("Copy failed. Select the text and copy it manually."));
      }}
    >
      {copied ? <Check size={14} aria-hidden="true" /> : <Copy size={14} aria-hidden="true" />}
    </button>
  );
}

export function JsonBlock({ value, title }: { value: unknown; title: string }) {
  const content = JSON.stringify(value, null, 2) ?? "null";
  return (
    <div className="json">
      <div className="json-head">
        <span>{title}</span>
        <CopyButton value={content} label={`Copy ${title}`} />
      </div>
      <pre tabIndex={0} aria-label={title}>
        <code>{content}</code>
      </pre>
    </div>
  );
}

export function Loading({ children }: { children: ReactNode }) {
  return (
    <div className="state state-loading" role="status">
      <span className="pulse" aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}

export function EmptyState({
  icon: Icon = Info,
  title,
  children,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="state">
      <Icon size={22} strokeWidth={1.5} aria-hidden="true" />
      <h3>{title}</h3>
      <p>{children}</p>
      {action && <div className="state-action">{action}</div>}
    </div>
  );
}

export function ErrorState({
  error,
  compact = false,
}: {
  error: ApiError;
  compact?: boolean;
}) {
  const { refresh, openConnect } = useActions();
  const locked = error.status === 401 || error.status === 403;
  const forbidden = error.status === 403;
  return (
    <div className={`error-card ${compact ? "compact" : ""}`} role="alert">
      {locked ? <KeyRound size={20} aria-hidden="true" /> : <Unplug size={20} aria-hidden="true" />}
      <div>
        <h3>
          {forbidden
            ? "Your role cannot open this view"
            : locked
              ? "Connect your IRIS session"
              : ["API_SCHEMA_MISMATCH", "INVALID_API_RESPONSE"].includes(error.code)
                ? "API contract needs attention"
                : "Native runtime unavailable"}
        </h3>
        <p>{error.message}</p>
        <code className="error-code">{error.code}</code>
        <div className="row-actions">
          <Button onClick={locked ? openConnect : refresh} icon={locked ? KeyRound : ArrowRight}>
            {forbidden ? "Switch IRIS account" : locked ? "Connect to IRIS" : "Try again"}
          </Button>
          {!compact && (
            <a className="link" href="#health">
              Inspect system health <ArrowRight size={13} aria-hidden="true" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

export function ResourceState<T>({
  resource,
  emptyTitle,
  emptyDescription,
}: {
  resource: Resource<T>;
  emptyTitle?: string;
  emptyDescription?: string;
}) {
  if (resource.loading) return <Loading>Reading native IRIS records…</Loading>;
  if (resource.error) return <ErrorState error={resource.error} />;
  return (
    <EmptyState title={emptyTitle ?? "No records yet"}>
      {emptyDescription ??
        "Records appear here after the native production has processed an event."}
    </EmptyState>
  );
}

export function Metadata({ children }: { children: ReactNode }) {
  return <dl className="meta">{children}</dl>;
}
export function MetaRow({
  label,
  children,
  mono = false,
}: {
  label: string;
  children: ReactNode;
  mono?: boolean;
}) {
  return (
    <div>
      <dt>{label}</dt>
      <dd className={mono ? "mono" : undefined}>{children}</dd>
    </div>
  );
}

const PATH = [
  { name: "Receive", detail: "Business Service keeps the original payload" },
  { name: "Investigate", detail: "Native AI Hub reads scoped evidence" },
  { name: "Authorize", detail: "Deterministic policy decides the route" },
  { name: "Preserve", detail: "Outcome, receipt and trace are persisted" },
];
export function NativePath({ observed = false }: { observed?: boolean }) {
  return (
    <ol
      className="native-path"
      aria-label={
        observed
          ? "Application processing stages"
          : "Required native processing stages, not yet observed"
      }
    >
      {PATH.map(({ name, detail }, index) => (
        <li key={name}>
          <span className="mono">{String(index + 1).padStart(2, "0")}</span>
          <strong>{name}</strong>
          <small>{detail}</small>
        </li>
      ))}
    </ol>
  );
}

export function RouteMark({ routing }: { routing: string }) {
  return (
    <span className={`route route-${toneFor(routing)}`}>
      <span aria-hidden="true" />
      {humanize(routing)}
    </span>
  );
}

export function CaseTable({ cases }: { cases: Investigation[] }) {
  return (
    <div className="table-wrap" role="region" aria-label="Recent investigations" tabIndex={0}>
      <table className="table">
        <thead>
          <tr>
            <th scope="col">Event / source</th>
            <th scope="col">Classification</th>
            <th scope="col">Policy</th>
            <th scope="col">Route</th>
            <th scope="col">Received</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((item) => (
            <tr key={item.id}>
              <td>
                <a
                  className="link mono"
                  href={`#investigations/${encodeURIComponent(item.id)}`}
                  aria-label={`Open investigation ${item.event_id}`}
                >
                  {item.event_id}
                </a>
                <small>{item.source}</small>
              </td>
              <td>
                {item.assessment ? humanize(item.assessment.classification) : "Awaiting assessment"}
              </td>
              <td>
                {item.policy ? (
                  <DecisionBadge value={item.policy.decision} />
                ) : (
                  <span className="quiet">Pending</span>
                )}
              </td>
              <td>
                <RouteMark routing={item.routing} />
              </td>
              <td className="mono nowrap">{shortTime(item.received_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Modal({
  title,
  description,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  description: string;
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const id = useId();
  useEffect(() => {
    const previous =
      document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusable = () => [
      ...(ref.current?.querySelectorAll<HTMLElement>(
        'button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href], [tabindex="0"]',
      ) ?? []),
    ];
    (
      ref.current?.querySelector<HTMLElement>("[data-autofocus]:not(:disabled)") ??
      focusable()[0] ??
      ref.current
    )?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
      }
      if (event.key === "Tab") {
        const items = focusable();
        const first = items[0];
        const last = items[items.length - 1];
        if (!items.length) {
          event.preventDefault();
          ref.current?.focus();
        } else if (
          event.shiftKey &&
          (document.activeElement === first || !ref.current?.contains(document.activeElement))
        ) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", keydown);
    return () => {
      document.removeEventListener("keydown", keydown);
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, [onClose]);
  return (
    <div
      className="scrim"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        className={`dialog ${wide ? "dialog-wide" : ""}`}
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${id}-title`}
        aria-describedby={`${id}-description`}
        tabIndex={-1}
      >
        <div className="dialog-head">
          <h2 id={`${id}-title`}>{title}</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Close dialog">
            <X size={17} aria-hidden="true" />
          </button>
        </div>
        <p id={`${id}-description`} className="dialog-description">
          {description}
        </p>
        {children}
      </div>
    </div>
  );
}

export function InlineError({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : "The action could not be completed.";
  return (
    <div className="inline-error" role="alert">
      <AlertCircle size={16} aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

export function TraceLink({ item }: { item: Investigation }) {
  const safe =
    item.trace_url &&
    (/^\/(?!\/)/.test(item.trace_url) || /^https?:\/\//.test(item.trace_url));
  const recorded = item.trace_id !== null && String(item.trace_id).trim() !== "";
  return (
    <div className="trace">
      <span className="kicker">Native trace</span>
      {recorded ? (
        <>
          <div className="copy-row">
            <code>{item.trace_id}</code>
            <CopyButton value={String(item.trace_id)} label="Copy native trace ID" />
          </div>
          {safe ? (
            <a className="link" href={item.trace_url} target="_blank" rel="noreferrer">
              Open IRIS Visual Trace <ExternalLink size={13} aria-hidden="true" />
            </a>
          ) : (
            <p className="quiet small">Find this session ID in the IRIS Message Viewer.</p>
          )}
        </>
      ) : (
        <p className="quiet small">A native trace ID has not been recorded.</p>
      )}
    </div>
  );
}

export function Notice({
  children,
  tone = "accent",
  icon: Icon = Info,
}: {
  children: ReactNode;
  tone?: Tone;
  icon?: LucideIcon;
}) {
  return (
    <div className={`notice notice-${tone}`}>
      <Icon size={16} aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
}
