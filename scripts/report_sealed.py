#!/usr/bin/env python3
"""Report all preregistered repetitions; no filtering or relabelling."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from statistics import median

from run_sealed import ROOT, frozen, DATASETS
from run_heldout import write_json
from heldout_metrics import ROUTES, score_row, summarize
from silentshift.engine import _recommendation_errors, strict_loads


def report(name,source,destination):
    data=frozen(name);cases=data['scenarios'];sha=DATASETS[name][2]
    manifest=json.loads((source/'manifest.json').read_text())
    if manifest['status']!='completed' or manifest['completed']!=3*len(cases):
        raise ValueError('Report requires every preregistered attempt, including failures')
    arms={'rules-only':[],'agent+policy':[]};observations=[]
    for trial in range(1,4):
        baseline=json.loads((source/f'rules-trial-{trial}.json').read_text())
        if baseline['dataset_sha256']!=sha or len(baseline['cases'])!=len(cases):raise ValueError('Baseline coverage mismatch')
        mapping={r['scenario_id']:r for r in baseline['cases']}
        for c in cases:
            r=mapping[c['id']]
            arms['rules-only'].append(score_row(c,r['decision'],trial=trial,elapsed_ms=r['elapsed_ms']))
            record=json.loads((source/f'trial-{trial}'/(c['id']+'.json')).read_text())
            if (record['dataset_sha256']!=sha or record['run_id']!=manifest['run_id'] or record['scenario_id']!=c['id'] or record['trial']!=trial or not record['semantic_inputs_match_frozen']):
                raise ValueError('Native checkpoint identity mismatch')
            v=record['record'];agent=v.get('agent') or {};actual=ROUTES.get(v['routing'],'INVALID')
            arms['agent+policy'].append(score_row(c,actual,delivery_count=v['delivery_count'],elapsed_ms=agent.get('elapsed_ms'),trial=trial,case_id=v['id'],trace_id=v['trace_id']))
            raw=agent.get('raw_response')
            try:errors=_recommendation_errors(strict_loads(raw),set(v['assessment']['evidence_ids']))
            except (ValueError,TypeError,RecursionError):errors=['No valid strict JSON response']
            observations.append({'scenario_id':c['id'],'trial':trial,'agent_status':agent.get('status'),
                'model_invoked':agent.get('model_invoked'),'failure_code':agent.get('failure_code'),
                'tool_reads':agent.get('tool_reads'),'schema_errors':errors,
                'service_elapsed_ms':record.get('service_elapsed_ms'),
                'quoted_findings':(v.get('recommendation') or {}).get('cited_findings'),
                'citation_checks':[x for x in v['policy']['checks'] if x['code']=='CITED_PROSE_GROUNDED']})
    summary={'dataset':name,'dataset_sha256':sha,'source_commit':manifest['source_commit'],
             'created_at':datetime.now(timezone.utc).isoformat(),'identity':manifest['identity'],
             'synthetic':True,'unique_orders':len(cases),'trials':3,'arms':{},'observations':observations}
    for arm,rows in arms.items():
        summary['arms'][arm]={'pooled':summarize(rows),'trials':{str(t):summarize([r for r in rows if r['trial']==t]) for t in range(1,4)},
            'categories':{cat:summarize([r for r in rows if r['category']==cat]) for cat in ['structured','unstructured','clean']},
            'failures':[r for r in rows if not r['correct']], 'cases':rows}
    a=summary['arms']['agent+policy'];b=summary['arms']['rules-only']
    unstructured_better=a['categories']['unstructured']['correct']>b['categories']['unstructured']['correct']
    wrong_better=a['pooled']['wrong_deliveries']<b['pooled']['wrong_deliveries']
    summary['comparison']={'fewer_wrong_deliveries':wrong_better,'more_correct_unstructured_routes':unstructured_better}
    write_json(source/'summary.json',summary)
    title='Sealed v3 result' if name=='sealed' else 'v2 dev set, after tuning'
    lines=[f'# {title}','','Measured on '+summary['created_at']+'. Synthetic examples only; delivery is to the IRIS simulator. No accuracy claim about customer data or another build.','',
        f"Source: `{manifest['source_commit']}`. Dataset SHA-256: `{sha}`. Labels were committed at `{manifest['labels_commit']}` before evaluation. Native runtime: `{manifest['identity']['runtime']}`; model `{manifest['identity']['model']}`; prompt `{manifest['identity']['prompt_version']}`.",
        '',f"{len(cases)} distinct orders, three actual baseline executions and three fresh native agent + policy investigations per order. The repeated executions are not independent samples. Every attempt, including failed/model-invalid attempts, remains in the denominator. No label edits or selective retries.",
        '', 'The deterministic baseline is unchanged. Agent findings may add containment or review; they cannot release any baseline hold. Exact quotations establish provenance, not semantic entailment. Legitimate prose authorizations that require releasing a structured hold remain outside this experiment’s permitted authority.',
        '', '## Results','', '| Arm / trial | Correct routes | Wrong deliveries | False holds | Review | Median investigation |','| --- | --- | --- | --- | --- | --- |']
    def show(r):
        ms=r['median_elapsed_ms'];return 'unavailable' if ms is None else f"{ms:.3f} ms"
    for arm in arms:
        for t in range(1,4):
            r=summary['arms'][arm]['trials'][str(t)]
            lines.append(f"| {arm}, {t} | {r['correct']}/{r['n']} | {r['wrong_deliveries']}/{r['bad_orders']} | {r['false_holds']}/{r['allow_eligible']} | {r['reviews']}/{r['n']} ({r['review_rate']:.1%}) | {show(r)} |")
    lines+=['','Baseline wrong deliveries are counterfactual ALLOW recommendations; policy wrong deliveries require an actual simulator receipt. Baseline timing covers only assessment + rule evaluation inside Embedded Python. Agent timing covers native investigation when recorded, not an equivalent scope or a latency-speedup comparison. Service wall times are separately retained. Missing times are not zero-filled.','', '## By category, pooled repetitions','','| Arm | Category | Correct routes | Wrong deliveries | False holds | Review |','| --- | --- | --- | --- | --- | --- |']
    for arm in arms:
        for cat in ['structured','unstructured','clean']:
            r=summary['arms'][arm]['categories'][cat]
            lines.append(f"| {arm} | {cat} | {r['correct']}/{r['n']} | {r['wrong_deliveries']}/{r['bad_orders']} | {r['false_holds']}/{r['allow_eligible']} | {r['reviews']}/{r['n']} |")
    lines+=['','Agent + policy '+('has fewer observed wrong simulator deliveries than the baseline’s counterfactual releases.' if wrong_better else 'does not beat rules-only on wrong deliveries.'),
        'Agent + policy '+('has more correct routes in the unstructured split in these synthetic repetitions.' if unstructured_better else 'does not beat rules-only on correct routes in the unstructured split.'),
        '', '## Every route failure','','A/Q/R = ALLOW/QUARANTINE/REQUEST_REVIEW. Each row lists all failing repetitions, including cases where rules beat the agent.','', '| ID | Category | Truth | Rules errors (trial: route) | Agent + policy errors (trial: route) | Rules win in trial |','| --- | --- | --- | --- | --- | --- |']
    ab={'ALLOW':'A','QUARANTINE':'Q','REQUEST_REVIEW':'R','INVALID':'INVALID'}
    for c in cases:
        rs=[r for r in arms['rules-only'] if r['scenario_id']==c['id']];ags=[r for r in arms['agent+policy'] if r['scenario_id']==c['id']]
        if all(r['correct'] for r in rs+ags):continue
        def failures(rows):return ', '.join(f"{r['trial']}: {ab[r['prediction']]}" for r in rows if not r['correct']) or '—'
        wins=[str(r['trial']) for r,q in zip(rs,ags) if r['correct'] and not q['correct']]
        lines.append(f"| {c['id']} | {c['category']} | {ab[c['ground_truth']['decision']]} | {failures(rs)} | {failures(ags)} | {', '.join(wins) or '—'} |")
    lines+=['','## Failed or schema-invalid agent attempts','','| ID | Trial | Agent status | Failure / schema errors |','| --- | --- | --- | --- |']
    bad=[o for o in observations if o['agent_status']!='returned' or o['schema_errors']]
    for o in bad:lines.append(f"| {o['scenario_id']} | {o['trial']} | {o['agent_status']} | {o['failure_code'] or '; '.join(o['schema_errors'])} |")
    if not bad:lines.append('No failed or schema-invalid agent attempts were observed.')
    lines+=['','## Time per order','','Milliseconds; three agent investigation times are retained separately. — means unavailable, not zero.','', '| ID | Rules median | Agent trials 1 / 2 / 3 | Agent median |','| --- | --- | --- | --- |']
    for c in cases:
        rs=[r['elapsed_ms'] for r in arms['rules-only'] if r['scenario_id']==c['id']];ag=[r['elapsed_ms'] for r in arms['agent+policy'] if r['scenario_id']==c['id']]
        fmt=lambda n:'—' if n is None else f'{n:.3f}'
        present=[n for n in ag if n is not None]
        lines.append(f"| {c['id']} | {fmt(median(rs))} | {' / '.join(fmt(n) for n in ag)} | {fmt(median(present) if present else None)} |")
    relative='../'+str(source.relative_to(ROOT))
    lines+=['','## Reproduction and limits','',f'Raw records, traces, per-case service timings, citation checks, complete metrics and native identity: [manifest]({relative}/manifest.json), [summary]({relative}/summary.json).',
        '', 'The operator-only evaluation host suppresses automatic indexing of evaluated outcomes. Contract/reference retrieval, the four tools, local inference, deterministic policy and simulator routing remain native. The precise production substitution is recorded in the manifest. Historical core fixtures may exist in the isolated instance; evaluated outcomes are not added to the precedent corpus.',
        '', 'This is an implementation-aware, seeded synthetic set. The generator author knew its families; it is not independently human-adjudicated or a production distribution. Model inference remains nondeterministic and quotation checks can accept a semantically mistaken interpretation. Results apply only to the named source, prompt, model and runtime.']
    destination.write_text('\n'.join(lines)+'\n')
    print(json.dumps({arm:{'pooled':summary['arms'][arm]['pooled'],'unstructured':summary['arms'][arm]['categories']['unstructured']} for arm in arms},indent=2))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dataset',choices=DATASETS,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();report(a.dataset,a.source,a.output)
