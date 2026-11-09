import { useCallback, useEffect, useState } from "react";
import {
  ArrowUpRight,
  KeyRound,
  LockKeyhole,
  Menu,
  RefreshCw,
  Search,
  X,
} from "lucide-react";
import { clearCredentials, request, setCredentials, useApi } from "./api";
import { HealthSchema } from "./schema";
import Investigations, { ReviewPermissionContext } from "./Investigations";
import {
  Evaluations,
  Messages,
  Overview,
  Policies,
  ScenarioLab,
  SystemHealth,
} from "./Views";
import { AppContext, Badge, Button, InlineError, Modal } from "./ui";
import Landing from "./Landing";
import Reviews from "./Reviews";
import CSVImport, { useCSVImport } from "./CSVImport";

const views = [
  "investigations",
  "reviews",
  "scenarios",
  "overview",
  "messages",
  "imports",
  "evaluations",
  "policies",
  "health",
] as const;
type View = (typeof views)[number];
type Group = "Workspace" | "Validation";
const navigation: { id: View; label: string; group: Group }[] = [
  { id: "overview", label: "Overview", group: "Workspace" },
  { id: "investigations", label: "Investigations", group: "Workspace" },
  { id: "reviews", label: "Review", group: "Workspace" },
  { id: "messages", label: "Message Explorer", group: "Workspace" },
  { id: "imports", label: "CSV Import", group: "Workspace" },
  { id: "scenarios", label: "Scenario Lab", group: "Validation" },
  { id: "evaluations", label: "Evaluations", group: "Validation" },
  { id: "policies", label: "Policies", group: "Validation" },
  { id: "health", label: "System Health", group: "Validation" },
];
const GROUPS: Group[] = ["Workspace", "Validation"];

function readRoute(): { view: View; caseId?: string } {
  const [raw, caseId] = window.location.hash.slice(1).split("/");
  const view = views.includes(raw as View) ? (raw as View) : "investigations";
  try {
    return {
      view,
      caseId:
        (view === "investigations" || view === "reviews") && caseId
          ? decodeURIComponent(caseId)
          : undefined,
    };
  } catch {
    return { view };
  }
}

export function Brand() {
  return (
    <span className="brand">
      <svg viewBox="0 0 32 32" fill="none" aria-hidden="true" width="22" height="22">
        <path
          d="M5 7h16l-5 9H7m20 9H11l5-9h9"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="square"
        />
      </svg>
      <span>SilentShift</span>
    </span>
  );
}

