import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { ArrowRight, ArrowUpRight, Check, Menu, X } from "lucide-react";
import "./landing.css";
import FlowPreview from "./FlowPreview";
import { Badge, CopyButton } from "./ui";
import type { Tone } from "./ui";

/* Public product pages. Each is its own HTML document (see vite.config.ts), so these
 * components never mount authenticated API hooks and never touch credentials. */

export const PUBLIC_PAGES = [
  "how-it-works",
  "product",
  "safeguards",
  "evidence-record",
  "run-locally",
] as const;
export type PublicPage = (typeof PUBLIC_PAGES)[number];
type SitePage = "home" | PublicPage;

export function isPublicPage(value: string | undefined): value is PublicPage {
  return PUBLIC_PAGES.includes(value as PublicPage);
}

const NAV: { page: PublicPage; label: string }[] = [
  { page: "how-it-works", label: "How it works" },
  { page: "product", label: "Workbench" },
  { page: "safeguards", label: "Safeguards" },
  { page: "evidence-record", label: "Evidence" },
  { page: "run-locally", label: "Run locally" },
];
const href = (page: SitePage) => (page === "home" ? "/" : `/${page}/`);

/** Hashes from the former single-page landing, mapped to their new documents. */
const LEGACY_SECTIONS: Record<string, PublicPage> = {
  "landing/problem": "how-it-works",
  "landing/route": "how-it-works",
  "landing/workbench": "product",
  "landing/proof": "evidence-record",
  "landing/setup": "run-locally",
};
export function legacySectionUrl(hash: string) {
  const page = LEGACY_SECTIONS[hash];
  return page ? href(page) : null;
}

const ROUTE: { role: string; title: string; text: string; tone: Tone }[] = [
  {
    role: "Receives",
    title: "Receive in IRIS",
    text: "The Business Service preserves the original payload, unchanged.",
    tone: "muted",
  },
  {
    role: "Recommends",
    title: "Investigate the evidence",
    text: "Native AI Hub reads scoped, read-only evidence and proposes a recommendation.",
    tone: "agent",
  },
  {
    role: "Decides",
    title: "Validate the permission",
    text: "Deterministic policy in Embedded Python blocks unverified release. Conflicting references go to human review.",
    tone: "accent",
  },
  {
    role: "Records",
    title: "Route and preserve",
    text: "Business Operations persist every outcome and receipt. Each route stays inspectable in Visual Trace.",
    tone: "muted",
  },
];

const SURFACES: { view: string; title: string; group: string; text: string }[] = [
  {
    view: "overview",
    group: "Workspace",
    title: "Overview",
    text: "What arrived, what contradicted its agreement, and what was contained.",
  },
  {
    view: "investigations",
    group: "Workspace",
    title: "Investigations",
    text: "A queue of cases with the original payload, approved references, semantic findings, precedents, policy checks and native trace.",
  },
  {
    view: "reviews",
    group: "Workspace",
    title: "Review",
    text: "Eligible holds become native Workflow review tasks. Actions need reviewer permission, a written reason and the current case version.",
  },
  {
    view: "messages",
    group: "Workspace",
    title: "Message Explorer",
    text: "Inspect or inject partner JSON, compare it with the reference snapshot, then follow it to its investigation and IRIS trace.",
  },
  {
    view: "imports",
    group: "Workspace",
    title: "CSV Import",
    text: "Preview an order feed against a separate approved export, then commit to investigate each line. Up to 20 rows and 128 KiB per file.",
  },
  {
    view: "scenarios",
    group: "Validation",
    title: "Scenario Lab",
    text: "Inject frozen synthetic scenarios into the native production and compare the observed route with ground truth.",
  },
  {
    view: "evaluations",
    group: "Validation",
    title: "Evaluations",
    text: "Compare deterministic rules, native recommendations and policy-constrained outcomes from measured runs.",
  },
  {
    view: "policies",
    group: "Validation",
    title: "Policies",
    text: "The agent recommends. Deterministic policy decides which actions are permitted.",
  },
  {
    view: "health",
    group: "Validation",
    title: "System Health",
    text: "Production, component and agent-configuration status as reported by IRIS. Configuration is not proof of execution.",
  },
];

