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
  CheckCircle2,
  Copy,
  Database,
  ExternalLink,
  Fingerprint,
  KeyRound,
  Layers3,
  ShieldCheck,
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
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
export function toneFor(value: string): string {
  if (
    [
      "ALLOW",
      "DELIVERED",
      "CLEAR",
      "LEGITIMATE_CHANGE",
      "running",
      "ready",
    ].includes(value)
  )
    return "mint";
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
    return "coral";
  if (
    [
      "REQUEST_REVIEW",
      "REVIEW",
      "SUSPICIOUS",
      "INSUFFICIENT_EVIDENCE",
      "warning",
    ].includes(value)
  )
    return "amber";
  return "muted";
}
export function Badge({
  children,
  tone = "muted",
  dot = false,
}: {
  children: ReactNode;
  tone?: string;
  dot?: boolean;
}) {
  return (
    <span className={`badge ${tone}`}>
      {dot && <span className="status-dot" aria-hidden="true" />}
      {children}
    </span>
  );
}
export function DecisionBadge({ value }: { value: string }) {
  return <Badge tone={toneFor(value)}>{humanize(value)}</Badge>;
}

export function PageHeading({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <header className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children && <div className="heading-actions">{children}</div>}
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
    <button className={`button ${kind} ${className}`} {...props}>
      {Icon && <Icon size={16} aria-hidden="true" />}
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
    if (copied) {
      const timeout = window.setTimeout(() => setCopied(false), 1800);
      return () => window.clearTimeout(timeout);
    }
  }, [copied]);
  return (
    <button
      className="icon-button copy-button"
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
          .catch(() =>
            notify("Copy failed. Select the text and copy it manually."),
          );
      }}
    >
      {copied ? (
        <Check size={15} aria-hidden="true" />
      ) : (
        <Copy size={15} aria-hidden="true" />
      )}
    </button>
  );
}

export function JsonBlock({
  value,
  title,
  compact = false,
}: {
  value: unknown;
  title: string;
  compact?: boolean;
}) {
  const content = JSON.stringify(value, null, 2) ?? "null";
  return (
    <div className={`json-block ${compact ? "compact" : ""}`}>
      <div className="json-heading">
        <span>{title}</span>
        <CopyButton value={content} label={`Copy ${title}`} />
      </div>
      <pre tabIndex={0} aria-label={title}>
        <code>{content}</code>
      </pre>
    </div>
  );
}