function ConnectDialog({
  onClose,
  onConnected,
  onClear,
  currentUser,
}: {
  onClose: () => void;
  onConnected: (username: string) => void;
  onClear: () => void;
  currentUser: string | null;
}) {
  const [username, setUsername] = useState(currentUser ?? "");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  return (
    <Modal
      title="Connect to native IRIS"
      description="Use the IRIS account configured for SilentShift. Credentials are kept only in this tab's memory and are sent through the same-origin API."
      onClose={onClose}
    >
      <form
        className="form"
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          if (!username.trim() || /[:\r\n]/.test(username)) {
            setError(new Error("Enter an IRIS username without a colon or line break."));
            return;
          }
          setBusy(true);
          setError(null);
          setCredentials(username.trim(), password);
          try {
            await request("/api/health", HealthSchema);
            setPassword("");
            onConnected(username.trim());
          } catch (failure) {
            clearCredentials();
            setError(failure);
          } finally {
            setBusy(false);
          }
        }}
      >
        <div className="scope">
          <span className="kicker">Local workspace</span>
          <code>/silentshift/api</code>
        </div>
        <label className="label" htmlFor="iris-username">
          IRIS username
        </label>
        <input
          id="iris-username"
          data-autofocus
          autoComplete="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="Your IRIS username"
          required
          maxLength={80}
          disabled={busy}
        />
        <label className="label" htmlFor="iris-password">
          Password
        </label>
        <input
          id="iris-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
          disabled={busy}
        />
        <p className="hint with-icon">
          <LockKeyhole size={14} aria-hidden="true" />
          No browser storage. No credentials in URLs. Remote use requires HTTPS.
        </p>
        {error !== null && <InlineError error={error} />}
        <div className="dialog-actions">
          {currentUser && (
            <Button
              kind="ghost"
              onClick={() => {
                onClear();
                onClose();
              }}
            >
              Clear session
            </Button>
          )}
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            kind="primary"
            icon={KeyRound}
            disabled={busy || !username.trim() || !password}
          >
            {busy ? "Checking native API…" : "Connect session"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function isLandingRoute() {
  const hash = window.location.hash.slice(1);
  return !hash || hash === "landing" || hash.startsWith("landing/");
}

export default function App() {
  const [landing, setLanding] = useState(isLandingRoute);
  const [username, setUsername] = useState<string | null>(null);
  useEffect(() => {
    const listener = () => setLanding(isLandingRoute());
    window.addEventListener("hashchange", listener);
    return () => window.removeEventListener("hashchange", listener);
  }, []);
  // Public product information never mounts the authenticated API hooks.
  return landing ? (
    <Landing />
  ) : (
    <WorkbenchApp username={username} setUsername={setUsername} />
  );
}

const CASE_ID = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i;

function QuickSwitch({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const trimmed = query.trim();
  const isCase = CASE_ID.test(trimmed);
  const matches = navigation.filter((item) =>
    item.label.toLowerCase().includes(trimmed.toLowerCase()),
  );
  const targets = isCase
    ? [{ href: `#investigations/${encodeURIComponent(trimmed)}`, label: "Open investigation", hint: trimmed.slice(0, 8) }]
    : matches.map((item) => ({ href: `#${item.id}`, label: item.label, hint: item.group }));
  useEffect(() => setActive(0), [query]);
  const go = (href: string) => {
    window.location.hash = href.slice(1);
    onClose();
  };
  return (
    <Modal
      title="Go to workspace"
      description="Find a view or paste a complete investigation ID."
      onClose={onClose}
    >
      <form
        className="form"
        onSubmit={(event) => {
          event.preventDefault();
          const target = targets[active] ?? targets[0];
          if (target) go(target.href);
        }}
      >
        <label className="sr-only" htmlFor="workspace-query">
          Find a view or investigation
        </label>
        <input
          id="workspace-query"
          data-autofocus
          autoComplete="off"
          role="combobox"
          aria-expanded="true"
          aria-controls="workspace-results"
          aria-activedescendant={targets.length ? `workspace-result-${active}` : undefined}
          placeholder="Try Review, Scenario Lab, or a case ID…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (!targets.length) return;
            if (event.key === "ArrowDown") {
              event.preventDefault();
              setActive((index) => (index + 1) % targets.length);
            } else if (event.key === "ArrowUp") {
              event.preventDefault();
              setActive((index) => (index + targets.length - 1) % targets.length);
            }
          }}
        />
        <ul className="switch-results" id="workspace-results" role="listbox" aria-label="Matching workspace views">
          {targets.map((target, index) => (
            <li key={target.href} role="option" id={`workspace-result-${index}`} aria-selected={index === active}>
              <a
                href={target.href}
                className={index === active ? "active" : ""}
                onClick={onClose}
                onMouseEnter={() => setActive(index)}
              >
                <span>{target.label}</span>
                <small className="mono">{target.hint}</small>
              </a>
            </li>
          ))}
        </ul>
        {!targets.length && (
          <p className="quiet small">No matching view. Paste a full case ID to open its investigation.</p>
        )}
        <p className="hint">
          <kbd>↑</kbd> <kbd>↓</kbd> choose · <kbd>Enter</kbd> opens · <kbd>Esc</kbd> closes
        </p>
      </form>
    </Modal>
  );
}