const PROOF: { scenario: string; policy: string; tone: Tone }[] = [
  { scenario: "Quantity-unit mismatch", policy: "Quarantine", tone: "hold" },
  { scenario: "Currency-scale mismatch", policy: "Quarantine", tone: "hold" },
  { scenario: "Approved contract amendment", policy: "Allow", tone: "allow" },
  { scenario: "Conflicting references", policy: "Request review", tone: "review" },
  { scenario: "Labeled unsafe-proposal injection", policy: "Quarantine", tone: "hold" },
];

const COMMANDS =
  "uv run --env-file .env python scripts/doctor.py\nuv run --env-file .env python scripts/bootstrap.py";

function Mark({ size = 22 }: { size?: number }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" aria-hidden="true" width={size} height={size}>
      <path
        d="M5 7h16l-5 9H7m20 9H11l5-9h9"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="square"
      />
    </svg>
  );
}

function SiteHeader({ current }: { current: SitePage }) {
  const [open, setOpen] = useState(false);
  const toggle = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!open) return;
    const listener = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        toggle.current?.focus();
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [open]);
  return (
    <header className="site-header">
      <div className="site-wrap site-header-inner">
        <a
          className="site-brand"
          href="/"
          aria-current={current === "home" ? "page" : undefined}
        >
          <Mark />
          <span>SilentShift</span>
        </a>
        <button
          ref={toggle}
          className="icon-btn site-menu-toggle"
          type="button"
          aria-expanded={open}
          aria-controls="site-navigation"
          aria-label={open ? "Close site navigation" : "Open site navigation"}
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
        </button>
        <nav
          id="site-navigation"
          className={`site-nav ${open ? "open" : ""}`}
          aria-label="Site"
        >
          <ul>
            {NAV.map(({ page, label }) => (
              <li key={page}>
                <a href={href(page)} aria-current={current === page ? "page" : undefined}>
                  {label}
                </a>
              </li>
            ))}
          </ul>
          <a className="btn btn-primary site-cta" href="/#investigations">
            Open workbench <ArrowRight size={15} aria-hidden="true" />
          </a>
        </nav>
      </div>
    </header>
  );
}

function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-wrap site-footer-inner">
        <div className="site-footer-brand">
          <a className="site-brand" href="/">
            <Mark size={18} />
            <span>SilentShift</span>
          </a>
          <p>Semantic integrity on InterSystems IRIS.</p>
          <Badge>Synthetic demonstration · simulator-only delivery</Badge>
        </div>
        <nav aria-label="Footer">
          <ul>
            <li>
              <a href="/">Home</a>
            </li>
            {NAV.map(({ page, label }) => (
              <li key={page}>
                <a href={href(page)}>{label}</a>
              </li>
            ))}
            <li>
              <a href="/#investigations">Workbench</a>
            </li>
            <li>
              <a href="https://github.com/himanshu748/silentshift" target="_blank" rel="noreferrer">
                Source on GitHub <ArrowUpRight size={13} aria-hidden="true" />
                <span className="sr-only">(opens in a new tab)</span>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </footer>
  );
}

/** Shared document chrome: skip link, header, main landmark and footer. */
function SiteLayout({
  current,
  focusMain = false,
  children,
}: {
  current: SitePage;
  focusMain?: boolean;
  children: ReactNode;
}) {
  const main = useRef<HTMLElement>(null);
  useEffect(() => {
    // Arriving from the in-document workbench: move focus to the new content.
    if (focusMain) main.current?.focus({ preventScroll: true });
  }, [focusMain]);
  return (
    <div className="site">
      <a
        className="skip"
        href="#site-main"
        onClick={(event) => {
          // Keep the hash untouched: on the root document a hash selects a workbench view.
          event.preventDefault();
          main.current?.focus();
        }}
      >
        Skip to content
      </a>
      <SiteHeader current={current} />
      <main id="site-main" ref={main} tabIndex={-1}>
        {children}
      </main>
      <SiteFooter />
    </div>
  );
}

