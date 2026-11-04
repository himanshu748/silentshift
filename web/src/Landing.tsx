import { useEffect } from "react";
import { ArrowUpRight, Check, ShieldCheck, X } from "lucide-react";
import "./landing.css";
import FlowPreview from "./FlowPreview";

export default function Landing() {
  useEffect(() => {
    document.title = "SilentShift · Catch what status codes miss";
    const section = document.getElementById(window.location.hash.slice(1));
    if (section) section.scrollIntoView({ behavior: "instant", block: "start" });
    else window.scrollTo({ top: 0, behavior: "instant" });
  }, []);

  return (
    <div className="landing-page">
      <a className="landing-skip" href="#landing/main">Skip to content</a>
      <header className="landing-header" id="landing">
        <div className="landing-container landing-nav">
          <a className="landing-brand" href="#landing" aria-label="SilentShift home">
            <img src="/favicon.svg" alt="" width="32" height="32" />
            <span>SilentShift.</span>
          </a>
          <nav aria-label="Product navigation">
            <a href="#landing/proof">Evidence</a>
            <a href="#landing/setup">Run locally</a>
          </nav>
          <a className="landing-nav-action" href="#investigations">Open workbench <ArrowUpRight size={16} aria-hidden="true" /></a>
        </div>
      </header>
      <main id="landing/main" tabIndex={-1}>
        <section className="landing-container landing-hero" aria-labelledby="landing-title">
          <div className="landing-hero-heading">
            <div>
              <div className="landing-product-label"><span /> Semantic integrity for IRIS</div>
              <h1 id="landing-title">Catch what <br /><span>status codes miss.</span></h1>
              <p>The request succeeded. The business meaning changed. Investigate orders and payments against approved evidence before anything reaches its destination.</p>
              <div className="landing-actions">
                <a className="landing-button landing-primary" href="#investigations">Open workbench <ArrowUpRight size={18} aria-hidden="true" /></a>
                <a className="landing-button landing-secondary" href="#landing/proof">Inspect measured evidence</a>
              </div>
            </div>
          </div>
          <FlowPreview />
        </section>
        <div className="landing-tech-strip landing-container"><span>One native production.</span><span>AI Hub investigation</span><span>Deterministic policy</span><span>Human review</span><span>Visual Trace</span></div>
        <section className="landing-container landing-contrast" aria-labelledby="landing-contract-title">
          <div className="landing-section-heading">
            <h2 id="landing-contract-title">Changed units need approved evidence.</h2>
            <p>A supplier sends 20 cases. The contract determines what happens next.</p>
          </div>
          <div className="landing-contrast-layout">
            <div className="landing-contract-comparison">
              <article>
                <h3>A: Unapproved unit change</h3>
                <dl>
                  <div><dt>Partner sends</dt><dd>20 CASE</dd></div>
                  <div><dt>Approved contract</dt><dd>240 EA</dd></div>
                </dl>
                <p className="landing-case-verdict landing-held"><X size={16} aria-hidden="true" /> Quarantine</p>
              </article>
              <article>
                <h3>C: Approved amendment</h3>
                <dl>
                  <div><dt>Partner sends</dt><dd>20 CASE</dd></div>
                  <div><dt>Approved contract</dt><dd>20 CASE</dd></div>
                </dl>
                <p className="landing-case-verdict landing-allowed"><Check size={16} aria-hidden="true" /> Allow</p>
              </article>
            </div>
            <div className="landing-contrast-note">
              <ShieldCheck size={24} strokeWidth={1.5} aria-hidden="true" />
              <p>An effective approved amendment authorizes case C. Unverified conversions remain blocked.</p>
              <a className="landing-text-link" href="#scenarios">Open Scenario Lab <ArrowUpRight size={16} aria-hidden="true" /></a>
            </div>
          </div>
          <figure className="landing-approved-capture">
            <a href="/evidence/native-approved-workbench.png" target="_blank" rel="noreferrer" aria-label="Open full-size capture of the approved native delivery">
              <picture>
                <source media="(max-width: 600px)" srcSet="/evidence/native-approved-mobile.png" />
                <img src="/evidence/native-approved-workbench.png" alt="Actual SilentShift approved-amendment investigation with an allow policy and delivery to the destination simulator." width="1440" height="960" loading="lazy" />
              </picture>
            </a>
            <figcaption>Recorded approved-amendment case. The destination is an IRIS simulator, not an external business system.</figcaption>
          </figure>
        </section>
        <section className="landing-pipeline" id="landing/pipeline" aria-labelledby="landing-pipeline-title">
          <div className="landing-container">
            <div className="landing-section-heading">
              <h2 id="landing-pipeline-title">IRIS owns the whole route.</h2>
              <p>Business Process orchestrates every stage.</p>
            </div>
            <ol className="landing-stages">
              <li><h3>1. Receive in IRIS</h3><p>Business Service preserves original payloads.</p><code>SilentShift.Service.Partner</code></li>
              <li><h3>2. Investigate the evidence</h3><p>Native AI Hub investigates scoped evidence.</p><code>SilentShift.AI.Investigator</code></li>
              <li><h3>3. Validate the permission</h3><p>Embedded Python blocks unverified release.</p></li>
              <li><h3>4. Route and preserve</h3><p>Business Operations persist every outcome.</p><code>SilentShift.Production</code></li>
            </ol>
            <a className="landing-text-link" href="/evidence/provider-calls.json" target="_blank" rel="noreferrer">Read recorded traces <ArrowUpRight size={16} aria-hidden="true" /></a>
            <p className="landing-scope-note">Recorded native invocation, tool and per-provider-call evidence. Current verification is linked in the repository.</p>
          </div>
        </section>
        <section className="landing-container landing-proof" id="landing/proof" aria-labelledby="landing-proof-title">
          <div className="landing-section-heading">
            <h2 id="landing-proof-title">Five cases. Five controlled outcomes.</h2>
            <p>Five synthetic scenarios, run natively in IRIS.</p>
          </div>
          <table className="landing-proof-table">
            <thead><tr><th scope="col">Scenario</th><th scope="col">Observed policy</th></tr></thead>
            <tbody>
              <tr><th scope="row">Quantity-unit mismatch</th><td><span className="landing-held">Quarantine</span></td></tr>
              <tr><th scope="row">Currency-scale mismatch</th><td><span className="landing-held">Quarantine</span></td></tr>
              <tr><th scope="row">Approved contract amendment</th><td><span className="landing-allowed">Allow</span></td></tr>
              <tr><th scope="row">Conflicting references</th><td><span className="landing-review">Request review</span></td></tr>
              <tr><th scope="row">Labeled unsafe-proposal injection</th><td><span className="landing-held">Quarantine</span></td></tr>
            </tbody>
          </table>
          <div className="landing-proof-notes">
            <p>Rule-only baseline: 5/5. No AI accuracy uplift demonstrated.</p>
            <a className="landing-text-link" href="/evidence/native-summary.json" target="_blank" rel="noreferrer">Trial records, including failures <ArrowUpRight size={16} aria-hidden="true" /></a>
          </div>
          <p className="landing-scope-note">November 2, 2026. Synthetic cases, not general accuracy.</p>
          <figure className="landing-product">
            <a href="/evidence/native-currency-workbench.png" target="_blank" rel="noreferrer" aria-label="Open full-size capture of the native currency investigation">
              <picture>
                <source media="(max-width: 600px)" srcSet="/evidence/native-currency-mobile.png" />
                <img src="/evidence/native-currency-workbench.png" alt="Actual SilentShift investigation: 12550 minor currency units contradict 125.50 major units; deterministic policy quarantines the message." width="1440" height="960" fetchPriority="high" />
              </picture>
            </a>
            <figcaption>Recorded native investigation, synthetic payment event held from the destination simulator.</figcaption>
          </figure>

        </section>
        <section className="landing-setup" id="landing/setup" aria-labelledby="landing-setup-title">
          <div className="landing-container landing-setup-layout">
            <div>
              <h2 id="landing-setup-title">Start the IRIS production.</h2>
              <p>Load authorized build 154. Configure <code>.env</code>.</p>
              <p><a className="landing-text-link" href="https://github.com/himanshu748/silentshift#native-build-154-setup" target="_blank" rel="noreferrer">Get source and setup <ArrowUpRight size={16} aria-hidden="true" /></a></p>
              <a className="landing-text-link" href="#health">Check local runtime <ArrowUpRight size={16} aria-hidden="true" /></a>
            </div>
            <div className="landing-command">
              <pre tabIndex={0} aria-label="Native setup commands"><code>{"uv run --env-file .env python scripts/doctor.py\nuv run --env-file .env python scripts/bootstrap.py"}</code></pre>
              <p>Tested: <code>2026.3.0AI.154.0</code>. Kit excluded; newer versions unverified.</p>
            </div>
          </div>
        </section>
      </main>
      <footer className="landing-footer landing-container">
        <a className="landing-brand" href="#landing" aria-label="SilentShift home"><img src="/favicon.svg" alt="" width="24" height="24" /><span>SilentShift.</span></a>
        <p>Semantic integrity on InterSystems IRIS.</p>
        <a href="https://github.com/himanshu748/silentshift" target="_blank" rel="noreferrer">Source on GitHub <ArrowUpRight size={14} aria-hidden="true" /></a>
      </footer>
    </div>
  );
}
