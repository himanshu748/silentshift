import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { ArrowRight, ArrowUpRight, Check, X } from "lucide-react";
import "./landing.css";
import FlowPreview from "./FlowPreview";
import { Badge, CopyButton } from "./ui";
import type { Tone } from "./ui";

const SECTIONS = [
  { id: "landing/problem", label: "Problem" },
  { id: "landing/route", label: "Route" },
  { id: "landing/workbench", label: "Workbench" },
  { id: "landing/proof", label: "Evidence" },
  { id: "landing/setup", label: "Run locally" },
];

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
    text: "Native AI Hub reads scoped evidence and proposes a recommendation.",
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

const SURFACES = [
  {
    href: "#investigations",
    title: "Investigations",
    text: "A queue of cases with the original payload, approved references, semantic findings, policy checks and native trace.",
  },
  {
    href: "#reviews",
    title: "Review",
    text: "Eligible holds become native review tasks. Actions need reviewer permission, a written reason and the current case version.",
  },
  {
    href: "#imports",
    title: "CSV Import",
    text: "Preview an order feed against a separate approved export, then investigate each line. Up to 20 rows and 128 KiB per file.",
  },
  {
    href: "#scenarios",
    title: "Scenario Lab",
    text: "Inject frozen synthetic scenarios into the native production and compare the observed route with ground truth.",
  },
  {
    href: "#messages",
    title: "Message Explorer",
    text: "Inspect or inject partner JSON, then follow it to its investigation and IRIS trace.",
  },
  {
    href: "#health",
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

function Heading({
  index,
  id,
  title,
  children,
}: {
  index: string;
  id: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <header className="landing-heading">
      <span className="landing-index mono" aria-hidden="true">
        {index}
      </span>
      <h2 id={id}>{title}</h2>
      <p>{children}</p>
    </header>
  );
}

export default function Landing() {
  const main = useRef<HTMLElement>(null);
  useEffect(() => {
    document.title = "SilentShift · Catch what status codes miss";
    const section = document.getElementById(window.location.hash.slice(1));
    if (section) section.scrollIntoView({ behavior: "instant", block: "start" });
    else window.scrollTo({ top: 0, behavior: "instant" });
  }, []);

  return (
    <div className="landing-page">
      <a
        className="skip"
        href="#landing/main"
        onClick={(event) => {
          event.preventDefault();
          main.current?.focus();
        }}
      >
        Skip to content
      </a>

      <header className="landing-header" id="landing">
        <div className="landing-wrap landing-header-inner">
          <a className="landing-brand" href="#landing" aria-label="SilentShift home">
            <Mark />
            <span>SilentShift</span>
          </a>
          <nav className="landing-nav" aria-label="Product sections">
            {SECTIONS.map(({ id, label }) => (
              <a key={id} href={`#${id}`}>
                {label}
              </a>
            ))}
          </nav>
          <a className="btn btn-primary" href="#investigations">
            Open workbench <ArrowRight size={15} aria-hidden="true" />
          </a>
        </div>
      </header>

      <main id="landing/main" ref={main} tabIndex={-1}>
        <section className="landing-wrap landing-hero" aria-labelledby="landing-title">
          <div className="landing-hero-copy">
            <p className="landing-eyebrow">
              <span aria-hidden="true" />
              Semantic integrity for InterSystems IRIS
            </p>
            <h1 id="landing-title">
              Catch what <span>status codes miss.</span>
            </h1>
            <p className="landing-lead">
              The request succeeded. The business meaning changed. SilentShift investigates orders
              and payments against approved evidence before anything reaches its destination.
            </p>
            <p className="landing-audience">
              For integration operations teams running B2B order and payment pipelines.
            </p>
            <div className="landing-actions">
              <a className="btn btn-primary landing-cta" href="#investigations">
                Open workbench <ArrowRight size={16} aria-hidden="true" />
              </a>
              <a className="btn btn-secondary landing-cta" href="#landing/proof">
                Inspect recorded evidence
              </a>
            </div>
            <dl className="landing-roles">
              <div>
                <dt>Investigates</dt>
                <dd>Native IRIS AI Hub</dd>
              </div>
              <div>
                <dt>Decides</dt>
                <dd>Deterministic policy</dd>
              </div>
              <div>
                <dt>Resolves</dt>
                <dd>Human reviewers, for eligible holds</dd>
              </div>
            </dl>
          </div>
          <div className="landing-hero-figure">
            <FlowPreview />
            <p className="landing-caption">
              Illustration only · synthetic values · no API or model call
            </p>
          </div>
        </section>

        <section
          className="landing-band landing-band-panel"
          id="landing/problem"
          aria-labelledby="landing-problem-title"
        >
          <div className="landing-wrap">
            <Heading index="01" id="landing-problem-title" title="Valid message. Contradicted agreement.">
              A supplier sends 20 cases. The message is valid and the delivery would succeed. The
              contract determines what happens next.
            </Heading>

            <div className="landing-entries">
              <article className="landing-entry landing-entry-hold" aria-labelledby="landing-case-a">
                <header>
                  <h3 id="landing-case-a">Case A · Unapproved unit change</h3>
                  <Badge tone="hold">
                    <X size={13} aria-hidden="true" /> Quarantine
                  </Badge>
                </header>
                <div className="landing-compare">
                  <div>
                    <span>Partner sends</span>
                    <strong className="mono">
                      20 <small>CASE</small>
                    </strong>
                  </div>
                  <span className="landing-mark" aria-hidden="true">
                    ≠
                  </span>
                  <span className="sr-only">does not match</span>
                  <div>
                    <span>Approved contract</span>
                    <strong className="mono">
                      240 <small>EA</small>
                    </strong>
                  </div>
                </div>
                <p>
                  No approved CASE-to-EA conversion exists. A plausible conversion cannot authorize
                  release.
                </p>
              </article>

              <article className="landing-entry landing-entry-allow" aria-labelledby="landing-case-c">
                <header>
                  <h3 id="landing-case-c">Case C · Approved amendment</h3>
                  <Badge tone="allow">
                    <Check size={13} aria-hidden="true" /> Allow
                  </Badge>
                </header>
                <div className="landing-compare">
                  <div>
                    <span>Partner sends</span>
                    <strong className="mono">
                      20 <small>CASE</small>
                    </strong>
                  </div>
                  <span className="landing-mark" aria-hidden="true">
                    =
                  </span>
                  <span className="sr-only">matches</span>
                  <div>
                    <span>
                      Amended contract <em>Effective · approved</em>
                    </span>
                    <strong className="mono">
                      20 <small>CASE</small>
                    </strong>
                  </div>
                </div>
                <p>
                  An effective approved amendment authorizes the 20 CASE order. Unverified
                  conversions remain blocked.
                </p>
                <a className="link" href="#scenarios">
                  Open Scenario Lab <ArrowUpRight size={14} aria-hidden="true" />
                </a>
              </article>
            </div>

            <figure className="landing-capture">
              <a
                href="/evidence/native-approved-workbench.png"
                target="_blank"
                rel="noreferrer"
                aria-label="Open full-size capture of the approved native delivery"
              >
                <picture>
                  <source media="(max-width: 600px)" srcSet="/evidence/native-approved-mobile.png" />
                  <img
                    src="/evidence/native-approved-workbench.png"
                    alt="Actual SilentShift approved-amendment investigation with an allow policy and delivery to the destination simulator."
                    width="1440"
                    height="960"
                    loading="lazy"
                  />
                </picture>
              </a>
              <figcaption>
                <Badge>Recorded capture</Badge>
                Approved-amendment case. The destination is an IRIS simulator, not an external
                business system.
              </figcaption>
            </figure>
          </div>
        </section>

        <section className="landing-band" id="landing/route" aria-labelledby="landing-route-title">
          <div className="landing-wrap">
            <Heading index="02" id="landing-route-title" title="IRIS owns the whole route.">
              One native production. A Business Process orchestrates every stage, and the AI
              recommendation never releases a message on its own.
            </Heading>
            <ol className="landing-route">
              {ROUTE.map(({ role, title, text, tone }, index) => (
                <li key={title} className={`landing-step landing-step-${tone}`}>
                  <span className="landing-step-top">
                    <span className="mono">{String(index + 1).padStart(2, "0")}</span>
                    <span className="kicker">{role}</span>
                  </span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </li>
              ))}
            </ol>
            <div className="landing-route-foot">
              <details className="disclosure plain landing-tech">
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
              <div className="landing-trace-link">
                <a
                  className="link"
                  href="/evidence/provider-calls.json"
                  target="_blank"
                  rel="noreferrer"
                >
                  Read recorded traces <ArrowUpRight size={14} aria-hidden="true" />
                </a>
                <p className="small quiet">
                  Recorded native invocation, tool and per-provider-call evidence. Current
                  verification is linked in the repository.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          className="landing-band landing-band-panel"
          id="landing/workbench"
          aria-labelledby="landing-workbench-title"
        >
          <div className="landing-wrap">
            <Heading index="03" id="landing-workbench-title" title="One workbench for every hold.">
              Every view reads the native IRIS API; there is no mock backend. Without a running
              production, the workbench says so instead of showing sample records.
            </Heading>
            <ul className="landing-surfaces">
              {SURFACES.map(({ href, title, text }) => (
                <li key={href}>
                  <a className="landing-surface" href={href}>
                    <span className="landing-surface-title">
                      {title}
                      <ArrowRight size={16} aria-hidden="true" />
                    </span>
                    <span className="landing-surface-text">{text}</span>
                  </a>
                </li>
              ))}
            </ul>
            <p className="landing-footnote small quiet">
              CSV Import delivers per line to the IRIS simulator. Whole-order completeness and
              external delivery are not verified.
            </p>
          </div>
        </section>

        <section className="landing-band" id="landing/proof" aria-labelledby="landing-proof-title">
          <div className="landing-wrap">
            <Heading index="04" id="landing-proof-title" title="Five cases. Five controlled outcomes.">
              Five synthetic scenarios, run natively in IRIS.
            </Heading>
            <div className="landing-proof">
              <div className="landing-proof-record">
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
                <div className="landing-limits">
                  <p>
                    <strong>Rule-only baseline: 5/5.</strong> No AI accuracy uplift demonstrated.
                  </p>
                  <p>November 2, 2026. Synthetic cases, not general accuracy.</p>
                  <a
                    className="link"
                    href="/evidence/native-summary.json"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Trial records, including failures <ArrowUpRight size={14} aria-hidden="true" />
                  </a>
                </div>
              </div>
              <figure className="landing-capture">
                <a
                  href="/evidence/native-currency-workbench.png"
                  target="_blank"
                  rel="noreferrer"
                  aria-label="Open full-size capture of the native currency investigation"
                >
                  <picture>
                    <source media="(max-width: 600px)" srcSet="/evidence/native-currency-mobile.png" />
                    <img
                      src="/evidence/native-currency-workbench.png"
                      alt="Actual SilentShift investigation: 12550 minor currency units contradict 125.50 major units; deterministic policy quarantines the message."
                      width="1440"
                      height="960"
                      loading="lazy"
                    />
                  </picture>
                </a>
                <figcaption>
                  <Badge>Recorded capture</Badge>
                  Native investigation of a synthetic payment event, held from the destination
                  simulator.
                </figcaption>
              </figure>
            </div>
          </div>
        </section>

        <section
          className="landing-band landing-band-panel"
          id="landing/setup"
          aria-labelledby="landing-setup-title"
        >
          <div className="landing-wrap landing-setup">
            <div>
              <Heading index="05" id="landing-setup-title" title="Start the IRIS production.">
                Load authorized build 154. Configure <code>.env</code>. No EAP kit is bundled with
                the source.
              </Heading>
              <a
                className="link"
                href="https://github.com/himanshu748/silentshift#native-build-154-setup"
                target="_blank"
                rel="noreferrer"
              >
                Get source and setup <ArrowUpRight size={14} aria-hidden="true" />
              </a>
            </div>
            <div className="landing-command">
              <div className="landing-command-head">
                <span className="kicker">Native setup</span>
                <CopyButton value={COMMANDS} label="Copy setup commands" />
              </div>
              <pre tabIndex={0} aria-label="Native setup commands">
                <code>{COMMANDS}</code>
              </pre>
              <p className="small quiet">
                Tested: <code>2026.3.0AI.154.0</code>. Kit excluded; newer versions unverified.
              </p>
            </div>
          </div>
        </section>

        <section className="landing-final" aria-labelledby="landing-final-title">
          <div className="landing-wrap landing-final-inner">
            <div>
              <h2 id="landing-final-title">Inspect a held order yourself.</h2>
              <p>
                The workbench shows the contradiction, the approved reference, the observed route
                and the next permitted action. Connect to your local production to begin.
              </p>
            </div>
            <div className="landing-final-actions">
              <a className="btn landing-cta landing-cta-invert" href="#investigations">
                Open workbench <ArrowRight size={16} aria-hidden="true" />
              </a>
              <a className="link" href="#scenarios">
                Run a Scenario Lab case <ArrowUpRight size={14} aria-hidden="true" />
              </a>
              <a className="link" href="#health">
                Check local runtime <ArrowUpRight size={14} aria-hidden="true" />
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-wrap landing-footer">
        <a className="landing-brand" href="#landing" aria-label="SilentShift home">
          <Mark size={18} />
          <span>SilentShift</span>
        </a>
        <p>Semantic integrity on InterSystems IRIS.</p>
        <Badge>Synthetic demonstration</Badge>
        <a
          className="link"
          href="https://github.com/himanshu748/silentshift"
          target="_blank"
          rel="noreferrer"
        >
          Source on GitHub <ArrowUpRight size={14} aria-hidden="true" />
        </a>
      </footer>
    </div>
  );
}