function WorkbenchApp({
  username,
  setUsername,
}: {
  username: string | null;
  setUsername: (value: string | null) => void;
}) {
  const [route, setRoute] = useState(readRoute);
  const [epoch, setEpoch] = useState(0);
  const [connect, setConnect] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [quickSwitch, setQuickSwitch] = useState(false);
  const closeQuickSwitch = useCallback(() => setQuickSwitch(false), []);
  const health = useApi("/api/health", HealthSchema, epoch);
  const csvImport = useCSVImport();
  const refresh = useCallback(() => setEpoch((value) => value + 1), []);
  const openConnect = useCallback(() => setConnect(true), []);
  const closeConnect = useCallback(() => setConnect(false), []);
  const inspectCase = useCallback((id: string) => {
    window.location.hash = `investigations/${encodeURIComponent(id)}`;
  }, []);
  const notify = useCallback((message: string) => setToast(message), []);
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k" && !connect) {
        event.preventDefault();
        if (document.querySelector('[aria-modal="true"]') && !quickSwitch) return;
        setQuickSwitch((value) => !value);
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [connect, quickSwitch]);
  useEffect(() => {
    const listener = () => setRoute(readRoute());
    window.addEventListener("hashchange", listener);
    return () => window.removeEventListener("hashchange", listener);
  }, []);
  useEffect(() => {
    document.title = `${navigation.find((item) => item.id === route.view)?.label ?? "Investigations"} · SilentShift`;
    window.scrollTo({ top: 0, behavior: "instant" });
    setMenuOpen(false);
  }, [route.view]);
  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 5000);
    return () => window.clearTimeout(timeout);
  }, [toast]);
  const connected = Boolean(health.data);
  const status = health.loading
    ? "Checking API"
    : connected
      ? "Native API connected"
      : health.error?.status === 401
        ? "Session required"
        : health.error?.status === 403
          ? "Permission required"
          : "Native API offline";
  const statusTone = health.loading ? "muted" : connected ? "allow" : health.error?.status === 401 || health.error?.status === 403 ? "review" : "hold";
  return (
    <AppContext.Provider value={{ refresh, openConnect, inspectCase, notify }}>
      <a
        className="skip"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        Skip to content
      </a>
      <div className="shell">
        <header className="topbar">
          <div className="topbar-inner">
            <a href="#landing" aria-label="SilentShift product home" className="brand-link">
              <Brand />
            </a>
            <button
              className="icon-btn menu-toggle"
              type="button"
              aria-expanded={menuOpen}
              aria-controls="workspace-navigation"
              aria-label={menuOpen ? "Close navigation" : "Open navigation"}
              onClick={() => setMenuOpen((open) => !open)}
            >
              {menuOpen ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
            </button>
            <nav
              id="workspace-navigation"
              aria-label="Main navigation"
              className={`nav ${menuOpen ? "open" : ""}`}
            >
              {GROUPS.map((group) => (
                <div className="nav-group" key={group} role="group" aria-label={group}>
                  <span className="nav-group-label">{group}</span>
                  {navigation
                    .filter((item) => item.group === group)
                    .map(({ id, label }) => (
                      <a
                        key={id}
                        href={`#${id}`}
                        className={`nav-link ${route.view === id ? "active" : ""}`}
                        aria-current={route.view === id ? "page" : undefined}
                      >
                        {label}
                      </a>
                    ))}
                </div>
              ))}
            </nav>
            <div className="topbar-tools">
              <button
                className="jump"
                type="button"
                onClick={() => setQuickSwitch(true)}
                aria-label="Go to workspace"
                title="Go to workspace (⌘K or Ctrl+K)"
              >
                <Search size={14} aria-hidden="true" />
                <span>Go to</span>
                <kbd>⌘K</kbd>
              </button>
              <span className={`status status-${statusTone}`} role="status">
                <span aria-hidden="true" />
                {status}
              </span>
              <button
                className="icon-btn"
                type="button"
                onClick={refresh}
                aria-label="Refresh native API records"
                title="Refresh native API records"
              >
                <RefreshCw size={15} aria-hidden="true" />
              </button>
              <Button
                kind={username ? "ghost" : "primary"}
                icon={KeyRound}
                onClick={openConnect}
                title={username ? `Signed in as ${username}` : undefined}
              >
                {username ? "IRIS session" : "Connect"}
              </Button>
            </div>
          </div>
        </header>
        <ReviewPermissionContext.Provider value={health.data?.permissions?.review === true}>
          <main className="main" id="main-content" tabIndex={-1} key={route.view}>
            {csvImport.busy && route.view !== "imports" && (
              <div className="banner" role="status">
                CSV import is in progress. <a href="#imports">Return to import</a>
              </div>
            )}
            {route.view === "investigations" && (
              <Investigations refresh={epoch} caseId={route.caseId} />
            )}
            {route.view === "reviews" && (
              <Reviews refresh={epoch} caseId={route.caseId} health={health} />
            )}
            {route.view === "scenarios" && <ScenarioLab refresh={epoch} />}
            {route.view === "overview" && <Overview refresh={epoch} health={health} />}
            {route.view === "messages" && <Messages refresh={epoch} />}
            {route.view === "imports" && <CSVImport state={csvImport} health={health} />}
            {route.view === "evaluations" && <Evaluations refresh={epoch} />}
            {route.view === "policies" && <Policies refresh={epoch} />}
            {route.view === "health" && <SystemHealth health={health} />}
          </main>
        </ReviewPermissionContext.Provider>
        <footer className="footer">
          <span>Native InterSystems IRIS AI Hub · deterministic policy · human review</span>
          <a className="link" href="#landing">
            Product overview <ArrowUpRight size={13} aria-hidden="true" />
          </a>
          <Badge>Synthetic demonstration</Badge>
        </footer>
      </div>
      {quickSwitch && <QuickSwitch onClose={closeQuickSwitch} />}
      {connect && (
        <ConnectDialog
          currentUser={username}
          onClose={closeConnect}
          onConnected={(user) => {
            setUsername(user);
            setConnect(false);
            refresh();
            notify("Native IRIS session connected.");
          }}
          onClear={() => {
            clearCredentials();
            setUsername(null);
            refresh();
            notify("Session cleared from memory.");
          }}
        />
      )}
      {toast && (
        <div className="toast" role="status">
          <span>{toast}</span>
          <button className="icon-btn" type="button" aria-label="Dismiss notification" onClick={() => setToast(null)}>
            <X size={14} aria-hidden="true" />
          </button>
        </div>
      )}
    </AppContext.Provider>
  );
}
