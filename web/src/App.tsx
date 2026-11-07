import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Beaker,
  ChevronDown,
  Command,
  FileJson2,
  FileSpreadsheet,
  FlaskConical,
  GitCompareArrows,
  KeyRound,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  RefreshCw,
  ShieldCheck,
  Search,
  UserRoundCheck,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
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
const navigation: {
  id: View;
  label: string;
  icon: LucideIcon;
  group: "Workspace" | "Validation";
}[] = [
  {
    id: "overview",
    label: "Overview",
    icon: LayoutDashboard,
    group: "Workspace",
  },
  {
    id: "investigations",
    label: "Investigations",
    icon: GitCompareArrows,
    group: "Workspace",
  },
  {
    id: "reviews",
    label: "Review",
    icon: UserRoundCheck,
    group: "Workspace",
  },
  {
    id: "messages",
    label: "Message Explorer",
    icon: FileJson2,
    group: "Workspace",
  },
  { id: "imports", label: "CSV Import", icon: FileSpreadsheet, group: "Workspace" },
  { id: "scenarios", label: "Scenario Lab", icon: Beaker, group: "Validation" },
  {
    id: "evaluations",
    label: "Evaluations",
    icon: FlaskConical,
    group: "Validation",
  },
  { id: "policies", label: "Policies", icon: ShieldCheck, group: "Validation" },
  { id: "health", label: "System Health", icon: Activity, group: "Validation" },
];

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

