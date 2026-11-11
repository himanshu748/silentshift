"""Publish a selection of existing observations. Never evaluate or invoke a model."""
import argparse
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "7ae03be03ac6721639e83bdd9e3ed07a5350649e"
GITHUB = f"https://github.com/himanshu748/silentshift/blob/{SOURCE_COMMIT}/"
SELECTED = (("HO-045", "The quantity changed in prose", "contract_text"),
            ("HO-030", "The buyer cancelled the order", "buyer_po_note"),
            ("HO-017", "The old part was explicitly prohibited", "buyer_po_note"))
esc = html.escape


def read(path):
    return json.loads((ROOT / path).read_text())


def source(path):
    return {"path": path, "url": GITHUB + path,
            "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}


def build_data():
    summary_path = "evidence/heldout/summary.json"
    summary = read(summary_path)
    fixtures_path = "fixtures/v2-heldout/scenarios.json"
    fixtures = read(fixtures_path)
    rules_path = "evidence/heldout/rules-only.json"
    rules = {r["scenario_id"]: r for r in read(rules_path)["cases"]}
    assert source(fixtures_path)["sha256"] == summary["dataset_sha256"]
    cases = []
    for ident, title, clause_field in SELECTED:
        fixture = next(r for r in fixtures["scenarios"] if r["id"] == ident)
        trials = []
        for trial in (1, 2, 3):
            path = f"evidence/heldout/trial-{trial}/{ident}.json"
            raw = read(path)
            record = raw["record"]
            assert raw["dataset_sha256"] == summary["dataset_sha256"]
            assert fixture["category"] == "unstructured"
            assert rules[ident]["decision"] == "ALLOW"
            assert fixture["ground_truth"]["decision"] == record["recommendation"]["decision"] == "QUARANTINE"
            assert record["policy"]["decision"] == "REQUEST_REVIEW"
            assert record["delivery_count"] == 0
            assert record["workflow"]["status"] == "pending"
            assert record["review"] is None
            assert all(e in {r["id"] for r in record["references"]} for e in record["recommendation"]["evidence_ids"])
            trials.append({"trial": trial, "source": source(path), "case_id": raw["case_id"],
                           "session_id": raw["trace_id"], "message": record["message"],
                           "references": record["references"], "recommendation": record["recommendation"],
                           "policy": record["policy"], "workflow": record["workflow"],
                           "delivery_count": record["delivery_count"], "review": record["review"]})
        cases.append({"id": ident, "title": title, "clause_field": clause_field,
                      "category": fixture["category"], "truth": fixture["ground_truth"],
                      "baseline": rules[ident], "trials": trials})
    return {"schema": "silentshift-agent-value/1", "synthetic": True,
            "scope": "Presentation of existing November 9 observations; not a new evaluation",
            "sources": [source(summary_path), source("docs/EVAL_HELDOUT.md"), source(fixtures_path), source(rules_path)],
            "runtime": summary["manifest"]["identity"]["runtime"],
            "historical_module_version": summary["manifest"]["identity"]["module_version"],
            "source_commit": summary["manifest"]["source_commit"],
            "totals": summary["totals"], "trials": summary["trials"],
            "categories": summary["categories"], "cases": cases}


def metric_block(data):
    base = data["totals"]["rules-only"]
    shipped = data["totals"]["agent+policy"]
    trials = list(data["trials"]["agent+policy"].values())
    assert (base["n"], base["wrong_deliveries"], base["bad_orders"], [r["wrong_deliveries"] for r in trials]) == (48, 6, 23, [2, 3, 3])
    return f'''<aside class="heldout-summary" aria-label="Recorded held-out result">
<p class="eyebrow">Recorded comparison · {base['n']} synthetic orders</p>
<p class="heldout-main"><strong>6/23 → 2–3/23</strong> wrong deliveries</p>
<p>Rules-only release choices are counterfactual. Agent + policy counts actual simulator receipts in three trials.</p>
<p><strong>Review: {base['review_rate']:.1%} → {shipped['review_rate']:.1%}</strong> (pooled agent trials).</p>
<p class="heldout-limit"><strong>No overall accuracy gain:</strong> correct routes {base['correct']}/{base['n']} → {', '.join(str(r['correct'])+'/48' for r in trials)}. Unstructured routing stays 1/16 in every trial.</p>
<a href="{GITHUB}docs/EVAL_HELDOUT.md">Read the full comparison and every failure ↗</a>
</aside>'''


def render_case(case):
    record = case["trials"][0]
    reference = record["references"][0]
    evidence = reference[case["clause_field"]]
    baseline = case["baseline"]
    proposal = record["recommendation"]
    message = record["message"]
    trial_rows = "".join(f'<tr><th scope="row">{t["trial"]}</th><td>{esc(t["recommendation"]["decision"])}</td><td>{esc(t["policy"]["decision"])}</td><td>{esc(t["workflow"]["task_id"])}</td><td>{t["delivery_count"]}</td><td><a href="{t["source"]["url"]}">Raw trial {t["trial"]}</a></td></tr>' for t in case["trials"])
    return f'''<article class="value-case" id="{case['id']}" aria-labelledby="title-{case['id']}">
<header><p class="eyebrow">{case['id']} · unstructured · recorded trial 1</p><h2 id="title-{case['id']}">{esc(case['title'])}</h2>
<p class="value-order">Incoming: <strong>{esc(message['quantity'])} {esc(message['unit'])} · {esc(message['product_id'])}</strong></p></header>
<div class="value-clause"><p class="eyebrow">01 / The governing text · {esc(reference['id'])}</p><blockquote>{esc(evidence)}</blockquote>
<p class="value-note">Verbatim <code>record.references[0].{case['clause_field']}</code>. Synthetic approved-source provenance is stipulated; no real sender was authenticated.</p></div>
<div class="value-comparison"><section><p class="eyebrow">02 / Rules-only · counterfactual</p><h3>{esc(baseline['decision'])}</h3><p>Structured assessment: <strong>{esc(baseline['assessment']['classification'])}</strong>. The incoming structured fields matched the table; the deciding text above did not change this baseline result.</p><a href="{GITHUB}evidence/heldout/rules-only.json">Original rule record · {case['id']} ↗</a></section>
<section><p class="eyebrow">03 / Raw AI Hub recommendation</p><h3>{esc(proposal['decision'])}</h3><blockquote>{esc(proposal['explanation'])}</blockquote><p>Cited evidence: <code>{esc(', '.join(proposal['evidence_ids']))}</code></p><a href="{record['source']['url']}">Original recommendation and reference ↗</a></section></div>
<section class="value-policy"><p class="eyebrow">04 / Deterministic policy · recorded outcome</p><h3>{esc(record['policy']['decision'])} · no simulator delivery</h3><blockquote>{esc(' '.join(record['policy']['reasons']))}</blockquote>
<p>The concern is retained with a native Workflow task. Recorded task <code>{esc(record['workflow']['task_id'])}</code> status: <strong>{esc(record['workflow']['status'])}</strong>; no reviewer decision or eventual delivery is recorded here.</p>
<p><strong>Reviewer assist, not a correct final three-way route:</strong> the frozen label is <code>{esc(case['truth']['decision'])}</code>. The raw agent matches it; the shipped <code>REQUEST_REVIEW</code> is still scored incorrect. Containment is a narrower result than correct routing.</p></section>
<details><summary>Inspect all three recorded trials and the frozen label</summary><p>Frozen reason: {esc(case['truth']['reason'])}</p><p><a href="{GITHUB}fixtures/v2-heldout/scenarios.json">Frozen dataset · {case['id']}</a>. Labels were written before these runs. These examples were selected after results were known.</p>
<div class="value-table" role="region" tabindex="0" aria-label="{case['id']} all recorded trials"><table><caption>{case['id']}: all existing trials, no reruns</caption><thead><tr><th scope="col">Trial</th><th scope="col">Agent</th><th scope="col">Policy</th><th scope="col">Task</th><th scope="col">Deliveries</th><th scope="col">Source</th></tr></thead><tbody>{trial_rows}</tbody></table></div>
<dl><dt>Trial 1 native case</dt><dd>{esc(record['case_id'])}</dd><dt>Original local session</dt><dd>{esc(record['session_id'])}</dd></dl>
<details><summary>Read the complete contract snapshot</summary><pre>{esc(json.dumps(reference, indent=2))}</pre></details></details></article>'''


def build_html(data):
    cards = "\n".join(render_case(c) for c in data["cases"])
    links = "".join(f'<a href="#{c["id"]}">{c["id"]} · {esc(c["title"])}</a>' for c in data["cases"])
    return f'''<!doctype html>
<html lang="en"><head><link rel="preload" href="assets/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/ibm-plex-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>What the agent saw — SilentShift</title><meta name="description" content="Three recorded synthetic held-out cases: rules choose ALLOW, the agent cites contrary prose, and deterministic policy creates a human-review hold. Read the full measured trade-off."><link rel="icon" href="assets/mark.png"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="agent-value.css"></head><body>
<a class="skip-link" href="#main">Skip to agent evidence</a><header class="site-header wrap"><a class="brand" href="./" aria-label="SilentShift home"><img src="assets/mark.png" width="32" height="32" alt=""><span>SilentShift<span class="brand-stop">.</span></span></a><nav aria-label="Primary navigation"><a href="evidence-tour.html">Evidence tour</a><a href="receipts.html">Receipt inspector</a></nav></header>
<main id="main" tabindex="-1" class="wrap value-main"><section class="value-intro"><p class="eyebrow">The agent's contribution, in the record</p><h1>What the agent saw<br><em>that the rules missed.</em></h1><p>Three held-out orders matched their structured tables. The agent cited contrary prose. Policy kept the concern and sent the case to a human, rather than automatically delivering it.</p><p class="value-note">Historical synthetic observations, recorded November 9 on 154U ARM64. No new inference, evaluation or native connection. Current native package: 0.3.2; separate React workbench: 0.2.1. This historical comparison predates that release.</p></section>
{metric_block(data)}
<nav class="value-index" aria-label="Recorded examples">{links}</nav>
{cards}
<section class="value-limits"><p class="eyebrow">Read the result at its actual scope</p><h2>A useful finding.<br>Not a universal accuracy claim.</h2><p>These are selected examples, not additional evaluation cases. The same 48 orders repeat across three paired agent trials. The review-rate comparison uses 6/48 rules decisions and 31/144 agent-plus-policy decisions. Three trials do not establish statistical superiority.</p><p>Unstructured exact routing remains 1/16 for both arms in each trial. Rules also beat the agent on cases retained in the complete report. All outcomes are synthetic; delivery is only to the simulator. No completed human resolution is implied by a pending Workflow task.</p><p><a href="{GITHUB}docs/EVAL_HELDOUT.md">Full report, failures and rules wins</a> · <a href="{GITHUB}evidence/heldout/summary.json">Original summary</a> · <a href="assets/agent-value.json">Presentation extract with source hashes</a></p></section></main>
<footer class="wrap value-footer">Synthetic data. Evaluation build. Recorded evidence, not a hosted native demo. <a href="./">Back to SilentShift</a></footer></body></html>\n'''


def build_markdown(data):
    text = """# What the agent saw that the rules missed

On the existing **48 held-out synthetic orders**, rules-only would release **6/23** release-ineligible orders. Agent + policy produced **2/23, 3/23 and 3/23 actual wrong simulator deliveries**. Review increased from **12.5%** to **21.5%** across pooled agent trials.

**No overall accuracy gain:** correct routes were **33/48** for rules and **33/48, 33/48 and 30/48** for agent + policy. Unstructured exact routing stayed **1/16** in every trial. [Full report](EVAL_HELDOUT.md) · [original summary](../evidence/heldout/summary.json).

These are three selected November 9 observations, not new evaluation cases. In each, the raw agent matches the frozen QUARANTINE label and the baseline chooses ALLOW. Policy creates REQUEST_REVIEW instead: no simulator delivery, but still an incorrect final three-way label. This demonstrates **reviewer assist**, not autonomous resolution or a general accuracy improvement.

The pending native Workflow task retains the cited concern. No completed reviewer decision is recorded. Synthetic approved-source provenance is stipulated; no actual buyer identity or document authenticity was verified. The historical code checkpoint predates current native 0.3.2 / React 0.2.1.

The interactive static view is in [agent-value.html](site/agent-value.html). Its public Pages URL is prepared for the separately approved deployment, not claimed live by this branch.
"""
    for c in data["cases"]:
        t = c["trials"][0]
        ref = t["references"][0]
        text += f"""
<a id="{c['id'].lower()}"></a>

## {c['id']} — {c['title']}

Incoming: **{t['message']['quantity']} {t['message']['unit']} of {t['message']['product_id']}**.

> {ref[c['clause_field']]}

This is verbatim `record.references[0].{c['clause_field']}` from [trial 1]({t['source']['url']}).

- **Rules-only:** {c['baseline']['decision']}, structured assessment {c['baseline']['assessment']['classification']}. [Original baseline]({GITHUB}evidence/heldout/rules-only.json), scenario `{c['id']}`.
- **Raw agent:** {t['recommendation']['decision']}. “{t['recommendation']['explanation']}” Cites `{', '.join(t['recommendation']['evidence_ids'])}`.
- **Final policy:** {t['policy']['decision']}. “{' '.join(t['policy']['reasons'])}”
- **Consequence:** {t['delivery_count']} simulator deliveries; Workflow task `{t['workflow']['task_id']}` is `{t['workflow']['status']}`. Native case `{t['case_id']}`, session `{t['session_id']}`. No human resolution is recorded.
- **Frozen truth:** {c['truth']['decision']}. {c['truth']['reason']} [Frozen dataset]({GITHUB}fixtures/v2-heldout/scenarios.json).

| Existing trial | Raw agent | Final policy | Workflow task | Simulator deliveries | Original record |
| --- | --- | --- | --- | ---: | --- |
"""
        for trial in c["trials"]:
            text += f"| {trial['trial']} | {trial['recommendation']['decision']} | {trial['policy']['decision']} | {trial['workflow']['task_id']} | {trial['delivery_count']} | [Raw JSON]({trial['source']['url']}) |\n"
    return text + "\n## Read the wider result\n\nExamples were selected after results were known. The same 48 cases repeat across three paired agent trials; they are not 144 independent orders. The review denominators are 6/48 and 31/144. Three trials do not establish statistical superiority. Rules also beat the agent on cases retained in the [complete failure table](EVAL_HELDOUT.md#every-failure). No label or raw observation was changed. No model, native API, policy or evaluation was run to build this presentation.\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = build_data()
    outputs = {"docs/site/assets/agent-value.json": json.dumps(data, indent=2) + "\n",
               "docs/site/agent-value.html": build_html(data),
               "docs/AGENT_VALUE.md": build_markdown(data)}
    for name, content in outputs.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f"Presentation differs from recorded source: {name}")
        else:
            path.write_text(content)
    print("Recorded presentation matches existing source; no evaluation executed.")


if __name__ == "__main__":
    main()