export function EmptyState({
  icon: Icon = Layers3,
  title,
  children,
  action,
  compact = false,
}: {
  icon?: LucideIcon;
  title: string;
  children: ReactNode;
  action?: ReactNode;
  compact?: boolean;
}) {
  return (
    <div className={`empty-state ${compact ? "compact" : ""}`}>
      <div className="empty-icon">
        <Icon size={24} strokeWidth={1.5} aria-hidden="true" />
      </div>
      <h3>{title}</h3>
      <p>{children}</p>
      {action && <div className="empty-action">{action}</div>}
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
  return (
    <div className={`error-state ${compact ? "compact" : ""}`} role="alert">
      <div className="error-symbol">
        {locked ? <KeyRound size={21} /> : <Unplug size={21} />}
      </div>
      <div>
        <h3>
          {locked
            ? "Connect your IRIS session"
            : ["API_SCHEMA_MISMATCH", "INVALID_API_RESPONSE"].includes(error.code)
              ? "API contract needs attention"
              : "Native runtime unavailable"}
        </h3>
        <p>{error.message}</p>
        <span className="error-code mono">{error.code}</span>
        <div className="error-actions">
          <Button
            onClick={locked ? openConnect : refresh}
            icon={locked ? KeyRound : ArrowRight}
          >
            {locked ? "Connect to IRIS" : "Try again"}
          </Button>
          {!compact && (
            <a className="text-link" href="#health">
              Inspect system health <ArrowRight size={14} />
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
  if (resource.loading)
    return (
      <div className="loading-state" role="status">
        <div className="loading-mark">
          <Database size={22} />
        </div>
        <span>Reading native IRIS records…</span>
        <small>No local operational data is substituted.</small>
      </div>
    );
  if (resource.error) return <ErrorState error={resource.error} />;
  return (
    <EmptyState title={emptyTitle ?? "No records yet"}>
      {emptyDescription ??
        "Records appear here after the native production has processed an event."}
    </EmptyState>
  );
}

export function Metadata({ children }: { children: ReactNode }) {
  return <dl className="metadata">{children}</dl>;
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

export function NativePath({ observed = false }: { observed?: boolean }) {
  const steps = [
    { icon: Database, name: "Receive", detail: "Business Service" },
    { icon: Layers3, name: "Investigate", detail: "Native AI Hub" },
    { icon: ShieldCheck, name: "Authorize", detail: "Deterministic policy" },
    { icon: Fingerprint, name: "Preserve", detail: "Evidence & route" },
  ];
  return (
    <div
      className="native-path"
      aria-label={
        observed
          ? "Application processing stages"
          : "Required native processing stages, not yet observed"
      }
    >
      {steps.map(({ icon: Icon, name, detail }, index) => (
        <div className="path-step" key={name}>
          <div className="path-line">
            <span className="path-node">
              <Icon size={18} strokeWidth={1.5} />
            </span>
            {index < steps.length - 1 && <span className="path-connector" />}
          </div>
          <strong>{name}</strong>
          <small>{detail}</small>
        </div>
      ))}
    </div>
  );
}

export function CaseTable({ cases }: { cases: Investigation[] }) {
  const { inspectCase } = useActions();
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th>Event / source</th>
            <th>Classification</th>
            <th>Policy</th>
            <th>Route</th>
            <th>Received</th>
            <th>
              <span className="sr-only">Open case</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {cases.map((item) => (
            <tr key={item.id}>
              <td>
                <button
                  className="table-link mono"
                  onClick={() => inspectCase(item.id)}
                >
                  {item.event_id}
                </button>
                <small>{item.source}</small>
              </td>
              <td>
                {item.assessment
                  ? humanize(item.assessment.classification)
                  : "Awaiting assessment"}
              </td>
              <td>
                {item.policy ? (
                  <DecisionBadge value={item.policy.decision} />
                ) : (
                  <span className="subtle">Pending</span>
                )}
              </td>
              <td>
                <span className={`route-label ${toneFor(item.routing)}`}>
                  {humanize(item.routing)}
                </span>
              </td>
              <td className="mono small">{shortTime(item.received_at)}</td>
              <td>
                <button
                  className="icon-button"
                  aria-label={`Open investigation ${item.event_id}`}
                  onClick={() => inspectCase(item.id)}
                >
                  <ArrowRight size={16} />
                </button>
              </td>
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
}: {
  title: string;
  description: string;
  children: ReactNode;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const id = useId();
  useEffect(() => {
    const previous =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusable = () => [
      ...(ref.current?.querySelectorAll<HTMLElement>(
        'button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href], [tabindex="0"]',
      ) ?? []),
    ];
    (
      ref.current?.querySelector<HTMLElement>("[data-autofocus]") ??
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
          (document.activeElement === first ||
            !ref.current?.contains(document.activeElement))
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
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        className="modal"
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${id}-title`}
        aria-describedby={`${id}-description`}
        tabIndex={-1}
      >
        <div className="modal-header">
          <div className="modal-symbol">
            <ShieldCheck size={22} />
          </div>
          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>
        <h2 id={`${id}-title`}>{title}</h2>
        <p id={`${id}-description`} className="modal-description">
          {description}
        </p>
        {children}
      </div>
    </div>
  );
}

export function InlineError({ error }: { error: unknown }) {
  const message =
    error instanceof Error
      ? error.message
      : "The action could not be completed.";
  return (
    <div className="inline-error" role="alert">
      <AlertCircle size={17} />
      <span>{message}</span>
    </div>
  );
}

export function TraceLink({ item }: { item: Investigation }) {
  const safe =
    item.trace_url &&
    (/^\/(?!\/)/.test(item.trace_url) || /^https?:\/\//.test(item.trace_url));
  return (
    <div className="trace-box">
      <div className="section-kicker">
        <Fingerprint size={14} /> Native trace
      </div>
      {item.trace_id !== null && String(item.trace_id).trim() !== "" ? (
        <>
          <div className="copy-row">
            <code>{item.trace_id}</code>
            <CopyButton
              value={String(item.trace_id)}
              label="Copy native trace ID"
            />
          </div>
          {safe ? (
            <a
              className="text-link"
              href={item.trace_url}
              target="_blank"
              rel="noreferrer"
            >
              Open IRIS Visual Trace <ExternalLink size={13} />
            </a>
          ) : (
            <p className="small subtle">
              Find this session ID in the IRIS Message Viewer.
            </p>
          )}
        </>
      ) : (
        <p className="small subtle">A native trace ID has not been recorded.</p>
      )}
    </div>
  );
}

export function Notice({
  children,
  tone = "blue",
  icon: Icon = CheckCircle2,
}: {
  children: ReactNode;
  tone?: string;
  icon?: LucideIcon;
}) {
  return (
    <div className={`notice ${tone}`}>
      <Icon size={17} aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
}