function Brand({ small = false }: { small?: boolean }) {
  return (
    <span className={`brand ${small ? "brand-small" : ""}`}>
      <span className="brand-symbol" aria-hidden="true">
        <svg viewBox="0 0 32 32" fill="none">
          <path
            d="M5 7h16l-5 9H7m20 9H11l5-9h9"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="square"
          />
        </svg>
      </span>
      {!small && (
        <span>
          SilentShift<span className="brand-period">.</span>
        </span>
      )}
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
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          if (!username.trim() || /[:\r\n]/.test(username)) {
            setError(
              new Error(
                "Enter an IRIS username without a colon or line break.",
              ),
            );
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
        <div className="connection-scope">
          <span className="status-dot" />
          <span>Local workspace</span>
          <code>/silentshift/api</code>
        </div>
        <label className="field-label" htmlFor="iris-username">
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
        <label className="field-label" htmlFor="iris-password">
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
        <div className="credential-note">
          <LockKeyhole size={15} />
          <p>
            No browser storage. No credentials in URLs. Remote use requires
            HTTPS.
          </p>
        </div>
        {error !== null && <InlineError error={error} />}
        <div className="modal-actions">
          {currentUser && (
            <Button
              type="button"
              kind="ghost"
              onClick={() => {
                onClear();
                onClose();
              }}
            >
              Clear session
            </Button>
          )}
          <Button type="button" onClick={onClose}>
            Cancel
          </Button>
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

function QuickSwitch({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const matches = navigation.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase().trim()),
  );
  const caseId =
    /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(
      query.trim(),
    );
  return (
    <Modal
      title="Go to workspace"
      description="Find a view or paste a complete investigation ID."
      onClose={onClose}
    >
      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (caseId) {
            window.location.hash = `investigations/${encodeURIComponent(query.trim())}`;
            onClose();
          } else if (matches[0]) {
            window.location.hash = matches[0].id;
            onClose();
          }
        }}
      >
        <label className="sr-only" htmlFor="workspace-query">
          Find a view or investigation
        </label>
        <input
          id="workspace-query"
          data-autofocus
          autoComplete="off"
          placeholder="Try Review, Scenario Lab, or a case ID…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <nav
          className="quick-switch-results"
          aria-label="Matching workspace views"
        >
          {caseId ? (
            <a
              href={`#investigations/${encodeURIComponent(query.trim())}`}
              onClick={onClose}
            >
              <Search size={17} />
              <span>Open investigation</span>
              <small>{query.trim().slice(0, 8)}</small>
            </a>
          ) : (
            matches.map(({ id, label, icon: Icon }) => (
              <a key={id} href={`#${id}`} onClick={onClose}>
                <Icon size={17} />
                <span>{label}</span>
                <ArrowUpRight size={14} />
              </a>
            ))
          )}
          {!caseId && matches.length === 0 && (
            <p>
              No matching view. Paste a full case ID to open its investigation.
            </p>
          )}
        </nav>
        <p className="quick-switch-hint">
          Enter opens the first match. Tab moves through results. Escape closes.
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
  const [navigationOpen, setNavigationOpen] = useState(false);
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
      if (
        (event.metaKey || event.ctrlKey) &&
        event.key.toLowerCase() === "k" &&
        !connect
      ) {
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
    setNavigationOpen(false);
  }, [route.view]);
  useEffect(() => {
    if (toast) {
      const timeout = window.setTimeout(() => setToast(null), 5000);
      return () => window.clearTimeout(timeout);
    }
  }, [toast]);
  const current = navigation.find((item) => item.id === route.view)!;
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
  return (
    <AppContext.Provider value={{ refresh, openConnect, inspectCase, notify }}>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("main-content")?.focus();
        }}
      >
        Skip to content
      </a>
      <div className="app-shell">
        <aside className={`sidebar ${navigationOpen ? "navigation-open" : ""}`}>
          <a
            href="#landing"
            aria-label="SilentShift product home"
            className="brand-link"
          >
            <Brand />
          </a>
          <button
            className="button ghost navigation-toggle"
            type="button"
            aria-expanded={navigationOpen}
            aria-controls="workspace-navigation"
            onClick={() => setNavigationOpen((open) => !open)}
          >
            {navigationOpen ? <X size={18} /> : <Menu size={18} />}
            Navigation
          </button>
          <div className="workspace-switch">
            <span className="workspace-avatar">
              <Command size={15} />
            </span>
            <div>
              <strong>Integrity workspace</strong>
              <small>Synthetic demonstration</small>
            </div>
          </div>
          <nav id="workspace-navigation" aria-label="Main navigation">
            {(["Workspace", "Validation"] as const).map((group) => (
              <div className="nav-group" key={group}>
                <div className="nav-group-label">{group}</div>
                {navigation
                  .filter((item) => item.group === group)
                  .map(({ id, label, icon: Icon }) => (
                    <a
                      key={id}
                      href={`#${id}`}
                      className={`nav-item ${route.view === id ? "active" : ""}`}
                      aria-current={route.view === id ? "page" : undefined}
                    >
                      <Icon size={17} strokeWidth={1.6} />
                      <span>{label}</span>
                    </a>
                  ))}
              </div>
            ))}
          </nav>
          <div className="sidebar-bottom">
            <div className="native-identity">
              <Brand small />
              <div>
                <strong>IRIS AI Hub</strong>
                <span>Native by design</span>
              </div>
            </div>
            <div className="build-target">
              <span className="mono">154</span>
              <p>
                Community Early Access
                <br />
                Verified runtime
              </p>
            </div>
            <a
              className="sidebar-docs"
              href="https://github.com/intersystems-community/ai-hub-eap"
              target="_blank"
              rel="noreferrer"
            >
              AI Hub documentation <ArrowUpRight size={13} />
            </a>
          </div>
        </aside>
        <div className="main-shell">
          <header className="topbar">
            <div className="breadcrumb">
              <span>{current.group}</span>
              <ChevronDown className="breadcrumb-divider" size={12} />
              <strong>{current.label}</strong>
            </div>
            <div className="topbar-actions">
              <button
                className="workspace-jump"
                onClick={() => setQuickSwitch(true)}
                aria-label="Go to workspace"
                title="Go to workspace (⌘K or Ctrl+K)"
              >
                <Search size={15} />
                <span>Go to…</span>
                <kbd>⌘ K</kbd>
              </button>
              <span
                className={`connection-pill ${connected ? "mint" : "muted"}`}
              >
                <Activity size={13} aria-hidden="true" />
                {status}
              </span>
              <span className="topbar-divider" />
              <button
                className="icon-button"
                onClick={refresh}
                aria-label="Refresh native API records"
                title="Refresh native API records"
              >
                <RefreshCw size={16} />
              </button>
              <Button kind="ghost" icon={KeyRound} onClick={openConnect}>
                {username ? "IRIS session" : "Connect"}
              </Button>
            </div>
          </header>
          <ReviewPermissionContext.Provider
            value={health.data?.permissions?.review === true}
          >
            <main
              className="main-content"
              id="main-content"
              tabIndex={-1}
              key={route.view}
            >
              {csvImport.busy && route.view !== "imports" && <div className="csv-background" role="status">CSV import is in progress. <a href="#imports">Return to import</a></div>}
              {route.view === "investigations" && (
                <Investigations refresh={epoch} caseId={route.caseId} />
              )}
              {route.view === "reviews" && (
                <Reviews
                  refresh={epoch}
                  caseId={route.caseId}
                  health={health}
                />
              )}
              {route.view === "scenarios" && <ScenarioLab refresh={epoch} />}
              {route.view === "overview" && (
                <Overview refresh={epoch} health={health} />
              )}
              {route.view === "messages" && <Messages refresh={epoch} />}
              {route.view === "imports" && <CSVImport state={csvImport} health={health} />}
              {route.view === "evaluations" && <Evaluations refresh={epoch} />}
              {route.view === "policies" && <Policies refresh={epoch} />}
              {route.view === "health" && <SystemHealth health={health} />}
            </main>
          </ReviewPermissionContext.Provider>
          <footer className="app-footer">
            <span>
              <span className="footer-glyph" />
              Signal over noise. Substance over success codes.
            </span>
            <a className="text-link" href="#landing">
              Product overview
            </a>
            <Badge>Synthetic demonstration</Badge>
          </footer>
        </div>
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
          <ShieldCheck size={17} />
          <span>{toast}</span>
          <button
            className="icon-button"
            aria-label="Dismiss notification"
            onClick={() => setToast(null)}
          >
            <X size={15} />
          </button>
        </div>
      )}
    </AppContext.Provider>
  );
}
