#!/usr/bin/env python3
"""Report every frozen held-out result, including invalids and lost comparisons."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import mean, median, pstdev

from heldout_metrics import raw_proposal, score_row, summarize, ROUTES
from run_heldout import ROOT, DATA_SHA, LABEL_COMMIT, frozen_dataset, write_json
from silentshift.engine import strict_loads, _recommendation_errors


def report(source: Path, destination: Path):
    dataset = frozen_dataset()
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest["status"] != "completed" or manifest["completed"] != 144:
        raise ValueError("Report refused: all 144 preregistered native investigations must be retained")
    cases = {c["id"]: c for c in dataset["scenarios"]}
    rule_export = json.loads((source / "rules-only.json").read_text())
    if rule_export["dataset_sha256"] != DATA_SHA or len(rule_export["cases"]) != 48:
        raise ValueError("Rules-only coverage or input digest mismatch")
    arms = {"rules-only": [], "agent-only": [], "agent+policy": []}
    rule_predictions = {}
    for r in rule_export["cases"]:
        c = cases[r["scenario_id"]]
        if c["id"] in rule_predictions:
            raise ValueError("Duplicate baseline result")
        rule_predictions[c["id"]] = r["decision"]
        arms["rules-only"].append(score_row(c, r["decision"], elapsed_ms=r["elapsed_ms"]))
    observations = []
    for trial in range(1,4):
        for c in dataset["scenarios"]:
            r = json.loads((source / f"trial-{trial}" / (c["id"] + ".json")).read_text())
            if (r["dataset_sha256"] != DATA_SHA or r["trial"] != trial or r["scenario_id"] != c["id"]
                    or r["run_id"] != manifest["run_id"] or not r["semantic_inputs_match_frozen"]):
                raise ValueError("Native result identity mismatch")
            record = r["record"]
            agent = record.get("agent") or {}
            common = {"elapsed_ms": agent.get("elapsed_ms"), "trial": trial,
                "case_id": r["case_id"], "trace_id": r["trace_id"]}
            raw = raw_proposal(record)
            try:
                content=agent.get('raw_response') or record.get('recommendation')
                parsed=strict_loads(content) if isinstance(content,str) else content
                schema_errors=_recommendation_errors(parsed,set((record.get('assessment') or {}).get('evidence_ids',[])))
            except (ValueError,TypeError,RecursionError):
                schema_errors=['Response is not strict JSON']
            routed = ROUTES.get(record["routing"], "INVALID")
            delivery = record.get("delivery_count")
            if not isinstance(delivery, int) or isinstance(delivery,bool) or delivery < 0:
                raise ValueError("Observed delivery receipt count is missing")
            arms["agent-only"].append(score_row(c, raw, **common))
            arms["agent+policy"].append(score_row(c, routed, delivery_count=delivery, **common))
            observations.append({"scenario_id":c["id"], "trial":trial, "case_id":r["case_id"],
                "agent_status":agent.get("status"), "failure_code":agent.get("failure_code"),
                "model":agent.get("model"), "prompt_version":agent.get("prompt_version"),
                "model_invoked":agent.get("model_invoked"), "tool_reads":agent.get("tool_reads"),
                "raw_output_schema_valid":not schema_errors,"raw_output_schema_errors":schema_errors,
                "provider_response_count":sum(x.get("event_kind")=="provider_response" for x in r["provider_export"].get("provider_messages",[])),
                "service_elapsed_ms":r.get("service_elapsed_ms")})
    totals = {name:summarize(rows) for name,rows in arms.items()}
    splits = {name:{cat:summarize([r for r in rows if r["category"]==cat]) for cat in ("structured","unstructured","clean")} for name,rows in arms.items()}
    by_trial = {name:{str(t):summarize([r for r in rows if r["trial"]==t]) for t in range(1,4)} for name,rows in arms.items() if name!="rules-only"}
    trial_splits = {name:{str(t):{cat:summarize([r for r in rows if r["trial"]==t and r["category"]==cat]) for cat in ("structured","unstructured","clean")} for t in range(1,4)} for name,rows in arms.items() if name!="rules-only"}
    failures = {name:[r for r in rows if not r["correct"]] for name,rows in arms.items()}
    rules_win = {name:[r for r in failures[name] if rule_predictions[r["scenario_id"]]==r["truth"]] for name in ("agent-only","agent+policy")}
    per_case = {}
    for sid in cases:
        times = [r["elapsed_ms"] for r in arms["agent-only"] if r["scenario_id"]==sid and isinstance(r["elapsed_ms"],(int,float))]
        per_case[sid] = {"agent_investigation_median_ms":median(times) if times else None,
            "agent_predictions":[r["prediction"] for r in arms["agent-only"] if r["scenario_id"]==sid],
            "shipped_predictions":[r["prediction"] for r in arms["agent+policy"] if r["scenario_id"]==sid]}
    variation = {name:{"correct_counts":[by_trial[name][str(t)]["correct"] for t in range(1,4)],
        "correct_count_population_sd":pstdev(by_trial[name][str(t)]["correct"] for t in range(1,4)),
        "cases_with_varying_predictions":sum(len(set(per_case[sid]["agent_predictions" if name=="agent-only" else "shipped_predictions"]))>1 for sid in cases)} for name in by_trial}
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"dataset_sha256":DATA_SHA,"label_commit":LABEL_COMMIT,
        "manifest":manifest,"totals":totals,"categories":splits,"trials":by_trial,"trial_categories":trial_splits,
        "variation":variation,"failures":failures,"rules_beat_agent":rules_win,"per_case":per_case,"native_observations":observations}
    write_json(source/"summary.json",result)
    def metric_row(label, s):
        latency = f"{s['median_elapsed_ms']:.3f}" if s['median_elapsed_ms'] is not None else "unavailable"
        return f"| {label} | {s['correct']}/{s['n']} | {s['wrong_deliveries']}/{s['bad_orders']} | {s['false_holds']}/{s['allow_eligible']} | {s['reviews']}/{s['n']} ({s['review_rate']:.1%}) | {s['invalid']} | {latency} |"
    lines=["# Held-out synthetic comparison", "", "## Result", ""]
    base_wrong=totals['rules-only']['wrong_deliveries']
    policy_wrong=mean(by_trial['agent+policy'][str(t)]['wrong_deliveries'] for t in range(1,4))
    base_unstructured=splits['rules-only']['unstructured']['correct']
    policy_unstructured=mean(trial_splits['agent+policy'][str(t)]['unstructured']['correct'] for t in range(1,4))
    if policy_wrong>=base_wrong:
        lines.append(f"**Agent + policy does not beat rules-only on wrong deliveries:** rules-only recommends release for {base_wrong} bad orders; shipped policy has {policy_wrong:g} actual wrong simulator deliveries per trial on average.")
    else:
        lines.append(f"Agent + policy has fewer wrong deliveries on this synthetic set: rules-only recommends release for {base_wrong} bad orders; shipped policy has {policy_wrong:g} actual wrong simulator deliveries per trial on average. The baseline effect is counterfactual; only the shipped arm executes simulator delivery.")
    lines.append("")
    if policy_unstructured<=base_unstructured:
        lines.append(f"**Agent + policy does not beat rules-only on correct routes in the unstructured split:** baseline {base_unstructured}/16; shipped policy averages {policy_unstructured:g}/16 across three trials.")
    else:
        lines.append(f"Agent + policy has more correct routes in the unstructured split on this set: baseline {base_unstructured}/16; shipped policy averages {policy_unstructured:g}/16 across three trials. This is not a real-world accuracy or productivity estimate.")
    lines += ["", "## Frozen inputs and execution", "",
        f"Labels were committed first at `{LABEL_COMMIT}`; exact input SHA-256: `{DATA_SHA}`. No label, reason, category, clock or input was edited after execution. [Frozen protocol](../fixtures/v2-heldout/FROZEN.md) · [dataset](../fixtures/v2-heldout/scenarios.json).",
        "", "There are **48 synthetic orders**: **16 structured, 16 unstructured, 16 clean**. Unstructured examples include signed prose amendments, buyer PO notes, verified superseding emails, text-only conversion clauses and conflicting references. Synthetic approved-source provenance is stipulated; the application did not authenticate an email sender.",
        "", "The native target is **2026.3.0AI.154.0 Community / 154U ARM64**, source-loaded native **0.3.0**, local `qwen3-silentshift:4b-instruct`, prompt `silentshift-investigator/1.3.1`. Rules and policy are unchanged. No paid provider, other build, README change, IPM publication or OEX edit occurred. The operator-only evaluation harness is excluded from module.xml.",
        "", "The unchanged baseline executed once per case **inside IRIS Embedded Python**. The **144 native investigations** are three fresh trials of every case, in the frozen shuffled order. Agent-only and agent + policy are **paired projections of the same three model draws**, not six independent runs. Agent-only reads the raw final response, including attempted output retained when tool verification fails; it sees the released candidate assessment and tools. The shipped arm uses persisted routing and simulator receipt counts. Distinct synthetic scenario scopes isolate same-contract history; held-out results were not indexed as precedent vectors.",
        "", "Correct routes require the exact three-way label. A non-ALLOW truth released by the baseline/raw agent is a **counterfactual wrong-delivery choice**; the shipped arm requires an **actual local simulator receipt**. False holds include quarantine, review or invalid decisions on ALLOW truth. Invalids stay in all denominators and are not silently counted as review. A valid decision token in otherwise schema-invalid JSON remains the raw agent choice; policy may reject its schema independently.",
        "", "## Overall results", "", "Pooled agent denominators repeat the same 48 cases three times; they are **not 144 independent orders**. Wrong-delivery and false-hold denominators are respectively non-ALLOW and ALLOW truth counts.", "",
        "| Arm | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median time (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    lines += [metric_row(name,totals[name]) for name in arms]
    lines += ["", "Baseline timing covers only assessment + rule selection inside Embedded Python. Agent timing covers the native investigator operation and is shared by both paired arms; it excludes other service stages. These timing scopes differ and do not establish an end-to-end speedup.", "", "## Three-trial variance", "",
        "| Arm / trial | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median investigation (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name in by_trial:
        for t in range(1,4):lines.append(metric_row(f"{name} / {t}",by_trial[name][str(t)]))
    for name,v in variation.items():
        lines += ["",f"{name}: correct-count population SD **{v['correct_count_population_sd']:.3f}** across three trials; **{v['cases_with_varying_predictions']} / 48** cases changed their predicted route. Three trials are too few for a reliable statistical superiority claim."]
    times=[r['service_elapsed_ms'] for r in observations if isinstance(r.get('service_elapsed_ms'),(int,float))]
    lines += ["", f"Native service end-to-end median: **{median(times):.3f} ms**, across **{len(times)}** timed investigations. The raw JSON also records harness wall time separately. Per-case three-trial median investigation times and prediction sequences are in [summary.json](../evidence/heldout/summary.json).", "", "## Category results", "",
        "| Arm / category | Correct routes | Wrong deliveries / bad orders | False holds / eligible | Review rate | Invalid | Median time (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name in arms:
        for cat in ('structured','unstructured','clean'):lines.append(metric_row(f"{name} / {cat}",splits[name][cat]))
    lines += ["", "Per-trial split correct routes (every other split metric is retained in summary.json):", "", "| Arm / trial | Structured | Unstructured | Clean |", "| --- | ---: | ---: | ---: |"]
    for name in trial_splits:
        for t in range(1,4):
            values=[trial_splits[name][str(t)][cat]['correct'] for cat in ('structured','unstructured','clean')]
            lines.append(f"| {name} / {t} | {values[0]}/16 | {values[1]}/16 | {values[2]}/16 |")
    lines += ["", "## Every failure", "", "No failures are omitted. `HO-*` identifies the frozen scenario; UUID/session identify the actual native case/Visual Trace. Rule-only evaluations do not create business cases. Frozen one-line contractual reasons are in the dataset. `Rules win` marks a correct baseline and incorrect agent arm."]
    for name in arms:
        lines += ["",f"### {name}","",f"**{len(failures[name])} failures.**","", "| Scenario | Category | Trial | Truth | Observed | Native case / session | Rules win |", "| --- | --- | ---: | --- | --- | --- | --- |"]
        for r in failures[name]:
            native=f"{r['case_id']} / {r['trace_id']}" if r['case_id'] else 'not applicable: baseline function'
            win='yes' if name!='rules-only' and rule_predictions[r['scenario_id']]==r['truth'] else '—'
            lines.append(f"| {r['scenario_id']} | {r['category']} | {r['trial'] or '—'} | {r['truth']} | {r['prediction']} | {native} | {win} |")
    status_counts=Counter(r['agent_status'] for r in observations)
    invalid_schema=sum(not r['raw_output_schema_valid'] for r in observations)
    lines += ["", "## Limits and interpretation", "",
        "- This is a small, synthetic, implementation-aware, contract-first challenge set; it was not independently human-adjudicated. Freezing before execution prevents output-driven relabelling, not author or selection bias. It is held out from the original five-case demo, not a randomly sampled production workload.",
        "- The prose cases deliberately supply authoritative text with stale structured export columns. That probes a broader business-semantic task than the shipped structured-authority policy promises. The released prompt includes candidate findings and requires quarantine of current critical contradictions; this can anchor the agent to the structured baseline. Policy vetoes may prevent a correct prose-based recommendation from releasing an order. No runtime/prompt change was made to fix this limitation.",
        "- A prose authority assumption in these synthetic contracts is not evidence of real buyer identity, legal enforceability or external document authenticity. Clean false-positive traps and unstructured scenarios must not be marketed as measured customer coverage.",
        "- Agent-only is a raw recommendation ablation, not a separately deployed autonomous system. Neither baseline nor raw-agent counterfactual ALLOW recommendations caused delivery. All observed deliveries are local simulator effects; no external ERP/bank was contacted.",
        f"- Native agent statuses: `{dict(status_counts)}`. Invalid outputs and failed invocations remain counted. Route/effect discrepancies in shipped arm: **{totals['agent+policy']['route_effect_discrepancies']}**. See every raw record for failure stage, tool reads and provider metadata.",
        f"- **{invalid_schema} / 144** raw responses fail the released output-schema checks (separate from the invalid-decision count). A recognizable raw decision in a schema-invalid object is still scored as that agent-only choice. Schema errors for every response are in summary.json.",
        "- One harness preparation error called a private reference-seeding method before any held-out case or inference existed. It was repaired in test-only code; the failed attempt is retained. Rules-only results were preserved. No selective model rerun or label edit was used.",
        "", "## Reproduce and inspect", "", "The first run uses an isolated source-loaded live 154U instance prepared with the existing local verification driver. Setup's original native suite, five live demo cases, warmup and embedding preparation are **outside** the held-out denominators. Local Docker storage was expanded without deleting existing projects or weakening the storage floor. [Environment/setup receipt](../evidence/heldout/setup.json).", "", "```sh", "uv run python scripts/run_heldout.py --execute", "uv run python scripts/report_heldout.py", "```", "", "The runner refuses changed frozen inputs and resumes persisted cases without redispatch. Existing output belongs to its retained native instance; a fresh replication needs a new instance and a separate --output directory. It runs only local inference. Native message/reference payloads are copied without categories or truth labels. Preserve private credentials outside Git.", "", "[Raw run manifest](../evidence/heldout/manifest.json) · [rule-only native output](../evidence/heldout/rules-only.json) · [trial 1](../evidence/heldout/trial-1/) · [trial 2](../evidence/heldout/trial-2/) · [trial 3](../evidence/heldout/trial-3/) · [machine-readable summary, all failures and timings](../evidence/heldout/summary.json). No evidence file exceeds 50 MB."]
    destination.write_text("\n".join(lines)+"\n")
    print(json.dumps({"totals":totals,"categories":splits,"variation":variation},indent=2))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=ROOT/'evidence/heldout')
    p.add_argument('--output',type=Path,default=ROOT/'docs/EVAL_HELDOUT.md')
    a=p.parse_args();report(a.source,a.output)