function PageIntro({
  kicker,
  title,
  children,
}: {
  kicker: string;
  title: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="site-intro" aria-labelledby="page-title">
      <div className="site-wrap">
        <p className="site-kicker">{kicker}</p>
        <h1 id="page-title">{title}</h1>
        <div className="site-lead">{children}</div>
      </div>
    </section>
  );
}

function Section({
  id,
  title,
  lead,
  tinted = false,
  children,
}: {
  id: string;
  title: string;
  lead?: ReactNode;
  tinted?: boolean;
  children: ReactNode;
}) {
  return (
    <section className={`site-section ${tinted ? "tinted" : ""}`} aria-labelledby={id}>
      <div className="site-wrap">
        <header className="site-section-head">
          <h2 id={id}>{title}</h2>
          {lead && <p>{lead}</p>}
        </header>
        {children}
      </div>
    </section>
  );
}

function NextPage({ page, title, text }: { page: SitePage | "workbench"; title: string; text: string }) {
  return (
    <aside className="site-next" aria-label="Continue">
      <div className="site-wrap">
        <a href={page === "workbench" ? "/#investigations" : href(page)}>
          <span className="kicker">Next</span>
          <span className="site-next-title">
            {title} <ArrowRight size={18} aria-hidden="true" />
          </span>
          <span className="site-next-text">{text}</span>
        </a>
      </div>
    </aside>
  );
}

function Capture({
  src,
  mobile,
  alt,
  label,
  children,
}: {
  src: string;
  mobile: string;
  alt: string;
  label: string;
  children: ReactNode;
}) {
  return (
    <figure className="site-capture">
      <a href={src} target="_blank" rel="noreferrer" aria-label={`${label} (opens in a new tab)`}>
        <picture>
          <source media="(max-width: 600px)" srcSet={mobile} />
          <img src={src} alt={alt} width="1440" height="960" loading="lazy" />
        </picture>
      </a>
      <figcaption>
        <Badge>Recorded capture</Badge>
        {children}
      </figcaption>
    </figure>
  );
}

function CaseCompare({
  id,
  title,
  approved,
  children,
}: {
  id: string;
  title: string;
  approved: boolean;
  children: ReactNode;
}) {
  return (
    <article className={`site-case ${approved ? "allow" : "hold"}`} aria-labelledby={id}>
      <header>
        <h3 id={id}>{title}</h3>
        {approved ? (
          <Badge tone="allow">
            <Check size={13} aria-hidden="true" /> Allow
          </Badge>
        ) : (
          <Badge tone="hold">
            <X size={13} aria-hidden="true" /> Quarantine
          </Badge>
        )}
      </header>
      <div className="site-compare">
        <div>
          <span>Partner sends</span>
          <strong className="mono">
            20 <small>CASE</small>
          </strong>
        </div>
        <span className="site-compare-mark" aria-hidden="true">
          {approved ? "=" : "≠"}
        </span>
        <span className="sr-only">{approved ? "matches" : "does not match"}</span>
        <div>
          <span>{approved ? "Effective approved amendment" : "Approved contract"}</span>
          <strong className="mono">
            {approved ? "20" : "240"} <small>{approved ? "CASE" : "EA"}</small>
          </strong>
        </div>
      </div>
      <p>{children}</p>
    </article>
  );
}

/* ---------- Pages ---------- */

