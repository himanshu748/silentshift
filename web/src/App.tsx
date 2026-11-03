import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  Beaker,
  ChevronDown,
  Command,
  FileJson2,
  FlaskConical,
  GitCompareArrows,
  KeyRound,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  RefreshCw,
  ShieldCheck,
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

const views = [
  "investigations",
  "reviews",
  "scenarios",
  "overview",
  "messages",
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
  return landing ? <Landing /> : <WorkbenchApp username={username} setUsername={setUsername} />;
}

function WorkbenchApp({ username, setUsername }: { username: string | null; setUsername: (value: string | null) => void }) {
  const [route, setRoute] = useState(readRoute);
  const [epoch, setEpoch] = useState(0);
  const [connect, setConnect] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [navigationOpen, setNavigationOpen] = useState(false);
  const health = useApi("/api/health", HealthSchema, epoch);
  const refresh = useCallback(() => setEpoch((value) => value + 1), []);
  const openConnect = useCallback(() => setConnect(true), []);
  const closeConnect = useCallback(() => setConnect(false), []);
  const inspectCase = useCallback((id: string) => {
    window.location.hash = `investigations/${encodeURIComponent(id)}`;
  }, []);
  const notify = useCallback((message: string) => setToast(message), []);
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
            href="#investigations"
            aria-label="SilentShift investigations"
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
              {route.view === "investigations" && (
                <Investigations refresh={epoch} caseId={route.caseId} />
              )}
              {route.view === "reviews" && (
                <Reviews refresh={epoch} caseId={route.caseId} health={health} />
              )}
              {route.view === "scenarios" && <ScenarioLab refresh={epoch} />}
              {route.view === "overview" && (
                <Overview refresh={epoch} health={health} />
              )}
              {route.view === "messages" && <Messages refresh={epoch} />}
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
            <a className="text-link" href="#landing">Product overview</a>
            <Badge>Synthetic demonstration</Badge>
          </footer>
        </div>
      </div>
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
