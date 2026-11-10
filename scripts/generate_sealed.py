#!/usr/bin/env python3
"""Generate synthetic contractual labels independently of any evaluated system.

No engine, rule, model or prior run outputs are imported. One seed, one new
output directory. Labels follow the stipulated contracts, not observed routes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def generate(seed):
    rng=random.Random(seed)
    vendors=['copper-finch','juniper-quay','opal-forge','cedar-switch','mosaic-ridge','tamarind-dock',
             'birch-orbit','saffron-beacon','cobalt-reed','maple-current','pebble-works','silver-kite']
    wording=['dispatch instruction','commercial rider','purchase schedule','buyer commitment']
    cases=[]
    clock='2026-11-10T12:00:00Z'
    for category in ['structured','unstructured','clean']:
        for i in range(12):
            vendor=vendors[i];cid='C-'+str(rng.randrange(100000,999999));qty=rng.randrange(5,23)*6
            product='ITEM-'+str(rng.randrange(1000,9999));region=rng.choice(['APAC-NORTH','NA-CENTRAL','EU-SOUTH'])
            sid=f'V3-{category[0].upper()}-{i+1:02d}'
            msg={'event_id':'evt-'+sid.lower(),'correlation_id':'corr-'+sid.lower(),'source':vendor,'kind':'order',
                 'occurred_at':'2026-11-10T11:30:00Z','contract_id':cid,'business_unit':region,
                 'product_id':product,'quantity':str(qty),'unit':'EA','notes':'Synthetic partner order.'}
            ref={'id':'contract:'+cid+':r1','contract_id':cid,'authority':'approved','effective_from':'2026-11-01T00:00:00Z',
                 'effective_to':None,'business_unit':region,'product_id':product,'quantity':str(qty),'unit':'EA',
                 'timestamp_semantics':'event_time'}
            refs=[ref];decision='ALLOW';classification='CLEAR';reason='The active approved commitment and order agree; no conflicting operative instruction exists.'
            if category=='structured':
                if i%3==0:
                    msg['unit']='TRAY';decision='QUARANTINE';reason='The approved commitment requires EA, while the order declares TRAY without approved authority for that representation.'
                elif i%3==1:
                    msg['quantity']=str(qty+6);decision='QUARANTINE';reason=f'The approved quantity is {qty} EA, but the order sends {qty+6} EA.'
                else:
                    ref['effective_to']='2026-11-09T00:00:00Z';decision='REQUEST_REVIEW';reason='The only approved reference expired before the business event; current authority is missing.'
                classification='VERIFIED_CONTRADICTION' if decision=='QUARANTINE' else 'INSUFFICIENT_EVIDENCE'
            elif category=='unstructured':
                phrase=rng.choice(wording)
                if i in [0,6]:
                    # Approved text permits a change that stale structured exports still contradict.
                    msg['unit']='BUNDLE';msg['quantity']=str(qty//6)
                    ref['text']=f'Effective November 10, the signed {phrase} replaces the unit presentation: one BUNDLE contains six EA. For {product}, {qty//6} BUNDLE is the agreed presentation of {qty} EA. The old export columns have not been refreshed.'
                    classification='LEGITIMATE_CHANGE';reason=f'The effective signed prose authorizes {qty//6} BUNDLE as {qty} EA despite stale structured unit columns.'
                elif i in [1,7]:
                    msg['notes']=f'PO attachment: the buyer asks for {qty} EA.'
                    ref['text']=f'Approved PO buyer note, effective November 10: this shipment must contain {qty+12} EA of {product}; the number {qty} belongs to the superseded schedule. This note governs over the old tabular export.'
                    decision='QUARANTINE';reason=f'The approved buyer note requires {qty+12} EA, while the incoming order and stale export say {qty} EA.'
                elif i in [2,8]:
                    ref['text']=f'Superseding email approved by the contract owner on November 9: for {cid}, deliver {qty+18} EA, replacing the earlier {qty} EA entry. Effective for events from November 10. This is the governing instruction for {product}.'
                    decision='QUARANTINE';reason=f'The effective approved superseding email requires {qty+18} EA; the order retains the obsolete {qty} EA.'
                elif i in [3,9]:
                    msg['unit']='PACK';msg['quantity']=str(qty//6)
                    ref['text']=f'Text-only conversion clause in the approved {phrase}: for {product}, each PACK is exactly six EA. The invoice presentation {qty//6} PACK is expressly permitted for this {qty} EA commitment from November 1 onward.'
                    classification='LEGITIMATE_CHANGE';reason='The approved operative conversion clause explicitly permits the incoming PACK presentation; the tabular EA fields alone are incomplete.'
                elif i in [4,10]:
                    ref['text']=f'Approved {phrase}: the controlling quantity for {product} is {qty} EA.'
                    other=dict(ref);other['id']='contract:'+cid+':peer';other['text']=f'Equally approved and effective {phrase}: the controlling quantity for {product} is {qty+6} EA. Neither document states that it supersedes the other.';refs.append(other)
                    decision='REQUEST_REVIEW';classification='INSUFFICIENT_EVIDENCE';reason='Equally authoritative effective prose references disagree and neither supersedes the other; a reviewer must resolve the conflict.'
                else:
                    ref['text']=f'The signed {phrase} for {product} requires unit SERIAL, not EA. This representation requirement applies from November 10; legacy export columns still show EA. The order quantity remains {qty}.'
                    decision='QUARANTINE';reason='An effective approved prose instruction requires SERIAL representation, while the order still uses EA.'
                if decision=='QUARANTINE':classification='VERIFIED_CONTRADICTION'
            else:
                if i%4==0:
                    ref['text']=f'Historical draft, not operative: a proposal once mentioned {qty+12} EA. That proposal was rejected. The approved and current commitment remains {qty} EA of {product}.'
                elif i%4==1:
                    msg['notes']='Partner requests a possible future carton presentation. No change is made to this order; quantities and units stay as agreed.'
                    ref['text']=f'The label CARTON is only a warehouse nickname, not an order unit. Current approved supply remains {qty} EA.'
                elif i%4==2:
                    ref['text']=f'For a different product OTHER-{product}, a separate order uses {qty+6} EA. This document confirms that {product} remains {qty} EA.'
                else:
                    ref['text']=f'A future proposal for November 20 would use {qty+18} EA. It is not approved and is not effective for this event. Current approved quantity is {qty} EA.'
            cases.append({'id':sid,'name':vendor+' '+category+' order','category':category,'message':msg,'references':refs,
                          'ground_truth':{'decision':decision,'classification':classification,'reason':reason}})
    rng.shuffle(cases)
    return {'dataset_version':'silentshift-sealed/3.0.0','schema_version':'silentshift-message/1','clock':clock,
            'provenance':'Synthetic contractual authority is stipulated. Generator written before dev-failure diagnosis; not independently human-adjudicated. Labels are never provided to the evaluated system.',
            'scenarios':cases}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seed',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Refuse to overwrite a sealed directory')
    data=generate(a.seed);raw=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode();digest=hashlib.sha256(raw).hexdigest()
    a.output.mkdir(parents=True)
    (a.output/'scenarios.json').write_bytes(raw)
    generator_digest=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest={'dataset_version':data['dataset_version'],'seed':a.seed,'sha256':digest,'generator_sha256':generator_digest,
              'count':len(data['scenarios']),'categories':{c:sum(x['category']==c for x in data['scenarios']) for c in ['structured','unstructured','clean']}}
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    protocol=f'''# Sealed v3 evaluation\n\nGenerated once from seed `{a.seed}` by `scripts/generate_sealed.py`.\nExact scenarios.json SHA-256: `{digest}`.\nGenerator SHA-256: `{generator_digest}`.\n\n36 synthetic orders: 12 structured, 12 unstructured, 12 clean, with new vendors and wording. Labels and one-line reasons derive from the stipulated contractual records, without importing or running any evaluated engine, baseline or model. The generator author knows its template families; this is not independent human blinding or customer validation.\n\n## Access and freeze\n\nAfter committing this directory, do not open the case file until the sealed execution phase. Do not use it for diagnosis, prompt selection or policy tuning. v2-heldout is now the dev set; preserve its original historical run and labels. Never edit a v3 input, category, label, reason, clock or order after generation. Disputed labels must be reported without relabelling.\n\n## Preregistered scoring\n\nFreeze the tuned source commit, prompt version and model identity before opening/running this set. Native target: 2026.3.0AI.154.0 / 154U ARM64, local Ollama qwen3-silentshift:4b-instruct only. Three executions of the unchanged deterministic baseline and three fresh native agent + policy investigations per case, in frozen order, trial-major. No selective model retries or output repair. Agent evidence may add a hold, but must never release a baseline rule hold. Do not copy labels, category or reasons into native/model inputs. Distinct case/trial namespaces isolate precedent history. No manual approvals or indexing of these outcomes as precedents.\n\nScore exact ALLOW / QUARANTINE / REQUEST_REVIEW routes. Invalid, failed and timed-out attempts remain in denominators. Wrong deliveries mean a non-ALLOW truth released by a baseline counterfactual, or actually delivered to the simulator by the policy arm. False holds mean any non-ALLOW outcome on ALLOW truth. Report review rate, per-category and per-trial results, all failures with IDs, and measured per-case time. Separate baseline assessment time from agent/service time. Repeated orders are not independent samples. Run this set once as three preregistered repetitions, then report regardless of outcome; no further tuning against these results.\n'''
    (a.output/'FROZEN.md').write_text(protocol)
    print(json.dumps({'generated':len(data['scenarios']),'sha256':digest,'seed':a.seed,'output':str(a.output),'rules_or_models_run':False}))


if __name__=='__main__':main()