export function Home({ focusMain = false }: { focusMain?: boolean }) {
  useEffect(() => {
    document.title = "SilentShift · Catch what status codes miss";
  }, []);
  return (
    <SiteLayout current="home" focusMain={focusMain}>
      <section className="site-hero" aria-labelledby="page-title">
        <div className="site-wrap site-hero-grid">
          <div className="site-hero-copy">
            <p className="site-kicker">Semantic integrity for InterSystems IRIS</p>
            <h1 id="page-title">
              Catch what <em>status codes miss.</em>
            </h1>
            <p className="site-hero-lead">
              The request succeeded. The business meaning changed. SilentShift investigates B2B
              orders and payments against the approved agreement before anything reaches its
              destination.
            </p>
            <p className="site-hero-audience">
              For integration operations teams running order and payment pipelines on IRIS.
            </p>
            <div className="site-actions">
              <a className="btn btn-primary site-btn-lg" href="/#investigations">
                Open workbench <ArrowRight size={16} aria-hidden="true" />
              </a>
              <a className="btn btn-secondary site-btn-lg" href={href("how-it-works")}>
                How it works
              </a>
            </div>
          </div>
          <div className="site-hero-figure">
            <FlowPreview />
            <p className="site-caption">Illustration only · synthetic values · no API or model call</p>
          </div>
        </div>
      </section>

      <section className="site-roles" aria-label="Who does what">
        <div className="site-wrap">
          <dl>
            <div>
              <dt>Investigates</dt>
              <dd>Native IRIS AI Hub, on read-only evidence</dd>
            </div>
            <div>
              <dt>Decides</dt>
              <dd>Deterministic policy, never the model</dd>
            </div>
            <div>
              <dt>Resolves</dt>
              <dd>Human reviewers, for eligible holds</dd>
            </div>
          </dl>
        </div>
      </section>

      <Section
        id="home-pages"
        title="Explore SilentShift"
        lead="Each page covers one question. The workbench is where the native records live."
      >
        <ul className="site-directory">
          {[
            {
              page: "how-it-works" as const,
              title: "How it works",
              text: "Why a valid message can still be wrong, and the four stages IRIS runs for every event.",
            },
            {
              page: "product" as const,
              title: "The workbench",
              text: "Nine views over the native API: investigations, review, CSV import, Scenario Lab and more.",
            },
            {
              page: "safeguards" as const,
              title: "Safeguards",
              text: "What the model may and may not do, how review is enforced and how credentials are handled.",
            },
            {
              page: "evidence-record" as const,
              title: "Evidence record",
              text: "Five synthetic scenarios run natively, the observed outcomes, and their stated limits.",
            },
            {
              page: "run-locally" as const,
              title: "Run locally",
              text: "Start the build 154 production, check it with the doctor script and connect the workbench.",
            },
          ].map(({ page, title, text }) => (
            <li key={page}>
              <a className="site-card" href={href(page)}>
                <span className="site-card-title">
                  {title} <ArrowRight size={16} aria-hidden="true" />
                </span>
                <span className="site-card-text">{text}</span>
              </a>
            </li>
          ))}
        </ul>
      </Section>

      <NextPage
        page="workbench"
        title="Inspect a held order yourself"
        text="The workbench shows the contradiction, the approved reference, the observed route and the next permitted action. It needs a running local production and an IRIS session."
      />
    </SiteLayout>
  );
}

function HowItWorks() {
  return (
    <SiteLayout current="how-it-works">
      <PageIntro kicker="How it works" title="Valid message. Contradicted agreement.">
        <p>
          A supplier sends 20 cases. The JSON is valid and the delivery would succeed. The approved
          contract, not the transport, determines what happens next.
        </p>
      </PageIntro>

      <Section id="hiw-cases" title="Same order, two agreements" tinted>
        <div className="site-cases">
          <CaseCompare id="case-a" title="Case A · Unapproved unit change" approved={false}>
            No approved CASE-to-EA conversion exists. A plausible conversion cannot authorize
            release.
          </CaseCompare>
          <CaseCompare id="case-c" title="Case C · Approved amendment" approved>
            An effective approved amendment authorizes the 20 CASE order. Unverified conversions
            remain blocked.
          </CaseCompare>
        </div>
      </Section>

      <Section
        id="hiw-route"
        title="IRIS owns the whole route"
        lead="One native production. A Business Process orchestrates every stage, and the AI recommendation never releases a message on its own."
      >
        <ol className="site-route">
          {ROUTE.map(({ role, title, text, tone }, index) => (
            <li key={title} className={`site-step tone-${tone}`}>
              <span className="site-step-top">
                <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                <span className="kicker">{role}</span>
              </span>
              <h3>{title}</h3>
              <p>{text}</p>
            </li>
          ))}
        </ol>
        <div className="site-split">
          <details className="disclosure plain">
            <summary>Technical names</summary>
            <dl className="meta">
              <div>
                <dt>Receive</dt>
                <dd className="mono">SilentShift.Service.Partner</dd>
              </div>
              <div>
                <dt>Investigate</dt>
                <dd className="mono">SilentShift.AI.Investigator</dd>
              </div>
              <div>
                <dt>Production</dt>
                <dd className="mono">SilentShift.Production</dd>
              </div>
            </dl>
          </details>
          <div className="site-note">
            <a className="link" href="/evidence/provider-calls.json" target="_blank" rel="noreferrer">
              Read recorded traces <ArrowUpRight size={14} aria-hidden="true" />
              <span className="sr-only">(opens in a new tab)</span>
            </a>
            <p className="small quiet">
              Recorded native invocation, tool and per-provider-call evidence.
            </p>
          </div>
        </div>
      </Section>

      <Section
        id="hiw-capture"
        title="What an allowed route looks like"
        lead="The approved-amendment case, as recorded from the native workbench."
        tinted
      >
        <Capture
          src="/evidence/native-approved-workbench.png"
          mobile="/evidence/native-approved-mobile.png"
          label="Open full-size capture of the approved native delivery"
          alt="Actual SilentShift approved-amendment investigation with an allow policy and delivery to the destination simulator."
        >
          The destination is an IRIS simulator, not an external business system.
        </Capture>
      </Section>

      <NextPage
        page="product"
        title="Tour the workbench"
        text="See where investigations, precedents, review tasks and traces appear."
      />
    </SiteLayout>
  );
}

function Product() {
  const groups = ["Workspace", "Validation"];
  return (
    <SiteLayout current="product">
      <PageIntro kicker="The workbench" title="One workbench for every hold.">
        <p>
          Every view reads the native IRIS API; there is no mock backend. Without a running
          production, the workbench says so instead of showing sample records.
        </p>
      </PageIntro>

      {groups.map((group, index) => (
        <Section
          key={group}
          id={`product-${group.toLowerCase()}`}
          title={group}
          lead={
            group === "Workspace"
              ? "Daily operations: what arrived, what was held and who resolves it."
              : "Checking the system itself: synthetic scenarios, measured runs, rules and runtime."
          }
          tinted={index === 0}
        >
          <ul className="site-directory">
            {SURFACES.filter((item) => item.group === group).map(({ view, title, text }) => (
              <li key={view}>
                <a className="site-card" href={`/#${view}`}>
                  <span className="site-card-title">
                    {title} <ArrowRight size={16} aria-hidden="true" />
                  </span>
                  <span className="site-card-text">{text}</span>
                  <code className="site-card-path">/#{view}</code>
                </a>
              </li>
            ))}
          </ul>
        </Section>
      ))}

      <Section id="product-links" title="Deep links and shortcuts">
        <ul className="site-list">
          <li>
            Open a specific case with <code>/#investigations/&lt;case-id&gt;</code> or its review
            task with <code>/#reviews/&lt;case-id&gt;</code>.
          </li>
          <li>
            Inside the workbench, press <kbd>⌘K</kbd> or <kbd>Ctrl+K</kbd> to jump to a view or
            paste a complete investigation ID.
          </li>
          <li>
            CSV Import delivers per line to the IRIS simulator. Whole-order completeness and
            external delivery are not verified.
          </li>
        </ul>
      </Section>

      <NextPage
        page="safeguards"
        title="Read the safeguards"
        text="How policy, review permissions and session handling constrain what the workbench can do."
      />
    </SiteLayout>
  );
}

function Safeguards() {
  return (
    <SiteLayout current="safeguards">
      <PageIntro kicker="Safeguards" title="The model recommends. It never releases.">
        <p>
          SilentShift separates investigation from authority. AI Hub can read evidence and propose;
          only deterministic policy and permitted reviewers change a route.
        </p>
      </PageIntro>

      <Section id="sg-authority" title="Who may do what" tinted>
        <div className="table-wrap" role="region" aria-label="Authority by participant" tabIndex={0}>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">Participant</th>
                <th scope="col">May</th>
                <th scope="col">May not</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Native AI Hub investigator</th>
                <td>Read scoped, read-only evidence and precedents; propose a recommendation</td>
                <td>Release, hold or modify a message</td>
              </tr>
              <tr>
                <th scope="row">Deterministic policy</th>
                <td>Decide the route; block unverified release; send conflicting references to review</td>
                <td>Accept a plausible but unapproved conversion as authority</td>
              </tr>
              <tr>
                <th scope="row">Human reviewer</th>
                <td>Resolve eligible holds through native Workflow tasks</td>
                <td>Act without reviewer permission, a written reason and the current case version</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Section>

      <Section
        id="sg-review"
        title="Review is enforced by the server"
        lead="The workbench only reflects the rules; the native API enforces them."
      >
        <ul className="site-checks">
          <li>Review actions require the reviewer permission reported by the native API.</li>
          <li>Every action needs a written reason.</li>
          <li>Every action must carry the current case version.</li>
          <li>Critical contradictions cannot be approved. Corrected input or approved authority requires a new investigation.</li>
          <li>Only eligible holds become review tasks; other routes are decided by policy alone.</li>
        </ul>
      </Section>

      <Section id="sg-session" title="Session handling" tinted>
        <ul className="site-checks">
          <li>IRIS credentials are kept only in the memory of the workbench tab.</li>
          <li>No browser storage and no credentials in URLs. Requests use the same-origin API.</li>
          <li>
            Product pages are separate documents. Opening one from the workbench ends the
            in-memory session, so you reconnect when you return.
          </li>
          <li>Remote use requires HTTPS.</li>
        </ul>
      </Section>

      <Section id="sg-limits" title="Stated limits">
        <ul className="site-list">
          <li>All sample data is synthetic. Delivery goes to an IRIS simulator only.</li>
          <li>There is no hosted demo; run the native app locally to investigate an order.</li>
          <li>System Health shows configuration as reported by IRIS; configuration is not proof of execution.</li>
          <li>CSV Import checks per line; whole-order completeness is not verified.</li>
        </ul>
      </Section>

      <NextPage
        page="evidence-record"
        title="See the evidence record"
        text="The recorded native outcomes, and what they do not show."
      />
    </SiteLayout>
  );
}

function EvidenceRecord() {
  return (
    <SiteLayout current="evidence-record">
      <PageIntro kicker="Evidence record" title="Five cases. Five controlled outcomes.">
        <p>
          Five synthetic scenarios, run natively in IRIS on November 2, 2026. These are synthetic
          cases, not a measure of general accuracy.
        </p>
      </PageIntro>

      <Section id="ev-outcomes" title="Observed outcomes" tinted>
        <div className="site-proof">
          <div className="table-wrap" role="region" aria-label="Recorded scenario outcomes" tabIndex={0}>
            <table className="table">
              <thead>
                <tr>
                  <th scope="col">Synthetic scenario</th>
                  <th scope="col">Observed policy</th>
                </tr>
              </thead>
              <tbody>
                {PROOF.map(({ scenario, policy, tone }) => (
                  <tr key={scenario}>
                    <th scope="row">{scenario}</th>
                    <td>
                      <Badge tone={tone}>{policy}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="site-limits">
            <p>
              <strong>Rule-only baseline: 5/5.</strong> No AI accuracy uplift demonstrated.
            </p>
            <ul className="site-list">
              <li>
                <a className="link" href="/evidence/native-summary.json" target="_blank" rel="noreferrer">
                  Trial records, including failures <ArrowUpRight size={14} aria-hidden="true" />
                  <span className="sr-only">(opens in a new tab)</span>
                </a>
              </li>
              <li>
                <a className="link" href="/evidence/provider-calls.json" target="_blank" rel="noreferrer">
                  Provider-call traces <ArrowUpRight size={14} aria-hidden="true" />
                  <span className="sr-only">(opens in a new tab)</span>
                </a>
              </li>
              <li>
                <a className="link" href="/evidence/traceability.json" target="_blank" rel="noreferrer">
                  Traceability record <ArrowUpRight size={14} aria-hidden="true" />
                  <span className="sr-only">(opens in a new tab)</span>
                </a>
              </li>
            </ul>
            <p className="small quiet">Current verification is linked in the repository.</p>
          </div>
        </div>
      </Section>

      <Section
        id="ev-capture"
        title="A held payment"
        lead="12550 minor EUR units equals 125.50 major EUR units. The interface requires major units and authorizes no conversion."
      >
        <Capture
          src="/evidence/native-currency-workbench.png"
          mobile="/evidence/native-currency-mobile.png"
          label="Open full-size capture of the native currency investigation"
          alt="Actual SilentShift investigation: the payload uses minor EUR units while the approved interface requires major units. Policy quarantines the unauthorized representation change."
        >
          Native investigation of a synthetic payment event, held from the destination simulator.
        </Capture>
      </Section>

      <Section id="ev-reproduce" title="Reproduce it" tinted>
        <p className="site-prose">
          Scenario Lab injects the same frozen synthetic scenarios into your own local production
          and compares the observed route with ground truth.{" "}
          <a className="link" href="/#scenarios">
            Open Scenario Lab <ArrowRight size={14} aria-hidden="true" />
          </a>
        </p>
      </Section>

      <NextPage
        page="run-locally"
        title="Run it locally"
        text="Start the native production and check the runtime before connecting."
      />
    </SiteLayout>
  );
}

function RunLocally() {
  return (
    <SiteLayout current="run-locally">
      <PageIntro kicker="Run locally" title="Start the IRIS production.">
        <p>
          Load authorized build 154 and configure <code>.env</code>. No EAP kit is bundled with the
          source.
        </p>
      </PageIntro>

      <Section id="rl-steps" title="Three steps" tinted>
        <ol className="site-steps">
          <li>
            <h3>Prepare the runtime</h3>
            <p>
              Load the authorized IRIS build and configure <code>.env</code> as described in the
              single installation guide. Complete its prerequisites and local-model setup first.
            </p>
            <a
              className="link"
              href="https://github.com/himanshu748/silentshift/blob/main/INSTALL.md"
              target="_blank"
              rel="noreferrer"
            >
              Get source and setup <ArrowUpRight size={14} aria-hidden="true" />
              <span className="sr-only">(opens in a new tab)</span>
            </a>
          </li>
          <li>
            <h3>Check and bootstrap</h3>
            <div className="site-command">
              <div className="site-command-head">
                <span className="kicker">Native setup</span>
                <CopyButton value={COMMANDS} label="Copy setup commands" />
              </div>
              <pre tabIndex={0} aria-label="Native setup commands">
                <code>{COMMANDS}</code>
              </pre>
              <p className="small quiet">
                Tested: <code>2026.3.0AI.154.0 / 154U ARM64</code>. Kit excluded; other builds and platforms unverified.
              </p>
            </div>
          </li>
          <li>
            <h3>Connect the workbench</h3>
            <p>
              Open the workbench and choose <strong>Connect</strong>. Use the IRIS account
              configured for SilentShift; credentials stay in that tab's memory.
            </p>
            <a className="link" href="/#health">
              Check System Health <ArrowRight size={14} aria-hidden="true" />
            </a>
          </li>
        </ol>
      </Section>

      <NextPage
        page="workbench"
        title="Open the workbench"
        text="Start with the investigation queue, or run a Scenario Lab case to produce your first record."
      />
    </SiteLayout>
  );
}

const PAGES: Record<PublicPage, () => ReactNode> = {
  "how-it-works": HowItWorks,
  product: Product,
  safeguards: Safeguards,
  "evidence-record": EvidenceRecord,
  "run-locally": RunLocally,
};

export default function PublicSite({ page }: { page: PublicPage }) {
  const Page = PAGES[page];
  return <Page />;
}
